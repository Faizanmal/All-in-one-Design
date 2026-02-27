"""
Real-time Collaboration WebSocket Consumers

Provides live editing capabilities with presence tracking,
cursor synchronization, and conflict resolution.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone

logger = logging.getLogger('collaboration')


class CollaborationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time project collaboration.
    
    Handles:
    - User presence tracking
    - Cursor position sharing
    - Component locking
    - Real-time edits with OT-like conflict resolution
    - Chat messages
    """
    
    # Room prefix for channel groups
    ROOM_PREFIX = "project_collab_"
    
    # Cache keys
    PRESENCE_KEY = "collab:presence:{project_id}"
    LOCKS_KEY = "collab:locks:{project_id}"
    CURSORS_KEY = "collab:cursors:{project_id}"
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f"{self.ROOM_PREFIX}{self.project_id}"
        self.user = self.scope.get('user')
        
        # Check authentication
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Check project access
        has_access = await self.check_project_access()
        if not has_access:
            await self.close(code=4003)
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Add user to presence
        await self.add_presence()
        
        # Send current state to new user
        await self.send_initial_state()
        
        # Notify others of new user
        await self.broadcast_presence_update()
        
        logger.info(f"User {self.user.username} connected to project {self.project_id}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            # Remove user from presence
            await self.remove_presence()
            
            # Release any component locks held by this user
            await self.release_all_locks()
            
            # Notify others
            await self.broadcast_presence_update()
            
            logger.info(f"User {self.user.username} disconnected from project {self.project_id}")
        
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive_json(self, content: Dict[str, Any]):
        """Handle incoming WebSocket messages."""
        message_type = content.get('type')
        
        handlers = {
            'cursor_move': self.handle_cursor_move,
            'component_lock': self.handle_component_lock,
            'component_unlock': self.handle_component_unlock,
            'component_update': self.handle_component_update,
            'component_add': self.handle_component_add,
            'component_delete': self.handle_component_delete,
            'chat_message': self.handle_chat_message,
            'ping': self.handle_ping,
            'request_sync': self.handle_request_sync,
        }
        
        handler = handlers.get(message_type)
        if handler:
            try:
                await handler(content)
            except Exception as e:
                logger.error(f"Error handling {message_type}: {e}")
                await self.send_json({
                    'type': 'error',
                    'message': str(e),
                    'original_type': message_type,
                })
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}',
            })
    
    # ==========================================
    # MESSAGE HANDLERS
    # ==========================================
    
    async def handle_cursor_move(self, content: Dict[str, Any]):
        """Handle cursor position updates."""
        cursor_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'x': content.get('x', 0),
            'y': content.get('y', 0),
            'component_id': content.get('component_id'),
            'timestamp': timezone.now().isoformat(),
        }
        
        # Update cursor in cache
        await self.update_cursor(cursor_data)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'cursor': cursor_data,
            }
        )
    
    async def handle_component_lock(self, content: Dict[str, Any]):
        """Handle component lock requests."""
        component_id = content.get('component_id')
        if not component_id:
            return
        
        success, holder = await self.try_acquire_lock(component_id)
        
        if success:
            # Broadcast lock to all
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'lock_acquired',
                    'component_id': component_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
        else:
            # Notify requester of failure
            await self.send_json({
                'type': 'lock_denied',
                'component_id': component_id,
                'held_by': holder,
            })
    
    async def handle_component_unlock(self, content: Dict[str, Any]):
        """Handle component unlock requests."""
        component_id = content.get('component_id')
        if not component_id:
            return
        
        released = await self.release_lock(component_id)
        
        if released:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'lock_released',
                    'component_id': component_id,
                    'user_id': self.user.id,
                }
            )
    
    async def handle_component_update(self, content: Dict[str, Any]):
        """Handle component property updates."""
        component_id = content.get('component_id')
        changes = content.get('changes', {})
        version = content.get('version', 0)
        
        # Check if user has lock
        has_lock = await self.check_has_lock(component_id)
        if not has_lock:
            await self.send_json({
                'type': 'update_rejected',
                'component_id': component_id,
                'reason': 'Component is locked by another user',
            })
            return
        
        # Apply update to database
        success, new_version = await self.apply_component_update(
            component_id, changes, version
        )
        
        if success:
            # Broadcast update to all
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'component_updated',
                    'component_id': component_id,
                    'changes': changes,
                    'version': new_version,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
        else:
            # Version conflict - request client to sync
            await self.send_json({
                'type': 'sync_required',
                'component_id': component_id,
                'reason': 'Version conflict',
            })
    
    async def handle_component_add(self, content: Dict[str, Any]):
        """Handle new component additions."""
        component_data = content.get('component', {})
        
        new_component = await self.add_component(component_data)
        
        if new_component:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'component_added',
                    'component': new_component,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
    
    async def handle_component_delete(self, content: Dict[str, Any]):
        """Handle component deletions."""
        component_id = content.get('component_id')
        
        # Check lock
        has_lock = await self.check_has_lock(component_id)
        if not has_lock:
            lock_holder = await self.get_lock_holder(component_id)
            if lock_holder and lock_holder != self.user.id:
                await self.send_json({
                    'type': 'delete_rejected',
                    'component_id': component_id,
                    'reason': 'Component is locked',
                })
                return
        
        success = await self.delete_component(component_id)
        
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'component_deleted',
                    'component_id': component_id,
                    'user_id': self.user.id,
                    'username': self.user.username,
                }
            )
    
    async def handle_chat_message(self, content: Dict[str, Any]):
        """Handle chat messages."""
        message = content.get('message', '').strip()
        if not message:
            return
        
        chat_data = {
            'user_id': self.user.id,
            'username': self.user.username,
            'message': message[:1000],  # Limit message length
            'timestamp': timezone.now().isoformat(),
        }
        
        # Save to database
        await self.save_chat_message(chat_data)
        
        # Broadcast to all
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_broadcast',
                'chat': chat_data,
            }
        )
    
    async def handle_ping(self, content: Dict[str, Any]):
        """Handle ping for connection keep-alive."""
        await self.update_presence_timestamp()
        await self.send_json({
            'type': 'pong',
            'timestamp': timezone.now().isoformat(),
        })
    
    async def handle_request_sync(self, content: Dict[str, Any]):
        """Handle full state sync request."""
        await self.send_initial_state()
    
    # ==========================================
    # BROADCAST HANDLERS (called by group_send)
    # ==========================================
    
    async def cursor_update(self, event):
        """Send cursor update to client."""
        # Don't send user's own cursor back
        if event['cursor']['user_id'] != self.user.id:
            await self.send_json({
                'type': 'cursor_update',
                'cursor': event['cursor'],
            })
    
    async def lock_acquired(self, event):
        """Send lock acquired notification."""
        await self.send_json({
            'type': 'lock_acquired',
            'component_id': event['component_id'],
            'user_id': event['user_id'],
            'username': event['username'],
        })
    
    async def lock_released(self, event):
        """Send lock released notification."""
        await self.send_json({
            'type': 'lock_released',
            'component_id': event['component_id'],
            'user_id': event['user_id'],
        })
    
    async def component_updated(self, event):
        """Send component update to client."""
        # Always send, client handles merging
        await self.send_json({
            'type': 'component_updated',
            'component_id': event['component_id'],
            'changes': event['changes'],
            'version': event['version'],
            'user_id': event['user_id'],
            'username': event['username'],
            'is_own': event['user_id'] == self.user.id,
        })
    
    async def component_added(self, event):
        """Send new component notification."""
        await self.send_json({
            'type': 'component_added',
            'component': event['component'],
            'user_id': event['user_id'],
            'username': event['username'],
        })
    
    async def component_deleted(self, event):
        """Send component deleted notification."""
        await self.send_json({
            'type': 'component_deleted',
            'component_id': event['component_id'],
            'user_id': event['user_id'],
            'username': event['username'],
        })
    
    async def chat_broadcast(self, event):
        """Send chat message to client."""
        await self.send_json({
            'type': 'chat_message',
            'chat': event['chat'],
        })
    
    async def presence_update(self, event):
        """Send presence update to client."""
        await self.send_json({
            'type': 'presence_update',
            'users': event['users'],
        })
    
    async def user_joined(self, event):
        """Send user joined notification."""
        await self.send_json({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
        })
    
    async def user_left(self, event):
        """Send user left notification."""
        await self.send_json({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        })
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    @database_sync_to_async
    def check_project_access(self) -> bool:
        """Check if user has access to the project."""
        from projects.models import Project
        try:
            project = Project.objects.get(id=self.project_id)
            return (
                project.user == self.user or
                self.user in project.collaborators.all() or
                project.is_public
            )
        except Project.DoesNotExist:
            return False
    
    async def add_presence(self):
        """Add user to presence list."""
        cache_key = self.PRESENCE_KEY.format(project_id=self.project_id)
        presence = cache.get(cache_key, {})
        
        presence[str(self.user.id)] = {
            'user_id': self.user.id,
            'username': self.user.username,
            'channel_name': self.channel_name,
            'connected_at': timezone.now().isoformat(),
            'last_seen': timezone.now().isoformat(),
            'color': self._get_user_color(self.user.id),
        }
        
        cache.set(cache_key, presence, 3600)  # 1 hour TTL
    
    async def remove_presence(self):
        """Remove user from presence list."""
        cache_key = self.PRESENCE_KEY.format(project_id=self.project_id)
        presence = cache.get(cache_key, {})
        
        presence.pop(str(self.user.id), None)
        
        cache.set(cache_key, presence, 3600)
    
    async def update_presence_timestamp(self):
        """Update user's last seen timestamp."""
        cache_key = self.PRESENCE_KEY.format(project_id=self.project_id)
        presence = cache.get(cache_key, {})
        
        if str(self.user.id) in presence:
            presence[str(self.user.id)]['last_seen'] = timezone.now().isoformat()
            cache.set(cache_key, presence, 3600)
    
    async def get_presence(self) -> Dict[str, Any]:
        """Get current presence list."""
        cache_key = self.PRESENCE_KEY.format(project_id=self.project_id)
        return cache.get(cache_key, {})
    
    async def broadcast_presence_update(self):
        """Broadcast presence update to all users."""
        presence = await self.get_presence()
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update',
                'users': list(presence.values()),
            }
        )
    
    async def update_cursor(self, cursor_data: Dict[str, Any]):
        """Update cursor position in cache."""
        cache_key = self.CURSORS_KEY.format(project_id=self.project_id)
        cursors = cache.get(cache_key, {})
        
        cursors[str(self.user.id)] = cursor_data
        
        cache.set(cache_key, cursors, 300)  # 5 min TTL
    
    async def get_cursors(self) -> Dict[str, Any]:
        """Get all active cursors."""
        cache_key = self.CURSORS_KEY.format(project_id=self.project_id)
        return cache.get(cache_key, {})
    
    async def try_acquire_lock(self, component_id: str) -> tuple:
        """Try to acquire a lock on a component."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        locks = cache.get(cache_key, {})
        
        existing_lock = locks.get(component_id)
        
        # Check if already locked by someone else
        if existing_lock and existing_lock['user_id'] != self.user.id:
            # Check if lock is stale (> 30 seconds without update)
            lock_time = datetime.fromisoformat(existing_lock['acquired_at'])
            if timezone.now() - lock_time < timedelta(seconds=30):
                return False, existing_lock
        
        # Acquire lock
        locks[component_id] = {
            'user_id': self.user.id,
            'username': self.user.username,
            'acquired_at': timezone.now().isoformat(),
        }
        
        cache.set(cache_key, locks, 3600)
        return True, None
    
    async def release_lock(self, component_id: str) -> bool:
        """Release a lock on a component."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        locks = cache.get(cache_key, {})
        
        existing_lock = locks.get(component_id)
        
        if existing_lock and existing_lock['user_id'] == self.user.id:
            del locks[component_id]
            cache.set(cache_key, locks, 3600)
            return True
        
        return False
    
    async def release_all_locks(self):
        """Release all locks held by this user."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        locks = cache.get(cache_key, {})
        
        to_release = [
            comp_id for comp_id, lock in locks.items()
            if lock['user_id'] == self.user.id
        ]
        
        for comp_id in to_release:
            del locks[comp_id]
        
        cache.set(cache_key, locks, 3600)
        
        # Broadcast released locks
        for comp_id in to_release:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'lock_released',
                    'component_id': comp_id,
                    'user_id': self.user.id,
                }
            )
    
    async def check_has_lock(self, component_id: str) -> bool:
        """Check if current user has lock on component."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        locks = cache.get(cache_key, {})
        
        lock = locks.get(component_id)
        return lock and lock['user_id'] == self.user.id
    
    async def get_lock_holder(self, component_id: str) -> Optional[int]:
        """Get user ID of lock holder."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        locks = cache.get(cache_key, {})
        
        lock = locks.get(component_id)
        return lock['user_id'] if lock else None
    
    async def get_locks(self) -> Dict[str, Any]:
        """Get all active locks."""
        cache_key = self.LOCKS_KEY.format(project_id=self.project_id)
        return cache.get(cache_key, {})
    
    async def send_initial_state(self):
        """Send initial state to newly connected user."""
        presence = await self.get_presence()
        cursors = await self.get_cursors()
        locks = await self.get_locks()
        
        await self.send_json({
            'type': 'initial_state',
            'project_id': self.project_id,
            'users': list(presence.values()),
            'cursors': list(cursors.values()),
            'locks': locks,
            'your_user_id': self.user.id,
            'your_color': self._get_user_color(self.user.id),
        })
    
    @database_sync_to_async
    def apply_component_update(
        self,
        component_id: str,
        changes: Dict[str, Any],
        version: int
    ) -> tuple:
        """Apply component update to database."""
        from projects.models import DesignComponent
        
        try:
            component = DesignComponent.objects.get(id=component_id)
            
            # Update properties
            for key, value in changes.items():
                if key in ['x', 'y', 'width', 'height', 'rotation']:
                    # Position/size changes go in properties
                    component.properties[key] = value
                elif key == 'z_index':
                    component.z_index = value
                else:
                    component.properties[key] = value
            
            component.save()
            
            return True, version + 1
        except DesignComponent.DoesNotExist:
            return False, version
    
    @database_sync_to_async
    def add_component(self, component_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add a new component to the project."""
        from projects.models import Project, DesignComponent
        
        try:
            project = Project.objects.get(id=self.project_id)
            
            component = DesignComponent.objects.create(
                project=project,
                component_type=component_data.get('type', 'shape'),
                properties=component_data.get('properties', {}),
                z_index=component_data.get('z_index', 0),
            )
            
            return {
                'id': str(component.id),
                'type': component.component_type,
                'properties': component.properties,
                'z_index': component.z_index,
            }
        except Project.DoesNotExist:
            return None
    
    @database_sync_to_async
    def delete_component(self, component_id: str) -> bool:
        """Delete a component from the project."""
        from projects.models import DesignComponent
        
        try:
            component = DesignComponent.objects.get(
                id=component_id,
                project_id=self.project_id
            )
            component.delete()
            return True
        except DesignComponent.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_chat_message(self, chat_data: Dict[str, Any]):
        """Save chat message to database."""
        from .collaboration_models import CollaborationChatMessage
        
        CollaborationChatMessage.objects.create(
            project_id=self.project_id,
            user_id=chat_data['user_id'],
            message=chat_data['message'],
        )
    
    def _get_user_color(self, user_id: int) -> str:
        """Get consistent color for user."""
        colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8B500', '#00CED1',
        ]
        return colors[user_id % len(colors)]


class CollaborationChatMessage(models.Model):
    """Persisted chat messages for collaboration."""
    project_id = models.IntegerField(db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['project_id', 'created_at']),
        ]

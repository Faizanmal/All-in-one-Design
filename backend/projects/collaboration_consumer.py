"""
WebSocket consumer for real-time collaborative canvas editing
"""
import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Project
from .collaboration_models import CollaborationSession, CanvasEdit


class CollaborativeCanvasConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing
    Handles cursor positions, element updates, and user presence
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'canvas_{self.project_id}'
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Verify user has access to project
        has_access = await self.check_project_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Create or update collaboration session
        self.session_id = str(uuid.uuid4())
        await self.create_collaboration_session()
        
        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username,
                'session_id': self.session_id
            }
        )
        
        # Send active users to newly connected user
        active_users = await self.get_active_users()
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': active_users
        }))

    async def disconnect(self, close_code):
        # Remove session
        await self.remove_collaboration_session()
        
        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            # Route different actions
            if action == 'cursor_move':
                await self.handle_cursor_move(data)
            elif action == 'element_update':
                await self.handle_element_update(data)
            elif action == 'element_create':
                await self.handle_element_create(data)
            elif action == 'element_delete':
                await self.handle_element_delete(data)
            elif action == 'selection_change':
                await self.handle_selection_change(data)
            elif action == 'viewport_change':
                await self.handle_viewport_change(data)
            elif action == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            pass

    async def handle_cursor_move(self, data):
        """Broadcast cursor position to other users"""
        position = data.get('position', {})
        
        # Update session cursor position
        await self.update_session_cursor(position)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cursor_update',
                'user_id': self.user.id,
                'username': self.user.username,
                'position': position
            }
        )

    async def handle_element_update(self, data):
        """Handle element property updates"""
        element_id = data.get('element_id')
        updates = data.get('updates', {})
        previous_data = data.get('previous_data', {})
        
        # Save edit to database
        await self.save_canvas_edit('update', element_id, previous_data, updates)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'element_updated',
                'user_id': self.user.id,
                'username': self.user.username,
                'element_id': element_id,
                'updates': updates,
                'timestamp': data.get('timestamp')
            }
        )

    async def handle_element_create(self, data):
        """Handle new element creation"""
        element_data = data.get('element_data', {})
        element_id = element_data.get('id', str(uuid.uuid4()))
        
        # Save edit to database
        await self.save_canvas_edit('create', element_id, {}, element_data)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'element_created',
                'user_id': self.user.id,
                'username': self.user.username,
                'element_data': element_data,
                'timestamp': data.get('timestamp')
            }
        )

    async def handle_element_delete(self, data):
        """Handle element deletion"""
        element_id = data.get('element_id')
        element_data = data.get('element_data', {})
        
        # Save edit to database
        await self.save_canvas_edit('delete', element_id, element_data, {})
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'element_deleted',
                'user_id': self.user.id,
                'username': self.user.username,
                'element_id': element_id,
                'timestamp': data.get('timestamp')
            }
        )

    async def handle_selection_change(self, data):
        """Handle user selection changes"""
        selected_elements = data.get('selected_elements', [])
        
        # Update session
        await self.update_session_selection(selected_elements)
        
        # Broadcast to others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'selection_changed',
                'user_id': self.user.id,
                'username': self.user.username,
                'selected_elements': selected_elements
            }
        )

    async def handle_viewport_change(self, data):
        """Handle viewport (zoom/pan) changes"""
        viewport = data.get('viewport', {})
        
        # Update session
        await self.update_session_viewport(viewport)

    # Channel layer event handlers
    async def user_joined(self, event):
        """Send user joined notification"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
                'session_id': event['session_id']
            }))

    async def user_left(self, event):
        """Send user left notification"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'username': event['username']
            }))

    async def cursor_update(self, event):
        """Send cursor position update"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'user_id': event['user_id'],
                'username': event['username'],
                'position': event['position']
            }))

    async def element_updated(self, event):
        """Send element update"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'element_updated',
                'user_id': event['user_id'],
                'username': event['username'],
                'element_id': event['element_id'],
                'updates': event['updates'],
                'timestamp': event['timestamp']
            }))

    async def element_created(self, event):
        """Send element creation"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'element_created',
                'user_id': event['user_id'],
                'username': event['username'],
                'element_data': event['element_data'],
                'timestamp': event['timestamp']
            }))

    async def element_deleted(self, event):
        """Send element deletion"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'element_deleted',
                'user_id': event['user_id'],
                'username': event['username'],
                'element_id': event['element_id'],
                'timestamp': event['timestamp']
            }))

    async def selection_changed(self, event):
        """Send selection change"""
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'selection_changed',
                'user_id': event['user_id'],
                'username': event['username'],
                'selected_elements': event['selected_elements']
            }))

    # Database operations
    @database_sync_to_async
    def check_project_access(self):
        """Check if user has access to project"""
        try:
            project = Project.objects.get(id=self.project_id)
            return (
                project.user == self.user or 
                self.user in project.collaborators.all()
            )
        except Project.DoesNotExist:
            return False

    @database_sync_to_async
    def create_collaboration_session(self):
        """Create or update collaboration session"""
        CollaborationSession.objects.update_or_create(
            project_id=self.project_id,
            user=self.user,
            defaults={
                'session_id': self.session_id,
                'is_active': True
            }
        )

    @database_sync_to_async
    def remove_collaboration_session(self):
        """Remove collaboration session"""
        CollaborationSession.objects.filter(
            project_id=self.project_id,
            user=self.user
        ).update(is_active=False)

    @database_sync_to_async
    def get_active_users(self):
        """Get list of active users in session"""
        sessions = CollaborationSession.objects.filter(
            project_id=self.project_id,
            is_active=True
        ).select_related('user')
        
        return [
            {
                'user_id': session.user.id,
                'username': session.user.username,
                'cursor_position': session.cursor_position,
                'selected_elements': session.selected_elements
            }
            for session in sessions
        ]

    @database_sync_to_async
    def update_session_cursor(self, position):
        """Update session cursor position"""
        CollaborationSession.objects.filter(
            project_id=self.project_id,
            user=self.user
        ).update(cursor_position=position)

    @database_sync_to_async
    def update_session_selection(self, selected_elements):
        """Update session selection"""
        CollaborationSession.objects.filter(
            project_id=self.project_id,
            user=self.user
        ).update(selected_elements=selected_elements)

    @database_sync_to_async
    def update_session_viewport(self, viewport):
        """Update session viewport"""
        CollaborationSession.objects.filter(
            project_id=self.project_id,
            user=self.user
        ).update(viewport=viewport)

    @database_sync_to_async
    def save_canvas_edit(self, edit_type, element_id, previous_data, new_data):
        """Save canvas edit to database"""
        CanvasEdit.objects.create(
            project_id=self.project_id,
            user=self.user,
            edit_type=edit_type,
            element_id=element_id,
            previous_data=previous_data,
            new_data=new_data
        )

"""
Plugin Runtime Engine
Secure plugin execution environment with sandboxing and API access
"""
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from django.conf import settings
from django.utils import timezone
from celery import shared_task

logger = logging.getLogger(__name__)


class PluginPermission(Enum):
    """Permissions that plugins can request"""
    READ_PROJECT = "read_project"
    WRITE_PROJECT = "write_project"
    READ_ASSETS = "read_assets"
    WRITE_ASSETS = "write_assets"
    ACCESS_AI = "access_ai"
    ACCESS_NETWORK = "access_network"
    READ_USER = "read_user"
    NOTIFICATIONS = "notifications"
    STORAGE = "storage"
    CLIPBOARD = "clipboard"


class PluginEvent(Enum):
    """Events that plugins can listen to"""
    PROJECT_OPEN = "project.open"
    PROJECT_SAVE = "project.save"
    ELEMENT_SELECT = "element.select"
    ELEMENT_CREATE = "element.create"
    ELEMENT_UPDATE = "element.update"
    ELEMENT_DELETE = "element.delete"
    EXPORT_START = "export.start"
    EXPORT_COMPLETE = "export.complete"
    AI_GENERATE = "ai.generate"
    CANVAS_CLICK = "canvas.click"
    SHORTCUT = "shortcut"


@dataclass
class PluginContext:
    """Context passed to plugin execution"""
    plugin_id: str
    user_id: int
    project_id: Optional[int] = None
    permissions: List[PluginPermission] = None
    settings: Dict = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.settings is None:
            self.settings = {}


class PluginAPI:
    """
    API exposed to plugins for interacting with the platform
    All methods are sandboxed and permission-checked
    """
    
    def __init__(self, context: PluginContext):
        self.context = context
        self._storage = {}
        self._execution_log = []
    
    def _require_permission(self, permission: PluginPermission):
        """Check if plugin has required permission"""
        if permission not in self.context.permissions:
            raise PermissionError(f"Plugin does not have permission: {permission.value}")
    
    def _log_action(self, action: str, data: Any = None):
        """Log plugin action for auditing"""
        self._execution_log.append({
            'timestamp': timezone.now().isoformat(),
            'action': action,
            'data': data
        })
    
    # Project API
    def get_project(self) -> Dict:
        """Get current project data"""
        self._require_permission(PluginPermission.READ_PROJECT)
        self._log_action('get_project')
        
        from projects.models import Project
        
        if not self.context.project_id:
            return None
        
        try:
            project = Project.objects.get(id=self.context.project_id)
            return {
                'id': project.id,
                'name': project.name,
                'type': project.project_type,
                'design_data': project.design_data,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat()
            }
        except Project.DoesNotExist:
            return None
    
    def update_project(self, updates: Dict) -> bool:
        """Update project data"""
        self._require_permission(PluginPermission.WRITE_PROJECT)
        self._log_action('update_project', updates)
        
        from projects.models import Project
        
        if not self.context.project_id:
            return False
        
        try:
            project = Project.objects.get(id=self.context.project_id)
            
            if 'name' in updates:
                project.name = updates['name']
            if 'design_data' in updates:
                project.design_data = updates['design_data']
            
            project.save()
            return True
        except Project.DoesNotExist:
            return False
    
    def get_elements(self) -> List[Dict]:
        """Get all elements in the current project"""
        self._require_permission(PluginPermission.READ_PROJECT)
        self._log_action('get_elements')
        
        project = self.get_project()
        if not project:
            return []
        
        design_data = project.get('design_data', {})
        return design_data.get('elements', design_data.get('components', []))
    
    def add_element(self, element: Dict) -> str:
        """Add an element to the project"""
        self._require_permission(PluginPermission.WRITE_PROJECT)
        self._log_action('add_element', element)
        
        from projects.models import Project
        import uuid
        
        if not self.context.project_id:
            raise ValueError("No project context")
        
        try:
            project = Project.objects.get(id=self.context.project_id)
            design_data = project.design_data or {}
            elements = design_data.get('elements', [])
            
            # Generate element ID
            element_id = str(uuid.uuid4())[:8]
            element['id'] = element_id
            element['plugin_created'] = self.context.plugin_id
            
            elements.append(element)
            design_data['elements'] = elements
            project.design_data = design_data
            project.save()
            
            return element_id
        except Project.DoesNotExist:
            raise ValueError("Project not found")
    
    def update_element(self, element_id: str, updates: Dict) -> bool:
        """Update an element in the project"""
        self._require_permission(PluginPermission.WRITE_PROJECT)
        self._log_action('update_element', {'id': element_id, 'updates': updates})
        
        from projects.models import Project
        
        if not self.context.project_id:
            return False
        
        try:
            project = Project.objects.get(id=self.context.project_id)
            design_data = project.design_data or {}
            elements = design_data.get('elements', [])
            
            for element in elements:
                if element.get('id') == element_id:
                    element.update(updates)
                    break
            else:
                return False
            
            design_data['elements'] = elements
            project.design_data = design_data
            project.save()
            return True
        except Project.DoesNotExist:
            return False
    
    def delete_element(self, element_id: str) -> bool:
        """Delete an element from the project"""
        self._require_permission(PluginPermission.WRITE_PROJECT)
        self._log_action('delete_element', element_id)
        
        from projects.models import Project
        
        if not self.context.project_id:
            return False
        
        try:
            project = Project.objects.get(id=self.context.project_id)
            design_data = project.design_data or {}
            elements = design_data.get('elements', [])
            
            original_len = len(elements)
            elements = [e for e in elements if e.get('id') != element_id]
            
            if len(elements) == original_len:
                return False
            
            design_data['elements'] = elements
            project.design_data = design_data
            project.save()
            return True
        except Project.DoesNotExist:
            return False
    
    # Assets API
    def get_assets(self) -> List[Dict]:
        """Get user's assets"""
        self._require_permission(PluginPermission.READ_ASSETS)
        self._log_action('get_assets')
        
        from assets.models import Asset
        
        assets = Asset.objects.filter(user_id=self.context.user_id)[:100]
        return [
            {
                'id': asset.id,
                'name': asset.name,
                'type': asset.asset_type,
                'url': asset.file.url if asset.file else None,
                'metadata': asset.metadata
            }
            for asset in assets
        ]
    
    # AI API
    def generate_with_ai(self, prompt: str, options: Dict = None) -> Dict:
        """Generate content using AI"""
        self._require_permission(PluginPermission.ACCESS_AI)
        self._log_action('generate_with_ai', {'prompt': prompt, 'options': options})
        
        from ai_services.services import AIDesignService
        
        service = AIDesignService()
        result = service.generate_design(
            prompt=prompt,
            design_type=options.get('type', 'general') if options else 'general',
            user_id=self.context.user_id
        )
        
        return result
    
    def analyze_design(self, element_ids: List[str] = None) -> Dict:
        """Analyze design for insights"""
        self._require_permission(PluginPermission.ACCESS_AI)
        self._log_action('analyze_design', element_ids)
        
        project = self.get_project()
        if not project:
            return {'error': 'No project context'}
        
        # Basic analysis
        elements = project.get('design_data', {}).get('elements', [])
        
        if element_ids:
            elements = [e for e in elements if e.get('id') in element_ids]
        
        return {
            'element_count': len(elements),
            'types': list(set(e.get('type') for e in elements)),
            'colors_used': self._extract_colors(elements),
            'suggestions': self._generate_suggestions(elements)
        }
    
    def _extract_colors(self, elements: List[Dict]) -> List[str]:
        """Extract colors used in elements"""
        colors = set()
        for element in elements:
            style = element.get('style', {})
            if 'color' in style:
                colors.add(style['color'])
            if 'backgroundColor' in style:
                colors.add(style['backgroundColor'])
        return list(colors)
    
    def _generate_suggestions(self, elements: List[Dict]) -> List[str]:
        """Generate design suggestions"""
        suggestions = []
        
        colors = self._extract_colors(elements)
        if len(colors) > 5:
            suggestions.append("Consider using fewer colors for a more cohesive design")
        
        font_sizes = []
        for element in elements:
            if element.get('type') == 'text':
                size = element.get('style', {}).get('fontSize', '16px')
                font_sizes.append(int(str(size).replace('px', '').replace('pt', '')))
        
        if font_sizes and len(set(font_sizes)) > 4:
            suggestions.append("Consider using a more consistent typographic scale")
        
        return suggestions
    
    # User API
    def get_user_info(self) -> Dict:
        """Get current user info (limited)"""
        self._require_permission(PluginPermission.READ_USER)
        self._log_action('get_user_info')
        
        from django.contrib.auth.models import User
        
        try:
            user = User.objects.get(id=self.context.user_id)
            return {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'subscription_tier': getattr(user, 'subscription', None).tier.name if hasattr(user, 'subscription') and user.subscription else 'free'
            }
        except User.DoesNotExist:
            return None
    
    # Storage API
    def storage_get(self, key: str) -> Any:
        """Get value from plugin storage"""
        self._require_permission(PluginPermission.STORAGE)
        
        from plugins.models import PluginStorage
        
        try:
            storage = PluginStorage.objects.get(
                plugin_id=self.context.plugin_id,
                user_id=self.context.user_id,
                key=key
            )
            return json.loads(storage.value)
        except PluginStorage.DoesNotExist:
            return None
    
    def storage_set(self, key: str, value: Any) -> bool:
        """Set value in plugin storage"""
        self._require_permission(PluginPermission.STORAGE)
        self._log_action('storage_set', {'key': key})
        
        from plugins.models import PluginStorage
        
        storage, _ = PluginStorage.objects.update_or_create(
            plugin_id=self.context.plugin_id,
            user_id=self.context.user_id,
            key=key,
            defaults={'value': json.dumps(value)}
        )
        return True
    
    def storage_delete(self, key: str) -> bool:
        """Delete value from plugin storage"""
        self._require_permission(PluginPermission.STORAGE)
        self._log_action('storage_delete', key)
        
        from plugins.models import PluginStorage
        
        deleted, _ = PluginStorage.objects.filter(
            plugin_id=self.context.plugin_id,
            user_id=self.context.user_id,
            key=key
        ).delete()
        return deleted > 0
    
    # Notification API
    def show_notification(self, message: str, notification_type: str = 'info') -> bool:
        """Show notification to user"""
        self._require_permission(PluginPermission.NOTIFICATIONS)
        self._log_action('show_notification', {'message': message, 'type': notification_type})
        
        from notifications.models import Notification
        
        Notification.objects.create(
            user_id=self.context.user_id,
            notification_type=notification_type,
            title=f"Plugin: {self.context.plugin_id}",
            message=message
        )
        return True
    
    # Network API (for external API calls)
    def fetch(self, url: str, options: Dict = None) -> Dict:
        """Make HTTP request (limited domains)"""
        self._require_permission(PluginPermission.ACCESS_NETWORK)
        self._log_action('fetch', {'url': url})
        
        import requests
        from urllib.parse import urlparse
        
        # Validate URL against allowed domains
        parsed = urlparse(url)
        allowed_domains = getattr(settings, 'PLUGIN_ALLOWED_DOMAINS', [
            'api.unsplash.com',
            'api.pexels.com',
            'fonts.googleapis.com',
            'api.iconify.design'
        ])
        
        if parsed.netloc not in allowed_domains:
            raise PermissionError(f"Domain not allowed: {parsed.netloc}")
        
        options = options or {}
        method = options.get('method', 'GET').upper()
        headers = options.get('headers', {})
        body = options.get('body')
        timeout = min(options.get('timeout', 10), 30)  # Max 30 seconds
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                'status': response.status_code,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'headers': dict(response.headers)
            }
        except requests.RequestException as e:
            return {
                'status': 0,
                'error': str(e)
            }


class PluginRuntime:
    """
    Secure plugin execution runtime
    Provides sandboxed environment for running plugin code
    """
    
    def __init__(self):
        self._plugins = {}
        self._event_handlers = {}
        self._execution_limits = {
            'max_execution_time': 30,  # seconds
            'max_memory': 50 * 1024 * 1024,  # 50MB
            'max_api_calls': 100
        }
    
    def register_plugin(self, plugin_id: str, plugin_config: Dict):
        """Register a plugin with its configuration"""
        self._plugins[plugin_id] = plugin_config
    
    def register_event_handler(
        self,
        plugin_id: str,
        event: PluginEvent,
        handler: Callable
    ):
        """Register an event handler for a plugin"""
        key = (plugin_id, event)
        if key not in self._event_handlers:
            self._event_handlers[key] = []
        self._event_handlers[key].append(handler)
    
    def emit_event(
        self,
        event: PluginEvent,
        data: Dict,
        user_id: int,
        project_id: Optional[int] = None
    ) -> List[Dict]:
        """Emit an event to all registered plugin handlers"""
        results = []
        
        for (plugin_id, ev), handlers in self._event_handlers.items():
            if ev == event:
                for handler in handlers:
                    try:
                        context = PluginContext(
                            plugin_id=plugin_id,
                            user_id=user_id,
                            project_id=project_id,
                            permissions=self._plugins.get(plugin_id, {}).get('permissions', [])
                        )
                        
                        api = PluginAPI(context)
                        result = handler(api, data)
                        
                        results.append({
                            'plugin_id': plugin_id,
                            'success': True,
                            'result': result
                        })
                    except Exception as e:
                        logger.error(f"Plugin {plugin_id} error on event {event}: {e}")
                        results.append({
                            'plugin_id': plugin_id,
                            'success': False,
                            'error': str(e)
                        })
        
        return results
    
    def execute_plugin_action(
        self,
        plugin_id: str,
        action: str,
        params: Dict,
        context: PluginContext
    ) -> Dict:
        """Execute a specific plugin action"""
        
        if plugin_id not in self._plugins:
            return {'success': False, 'error': 'Plugin not registered'}
        
        plugin_config = self._plugins[plugin_id]
        actions = plugin_config.get('actions', {})
        
        if action not in actions:
            return {'success': False, 'error': f'Action not found: {action}'}
        
        action_handler = actions[action]
        
        try:
            start_time = time.time()
            api = PluginAPI(context)
            
            result = action_handler(api, params)
            
            execution_time = time.time() - start_time
            
            if execution_time > self._execution_limits['max_execution_time']:
                logger.warning(f"Plugin {plugin_id} exceeded execution time: {execution_time}s")
            
            return {
                'success': True,
                'result': result,
                'execution_time': execution_time
            }
        except PermissionError as e:
            return {'success': False, 'error': f'Permission denied: {str(e)}'}
        except Exception as e:
            logger.error(f"Plugin {plugin_id} action {action} error: {e}")
            return {'success': False, 'error': str(e)}


# Singleton runtime instance
plugin_runtime = PluginRuntime()


# Celery tasks for async plugin execution
@shared_task(bind=True, max_retries=2, time_limit=60)
def execute_plugin_async(
    self,
    plugin_id: str,
    action: str,
    params: Dict,
    user_id: int,
    project_id: Optional[int] = None
):
    """Execute plugin action asynchronously"""
    
    from plugins.models import Plugin, InstalledPlugin
    
    try:
        plugin = Plugin.objects.get(id=plugin_id)
        installation = InstalledPlugin.objects.get(
            plugin=plugin,
            user_id=user_id,
            is_active=True
        )
        
        permissions = [
            PluginPermission(p) for p in installation.granted_permissions
        ]
        
        context = PluginContext(
            plugin_id=str(plugin_id),
            user_id=user_id,
            project_id=project_id,
            permissions=permissions,
            settings=installation.settings
        )
        
        result = plugin_runtime.execute_plugin_action(
            str(plugin_id),
            action,
            params,
            context
        )
        
        # Log execution
        from plugins.models import PluginExecution
        PluginExecution.objects.create(
            plugin=plugin,
            user_id=user_id,
            action=action,
            execution_time=result.get('execution_time', 0),
            success=result.get('success', False),
            error_message=result.get('error', '')
        )
        
        return result
        
    except Plugin.DoesNotExist:
        return {'success': False, 'error': 'Plugin not found'}
    except InstalledPlugin.DoesNotExist:
        return {'success': False, 'error': 'Plugin not installed for user'}
    except Exception as e:
        logger.error(f"Async plugin execution failed: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def emit_plugin_event(
    event_name: str,
    data: Dict,
    user_id: int,
    project_id: Optional[int] = None
):
    """Emit event to all installed plugins"""
    
    from plugins.models import InstalledPlugin
    
    try:
        # event unused
        _ = PluginEvent(event_name)
    except ValueError:
        return {'success': False, 'error': f'Invalid event: {event_name}'}
    
    # Get all installed plugins for user
    installations = InstalledPlugin.objects.filter(
        user_id=user_id,
        is_active=True
    ).select_related('plugin')
    
    results = []
    
    for installation in installations:
        plugin = installation.plugin
        
        # Check if plugin has handler for this event
        event_handlers = plugin.manifest.get('events', [])
        if event_name not in event_handlers:
            continue
        
        # Execute plugin event handler
        result = execute_plugin_async.delay(
            str(plugin.id),
            f'on_{event_name}',
            data,
            user_id,
            project_id
        )
        
        results.append({
            'plugin_id': str(plugin.id),
            'task_id': result.id
        })
    
    return {'results': results}

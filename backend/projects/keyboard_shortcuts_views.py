"""
Keyboard Shortcuts API Views

REST API endpoints for keyboard shortcuts management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .keyboard_shortcuts import (
    KeyboardShortcut,
    ShortcutPreset,
    ShortcutsService
)


class ShortcutsViewSet(viewsets.ViewSet):
    """
    ViewSet for managing keyboard shortcuts.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        Get all shortcuts with user customizations applied.
        
        GET /api/v1/projects/shortcuts/
        """
        platform = request.query_params.get('platform', 'default')
        
        service = ShortcutsService(request.user)
        shortcuts = service.get_all_shortcuts(platform)
        
        return Response({
            'shortcuts': shortcuts,
            'total': len(shortcuts)
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get shortcuts organized by category.
        
        GET /api/v1/projects/shortcuts/by_category/
        """
        platform = request.query_params.get('platform', 'default')
        
        service = ShortcutsService(request.user)
        categories = service.get_shortcuts_by_category(platform)
        
        return Response({
            'categories': categories
        })
    
    @action(detail=False, methods=['post'])
    def set(self, request):
        """
        Set a custom key binding for a shortcut.
        
        POST /api/v1/projects/shortcuts/set/
        {
            "action_id": "edit.undo",
            "key": "Ctrl+Y"
        }
        """
        action_id = request.data.get('action_id')
        key = request.data.get('key')
        
        if not action_id or not key:
            return Response(
                {'error': 'action_id and key are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ShortcutsService(request.user)
        
        try:
            result = service.set_shortcut(action_id, key)
            return Response(result)
        except KeyboardShortcut.DoesNotExist:
            return Response(
                {'error': f'Shortcut {action_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """
        Reset a shortcut to its default binding.
        
        POST /api/v1/projects/shortcuts/reset/
        {
            "action_id": "edit.undo"
        }
        """
        action_id = request.data.get('action_id')
        
        if not action_id:
            return Response(
                {'error': 'action_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ShortcutsService(request.user)
        
        try:
            result = service.reset_shortcut(action_id)
            return Response(result)
        except KeyboardShortcut.DoesNotExist:
            return Response(
                {'error': f'Shortcut {action_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def reset_all(self, request):
        """
        Reset all shortcuts to defaults.
        
        POST /api/v1/projects/shortcuts/reset_all/
        """
        service = ShortcutsService(request.user)
        result = service.reset_all_shortcuts()
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Enable or disable a shortcut.
        
        POST /api/v1/projects/shortcuts/toggle/
        {
            "action_id": "edit.undo",
            "enabled": true
        }
        """
        action_id = request.data.get('action_id')
        enabled = request.data.get('enabled', True)
        
        if not action_id:
            return Response(
                {'error': 'action_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ShortcutsService(request.user)
        
        try:
            result = service.toggle_shortcut(action_id, enabled)
            return Response(result)
        except KeyboardShortcut.DoesNotExist:
            return Response(
                {'error': f'Shortcut {action_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search shortcuts by name or key.
        
        GET /api/v1/projects/shortcuts/search/?q=undo
        """
        query = request.query_params.get('q', '')
        
        if len(query) < 1:
            return Response({'results': []})
        
        service = ShortcutsService(request.user)
        results = service.search_shortcuts(query)
        
        return Response({
            'query': query,
            'results': results,
            'count': len(results)
        })
    
    @action(detail=False, methods=['get'])
    def cheat_sheet(self, request):
        """
        Generate a printable cheat sheet.
        
        GET /api/v1/projects/shortcuts/cheat_sheet/?format=html
        """
        format_type = request.query_params.get('format', 'json')
        
        service = ShortcutsService(request.user)
        cheat_sheet = service.generate_cheat_sheet(format_type)
        
        if format_type == 'html':
            return Response({'html': cheat_sheet})
        elif format_type == 'markdown':
            return Response({'markdown': cheat_sheet})
        else:
            return Response({'categories': cheat_sheet})
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export shortcuts to JSON.
        
        GET /api/v1/projects/shortcuts/export/
        """
        service = ShortcutsService(request.user)
        data = service.export_shortcuts()
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def import_shortcuts(self, request):
        """
        Import shortcuts from JSON.
        
        POST /api/v1/projects/shortcuts/import_shortcuts/
        """
        service = ShortcutsService(request.user)
        result = service.import_shortcuts(request.data)
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """
        Get default shortcut definitions.
        
        GET /api/v1/projects/shortcuts/defaults/
        """
        return Response({
            'shortcuts': ShortcutsService.get_default_shortcuts()
        })


class ShortcutPresetsViewSet(viewsets.ViewSet):
    """
    ViewSet for shortcut presets.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List available presets.
        
        GET /api/v1/projects/shortcut-presets/
        """
        # Get user presets
        user_presets = ShortcutPreset.objects.filter(user=request.user)
        
        # Get system/app presets
        system_presets = ShortcutPreset.objects.filter(preset_type__in=['system', 'app'])
        
        return Response({
            'user_presets': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'shortcut_count': len(p.mappings),
                    'is_default': p.is_default,
                }
                for p in user_presets
            ],
            'system_presets': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'icon': p.icon,
                    'shortcut_count': len(p.mappings),
                }
                for p in system_presets
            ],
            'application_presets': ShortcutsService.get_application_presets()
        })
    
    def create(self, request):
        """
        Create a new preset from current shortcuts.
        
        POST /api/v1/projects/shortcut-presets/
        {
            "name": "My Custom Preset",
            "description": "My preferred shortcuts"
        }
        """
        name = request.data.get('name', 'My Preset')
        description = request.data.get('description', '')
        
        service = ShortcutsService(request.user)
        result = service.save_as_preset(name, description)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        Apply a preset.
        
        POST /api/v1/projects/shortcut-presets/{id}/apply/
        """
        service = ShortcutsService(request.user)
        
        try:
            result = service.apply_preset(pk)
            return Response(result)
        except ShortcutPreset.DoesNotExist:
            return Response(
                {'error': 'Preset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, pk=None):
        """
        Delete a user preset.
        
        DELETE /api/v1/projects/shortcut-presets/{id}/
        """
        try:
            preset = ShortcutPreset.objects.get(pk=pk, user=request.user)
            preset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ShortcutPreset.DoesNotExist:
            return Response(
                {'error': 'Preset not found or not owned by user'},
                status=status.HTTP_404_NOT_FOUND
            )


class LearningModeViewSet(viewsets.ViewSet):
    """
    ViewSet for shortcut learning mode.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get learning mode statistics.
        
        GET /api/v1/projects/shortcuts-learning/stats/
        """
        service = ShortcutsService(request.user)
        stats = service.get_learning_stats()
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle learning mode.
        
        POST /api/v1/projects/shortcuts-learning/toggle/
        {
            "enabled": true
        }
        """
        enabled = request.data.get('enabled', True)
        
        service = ShortcutsService(request.user)
        result = service.toggle_learning_mode(enabled)
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def log_usage(self, request):
        """
        Log shortcut or UI action usage.
        
        POST /api/v1/projects/shortcuts-learning/log_usage/
        {
            "action_id": "edit.undo",
            "used_shortcut": true
        }
        """
        action_id = request.data.get('action_id')
        used_shortcut = request.data.get('used_shortcut', True)
        
        if not action_id:
            return Response(
                {'error': 'action_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ShortcutsService(request.user)
        service.log_usage(action_id, used_shortcut)
        
        return Response({'logged': True})
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Get shortcut suggestions based on usage patterns.
        
        GET /api/v1/projects/shortcuts-learning/suggestions/
        """
        service = ShortcutsService(request.user)
        stats = service.get_learning_stats()
        
        # Convert to_learn queryset to suggestions
        suggestions = [
            {
                'action_id': item['shortcut__action_id'],
                'name': item['shortcut__name'],
                'key': item['shortcut__default_key'],
                'times_used_via_ui': item['count'],
                'message': f"You've used '{item['shortcut__name']}' {item['count']} times. Try the shortcut: {item['shortcut__default_key']}"
            }
            for item in stats.get('to_learn', [])
        ]
        
        return Response({
            'suggestions': suggestions,
            'total_ui_actions_today': stats.get('actions_via_ui_today', 0)
        })

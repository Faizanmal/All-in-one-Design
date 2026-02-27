"""
Keyboard Shortcuts Manager Models and Service

Provides customizable keyboard shortcuts, shortcut presets,
cheat sheet generation, and learning mode functionality.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ShortcutCategory(models.Model):
    """
    Category for organizing shortcuts.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon name
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Shortcut categories'
    
    def __str__(self):
        return self.name


class KeyboardShortcut(models.Model):
    """
    Individual keyboard shortcut definition.
    """
    ACTION_TYPES = [
        ('tool', 'Select Tool'),
        ('action', 'Perform Action'),
        ('view', 'Change View'),
        ('panel', 'Toggle Panel'),
        ('zoom', 'Zoom Control'),
        ('edit', 'Edit Operation'),
        ('file', 'File Operation'),
        ('layer', 'Layer Operation'),
        ('align', 'Alignment'),
        ('transform', 'Transform'),
        ('history', 'History'),
        ('custom', 'Custom'),
    ]
    
    # Shortcut definition
    action_id = models.CharField(max_length=100, unique=True)  # e.g., 'tool.select', 'edit.undo'
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        ShortcutCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shortcuts'
    )
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, default='action')
    
    # Default key binding
    default_key = models.CharField(max_length=50)  # e.g., 'Ctrl+Z', 'V', 'Shift+Alt+C'
    
    # Platform-specific defaults
    default_key_mac = models.CharField(max_length=50, blank=True)  # e.g., 'Cmd+Z'
    default_key_windows = models.CharField(max_length=50, blank=True)
    default_key_linux = models.CharField(max_length=50, blank=True)
    
    # Metadata
    is_system = models.BooleanField(default=True)  # System shortcut vs user-defined
    is_customizable = models.BooleanField(default=True)
    requires_selection = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.default_key})"
    
    def get_key_for_platform(self, platform='default'):
        """Get the key binding for a specific platform."""
        if platform == 'mac' and self.default_key_mac:
            return self.default_key_mac
        elif platform == 'windows' and self.default_key_windows:
            return self.default_key_windows
        elif platform == 'linux' and self.default_key_linux:
            return self.default_key_linux
        return self.default_key


class UserShortcutOverride(models.Model):
    """
    User-specific shortcut customization.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shortcut_overrides'
    )
    shortcut = models.ForeignKey(
        KeyboardShortcut,
        on_delete=models.CASCADE,
        related_name='overrides'
    )
    
    # Custom key binding
    custom_key = models.CharField(max_length=50)
    
    # Override settings
    is_enabled = models.BooleanField(default=True)  # Allow disabling shortcuts
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'shortcut']
    
    def __str__(self):
        return f"{self.user.username}: {self.shortcut.name} -> {self.custom_key}"


class ShortcutPreset(models.Model):
    """
    Preset collection of shortcut mappings.
    E.g., "Photoshop", "Figma", "Sketch" compatible layouts.
    """
    PRESET_TYPES = [
        ('system', 'System Preset'),
        ('app', 'Application Preset'),
        ('user', 'User Preset'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    preset_type = models.CharField(max_length=20, choices=PRESET_TYPES, default='user')
    
    # For user presets
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shortcut_presets'
    )
    
    # Shortcut mappings: {action_id: key_binding}
    mappings = models.JSONField(default=dict)
    
    # Metadata
    icon = models.CharField(max_length=50, blank=True)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['preset_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.preset_type})"


class ShortcutUsageLog(models.Model):
    """
    Track shortcut usage for learning mode analytics.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shortcut_usage'
    )
    shortcut = models.ForeignKey(
        KeyboardShortcut,
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    # Was the shortcut used, or was the action done via UI?
    used_shortcut = models.BooleanField(default=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


class LearningModeSettings(models.Model):
    """
    User settings for shortcut learning mode.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shortcut_learning_settings'
    )
    
    # Learning mode toggle
    is_enabled = models.BooleanField(default=False)
    
    # Show shortcut hints on UI actions
    show_hints = models.BooleanField(default=True)
    
    # Categories to learn
    learning_categories = models.JSONField(default=list)  # List of category IDs
    
    # Daily goal
    daily_goal = models.IntegerField(default=10)  # Shortcuts to learn per day
    
    # Progress tracking
    shortcuts_learned = models.JSONField(default=list)  # List of action_ids mastered
    current_streak = models.IntegerField(default=0)
    best_streak = models.IntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Learning settings for {self.user.username}"


class ShortcutsService:
    """
    Service for managing keyboard shortcuts.
    """
    
    def __init__(self, user):
        self.user = user
    
    def get_all_shortcuts(self, platform='default', include_disabled=False):
        """
        Get all shortcuts with user overrides applied.
        """
        shortcuts = KeyboardShortcut.objects.select_related('category').all()
        overrides = {
            o.shortcut_id: o 
            for o in UserShortcutOverride.objects.filter(user=self.user)
        }
        
        result = []
        for shortcut in shortcuts:
            override = overrides.get(shortcut.id)
            
            # Skip disabled shortcuts unless requested
            if override and not override.is_enabled and not include_disabled:
                continue
            
            result.append({
                'action_id': shortcut.action_id,
                'name': shortcut.name,
                'description': shortcut.description,
                'category': shortcut.category.name if shortcut.category else 'General',
                'action_type': shortcut.action_type,
                'key': override.custom_key if override else shortcut.get_key_for_platform(platform),
                'default_key': shortcut.get_key_for_platform(platform),
                'is_custom': bool(override),
                'is_enabled': override.is_enabled if override else True,
                'is_customizable': shortcut.is_customizable,
                'requires_selection': shortcut.requires_selection,
            })
        
        return result
    
    def get_shortcuts_by_category(self, platform='default'):
        """
        Get shortcuts organized by category.
        """
        all_shortcuts = self.get_all_shortcuts(platform)
        
        categories = {}
        for shortcut in all_shortcuts:
            cat = shortcut['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(shortcut)
        
        return categories
    
    def set_shortcut(self, action_id, key):
        """
        Set a custom key binding for a shortcut.
        """
        shortcut = KeyboardShortcut.objects.get(action_id=action_id)
        
        if not shortcut.is_customizable:
            raise ValueError(f"Shortcut '{action_id}' is not customizable")
        
        # Check for conflicts
        conflict = self._check_conflict(key, action_id)
        if conflict:
            raise ValueError(f"Key '{key}' conflicts with '{conflict['name']}'")
        
        override, created = UserShortcutOverride.objects.update_or_create(
            user=self.user,
            shortcut=shortcut,
            defaults={'custom_key': key, 'is_enabled': True}
        )
        
        return {
            'action_id': action_id,
            'key': key,
            'created': created
        }
    
    def reset_shortcut(self, action_id):
        """
        Reset a shortcut to its default binding.
        """
        shortcut = KeyboardShortcut.objects.get(action_id=action_id)
        
        UserShortcutOverride.objects.filter(
            user=self.user,
            shortcut=shortcut
        ).delete()
        
        return {
            'action_id': action_id,
            'key': shortcut.default_key
        }
    
    def reset_all_shortcuts(self):
        """
        Reset all shortcuts to defaults.
        """
        count = UserShortcutOverride.objects.filter(user=self.user).delete()[0]
        return {'reset_count': count}
    
    def toggle_shortcut(self, action_id, enabled):
        """
        Enable or disable a shortcut.
        """
        shortcut = KeyboardShortcut.objects.get(action_id=action_id)
        
        override, created = UserShortcutOverride.objects.get_or_create(
            user=self.user,
            shortcut=shortcut,
            defaults={'custom_key': shortcut.default_key}
        )
        
        override.is_enabled = enabled
        override.save()
        
        return {
            'action_id': action_id,
            'is_enabled': enabled
        }
    
    def _check_conflict(self, key, exclude_action_id=None):
        """
        Check if a key binding conflicts with existing shortcuts.
        """
        all_shortcuts = self.get_all_shortcuts()
        
        for shortcut in all_shortcuts:
            if shortcut['action_id'] != exclude_action_id and shortcut['key'].lower() == key.lower():
                return shortcut
        
        return None
    
    def apply_preset(self, preset_id):
        """
        Apply a shortcut preset.
        """
        preset = ShortcutPreset.objects.get(id=preset_id)
        
        # Clear existing overrides
        UserShortcutOverride.objects.filter(user=self.user).delete()
        
        # Apply preset mappings
        for action_id, key in preset.mappings.items():
            try:
                shortcut = KeyboardShortcut.objects.get(action_id=action_id)
                if shortcut.is_customizable:
                    UserShortcutOverride.objects.create(
                        user=self.user,
                        shortcut=shortcut,
                        custom_key=key
                    )
            except KeyboardShortcut.DoesNotExist:
                continue
        
        return {
            'preset_name': preset.name,
            'shortcuts_applied': len(preset.mappings)
        }
    
    def save_as_preset(self, name, description=''):
        """
        Save current shortcuts as a new preset.
        """
        all_shortcuts = self.get_all_shortcuts()
        mappings = {
            s['action_id']: s['key']
            for s in all_shortcuts
            if s['is_custom']
        }
        
        preset = ShortcutPreset.objects.create(
            user=self.user,
            name=name,
            description=description,
            preset_type='user',
            mappings=mappings
        )
        
        return {
            'preset_id': preset.id,
            'name': preset.name,
            'shortcut_count': len(mappings)
        }
    
    def export_shortcuts(self):
        """
        Export shortcuts to JSON.
        """
        all_shortcuts = self.get_all_shortcuts()
        
        return {
            'exported_at': timezone.now().isoformat(),
            'user': self.user.username,
            'shortcuts': all_shortcuts
        }
    
    def import_shortcuts(self, data):
        """
        Import shortcuts from JSON.
        """
        shortcuts_data = data.get('shortcuts', [])
        imported = 0
        
        for shortcut_data in shortcuts_data:
            if shortcut_data.get('is_custom'):
                try:
                    self.set_shortcut(
                        shortcut_data['action_id'],
                        shortcut_data['key']
                    )
                    imported += 1
                except (KeyboardShortcut.DoesNotExist, ValueError):
                    continue
        
        return {'imported_count': imported}
    
    def generate_cheat_sheet(self, format='html'):
        """
        Generate a printable cheat sheet of all shortcuts.
        """
        categories = self.get_shortcuts_by_category()
        
        if format == 'html':
            return self._generate_html_cheat_sheet(categories)
        elif format == 'markdown':
            return self._generate_markdown_cheat_sheet(categories)
        elif format == 'json':
            return categories
        
        return categories
    
    def _generate_html_cheat_sheet(self, categories):
        """Generate HTML cheat sheet."""
        html = ['<div class="cheat-sheet">']
        html.append('<h1>Keyboard Shortcuts</h1>')
        
        for category, shortcuts in categories.items():
            html.append('<div class="category">')
            html.append(f'<h2>{category}</h2>')
            html.append('<table>')
            html.append('<tr><th>Action</th><th>Shortcut</th></tr>')
            
            for s in shortcuts:
                html.append(f'<tr><td>{s["name"]}</td><td><kbd>{s["key"]}</kbd></td></tr>')
            
            html.append('</table>')
            html.append('</div>')
        
        html.append('</div>')
        return '\n'.join(html)
    
    def _generate_markdown_cheat_sheet(self, categories):
        """Generate Markdown cheat sheet."""
        md = ['# Keyboard Shortcuts\n']
        
        for category, shortcuts in categories.items():
            md.append(f'## {category}\n')
            md.append('| Action | Shortcut |')
            md.append('|--------|----------|')
            
            for s in shortcuts:
                md.append(f'| {s["name"]} | `{s["key"]}` |')
            
            md.append('')
        
        return '\n'.join(md)
    
    def log_usage(self, action_id, used_shortcut=True):
        """
        Log shortcut usage for learning analytics.
        """
        try:
            shortcut = KeyboardShortcut.objects.get(action_id=action_id)
            ShortcutUsageLog.objects.create(
                user=self.user,
                shortcut=shortcut,
                used_shortcut=used_shortcut
            )
        except KeyboardShortcut.DoesNotExist:
            pass
    
    def get_learning_stats(self):
        """
        Get learning mode statistics.
        """
        settings, created = LearningModeSettings.objects.get_or_create(
            user=self.user
        )
        
        # Count today's usage
        today = timezone.now().date()
        today_logs = ShortcutUsageLog.objects.filter(
            user=self.user,
            timestamp__date=today
        )
        
        shortcuts_used_today = today_logs.filter(used_shortcut=True).values('shortcut').distinct().count()
        actions_via_ui = today_logs.filter(used_shortcut=False).count()
        
        # Get most used shortcuts
        from django.db.models import Count
        most_used = ShortcutUsageLog.objects.filter(
            user=self.user,
            used_shortcut=True
        ).values('shortcut__name', 'shortcut__action_id').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Get shortcuts to learn (used via UI but not via shortcut)
        to_learn = ShortcutUsageLog.objects.filter(
            user=self.user,
            used_shortcut=False
        ).values('shortcut__name', 'shortcut__action_id', 'shortcut__default_key').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'is_learning_mode': settings.is_enabled,
            'daily_goal': settings.daily_goal,
            'shortcuts_used_today': shortcuts_used_today,
            'actions_via_ui_today': actions_via_ui,
            'current_streak': settings.current_streak,
            'best_streak': settings.best_streak,
            'shortcuts_learned': len(settings.shortcuts_learned),
            'most_used': list(most_used),
            'to_learn': list(to_learn),
        }
    
    def toggle_learning_mode(self, enabled):
        """
        Toggle learning mode on/off.
        """
        settings, created = LearningModeSettings.objects.get_or_create(
            user=self.user
        )
        settings.is_enabled = enabled
        settings.save()
        
        return {'is_enabled': enabled}
    
    def search_shortcuts(self, query):
        """
        Search shortcuts by name or key.
        """
        all_shortcuts = self.get_all_shortcuts()
        query = query.lower()
        
        results = [
            s for s in all_shortcuts
            if query in s['name'].lower() or 
               query in s['key'].lower() or
               query in s.get('description', '').lower()
        ]
        
        return results
    
    @staticmethod
    def get_default_shortcuts():
        """
        Return default shortcut definitions.
        """
        return [
            # Selection & Tools
            {'action_id': 'tool.select', 'name': 'Select Tool', 'key': 'V', 'category': 'Tools'},
            {'action_id': 'tool.hand', 'name': 'Hand Tool', 'key': 'H', 'category': 'Tools'},
            {'action_id': 'tool.zoom', 'name': 'Zoom Tool', 'key': 'Z', 'category': 'Tools'},
            {'action_id': 'tool.rectangle', 'name': 'Rectangle Tool', 'key': 'R', 'category': 'Tools'},
            {'action_id': 'tool.ellipse', 'name': 'Ellipse Tool', 'key': 'O', 'category': 'Tools'},
            {'action_id': 'tool.line', 'name': 'Line Tool', 'key': 'L', 'category': 'Tools'},
            {'action_id': 'tool.pen', 'name': 'Pen Tool', 'key': 'P', 'category': 'Tools'},
            {'action_id': 'tool.text', 'name': 'Text Tool', 'key': 'T', 'category': 'Tools'},
            {'action_id': 'tool.frame', 'name': 'Frame Tool', 'key': 'F', 'category': 'Tools'},
            
            # Edit
            {'action_id': 'edit.undo', 'name': 'Undo', 'key': 'Ctrl+Z', 'key_mac': 'Cmd+Z', 'category': 'Edit'},
            {'action_id': 'edit.redo', 'name': 'Redo', 'key': 'Ctrl+Shift+Z', 'key_mac': 'Cmd+Shift+Z', 'category': 'Edit'},
            {'action_id': 'edit.cut', 'name': 'Cut', 'key': 'Ctrl+X', 'key_mac': 'Cmd+X', 'category': 'Edit'},
            {'action_id': 'edit.copy', 'name': 'Copy', 'key': 'Ctrl+C', 'key_mac': 'Cmd+C', 'category': 'Edit'},
            {'action_id': 'edit.paste', 'name': 'Paste', 'key': 'Ctrl+V', 'key_mac': 'Cmd+V', 'category': 'Edit'},
            {'action_id': 'edit.duplicate', 'name': 'Duplicate', 'key': 'Ctrl+D', 'key_mac': 'Cmd+D', 'category': 'Edit'},
            {'action_id': 'edit.delete', 'name': 'Delete', 'key': 'Delete', 'category': 'Edit'},
            {'action_id': 'edit.select_all', 'name': 'Select All', 'key': 'Ctrl+A', 'key_mac': 'Cmd+A', 'category': 'Edit'},
            
            # View
            {'action_id': 'view.zoom_in', 'name': 'Zoom In', 'key': 'Ctrl++', 'key_mac': 'Cmd++', 'category': 'View'},
            {'action_id': 'view.zoom_out', 'name': 'Zoom Out', 'key': 'Ctrl+-', 'key_mac': 'Cmd+-', 'category': 'View'},
            {'action_id': 'view.zoom_fit', 'name': 'Zoom to Fit', 'key': 'Ctrl+1', 'key_mac': 'Cmd+1', 'category': 'View'},
            {'action_id': 'view.zoom_100', 'name': 'Zoom to 100%', 'key': 'Ctrl+0', 'key_mac': 'Cmd+0', 'category': 'View'},
            {'action_id': 'view.toggle_grid', 'name': 'Toggle Grid', 'key': "Ctrl+'", 'key_mac': "Cmd+'", 'category': 'View'},
            {'action_id': 'view.toggle_rulers', 'name': 'Toggle Rulers', 'key': 'Ctrl+R', 'key_mac': 'Cmd+R', 'category': 'View'},
            
            # Layers
            {'action_id': 'layer.bring_front', 'name': 'Bring to Front', 'key': 'Ctrl+]', 'key_mac': 'Cmd+]', 'category': 'Layers'},
            {'action_id': 'layer.send_back', 'name': 'Send to Back', 'key': 'Ctrl+[', 'key_mac': 'Cmd+[', 'category': 'Layers'},
            {'action_id': 'layer.group', 'name': 'Group', 'key': 'Ctrl+G', 'key_mac': 'Cmd+G', 'category': 'Layers'},
            {'action_id': 'layer.ungroup', 'name': 'Ungroup', 'key': 'Ctrl+Shift+G', 'key_mac': 'Cmd+Shift+G', 'category': 'Layers'},
            {'action_id': 'layer.lock', 'name': 'Lock/Unlock', 'key': 'Ctrl+L', 'key_mac': 'Cmd+L', 'category': 'Layers'},
            
            # Align
            {'action_id': 'align.left', 'name': 'Align Left', 'key': 'Alt+A', 'category': 'Align'},
            {'action_id': 'align.center', 'name': 'Align Center', 'key': 'Alt+H', 'category': 'Align'},
            {'action_id': 'align.right', 'name': 'Align Right', 'key': 'Alt+D', 'category': 'Align'},
            {'action_id': 'align.top', 'name': 'Align Top', 'key': 'Alt+W', 'category': 'Align'},
            {'action_id': 'align.middle', 'name': 'Align Middle', 'key': 'Alt+V', 'category': 'Align'},
            {'action_id': 'align.bottom', 'name': 'Align Bottom', 'key': 'Alt+S', 'category': 'Align'},
            
            # File
            {'action_id': 'file.new', 'name': 'New Project', 'key': 'Ctrl+N', 'key_mac': 'Cmd+N', 'category': 'File'},
            {'action_id': 'file.open', 'name': 'Open Project', 'key': 'Ctrl+O', 'key_mac': 'Cmd+O', 'category': 'File'},
            {'action_id': 'file.save', 'name': 'Save', 'key': 'Ctrl+S', 'key_mac': 'Cmd+S', 'category': 'File'},
            {'action_id': 'file.export', 'name': 'Export', 'key': 'Ctrl+Shift+E', 'key_mac': 'Cmd+Shift+E', 'category': 'File'},
        ]
    
    @staticmethod
    def get_application_presets():
        """
        Return popular application preset configurations.
        """
        return {
            'photoshop': {
                'name': 'Adobe Photoshop',
                'icon': 'photoshop',
                'mappings': {
                    'tool.select': 'V',
                    'tool.hand': 'H',
                    'tool.zoom': 'Z',
                    'tool.rectangle': 'U',
                    'tool.pen': 'P',
                    'tool.text': 'T',
                    'edit.free_transform': 'Ctrl+T',
                }
            },
            'figma': {
                'name': 'Figma',
                'icon': 'figma',
                'mappings': {
                    'tool.select': 'V',
                    'tool.hand': 'H',
                    'tool.frame': 'F',
                    'tool.rectangle': 'R',
                    'tool.ellipse': 'O',
                    'tool.line': 'L',
                    'tool.pen': 'P',
                    'tool.text': 'T',
                }
            },
            'sketch': {
                'name': 'Sketch',
                'icon': 'sketch',
                'mappings': {
                    'tool.select': 'V',
                    'tool.rectangle': 'R',
                    'tool.ellipse': 'O',
                    'tool.line': 'L',
                    'tool.text': 'T',
                    'layer.group': 'Cmd+G',
                }
            }
        }

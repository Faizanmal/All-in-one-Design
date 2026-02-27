"""
Smart Selection & Magic Tools Models

Provides models for:
- Smart selection presets and queries
- Batch operations history
- Find & replace operations
- Batch rename templates
"""

from django.db import models
from django.conf import settings
import uuid
import re


class SmartSelectionPreset(models.Model):
    """
    Saved smart selection queries for reuse.
    """
    
    PRESET_TYPES = [
        ('layer_type', 'By Layer Type'),
        ('property', 'By Property'),
        ('style', 'By Style'),
        ('name', 'By Name Pattern'),
        ('size', 'By Size'),
        ('position', 'By Position'),
        ('custom', 'Custom Query'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selection_presets')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preset_type = models.CharField(max_length=20, choices=PRESET_TYPES)
    
    # Selection criteria (JSON query format)
    query = models.JSONField(help_text='Selection query in JSON format')
    # Example queries:
    # {"layer_type": "text"}
    # {"property": {"fill_color": "#FF0000"}}
    # {"style": {"font_family": "Inter"}}
    # {"name_pattern": "Button*"}
    # {"size": {"width": {"gte": 100, "lte": 200}}}
    
    # UI configuration
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    keyboard_shortcut = models.CharField(max_length=50, blank=True)
    
    # Usage tracking
    use_count = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    is_system = models.BooleanField(default=False, help_text='System presets cannot be deleted')
    is_favorite = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_favorite', '-use_count', 'name']
        verbose_name = 'Smart Selection Preset'
        verbose_name_plural = 'Smart Selection Presets'
    
    def __str__(self):
        return self.name


class BatchOperation(models.Model):
    """
    Records batch operations for undo/redo and history.
    """
    
    OPERATION_TYPES = [
        ('rename', 'Batch Rename'),
        ('resize', 'Batch Resize'),
        ('style', 'Batch Style Change'),
        ('transform', 'Batch Transform'),
        ('replace', 'Find & Replace'),
        ('delete', 'Batch Delete'),
        ('duplicate', 'Batch Duplicate'),
        ('align', 'Batch Align'),
        ('distribute', 'Batch Distribute'),
        ('group', 'Batch Group'),
        ('ungroup', 'Batch Ungroup'),
        ('lock', 'Batch Lock'),
        ('unlock', 'Batch Unlock'),
        ('show', 'Batch Show'),
        ('hide', 'Batch Hide'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('undone', 'Undone'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='batch_operations_smart_tools')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='batch_operations_smart_tools')
    
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Affected components
    component_ids = models.JSONField(help_text='Array of affected component IDs')
    component_count = models.IntegerField(default=0)
    
    # Operation details
    operation_data = models.JSONField(help_text='Operation parameters')
    
    # State for undo
    previous_state = models.JSONField(help_text='Previous state of components')
    
    # Results
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    error_messages = models.JSONField(default=list)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Batch Operation'
        verbose_name_plural = 'Batch Operations'
    
    def __str__(self):
        return f"{self.get_operation_type_display()} - {self.component_count} items"


class RenameTemplate(models.Model):
    """
    Templates for batch renaming layers.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rename_templates')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Template pattern
    pattern = models.CharField(max_length=500, help_text='Rename pattern with placeholders')
    # Placeholders:
    # {name} - Original name
    # {n} - Sequential number
    # {n:3} - Sequential number with padding (001, 002)
    # {type} - Layer type
    # {parent} - Parent layer name
    # {date} - Current date
    # {time} - Current time
    # {width} - Layer width
    # {height} - Layer height
    
    # Options
    start_number = models.IntegerField(default=1)
    number_step = models.IntegerField(default=1)
    preserve_extension = models.BooleanField(default=True)
    
    # Case transformation
    CASE_TRANSFORMS = [
        ('none', 'No Change'),
        ('lower', 'lowercase'),
        ('upper', 'UPPERCASE'),
        ('title', 'Title Case'),
        ('sentence', 'Sentence case'),
        ('camel', 'camelCase'),
        ('pascal', 'PascalCase'),
        ('snake', 'snake_case'),
        ('kebab', 'kebab-case'),
    ]
    case_transform = models.CharField(max_length=20, choices=CASE_TRANSFORMS, default='none')
    
    is_favorite = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_favorite', '-use_count', 'name']
        verbose_name = 'Rename Template'
        verbose_name_plural = 'Rename Templates'
    
    def __str__(self):
        return self.name
    
    def apply_to_name(self, original_name: str, index: int, context: dict = None) -> str:
        """Apply template pattern to a name."""
        context = context or {}
        
        number = self.start_number + (index * self.number_step)
        
        result = self.pattern
        
        # Basic replacements
        result = result.replace('{name}', original_name)
        result = result.replace('{n}', str(number))
        result = result.replace('{type}', context.get('type', ''))
        result = result.replace('{parent}', context.get('parent', ''))
        result = result.replace('{width}', str(context.get('width', '')))
        result = result.replace('{height}', str(context.get('height', '')))
        
        # Padded numbers
        import re
        pattern = r'\{n:(\d+)\}'
        for match in re.finditer(pattern, result):
            padding = int(match.group(1))
            padded_number = str(number).zfill(padding)
            result = result.replace(match.group(0), padded_number)
        
        # Date/time
        from datetime import datetime
        now = datetime.now()
        result = result.replace('{date}', now.strftime('%Y-%m-%d'))
        result = result.replace('{time}', now.strftime('%H-%M-%S'))
        
        # Apply case transformation
        result = self._apply_case_transform(result)
        
        return result
    
    def _apply_case_transform(self, text: str) -> str:
        """Apply case transformation to text."""
        if self.case_transform == 'lower':
            return text.lower()
        elif self.case_transform == 'upper':
            return text.upper()
        elif self.case_transform == 'title':
            return text.title()
        elif self.case_transform == 'sentence':
            return text.capitalize()
        elif self.case_transform == 'camel':
            words = re.split(r'[\s_-]+', text)
            return words[0].lower() + ''.join(w.title() for w in words[1:])
        elif self.case_transform == 'pascal':
            words = re.split(r'[\s_-]+', text)
            return ''.join(w.title() for w in words)
        elif self.case_transform == 'snake':
            return re.sub(r'[\s-]+', '_', text).lower()
        elif self.case_transform == 'kebab':
            return re.sub(r'[\s_]+', '-', text).lower()
        return text


class FindReplaceOperation(models.Model):
    """
    Find and replace operations on design elements.
    """
    
    TARGET_TYPES = [
        ('text', 'Text Content'),
        ('layer_name', 'Layer Names'),
        ('color', 'Colors'),
        ('font', 'Fonts'),
        ('effect', 'Effects'),
        ('style', 'Styles'),
    ]
    
    SCOPE_CHOICES = [
        ('selection', 'Selection Only'),
        ('page', 'Current Page'),
        ('project', 'Entire Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='find_replace_ops')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='find_replace_ops')
    
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='project')
    
    # Search criteria
    find_value = models.TextField(help_text='Value to find')
    replace_value = models.TextField(help_text='Value to replace with')
    
    # Options
    use_regex = models.BooleanField(default=False)
    case_sensitive = models.BooleanField(default=False)
    whole_word = models.BooleanField(default=False)
    
    # For color replacement
    color_tolerance = models.IntegerField(default=0, help_text='Color matching tolerance (0-100)')
    
    # Results
    matches_found = models.IntegerField(default=0)
    replacements_made = models.IntegerField(default=0)
    affected_components = models.JSONField(default=list)
    
    # State for undo
    previous_state = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Find & Replace Operation'
        verbose_name_plural = 'Find & Replace Operations'
    
    def __str__(self):
        return f"Replace '{self.find_value}' with '{self.replace_value}'"


class ResizePreset(models.Model):
    """
    Presets for batch resizing operations.
    """
    
    RESIZE_MODES = [
        ('absolute', 'Absolute Size'),
        ('scale', 'Scale Factor'),
        ('fit', 'Fit to Size'),
        ('fill', 'Fill to Size'),
        ('width', 'Set Width (Proportional)'),
        ('height', 'Set Height (Proportional)'),
    ]
    
    ANCHOR_POINTS = [
        ('top-left', 'Top Left'),
        ('top-center', 'Top Center'),
        ('top-right', 'Top Right'),
        ('center-left', 'Center Left'),
        ('center', 'Center'),
        ('center-right', 'Center Right'),
        ('bottom-left', 'Bottom Left'),
        ('bottom-center', 'Bottom Center'),
        ('bottom-right', 'Bottom Right'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resize_presets')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    resize_mode = models.CharField(max_length=20, choices=RESIZE_MODES)
    
    # Size values (interpretation depends on mode)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    scale_x = models.FloatField(default=1.0)
    scale_y = models.FloatField(default=1.0)
    
    # Options
    maintain_aspect_ratio = models.BooleanField(default=True)
    anchor = models.CharField(max_length=20, choices=ANCHOR_POINTS, default='center')
    round_to_pixels = models.BooleanField(default=True)
    
    # Constraints
    min_width = models.FloatField(null=True, blank=True)
    min_height = models.FloatField(null=True, blank=True)
    max_width = models.FloatField(null=True, blank=True)
    max_height = models.FloatField(null=True, blank=True)
    
    is_favorite = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_favorite', '-use_count', 'name']
        verbose_name = 'Resize Preset'
        verbose_name_plural = 'Resize Presets'
    
    def __str__(self):
        return self.name


class SelectionHistory(models.Model):
    """
    Tracks selection history for smart selection suggestions.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='selection_history')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='selection_history')
    
    # What was selected
    selection_query = models.JSONField(help_text='Query that was used or inferred')
    selected_ids = models.JSONField(help_text='IDs of selected components')
    component_count = models.IntegerField(default=0)
    
    # Context
    action_taken = models.CharField(max_length=50, blank=True, help_text='Action taken after selection')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Selection History'
        verbose_name_plural = 'Selection History'


class MagicWand(models.Model):
    """
    Magic wand selection settings for color/style based selection.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='magic_wand_settings')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='magic_wand_settings')
    
    # Tolerance settings
    color_tolerance = models.IntegerField(default=10, help_text='Color matching tolerance (0-255)')
    include_similar_fonts = models.BooleanField(default=False)
    include_similar_sizes = models.BooleanField(default=False)
    size_tolerance = models.FloatField(default=5.0, help_text='Size tolerance in pixels')
    
    # Scope
    search_scope = models.CharField(max_length=20, default='page', choices=[
        ('page', 'Current Page'),
        ('project', 'Entire Project'),
        ('selection', 'Within Selection'),
    ])
    
    # What to match
    match_fill = models.BooleanField(default=True)
    match_stroke = models.BooleanField(default=True)
    match_font = models.BooleanField(default=False)
    match_effects = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Magic Wand Settings'
        verbose_name_plural = 'Magic Wand Settings'

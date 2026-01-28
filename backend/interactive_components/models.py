"""
Interactive Components Models

Components that have internal interactions for advanced prototyping.
Examples: Dropdowns that open, carousels that swipe, accordions that expand.
"""

from django.db import models
from django.conf import settings
import uuid


class InteractiveComponent(models.Model):
    """
    A component with built-in interactive behaviors.
    """
    
    COMPONENT_TYPES = [
        ('dropdown', 'Dropdown Menu'),
        ('carousel', 'Carousel/Slider'),
        ('accordion', 'Accordion'),
        ('tabs', 'Tab Container'),
        ('modal', 'Modal/Dialog'),
        ('tooltip', 'Tooltip'),
        ('popover', 'Popover'),
        ('drawer', 'Drawer/Sidebar'),
        ('toggle', 'Toggle Switch'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Button Group'),
        ('input', 'Input Field'),
        ('select', 'Select/Combobox'),
        ('date_picker', 'Date Picker'),
        ('slider', 'Range Slider'),
        ('progress', 'Progress Bar'),
        ('stepper', 'Stepper/Wizard'),
        ('pagination', 'Pagination'),
        ('video_player', 'Video Player'),
        ('audio_player', 'Audio Player'),
        ('custom', 'Custom Interactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='interactive_components')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=30, choices=COMPONENT_TYPES)
    description = models.TextField(blank=True)
    
    # Visual states
    default_state = models.CharField(max_length=50, default='default')
    
    # Component configuration
    config = models.JSONField(default=dict)
    # Examples:
    # dropdown: {"options": [...], "placeholder": "Select...", "multiSelect": false}
    # carousel: {"autoPlay": true, "interval": 3000, "showDots": true, "showArrows": true}
    # accordion: {"allowMultiple": false, "defaultExpanded": [0]}
    
    # Styling
    styles = models.JSONField(default=dict)
    
    # Position and size
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    width = models.FloatField(default=200)
    height = models.FloatField(default=100)
    
    # Layer info
    z_index = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
        verbose_name = 'Interactive Component'
        verbose_name_plural = 'Interactive Components'
    
    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"


class ComponentState(models.Model):
    """
    Visual state of an interactive component.
    Each component can have multiple states (default, hover, active, disabled, etc.)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(InteractiveComponent, on_delete=models.CASCADE, related_name='states')
    
    name = models.CharField(max_length=100)  # e.g., "open", "closed", "hover", "active"
    description = models.TextField(blank=True)
    
    # State properties (styling overrides)
    properties = models.JSONField(default=dict)
    
    # Visual elements in this state
    elements = models.JSONField(default=list)
    # Each element: {"id": "...", "type": "...", "properties": {...}}
    
    # Transitions
    enter_transition = models.JSONField(default=dict)
    # {"duration": 300, "easing": "ease-in-out", "delay": 0}
    
    exit_transition = models.JSONField(default=dict)
    
    is_default = models.BooleanField(default=False)
    
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['component', 'name']
    
    def __str__(self):
        return f"{self.component.name} - {self.name}"


class ComponentInteraction(models.Model):
    """
    Defines interactions that trigger state changes or actions.
    """
    
    TRIGGER_TYPES = [
        ('click', 'On Click'),
        ('hover', 'On Hover'),
        ('hover_end', 'On Hover End'),
        ('focus', 'On Focus'),
        ('blur', 'On Blur'),
        ('key_press', 'On Key Press'),
        ('swipe_left', 'On Swipe Left'),
        ('swipe_right', 'On Swipe Right'),
        ('swipe_up', 'On Swipe Up'),
        ('swipe_down', 'On Swipe Down'),
        ('drag', 'On Drag'),
        ('drop', 'On Drop'),
        ('scroll', 'On Scroll'),
        ('timer', 'On Timer'),
        ('value_change', 'On Value Change'),
        ('load', 'On Load'),
        ('custom', 'Custom Event'),
    ]
    
    ACTION_TYPES = [
        ('change_state', 'Change State'),
        ('toggle_state', 'Toggle State'),
        ('set_variable', 'Set Variable'),
        ('navigate', 'Navigate To'),
        ('open_url', 'Open URL'),
        ('play_animation', 'Play Animation'),
        ('stop_animation', 'Stop Animation'),
        ('show_component', 'Show Component'),
        ('hide_component', 'Hide Component'),
        ('enable', 'Enable Component'),
        ('disable', 'Disable Component'),
        ('scroll_to', 'Scroll To'),
        ('play_video', 'Play Video'),
        ('pause_video', 'Pause Video'),
        ('play_audio', 'Play Audio'),
        ('custom', 'Custom Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(InteractiveComponent, on_delete=models.CASCADE, related_name='interactions')
    
    name = models.CharField(max_length=255, blank=True)
    
    # Trigger
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES)
    trigger_target = models.CharField(max_length=100, blank=True)  # Element ID within component
    trigger_config = models.JSONField(default=dict)
    # Examples:
    # key_press: {"key": "Enter"}
    # timer: {"delay": 2000}
    # swipe: {"threshold": 50}
    
    # Condition (optional)
    condition = models.JSONField(null=True, blank=True)
    # {"variable": "isLoggedIn", "operator": "equals", "value": true}
    
    # Action
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_config = models.JSONField(default=dict)
    # Examples:
    # change_state: {"targetState": "open"}
    # set_variable: {"variable": "selectedIndex", "value": 0}
    # navigate: {"screen": "screen_id", "transition": "slide"}
    
    # Execution order
    order = models.IntegerField(default=0)
    
    is_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.get_trigger_type_display()} → {self.get_action_type_display()}"


class ComponentVariable(models.Model):
    """
    Variables that store state within a component.
    """
    
    VARIABLE_TYPES = [
        ('string', 'String'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('array', 'Array'),
        ('object', 'Object'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(InteractiveComponent, on_delete=models.CASCADE, related_name='variables')
    
    name = models.CharField(max_length=100)
    variable_type = models.CharField(max_length=20, choices=VARIABLE_TYPES)
    default_value = models.JSONField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    
    # Constraints
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    options = models.JSONField(null=True, blank=True)  # For enum-like constraints
    
    class Meta:
        unique_together = ['component', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.variable_type})"


class CarouselItem(models.Model):
    """
    Individual items in a carousel component.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(
        InteractiveComponent, 
        on_delete=models.CASCADE, 
        related_name='carousel_items',
        limit_choices_to={'component_type': 'carousel'}
    )
    
    # Content
    content_type = models.CharField(max_length=20, choices=[
        ('image', 'Image'),
        ('video', 'Video'),
        ('component', 'Component'),
        ('custom', 'Custom HTML'),
    ])
    content = models.JSONField(default=dict)
    # image: {"url": "...", "alt": "..."}
    # video: {"url": "...", "poster": "...", "autoplay": false}
    # component: {"componentId": "..."}
    
    # Metadata
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class DropdownOption(models.Model):
    """
    Options in a dropdown component.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(
        InteractiveComponent,
        on_delete=models.CASCADE,
        related_name='dropdown_options',
        limit_choices_to={'component_type__in': ['dropdown', 'select']}
    )
    
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, blank=True)
    
    is_disabled = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    
    # For grouped options
    group = models.CharField(max_length=100, blank=True)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class AccordionSection(models.Model):
    """
    Sections in an accordion component.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(
        InteractiveComponent,
        on_delete=models.CASCADE,
        related_name='accordion_sections',
        limit_choices_to={'component_type': 'accordion'}
    )
    
    title = models.CharField(max_length=255)
    content = models.JSONField(default=dict)  # Can be text or component reference
    
    icon = models.CharField(max_length=100, blank=True)
    is_expanded = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class TabItem(models.Model):
    """
    Tabs in a tab container component.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(
        InteractiveComponent,
        on_delete=models.CASCADE,
        related_name='tab_items',
        limit_choices_to={'component_type': 'tabs'}
    )
    
    label = models.CharField(max_length=255)
    content = models.JSONField(default=dict)
    
    icon = models.CharField(max_length=100, blank=True)
    badge = models.CharField(max_length=50, blank=True)
    
    is_active = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']


class InteractiveTemplate(models.Model):
    """
    Pre-built interactive component templates.
    """
    
    CATEGORIES = [
        ('navigation', 'Navigation'),
        ('form', 'Form Elements'),
        ('media', 'Media'),
        ('content', 'Content Display'),
        ('feedback', 'Feedback'),
        ('overlay', 'Overlays'),
        ('commerce', 'E-Commerce'),
        ('social', 'Social Media'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORIES)
    
    component_type = models.CharField(max_length=30, choices=InteractiveComponent.COMPONENT_TYPES)
    
    # Template data (serialized component)
    template_data = models.JSONField()
    
    # Preview
    preview_image = models.URLField(blank=True)
    preview_animation = models.URLField(blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

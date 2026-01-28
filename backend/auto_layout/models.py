"""
Auto-Layout System Models

Production-ready auto-layout system implementing Figma-like responsive frames
with automatic spacing, sizing, constraints, and flex-like behavior.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class AutoLayoutFrame(models.Model):
    """
    A responsive frame that automatically adjusts child spacing and sizing.
    Implements Figma's auto-layout behavior with production-grade features.
    """
    
    # Layout Direction
    DIRECTION_HORIZONTAL = 'horizontal'
    DIRECTION_VERTICAL = 'vertical'
    DIRECTION_WRAP = 'wrap'
    DIRECTION_CHOICES = [
        (DIRECTION_HORIZONTAL, 'Horizontal'),
        (DIRECTION_VERTICAL, 'Vertical'),
        (DIRECTION_WRAP, 'Wrap'),
    ]
    
    # Primary Axis Alignment (Main Axis)
    ALIGN_START = 'start'
    ALIGN_CENTER = 'center'
    ALIGN_END = 'end'
    ALIGN_SPACE_BETWEEN = 'space-between'
    ALIGN_SPACE_AROUND = 'space-around'
    ALIGN_SPACE_EVENLY = 'space-evenly'
    PRIMARY_ALIGN_CHOICES = [
        (ALIGN_START, 'Start'),
        (ALIGN_CENTER, 'Center'),
        (ALIGN_END, 'End'),
        (ALIGN_SPACE_BETWEEN, 'Space Between'),
        (ALIGN_SPACE_AROUND, 'Space Around'),
        (ALIGN_SPACE_EVENLY, 'Space Evenly'),
    ]
    
    # Cross Axis Alignment
    CROSS_ALIGN_CHOICES = [
        (ALIGN_START, 'Start'),
        (ALIGN_CENTER, 'Center'),
        (ALIGN_END, 'End'),
        ('stretch', 'Stretch'),
        ('baseline', 'Baseline'),
    ]
    
    # Sizing Modes
    SIZING_FIXED = 'fixed'
    SIZING_HUG = 'hug'
    SIZING_FILL = 'fill'
    SIZING_CHOICES = [
        (SIZING_FIXED, 'Fixed'),
        (SIZING_HUG, 'Hug Contents'),
        (SIZING_FILL, 'Fill Container'),
    ]
    
    # Overflow Behavior
    OVERFLOW_VISIBLE = 'visible'
    OVERFLOW_HIDDEN = 'hidden'
    OVERFLOW_SCROLL = 'scroll'
    OVERFLOW_AUTO = 'auto'
    OVERFLOW_CHOICES = [
        (OVERFLOW_VISIBLE, 'Visible'),
        (OVERFLOW_HIDDEN, 'Hidden'),
        (OVERFLOW_SCROLL, 'Scroll'),
        (OVERFLOW_AUTO, 'Auto'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.CASCADE, 
        related_name='auto_layout_frames'
    )
    component = models.OneToOneField(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='auto_layout_config',
        null=True,
        blank=True
    )
    
    # Basic Properties
    name = models.CharField(max_length=255, default='Auto Layout Frame')
    enabled = models.BooleanField(default=True)
    
    # Layout Direction and Alignment
    direction = models.CharField(
        max_length=20, 
        choices=DIRECTION_CHOICES, 
        default=DIRECTION_VERTICAL
    )
    primary_axis_alignment = models.CharField(
        max_length=20,
        choices=PRIMARY_ALIGN_CHOICES,
        default=ALIGN_START
    )
    cross_axis_alignment = models.CharField(
        max_length=20,
        choices=CROSS_ALIGN_CHOICES,
        default=ALIGN_START
    )
    
    # Spacing (Gap between items)
    item_spacing = models.FloatField(default=10.0, validators=[MinValueValidator(0)])
    
    # Padding (Individual sides for precise control)
    padding_top = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    padding_right = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    padding_bottom = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    padding_left = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    
    # Sizing Mode
    horizontal_sizing = models.CharField(
        max_length=20,
        choices=SIZING_CHOICES,
        default=SIZING_HUG
    )
    vertical_sizing = models.CharField(
        max_length=20,
        choices=SIZING_CHOICES,
        default=SIZING_HUG
    )
    
    # Size Constraints
    min_width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    min_height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Fixed dimensions (when sizing mode is 'fixed')
    width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Overflow behavior
    overflow_horizontal = models.CharField(
        max_length=20,
        choices=OVERFLOW_CHOICES,
        default=OVERFLOW_VISIBLE
    )
    overflow_vertical = models.CharField(
        max_length=20,
        choices=OVERFLOW_CHOICES,
        default=OVERFLOW_VISIBLE
    )
    
    # Stroke behavior
    stroke_included_in_layout = models.BooleanField(default=True)
    
    # Corner radius (for visual styling)
    corner_radius = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    corner_radius_top_left = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    corner_radius_top_right = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    corner_radius_bottom_right = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    corner_radius_bottom_left = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Background
    background_color = models.CharField(max_length=50, blank=True, default='')
    background_opacity = models.FloatField(
        default=1.0, 
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Clip content to frame bounds
    clip_content = models.BooleanField(default=False)
    
    # Z-ordering
    z_index = models.IntegerField(default=0)
    
    # Nested auto-layout support
    parent_frame = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_frames'
    )
    
    # Absolute positioning (break out of auto-layout)
    absolute_position = models.BooleanField(default=False)
    absolute_x = models.FloatField(null=True, blank=True)
    absolute_y = models.FloatField(null=True, blank=True)
    
    # Canvas position
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_auto_layouts'
    )
    
    class Meta:
        ordering = ['z_index', '-created_at']
        verbose_name = 'Auto Layout Frame'
        verbose_name_plural = 'Auto Layout Frames'
    
    def __str__(self):
        return f"{self.name} ({self.direction})"
    
    def get_computed_padding(self):
        """Get padding as a dict for easy use."""
        return {
            'top': self.padding_top,
            'right': self.padding_right,
            'bottom': self.padding_bottom,
            'left': self.padding_left
        }
    
    def set_uniform_padding(self, value):
        """Set the same padding on all sides."""
        self.padding_top = value
        self.padding_right = value
        self.padding_bottom = value
        self.padding_left = value
        
    def get_corner_radii(self):
        """Get corner radius values, with fallback to uniform radius."""
        return {
            'topLeft': self.corner_radius_top_left or self.corner_radius,
            'topRight': self.corner_radius_top_right or self.corner_radius,
            'bottomRight': self.corner_radius_bottom_right or self.corner_radius,
            'bottomLeft': self.corner_radius_bottom_left or self.corner_radius,
        }


class AutoLayoutChild(models.Model):
    """
    Configuration for a child element within an auto-layout frame.
    Controls how individual items behave within the parent layout.
    """
    
    # Sizing behaviors for child
    SIZING_FIXED = 'fixed'
    SIZING_FILL = 'fill'
    SIZING_HUG = 'hug'
    SIZING_CHOICES = [
        (SIZING_FIXED, 'Fixed'),
        (SIZING_FILL, 'Fill Container'),
        (SIZING_HUG, 'Hug Contents'),
    ]
    
    # Self alignment (override parent's cross-axis alignment)
    ALIGN_AUTO = 'auto'
    ALIGN_START = 'start'
    ALIGN_CENTER = 'center'
    ALIGN_END = 'end'
    ALIGN_STRETCH = 'stretch'
    SELF_ALIGN_CHOICES = [
        (ALIGN_AUTO, 'Auto (Inherit)'),
        (ALIGN_START, 'Start'),
        (ALIGN_CENTER, 'Center'),
        (ALIGN_END, 'End'),
        (ALIGN_STRETCH, 'Stretch'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent_frame = models.ForeignKey(
        AutoLayoutFrame,
        on_delete=models.CASCADE,
        related_name='children'
    )
    component = models.ForeignKey(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='auto_layout_child_config',
        null=True,
        blank=True
    )
    
    # Order in the layout (for reordering children)
    order = models.IntegerField(default=0)
    
    # Sizing
    horizontal_sizing = models.CharField(
        max_length=20,
        choices=SIZING_CHOICES,
        default=SIZING_HUG
    )
    vertical_sizing = models.CharField(
        max_length=20,
        choices=SIZING_CHOICES,
        default=SIZING_HUG
    )
    
    # Fixed size values (when sizing is 'fixed')
    fixed_width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    fixed_height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Fill ratio (for 'fill' mode - relative sizing)
    fill_ratio = models.FloatField(default=1.0, validators=[MinValueValidator(0)])
    
    # Minimum/Maximum constraints
    min_width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_width = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    min_height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    max_height = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Self-alignment (override parent's cross-axis alignment for this child)
    align_self = models.CharField(
        max_length=20,
        choices=SELF_ALIGN_CHOICES,
        default=ALIGN_AUTO
    )
    
    # Flex grow/shrink (CSS flexbox-like behavior)
    flex_grow = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    flex_shrink = models.FloatField(default=1.0, validators=[MinValueValidator(0)])
    
    # Absolute positioning (break out of auto-layout flow)
    is_absolute = models.BooleanField(default=False)
    absolute_x = models.FloatField(null=True, blank=True)
    absolute_y = models.FloatField(null=True, blank=True)
    
    # Absolute position anchor (which corner to anchor to)
    ANCHOR_TOP_LEFT = 'top-left'
    ANCHOR_TOP_CENTER = 'top-center'
    ANCHOR_TOP_RIGHT = 'top-right'
    ANCHOR_CENTER_LEFT = 'center-left'
    ANCHOR_CENTER = 'center'
    ANCHOR_CENTER_RIGHT = 'center-right'
    ANCHOR_BOTTOM_LEFT = 'bottom-left'
    ANCHOR_BOTTOM_CENTER = 'bottom-center'
    ANCHOR_BOTTOM_RIGHT = 'bottom-right'
    ANCHOR_CHOICES = [
        (ANCHOR_TOP_LEFT, 'Top Left'),
        (ANCHOR_TOP_CENTER, 'Top Center'),
        (ANCHOR_TOP_RIGHT, 'Top Right'),
        (ANCHOR_CENTER_LEFT, 'Center Left'),
        (ANCHOR_CENTER, 'Center'),
        (ANCHOR_CENTER_RIGHT, 'Center Right'),
        (ANCHOR_BOTTOM_LEFT, 'Bottom Left'),
        (ANCHOR_BOTTOM_CENTER, 'Bottom Center'),
        (ANCHOR_BOTTOM_RIGHT, 'Bottom Right'),
    ]
    absolute_anchor = models.CharField(
        max_length=20,
        choices=ANCHOR_CHOICES,
        default=ANCHOR_TOP_LEFT
    )
    
    # Visibility
    visible = models.BooleanField(default=True)
    
    # Rotation (degrees)
    rotation = models.FloatField(default=0.0)
    
    # Computed values (cached for performance)
    computed_x = models.FloatField(null=True, blank=True)
    computed_y = models.FloatField(null=True, blank=True)
    computed_width = models.FloatField(null=True, blank=True)
    computed_height = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Auto Layout Child'
        verbose_name_plural = 'Auto Layout Children'
    
    def __str__(self):
        return f"Child {self.order} in {self.parent_frame.name}"


class LayoutConstraint(models.Model):
    """
    Constraints that define how an element responds to its parent's size changes.
    Similar to Figma's constraint system.
    """
    
    # Horizontal Constraints
    CONSTRAINT_LEFT = 'left'
    CONSTRAINT_RIGHT = 'right'
    CONSTRAINT_LEFT_RIGHT = 'left_right'
    CONSTRAINT_CENTER = 'center'
    CONSTRAINT_SCALE = 'scale'
    HORIZONTAL_CHOICES = [
        (CONSTRAINT_LEFT, 'Left'),
        (CONSTRAINT_RIGHT, 'Right'),
        (CONSTRAINT_LEFT_RIGHT, 'Left and Right'),
        (CONSTRAINT_CENTER, 'Center'),
        (CONSTRAINT_SCALE, 'Scale'),
    ]
    
    # Vertical Constraints
    CONSTRAINT_TOP = 'top'
    CONSTRAINT_BOTTOM = 'bottom'
    CONSTRAINT_TOP_BOTTOM = 'top_bottom'
    VERTICAL_CHOICES = [
        (CONSTRAINT_TOP, 'Top'),
        (CONSTRAINT_BOTTOM, 'Bottom'),
        (CONSTRAINT_TOP_BOTTOM, 'Top and Bottom'),
        (CONSTRAINT_CENTER, 'Center'),
        (CONSTRAINT_SCALE, 'Scale'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.OneToOneField(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='layout_constraint'
    )
    
    # Constraint settings
    horizontal = models.CharField(
        max_length=20,
        choices=HORIZONTAL_CHOICES,
        default=CONSTRAINT_LEFT
    )
    vertical = models.CharField(
        max_length=20,
        choices=VERTICAL_CHOICES,
        default=CONSTRAINT_TOP
    )
    
    # Fixed margins (distances from parent edges)
    margin_left = models.FloatField(null=True, blank=True)
    margin_right = models.FloatField(null=True, blank=True)
    margin_top = models.FloatField(null=True, blank=True)
    margin_bottom = models.FloatField(null=True, blank=True)
    
    # Percentage-based positioning (0-100)
    percent_x = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    percent_y = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Percentage-based sizing
    percent_width = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    percent_height = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Aspect ratio lock
    lock_aspect_ratio = models.BooleanField(default=False)
    aspect_ratio = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Layout Constraint'
        verbose_name_plural = 'Layout Constraints'
    
    def __str__(self):
        return f"Constraint: H={self.horizontal}, V={self.vertical}"


class ResponsiveBreakpoint(models.Model):
    """
    Defines responsive breakpoints for adapting layouts to different screen sizes.
    """
    
    DEVICE_DESKTOP = 'desktop'
    DEVICE_TABLET = 'tablet'
    DEVICE_MOBILE = 'mobile'
    DEVICE_CUSTOM = 'custom'
    DEVICE_CHOICES = [
        (DEVICE_DESKTOP, 'Desktop'),
        (DEVICE_TABLET, 'Tablet'),
        (DEVICE_MOBILE, 'Mobile'),
        (DEVICE_CUSTOM, 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='responsive_breakpoints'
    )
    
    name = models.CharField(max_length=100)
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES,
        default=DEVICE_CUSTOM
    )
    
    # Breakpoint range
    min_width = models.IntegerField(validators=[MinValueValidator(0)])
    max_width = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Default canvas dimensions for this breakpoint
    canvas_width = models.IntegerField(default=1920)
    canvas_height = models.IntegerField(default=1080)
    
    # Scale factor
    scale = models.FloatField(default=1.0)
    
    # Order for priority
    priority = models.IntegerField(default=0)
    
    # Active state
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-min_width']
        verbose_name = 'Responsive Breakpoint'
        verbose_name_plural = 'Responsive Breakpoints'
    
    def __str__(self):
        return f"{self.name} ({self.min_width}px+)"


class ResponsiveOverride(models.Model):
    """
    Stores overrides for auto-layout frames at specific breakpoints.
    Allows different layout configurations for different screen sizes.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    frame = models.ForeignKey(
        AutoLayoutFrame,
        on_delete=models.CASCADE,
        related_name='responsive_overrides'
    )
    breakpoint = models.ForeignKey(
        ResponsiveBreakpoint,
        on_delete=models.CASCADE,
        related_name='layout_overrides'
    )
    
    # Override settings (null means inherit from base frame)
    direction = models.CharField(
        max_length=20,
        choices=AutoLayoutFrame.DIRECTION_CHOICES,
        null=True,
        blank=True
    )
    item_spacing = models.FloatField(null=True, blank=True)
    padding_top = models.FloatField(null=True, blank=True)
    padding_right = models.FloatField(null=True, blank=True)
    padding_bottom = models.FloatField(null=True, blank=True)
    padding_left = models.FloatField(null=True, blank=True)
    primary_axis_alignment = models.CharField(
        max_length=20,
        choices=AutoLayoutFrame.PRIMARY_ALIGN_CHOICES,
        null=True,
        blank=True
    )
    cross_axis_alignment = models.CharField(
        max_length=20,
        choices=AutoLayoutFrame.CROSS_ALIGN_CHOICES,
        null=True,
        blank=True
    )
    horizontal_sizing = models.CharField(
        max_length=20,
        choices=AutoLayoutFrame.SIZING_CHOICES,
        null=True,
        blank=True
    )
    vertical_sizing = models.CharField(
        max_length=20,
        choices=AutoLayoutFrame.SIZING_CHOICES,
        null=True,
        blank=True
    )
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    # Visibility at this breakpoint
    visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['frame', 'breakpoint']
        verbose_name = 'Responsive Override'
        verbose_name_plural = 'Responsive Overrides'
    
    def __str__(self):
        return f"{self.frame.name} @ {self.breakpoint.name}"


class LayoutPreset(models.Model):
    """
    Reusable auto-layout presets that can be applied to frames.
    """
    
    CATEGORY_CHOICES = [
        ('navigation', 'Navigation'),
        ('cards', 'Cards'),
        ('lists', 'Lists'),
        ('grids', 'Grids'),
        ('forms', 'Forms'),
        ('headers', 'Headers'),
        ('footers', 'Footers'),
        ('sidebars', 'Sidebars'),
        ('modals', 'Modals'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='layout_presets',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='custom'
    )
    
    # Preset configuration (stored as JSON)
    config = models.JSONField(default=dict)
    
    # Preview image
    thumbnail = models.ImageField(upload_to='layout_presets/', null=True, blank=True)
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)  # Built-in presets
    
    # Usage stats
    use_count = models.IntegerField(default=0)
    
    # Tags for search
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-use_count', 'name']
        verbose_name = 'Layout Preset'
        verbose_name_plural = 'Layout Presets'
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def apply_to_frame(self, frame: AutoLayoutFrame):
        """Apply this preset's configuration to a frame."""
        config = self.config
        
        if 'direction' in config:
            frame.direction = config['direction']
        if 'primaryAxisAlignment' in config:
            frame.primary_axis_alignment = config['primaryAxisAlignment']
        if 'crossAxisAlignment' in config:
            frame.cross_axis_alignment = config['crossAxisAlignment']
        if 'itemSpacing' in config:
            frame.item_spacing = config['itemSpacing']
        if 'padding' in config:
            padding = config['padding']
            frame.padding_top = padding.get('top', 0)
            frame.padding_right = padding.get('right', 0)
            frame.padding_bottom = padding.get('bottom', 0)
            frame.padding_left = padding.get('left', 0)
        if 'horizontalSizing' in config:
            frame.horizontal_sizing = config['horizontalSizing']
        if 'verticalSizing' in config:
            frame.vertical_sizing = config['verticalSizing']
        
        self.use_count += 1
        self.save(update_fields=['use_count'])
        
        return frame

"""
Presentation Mode & Developer Handoff System

Production-ready presentation mode for stakeholder reviews and
comprehensive developer handoff with code generation.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Presentation(models.Model):
    """
    A presentation created from design artboards.
    """
    
    TRANSITION_NONE = 'none'
    TRANSITION_FADE = 'fade'
    TRANSITION_SLIDE = 'slide'
    TRANSITION_PUSH = 'push'
    TRANSITION_ZOOM = 'zoom'
    TRANSITION_FLIP = 'flip'
    TRANSITION_DISSOLVE = 'dissolve'
    TRANSITION_CHOICES = [
        (TRANSITION_NONE, 'None'),
        (TRANSITION_FADE, 'Fade'),
        (TRANSITION_SLIDE, 'Slide'),
        (TRANSITION_PUSH, 'Push'),
        (TRANSITION_ZOOM, 'Zoom'),
        (TRANSITION_FLIP, 'Flip'),
        (TRANSITION_DISSOLVE, 'Dissolve'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='presentations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='presentations'
    )
    
    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Presentation settings
    default_transition = models.CharField(
        max_length=20,
        choices=TRANSITION_CHOICES,
        default=TRANSITION_FADE
    )
    transition_duration = models.IntegerField(default=500)  # ms
    auto_advance = models.BooleanField(default=False)
    auto_advance_delay = models.IntegerField(default=5000)  # ms
    
    # Display settings
    show_navigation = models.BooleanField(default=True)
    show_slide_numbers = models.BooleanField(default=True)
    show_progress_bar = models.BooleanField(default=True)
    loop = models.BooleanField(default=False)
    
    # Background
    background_color = models.CharField(max_length=50, default='#000000')
    background_image = models.ImageField(upload_to='presentations/', null=True, blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='presentation_logos/', null=True, blank=True)
    logo_position = models.CharField(max_length=20, default='top-left')
    
    # Sharing
    is_public = models.BooleanField(default=False)
    share_link = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password_protected = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=255, blank=True)
    
    # Allow actions
    allow_comments = models.BooleanField(default=True)
    allow_download = models.BooleanField(default=False)
    
    # View tracking
    view_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Version tracking
    version = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Presentation'
        verbose_name_plural = 'Presentations'
    
    def __str__(self):
        return self.title


class PresentationSlide(models.Model):
    """
    Individual slide in a presentation.
    """
    
    LAYOUT_FULL = 'full'
    LAYOUT_CENTERED = 'centered'
    LAYOUT_SPLIT = 'split'
    LAYOUT_GRID = 'grid'
    LAYOUT_CHOICES = [
        (LAYOUT_FULL, 'Full Bleed'),
        (LAYOUT_CENTERED, 'Centered'),
        (LAYOUT_SPLIT, 'Split'),
        (LAYOUT_GRID, 'Grid'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name='slides'
    )
    
    # Linked design content
    design_component = models.ForeignKey(
        'projects.DesignComponent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presentation_slides'
    )
    
    # Slide content (if not linked to component)
    title = models.CharField(max_length=255, blank=True)
    content = models.JSONField(default=dict)  # Rich content
    
    # Image snapshot of the design
    snapshot = models.ImageField(upload_to='slide_snapshots/', null=True, blank=True)
    
    # Layout
    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default=LAYOUT_FULL
    )
    
    # Order
    order = models.IntegerField(default=0)
    
    # Slide-specific transition (overrides presentation default)
    transition = models.CharField(
        max_length=20,
        choices=Presentation.TRANSITION_CHOICES,
        null=True,
        blank=True
    )
    transition_duration = models.IntegerField(null=True, blank=True)
    
    # Timing
    duration = models.IntegerField(null=True, blank=True)  # Override auto-advance timing
    
    # Notes for presenter
    speaker_notes = models.TextField(blank=True)
    
    # Background override
    background_color = models.CharField(max_length=50, blank=True)
    background_image = models.ImageField(upload_to='slide_backgrounds/', null=True, blank=True)
    
    # Visibility
    is_hidden = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Presentation Slide'
        verbose_name_plural = 'Presentation Slides'
    
    def __str__(self):
        return f"Slide {self.order + 1}: {self.title or 'Untitled'}"


class SlideAnnotation(models.Model):
    """
    Annotations and hotspots on presentation slides.
    """
    
    ANNOTATION_TYPES = [
        ('hotspot', 'Hotspot'),
        ('note', 'Note'),
        ('callout', 'Callout'),
        ('link', 'Link'),
        ('video', 'Video'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slide = models.ForeignKey(
        PresentationSlide,
        on_delete=models.CASCADE,
        related_name='annotations'
    )
    
    # Type
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES)
    
    # Position
    position_x = models.FloatField()
    position_y = models.FloatField()
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    
    # Content
    content = models.JSONField(default=dict)
    # hotspot: {"action": "next_slide"} or {"action": "goto", "target": "slide_id"}
    # note: {"text": "...", "color": "#..."}
    # link: {"url": "https://...", "text": "..."}
    
    # Visibility
    visible_in_presentation = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name = 'Slide Annotation'
        verbose_name_plural = 'Slide Annotations'


class PresentationViewer(models.Model):
    """
    Tracks who has viewed a presentation.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    presentation = models.ForeignKey(
        Presentation,
        on_delete=models.CASCADE,
        related_name='viewers'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_presentations'
    )
    
    # For anonymous viewers
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # View stats
    first_viewed = models.DateTimeField(auto_now_add=True)
    last_viewed = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=1)
    
    # Engagement
    slides_viewed = models.JSONField(default=list)
    time_spent = models.IntegerField(default=0)  # seconds
    completed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Presentation Viewer'
        verbose_name_plural = 'Presentation Viewers'


class DevModeProject(models.Model):
    """
    Developer mode configuration for a project.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='dev_mode_config'
    )
    
    # Enabled status
    enabled = models.BooleanField(default=True)
    
    # Code generation settings
    default_framework = models.CharField(max_length=50, default='react')
    default_language = models.CharField(max_length=50, default='typescript')
    default_styling = models.CharField(max_length=50, default='tailwind')
    
    # Unit preferences
    unit_system = models.CharField(max_length=20, default='px')  # px, rem, em
    rem_base = models.IntegerField(default=16)
    
    # Code style preferences
    indent_size = models.IntegerField(default=2)
    use_semicolons = models.BooleanField(default=True)
    quote_style = models.CharField(max_length=10, default='single')
    
    # Export preferences
    include_comments = models.BooleanField(default=True)
    include_measurements = models.BooleanField(default=True)
    group_styles = models.BooleanField(default=True)
    
    # Component naming
    component_naming = models.CharField(max_length=20, default='pascal')  # pascal, camel, kebab
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dev Mode Project'
        verbose_name_plural = 'Dev Mode Projects'


class DevModeInspection(models.Model):
    """
    Cached inspection data for elements in dev mode.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dev_mode_project = models.ForeignKey(
        DevModeProject,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    design_component = models.ForeignKey(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='dev_inspections'
    )
    
    # Computed CSS properties
    css_properties = models.JSONField(default=dict)
    # {
    #   "width": "200px",
    #   "height": "50px",
    #   "background-color": "#6366f1",
    #   "border-radius": "8px",
    #   ...
    # }
    
    # Tailwind classes
    tailwind_classes = models.TextField(blank=True)
    
    # Computed dimensions and spacing
    dimensions = models.JSONField(default=dict)
    # {"width": 200, "height": 50, "x": 100, "y": 150}
    
    spacing = models.JSONField(default=dict)
    # {"margin": {"top": 16, ...}, "padding": {"top": 8, ...}}
    
    # Typography
    typography = models.JSONField(default=dict)
    # {"fontFamily": "Inter", "fontSize": 16, "fontWeight": 500, ...}
    
    # Colors
    colors = models.JSONField(default=dict)
    # {"fill": "#6366f1", "stroke": null, "text": "#ffffff"}
    
    # Generated code for different frameworks
    react_code = models.TextField(blank=True)
    vue_code = models.TextField(blank=True)
    html_code = models.TextField(blank=True)
    swift_code = models.TextField(blank=True)
    kotlin_code = models.TextField(blank=True)
    flutter_code = models.TextField(blank=True)
    
    # Last generated
    generated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dev Mode Inspection'
        verbose_name_plural = 'Dev Mode Inspections'


class CodeExportConfig(models.Model):
    """
    Configuration for code export.
    """
    
    FRAMEWORK_CHOICES = [
        ('react', 'React'),
        ('react_native', 'React Native'),
        ('vue', 'Vue'),
        ('angular', 'Angular'),
        ('svelte', 'Svelte'),
        ('html', 'HTML/CSS'),
        ('ios', 'iOS (SwiftUI)'),
        ('android', 'Android (Jetpack Compose)'),
        ('flutter', 'Flutter'),
    ]
    
    STYLING_CHOICES = [
        ('tailwind', 'Tailwind CSS'),
        ('css', 'Plain CSS'),
        ('scss', 'SCSS'),
        ('css_modules', 'CSS Modules'),
        ('styled_components', 'Styled Components'),
        ('emotion', 'Emotion'),
        ('inline', 'Inline Styles'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_export_configs'
    )
    
    # Config name
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Framework and styling
    framework = models.CharField(max_length=30, choices=FRAMEWORK_CHOICES)
    styling = models.CharField(max_length=30, choices=STYLING_CHOICES, default='tailwind')
    
    # TypeScript settings
    use_typescript = models.BooleanField(default=True)
    strict_types = models.BooleanField(default=True)
    
    # Component generation
    generate_props = models.BooleanField(default=True)
    generate_types = models.BooleanField(default=True)
    export_default = models.BooleanField(default=True)
    
    # Styling options
    responsive_breakpoints = models.JSONField(default=dict)
    color_format = models.CharField(max_length=20, default='hex')  # hex, rgb, hsl
    
    # Asset handling
    asset_path = models.CharField(max_length=255, default='/assets')
    image_optimization = models.BooleanField(default=True)
    
    # Is default
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Code Export Config'
        verbose_name_plural = 'Code Export Configs'
    
    def __str__(self):
        return f"{self.name} ({self.framework})"


class CodeExportHistory(models.Model):
    """
    History of code exports for tracking and re-download.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='presentation_code_exports'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='presentation_code_exports'
    )
    config = models.ForeignKey(
        CodeExportConfig,
        on_delete=models.SET_NULL,
        null=True,
        related_name='exports'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export scope
    export_type = models.CharField(max_length=30, default='full')  # full, selection, component
    selected_elements = models.JSONField(default=list)
    
    # Output
    output_file = models.FileField(upload_to='code_exports/', null=True, blank=True)
    output_url = models.URLField(blank=True)
    file_size = models.BigIntegerField(default=0)
    
    # Stats
    components_exported = models.IntegerField(default=0)
    files_generated = models.IntegerField(default=0)
    lines_of_code = models.IntegerField(default=0)
    
    # Error info
    error_message = models.TextField(blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Code Export History'
        verbose_name_plural = 'Code Export Histories'


class MeasurementOverlay(models.Model):
    """
    Saved measurement overlays for developer reference.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dev_mode_project = models.ForeignKey(
        DevModeProject,
        on_delete=models.CASCADE,
        related_name='measurement_overlays'
    )
    
    # Name for the overlay set
    name = models.CharField(max_length=255)
    
    # Source and target elements
    source_element_id = models.CharField(max_length=100)
    target_element_id = models.CharField(max_length=100, blank=True)  # For distances
    
    # Measurement data
    measurement_type = models.CharField(max_length=30)  # distance, spacing, size
    value = models.FloatField()
    unit = models.CharField(max_length=10, default='px')
    
    # Position
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # Direction for distance measurements
    direction = models.CharField(max_length=20, blank=True)  # horizontal, vertical, diagonal
    
    # Visibility
    visible = models.BooleanField(default=True)
    color = models.CharField(max_length=50, default='#ff0000')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Measurement Overlay'
        verbose_name_plural = 'Measurement Overlays'


class AssetExportQueue(models.Model):
    """
    Queue for automatic asset exports from designs.
    """
    
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('jpg', 'JPEG'),
        ('svg', 'SVG'),
        ('webp', 'WebP'),
        ('pdf', 'PDF'),
        ('avif', 'AVIF'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='asset_export_queue'
    )
    design_component = models.ForeignKey(
        'projects.DesignComponent',
        on_delete=models.CASCADE,
        related_name='export_queue'
    )
    
    # Export settings
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    scale = models.FloatField(default=1.0)  # 1x, 2x, 3x
    quality = models.IntegerField(default=90, validators=[MinValueValidator(1), MaxValueValidator(100)])
    
    # Output
    output_file = models.FileField(upload_to='asset_exports/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(default=0)
    
    # Dimensions
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Timestamps
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Asset Export Queue'
        verbose_name_plural = 'Asset Export Queue'

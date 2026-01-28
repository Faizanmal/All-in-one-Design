from django.db import models
from django.conf import settings
import uuid


class DesignSystem(models.Model):
    """A complete design system with tokens, components, and documentation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='design_systems')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='design_systems', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, default='1.0.0')
    
    # Branding
    logo = models.ImageField(upload_to='design_system_logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='design_system_favicons/', null=True, blank=True)
    
    # Settings
    is_public = models.BooleanField(default=False)
    auto_sync = models.BooleanField(default=True)  # Auto-sync with Figma/Storybook
    
    # External integrations
    figma_file_key = models.CharField(max_length=255, blank=True)
    storybook_url = models.URLField(blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Design System'
        verbose_name_plural = 'Design Systems'
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class DesignToken(models.Model):
    """Design tokens (colors, typography, spacing, etc.)"""
    TOKEN_TYPES = [
        ('color', 'Color'),
        ('typography', 'Typography'),
        ('spacing', 'Spacing'),
        ('sizing', 'Sizing'),
        ('border-radius', 'Border Radius'),
        ('border-width', 'Border Width'),
        ('shadow', 'Shadow'),
        ('opacity', 'Opacity'),
        ('z-index', 'Z-Index'),
        ('duration', 'Duration'),
        ('easing', 'Easing'),
        ('font-family', 'Font Family'),
        ('font-weight', 'Font Weight'),
        ('line-height', 'Line Height'),
        ('letter-spacing', 'Letter Spacing'),
        ('breakpoint', 'Breakpoint'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='tokens')
    
    name = models.CharField(max_length=255)  # e.g., "primary-500"
    category = models.CharField(max_length=100)  # e.g., "colors", "spacing"
    token_type = models.CharField(max_length=50, choices=TOKEN_TYPES)
    
    # Value storage
    value = models.JSONField()  # Can store various types of values
    # Example for color: {"hex": "#6366f1", "rgb": "99, 102, 241", "hsl": "239, 84%, 67%"}
    # Example for typography: {"fontSize": "16px", "lineHeight": "1.5", "fontWeight": "400"}
    
    # Reference to other tokens
    reference = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='references')
    
    # Description and usage
    description = models.TextField(blank=True)
    usage_guidelines = models.TextField(blank=True)
    
    # Grouping
    group = models.CharField(max_length=100, blank=True)  # e.g., "brand", "semantic", "component"
    order = models.IntegerField(default=0)
    
    # Deprecated tokens
    is_deprecated = models.BooleanField(default=False)
    deprecated_message = models.CharField(max_length=255, blank=True)
    replacement = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replaces')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'group', 'order', 'name']
        unique_together = ['design_system', 'name']
    
    def __str__(self):
        return f"{self.category}/{self.name}"


class ComponentDefinition(models.Model):
    """Component definitions in the design system"""
    COMPONENT_STATES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('approved', 'Approved'),
        ('deprecated', 'Deprecated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='components')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)  # e.g., "buttons", "forms", "navigation"
    
    # Component status
    status = models.CharField(max_length=20, choices=COMPONENT_STATES, default='draft')
    
    # Visual representation
    preview_image = models.ImageField(upload_to='component_previews/', null=True, blank=True)
    figma_node_id = models.CharField(max_length=255, blank=True)
    storybook_path = models.CharField(max_length=255, blank=True)
    
    # Component structure
    variants = models.JSONField(default=list)  # List of variant definitions
    props = models.JSONField(default=list)  # List of prop definitions
    slots = models.JSONField(default=list)  # Named slots/children areas
    
    # Code templates
    html_template = models.TextField(blank=True)
    react_template = models.TextField(blank=True)
    vue_template = models.TextField(blank=True)
    angular_template = models.TextField(blank=True)
    
    # Design specifications
    specs = models.JSONField(default=dict)  # Detailed design specs
    anatomy = models.JSONField(default=dict)  # Component anatomy/structure
    
    # Usage guidelines
    usage_guidelines = models.TextField(blank=True)
    dos = models.JSONField(default=list)  # Best practices
    donts = models.JSONField(default=list)  # Anti-patterns
    
    # Accessibility
    accessibility_guidelines = models.TextField(blank=True)
    aria_attributes = models.JSONField(default=dict)
    
    # Related components
    related_components = models.ManyToManyField('self', blank=True)
    
    # Metadata
    tags = models.JSONField(default=list)
    version = models.CharField(max_length=50, default='1.0.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category}/{self.name}"


class ComponentVariant(models.Model):
    """Variants of a component (e.g., primary button, secondary button)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.ForeignKey(ComponentDefinition, on_delete=models.CASCADE, related_name='variant_instances')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Variant-specific values
    props = models.JSONField(default=dict)
    tokens = models.JSONField(default=dict)  # Token overrides for this variant
    
    # Preview
    preview_image = models.ImageField(upload_to='variant_previews/', null=True, blank=True)
    
    # Code example
    code_example = models.TextField(blank=True)
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.component.name} - {self.name}"


class StyleGuide(models.Model):
    """Style guide documentation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.OneToOneField(DesignSystem, on_delete=models.CASCADE, related_name='style_guide')
    
    # Brand guidelines
    brand_overview = models.TextField(blank=True)
    brand_values = models.JSONField(default=list)
    tone_of_voice = models.TextField(blank=True)
    
    # Logo usage
    logo_guidelines = models.TextField(blank=True)
    logo_variations = models.JSONField(default=list)  # Different logo versions
    logo_clearspace = models.JSONField(default=dict)  # Clear space rules
    logo_misuse = models.JSONField(default=list)  # What not to do
    
    # Color guidelines
    color_guidelines = models.TextField(blank=True)
    color_accessibility = models.TextField(blank=True)
    
    # Typography guidelines
    typography_guidelines = models.TextField(blank=True)
    typography_scale = models.JSONField(default=dict)
    
    # Imagery guidelines
    imagery_guidelines = models.TextField(blank=True)
    photography_style = models.TextField(blank=True)
    illustration_style = models.TextField(blank=True)
    iconography_guidelines = models.TextField(blank=True)
    
    # Layout guidelines
    layout_guidelines = models.TextField(blank=True)
    grid_system = models.JSONField(default=dict)
    spacing_guidelines = models.TextField(blank=True)
    
    # Motion guidelines
    motion_guidelines = models.TextField(blank=True)
    animation_principles = models.JSONField(default=list)
    
    # Custom sections
    custom_sections = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Style Guide'
        verbose_name_plural = 'Style Guides'
    
    def __str__(self):
        return f"Style Guide for {self.design_system.name}"


class DocumentationPage(models.Model):
    """Custom documentation pages for the design system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='documentation_pages')
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    content = models.TextField()  # Markdown content
    
    # Hierarchy
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.IntegerField(default=0)
    
    # Visibility
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        unique_together = ['design_system', 'slug']
    
    def __str__(self):
        return self.title


class DesignSystemExport(models.Model):
    """Export jobs for design systems"""
    EXPORT_FORMATS = [
        ('pdf', 'PDF Style Guide'),
        ('web', 'Static Website'),
        ('figma', 'Figma Library'),
        ('sketch', 'Sketch Library'),
        ('css', 'CSS Variables'),
        ('scss', 'SCSS Variables'),
        ('json', 'JSON Tokens'),
        ('js', 'JavaScript/TypeScript'),
        ('ios', 'iOS Swift'),
        ('android', 'Android XML'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='exports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    export_format = models.CharField(max_length=20, choices=EXPORT_FORMATS)
    options = models.JSONField(default=dict)  # Format-specific options
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Result
    output_file = models.FileField(upload_to='design_system_exports/', null=True, blank=True)
    output_url = models.URLField(blank=True)  # For web exports
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.design_system.name} - {self.export_format}"


class DesignSystemSync(models.Model):
    """Sync history with external tools"""
    SYNC_SOURCES = [
        ('figma', 'Figma'),
        ('storybook', 'Storybook'),
        ('sketch', 'Sketch'),
        ('manual', 'Manual Update'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='sync_history')
    
    source = models.CharField(max_length=20, choices=SYNC_SOURCES)
    direction = models.CharField(max_length=10, default='pull')  # pull or push
    
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Changes
    changes_summary = models.JSONField(default=dict)
    # Example: {"tokens_added": 5, "tokens_updated": 10, "components_added": 2}
    
    error_message = models.TextField(blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Design System Sync'
        verbose_name_plural = 'Design System Syncs'
    
    def __str__(self):
        return f"{self.design_system.name} - {self.source} ({self.status})"

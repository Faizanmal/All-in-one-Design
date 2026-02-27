"""
Design Tokens Manager Models

Centralized design tokens with variables, themes, and sync capabilities.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class DesignTokenLibrary(models.Model):
    """
    A collection of design tokens that can be shared across projects.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='token_libraries'
    )
    
    # Version control
    version = models.CharField(max_length=50, default='1.0.0')
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(
        default=False,
        help_text="Use as default library for new projects"
    )
    
    # Sync settings
    sync_enabled = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    usage_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name_plural = 'Design Token Libraries'
    
    def __str__(self):
        return f"{self.name} v{self.version}"
    
    def increment_version(self, increment_type='patch'):
        """
        Increment the version number.
        """
        parts = self.version.split('.')
        if len(parts) != 3:
            parts = ['1', '0', '0']
        
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        if increment_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif increment_type == 'minor':
            minor += 1
            patch = 0
        else:
            patch += 1
        
        self.version = f"{major}.{minor}.{patch}"
        self.save()
        return self.version


class DesignToken(models.Model):
    """
    Individual design token (color, spacing, typography, etc.)
    """
    TOKEN_TYPES = [
        ('color', 'Color'),
        ('spacing', 'Spacing'),
        ('sizing', 'Sizing'),
        ('typography', 'Typography'),
        ('font-family', 'Font Family'),
        ('font-size', 'Font Size'),
        ('font-weight', 'Font Weight'),
        ('line-height', 'Line Height'),
        ('border-radius', 'Border Radius'),
        ('border-width', 'Border Width'),
        ('shadow', 'Shadow'),
        ('opacity', 'Opacity'),
        ('z-index', 'Z-Index'),
        ('breakpoint', 'Breakpoint'),
        ('duration', 'Duration'),
        ('easing', 'Easing'),
        ('custom', 'Custom'),
    ]
    
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    
    # Token identification
    name = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-z][a-z0-9-]*$',
                message='Token name must be lowercase, start with a letter, and contain only letters, numbers, and hyphens'
            )
        ]
    )
    category = models.CharField(max_length=100, blank=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    
    # Token value
    value = models.CharField(max_length=500)
    
    # CSS variable name (auto-generated)
    css_variable = models.CharField(max_length=150, blank=True)
    
    # Reference to another token
    references = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referenced_by',
        help_text="Reference another token for aliasing"
    )
    
    # Description and usage
    description = models.TextField(blank=True)
    usage_examples = models.JSONField(
        default=list,
        help_text="Example use cases for this token"
    )
    
    # Metadata
    deprecated = models.BooleanField(default=False)
    deprecated_message = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        unique_together = ['library', 'name']
    
    def __str__(self):
        return f"{self.library.name}/{self.name}: {self.value}"
    
    def save(self, *args, **kwargs):
        # Auto-generate CSS variable name
        if not self.css_variable:
            prefix = self.library.name.lower().replace(' ', '-')
            self.css_variable = f"--{prefix}-{self.name}"
        super().save(*args, **kwargs)
    
    def get_resolved_value(self):
        """
        Get the resolved value, following references.
        """
        if self.references:
            return self.references.get_resolved_value()
        return self.value


class DesignTheme(models.Model):
    """
    A theme is a collection of token overrides for different contexts
    (light mode, dark mode, brand variations, etc.)
    """
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='themes'
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    
    # Theme type
    theme_type = models.CharField(
        max_length=20,
        choices=[
            ('color-scheme', 'Color Scheme'),
            ('brand', 'Brand Variation'),
            ('density', 'Density'),
            ('accessibility', 'Accessibility'),
            ('custom', 'Custom'),
        ],
        default='color-scheme'
    )
    
    # Base theme to extend
    extends = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    
    # Is this the default theme?
    is_default = models.BooleanField(default=False)
    
    # Selector for CSS
    css_selector = models.CharField(
        max_length=100,
        blank=True,
        help_text="CSS selector for this theme (e.g., [data-theme='dark'])"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['library', 'slug']
    
    def __str__(self):
        return f"{self.library.name} - {self.name}"


class ThemeTokenOverride(models.Model):
    """
    Token value override for a specific theme.
    """
    theme = models.ForeignKey(
        DesignTheme,
        on_delete=models.CASCADE,
        related_name='overrides'
    )
    token = models.ForeignKey(
        DesignToken,
        on_delete=models.CASCADE,
        related_name='theme_overrides'
    )
    
    # Override value
    value = models.CharField(max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['theme', 'token']
    
    def __str__(self):
        return f"{self.theme.name}: {self.token.name} = {self.value}"


class TokenGroup(models.Model):
    """
    Group tokens for organization (e.g., "Primary Colors", "Base Spacing")
    """
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    
    tokens = models.ManyToManyField(
        DesignToken,
        related_name='groups',
        blank=True
    )
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.library.name} - {self.name}"


class ProjectTokenBinding(models.Model):
    """
    Bind a token library to a project for sync.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='token_bindings'
    )
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='project_bindings'
    )
    theme = models.ForeignKey(
        DesignTheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='project_bindings'
    )
    
    # Local overrides for this project
    local_overrides = models.JSONField(
        default=dict,
        help_text="Project-specific token overrides"
    )
    
    # Sync status
    is_synced = models.BooleanField(default=True)
    last_synced = models.DateTimeField(auto_now_add=True)
    sync_errors = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'library']
    
    def __str__(self):
        return f"{self.project.name} -> {self.library.name}"


class TokenExportFormat(models.Model):
    """
    Export format configuration for tokens.
    """
    FORMAT_TYPES = [
        ('css', 'CSS Variables'),
        ('scss', 'SCSS Variables'),
        ('less', 'LESS Variables'),
        ('json', 'JSON'),
        ('js', 'JavaScript Module'),
        ('ts', 'TypeScript Module'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('tailwind', 'Tailwind Config'),
        ('figma', 'Figma Tokens'),
        ('style-dictionary', 'Style Dictionary'),
    ]
    
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='export_formats'
    )
    
    format_type = models.CharField(max_length=20, choices=FORMAT_TYPES)
    name = models.CharField(max_length=100)
    
    # Format configuration
    config = models.JSONField(
        default=dict,
        help_text="Format-specific configuration options"
    )
    
    # Template for custom formats
    template = models.TextField(
        blank=True,
        help_text="Custom template for export (uses Jinja2 syntax)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['library', 'format_type']
    
    def __str__(self):
        return f"{self.library.name} - {self.get_format_type_display()}"


class TokenChangeLog(models.Model):
    """
    Track changes to tokens for version history.
    """
    CHANGE_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('rename', 'Renamed'),
    ]
    
    library = models.ForeignKey(
        DesignTokenLibrary,
        on_delete=models.CASCADE,
        related_name='change_logs'
    )
    token = models.ForeignKey(
        DesignToken,
        on_delete=models.SET_NULL,
        null=True,
        related_name='change_logs'
    )
    
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    
    # Change details
    old_value = models.CharField(max_length=500, blank=True)
    new_value = models.CharField(max_length=500, blank=True)
    
    # Author
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Library version at time of change
    library_version = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        token_name = self.token.name if self.token else 'Unknown'
        return f"{self.change_type} {token_name} @ {self.created_at}"

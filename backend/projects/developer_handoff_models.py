"""
Developer Handoff Models
Models for code export, design systems, and developer tools
"""
from django.db import models
from django.contrib.auth.models import User


class CodeExport(models.Model):
    """Track code export requests"""
    FORMAT_CHOICES = (
        ('react', 'React'),
        ('react_typescript', 'React TypeScript'),
        ('vue', 'Vue.js'),
        ('html_css', 'HTML/CSS'),
        ('tailwind', 'Tailwind CSS'),
        ('styled_components', 'Styled Components'),
        ('scss', 'SCSS'),
        ('flutter', 'Flutter'),
        ('swift_ui', 'SwiftUI'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_exports')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='code_exports')
    
    # Export format
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='react')
    
    # Export options
    options = models.JSONField(default=dict)
    # {
    #   "include_comments": true,
    #   "component_naming": "PascalCase",
    #   "css_naming": "BEM",
    #   "responsive": true,
    #   "breakpoints": [768, 1024, 1440]
    # }
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    output_code = models.TextField(blank=True)
    output_files = models.JSONField(default=dict)  # Filename -> content mapping
    error_message = models.TextField(blank=True)
    
    # Metadata
    lines_of_code = models.IntegerField(default=0)
    components_generated = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Code Export #{self.id} - {self.get_format_display()}"


class DesignSystem(models.Model):
    """User-created design systems"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_systems')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, default='1.0.0')
    
    # Color tokens
    colors = models.JSONField(default=dict)
    # {
    #   "primary": {"50": "#E3F2FD", "500": "#2196F3", "900": "#0D47A1"},
    #   "secondary": {...},
    #   "neutral": {...},
    #   "semantic": {"success": "#4CAF50", "error": "#F44336"}
    # }
    
    # Typography tokens
    typography = models.JSONField(default=dict)
    # {
    #   "fontFamilies": {"heading": "Inter", "body": "Roboto"},
    #   "fontSizes": {"xs": "12px", "sm": "14px", "base": "16px"},
    #   "fontWeights": {"normal": 400, "medium": 500, "bold": 700},
    #   "lineHeights": {"tight": 1.25, "normal": 1.5}
    # }
    
    # Spacing tokens
    spacing = models.JSONField(default=dict)
    # {
    #   "0": "0px", "1": "4px", "2": "8px", "3": "12px", "4": "16px"
    # }
    
    # Border radius tokens
    radii = models.JSONField(default=dict)
    # {
    #   "none": "0px", "sm": "4px", "md": "8px", "lg": "16px", "full": "9999px"
    # }
    
    # Shadow tokens
    shadows = models.JSONField(default=dict)
    
    # Breakpoints
    breakpoints = models.JSONField(default=dict)
    # {
    #   "sm": "640px", "md": "768px", "lg": "1024px", "xl": "1280px"
    # }
    
    # Component variants
    component_variants = models.JSONField(default=dict)
    # {
    #   "button": {
    #     "primary": {...},
    #     "secondary": {...}
    #   }
    # }
    
    # Source projects
    source_projects = models.ManyToManyField('projects.Project', blank=True, related_name='design_systems')
    
    # Sharing
    is_public = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class DesignSystemExport(models.Model):
    """Export design system to various formats"""
    FORMAT_CHOICES = (
        ('css_variables', 'CSS Variables'),
        ('scss_variables', 'SCSS Variables'),
        ('tailwind_config', 'Tailwind Config'),
        ('json_tokens', 'JSON Tokens'),
        ('figma_tokens', 'Figma Tokens'),
        ('style_dictionary', 'Style Dictionary'),
    )
    
    design_system = models.ForeignKey(DesignSystem, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES)
    output_content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.design_system.name} - {self.get_format_display()}"


class ComponentSpec(models.Model):
    """Generated component specifications for developers"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='component_specs')
    element_id = models.CharField(max_length=255)
    
    # Component info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Specifications
    dimensions = models.JSONField(default=dict)  # width, height, padding, margin
    styles = models.JSONField(default=dict)  # All CSS properties
    responsive_variants = models.JSONField(default=dict)  # Different breakpoints
    
    # States
    states = models.JSONField(default=dict)  # hover, active, focus, disabled
    
    # Props (for component-based frameworks)
    props = models.JSONField(default=list)  # Prop definitions
    
    # Assets
    assets = models.JSONField(default=list)  # Referenced images, icons
    
    # Code snippets
    code_snippets = models.JSONField(default=dict)  # Framework -> code
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['project', 'element_id']
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"


class HandoffAnnotation(models.Model):
    """Developer annotations on designs"""
    ANNOTATION_TYPES = (
        ('note', 'Note'),
        ('spec', 'Specification'),
        ('question', 'Question'),
        ('requirement', 'Requirement'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='handoff_annotations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='handoff_annotations')
    
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES, default='note')
    
    # Position on canvas
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # Target element (optional)
    target_element_id = models.CharField(max_length=255, blank=True)
    
    # Content
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_annotations'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_annotation_type_display()})"

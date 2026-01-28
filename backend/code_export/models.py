from django.db import models
from django.contrib.auth.models import User
from projects.models import Project, DesignComponent


class ExportConfiguration(models.Model):
    """Configuration for code export settings"""
    FRAMEWORK_CHOICES = (
        ('react', 'React'),
        ('vue', 'Vue.js'),
        ('angular', 'Angular'),
        ('svelte', 'Svelte'),
        ('html', 'HTML/CSS'),
        ('swiftui', 'SwiftUI (iOS)'),
        ('jetpack_compose', 'Jetpack Compose (Android)'),
        ('flutter', 'Flutter'),
        ('react_native', 'React Native'),
    )
    
    STYLING_CHOICES = (
        ('tailwind', 'Tailwind CSS'),
        ('css_modules', 'CSS Modules'),
        ('styled_components', 'Styled Components'),
        ('emotion', 'Emotion'),
        ('scss', 'SCSS'),
        ('vanilla_css', 'Vanilla CSS'),
        ('chakra_ui', 'Chakra UI'),
        ('material_ui', 'Material UI'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_configs')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Export settings
    framework = models.CharField(max_length=30, choices=FRAMEWORK_CHOICES, default='react')
    styling = models.CharField(max_length=30, choices=STYLING_CHOICES, default='tailwind')
    
    # Code generation options
    typescript_enabled = models.BooleanField(default=True)
    component_naming = models.CharField(max_length=20, default='PascalCase')  # PascalCase, camelCase, kebab-case
    use_absolute_imports = models.BooleanField(default=True)
    generate_tests = models.BooleanField(default=False)
    generate_storybook = models.BooleanField(default=False)
    
    # Responsive settings
    breakpoints = models.JSONField(default=dict)  # {"sm": 640, "md": 768, "lg": 1024, "xl": 1280}
    generate_responsive = models.BooleanField(default=True)
    
    # Advanced options
    custom_config = models.JSONField(default=dict)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', '-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.framework}/{self.styling})"


class CodeExport(models.Model):
    """Record of code exports"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_export_records')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='code_export_records')
    config = models.ForeignKey(ExportConfiguration, on_delete=models.SET_NULL, null=True)
    
    # Export metadata
    framework = models.CharField(max_length=30)
    styling = models.CharField(max_length=30)
    
    # Generated code
    generated_code = models.JSONField(default=dict)  # {"filename": "code content"}
    preview_url = models.URLField(blank=True)
    download_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Statistics
    file_count = models.IntegerField(default=0)
    total_lines = models.IntegerField(default=0)
    export_size = models.IntegerField(default=0)  # in bytes
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export {self.project.name} ({self.framework})"


class DesignSpec(models.Model):
    """Automatic design specification documentation"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='design_specs')
    component = models.ForeignKey(DesignComponent, on_delete=models.CASCADE, null=True, blank=True, related_name='specs')
    
    # Spec content
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Design properties
    dimensions = models.JSONField(default=dict)  # width, height, padding, margin
    colors = models.JSONField(default=dict)  # background, text, border colors
    typography = models.JSONField(default=dict)  # font-family, size, weight, line-height
    spacing = models.JSONField(default=dict)  # padding, margin, gap
    effects = models.JSONField(default=dict)  # shadows, blur, opacity
    
    # CSS/Style values
    computed_styles = models.JSONField(default=dict)
    
    # Assets
    assets = models.JSONField(default=list)  # List of required assets with URLs
    
    # Developer notes
    notes = models.TextField(blank=True)
    implementation_hints = models.JSONField(default=list)
    
    # Metadata
    auto_generated = models.BooleanField(default=True)
    version = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Spec: {self.name}"


class ComponentLibrary(models.Model):
    """Reusable component library for export"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='component_libraries')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='component_libraries')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Component definitions
    components = models.JSONField(default=list)
    
    # Export presets
    default_framework = models.CharField(max_length=30, default='react')
    default_styling = models.CharField(max_length=30, default='tailwind')
    
    # NPM/Package info
    package_name = models.CharField(max_length=255, blank=True)
    package_registry = models.CharField(max_length=50, default='npm')  # npm, github, private
    
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Component libraries'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class HandoffAnnotation(models.Model):
    """Annotations for developer handoff"""
    ANNOTATION_TYPES = (
        ('dimension', 'Dimension'),
        ('spacing', 'Spacing'),
        ('color', 'Color'),
        ('typography', 'Typography'),
        ('interaction', 'Interaction'),
        ('note', 'Note'),
        ('asset', 'Asset'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='handoff_annotations')
    component = models.ForeignKey(DesignComponent, on_delete=models.CASCADE, null=True, blank=True)
    
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES)
    
    # Position on canvas
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # Annotation content
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Visual
    color = models.CharField(max_length=20, default='#3B82F6')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='resolved_annotations')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.annotation_type}: {self.title}"

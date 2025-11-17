from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    """Main project model for storing user designs"""
    PROJECT_TYPES = (
        ('graphic', 'Graphic Design'),
        ('ui_ux', 'UI/UX Design'),
        ('logo', 'Logo Design'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    
    # Canvas configuration
    canvas_width = models.IntegerField(default=1920)
    canvas_height = models.IntegerField(default=1080)
    canvas_background = models.CharField(max_length=50, default='#FFFFFF')
    
    # Design data stored as JSON
    design_data = models.JSONField(default=dict)
    
    # AI-generated metadata
    ai_prompt = models.TextField(blank=True)
    color_palette = models.JSONField(default=list)  # Array of hex colors
    suggested_fonts = models.JSONField(default=list)  # Array of font names
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Collaboration
    is_public = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(User, related_name='collaborated_projects', blank=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_project_type_display()})"


class DesignComponent(models.Model):
    """Individual design components/elements in a project"""
    COMPONENT_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('shape', 'Shape'),
        ('button', 'Button'),
        ('icon', 'Icon'),
        ('group', 'Group'),
        ('frame', 'Frame'),
        ('map', 'Map'),
        ('chart', 'Chart'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='components')
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    
    # Component properties stored as JSON
    properties = models.JSONField(default=dict)
    # {
    #   "text": "Hello",
    #   "fontSize": 24,
    #   "fontFamily": "Arial",
    #   "color": "#000000",
    #   "position": {"x": 100, "y": 100},
    #   "size": {"width": 200, "height": 50},
    #   "rotation": 0,
    #   "opacity": 1,
    #   "style": {...}
    # }
    
    # Layering
    z_index = models.IntegerField(default=0)
    
    # AI metadata
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['z_index']
    
    def __str__(self):
        return f"{self.component_type} in {self.project.name}"


class ProjectVersion(models.Model):
    """Version control for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    design_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['project', 'version_number']
    
    def __str__(self):
        return f"{self.project.name} v{self.version_number}"


class ExportTemplate(models.Model):
    """Reusable export templates for consistent export configurations"""
    FORMAT_CHOICES = (
        ('svg', 'SVG'),
        ('pdf', 'PDF'),
        ('png', 'PNG'),
        ('figma', 'Figma JSON'),
    )
    
    QUALITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('ultra', 'Ultra'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_templates')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='svg')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES, default='high')
    
    # Configuration options
    optimize = models.BooleanField(default=True)
    include_metadata = models.BooleanField(default=False)
    compression = models.CharField(max_length=10, default='medium')
    
    # Dimensions
    width = models.IntegerField(null=True, blank=True, help_text="Custom width (null = original)")
    height = models.IntegerField(null=True, blank=True, help_text="Custom height (null = original)")
    scale = models.FloatField(default=1.0, help_text="Scale factor (1.0 = 100%)")
    
    # Format-specific options stored as JSON
    format_options = models.JSONField(default=dict)
    # {
    #   "svg": {"pretty_print": false, "embed_fonts": true},
    #   "pdf": {"page_size": "A4", "orientation": "portrait"},
    #   "png": {"quality": 95, "optimize": true},
    #   "figma": {"include_constraints": true}
    # }
    
    # Template metadata
    is_public = models.BooleanField(default=False)
    use_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_format_display()})"


class ExportJob(models.Model):
    """Track export jobs for batch processing and monitoring"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_jobs')
    projects = models.ManyToManyField(Project, related_name='export_jobs')
    template = models.ForeignKey(ExportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    format = models.CharField(max_length=10, default='svg')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Progress tracking
    total_projects = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    failed_projects = models.IntegerField(default=0)
    
    # File storage
    output_file = models.FileField(upload_to='exports/%Y/%m/%d/', null=True, blank=True)
    file_size = models.BigIntegerField(default=0, help_text="File size in bytes")
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export Job {self.id} - {self.status}"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_projects == 0:
            return 0
        return int((self.completed_projects / self.total_projects) * 100)
    
    @property
    def duration(self):
        """Calculate job duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class Asset(models.Model):
    """Store design assets like images, icons, fonts"""
    ASSET_TYPES = (
        ('image', 'Image'),
        ('icon', 'Icon'),
        ('font', 'Font'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('svg', 'SVG'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assets', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    
    # File storage
    file_url = models.URLField()  # S3 or cloud storage URL
    file_size = models.IntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)
    
    # Dimensions (for images/videos)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # AI metadata
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    # Tags for searchability
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.asset_type})"


class ColorPalette(models.Model):
    """Store and manage color palettes"""
    name = models.CharField(max_length=255)
    colors = models.JSONField(default=list)  # ['#FF0000', '#00FF00', '#0000FF']
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)  # ['modern', 'vibrant', 'pastel']
    
    # AI-generated
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    # Usage
    is_public = models.BooleanField(default=True)
    use_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-use_count', '-created_at']
    
    def __str__(self):
        return self.name


class FontFamily(models.Model):
    """Manage available fonts"""
    name = models.CharField(max_length=255, unique=True)
    font_family = models.CharField(max_length=255)  # CSS font-family value
    
    # Font files
    regular_url = models.URLField(blank=True)
    bold_url = models.URLField(blank=True)
    italic_url = models.URLField(blank=True)
    bold_italic_url = models.URLField(blank=True)
    
    # Metadata
    category = models.CharField(max_length=50, choices=(
        ('serif', 'Serif'),
        ('sans-serif', 'Sans Serif'),
        ('monospace', 'Monospace'),
        ('display', 'Display'),
        ('handwriting', 'Handwriting'),
    ))
    
    is_google_font = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


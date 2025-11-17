from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):
    """Pre-built design templates"""
    TEMPLATE_CATEGORIES = (
        ('social_media', 'Social Media'),
        ('presentation', 'Presentation'),
        ('poster', 'Poster'),
        ('flyer', 'Flyer'),
        ('ui_kit', 'UI Kit'),
        ('mobile_app', 'Mobile App'),
        ('web_design', 'Web Design'),
        ('logo', 'Logo'),
        ('business_card', 'Business Card'),
        ('infographic', 'Infographic'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=TEMPLATE_CATEGORIES)
    
    # Template design data
    design_data = models.JSONField(default=dict)
    thumbnail_url = models.URLField(blank=True)
    
    # Dimensions
    width = models.IntegerField(default=1920)
    height = models.IntegerField(default=1080)
    
    # Metadata
    tags = models.JSONField(default=list)  # ['modern', 'minimalist', 'corporate']
    color_palette = models.JSONField(default=list)  # ['#FF0000', '#00FF00']
    
    # Usage
    is_premium = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    use_count = models.IntegerField(default=0)
    
    # AI-generated
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-use_count', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class TemplateComponent(models.Model):
    """Reusable components for templates"""
    COMPONENT_TYPES = (
        ('header', 'Header'),
        ('footer', 'Footer'),
        ('sidebar', 'Sidebar'),
        ('card', 'Card'),
        ('button', 'Button'),
        ('form', 'Form'),
        ('navigation', 'Navigation'),
        ('hero', 'Hero Section'),
    )
    
    name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=30, choices=COMPONENT_TYPES)
    design_data = models.JSONField(default=dict)
    thumbnail_url = models.URLField(blank=True)
    
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.component_type})"

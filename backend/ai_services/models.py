from django.db import models
from django.contrib.auth.models import User


class AIGenerationRequest(models.Model):
    """Track AI generation requests for analytics and debugging"""
    REQUEST_TYPES = (
        ('layout', 'Layout Generation'),
        ('logo', 'Logo Generation'),
        ('color_palette', 'Color Palette'),
        ('text_content', 'Text Content'),
        ('image', 'Image Generation'),
        ('refinement', 'Design Refinement'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input
    prompt = models.TextField()
    parameters = models.JSONField(default=dict)  # Additional parameters like style, colors, etc.
    
    # Output
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # AI model info
    model_used = models.CharField(max_length=100, blank=True)  # e.g., 'gpt-4', 'dall-e-3'
    tokens_used = models.IntegerField(null=True, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.request_type} - {self.status} ({self.user.username})"


class AIPromptTemplate(models.Model):
    """Pre-defined prompt templates for consistent AI generation"""
    TEMPLATE_TYPES = (
        ('layout', 'Layout Generation'),
        ('logo', 'Logo Generation'),
        ('refinement', 'Design Refinement'),
        ('content', 'Content Generation'),
    )
    
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    
    # Prompt template with placeholders
    prompt_template = models.TextField()
    # Example: "Generate a {style} {design_type} design for {industry} with colors {colors}"
    
    # Default parameters
    default_parameters = models.JSONField(default=dict)
    
    # Metadata
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


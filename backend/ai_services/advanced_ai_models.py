"""
Advanced AI Service Models
Models for enhanced AI capabilities
"""
from django.db import models
from django.contrib.auth.models import User


class ImageToDesignRequest(models.Model):
    """Track image-to-design conversion requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_to_design_requests')
    
    # Input
    source_image = models.ImageField(upload_to='ai/image_to_design/%Y/%m/')
    prompt = models.TextField(blank=True, help_text="Additional instructions for conversion")
    target_design_type = models.CharField(max_length=50, default='ui_ux')
    
    # Processing options
    extract_colors = models.BooleanField(default=True)
    extract_typography = models.BooleanField(default=True)
    extract_layout = models.BooleanField(default=True)
    preserve_style = models.BooleanField(default=True)
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Processing info
    model_used = models.CharField(max_length=100, blank=True)
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Image to Design #{self.id} - {self.status}"


class StyleTransferRequest(models.Model):
    """Track style transfer requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    STYLE_PRESETS = (
        ('apple', 'Apple Design'),
        ('google_material', 'Google Material'),
        ('microsoft_fluent', 'Microsoft Fluent'),
        ('minimalist', 'Minimalist'),
        ('brutalist', 'Brutalist'),
        ('scandinavian', 'Scandinavian'),
        ('retro', 'Retro'),
        ('futuristic', 'Futuristic'),
        ('organic', 'Organic'),
        ('corporate', 'Corporate'),
        ('playful', 'Playful'),
        ('elegant', 'Elegant'),
        ('custom', 'Custom'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='style_transfer_requests')
    
    # Source
    source_project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='style_transfers')
    
    # Style reference
    style_preset = models.CharField(max_length=50, choices=STYLE_PRESETS, default='minimalist')
    style_reference_image = models.ImageField(upload_to='ai/style_reference/%Y/%m/', null=True, blank=True)
    style_description = models.TextField(blank=True)
    
    # Transfer options
    transfer_colors = models.BooleanField(default=True)
    transfer_typography = models.BooleanField(default=True)
    transfer_spacing = models.BooleanField(default=True)
    transfer_shapes = models.BooleanField(default=True)
    intensity = models.FloatField(default=0.8, help_text="Style transfer intensity (0-1)")
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_project = models.ForeignKey(
        'projects.Project', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='style_transfer_results'
    )
    result_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Style Transfer #{self.id} - {self.style_preset}"


class VoiceToDesignRequest(models.Model):
    """Track voice-to-design requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('transcribing', 'Transcribing'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voice_to_design_requests')
    
    # Input
    audio_file = models.FileField(upload_to='ai/voice_to_design/%Y/%m/')
    audio_duration_seconds = models.FloatField(null=True, blank=True)
    
    # Transcription
    transcribed_text = models.TextField(blank=True)
    transcription_confidence = models.FloatField(null=True, blank=True)
    
    # Generation options
    design_type = models.CharField(max_length=50, default='ui_ux')
    additional_context = models.TextField(blank=True)
    
    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    result_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Processing info
    transcription_model = models.CharField(max_length=100, blank=True)
    generation_model = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Voice to Design #{self.id} - {self.status}"


class DesignTrend(models.Model):
    """Track design trends and analysis"""
    TREND_CATEGORIES = (
        ('color', 'Color Trends'),
        ('typography', 'Typography Trends'),
        ('layout', 'Layout Trends'),
        ('style', 'Style Trends'),
        ('component', 'Component Trends'),
        ('animation', 'Animation Trends'),
    )
    
    category = models.CharField(max_length=50, choices=TREND_CATEGORIES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Trend data
    trend_data = models.JSONField(default=dict)
    # {
    #   "colors": ["#FF6B6B", "#4ECDC4"],
    #   "fonts": ["Inter", "Poppins"],
    #   "examples": [...]
    # }
    
    # Popularity metrics
    popularity_score = models.FloatField(default=0)
    growth_rate = models.FloatField(default=0, help_text="Percentage growth")
    
    # Time period
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    # Industries
    industries = models.JSONField(default=list)  # ["tech", "fashion", "healthcare"]
    
    # Source
    source = models.CharField(max_length=100, blank=True)  # dribbble, behance, internal
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity_score', '-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class TrendAnalysisRequest(models.Model):
    """Track trend analysis requests for projects"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trend_analyses')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='trend_analyses')
    
    # Analysis results
    overall_score = models.FloatField(null=True, blank=True, help_text="0-100 trend alignment score")
    color_score = models.FloatField(null=True, blank=True)
    typography_score = models.FloatField(null=True, blank=True)
    layout_score = models.FloatField(null=True, blank=True)
    
    # Recommendations
    recommendations = models.JSONField(default=list)
    # [
    #   {"area": "colors", "suggestion": "...", "trend": "..."},
    #   ...
    # ]
    
    # Matched trends
    matched_trends = models.ManyToManyField(DesignTrend, blank=True)
    
    analysis_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Trend Analysis for {self.project.name}"


class AIDesignSuggestion(models.Model):
    """AI-generated design suggestions and improvements"""
    SUGGESTION_TYPES = (
        ('color', 'Color Improvement'),
        ('typography', 'Typography Improvement'),
        ('layout', 'Layout Improvement'),
        ('accessibility', 'Accessibility'),
        ('performance', 'Performance'),
        ('consistency', 'Consistency'),
        ('trend', 'Trend Alignment'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='ai_suggestions')
    
    suggestion_type = models.CharField(max_length=50, choices=SUGGESTION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Affected elements
    affected_element_ids = models.JSONField(default=list)
    
    # Suggested changes
    suggested_changes = models.JSONField(default=dict)
    # {
    #   "before": {...},
    #   "after": {...},
    #   "preview_url": "..."
    # }
    
    # User interaction
    is_applied = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_suggestion_type_display()})"

"""
Analytics and Usage Tracking Models
Track user behavior, project metrics, and AI usage
"""
from django.db import models
from django.contrib.auth.models import User


class UserActivity(models.Model):
    """Track user activity for analytics"""
    ACTIVITY_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('project_create', 'Project Created'),
        ('project_update', 'Project Updated'),
        ('project_delete', 'Project Deleted'),
        ('project_export', 'Project Exported'),
        ('ai_generation', 'AI Generation'),
        ('asset_upload', 'Asset Uploaded'),
        ('template_use', 'Template Used'),
        ('collaboration_invite', 'Collaboration Invite'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Contextual data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Performance tracking
    duration_ms = models.IntegerField(null=True, blank=True, help_text="Duration in milliseconds")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class ProjectAnalytics(models.Model):
    """Aggregate analytics for projects"""
    project = models.OneToOneField('projects.Project', on_delete=models.CASCADE, related_name='analytics')
    
    # View and engagement metrics
    view_count = models.IntegerField(default=0)
    edit_count = models.IntegerField(default=0)
    export_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    
    # Time metrics
    total_edit_time_seconds = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    last_edited = models.DateTimeField(null=True, blank=True)
    
    # Component metrics
    total_components = models.IntegerField(default=0)
    ai_generated_components = models.IntegerField(default=0)
    
    # Collaboration metrics
    total_collaborators = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Project analytics'
    
    def __str__(self):
        return f"Analytics for {self.project.name}"


class AIUsageMetrics(models.Model):
    """Track AI service usage for billing and monitoring"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage')
    
    # Usage type
    service_type = models.CharField(max_length=50, choices=(
        ('layout_generation', 'Layout Generation'),
        ('logo_generation', 'Logo Generation'),
        ('image_generation', 'Image Generation'),
        ('color_palette', 'Color Palette'),
        ('font_suggestion', 'Font Suggestion'),
        ('design_refinement', 'Design Refinement'),
    ))
    
    # Token and cost tracking
    tokens_used = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    # Request details
    model_used = models.CharField(max_length=100)
    request_duration_ms = models.IntegerField(help_text="Duration in milliseconds")
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # Reference
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    generation_request = models.ForeignKey('ai_services.AIGenerationRequest', on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['service_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.service_type} ({self.tokens_used} tokens)"


class DailyUsageStats(models.Model):
    """Aggregated daily statistics for dashboard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    
    # Project metrics
    projects_created = models.IntegerField(default=0)
    projects_edited = models.IntegerField(default=0)
    projects_exported = models.IntegerField(default=0)
    
    # AI usage
    ai_generations_count = models.IntegerField(default=0)
    ai_tokens_used = models.IntegerField(default=0)
    ai_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    # Asset usage
    assets_uploaded = models.IntegerField(default=0)
    storage_used_bytes = models.BigIntegerField(default=0)
    
    # Activity
    total_edit_time_seconds = models.IntegerField(default=0)
    unique_sessions = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


class SystemMetrics(models.Model):
    """System-wide metrics for monitoring"""
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # User metrics
    active_users_1h = models.IntegerField(default=0)
    active_users_24h = models.IntegerField(default=0)
    new_users_24h = models.IntegerField(default=0)
    
    # Project metrics
    projects_created_24h = models.IntegerField(default=0)
    projects_edited_24h = models.IntegerField(default=0)
    
    # AI metrics
    ai_requests_24h = models.IntegerField(default=0)
    ai_tokens_used_24h = models.IntegerField(default=0)
    ai_errors_24h = models.IntegerField(default=0)
    
    # Performance metrics
    avg_response_time_ms = models.FloatField(default=0)
    error_rate_percentage = models.FloatField(default=0)
    
    # Storage metrics
    total_storage_bytes = models.BigIntegerField(default=0)
    total_assets = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"System Metrics - {self.timestamp}"


class SearchQuery(models.Model):
    """Track search queries for analytics and improvements"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_queries', null=True, blank=True)
    
    query = models.CharField(max_length=500)
    search_type = models.CharField(max_length=50, choices=[
        ('projects', 'Projects'),
        ('assets', 'Assets'),
        ('templates', 'Templates'),
        ('teams', 'Teams'),
        ('global', 'Global'),
    ])
    
    # Results
    results_count = models.IntegerField(default=0)
    
    # Filters applied
    filters = models.JSONField(default=dict, blank=True)
    
    # Performance
    response_time_ms = models.IntegerField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Search queries'
    
    def __str__(self):
        return f"{self.query} ({self.search_type})"


class FeatureUsage(models.Model):
    """Track feature usage across the platform"""
    feature_name = models.CharField(max_length=100)
    feature_category = models.CharField(max_length=50, choices=[
        ('ai', 'AI Features'),
        ('export', 'Export'),
        ('collaboration', 'Collaboration'),
        ('design', 'Design Tools'),
        ('asset', 'Asset Management'),
        ('other', 'Other'),
    ])
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feature_usage')
    
    # Usage count
    usage_count = models.IntegerField(default=1)
    
    # Context
    context = models.JSONField(default=dict, blank=True)
    
    first_used = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'feature_name']
        ordering = ['-last_used']
    
    def __str__(self):
        return f"{self.user.username} - {self.feature_name}"


class ExportAnalytics(models.Model):
    """Track export usage and performance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_analytics')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='export_analytics')
    
    format = models.CharField(max_length=20)
    file_size_bytes = models.BigIntegerField()
    
    # Performance
    processing_time_ms = models.IntegerField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Export analytics'
    
    def __str__(self):
        return f"{self.user.username} - {self.format} export"

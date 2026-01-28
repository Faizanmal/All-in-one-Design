"""
Design System Analytics Models

Track component usage, style consistency, adoption rates.
"""

from django.db import models
from django.conf import settings
import uuid


class ComponentUsage(models.Model):
    """Track individual component usage."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='usage_stats')
    component_id = models.CharField(max_length=100)
    component_name = models.CharField(max_length=255)
    component_type = models.CharField(max_length=50, blank=True)
    
    # Usage counts
    usage_count = models.IntegerField(default=0)
    project_count = models.IntegerField(default=0)  # Number of unique projects
    
    # Trend tracking
    weekly_usage = models.JSONField(default=list)  # Last 12 weeks
    monthly_usage = models.JSONField(default=list)  # Last 12 months
    
    # Last used
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    last_used_in_project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Override tracking
    override_count = models.IntegerField(default=0)  # Times component was detached/modified
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count']
        unique_together = ['design_system', 'component_id']


class StyleUsage(models.Model):
    """Track style (color, typography, etc.) usage."""
    
    STYLE_TYPES = [
        ('color', 'Color'),
        ('typography', 'Typography'),
        ('effect', 'Effect'),
        ('spacing', 'Spacing'),
        ('border_radius', 'Border Radius'),
        ('shadow', 'Shadow'),
        ('gradient', 'Gradient'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='style_usage_stats')
    
    style_type = models.CharField(max_length=20, choices=STYLE_TYPES)
    style_id = models.CharField(max_length=100)
    style_name = models.CharField(max_length=255)
    style_value = models.TextField(blank=True)
    
    usage_count = models.IntegerField(default=0)
    project_count = models.IntegerField(default=0)
    
    # Consistency tracking
    direct_usage = models.IntegerField(default=0)  # Used via style reference
    hardcoded_usage = models.IntegerField(default=0)  # Same value but not linked
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count']
        unique_together = ['design_system', 'style_id']


class AdoptionMetric(models.Model):
    """Team/project design system adoption metrics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='adoption_metrics')
    
    # Scope
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(max_length=10, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')])
    
    # Metrics
    total_elements = models.IntegerField(default=0)
    system_elements = models.IntegerField(default=0)  # Elements from design system
    adoption_rate = models.FloatField(default=0)  # system_elements / total_elements
    
    # Style consistency
    total_styles = models.IntegerField(default=0)
    linked_styles = models.IntegerField(default=0)
    style_consistency = models.FloatField(default=0)
    
    # Component consistency
    total_components = models.IntegerField(default=0)
    unmodified_components = models.IntegerField(default=0)
    component_consistency = models.FloatField(default=0)
    
    # Detachment events
    detach_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_start']


class DesignSystemHealth(models.Model):
    """Overall health score for a design system."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='health_scores')
    
    # Date of assessment
    assessed_at = models.DateField(auto_now_add=True)
    
    # Health scores (0-100)
    overall_score = models.FloatField(default=0)
    adoption_score = models.FloatField(default=0)
    consistency_score = models.FloatField(default=0)
    coverage_score = models.FloatField(default=0)
    freshness_score = models.FloatField(default=0)
    documentation_score = models.FloatField(default=0)
    
    # Details
    issues = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-assessed_at']
        unique_together = ['design_system', 'assessed_at']


class UsageEvent(models.Model):
    """Individual usage event for detailed tracking."""
    
    EVENT_TYPES = [
        ('insert', 'Component Inserted'),
        ('update', 'Component Updated'),
        ('delete', 'Component Deleted'),
        ('detach', 'Component Detached'),
        ('swap', 'Component Swapped'),
        ('style_apply', 'Style Applied'),
        ('style_detach', 'Style Detached'),
        ('library_publish', 'Library Published'),
        ('library_update', 'Library Updated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='usage_events')
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # What was used
    component_id = models.CharField(max_length=100, blank=True)
    component_name = models.CharField(max_length=255, blank=True)
    style_id = models.CharField(max_length=100, blank=True)
    style_name = models.CharField(max_length=255, blank=True)
    
    # Context
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['design_system', 'event_type', 'created_at']),
            models.Index(fields=['component_id', 'created_at']),
        ]


class DeprecationNotice(models.Model):
    """Track deprecated components/styles."""
    
    DEPRECATED_TYPES = [
        ('component', 'Component'),
        ('style', 'Style'),
        ('variant', 'Variant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='deprecations')
    
    deprecated_type = models.CharField(max_length=20, choices=DEPRECATED_TYPES)
    deprecated_id = models.CharField(max_length=100)
    deprecated_name = models.CharField(max_length=255)
    
    # Replacement suggestion
    replacement_id = models.CharField(max_length=100, blank=True)
    replacement_name = models.CharField(max_length=255, blank=True)
    
    # Timeline
    deprecated_at = models.DateTimeField(auto_now_add=True)
    removal_date = models.DateField(null=True, blank=True)
    
    # Impact
    current_usage_count = models.IntegerField(default=0)
    affected_projects = models.JSONField(default=list)
    
    # Notification
    migration_guide = models.TextField(blank=True)
    notified_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    
    class Meta:
        ordering = ['-deprecated_at']


class AnalyticsDashboard(models.Model):
    """Custom analytics dashboard configuration."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design_system = models.ForeignKey('design_systems.DesignSystem', on_delete=models.CASCADE, related_name='dashboards')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analytics_dashboards')
    
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    
    # Widget configuration
    widgets = models.JSONField(default=list)
    # [
    #   {"type": "adoption_chart", "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
    #   {"type": "top_components", "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
    # ]
    
    # Filters
    default_period = models.CharField(max_length=20, default='30d')
    team_filter = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']

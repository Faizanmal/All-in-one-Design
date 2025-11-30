"""
Advanced Analytics Models
Enhanced analytics, insights, and reporting features
"""
from django.db import models
from django.contrib.auth.models import User


class AnalyticsDashboard(models.Model):
    """Custom analytics dashboards"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_dashboards')
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='analytics_dashboards',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Dashboard layout
    layout = models.JSONField(default=list)
    # [{"widget_id": "uuid", "type": "chart", "position": {"x": 0, "y": 0, "w": 6, "h": 4}, "config": {...}}]
    
    # Sharing
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, related_name='shared_dashboards', blank=True)
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name


class AnalyticsWidget(models.Model):
    """Pre-defined analytics widgets"""
    WIDGET_TYPES = (
        ('line_chart', 'Line Chart'),
        ('bar_chart', 'Bar Chart'),
        ('pie_chart', 'Pie Chart'),
        ('area_chart', 'Area Chart'),
        ('metric', 'Single Metric'),
        ('table', 'Data Table'),
        ('heatmap', 'Heatmap'),
        ('funnel', 'Funnel'),
        ('map', 'Geographic Map'),
        ('timeline', 'Timeline'),
    )
    
    METRIC_TYPES = (
        ('projects_created', 'Projects Created'),
        ('projects_completed', 'Projects Completed'),
        ('designs_exported', 'Designs Exported'),
        ('collaboration_sessions', 'Collaboration Sessions'),
        ('time_spent', 'Time Spent'),
        ('ai_generations', 'AI Generations'),
        ('template_usage', 'Template Usage'),
        ('storage_used', 'Storage Used'),
        ('team_activity', 'Team Activity'),
        ('asset_uploads', 'Asset Uploads'),
        ('comments_made', 'Comments Made'),
        ('versions_created', 'Versions Created'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    widget_type = models.CharField(max_length=50, choices=WIDGET_TYPES)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    
    # Configuration
    config = models.JSONField(default=dict)
    # {"aggregation": "sum", "groupBy": "day", "filters": {...}, "colors": [...]}
    
    # Default size
    default_width = models.IntegerField(default=6)
    default_height = models.IntegerField(default=4)
    
    is_system = models.BooleanField(default=False)  # System-provided widgets
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AnalyticsReport(models.Model):
    """Scheduled analytics reports"""
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    )
    
    FORMAT_CHOICES = (
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('html', 'HTML'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_reports')
    dashboard = models.ForeignKey(
        AnalyticsDashboard,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Report configuration
    metrics = models.JSONField(default=list)
    # ["projects_created", "time_spent", "ai_generations"]
    
    filters = models.JSONField(default=dict)
    # {"date_range": "last_30_days", "project_type": "banner"}
    
    # Schedule
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='weekly')
    send_day = models.IntegerField(default=1)  # Day of week (1-7) or day of month (1-31)
    send_time = models.TimeField(null=True, blank=True)
    
    # Delivery
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='pdf')
    recipients = models.JSONField(default=list)  # List of email addresses
    
    # Status
    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    next_send_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class ReportExecution(models.Model):
    """Track report executions"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    report = models.ForeignKey(AnalyticsReport, on_delete=models.CASCADE, related_name='executions')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Generated report
    file_url = models.URLField(blank=True)
    file_size = models.IntegerField(default=0)
    
    # Execution details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Data snapshot
    data_snapshot = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class UserActivityLog(models.Model):
    """Detailed user activity tracking"""
    ACTION_TYPES = (
        # Project actions
        ('project_create', 'Project Created'),
        ('project_open', 'Project Opened'),
        ('project_save', 'Project Saved'),
        ('project_export', 'Project Exported'),
        ('project_delete', 'Project Deleted'),
        ('project_share', 'Project Shared'),
        
        # Design actions
        ('element_add', 'Element Added'),
        ('element_modify', 'Element Modified'),
        ('element_delete', 'Element Deleted'),
        ('layer_change', 'Layer Changed'),
        
        # AI actions
        ('ai_generate', 'AI Generation'),
        ('ai_suggestion', 'AI Suggestion Used'),
        
        # Collaboration actions
        ('comment_add', 'Comment Added'),
        ('collaboration_join', 'Collaboration Joined'),
        ('collaboration_leave', 'Collaboration Left'),
        
        # Asset actions
        ('asset_upload', 'Asset Uploaded'),
        ('asset_use', 'Asset Used'),
        
        # Template actions
        ('template_use', 'Template Used'),
        ('template_create', 'Template Created'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        related_name='activity_logs',
        null=True,
        blank=True
    )
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    
    # Action details
    details = models.JSONField(default=dict)
    # {"element_type": "text", "element_id": "...", "changes": {...}}
    
    # Context
    session_id = models.CharField(max_length=255, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timing
    duration = models.IntegerField(default=0, help_text="Duration in milliseconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['created_at']),
        ]


class PerformanceMetric(models.Model):
    """System and user performance metrics"""
    METRIC_CATEGORIES = (
        ('page_load', 'Page Load'),
        ('render', 'Render Performance'),
        ('api', 'API Response'),
        ('export', 'Export Performance'),
        ('ai', 'AI Processing'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='performance_metrics',
        null=True,
        blank=True
    )
    
    category = models.CharField(max_length=50, choices=METRIC_CATEGORIES)
    name = models.CharField(max_length=255)
    
    # Metric values
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='ms')
    
    # Context
    context = models.JSONField(default=dict)
    # {"page": "editor", "project_size": "large", "element_count": 150}
    
    # Device info
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'created_at']),
        ]


class UsageQuota(models.Model):
    """Track usage quotas for users/teams"""
    QUOTA_TYPES = (
        ('storage', 'Storage'),
        ('projects', 'Projects'),
        ('exports', 'Exports'),
        ('ai_generations', 'AI Generations'),
        ('collaborators', 'Collaborators'),
        ('api_calls', 'API Calls'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usage_quotas',
        null=True,
        blank=True
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='usage_quotas',
        null=True,
        blank=True
    )
    
    quota_type = models.CharField(max_length=50, choices=QUOTA_TYPES)
    
    # Limits
    limit = models.BigIntegerField()
    used = models.BigIntegerField(default=0)
    
    # Period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Alerts
    alert_threshold = models.IntegerField(default=80)  # Percentage
    alert_sent = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['user', 'team', 'quota_type', 'period_start']
    
    @property
    def usage_percentage(self):
        if self.limit > 0:
            return (self.used / self.limit) * 100
        return 0
    
    @property
    def is_exceeded(self):
        return self.used >= self.limit


class DesignInsight(models.Model):
    """AI-generated design insights"""
    INSIGHT_TYPES = (
        ('accessibility', 'Accessibility'),
        ('performance', 'Performance'),
        ('consistency', 'Consistency'),
        ('best_practice', 'Best Practice'),
        ('trend', 'Design Trend'),
        ('improvement', 'Improvement Suggestion'),
    )
    
    SEVERITY_LEVELS = (
        ('info', 'Info'),
        ('suggestion', 'Suggestion'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='insights')
    
    insight_type = models.CharField(max_length=50, choices=INSIGHT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='suggestion')
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Element reference
    element_id = models.CharField(max_length=255, blank=True)
    element_type = models.CharField(max_length=50, blank=True)
    
    # Suggestion
    suggestion = models.TextField(blank=True)
    auto_fix_available = models.BooleanField(default=False)
    auto_fix_data = models.JSONField(default=dict)
    
    # Status
    is_dismissed = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.insight_type}: {self.title}"

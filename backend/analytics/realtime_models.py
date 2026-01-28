from django.db import models
from django.conf import settings
import uuid


class Heatmap(models.Model):
    """Design engagement heatmap data"""
    HEATMAP_TYPES = [
        ('click', 'Click Heatmap'),
        ('hover', 'Hover Heatmap'),
        ('scroll', 'Scroll Heatmap'),
        ('attention', 'Attention Heatmap'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='heatmaps')
    
    heatmap_type = models.CharField(max_length=20, choices=HEATMAP_TYPES)
    
    # Dimensions
    width = models.IntegerField()
    height = models.IntegerField()
    
    # Data points
    data_points = models.JSONField(default=list)
    # Example: [{"x": 100, "y": 200, "value": 10}, ...]
    
    # Aggregated data
    total_interactions = models.IntegerField(default=0)
    
    # Time range
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Generated image
    heatmap_image = models.ImageField(upload_to='heatmaps/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.heatmap_type}"


class UserFlow(models.Model):
    """User navigation flow through designs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='user_flows')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Flow steps
    steps = models.JSONField(default=list)
    # Example: [{"page": "page_id", "time_spent": 30, "next_page": "page_id"}, ...]
    
    # Entry and exit points
    entry_point = models.CharField(max_length=255, blank=True)
    exit_points = models.JSONField(default=list)
    
    # Metrics
    total_users = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0)
    average_time = models.FloatField(default=0)  # seconds
    
    # Drop-off analysis
    drop_off_points = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class DesignSession(models.Model):
    """Individual user session on a design"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='design_sessions')
    
    # Session info
    session_id = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Device info
    device_type = models.CharField(max_length=50, blank=True)  # desktop, mobile, tablet
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    screen_width = models.IntegerField(null=True, blank=True)
    screen_height = models.IntegerField(null=True, blank=True)
    
    # Location
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Timing
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    total_duration = models.IntegerField(default=0)  # seconds
    
    # Pages viewed
    pages_viewed = models.JSONField(default=list)
    
    # Interactions
    click_count = models.IntegerField(default=0)
    scroll_depth = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session {self.session_id[:8]}"


class DesignInteraction(models.Model):
    """Individual interactions with design elements"""
    INTERACTION_TYPES = [
        ('click', 'Click'),
        ('hover', 'Hover'),
        ('scroll', 'Scroll'),
        ('zoom', 'Zoom'),
        ('pan', 'Pan'),
        ('select', 'Select'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(DesignSession, on_delete=models.CASCADE, related_name='interactions')
    
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    
    # Position
    x = models.FloatField()
    y = models.FloatField()
    
    # Target element
    element_id = models.CharField(max_length=255, blank=True)
    element_type = models.CharField(max_length=100, blank=True)
    
    # Page
    page_id = models.CharField(max_length=255, blank=True)
    
    timestamp = models.DateTimeField()
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['timestamp']


class DesignMetric(models.Model):
    """Aggregated design metrics"""
    METRIC_TYPES = [
        ('views', 'Total Views'),
        ('unique_visitors', 'Unique Visitors'),
        ('avg_time', 'Average Time'),
        ('bounce_rate', 'Bounce Rate'),
        ('engagement', 'Engagement Score'),
    ]
    
    PERIOD_TYPES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='design_metrics')
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    period_start = models.DateTimeField()
    
    # Value
    value = models.FloatField()
    
    # Comparison
    previous_value = models.FloatField(null=True, blank=True)
    change_percent = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['project', 'metric_type', 'period_type', 'period_start']


class ElementAnalytics(models.Model):
    """Analytics for individual design elements"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='element_analytics')
    
    element_id = models.CharField(max_length=255)
    element_type = models.CharField(max_length=100)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Metrics
    click_count = models.IntegerField(default=0)
    hover_count = models.IntegerField(default=0)
    hover_duration_avg = models.FloatField(default=0)  # seconds
    
    # Visibility
    visibility_count = models.IntegerField(default=0)  # Times scrolled into view
    
    # Attention
    attention_score = models.FloatField(default=0)
    
    # Time range
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attention_score']


class ConversionGoal(models.Model):
    """Conversion goals for designs"""
    GOAL_TYPES = [
        ('click', 'Element Click'),
        ('page_view', 'Page View'),
        ('time_on_page', 'Time on Page'),
        ('scroll_depth', 'Scroll Depth'),
        ('form_submit', 'Form Submit'),
        ('download', 'Download'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='conversion_goals')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=50, choices=GOAL_TYPES)
    
    # Target
    target_element_id = models.CharField(max_length=255, blank=True)
    target_page_id = models.CharField(max_length=255, blank=True)
    target_value = models.FloatField(null=True, blank=True)  # e.g., scroll depth %, time in seconds
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ConversionEvent(models.Model):
    """Conversion events"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(ConversionGoal, on_delete=models.CASCADE, related_name='events')
    session = models.ForeignKey(DesignSession, on_delete=models.CASCADE, related_name='conversions')
    
    # Event details
    value = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    
    timestamp = models.DateTimeField()
    
    class Meta:
        ordering = ['-timestamp']


class CompetitorAnalysis(models.Model):
    """Competitor design analysis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competitor_analyses')
    
    name = models.CharField(max_length=255)
    competitor_url = models.URLField()
    
    # Analysis results
    design_score = models.FloatField(null=True, blank=True)
    ux_score = models.FloatField(null=True, blank=True)
    accessibility_score = models.FloatField(null=True, blank=True)
    
    # Extracted data
    colors_used = models.JSONField(default=list)
    fonts_used = models.JSONField(default=list)
    technologies = models.JSONField(default=list)
    
    # Screenshots
    screenshot = models.ImageField(upload_to='competitor_screenshots/', null=True, blank=True)
    
    # AI insights
    ai_insights = models.JSONField(default=list)
    
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return self.name


class RealtimeAnalyticsDashboard(models.Model):
    """Custom analytics dashboards"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='realtime_analytics_dashboards')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Dashboard configuration
    widgets = models.JSONField(default=list)
    # Example: [{"type": "chart", "metric": "views", "position": {"x": 0, "y": 0, "w": 4, "h": 3}}]
    
    # Filters
    default_filters = models.JSONField(default=dict)
    # Example: {"date_range": "last_30_days", "projects": ["uuid1", "uuid2"]}
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RealtimeAnalyticsReport(models.Model):
    """Generated analytics reports"""
    REPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='realtime_analytics_reports')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='realtime_analytics_reports', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    report_format = models.CharField(max_length=10, choices=REPORT_FORMATS)
    
    # Report configuration
    metrics_included = models.JSONField(default=list)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    
    # Generated file
    file = models.FileField(upload_to='analytics_reports/', null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='pending')  # pending, generating, completed, failed
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

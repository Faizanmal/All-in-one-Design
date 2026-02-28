"""
Productivity Enhancement Models
A/B Testing, Plugins, and Offline Support
"""
from django.db import models
from django.contrib.auth.models import User


class ABTest(models.Model):
    """A/B test configurations for designs"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    )
    
    GOAL_CHOICES = (
        ('clicks', 'Clicks'),
        ('conversions', 'Conversions'),
        ('engagement_time', 'Engagement Time'),
        ('scroll_depth', 'Scroll Depth'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_ab_tests_user')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='project_ab_tests')
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Test configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Traffic allocation
    traffic_percentage = models.IntegerField(default=100, help_text="Percentage of visitors to include in test")
    
    # Goals
    primary_goal = models.CharField(max_length=100, choices=GOAL_CHOICES, default='clicks')
    goals = models.JSONField(default=list)
    # ["clicks", "conversions", "engagement_time", "scroll_depth"]
    
    # Target audience configuration
    target_audience = models.JSONField(default=dict, blank=True)
    # {"device": ["desktop", "mobile"], "location": ["US", "EU"], "traffic_source": ["organic"]}
    
    # Statistical settings
    min_sample_size = models.IntegerField(default=100, help_text="Minimum sample size per variant")
    confidence_threshold = models.FloatField(default=95.0, help_text="Required confidence level (0-100)")
    
    # Winner
    winning_variant = models.ForeignKey(
        'ABTestVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='won_tests'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class ABTestVariant(models.Model):
    """Individual variants in an A/B test"""
    test = models.ForeignKey(ABTest, on_delete=models.CASCADE, related_name='variants')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Design data for this variant
    design_data = models.JSONField(default=dict)
    
    # Traffic percentage for this variant
    traffic_percentage = models.IntegerField(default=50, help_text="Traffic percentage for this variant")
    
    # Control variant flag
    is_control = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.name} ({self.test.name})"


class ABTestResult(models.Model):
    """Results and analytics for A/B test variants"""
    variant = models.OneToOneField(ABTestVariant, on_delete=models.CASCADE, related_name='results')
    
    # Traffic
    impressions = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    
    # Engagement
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    total_engagement_time = models.IntegerField(default=0, help_text="Total time in seconds")
    
    # Rates
    click_rate = models.FloatField(default=0)
    conversion_rate = models.FloatField(default=0)
    avg_engagement_time = models.FloatField(default=0)
    
    # Statistical significance
    confidence_level = models.FloatField(default=0, help_text="Statistical confidence (0-100)")
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Results for {self.variant.name}"


class ABTestEvent(models.Model):
    """Track individual events in A/B tests"""
    EVENT_TYPES = (
        ('impression', 'Impression'),
        ('click', 'Click'),
        ('conversion', 'Conversion'),
        ('engagement', 'Engagement'),
        ('scroll', 'Scroll'),
        ('hover', 'Hover'),
    )
    
    variant = models.ForeignKey(ABTestVariant, on_delete=models.CASCADE, related_name='events')
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Visitor info
    visitor_id = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255)
    
    # Event data
    event_data = models.JSONField(default=dict)
    # {"element_id": "cta-button", "x": 100, "y": 200, "duration": 5}
    
    # Context
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    referrer = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant', 'event_type']),
            models.Index(fields=['visitor_id']),
        ]


class Plugin(models.Model):
    """Plugin definitions for the plugin ecosystem"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('published', 'Published'),
        ('deprecated', 'Deprecated'),
    )
    
    CATEGORY_CHOICES = (
        ('tools', 'Tools'),
        ('effects', 'Effects'),
        ('integrations', 'Integrations'),
        ('ai', 'AI & Automation'),
        ('export', 'Export'),
        ('collaboration', 'Collaboration'),
        ('analytics', 'Analytics'),
        ('other', 'Other'),
    )
    
    # Creator
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_plugins')
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Version
    version = models.CharField(max_length=50)
    changelog = models.TextField(blank=True)
    
    # Plugin code and hooks
    entry_point = models.CharField(max_length=255, help_text="Main function/class name")
    source_code = models.TextField(blank=True, help_text="Plugin source code (for sandboxed execution)")
    source_url = models.URLField(blank=True, help_text="External source URL")
    hooks = models.JSONField(default=list, help_text="List of hooks this plugin uses")
    # ["canvas:onLoad", "canvas:onSave", "toolbar:addButton", "menu:addItem"]
    api_version = models.CharField(max_length=20, default='1.0', help_text="Minimum API version required")
    
    # Configuration schema
    config_schema = models.JSONField(default=dict, help_text="JSON Schema for plugin configuration")
    
    # Requirements and permissions
    permissions = models.JSONField(default=list)
    # ["canvas:read", "canvas:write", "user:read", "api:external"]
    
    # Assets
    icon = models.ImageField(upload_to='plugins/icons/', null=True, blank=True)
    banner = models.ImageField(upload_to='plugins/banners/', null=True, blank=True)
    screenshots = models.JSONField(default=list)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    is_free = models.BooleanField(default=True)
    
    # Stats
    installs = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_official = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-installs']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class PluginInstallation(models.Model):
    """Track plugin installations by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_installed_plugins')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='installations')
    
    # Version installed
    installed_version = models.CharField(max_length=50)
    
    # Configuration
    config = models.JSONField(default=dict)
    
    # Status
    is_enabled = models.BooleanField(default=True)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'plugin']
        ordering = ['-installed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plugin.name}"


class PluginReview(models.Model):
    """User reviews for plugins"""
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_plugin_reviews')
    
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    review = models.TextField()
    
    is_verified_install = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['plugin', 'user']
        ordering = ['-created_at']


class OfflineSync(models.Model):
    """Track offline changes for synchronization"""
    SYNC_STATUS = (
        ('pending', 'Pending'),
        ('syncing', 'Syncing'),
        ('completed', 'Completed'),
        ('conflict', 'Conflict'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offline_syncs')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='offline_syncs')
    
    # Change tracking
    changes = models.JSONField(default=list)
    # [
    #   {"type": "update", "path": "elements[0].position", "value": {...}, "timestamp": "..."},
    #   {"type": "add", "path": "elements", "value": {...}, "timestamp": "..."},
    # ]
    
    # Version tracking
    last_known_version = models.CharField(max_length=100, blank=True)
    
    # Sync status
    status = models.CharField(max_length=20, choices=SYNC_STATUS, default='pending')
    
    # Conflict resolution
    conflicts = models.JSONField(default=list)
    resolved_changes = models.JSONField(default=list)
    
    # Device info
    device_id = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255, blank=True)
    client_version = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Offline sync for {self.project.name} ({self.status})"


class UserPreference(models.Model):
    """User preferences and settings for offline support"""
    THEME_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='productivity_preferences')
    
    # UI preferences
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='system')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    keyboard_shortcuts = models.JSONField(default=dict)
    
    # Editor preferences
    auto_save = models.BooleanField(default=True)
    auto_save_interval = models.IntegerField(default=30, help_text="Seconds between auto-saves")
    canvas_grid = models.BooleanField(default=True)
    snap_to_grid = models.BooleanField(default=True)
    grid_size = models.IntegerField(default=10)
    default_export_format = models.CharField(max_length=20, default='png')
    
    # Notification preferences
    notification_email = models.BooleanField(default=True)
    notification_push = models.BooleanField(default=True)
    notification_sound = models.BooleanField(default=True)
    
    # Offline settings
    offline_mode = models.BooleanField(default=True, help_text="Enable offline mode support")
    offline_projects = models.JSONField(default=list)  # List of project IDs
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"

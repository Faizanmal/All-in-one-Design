from django.db import models
from django.conf import settings
import uuid


class PluginCategory(models.Model):
    """Plugin categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    
    # Display order
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Plugin Category'
        verbose_name_plural = 'Plugin Categories'
    
    def __str__(self):
        return self.name


class Plugin(models.Model):
    """Plugin definitions"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('published', 'Published'),
        ('deprecated', 'Deprecated'),
    ]
    
    PRICING_TYPES = [
        ('free', 'Free'),
        ('freemium', 'Freemium'),
        ('paid', 'Paid'),
        ('subscription', 'Subscription'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='developed_plugins')
    category = models.ForeignKey(PluginCategory, on_delete=models.SET_NULL, null=True, related_name='plugins')
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    
    # Branding
    icon = models.ImageField(upload_to='plugin_icons/')
    banner = models.ImageField(upload_to='plugin_banners/', null=True, blank=True)
    screenshots = models.JSONField(default=list)
    
    # Version info
    current_version = models.CharField(max_length=50)
    min_platform_version = models.CharField(max_length=50, default='1.0.0')
    
    # Source code / package
    source_url = models.URLField(blank=True)
    package_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Pricing
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_currency = models.CharField(max_length=3, default='USD')
    
    # Stats
    install_count = models.IntegerField(default=0)
    active_installs = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    
    # Metadata
    tags = models.JSONField(default=list)
    features = models.JSONField(default=list)
    requirements = models.JSONField(default=dict)
    
    # Permissions
    permissions = models.JSONField(default=list)
    # Example: ["read:projects", "write:projects", "access:canvas"]
    
    # Support
    documentation_url = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    changelog_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-install_count']
    
    def __str__(self):
        return self.name


class PluginVersion(models.Model):
    """Plugin version history"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='versions')
    
    version = models.CharField(max_length=50)
    
    # Release info
    release_notes = models.TextField(blank=True)
    is_stable = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)
    
    # Package
    package_file = models.FileField(upload_to='plugin_packages/')
    package_size = models.BigIntegerField(default=0)
    
    # Checksums
    checksum_sha256 = models.CharField(max_length=64, blank=True)
    
    # Platform compatibility
    min_platform_version = models.CharField(max_length=50)
    max_platform_version = models.CharField(max_length=50, blank=True)
    
    # Download stats
    download_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['plugin', 'version']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.plugin.name} v{self.version}"


class PluginInstallation(models.Model):
    """User's installed plugins"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='installed_plugins')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='installations')
    version = models.ForeignKey(PluginVersion, on_delete=models.SET_NULL, null=True)
    
    # Installation status
    is_enabled = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=True)
    
    # User settings for this plugin
    settings = models.JSONField(default=dict)
    
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'plugin']
        ordering = ['-installed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plugin.name}"


class PluginReview(models.Model):
    """Plugin reviews from users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plugin_reviews')
    
    rating = models.IntegerField()  # 1-5
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    
    # Version reviewed
    version = models.CharField(max_length=50, blank=True)
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    # Developer response
    developer_response = models.TextField(blank=True)
    developer_responded_at = models.DateTimeField(null=True, blank=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['plugin', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.plugin.name} - {self.rating}★ by {self.user.username}"


class PluginPurchase(models.Model):
    """Plugin purchases for paid plugins"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='plugin_purchases')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='purchases')
    
    # Payment info
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # For subscriptions
    is_subscription = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    # Refund
    is_refunded = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)
    
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.plugin.name}"


class DeveloperProfile(models.Model):
    """Developer profile for the marketplace"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='developer_profile')
    
    display_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='developer_avatars/', null=True, blank=True)
    
    # Links
    website = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Payout info
    payout_email = models.EmailField(blank=True)
    payout_method = models.CharField(max_length=50, blank=True)  # paypal, stripe, etc.
    
    # Stats
    total_plugins = models.IntegerField(default=0)
    total_installs = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Developer Profile'
        verbose_name_plural = 'Developer Profiles'
    
    def __str__(self):
        return self.display_name


class APIEndpoint(models.Model):
    """Plugin API endpoints registry"""
    METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, choices=METHODS)
    
    description = models.TextField(blank=True)
    
    # Parameters
    parameters = models.JSONField(default=list)
    # Example: [{"name": "project_id", "type": "string", "required": true}]
    
    # Response schema
    response_schema = models.JSONField(default=dict)
    
    # Required permissions
    required_permissions = models.JSONField(default=list)
    
    # Version
    api_version = models.CharField(max_length=20, default='v1')
    is_deprecated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['path', 'method']
    
    def __str__(self):
        return f"{self.method} {self.path}"


class WebhookSubscription(models.Model):
    """Plugin webhook subscriptions"""
    EVENT_TYPES = [
        ('project.created', 'Project Created'),
        ('project.updated', 'Project Updated'),
        ('project.deleted', 'Project Deleted'),
        ('canvas.changed', 'Canvas Changed'),
        ('asset.uploaded', 'Asset Uploaded'),
        ('comment.added', 'Comment Added'),
        ('export.completed', 'Export Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='webhook_subscriptions')
    installation = models.ForeignKey(PluginInstallation, on_delete=models.CASCADE, related_name='webhooks')
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    callback_url = models.URLField()
    
    # Security
    secret = models.CharField(max_length=255)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    failure_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class PluginLog(models.Model):
    """Plugin activity logs"""
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    installation = models.ForeignKey(PluginInstallation, on_delete=models.CASCADE, related_name='logs')
    
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    details = models.JSONField(default=dict)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


class PluginSandbox(models.Model):
    """Plugin sandbox environments for testing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    developer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sandboxes')
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE, related_name='sandboxes', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    
    # Sandbox settings
    settings = models.JSONField(default=dict)
    
    # Test data
    test_project_id = models.UUIDField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Plugin Sandbox'
        verbose_name_plural = 'Plugin Sandboxes'
    
    def __str__(self):
        return self.name

"""
Mobile API Models

Models for supporting mobile apps (iOS/Android) for design viewing,
commenting, and presentation mode.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class MobileDevice(models.Model):
    """
    Registered mobile devices for push notifications and syncing.
    """
    
    PLATFORM_IOS = 'ios'
    PLATFORM_ANDROID = 'android'
    PLATFORM_CHOICES = [
        (PLATFORM_IOS, 'iOS'),
        (PLATFORM_ANDROID, 'Android'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mobile_devices'
    )
    
    # Device info
    device_id = models.CharField(max_length=255, unique=True)
    device_name = models.CharField(max_length=255, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    
    # Push notification tokens
    push_token = models.CharField(max_length=500, blank=True)
    push_enabled = models.BooleanField(default=True)
    
    # Device capabilities
    supports_biometrics = models.BooleanField(default=False)
    biometrics_enabled = models.BooleanField(default=False)
    
    # Screen info for responsive previews
    screen_width = models.IntegerField(null=True, blank=True)
    screen_height = models.IntegerField(null=True, blank=True)
    screen_scale = models.FloatField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)
    
    # Security
    trusted = models.BooleanField(default=False)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_active']
        verbose_name = 'Mobile Device'
        verbose_name_plural = 'Mobile Devices'
    
    def __str__(self):
        return f"{self.device_name or 'Unknown'} ({self.platform})"


class MobileSession(models.Model):
    """
    Active mobile sessions for tracking activity and syncing.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        MobileDevice,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    # Session token
    session_token = models.CharField(max_length=255, unique=True)
    
    # Session info
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Current activity
    current_project_id = models.CharField(max_length=100, blank=True)
    current_view = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'Mobile Session'
        verbose_name_plural = 'Mobile Sessions'


class OfflineCache(models.Model):
    """
    Cached content for offline viewing on mobile.
    """
    
    CACHE_TYPE_PROJECT = 'project'
    CACHE_TYPE_COMPONENT = 'component'
    CACHE_TYPE_ASSET = 'asset'
    CACHE_TYPE_PRESENTATION = 'presentation'
    TYPE_CHOICES = [
        (CACHE_TYPE_PROJECT, 'Project'),
        (CACHE_TYPE_COMPONENT, 'Component'),
        (CACHE_TYPE_ASSET, 'Asset'),
        (CACHE_TYPE_PRESENTATION, 'Presentation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        MobileDevice,
        on_delete=models.CASCADE,
        related_name='offline_cache'
    )
    
    # Content reference
    cache_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content_id = models.CharField(max_length=100)
    
    # Version tracking
    version = models.IntegerField(default=1)
    server_updated_at = models.DateTimeField()
    
    # Cache status
    cached_at = models.DateTimeField(auto_now=True)
    is_stale = models.BooleanField(default=False)
    
    # Size tracking
    cache_size = models.BigIntegerField(default=0)  # bytes
    
    # Priority
    priority = models.IntegerField(default=0)  # Higher = keep longer
    
    class Meta:
        unique_together = ['device', 'cache_type', 'content_id']
        ordering = ['-priority', '-cached_at']
        verbose_name = 'Offline Cache'
        verbose_name_plural = 'Offline Caches'


class MobileAnnotation(models.Model):
    """
    Annotations added from mobile devices.
    """
    
    ANNOTATION_TYPE_PIN = 'pin'
    ANNOTATION_TYPE_DRAW = 'draw'
    ANNOTATION_TYPE_VOICE = 'voice'
    TYPE_CHOICES = [
        (ANNOTATION_TYPE_PIN, 'Pin/Comment'),
        (ANNOTATION_TYPE_DRAW, 'Drawing'),
        (ANNOTATION_TYPE_VOICE, 'Voice Note'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='mobile_annotations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mobile_annotations'
    )
    device = models.ForeignKey(
        MobileDevice,
        on_delete=models.SET_NULL,
        null=True,
        related_name='annotations'
    )
    
    # Annotation type
    annotation_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Position on design
    position_x = models.FloatField()
    position_y = models.FloatField()
    
    # For which frame/screen
    screen_id = models.CharField(max_length=100, blank=True)
    
    # Content
    comment = models.TextField(blank=True)
    
    # For drawings
    drawing_data = models.JSONField(null=True, blank=True)
    # {"paths": [{"points": [...], "color": "#...", "width": 2}]}
    
    # For voice notes
    voice_recording = models.FileField(upload_to='voice_annotations/', null=True, blank=True)
    voice_duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # Visibility
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_mobile_annotations'
    )
    
    # Sync status
    synced = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mobile Annotation'
        verbose_name_plural = 'Mobile Annotations'


class MobileNotification(models.Model):
    """
    Notifications sent to mobile devices.
    """
    
    NOTIFICATION_TYPE_MENTION = 'mention'
    NOTIFICATION_TYPE_COMMENT = 'comment'
    NOTIFICATION_TYPE_SHARE = 'share'
    NOTIFICATION_TYPE_UPDATE = 'update'
    NOTIFICATION_TYPE_REVIEW = 'review'
    TYPE_CHOICES = [
        (NOTIFICATION_TYPE_MENTION, 'Mention'),
        (NOTIFICATION_TYPE_COMMENT, 'Comment'),
        (NOTIFICATION_TYPE_SHARE, 'Share'),
        (NOTIFICATION_TYPE_UPDATE, 'Update'),
        (NOTIFICATION_TYPE_REVIEW, 'Review Request'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        MobileDevice,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mobile_notifications'
    )
    
    # Notification content
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    
    # Deep link
    action_url = models.CharField(max_length=500, blank=True)
    
    # Related content
    project_id = models.CharField(max_length=100, blank=True)
    comment_id = models.CharField(max_length=100, blank=True)
    
    # Triggered by
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='triggered_mobile_notifications'
    )
    
    # Status
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification ID (from provider)
    push_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mobile Notification'
        verbose_name_plural = 'Mobile Notifications'


class MobilePreference(models.Model):
    """
    User preferences specific to mobile app.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mobile_preferences'
    )
    
    # Display preferences
    default_zoom = models.FloatField(default=1.0)
    dark_mode = models.BooleanField(default=False)
    reduced_motion = models.BooleanField(default=False)
    
    # Notification preferences
    notify_comments = models.BooleanField(default=True)
    notify_mentions = models.BooleanField(default=True)
    notify_updates = models.BooleanField(default=True)
    notify_reviews = models.BooleanField(default=True)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    # Data preferences
    auto_download_projects = models.BooleanField(default=False)
    max_cache_size = models.BigIntegerField(default=500 * 1024 * 1024)  # 500 MB
    wifi_only = models.BooleanField(default=True)
    
    # Security
    require_auth_for_view = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mobile Preference'
        verbose_name_plural = 'Mobile Preferences'


class MobileAppVersion(models.Model):
    """
    Track mobile app versions for compatibility.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    platform = models.CharField(max_length=20, choices=MobileDevice.PLATFORM_CHOICES)
    version = models.CharField(max_length=50)
    build_number = models.IntegerField()
    
    # Status
    is_required = models.BooleanField(default=False)  # Force update
    is_latest = models.BooleanField(default=False)
    is_deprecated = models.BooleanField(default=False)
    
    # Store links
    store_url = models.URLField(blank=True)
    
    # Release info
    release_notes = models.TextField(blank=True)
    
    # Compatibility
    min_api_version = models.CharField(max_length=50, blank=True)
    
    released_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-build_number']
        unique_together = ['platform', 'version']
        verbose_name = 'Mobile App Version'
        verbose_name_plural = 'Mobile App Versions'
    
    def __str__(self):
        return f"{self.platform} v{self.version}"

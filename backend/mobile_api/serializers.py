"""
Serializers for Mobile API app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    MobileDevice, MobileSession, OfflineCache, MobileAnnotation,
    MobileNotification, MobilePreference, MobileAppVersion
)

User = get_user_model()


class MobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for mobile devices."""
    
    class Meta:
        model = MobileDevice
        fields = [
            'id', 'device_id', 'device_name', 'platform', 'os_version',
            'app_version', 'push_token', 'push_enabled', 'supports_biometrics',
            'biometrics_enabled', 'screen_width', 'screen_height', 'screen_scale',
            'is_active', 'last_active', 'trusted', 'created_at'
        ]
        read_only_fields = ['id', 'last_active', 'created_at', 'trusted']


class MobileDeviceRegisterSerializer(serializers.Serializer):
    """Serializer for registering a mobile device."""
    
    device_id = serializers.CharField(max_length=255)
    device_name = serializers.CharField(max_length=255, required=False, default='')
    platform = serializers.ChoiceField(choices=MobileDevice.PLATFORM_CHOICES)
    os_version = serializers.CharField(max_length=50, required=False, default='')
    app_version = serializers.CharField(max_length=50, required=False, default='')
    push_token = serializers.CharField(max_length=500, required=False, default='')
    screen_width = serializers.IntegerField(required=False)
    screen_height = serializers.IntegerField(required=False)
    screen_scale = serializers.FloatField(required=False)
    supports_biometrics = serializers.BooleanField(required=False, default=False)


class MobileSessionSerializer(serializers.ModelSerializer):
    """Serializer for mobile sessions."""
    
    device = MobileDeviceSerializer(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileSession
        fields = [
            'id', 'device', 'session_token', 'started_at', 'expires_at',
            'last_activity', 'is_active', 'current_project_id', 'current_view',
            'time_remaining'
        ]
        read_only_fields = ['id', 'session_token', 'started_at', 'last_activity']
    
    def get_time_remaining(self, obj) -> int:
        """Get time remaining in seconds."""
        if obj.expires_at:
            remaining = obj.expires_at - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0


class CreateSessionSerializer(serializers.Serializer):
    """Serializer for creating a mobile session."""
    
    device_id = serializers.CharField(max_length=255)
    session_duration_hours = serializers.IntegerField(default=24, min_value=1, max_value=720)


class RefreshSessionSerializer(serializers.Serializer):
    """Serializer for refreshing a mobile session."""
    
    session_token = serializers.CharField(max_length=255)
    extend_hours = serializers.IntegerField(default=24, min_value=1, max_value=720)


class OfflineCacheSerializer(serializers.ModelSerializer):
    """Serializer for offline cache entries."""
    
    cache_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = OfflineCache
        fields = [
            'id', 'device', 'cache_type', 'content_id', 'version',
            'server_updated_at', 'cached_at', 'is_stale', 'cache_size',
            'cache_size_mb', 'priority'
        ]
        read_only_fields = ['id', 'cached_at', 'is_stale']
    
    def get_cache_size_mb(self, obj) -> float:
        """Get cache size in megabytes."""
        return round(obj.cache_size / (1024 * 1024), 2)


class CacheContentSerializer(serializers.Serializer):
    """Serializer for caching content."""
    
    cache_type = serializers.ChoiceField(choices=OfflineCache.TYPE_CHOICES)
    content_id = serializers.CharField(max_length=100)
    priority = serializers.IntegerField(default=0, min_value=0, max_value=100)


class SyncStatusSerializer(serializers.Serializer):
    """Serializer for sync status response."""
    
    content_id = serializers.CharField()
    cache_type = serializers.CharField()
    local_version = serializers.IntegerField()
    server_version = serializers.IntegerField()
    is_stale = serializers.BooleanField()
    needs_update = serializers.BooleanField()


class MobileAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for mobile annotations."""
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileAnnotation
        fields = [
            'id', 'project', 'user', 'user_name', 'device', 'annotation_type',
            'position_x', 'position_y', 'screen_id', 'comment', 'drawing_data',
            'voice_recording', 'voice_duration', 'is_resolved', 'resolved_by',
            'synced', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_name', 'synced', 'created_at', 'updated_at']
    
    def get_user_name(self, obj) -> str:
        """Get user display name."""
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return 'Unknown'


class CreateAnnotationSerializer(serializers.Serializer):
    """Serializer for creating an annotation."""
    
    project_id = serializers.UUIDField()
    annotation_type = serializers.ChoiceField(choices=MobileAnnotation.TYPE_CHOICES)
    position_x = serializers.FloatField()
    position_y = serializers.FloatField()
    screen_id = serializers.CharField(max_length=100, required=False, default='')
    comment = serializers.CharField(required=False, default='')
    drawing_data = serializers.JSONField(required=False)


class VoiceAnnotationSerializer(serializers.Serializer):
    """Serializer for voice annotation upload."""
    
    project_id = serializers.UUIDField()
    position_x = serializers.FloatField()
    position_y = serializers.FloatField()
    screen_id = serializers.CharField(max_length=100, required=False, default='')
    voice_file = serializers.FileField()
    duration = serializers.IntegerField()


class MobileNotificationSerializer(serializers.ModelSerializer):
    """Serializer for mobile notifications."""
    
    triggered_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MobileNotification
        fields = [
            'id', 'device', 'user', 'notification_type', 'title', 'body',
            'action_url', 'project_id', 'comment_id', 'triggered_by',
            'triggered_by_name', 'sent', 'sent_at', 'read', 'read_at',
            'push_id', 'created_at'
        ]
        read_only_fields = ['id', 'sent', 'sent_at', 'push_id', 'created_at']
    
    def get_triggered_by_name(self, obj) -> str:
        """Get triggering user name."""
        if obj.triggered_by:
            return obj.triggered_by.get_full_name() or obj.triggered_by.username
        return 'System'


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists."""
    
    class Meta:
        model = MobileNotification
        fields = [
            'id', 'notification_type', 'title', 'body', 'action_url',
            'read', 'created_at'
        ]


class MarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)


class MobilePreferenceSerializer(serializers.ModelSerializer):
    """Serializer for mobile preferences."""
    
    max_cache_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = MobilePreference
        fields = [
            'id', 'default_zoom', 'dark_mode', 'reduced_motion',
            'notify_comments', 'notify_mentions', 'notify_updates',
            'notify_reviews', 'quiet_hours_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'auto_download_projects', 'max_cache_size',
            'max_cache_size_mb', 'wifi_only', 'require_auth_for_view',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_max_cache_size_mb(self, obj) -> int:
        """Get max cache size in megabytes."""
        return obj.max_cache_size // (1024 * 1024)


class UpdatePreferencesSerializer(serializers.Serializer):
    """Serializer for updating preferences."""
    
    default_zoom = serializers.FloatField(min_value=0.1, max_value=5.0, required=False)
    dark_mode = serializers.BooleanField(required=False)
    reduced_motion = serializers.BooleanField(required=False)
    notify_comments = serializers.BooleanField(required=False)
    notify_mentions = serializers.BooleanField(required=False)
    notify_updates = serializers.BooleanField(required=False)
    notify_reviews = serializers.BooleanField(required=False)
    quiet_hours_enabled = serializers.BooleanField(required=False)
    quiet_hours_start = serializers.TimeField(required=False)
    quiet_hours_end = serializers.TimeField(required=False)
    auto_download_projects = serializers.BooleanField(required=False)
    max_cache_size_mb = serializers.IntegerField(min_value=100, max_value=10000, required=False)
    wifi_only = serializers.BooleanField(required=False)
    require_auth_for_view = serializers.BooleanField(required=False)


class MobileAppVersionSerializer(serializers.ModelSerializer):
    """Serializer for mobile app versions."""
    
    class Meta:
        model = MobileAppVersion
        fields = [
            'id', 'platform', 'version', 'build_number', 'is_required',
            'is_latest', 'is_deprecated', 'store_url', 'release_notes',
            'min_api_version', 'released_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppVersionCheckSerializer(serializers.Serializer):
    """Serializer for checking app version."""
    
    platform = serializers.ChoiceField(choices=MobileDevice.PLATFORM_CHOICES)
    current_version = serializers.CharField(max_length=50)
    build_number = serializers.IntegerField()


class AppVersionStatusSerializer(serializers.Serializer):
    """Serializer for app version status response."""
    
    current_version = serializers.CharField()
    latest_version = serializers.CharField()
    is_latest = serializers.BooleanField()
    update_required = serializers.BooleanField()
    update_available = serializers.BooleanField()
    store_url = serializers.CharField()
    release_notes = serializers.CharField()


class PushTokenUpdateSerializer(serializers.Serializer):
    """Serializer for updating push token."""
    
    device_id = serializers.CharField(max_length=255)
    push_token = serializers.CharField(max_length=500)


class BiometricAuthSerializer(serializers.Serializer):
    """Serializer for biometric authentication setup."""
    
    device_id = serializers.CharField(max_length=255)
    enable = serializers.BooleanField()
    public_key = serializers.CharField(required=False)


class ProjectSyncRequestSerializer(serializers.Serializer):
    """Serializer for project sync request."""
    
    project_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    last_sync = serializers.DateTimeField(required=False)
    include_assets = serializers.BooleanField(default=False)


class ProjectSyncResponseSerializer(serializers.Serializer):
    """Serializer for project sync response."""
    
    project_id = serializers.UUIDField()
    name = serializers.CharField()
    version = serializers.IntegerField()
    updated_at = serializers.DateTimeField()
    thumbnail_url = serializers.CharField()
    needs_download = serializers.BooleanField()
    size_bytes = serializers.IntegerField()


class MobileViewEventSerializer(serializers.Serializer):
    """Serializer for tracking mobile view events."""
    
    event_type = serializers.ChoiceField(choices=[
        ('view_project', 'View Project'),
        ('view_screen', 'View Screen'),
        ('comment', 'Comment'),
        ('annotate', 'Annotate'),
        ('share', 'Share'),
        ('download', 'Download'),
    ])
    project_id = serializers.UUIDField(required=False)
    screen_id = serializers.CharField(max_length=100, required=False)
    duration_seconds = serializers.IntegerField(required=False)
    metadata = serializers.JSONField(required=False)

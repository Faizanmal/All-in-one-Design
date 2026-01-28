from rest_framework import serializers
from .models import OfflineProject, SyncQueue, OfflineSettings, SyncLog, CachedAsset


class OfflineProjectSerializer(serializers.ModelSerializer):
    """Serializer for offline projects"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    cache_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = OfflineProject
        fields = [
            'id', 'project', 'project_name', 'last_synced', 'sync_version',
            'cached_data', 'cached_assets', 'cache_size', 'cache_size_mb',
            'is_enabled', 'needs_sync', 'created_at'
        ]
        read_only_fields = ['last_synced', 'sync_version', 'cache_size', 'created_at']
    
    def get_cache_size_mb(self, obj) -> float:
        return round(obj.cache_size / (1024 * 1024), 2)


class SyncQueueSerializer(serializers.ModelSerializer):
    """Serializer for sync queue items"""
    operation_display = serializers.CharField(source='get_operation_display', read_only=True)
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SyncQueue
        fields = [
            'id', 'operation', 'operation_display', 'entity_type', 'entity_type_display',
            'entity_id', 'data', 'status', 'status_display', 'error_message',
            'retry_count', 'conflict_data', 'resolved_by', 'created_at', 'synced_at', 'sequence'
        ]
        read_only_fields = ['created_at', 'synced_at']


class SyncQueueCreateSerializer(serializers.Serializer):
    """Serializer for creating sync queue items"""
    operation = serializers.ChoiceField(choices=SyncQueue.OPERATION_TYPES)
    entity_type = serializers.ChoiceField(choices=SyncQueue.ENTITY_TYPES)
    entity_id = serializers.CharField()
    data = serializers.JSONField()
    sequence = serializers.IntegerField(default=0)


class OfflineSettingsSerializer(serializers.ModelSerializer):
    """Serializer for offline settings"""
    max_storage_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = OfflineSettings
        fields = [
            'id', 'max_offline_storage', 'max_storage_mb', 'auto_cache_recent',
            'recent_project_count', 'auto_sync_on_connect', 'sync_interval_minutes',
            'background_sync_enabled', 'cache_images', 'cache_fonts', 'cache_videos',
            'default_conflict_resolution', 'updated_at'
        ]
        read_only_fields = ['updated_at']
    
    def get_max_storage_mb(self, obj) -> float:
        return round(obj.max_offline_storage / (1024 * 1024), 2)


class SyncLogSerializer(serializers.ModelSerializer):
    """Serializer for sync logs"""
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncLog
        fields = [
            'id', 'started_at', 'completed_at', 'duration_seconds',
            'items_synced', 'items_failed', 'conflicts_resolved',
            'bytes_uploaded', 'bytes_downloaded', 'success', 'error_message'
        ]
        read_only_fields = ['started_at', 'completed_at']
    
    def get_duration_seconds(self, obj) -> float:
        if obj.completed_at and obj.started_at:
            return (obj.completed_at - obj.started_at).total_seconds()
        return 0


class CachedAssetSerializer(serializers.ModelSerializer):
    """Serializer for cached assets"""
    file_size_kb = serializers.SerializerMethodField()
    
    class Meta:
        model = CachedAsset
        fields = [
            'id', 'original_url', 'asset_type', 'cache_key', 'file_size',
            'file_size_kb', 'mime_type', 'last_accessed', 'access_count',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['cache_key', 'created_at', 'last_accessed']
    
    def get_file_size_kb(self, obj) -> float:
        return round(obj.file_size / 1024, 2)


class SyncDataSerializer(serializers.Serializer):
    """Serializer for sync data package"""
    projects = serializers.ListField(child=serializers.DictField())
    components = serializers.ListField(child=serializers.DictField())
    assets = serializers.ListField(child=serializers.DictField())
    last_sync = serializers.DateTimeField()
    version = serializers.IntegerField()


class BulkSyncSerializer(serializers.Serializer):
    """Serializer for bulk sync operations"""
    items = SyncQueueCreateSerializer(many=True)


class ConflictResolutionSerializer(serializers.Serializer):
    """Serializer for conflict resolution"""
    queue_id = serializers.IntegerField()
    resolution = serializers.ChoiceField(choices=['local', 'remote', 'merged'])
    merged_data = serializers.JSONField(required=False)


class OfflineStatusSerializer(serializers.Serializer):
    """Serializer for offline status response"""
    is_online = serializers.BooleanField()
    pending_syncs = serializers.IntegerField()
    total_cache_size = serializers.IntegerField()
    projects_cached = serializers.IntegerField()
    last_sync = serializers.DateTimeField(allow_null=True)

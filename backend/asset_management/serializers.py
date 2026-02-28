from typing import List, Dict
from rest_framework import serializers
from .models import (
    AssetFolder, AssetTag, EnhancedAsset, AssetCollection,
    AssetUsageLog, CDNIntegration, BulkOperation, UnusedAssetReport
)


class AssetFolderSerializer(serializers.ModelSerializer):
    """Serializer for asset folders"""
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetFolder
        fields = [
            'id', 'name', 'description', 'parent', 'path', 'color', 'icon',
            'is_smart', 'smart_rules', 'asset_count', 'total_size',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['path', 'asset_count', 'total_size', 'created_at', 'updated_at']
    
    def get_children_count(self, obj) -> int:
        return obj.children.count()


class AssetTagSerializer(serializers.ModelSerializer):
    """Serializer for asset tags"""
    asset_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetTag
        fields = ['id', 'name', 'color', 'ai_generated', 'asset_count', 'created_at']
        read_only_fields = ['created_at']
    
    def get_asset_count(self, obj) -> int:
        return obj.assets.count()


class EnhancedAssetSerializer(serializers.ModelSerializer):
    """Serializer for enhanced assets"""
    folder_name = serializers.CharField(source='folder.name', read_only=True)
    tag_names = serializers.SerializerMethodField()
    file_size_human = serializers.SerializerMethodField()
    
    class Meta:
        model = EnhancedAsset
        fields = [
            'id', 'name', 'description', 'asset_type', 'file_url', 'thumbnail_url',
            'original_filename', 'file_size', 'file_size_human', 'mime_type',
            'width', 'height', 'duration', 'folder', 'folder_name', 'tags', 'tag_names',
            'ai_tags', 'ai_description', 'ai_colors', 'ai_objects', 'ai_text',
            'cdn_url', 'usage_count', 'last_used', 'version', 'is_favorite',
            'is_archived', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'file_size', 'mime_type', 'ai_tags', 'ai_description', 'ai_colors',
            'ai_objects', 'ai_text', 'usage_count', 'last_used', 'version',
            'created_at', 'updated_at'
        ]
    
    def get_tag_names(self, obj) -> List[str]:
        return list(obj.tags.values_list('name', flat=True))
    
    def get_file_size_human(self, obj) -> str:
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class EnhancedAssetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enhanced assets"""
    
    class Meta:
        model = EnhancedAsset
        fields = [
            'name', 'description', 'asset_type', 'file_url', 'thumbnail_url',
            'original_filename', 'file_size', 'mime_type', 'width', 'height',
            'duration', 'folder', 'tags'
        ]


class AssetCollectionSerializer(serializers.ModelSerializer):
    """Serializer for asset collections"""
    asset_count = serializers.SerializerMethodField()
    assets_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = AssetCollection
        fields = [
            'id', 'name', 'description', 'cover_image', 'color',
            'is_public', 'asset_count', 'assets_preview', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_asset_count(self, obj) -> int:
        return obj.assets.count()
    
    def get_assets_preview(self, obj) -> List[Dict]:
        return list(obj.assets.values('id', 'thumbnail_url', 'name')[:4])


class AssetUsageLogSerializer(serializers.ModelSerializer):
    """Serializer for asset usage logs"""
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = AssetUsageLog
        fields = [
            'id', 'asset', 'asset_name', 'project', 'project_name',
            'component_id', 'usage_type', 'added_at', 'removed_at'
        ]
        read_only_fields = ['added_at']


class CDNIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for CDN integrations"""
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = CDNIntegration
        fields = [
            'id', 'provider', 'provider_display', 'name', 'cloud_name',
            'default_transformations', 'auto_optimize', 'is_active',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
        }


class BulkOperationSerializer(serializers.ModelSerializer):
    """Serializer for bulk operations"""
    operation_display = serializers.CharField(source='get_operation_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = BulkOperation
        fields = [
            'id', 'operation', 'operation_display', 'status', 'status_display',
            'total_assets', 'processed_assets', 'progress', 'parameters',
            'results', 'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'processed_assets', 'results', 'error_message', 'created_at', 'completed_at'
        ]
    
    def get_progress(self, obj) -> float:
        if obj.total_assets == 0:
            return 0
        return round((obj.processed_assets / obj.total_assets) * 100, 1)


class UnusedAssetReportSerializer(serializers.ModelSerializer):
    """Serializer for unused asset reports"""
    size_human = serializers.SerializerMethodField()
    
    class Meta:
        model = UnusedAssetReport
        fields = [
            'id', 'total_unused', 'total_size', 'size_human',
            'unused_days_threshold', 'generated_at'
        ]
    
    def get_size_human(self, obj) -> str:
        size = obj.total_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class AssetSearchSerializer(serializers.Serializer):
    """Serializer for asset search"""
    query = serializers.CharField(required=False, allow_blank=True)
    asset_type = serializers.CharField(required=False)
    folder_id = serializers.IntegerField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    color = serializers.CharField(required=False)
    min_width = serializers.IntegerField(required=False)
    max_size = serializers.IntegerField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    is_favorite = serializers.BooleanField(required=False)
    unused = serializers.BooleanField(required=False)
    ai_search = serializers.BooleanField(default=False)


class BulkOperationRequestSerializer(serializers.Serializer):
    """Serializer for bulk operation requests"""
    operation = serializers.ChoiceField(choices=BulkOperation.OPERATION_TYPES)
    asset_ids = serializers.ListField(child=serializers.IntegerField())
    parameters = serializers.DictField(required=False, default=dict)

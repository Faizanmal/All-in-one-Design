"""
Integration Serializers
"""
from rest_framework import serializers
from .models import ExternalServiceConnection, ImportedAsset, FigmaImport, StockAssetSearch


class ExternalServiceConnectionSerializer(serializers.ModelSerializer):
    """Serializer for external service connections"""
    service_display = serializers.CharField(source='get_service_display', read_only=True)
    
    class Meta:
        model = ExternalServiceConnection
        fields = [
            'id', 'service', 'service_display', 'service_username',
            'is_active', 'last_synced', 'created_at', 'updated_at'
        ]
        read_only_fields = ['service_username', 'last_synced', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ImportedAssetSerializer(serializers.ModelSerializer):
    """Serializer for imported assets"""
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    asset_type_display = serializers.CharField(source='get_asset_type_display', read_only=True)
    
    class Meta:
        model = ImportedAsset
        fields = [
            'id', 'source', 'source_display', 'asset_type', 'asset_type_display',
            'external_id', 'external_url', 'name', 'description',
            'file', 'thumbnail', 'metadata', 'attribution_required',
            'attribution_text', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class FigmaImportSerializer(serializers.ModelSerializer):
    """Serializer for Figma imports"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_project_name = serializers.CharField(source='result_project.name', read_only=True)
    
    class Meta:
        model = FigmaImport
        fields = [
            'id', 'figma_file_key', 'figma_file_name', 'figma_node_ids',
            'import_images', 'import_vectors', 'import_styles', 'import_components',
            'status', 'status_display', 'result_project', 'result_project_name',
            'error_message', 'total_nodes', 'imported_nodes',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'result_project', 'error_message',
            'total_nodes', 'imported_nodes', 'created_at', 'completed_at'
        ]


class StockAssetSearchSerializer(serializers.ModelSerializer):
    """Serializer for stock asset search history"""
    
    class Meta:
        model = StockAssetSearch
        fields = [
            'id', 'provider', 'query', 'filters',
            'results_count', 'selected_asset_id', 'created_at'
        ]
        read_only_fields = ['created_at']


class StockAssetResultSerializer(serializers.Serializer):
    """Serializer for stock asset search results"""
    id = serializers.CharField()
    provider = serializers.CharField()
    url = serializers.URLField()
    thumbnail_url = serializers.URLField()
    preview_url = serializers.URLField()
    download_url = serializers.URLField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    description = serializers.CharField(allow_blank=True)
    photographer = serializers.CharField()
    photographer_url = serializers.URLField()
    attribution = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    color = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)

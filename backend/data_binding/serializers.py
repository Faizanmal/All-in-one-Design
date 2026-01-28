"""
Data Binding Serializers
"""

from rest_framework import serializers
from .models import (
    DataSource, DataVariable, DataBinding, DataCollection,
    RepeatingElement, DataTransform, DataSyncLog
)


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'source_type', 'url', 'file',
            'auth_type', 'auth_config', 'method', 'headers',
            'query_params', 'body_template', 'data_path', 'schema',
            'cache_duration', 'last_fetched', 'is_active', 'last_error',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_fetched', 'last_error', 'created_at', 'updated_at']
        extra_kwargs = {
            'auth_config': {'write_only': True}  # Don't expose credentials
        }
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DataSourceListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'source_type', 'is_active', 'last_fetched', 'created_at']


class DataVariableSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    
    class Meta:
        model = DataVariable
        fields = [
            'id', 'project', 'data_source', 'data_source_name',
            'name', 'variable_type', 'field_path',
            'default_value', 'transform', 'format_string',
            'current_value', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_value', 'created_at', 'updated_at']


class DataBindingSerializer(serializers.ModelSerializer):
    variable_name = serializers.CharField(source='variable.name', read_only=True)
    
    class Meta:
        model = DataBinding
        fields = [
            'id', 'project', 'variable', 'variable_name',
            'element_id', 'element_name', 'binding_type', 'property_name',
            'condition', 'true_value', 'false_value', 'template',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DataCollectionSerializer(serializers.ModelSerializer):
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    
    class Meta:
        model = DataCollection
        fields = [
            'id', 'project', 'data_source', 'data_source_name',
            'name', 'filter_expression', 'sort_field', 'sort_direction',
            'page_size', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RepeatingElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepeatingElement
        fields = [
            'id', 'project', 'collection', 'element_id',
            'template_element', 'direction', 'gap', 'columns',
            'alternate_styles', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DataTransformSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTransform
        fields = ['id', 'name', 'transform_type', 'config', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DataSyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSyncLog
        fields = ['id', 'data_source', 'status', 'records_fetched', 'duration_ms', 'error_message', 'created_at']


# Request Serializers

class FetchDataRequestSerializer(serializers.Serializer):
    data_source_id = serializers.UUIDField()
    force_refresh = serializers.BooleanField(default=False)


class TestConnectionSerializer(serializers.Serializer):
    source_type = serializers.ChoiceField(choices=[
        'csv', 'json', 'rest_api', 'graphql', 'google_sheets', 'airtable'
    ])
    url = serializers.URLField(required=False)
    auth_type = serializers.ChoiceField(choices=['none', 'api_key', 'bearer', 'basic'], default='none')
    auth_config = serializers.JSONField(default=dict)
    headers = serializers.JSONField(default=dict)
    method = serializers.CharField(default='GET')


class BindElementsRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    bindings = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )


class PreviewBindingSerializer(serializers.Serializer):
    variable_id = serializers.UUIDField()
    element_id = serializers.CharField()
    binding_type = serializers.CharField()
    row_index = serializers.IntegerField(default=0)


class TransformPreviewSerializer(serializers.Serializer):
    value = serializers.CharField()
    transform_type = serializers.CharField()
    config = serializers.JSONField(default=dict)

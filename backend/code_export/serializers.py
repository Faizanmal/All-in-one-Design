from rest_framework import serializers
from .models import (
    ExportConfiguration, CodeExport, DesignSpec,
    ComponentLibrary, HandoffAnnotation
)


class ExportConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for export configuration"""
    framework_display = serializers.CharField(source='get_framework_display', read_only=True)
    styling_display = serializers.CharField(source='get_styling_display', read_only=True)
    
    class Meta:
        model = ExportConfiguration
        fields = [
            'id', 'name', 'description', 'framework', 'framework_display',
            'styling', 'styling_display', 'typescript_enabled', 'component_naming',
            'use_absolute_imports', 'generate_tests', 'generate_storybook',
            'breakpoints', 'generate_responsive', 'custom_config', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CodeExportSerializer(serializers.ModelSerializer):
    """Serializer for code export records"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    config_name = serializers.CharField(source='config.name', read_only=True)
    
    class Meta:
        model = CodeExport
        fields = [
            'id', 'project', 'project_name', 'config', 'config_name',
            'framework', 'styling', 'generated_code', 'preview_url',
            'download_url', 'status', 'status_display', 'error_message',
            'file_count', 'total_lines', 'export_size', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'generated_code', 'preview_url', 'download_url', 'status',
            'error_message', 'file_count', 'total_lines', 'export_size',
            'created_at', 'completed_at'
        ]


class CodeExportCreateSerializer(serializers.Serializer):
    """Serializer for creating a new code export"""
    project_id = serializers.IntegerField()
    config_id = serializers.IntegerField(required=False)
    framework = serializers.ChoiceField(
        choices=ExportConfiguration.FRAMEWORK_CHOICES,
        default='react'
    )
    styling = serializers.ChoiceField(
        choices=ExportConfiguration.STYLING_CHOICES,
        default='tailwind'
    )
    typescript_enabled = serializers.BooleanField(default=True)
    component_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Specific component IDs to export. Leave empty for all."
    )


class DesignSpecSerializer(serializers.ModelSerializer):
    """Serializer for design specifications"""
    component_type = serializers.CharField(source='component.component_type', read_only=True)
    
    class Meta:
        model = DesignSpec
        fields = [
            'id', 'project', 'component', 'component_type', 'name', 'description',
            'dimensions', 'colors', 'typography', 'spacing', 'effects',
            'computed_styles', 'assets', 'notes', 'implementation_hints',
            'auto_generated', 'version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ComponentLibrarySerializer(serializers.ModelSerializer):
    """Serializer for component libraries"""
    component_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ComponentLibrary
        fields = [
            'id', 'name', 'description', 'version', 'components',
            'component_count', 'default_framework', 'default_styling',
            'package_name', 'package_registry', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_component_count(self, obj) -> int:
        return len(obj.components) if obj.components else 0


class HandoffAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for handoff annotations"""
    annotation_type_display = serializers.CharField(source='get_annotation_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = HandoffAnnotation
        fields = [
            'id', 'project', 'component', 'annotation_type', 'annotation_type_display',
            'position_x', 'position_y', 'title', 'content', 'color',
            'created_by', 'created_by_name', 'resolved', 'resolved_by',
            'resolved_by_name', 'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'resolved_by', 'resolved_at', 'created_at', 'updated_at']


class GeneratedCodeSerializer(serializers.Serializer):
    """Serializer for generated code response"""
    files = serializers.DictField(child=serializers.CharField())
    file_count = serializers.IntegerField()
    total_lines = serializers.IntegerField()
    total_size = serializers.IntegerField()
    download_url = serializers.URLField(required=False)


class DesignSpecsExportSerializer(serializers.Serializer):
    """Serializer for design specs export"""
    specs = serializers.ListField(child=serializers.DictField())
    css = serializers.CharField()
    tokens = serializers.DictField()


class BulkExportSerializer(serializers.Serializer):
    """Serializer for bulk export operations"""
    project_ids = serializers.ListField(child=serializers.IntegerField())
    framework = serializers.ChoiceField(
        choices=ExportConfiguration.FRAMEWORK_CHOICES,
        default='react'
    )
    styling = serializers.ChoiceField(
        choices=ExportConfiguration.STYLING_CHOICES,
        default='tailwind'
    )
    include_specs = serializers.BooleanField(default=True)
    include_assets = serializers.BooleanField(default=True)

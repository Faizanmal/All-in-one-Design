"""
Developer Handoff Serializers
"""
from rest_framework import serializers
from .developer_handoff_models import (
    CodeExport,
    DesignSystem,
    DesignSystemExport,
    ComponentSpec,
    HandoffAnnotation
)


class CodeExportSerializer(serializers.ModelSerializer):
    """Serializer for code exports"""
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = CodeExport
        fields = [
            'id', 'project', 'project_name', 'format', 'format_display',
            'options', 'status', 'status_display',
            'output_files', 'error_message',
            'lines_of_code', 'components_generated',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'output_files', 'error_message',
            'lines_of_code', 'components_generated',
            'created_at', 'completed_at'
        ]


class DesignSystemSerializer(serializers.ModelSerializer):
    """Serializer for design systems"""
    source_project_ids = serializers.PrimaryKeyRelatedField(
        source='source_projects',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = DesignSystem
        fields = [
            'id', 'name', 'description', 'version',
            'colors', 'typography', 'spacing', 'radii', 'shadows', 'breakpoints',
            'component_variants', 'source_project_ids',
            'is_public', 'is_template',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DesignSystemExportSerializer(serializers.ModelSerializer):
    """Serializer for design system exports"""
    format_display = serializers.CharField(source='get_format_display', read_only=True)
    design_system_name = serializers.CharField(source='design_system.name', read_only=True)
    
    class Meta:
        model = DesignSystemExport
        fields = [
            'id', 'design_system', 'design_system_name',
            'format', 'format_display', 'output_content',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ComponentSpecSerializer(serializers.ModelSerializer):
    """Serializer for component specifications"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ComponentSpec
        fields = [
            'id', 'project', 'project_name', 'element_id',
            'name', 'description',
            'dimensions', 'styles', 'responsive_variants',
            'states', 'props', 'assets', 'code_snippets',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class HandoffAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for handoff annotations"""
    annotation_type_display = serializers.CharField(source='get_annotation_type_display', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True)
    
    class Meta:
        model = HandoffAnnotation
        fields = [
            'id', 'project', 'user', 'user_username',
            'annotation_type', 'annotation_type_display',
            'position_x', 'position_y', 'target_element_id',
            'title', 'content',
            'is_resolved', 'resolved_by', 'resolved_by_username', 'resolved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'is_resolved', 'resolved_by', 'resolved_at',
            'created_at', 'updated_at'
        ]

from rest_framework import serializers
from .models import (
    DesignSystem, DesignToken, ComponentDefinition, ComponentVariant,
    StyleGuide, DocumentationPage, DesignSystemExport, DesignSystemSync
)
from typing import List, Dict


class DesignTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignToken
        fields = [
            'id', 'name', 'category', 'token_type', 'value',
            'reference', 'description', 'usage_guidelines',
            'group', 'order', 'is_deprecated', 'deprecated_message', 'replacement',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ComponentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentVariant
        fields = [
            'id', 'name', 'description', 'props', 'tokens',
            'preview_image', 'code_example', 'order'
        ]
        read_only_fields = ['id']


class ComponentDefinitionSerializer(serializers.ModelSerializer):
    variant_instances = ComponentVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = ComponentDefinition
        fields = [
            'id', 'design_system', 'name', 'description', 'category', 'status',
            'preview_image', 'figma_node_id', 'storybook_path',
            'variants', 'props', 'slots',
            'html_template', 'react_template', 'vue_template', 'angular_template',
            'specs', 'anatomy', 'usage_guidelines', 'dos', 'donts',
            'accessibility_guidelines', 'aria_attributes',
            'related_components', 'tags', 'version', 'variant_instances',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StyleGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleGuide
        fields = [
            'id', 'brand_overview', 'brand_values', 'tone_of_voice',
            'logo_guidelines', 'logo_variations', 'logo_clearspace', 'logo_misuse',
            'color_guidelines', 'color_accessibility',
            'typography_guidelines', 'typography_scale',
            'imagery_guidelines', 'photography_style', 'illustration_style', 'iconography_guidelines',
            'layout_guidelines', 'grid_system', 'spacing_guidelines',
            'motion_guidelines', 'animation_principles',
            'custom_sections', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DocumentationPageSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentationPage
        fields = [
            'id', 'title', 'slug', 'content', 'parent', 'order',
            'is_published', 'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj) -> List[Dict]:
        children = obj.children.filter(is_published=True)
        return DocumentationPageSerializer(children, many=True).data


class DesignSystemListSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    token_count = serializers.SerializerMethodField()
    component_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignSystem
        fields = [
            'id', 'user', 'team', 'name', 'description', 'version',
            'logo', 'is_public', 'token_count', 'component_count',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_token_count(self, obj) -> int:
        return obj.tokens.count()
    
    def get_component_count(self, obj) -> int:
        return obj.components.count()


class DesignSystemDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    tokens = DesignTokenSerializer(many=True, read_only=True)
    components = ComponentDefinitionSerializer(many=True, read_only=True)
    style_guide = StyleGuideSerializer(read_only=True)
    documentation_pages = DocumentationPageSerializer(many=True, read_only=True)
    
    class Meta:
        model = DesignSystem
        fields = [
            'id', 'user', 'team', 'name', 'description', 'version',
            'logo', 'favicon', 'is_public', 'auto_sync',
            'figma_file_key', 'storybook_url',
            'tokens', 'components', 'style_guide', 'documentation_pages',
            'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DesignSystemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystem
        fields = ['name', 'description', 'team', 'is_public', 'tags']


class DesignSystemExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystemExport
        fields = [
            'id', 'design_system', 'export_format', 'options',
            'status', 'output_file', 'output_url', 'error_message',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'output_file', 'output_url', 
                          'error_message', 'created_at', 'completed_at']


class DesignSystemSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystemSync
        fields = [
            'id', 'design_system', 'source', 'direction',
            'status', 'changes_summary', 'error_message',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'changes_summary', 'error_message',
                          'started_at', 'completed_at']


class TokenExportSerializer(serializers.Serializer):
    """Serializer for token export options"""
    format = serializers.ChoiceField(choices=['css', 'scss', 'json', 'js', 'ios', 'android'])
    categories = serializers.ListField(child=serializers.CharField(), required=False)
    prefix = serializers.CharField(default='', required=False)
    include_deprecated = serializers.BooleanField(default=False)

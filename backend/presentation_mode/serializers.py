"""
Serializers for Presentation Mode app.
"""
from rest_framework import serializers
from .models import (
    Presentation, PresentationSlide, SlideAnnotation, PresentationViewer,
    DevModeProject, DevModeInspection, CodeExportConfig, CodeExportHistory,
    MeasurementOverlay, AssetExportQueue
)


class SlideAnnotationSerializer(serializers.ModelSerializer):
    """Serializer for slide annotations."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = SlideAnnotation
        fields = [
            'id', 'slide', 'annotation_type', 'content', 'position_x',
            'position_y', 'width', 'height', 'style', 'is_visible',
            'show_on_hover', 'order', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class PresentationSlideSerializer(serializers.ModelSerializer):
    """Serializer for presentation slides."""
    annotations = SlideAnnotationSerializer(many=True, read_only=True)
    annotation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PresentationSlide
        fields = [
            'id', 'presentation', 'frame_id', 'title', 'notes',
            'transition', 'transition_duration', 'auto_advance',
            'advance_delay', 'background_override', 'order',
            'is_hidden', 'created_at', 'updated_at', 'annotations',
            'annotation_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_annotation_count(self, obj):
        return obj.annotations.filter(is_visible=True).count()


class PresentationSlideListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for slide lists."""
    
    class Meta:
        model = PresentationSlide
        fields = [
            'id', 'frame_id', 'title', 'order', 'is_hidden',
            'transition', 'auto_advance'
        ]


class PresentationViewerSerializer(serializers.ModelSerializer):
    """Serializer for presentation viewers."""
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = PresentationViewer
        fields = [
            'id', 'presentation', 'user', 'user_name', 'session_id',
            'current_slide', 'is_presenter', 'can_control', 'joined_at',
            'last_activity', 'left_at'
        ]
        read_only_fields = ['id', 'joined_at', 'last_activity']


class PresentationSerializer(serializers.ModelSerializer):
    """Serializer for presentations."""
    slides = PresentationSlideListSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    slide_count = serializers.SerializerMethodField()
    viewer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Presentation
        fields = [
            'id', 'project', 'name', 'description', 'default_transition',
            'default_transition_duration', 'show_navigation', 'show_progress',
            'loop', 'auto_play', 'auto_play_interval', 'background_color',
            'cursor_style', 'hotspot_style', 'share_link', 'share_password',
            'is_public', 'allow_comments', 'show_presenter_notes', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'slides', 'slide_count', 'viewer_count'
        ]
        read_only_fields = ['id', 'share_link', 'created_by', 'created_at', 'updated_at']
    
    def get_slide_count(self, obj):
        return obj.slides.filter(is_hidden=False).count()
    
    def get_viewer_count(self, obj):
        return obj.viewers.filter(left_at__isnull=True).count()


class PresentationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for presentation lists."""
    slide_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Presentation
        fields = [
            'id', 'name', 'description', 'is_public', 'is_active',
            'slide_count', 'updated_at'
        ]
    
    def get_slide_count(self, obj):
        return obj.slides.filter(is_hidden=False).count()


class DevModeInspectionSerializer(serializers.ModelSerializer):
    """Serializer for dev mode inspections."""
    inspected_by_name = serializers.CharField(source='inspected_by.username', read_only=True)
    
    class Meta:
        model = DevModeInspection
        fields = [
            'id', 'dev_mode_project', 'node_id', 'node_type', 'node_name',
            'css_code', 'tailwind_code', 'react_code', 'vue_code',
            'flutter_code', 'swift_code', 'properties', 'computed_styles',
            'inspected_by', 'inspected_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'css_code', 'tailwind_code', 'react_code', 'vue_code', 'flutter_code', 'swift_code', 'properties', 'computed_styles', 'inspected_by', 'created_at']


class CodeExportConfigSerializer(serializers.ModelSerializer):
    """Serializer for code export configuration."""
    
    class Meta:
        model = CodeExportConfig
        fields = [
            'id', 'dev_mode_project', 'name', 'format', 'framework',
            'css_unit', 'color_format', 'include_comments', 'include_variables',
            'use_design_tokens', 'naming_convention', 'indentation',
            'quote_style', 'custom_mappings', 'is_default', 'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CodeExportHistorySerializer(serializers.ModelSerializer):
    """Serializer for code export history."""
    config_name = serializers.CharField(source='config.name', read_only=True)
    exported_by_name = serializers.CharField(source='exported_by.username', read_only=True)
    
    class Meta:
        model = CodeExportHistory
        fields = [
            'id', 'config', 'config_name', 'node_ids', 'export_format',
            'generated_code', 'file_url', 'exported_by', 'exported_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'generated_code', 'file_url', 'exported_by', 'created_at']


class MeasurementOverlaySerializer(serializers.ModelSerializer):
    """Serializer for measurement overlays."""
    
    class Meta:
        model = MeasurementOverlay
        fields = [
            'id', 'dev_mode_project', 'from_node_id', 'to_node_id',
            'measurement_type', 'value', 'unit', 'is_pinned',
            'color', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AssetExportQueueSerializer(serializers.ModelSerializer):
    """Serializer for asset export queue."""
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    
    class Meta:
        model = AssetExportQueue
        fields = [
            'id', 'dev_mode_project', 'node_id', 'node_name', 'format',
            'scale', 'suffix', 'status', 'file_url', 'file_size',
            'error_message', 'requested_by', 'requested_by_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'file_url', 'file_size', 'error_message', 'requested_by', 'created_at', 'completed_at']


class DevModeProjectSerializer(serializers.ModelSerializer):
    """Serializer for dev mode projects."""
    configs = CodeExportConfigSerializer(many=True, read_only=True)
    recent_inspections = serializers.SerializerMethodField()
    
    class Meta:
        model = DevModeProject
        fields = [
            'id', 'project', 'is_enabled', 'default_css_unit',
            'default_color_format', 'show_grid', 'grid_size', 'grid_color',
            'show_guides', 'show_spacing', 'show_properties', 'show_code',
            'preferred_framework', 'created_at', 'updated_at', 'configs',
            'recent_inspections'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recent_inspections(self, obj):
        inspections = obj.inspections.order_by('-created_at')[:5]
        return DevModeInspectionSerializer(inspections, many=True).data


class InspectNodeSerializer(serializers.Serializer):
    """Serializer for node inspection request."""
    node_id = serializers.CharField()
    include_children = serializers.BooleanField(default=False)
    formats = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['css', 'tailwind', 'react', 'vue', 'flutter', 'swift']
        ),
        default=['css', 'tailwind']
    )


class ExportCodeSerializer(serializers.Serializer):
    """Serializer for code export request."""
    node_ids = serializers.ListField(child=serializers.CharField())
    config_id = serializers.UUIDField(required=False)
    format = serializers.ChoiceField(
        choices=['css', 'scss', 'tailwind', 'styled-components', 'react', 'vue', 'flutter', 'swift'],
        default='css'
    )


class ExportAssetSerializer(serializers.Serializer):
    """Serializer for asset export request."""
    node_ids = serializers.ListField(child=serializers.CharField())
    format = serializers.ChoiceField(
        choices=['png', 'jpg', 'svg', 'pdf', 'webp'],
        default='png'
    )
    scales = serializers.ListField(
        child=serializers.FloatField(),
        default=[1.0, 2.0]
    )


class StartPresentationSerializer(serializers.Serializer):
    """Serializer for starting a presentation."""
    start_slide = serializers.IntegerField(default=0)
    presenter_mode = serializers.BooleanField(default=False)


class SharePresentationSerializer(serializers.Serializer):
    """Serializer for sharing a presentation."""
    is_public = serializers.BooleanField(default=True)
    password = serializers.CharField(required=False, allow_blank=True)
    allow_comments = serializers.BooleanField(default=False)

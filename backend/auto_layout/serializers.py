"""
Auto-Layout System Serializers
"""
from rest_framework import serializers
from .models import (
    AutoLayoutFrame, AutoLayoutChild, LayoutConstraint,
    ResponsiveBreakpoint, ResponsiveOverride, LayoutPreset
)


class AutoLayoutChildSerializer(serializers.ModelSerializer):
    """Serializer for auto-layout children."""
    
    class Meta:
        model = AutoLayoutChild
        fields = [
            'id', 'parent_frame', 'component', 'order',
            'horizontal_sizing', 'vertical_sizing',
            'fixed_width', 'fixed_height', 'fill_ratio',
            'min_width', 'max_width', 'min_height', 'max_height',
            'align_self', 'flex_grow', 'flex_shrink',
            'is_absolute', 'absolute_x', 'absolute_y', 'absolute_anchor',
            'visible', 'rotation',
            'computed_x', 'computed_y', 'computed_width', 'computed_height',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AutoLayoutFrameSerializer(serializers.ModelSerializer):
    """Serializer for auto-layout frames."""
    
    children = AutoLayoutChildSerializer(many=True, read_only=True)
    padding = serializers.SerializerMethodField()
    corner_radii = serializers.SerializerMethodField()
    
    class Meta:
        model = AutoLayoutFrame
        fields = [
            'id', 'project', 'component', 'name', 'enabled',
            'direction', 'primary_axis_alignment', 'cross_axis_alignment',
            'item_spacing',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left', 'padding',
            'horizontal_sizing', 'vertical_sizing',
            'min_width', 'max_width', 'min_height', 'max_height',
            'width', 'height',
            'overflow_horizontal', 'overflow_vertical',
            'stroke_included_in_layout',
            'corner_radius', 'corner_radius_top_left', 'corner_radius_top_right',
            'corner_radius_bottom_right', 'corner_radius_bottom_left', 'corner_radii',
            'background_color', 'background_opacity', 'clip_content',
            'z_index', 'parent_frame',
            'absolute_position', 'absolute_x', 'absolute_y',
            'position_x', 'position_y',
            'children', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'children', 'padding', 'corner_radii']
    
    def get_padding(self, obj):
        return obj.get_computed_padding()
    
    def get_corner_radii(self, obj):
        return obj.get_corner_radii()


class LayoutConstraintSerializer(serializers.ModelSerializer):
    """Serializer for layout constraints."""
    
    class Meta:
        model = LayoutConstraint
        fields = [
            'id', 'component',
            'horizontal', 'vertical',
            'margin_left', 'margin_right', 'margin_top', 'margin_bottom',
            'percent_x', 'percent_y', 'percent_width', 'percent_height',
            'lock_aspect_ratio', 'aspect_ratio',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResponsiveBreakpointSerializer(serializers.ModelSerializer):
    """Serializer for responsive breakpoints."""
    
    class Meta:
        model = ResponsiveBreakpoint
        fields = [
            'id', 'project', 'name', 'device_type',
            'min_width', 'max_width',
            'canvas_width', 'canvas_height', 'scale',
            'priority', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResponsiveOverrideSerializer(serializers.ModelSerializer):
    """Serializer for responsive overrides."""
    
    class Meta:
        model = ResponsiveOverride
        fields = [
            'id', 'frame', 'breakpoint',
            'direction', 'item_spacing',
            'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
            'primary_axis_alignment', 'cross_axis_alignment',
            'horizontal_sizing', 'vertical_sizing',
            'width', 'height', 'visible',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LayoutPresetSerializer(serializers.ModelSerializer):
    """Serializer for layout presets."""
    
    class Meta:
        model = LayoutPreset
        fields = [
            'id', 'user', 'name', 'description', 'category',
            'config', 'thumbnail',
            'is_public', 'is_system', 'use_count', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'use_count', 'created_at', 'updated_at']


class ApplyPresetSerializer(serializers.Serializer):
    """Serializer for applying a preset to a frame."""
    preset_id = serializers.UUIDField()
    frame_id = serializers.UUIDField()


class ComputeLayoutSerializer(serializers.Serializer):
    """Serializer for computing layout request."""
    frame_id = serializers.UUIDField()
    viewport_width = serializers.IntegerField(required=False)
    viewport_height = serializers.IntegerField(required=False)

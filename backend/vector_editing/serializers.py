"""
Vector Editing Serializers

REST API serializers for vector editing models.
"""

from rest_framework import serializers
from .models import (
    VectorPath, PathPoint, BooleanOperation, PathOffset,
    VectorPattern, VectorShape, PenToolSession
)


class PathPointSerializer(serializers.ModelSerializer):
    """Serializer for individual path points."""
    
    class Meta:
        model = PathPoint
        fields = [
            'id', 'x', 'y',
            'handle_in_x', 'handle_in_y',
            'handle_out_x', 'handle_out_y',
            'point_type', 'corner_radius',
            'order', 'is_selected'
        ]
        read_only_fields = ['id']


class VectorPathSerializer(serializers.ModelSerializer):
    """Serializer for vector paths."""
    
    points = PathPointSerializer(many=True, read_only=True)
    svg_element = serializers.SerializerMethodField()
    bounds = serializers.SerializerMethodField()
    path_length = serializers.SerializerMethodField()
    
    class Meta:
        model = VectorPath
        fields = [
            'id', 'project', 'name', 'path_type',
            'path_data', 'path_points', 'points',
            'fill_color', 'fill_opacity', 'fill_rule',
            'fill_gradient', 'fill_pattern',
            'stroke_color', 'stroke_width', 'stroke_opacity',
            'stroke_cap', 'stroke_join', 'stroke_miter_limit',
            'stroke_dash_array', 'stroke_dash_offset',
            'transform_matrix',
            'x', 'y', 'width', 'height',
            'z_index', 'is_visible', 'is_locked',
            'tags', 'svg_element', 'bounds', 'path_length',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'svg_element', 'bounds', 'path_length']
    
    def get_svg_element(self, obj):
        return obj.get_svg_element()
    
    def get_bounds(self, obj):
        from .services import VectorService
        return VectorService.get_path_bounds(obj.path_data)
    
    def get_path_length(self, obj):
        from .services import VectorService
        return VectorService.get_path_length(obj.path_data)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VectorPathCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating vector paths."""
    
    class Meta:
        model = VectorPath
        fields = [
            'project', 'name', 'path_type', 'path_data',
            'fill_color', 'fill_opacity',
            'stroke_color', 'stroke_width',
            'x', 'y', 'width', 'height'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VectorPathUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vector paths."""
    
    class Meta:
        model = VectorPath
        fields = [
            'name', 'path_type', 'path_data', 'path_points',
            'fill_color', 'fill_opacity', 'fill_rule',
            'fill_gradient', 'fill_pattern',
            'stroke_color', 'stroke_width', 'stroke_opacity',
            'stroke_cap', 'stroke_join', 'stroke_miter_limit',
            'stroke_dash_array', 'stroke_dash_offset',
            'transform_matrix',
            'x', 'y', 'width', 'height',
            'z_index', 'is_visible', 'is_locked', 'tags'
        ]


class BooleanOperationSerializer(serializers.ModelSerializer):
    """Serializer for boolean operations."""
    
    result_path_data = VectorPathSerializer(source='result_path', read_only=True)
    
    class Meta:
        model = BooleanOperation
        fields = [
            'id', 'operation_type', 'source_paths',
            'result_path', 'result_path_data',
            'original_state', 'created_at'
        ]
        read_only_fields = ['id', 'result_path', 'original_state', 'created_at']


class BooleanOperationRequestSerializer(serializers.Serializer):
    """Serializer for boolean operation requests."""
    
    OPERATION_CHOICES = [
        ('union', 'Union'),
        ('subtract', 'Subtract'),
        ('intersect', 'Intersect'),
        ('exclude', 'Exclude'),
        ('divide', 'Divide'),
        ('trim', 'Trim'),
        ('merge', 'Merge'),
    ]
    
    operation_type = serializers.ChoiceField(choices=OPERATION_CHOICES)
    path_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2,
        help_text='List of path UUIDs to operate on'
    )
    
    def validate_path_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("At least 2 paths are required")
        return value


class PathOffsetSerializer(serializers.ModelSerializer):
    """Serializer for path offset operations."""
    
    result_path_data = VectorPathSerializer(source='result_path', read_only=True)
    
    class Meta:
        model = PathOffset
        fields = [
            'id', 'source_path', 'offset_type',
            'offset_value', 'join_type', 'miter_limit',
            'result_path', 'result_path_data', 'created_at'
        ]
        read_only_fields = ['id', 'result_path', 'created_at']


class PathOffsetRequestSerializer(serializers.Serializer):
    """Serializer for path offset requests."""
    
    OFFSET_TYPES = [
        ('expand', 'Expand'),
        ('contract', 'Contract'),
        ('outline_stroke', 'Outline Stroke'),
    ]
    
    JOIN_TYPES = [
        ('miter', 'Miter'),
        ('round', 'Round'),
        ('bevel', 'Bevel'),
    ]
    
    path_id = serializers.UUIDField()
    offset_type = serializers.ChoiceField(choices=OFFSET_TYPES)
    offset_value = serializers.FloatField(min_value=0.1, max_value=1000)
    join_type = serializers.ChoiceField(choices=JOIN_TYPES, default='round')
    miter_limit = serializers.FloatField(default=4.0, min_value=1.0)


class VectorPatternSerializer(serializers.ModelSerializer):
    """Serializer for vector patterns."""
    
    class Meta:
        model = VectorPattern
        fields = [
            'id', 'name', 'pattern_type',
            'pattern_content', 'width', 'height',
            'pattern_transform', 'preview_url',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class VectorShapeSerializer(serializers.ModelSerializer):
    """Serializer for vector shapes."""
    
    path_data = serializers.SerializerMethodField()
    
    class Meta:
        model = VectorShape
        fields = [
            'id', 'project', 'name', 'shape_type',
            'parameters', 'x', 'y',
            'fill_color', 'stroke_color', 'stroke_width',
            'z_index', 'path_data',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'path_data']
    
    def get_path_data(self, obj):
        from .services import VectorService
        return VectorService.shape_to_path(obj)


class ShapeToPathSerializer(serializers.Serializer):
    """Serializer for converting shapes to editable paths."""
    
    shape_id = serializers.UUIDField()
    keep_original = serializers.BooleanField(default=False)


class PenToolSessionSerializer(serializers.ModelSerializer):
    """Serializer for pen tool sessions."""
    
    class Meta:
        model = PenToolSession
        fields = [
            'id', 'project', 'current_path',
            'is_active', 'is_closed',
            'tool_settings', 'temp_points',
            'started_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'started_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PenToolPointSerializer(serializers.Serializer):
    """Serializer for adding points in pen tool mode."""
    
    x = serializers.FloatField()
    y = serializers.FloatField()
    handle_in_x = serializers.FloatField(default=0)
    handle_in_y = serializers.FloatField(default=0)
    handle_out_x = serializers.FloatField(default=0)
    handle_out_y = serializers.FloatField(default=0)
    point_type = serializers.ChoiceField(
        choices=['corner', 'smooth', 'symmetric', 'disconnected'],
        default='corner'
    )
    corner_radius = serializers.FloatField(default=0, min_value=0)


class CornerRoundingSerializer(serializers.Serializer):
    """Serializer for corner rounding operations."""
    
    path_id = serializers.UUIDField()
    point_radii = serializers.ListField(
        child=serializers.FloatField(min_value=0),
        help_text='List of corner radii for each point'
    )


class PathSimplifySerializer(serializers.Serializer):
    """Serializer for path simplification."""
    
    path_id = serializers.UUIDField()
    tolerance = serializers.FloatField(default=1.0, min_value=0.1, max_value=100)


class PathTransformSerializer(serializers.Serializer):
    """Serializer for path transformations."""
    
    path_ids = serializers.ListField(child=serializers.UUIDField())
    transform_type = serializers.ChoiceField(choices=[
        ('translate', 'Translate'),
        ('rotate', 'Rotate'),
        ('scale', 'Scale'),
        ('skew', 'Skew'),
        ('flip_horizontal', 'Flip Horizontal'),
        ('flip_vertical', 'Flip Vertical'),
    ])
    values = serializers.DictField(help_text='Transform values based on type')
    # translate: {dx, dy}
    # rotate: {angle, cx, cy}
    # scale: {sx, sy, cx, cy}
    # skew: {ax, ay}


class PathAlignSerializer(serializers.Serializer):
    """Serializer for path alignment."""
    
    path_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2
    )
    align_type = serializers.ChoiceField(choices=[
        ('left', 'Align Left'),
        ('center_h', 'Center Horizontal'),
        ('right', 'Align Right'),
        ('top', 'Align Top'),
        ('center_v', 'Center Vertical'),
        ('bottom', 'Align Bottom'),
    ])


class PathDistributeSerializer(serializers.Serializer):
    """Serializer for path distribution."""
    
    path_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=3
    )
    distribute_type = serializers.ChoiceField(choices=[
        ('horizontal', 'Distribute Horizontal'),
        ('vertical', 'Distribute Vertical'),
        ('spacing_h', 'Equal Horizontal Spacing'),
        ('spacing_v', 'Equal Vertical Spacing'),
    ])


class SVGImportSerializer(serializers.Serializer):
    """Serializer for SVG import."""
    
    svg_content = serializers.CharField()
    project_id = serializers.IntegerField()
    preserve_groups = serializers.BooleanField(default=True)
    flatten_transforms = serializers.BooleanField(default=False)


class SVGExportSerializer(serializers.Serializer):
    """Serializer for SVG export."""
    
    path_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text='Specific paths to export. If empty, exports all.'
    )
    include_styles = serializers.BooleanField(default=True)
    viewbox_padding = serializers.FloatField(default=0)
    minify = serializers.BooleanField(default=False)

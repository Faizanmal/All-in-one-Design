"""
Serializers for Animation Timeline app.
"""
from rest_framework import serializers
from .models import (
    AnimationProject, AnimationComposition, AnimationLayer,
    AnimationTrack, AnimationKeyframe, EasingPreset,
    AnimationEffect, LottieExport, AnimationSequence
)


class AnimationKeyframeSerializer(serializers.ModelSerializer):
    """Serializer for animation keyframes."""
    easing_preset_name = serializers.CharField(source='easing_preset.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AnimationKeyframe
        fields = [
            'id', 'track', 'frame_number', 'time_ms', 'value',
            'interpolation', 'easing_preset', 'easing_preset_name',
            'bezier_control_points', 'spring_config', 'is_hold',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnimationTrackSerializer(serializers.ModelSerializer):
    """Serializer for animation tracks."""
    keyframes = AnimationKeyframeSerializer(many=True, read_only=True)
    keyframe_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationTrack
        fields = [
            'id', 'layer', 'property_path', 'property_type',
            'is_locked', 'is_muted', 'color', 'created_at',
            'keyframes', 'keyframe_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_keyframe_count(self, obj):
        return obj.keyframes.count()


class AnimationEffectSerializer(serializers.ModelSerializer):
    """Serializer for animation effects."""
    
    class Meta:
        model = AnimationEffect
        fields = [
            'id', 'layer', 'effect_type', 'parameters',
            'start_frame', 'end_frame', 'is_enabled',
            'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnimationLayerSerializer(serializers.ModelSerializer):
    """Serializer for animation layers."""
    tracks = AnimationTrackSerializer(many=True, read_only=True)
    effects = AnimationEffectSerializer(many=True, read_only=True)
    parent_layer_name = serializers.CharField(source='parent_layer.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AnimationLayer
        fields = [
            'id', 'composition', 'name', 'layer_type', 'source_node_id',
            'parent_layer', 'parent_layer_name', 'in_point', 'out_point',
            'start_frame', 'time_stretch', 'is_visible', 'is_locked',
            'is_solo', 'is_shy', 'blend_mode', 'opacity', 'transform',
            'mask_mode', 'mask_data', 'order', 'color', 'created_at',
            'updated_at', 'tracks', 'effects'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnimationLayerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for layer lists."""
    track_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationLayer
        fields = [
            'id', 'name', 'layer_type', 'in_point', 'out_point',
            'is_visible', 'is_locked', 'order', 'color', 'track_count'
        ]
    
    def get_track_count(self, obj):
        return obj.tracks.count()


class AnimationSequenceSerializer(serializers.ModelSerializer):
    """Serializer for animation sequences."""
    
    class Meta:
        model = AnimationSequence
        fields = [
            'id', 'composition', 'source_composition', 'name',
            'start_frame', 'duration', 'speed', 'loop_count',
            'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AnimationCompositionSerializer(serializers.ModelSerializer):
    """Serializer for animation compositions."""
    layers = AnimationLayerListSerializer(many=True, read_only=True)
    sequences = AnimationSequenceSerializer(many=True, read_only=True)
    layer_count = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationComposition
        fields = [
            'id', 'project', 'name', 'description', 'width', 'height',
            'frame_rate', 'duration_frames', 'background_color',
            'is_main', 'created_at', 'updated_at', 'layers', 'sequences',
            'layer_count', 'duration_seconds'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_layer_count(self, obj):
        return obj.layers.count()
    
    def get_duration_seconds(self, obj):
        return obj.duration_frames / obj.frame_rate if obj.frame_rate else 0


class AnimationCompositionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for composition lists."""
    layer_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationComposition
        fields = [
            'id', 'name', 'width', 'height', 'frame_rate',
            'duration_frames', 'is_main', 'layer_count', 'updated_at'
        ]
    
    def get_layer_count(self, obj):
        return obj.layers.count()


class LottieExportSerializer(serializers.ModelSerializer):
    """Serializer for Lottie exports."""
    composition_name = serializers.CharField(source='composition.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = LottieExport
        fields = [
            'id', 'composition', 'composition_name', 'version', 'format',
            'file_url', 'file_size', 'include_assets', 'optimize',
            'target_size', 'export_data', 'status', 'error_message',
            'created_by', 'created_by_name', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'file_url', 'file_size', 'export_data', 'status', 'error_message', 'created_by', 'created_at', 'completed_at']


class AnimationProjectSerializer(serializers.ModelSerializer):
    """Serializer for animation projects."""
    compositions = AnimationCompositionListSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    composition_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationProject
        fields = [
            'id', 'project', 'name', 'description', 'thumbnail',
            'default_frame_rate', 'default_duration', 'color_depth',
            'working_color_space', 'is_published', 'created_by',
            'created_by_name', 'created_at', 'updated_at', 'compositions',
            'composition_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_composition_count(self, obj):
        return obj.compositions.count()


class AnimationProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for project lists."""
    composition_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AnimationProject
        fields = [
            'id', 'name', 'thumbnail', 'default_frame_rate',
            'is_published', 'updated_at', 'composition_count'
        ]
    
    def get_composition_count(self, obj):
        return obj.compositions.count()


class EasingPresetSerializer(serializers.ModelSerializer):
    """Serializer for easing presets."""
    
    class Meta:
        model = EasingPreset
        fields = [
            'id', 'name', 'description', 'easing_type', 'bezier_points',
            'spring_config', 'is_system', 'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class TimelineDataSerializer(serializers.Serializer):
    """Serializer for timeline data request."""
    start_frame = serializers.IntegerField(required=False, default=0)
    end_frame = serializers.IntegerField(required=False)
    include_keyframes = serializers.BooleanField(default=True)


class KeyframeBatchSerializer(serializers.Serializer):
    """Serializer for batch keyframe operations."""
    keyframes = serializers.ListField(
        child=serializers.DictField()
    )
    operation = serializers.ChoiceField(
        choices=['create', 'update', 'delete', 'shift']
    )
    shift_frames = serializers.IntegerField(required=False, default=0)


class ExportLottieSerializer(serializers.Serializer):
    """Serializer for Lottie export request."""
    format = serializers.ChoiceField(
        choices=['json', 'dotlottie'],
        default='json'
    )
    include_assets = serializers.BooleanField(default=True)
    optimize = serializers.BooleanField(default=False)
    target_size = serializers.IntegerField(required=False)

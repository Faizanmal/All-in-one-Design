from rest_framework import serializers
from .models import (
    Animation, Keyframe, LottieAnimation, MicroInteraction, 
    AnimationPreset, AnimationTimeline, TimelineItem
)


class KeyframeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyframe
        fields = ['id', 'position', 'properties', 'easing']


class AnimationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    keyframe_set = KeyframeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Animation
        fields = [
            'id', 'user', 'project', 'name', 'description', 'animation_type',
            'duration', 'delay', 'easing', 'easing_params', 'iterations',
            'direction', 'fill_mode', 'keyframes', 'keyframe_set',
            'tags', 'category', 'is_preset', 'is_public',
            'thumbnail', 'preview_gif',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class AnimationCreateSerializer(serializers.ModelSerializer):
    keyframes = serializers.ListField(child=serializers.DictField(), required=False)
    
    class Meta:
        model = Animation
        fields = [
            'name', 'description', 'animation_type', 'project',
            'duration', 'delay', 'easing', 'easing_params', 'iterations',
            'direction', 'fill_mode', 'keyframes',
            'tags', 'category'
        ]


class LottieAnimationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    lottie_url = serializers.SerializerMethodField()
    
    class Meta:
        model = LottieAnimation
        fields = [
            'id', 'user', 'project', 'name', 'description',
            'lottie_file', 'lottie_url', 'file_size',
            'version', 'frame_rate', 'in_point', 'out_point',
            'width', 'height', 'asset_count', 'layer_count',
            'thumbnail', 'tags', 'category',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'file_size', 'version', 'frame_rate',
                          'in_point', 'out_point', 'width', 'height',
                          'asset_count', 'layer_count', 'created_at', 'updated_at']
    
    def get_lottie_url(self, obj):
        if obj.lottie_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.lottie_file.url)
            return obj.lottie_file.url
        return None


class MicroInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicroInteraction
        fields = [
            'id', 'name', 'description', 'interaction_type',
            'animation_data', 'css_code', 'js_code', 'react_code', 'vue_code',
            'lottie_data', 'thumbnail', 'preview_url',
            'tags', 'is_premium', 'usage_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at', 'updated_at']


class AnimationPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimationPreset
        fields = [
            'id', 'name', 'description', 'category',
            'animation_data', 'parameters',
            'thumbnail', 'preview_gif',
            'tags', 'is_premium', 'usage_count',
            'created_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']


class TimelineItemSerializer(serializers.ModelSerializer):
    animation_name = serializers.ReadOnlyField(source='animation.name')
    lottie_name = serializers.ReadOnlyField(source='lottie.name')
    
    class Meta:
        model = TimelineItem
        fields = [
            'id', 'animation', 'animation_name', 'lottie', 'lottie_name',
            'track_index', 'start_time', 'end_time',
            'target_element_id', 'properties'
        ]


class AnimationTimelineSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    items = TimelineItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = AnimationTimeline
        fields = [
            'id', 'user', 'project', 'name', 'description',
            'duration', 'frame_rate', 'tracks', 'items',
            'export_settings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CSSExportSerializer(serializers.Serializer):
    animation_id = serializers.UUIDField()
    class_name = serializers.CharField(default='animation')
    include_keyframes = serializers.BooleanField(default=True)
    vendor_prefixes = serializers.BooleanField(default=True)


class LottieExportSerializer(serializers.Serializer):
    animation_id = serializers.UUIDField()
    optimize = serializers.BooleanField(default=True)
    compress = serializers.BooleanField(default=False)

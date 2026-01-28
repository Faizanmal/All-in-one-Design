"""
Media Assets Serializers
"""

from rest_framework import serializers
from .models import (
    VideoAsset, GIFAsset, LottieAsset, MediaPlacement,
    AnimatedExport, VideoFrame
)


class VideoAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAsset
        fields = [
            'id', 'name', 'source_type', 'file', 'url', 'embed_id',
            'duration', 'width', 'height', 'file_size', 'format',
            'thumbnail', 'autoplay', 'loop', 'muted', 'show_controls',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'duration', 'width', 'height', 'file_size', 'format', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GIFAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GIFAsset
        fields = [
            'id', 'name', 'file', 'width', 'height', 'frame_count',
            'duration', 'file_size', 'static_preview', 'autoplay', 'loop',
            'created_at'
        ]
        read_only_fields = ['id', 'width', 'height', 'frame_count', 'duration', 'file_size', 'static_preview', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LottieAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LottieAsset
        fields = [
            'id', 'name', 'json_data', 'file', 'version', 'frame_rate',
            'in_point', 'out_point', 'duration', 'width', 'height',
            'autoplay', 'loop', 'speed', 'direction', 'preview_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'frame_rate', 'in_point', 'out_point', 'duration', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Extract metadata from Lottie JSON
        json_data = validated_data.get('json_data', {})
        validated_data['version'] = json_data.get('v', '')
        validated_data['frame_rate'] = json_data.get('fr', 30)
        validated_data['in_point'] = json_data.get('ip', 0)
        validated_data['out_point'] = json_data.get('op', 0)
        validated_data['width'] = json_data.get('w')
        validated_data['height'] = json_data.get('h')
        if validated_data['frame_rate'] and validated_data['out_point']:
            validated_data['duration'] = (validated_data['out_point'] - validated_data.get('in_point', 0)) / validated_data['frame_rate']
        return super().create(validated_data)


class MediaPlacementSerializer(serializers.ModelSerializer):
    video_data = VideoAssetSerializer(source='video', read_only=True)
    gif_data = GIFAssetSerializer(source='gif', read_only=True)
    lottie_data = LottieAssetSerializer(source='lottie', read_only=True)
    
    class Meta:
        model = MediaPlacement
        fields = [
            'id', 'project', 'media_type', 'video', 'gif', 'lottie',
            'video_data', 'gif_data', 'lottie_data',
            'x', 'y', 'width', 'height', 'rotation',
            'clip_path', 'border_radius', 'z_index', 'is_visible', 'is_locked',
            'start_time', 'end_time', 'playback_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnimatedExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimatedExport
        fields = [
            'id', 'project', 'export_format', 'status', 'settings',
            'frame_start', 'frame_end', 'output_file', 'output_url',
            'file_size', 'progress', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'output_file', 'output_url', 'file_size', 'progress', 'error_message', 'started_at', 'completed_at', 'created_at']


class AnimatedExportRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    export_format = serializers.ChoiceField(choices=['gif', 'mp4', 'webm', 'lottie', 'apng', 'webp'])
    width = serializers.IntegerField(default=800, min_value=10, max_value=4096)
    height = serializers.IntegerField(default=600, min_value=10, max_value=4096)
    fps = serializers.IntegerField(default=30, min_value=1, max_value=60)
    quality = serializers.IntegerField(default=80, min_value=1, max_value=100)
    loop = serializers.BooleanField(default=True)
    duration = serializers.FloatField(required=False, min_value=0.1)
    start_time = serializers.FloatField(default=0, min_value=0)
    end_time = serializers.FloatField(required=False)
    background = serializers.CharField(default='#ffffff')


class VideoFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoFrame
        fields = ['id', 'video', 'frame_number', 'timestamp', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']


class ExtractFramesSerializer(serializers.Serializer):
    video_id = serializers.UUIDField()
    timestamps = serializers.ListField(
        child=serializers.FloatField(),
        required=False
    )
    frame_count = serializers.IntegerField(default=10, min_value=1, max_value=100)
    interval = serializers.FloatField(required=False, min_value=0.1)


class VideoFromURLSerializer(serializers.Serializer):
    url = serializers.URLField()
    name = serializers.CharField(max_length=255, required=False)
    project_id = serializers.IntegerField(required=False)

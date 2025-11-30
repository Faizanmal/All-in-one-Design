"""
Advanced AI Serializers
"""
from rest_framework import serializers
from .advanced_ai_models import (
    ImageToDesignRequest,
    StyleTransferRequest,
    VoiceToDesignRequest,
    DesignTrend,
    TrendAnalysisRequest,
    AIDesignSuggestion
)


class ImageToDesignRequestSerializer(serializers.ModelSerializer):
    """Serializer for image-to-design requests"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_project_name = serializers.CharField(source='result_project.name', read_only=True)
    
    class Meta:
        model = ImageToDesignRequest
        fields = [
            'id', 'source_image', 'prompt', 'target_design_type',
            'extract_colors', 'extract_typography', 'extract_layout', 'preserve_style',
            'status', 'status_display', 'result_project', 'result_project_name',
            'result_data', 'error_message', 'model_used', 'processing_time_ms',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'result_project', 'result_data', 'error_message',
            'model_used', 'processing_time_ms', 'created_at', 'completed_at'
        ]


class StyleTransferRequestSerializer(serializers.ModelSerializer):
    """Serializer for style transfer requests"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    style_preset_display = serializers.CharField(source='get_style_preset_display', read_only=True)
    source_project_name = serializers.CharField(source='source_project.name', read_only=True)
    result_project_name = serializers.CharField(source='result_project.name', read_only=True)
    
    class Meta:
        model = StyleTransferRequest
        fields = [
            'id', 'source_project', 'source_project_name',
            'style_preset', 'style_preset_display', 'style_reference_image', 'style_description',
            'transfer_colors', 'transfer_typography', 'transfer_spacing', 'transfer_shapes', 'intensity',
            'status', 'status_display', 'result_project', 'result_project_name',
            'result_data', 'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = [
            'status', 'result_project', 'result_data', 'error_message',
            'created_at', 'completed_at'
        ]


class VoiceToDesignRequestSerializer(serializers.ModelSerializer):
    """Serializer for voice-to-design requests"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    result_project_name = serializers.CharField(source='result_project.name', read_only=True)
    
    class Meta:
        model = VoiceToDesignRequest
        fields = [
            'id', 'audio_file', 'audio_duration_seconds',
            'transcribed_text', 'transcription_confidence',
            'design_type', 'additional_context',
            'status', 'status_display', 'result_project', 'result_project_name',
            'result_data', 'error_message',
            'transcription_model', 'generation_model',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'audio_duration_seconds', 'transcribed_text', 'transcription_confidence',
            'status', 'result_project', 'result_data', 'error_message',
            'transcription_model', 'generation_model', 'created_at', 'completed_at'
        ]


class DesignTrendSerializer(serializers.ModelSerializer):
    """Serializer for design trends"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = DesignTrend
        fields = [
            'id', 'category', 'category_display', 'name', 'description',
            'trend_data', 'popularity_score', 'growth_rate',
            'start_date', 'end_date', 'industries', 'source',
            'is_active', 'created_at', 'updated_at'
        ]


class TrendAnalysisRequestSerializer(serializers.ModelSerializer):
    """Serializer for trend analysis requests"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    matched_trends_data = DesignTrendSerializer(source='matched_trends', many=True, read_only=True)
    
    class Meta:
        model = TrendAnalysisRequest
        fields = [
            'id', 'project', 'project_name',
            'overall_score', 'color_score', 'typography_score', 'layout_score',
            'recommendations', 'matched_trends', 'matched_trends_data',
            'analysis_data', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIDesignSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AI design suggestions"""
    suggestion_type_display = serializers.CharField(source='get_suggestion_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = AIDesignSuggestion
        fields = [
            'id', 'project', 'project_name',
            'suggestion_type', 'suggestion_type_display',
            'priority', 'priority_display',
            'title', 'description',
            'affected_element_ids', 'suggested_changes',
            'is_applied', 'is_dismissed', 'user_feedback',
            'created_at'
        ]
        read_only_fields = ['created_at']

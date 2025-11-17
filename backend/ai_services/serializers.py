from rest_framework import serializers
from .models import AIGenerationRequest, AIPromptTemplate


class AIGenerationRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AIGenerationRequest
        fields = '__all__'
        read_only_fields = ('user', 'status', 'result', 'error_message', 
                           'model_used', 'tokens_used', 'created_at', 'completed_at')


class LayoutGenerationSerializer(serializers.Serializer):
    """Serializer for layout generation requests"""
    prompt = serializers.CharField(max_length=2000, required=True)
    design_type = serializers.ChoiceField(
        choices=['graphic', 'ui_ux', 'logo'],
        default='ui_ux'
    )


class LogoGenerationSerializer(serializers.Serializer):
    """Serializer for logo generation requests"""
    company_name = serializers.CharField(max_length=255, required=True)
    industry = serializers.CharField(max_length=255, required=False, allow_blank=True)
    style = serializers.CharField(max_length=100, default='modern')
    colors = serializers.ListField(
        child=serializers.CharField(max_length=7),  # Hex colors
        required=False,
        allow_empty=True
    )


class ColorPaletteGenerationSerializer(serializers.Serializer):
    """Serializer for color palette generation"""
    theme = serializers.CharField(max_length=500, required=True)


class DesignRefinementSerializer(serializers.Serializer):
    """Serializer for design refinement requests"""
    current_design = serializers.JSONField(required=True)
    refinement_instruction = serializers.CharField(max_length=1000, required=True)


class ImageGenerationSerializer(serializers.Serializer):
    """Serializer for AI image generation"""
    prompt = serializers.CharField(max_length=1000, required=True)
    size = serializers.ChoiceField(
        choices=['1024x1024', '1792x1024', '1024x1792'],
        default='1024x1024'
    )
    style = serializers.ChoiceField(
        choices=['vivid', 'natural'],
        default='vivid'
    )


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIPromptTemplate
        fields = '__all__'

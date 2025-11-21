"""
Serializers for enhanced template system
"""
from rest_framework import serializers
from templates.models import Template, TemplateComponent
from django.contrib.auth.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class TemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template lists"""
    created_by = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'category',
            'thumbnail_url', 'width', 'height',
            'tags', 'is_premium', 'use_count',
            'created_by', 'created_at'
        ]


class TemplateSerializer(serializers.ModelSerializer):
    """Full template serializer"""
    created_by = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Template
        fields = [
            'id', 'name', 'description', 'category',
            'design_data', 'thumbnail_url',
            'width', 'height', 'tags', 'color_palette',
            'is_premium', 'is_public', 'use_count',
            'ai_generated', 'ai_prompt',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['use_count', 'created_by', 'created_at', 'updated_at']
    
    def validate_design_data(self, value):
        """Validate design_data is a valid dict"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("design_data must be a dictionary")
        return value
    
    def validate_tags(self, value):
        """Validate tags is a list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("tags must be a list")
        return value


class TemplateComponentSerializer(serializers.ModelSerializer):
    """Serializer for template components"""
    
    class Meta:
        model = TemplateComponent
        fields = [
            'id', 'name', 'component_type',
            'design_data', 'thumbnail_url',
            'is_public', 'created_at'
        ]
        read_only_fields = ['created_at']


class TemplateCreateFromProjectSerializer(serializers.Serializer):
    """Serializer for creating a template from a project"""
    project_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.ChoiceField(
        choices=Template.TEMPLATE_CATEGORIES,
        default='social_media'
    )
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list
    )
    is_premium = serializers.BooleanField(default=False)
    is_public = serializers.BooleanField(default=False)

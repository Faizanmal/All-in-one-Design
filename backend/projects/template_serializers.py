"""
Serializers for Design Templates
"""
from rest_framework import serializers
from .models import DesignTemplate, TemplateFavorite, TemplateRating, ProjectTag


class DesignTemplateSerializer(serializers.ModelSerializer):
    """Serializer for design templates"""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignTemplate
        fields = [
            'id', 'name', 'description', 'category',
            'thumbnail_url', 'preview_images', 'design_data',
            'canvas_width', 'canvas_height', 'canvas_background',
            'tags', 'color_palette', 'suggested_fonts',
            'created_by', 'created_by_name', 'is_public', 'is_premium', 'is_featured',
            'use_count', 'favorite_count', 'rating',
            'is_favorited', 'user_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'use_count', 'favorite_count', 'rating', 'created_at', 'updated_at']
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TemplateFavorite.objects.filter(user=request.user, template=obj).exists()
        return False
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = TemplateRating.objects.filter(user=request.user, template=obj).first()
            return rating.rating if rating else None
        return None


class DesignTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing templates"""
    
    class Meta:
        model = DesignTemplate
        fields = [
            'id', 'name', 'category', 'thumbnail_url',
            'is_premium', 'is_featured', 'use_count', 
            'favorite_count', 'rating', 'tags'
        ]


class TemplateFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for template favorites"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = TemplateFavorite
        fields = ['id', 'user', 'template', 'template_name', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TemplateRatingSerializer(serializers.ModelSerializer):
    """Serializer for template ratings"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = TemplateRating
        fields = [
            'id', 'user', 'user_name', 'template', 'template_name',
            'rating', 'review', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ProjectTagSerializer(serializers.ModelSerializer):
    """Serializer for project tags"""
    
    class Meta:
        model = ProjectTag
        fields = [
            'id', 'name', 'slug', 'color', 'description',
            'project_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'project_count', 'created_at']

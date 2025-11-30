"""
Marketplace Serializers
"""
from rest_framework import serializers
from .marketplace_models import (
    MarketplaceTemplate,
    TemplateReview,
    TemplatePurchase,
    CreatorProfile,
    CreatorFollower,
    WhiteLabelConfig,
    WhiteLabelClient
)


class MarketplaceTemplateSerializer(serializers.ModelSerializer):
    """Serializer for marketplace templates"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    is_purchased = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceTemplate
        fields = [
            'id', 'creator', 'creator_name', 'name', 'slug', 'description',
            'category', 'category_display', 'thumbnail', 'preview_images',
            'is_free', 'price', 'tags', 'features', 'dimensions', 'compatible_with',
            'downloads', 'views', 'rating_average', 'rating_count',
            'status', 'status_display', 'is_featured',
            'created_at', 'published_at', 'is_purchased'
        ]
        read_only_fields = [
            'creator', 'downloads', 'views', 'rating_average', 'rating_count',
            'status', 'created_at', 'published_at'
        ]
    
    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TemplatePurchase.objects.filter(
                template=obj,
                user=request.user,
                status='completed'
            ).exists()
        return False


class TemplateReviewSerializer(serializers.ModelSerializer):
    """Serializer for template reviews"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TemplateReview
        fields = [
            'id', 'template', 'user', 'user_username',
            'rating', 'title', 'content',
            'helpful_count', 'is_verified_purchase',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'helpful_count', 'is_verified_purchase', 'created_at', 'updated_at']


class TemplatePurchaseSerializer(serializers.ModelSerializer):
    """Serializer for template purchases"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TemplatePurchase
        fields = [
            'id', 'template', 'template_name', 'user',
            'price_paid', 'status', 'status_display',
            'download_count', 'last_downloaded', 'created_at'
        ]
        read_only_fields = [
            'user', 'price_paid', 'creator_revenue', 'platform_revenue',
            'status', 'download_count', 'last_downloaded', 'created_at'
        ]


class CreatorProfileSerializer(serializers.ModelSerializer):
    """Serializer for creator profiles"""
    username = serializers.CharField(source='user.username', read_only=True)
    templates_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = CreatorProfile
        fields = [
            'id', 'user', 'username', 'display_name', 'bio',
            'avatar', 'cover_image',
            'website', 'twitter', 'dribbble', 'behance',
            'total_sales', 'follower_count', 'is_verified',
            'templates_count', 'is_following',
            'created_at'
        ]
        read_only_fields = [
            'user', 'total_sales', 'total_revenue', 'follower_count',
            'is_verified', 'verified_at', 'created_at'
        ]
    
    def get_templates_count(self, obj):
        return MarketplaceTemplate.objects.filter(
            creator=obj.user,
            status='published'
        ).count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CreatorFollower.objects.filter(
                creator=obj,
                follower=request.user
            ).exists()
        return False


class WhiteLabelConfigSerializer(serializers.ModelSerializer):
    """Serializer for white-label configurations"""
    client_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WhiteLabelConfig
        fields = [
            'id', 'company_name', 'logo', 'favicon',
            'primary_color', 'secondary_color', 'accent_color',
            'custom_domain', 'domain_verified',
            'hide_platform_branding', 'custom_email_domain', 'custom_support_email',
            'max_clients', 'max_projects_per_client',
            'is_active', 'client_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['domain_verified', 'created_at', 'updated_at']
    
    def get_client_count(self, obj):
        return obj.clients.filter(is_active=True).count()


class WhiteLabelClientSerializer(serializers.ModelSerializer):
    """Serializer for white-label clients"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = WhiteLabelClient
        fields = [
            'id', 'whitelabel', 'user', 'user_username', 'user_email',
            'max_projects', 'max_storage_mb', 'is_active', 'created_at'
        ]
        read_only_fields = ['whitelabel', 'created_at']

from rest_framework import serializers
from .models import (
    TemplateCategory, MarketplaceTemplate, TemplateVersion, TemplateReview,
    TemplatePurchase, CreatorProfile, CreatorPayout,
    TemplateCollection
)


class TemplateCategorySerializer(serializers.ModelSerializer):
    """Serializer for template categories"""
    template_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateCategory
        fields = [
            'id', 'name', 'slug', 'description', 'icon', 'color',
            'parent', 'order', 'is_featured', 'template_count', 'subcategories'
        ]
    
    def get_template_count(self, obj) -> int:
        return obj.templates.filter(status='approved').count()
    
    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return TemplateCategorySerializer(obj.subcategories.all(), many=True).data
        return []


class MarketplaceTemplateListSerializer(serializers.ModelSerializer):
    """Serializer for template listings"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceTemplate
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail',
            'category', 'category_name', 'creator', 'creator_name',
            'pricing_type', 'price', 'sale_price', 'effective_price',
            'downloads', 'average_rating', 'rating_count',
            'is_featured', 'is_editors_choice', 'is_favorited', 'is_purchased',
            'canvas_width', 'canvas_height', 'created_at'
        ]
    
    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_favorites.filter(user=request.user).exists()
        return False
    
    def get_is_purchased(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.pricing_type == 'free':
                return True
            return obj.purchases.filter(user=request.user, status='completed').exists()
        return False


class MarketplaceTemplateSerializer(serializers.ModelSerializer):
    """Full serializer for template details"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_profile = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketplaceTemplate
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'thumbnail', 'preview_images', 'preview_video',
            'category', 'category_name', 'tags',
            'creator', 'creator_name', 'creator_profile',
            'template_data', 'canvas_width', 'canvas_height',
            'pricing_type', 'price', 'sale_price', 'effective_price',
            'downloads', 'views', 'favorites',
            'average_rating', 'rating_count',
            'is_featured', 'is_editors_choice',
            'is_favorited', 'is_purchased', 'recent_reviews',
            'license_type', 'commercial_use',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'downloads', 'views', 'favorites', 'average_rating', 'rating_count',
            'created_at', 'updated_at', 'published_at'
        ]
    
    def get_creator_profile(self, obj):
        try:
            profile = obj.creator.creator_profile
            return {
                'display_name': profile.display_name,
                'avatar': profile.avatar,
                'is_verified': profile.is_verified,
                'is_pro': profile.is_pro,
            }
        except CreatorProfile.DoesNotExist:
            return None
    
    def get_is_favorited(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_favorites.filter(user=request.user).exists()
        return False
    
    def get_is_purchased(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.pricing_type == 'free':
                return True
            return obj.purchases.filter(user=request.user, status='completed').exists()
        return False
    
    def get_recent_reviews(self, obj):
        reviews = obj.reviews.filter(is_visible=True)[:3]
        return TemplateReviewSerializer(reviews, many=True).data


class MarketplaceTemplateCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating templates"""
    
    class Meta:
        model = MarketplaceTemplate
        fields = [
            'title', 'description', 'short_description', 'category', 'tags',
            'template_data', 'canvas_width', 'canvas_height',
            'thumbnail', 'preview_images', 'preview_video',
            'pricing_type', 'price', 'license_type', 'commercial_use'
        ]


class TemplateVersionSerializer(serializers.ModelSerializer):
    """Serializer for template versions"""
    
    class Meta:
        model = TemplateVersion
        fields = ['id', 'version', 'changelog', 'created_at']
        read_only_fields = ['created_at']


class TemplateReviewSerializer(serializers.ModelSerializer):
    """Serializer for template reviews"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TemplateReview
        fields = [
            'id', 'template', 'user', 'username', 'rating', 'title', 'content',
            'helpful_votes', 'is_verified_purchase', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'helpful_votes', 'is_verified_purchase', 'created_at', 'updated_at']


class TemplatePurchaseSerializer(serializers.ModelSerializer):
    """Serializer for template purchases"""
    template_title = serializers.CharField(source='template.title', read_only=True)
    
    class Meta:
        model = TemplatePurchase
        fields = [
            'id', 'template', 'template_title', 'amount', 'currency',
            'status', 'purchased_at'
        ]
        read_only_fields = ['amount', 'currency', 'status', 'purchased_at']


class CreatorProfileSerializer(serializers.ModelSerializer):
    """Serializer for creator profiles"""
    template_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CreatorProfile
        fields = [
            'id', 'user', 'display_name', 'bio', 'avatar', 'cover_image',
            'website', 'twitter', 'dribbble', 'behance',
            'is_verified', 'is_pro', 'total_sales', 'total_downloads',
            'follower_count', 'template_count', 'created_at'
        ]
        read_only_fields = [
            'is_verified', 'is_pro', 'total_sales', 'total_downloads',
            'follower_count', 'created_at'
        ]
    
    def get_template_count(self, obj) -> int:
        return MarketplaceTemplate.objects.filter(
            creator=obj.user, status='approved'
        ).count()


class CreatorPayoutSerializer(serializers.ModelSerializer):
    """Serializer for creator payouts"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CreatorPayout
        fields = [
            'id', 'amount', 'currency', 'period_start', 'period_end',
            'status', 'status_display', 'payout_method', 'transaction_id',
            'processed_at', 'created_at'
        ]
        read_only_fields = ['created_at', 'processed_at']


class TemplateCollectionSerializer(serializers.ModelSerializer):
    """Serializer for template collections"""
    template_count = serializers.SerializerMethodField()
    templates_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateCollection
        fields = [
            'id', 'name', 'slug', 'description', 'cover_image',
            'is_featured', 'template_count', 'templates_preview',
            'created_at', 'updated_at'
        ]
    
    def get_template_count(self, obj) -> int:
        return obj.templates.filter(status='approved').count()
    
    def get_templates_preview(self, obj):
        templates = obj.templates.filter(status='approved')[:4]
        return MarketplaceTemplateListSerializer(templates, many=True, context=self.context).data


class TemplateSearchSerializer(serializers.Serializer):
    """Serializer for template search"""
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    pricing_type = serializers.ChoiceField(
        choices=['free', 'paid', 'all'],
        required=False,
        default='all'
    )
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    sort_by = serializers.ChoiceField(
        choices=['newest', 'popular', 'rating', 'price_low', 'price_high'],
        required=False,
        default='newest'
    )
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class PurchaseRequestSerializer(serializers.Serializer):
    """Serializer for purchase requests"""
    template_id = serializers.IntegerField()
    payment_method = serializers.CharField()
    payment_token = serializers.CharField(required=False)

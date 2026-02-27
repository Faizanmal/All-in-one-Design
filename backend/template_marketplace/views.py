from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Avg
from django.utils.text import slugify
from drf_spectacular.utils import extend_schema

from .models import (
    TemplateCategory, MarketplaceTemplate, TemplateReview,
    TemplatePurchase, TemplateFavorite, CreatorProfile, TemplateCollection
)
from .serializers import (
    TemplateCategorySerializer, MarketplaceTemplateListSerializer,
    MarketplaceTemplateSerializer, MarketplaceTemplateCreateSerializer,
    TemplateReviewSerializer,
    TemplatePurchaseSerializer, CreatorProfileSerializer,
    TemplateCollectionSerializer,
    TemplateSearchSerializer, PurchaseRequestSerializer
)


class TemplateCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for template categories"""
    serializer_class = TemplateCategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return TemplateCategory.objects.filter(is_active=True, parent__isnull=True)
    
    @action(detail=True, methods=['get'])
    def templates(self, request, slug=None):
        """Get templates in category"""
        category = self.get_object()
        templates = MarketplaceTemplate.objects.filter(
            category=category, status='approved'
        )
        
        page = self.paginate_queryset(templates)
        if page is not None:
            serializer = MarketplaceTemplateListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)


class MarketplaceTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for marketplace templates"""
    lookup_field = 'slug'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'search', 'featured', 'popular']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketplaceTemplateCreateSerializer
        if self.action == 'list':
            return MarketplaceTemplateListSerializer
        return MarketplaceTemplateSerializer
    
    def get_queryset(self):
        queryset = MarketplaceTemplate.objects.filter(status='approved')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by pricing
        pricing = self.request.query_params.get('pricing')
        if pricing == 'free':
            queryset = queryset.filter(pricing_type='free')
        elif pricing == 'paid':
            queryset = queryset.filter(pricing_type='paid')
        
        return queryset.select_related('creator', 'category')
    
    def perform_create(self, serializer):
        slug = slugify(serializer.validated_data['title'])
        # Ensure unique slug
        counter = 1
        original_slug = slug
        while MarketplaceTemplate.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        serializer.save(
            creator=self.request.user,
            slug=slug,
            status='pending'
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        MarketplaceTemplate.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Get current user's templates"""
        templates = MarketplaceTemplate.objects.filter(creator=request.user)
        serializer = MarketplaceTemplateListSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    @extend_schema(request=TemplateSearchSerializer)
    def search(self, request):
        """Search templates"""
        serializer = TemplateSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        queryset = MarketplaceTemplate.objects.filter(status='approved')
        
        # Text search
        query = serializer.validated_data.get('query')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__contains=query)
            )
        
        # Category filter
        category = serializer.validated_data.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Pricing filter
        pricing_type = serializer.validated_data.get('pricing_type', 'all')
        if pricing_type == 'free':
            queryset = queryset.filter(pricing_type='free')
        elif pricing_type == 'paid':
            queryset = queryset.filter(pricing_type='paid')
        
        # Price range
        min_price = serializer.validated_data.get('min_price')
        max_price = serializer.validated_data.get('max_price')
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Tags
        tags = serializer.validated_data.get('tags', [])
        for tag in tags:
            queryset = queryset.filter(tags__contains=tag)
        
        # Sorting
        sort_by = serializer.validated_data.get('sort_by', 'newest')
        if sort_by == 'popular':
            queryset = queryset.order_by('-downloads')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            response_serializer = MarketplaceTemplateListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(response_serializer.data)
        
        return Response(MarketplaceTemplateListSerializer(queryset, many=True, context={'request': request}).data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured templates"""
        templates = MarketplaceTemplate.objects.filter(
            status='approved', is_featured=True
        ).order_by('-updated_at')[:12]
        
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular templates"""
        templates = MarketplaceTemplate.objects.filter(
            status='approved'
        ).order_by('-downloads')[:12]
        
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, slug=None):
        """Toggle favorite status"""
        template = self.get_object()
        favorite, created = TemplateFavorite.objects.get_or_create(
            template=template, user=request.user
        )
        
        if not created:
            favorite.delete()
            MarketplaceTemplate.objects.filter(pk=template.pk).update(favorites=F('favorites') - 1)
            return Response({'favorited': False})
        
        MarketplaceTemplate.objects.filter(pk=template.pk).update(favorites=F('favorites') + 1)
        return Response({'favorited': True})
    
    @action(detail=True, methods=['post'])
    @extend_schema(request=PurchaseRequestSerializer)
    def purchase(self, request, slug=None):
        """Purchase a template"""
        template = self.get_object()
        
        if template.pricing_type == 'free':
            return Response({'error': 'This template is free'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already purchased
        if TemplatePurchase.objects.filter(
            template=template, user=request.user, status='completed'
        ).exists():
            return Response({'error': 'Already purchased'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create purchase record
        purchase = TemplatePurchase.objects.create(
            template=template,
            user=request.user,
            amount=template.effective_price,
            status='completed',  # In production, integrate with payment gateway
        )
        
        # Update template stats
        MarketplaceTemplate.objects.filter(pk=template.pk).update(downloads=F('downloads') + 1)
        
        # Update creator stats
        try:
            profile = template.creator.creator_profile
            profile.total_sales += 1
            profile.total_earnings += template.effective_price
            profile.save()
        except CreatorProfile.DoesNotExist:
            pass
        
        return Response(TemplatePurchaseSerializer(purchase).data)
    
    @action(detail=True, methods=['get'])
    def download(self, request, slug=None):
        """Download template data"""
        template = self.get_object()
        
        # Check access
        if template.pricing_type != 'free':
            if not TemplatePurchase.objects.filter(
                template=template, user=request.user, status='completed'
            ).exists():
                return Response(
                    {'error': 'Purchase required'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Increment download count for free templates
        if template.pricing_type == 'free':
            MarketplaceTemplate.objects.filter(pk=template.pk).update(downloads=F('downloads') + 1)
        
        return Response({
            'template_data': template.template_data,
            'canvas_width': template.canvas_width,
            'canvas_height': template.canvas_height,
        })
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, slug=None):
        """Submit template for review"""
        template = get_object_or_404(
            MarketplaceTemplate,
            slug=slug,
            creator=request.user
        )
        
        if template.status not in ['draft', 'rejected']:
            return Response(
                {'error': 'Template cannot be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template.status = 'pending'
        template.save()
        
        return Response({'status': 'submitted'})


class TemplateReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for template reviews"""
    serializer_class = TemplateReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        template_slug = self.request.query_params.get('template')
        queryset = TemplateReview.objects.filter(is_visible=True)
        
        if template_slug:
            queryset = queryset.filter(template__slug=template_slug)
        
        return queryset.select_related('user', 'template')
    
    def perform_create(self, serializer):
        template = serializer.validated_data['template']
        
        # Check if user purchased the template
        is_verified = TemplatePurchase.objects.filter(
            template=template, user=self.request.user, status='completed'
        ).exists() or template.pricing_type == 'free'
        
        review = serializer.save(
            user=self.request.user,
            is_verified_purchase=is_verified
        )
        
        # Update template average rating
        avg_rating = TemplateReview.objects.filter(
            template=template, is_visible=True
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        
        MarketplaceTemplate.objects.filter(pk=template.pk).update(
            average_rating=avg_rating,
            rating_count=F('rating_count') + 1
        )
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        review.helpful_votes += 1
        review.save()
        return Response({'helpful_votes': review.helpful_votes})


class CreatorProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for creator profiles"""
    serializer_class = CreatorProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        return CreatorProfile.objects.all()
    
    def get_object(self):
        if self.kwargs.get('username') == 'me':
            obj, created = CreatorProfile.objects.get_or_create(
                user=self.request.user,
                defaults={'display_name': self.request.user.username}
            )
            return obj
        return super().get_object()
    
    @action(detail=True, methods=['get'])
    def templates(self, request, username=None):
        """Get creator's templates"""
        profile = self.get_object()
        templates = MarketplaceTemplate.objects.filter(
            creator=profile.user, status='approved'
        )
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)
    
    @action(detail=True, methods=['get'])
    def earnings(self, request, username=None):
        """Get creator earnings (own only)"""
        if self.kwargs.get('username') != 'me':
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        profile = self.get_object()
        
        # Get earnings by period
        from django.db.models.functions import TruncMonth
        from django.db.models import Sum
        
        monthly = TemplatePurchase.objects.filter(
            template__creator=profile.user,
            status='completed'
        ).annotate(
            month=TruncMonth('purchased_at')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('-month')[:12]
        
        return Response({
            'total_earnings': profile.total_earnings,
            'total_sales': profile.total_sales,
            'monthly': list(monthly),
        })


class TemplateCollectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for template collections"""
    serializer_class = TemplateCollectionSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return TemplateCollection.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def templates(self, request, slug=None):
        """Get templates in collection"""
        collection = self.get_object()
        templates = collection.templates.filter(status='approved')
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)


class FavoriteTemplatesView(APIView):
    """Get user's favorite templates"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        favorites = TemplateFavorite.objects.filter(user=request.user).select_related('template')
        templates = [f.template for f in favorites if f.template.status == 'approved']
        return Response(MarketplaceTemplateListSerializer(templates, many=True, context={'request': request}).data)


class PurchasedTemplatesView(APIView):
    """Get user's purchased templates"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        purchases = TemplatePurchase.objects.filter(
            user=request.user, status='completed'
        ).select_related('template')
        
        return Response(TemplatePurchaseSerializer(purchases, many=True).data)

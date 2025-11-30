"""
Marketplace Views
REST API endpoints for the template marketplace
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q, F
from django.utils import timezone
from django.utils.text import slugify
from decimal import Decimal

from .marketplace_models import (
    MarketplaceTemplate,
    TemplateReview,
    TemplatePurchase,
    CreatorProfile,
    CreatorFollower,
    WhiteLabelConfig,
    WhiteLabelClient
)
from .marketplace_serializers import (
    MarketplaceTemplateSerializer,
    TemplateReviewSerializer,
    TemplatePurchaseSerializer,
    CreatorProfileSerializer,
    WhiteLabelConfigSerializer,
    WhiteLabelClientSerializer
)


class MarketplaceTemplateViewSet(viewsets.ModelViewSet):
    """Marketplace template management"""
    serializer_class = MarketplaceTemplateSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'downloads', 'rating_average', 'price']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'featured', 'popular', 'categories']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = MarketplaceTemplate.objects.all()
        
        if self.action in ['list', 'retrieve']:
            # Public views only show published templates
            queryset = queryset.filter(status='published')
        elif self.request.user.is_authenticated:
            # Creator can see their own templates
            queryset = queryset.filter(
                Q(status='published') | Q(creator=self.request.user)
            )
        
        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Price filter
        is_free = self.request.query_params.get('is_free')
        if is_free == 'true':
            queryset = queryset.filter(is_free=True)
        elif is_free == 'false':
            queryset = queryset.filter(is_free=False)
        
        # Price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        if max_price:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        
        return queryset
    
    def perform_create(self, serializer):
        slug = slugify(serializer.validated_data['name'])
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while MarketplaceTemplate.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        serializer.save(creator=self.request.user, slug=slug)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        MarketplaceTemplate.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured templates"""
        templates = MarketplaceTemplate.objects.filter(
            status='published',
            is_featured=True
        ).order_by('-featured_until')[:12]
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular templates"""
        templates = MarketplaceTemplate.objects.filter(
            status='published'
        ).order_by('-downloads')[:20]
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get template categories with counts"""
        categories = []
        for choice in MarketplaceTemplate.CATEGORY_CHOICES:
            count = MarketplaceTemplate.objects.filter(
                status='published',
                category=choice[0]
            ).count()
            categories.append({
                'slug': choice[0],
                'name': choice[1],
                'count': count
            })
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Submit template for review"""
        template = self.get_object()
        if template.creator != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if template.status != 'draft':
            return Response(
                {'error': 'Only draft templates can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template.status = 'pending_review'
        template.save()
        
        return Response({'status': 'pending_review'})
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """Purchase a template"""
        template = self.get_object()
        
        if template.creator == request.user:
            return Response(
                {'error': 'Cannot purchase your own template'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already purchased
        existing = TemplatePurchase.objects.filter(
            template=template,
            user=request.user,
            status='completed'
        ).first()
        
        if existing:
            return Response(
                {'error': 'Already purchased'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate revenue split
        creator_share = template.creator_revenue_share / 100
        creator_revenue = template.price * Decimal(str(creator_share))
        platform_revenue = template.price - creator_revenue
        
        # Create purchase (in production, integrate with Stripe)
        purchase = TemplatePurchase.objects.create(
            template=template,
            user=request.user,
            price_paid=template.price if not template.is_free else Decimal('0.00'),
            creator_revenue=creator_revenue if not template.is_free else Decimal('0.00'),
            platform_revenue=platform_revenue if not template.is_free else Decimal('0.00'),
            status='completed' if template.is_free else 'pending'
        )
        
        if template.is_free:
            # Update download count
            MarketplaceTemplate.objects.filter(pk=template.pk).update(
                downloads=F('downloads') + 1
            )
        
        serializer = TemplatePurchaseSerializer(purchase)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Download a purchased template"""
        template = self.get_object()
        
        # Check if purchased (or free)
        purchase = TemplatePurchase.objects.filter(
            template=template,
            user=request.user,
            status='completed'
        ).first()
        
        if not purchase and not template.is_free:
            return Response(
                {'error': 'Template not purchased'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update download tracking
        if purchase:
            purchase.download_count += 1
            purchase.last_downloaded = timezone.now()
            purchase.save()
        
        return Response({
            'design_data': template.design_data,
            'name': template.name
        })


class TemplateReviewViewSet(viewsets.ModelViewSet):
    """Template review management"""
    serializer_class = TemplateReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TemplateReview.objects.all()
        
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        return queryset
    
    def perform_create(self, serializer):
        template = serializer.validated_data['template']
        
        # Check if user purchased the template
        is_verified = TemplatePurchase.objects.filter(
            template=template,
            user=self.request.user,
            status='completed'
        ).exists()
        
        serializer.save(
            user=self.request.user,
            is_verified_purchase=is_verified
        )
        
        # Update template rating
        self._update_template_rating(template)
    
    def _update_template_rating(self, template):
        from django.db.models import Avg
        
        stats = TemplateReview.objects.filter(template=template).aggregate(
            avg_rating=Avg('rating'),
            count=models.Count('id')
        )
        
        template.rating_average = stats['avg_rating'] or 0
        template.rating_count = stats['count']
        template.save()
    
    @action(detail=True, methods=['post'])
    def mark_helpful(self, request, pk=None):
        """Mark a review as helpful"""
        review = self.get_object()
        TemplateReview.objects.filter(pk=review.pk).update(
            helpful_count=F('helpful_count') + 1
        )
        return Response({'status': 'marked_helpful'})


class CreatorProfileViewSet(viewsets.ModelViewSet):
    """Creator profile management"""
    serializer_class = CreatorProfileSerializer
    lookup_field = 'user__username'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'templates']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        return CreatorProfile.objects.all()
    
    def get_object(self):
        if self.kwargs.get('user__username') == 'me':
            return CreatorProfile.objects.get_or_create(
                user=self.request.user,
                defaults={'display_name': self.request.user.username}
            )[0]
        return super().get_object()
    
    @action(detail=True, methods=['get'])
    def templates(self, request, user__username=None):
        """Get creator's templates"""
        profile = self.get_object()
        templates = MarketplaceTemplate.objects.filter(
            creator=profile.user,
            status='published'
        )
        serializer = MarketplaceTemplateSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, user__username=None):
        """Follow a creator"""
        profile = self.get_object()
        
        if profile.user == request.user:
            return Response(
                {'error': 'Cannot follow yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follower, created = CreatorFollower.objects.get_or_create(
            creator=profile,
            follower=request.user
        )
        
        if created:
            CreatorProfile.objects.filter(pk=profile.pk).update(
                follower_count=F('follower_count') + 1
            )
            return Response({'status': 'followed'})
        
        return Response({'status': 'already_following'})
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, user__username=None):
        """Unfollow a creator"""
        profile = self.get_object()
        
        deleted, _ = CreatorFollower.objects.filter(
            creator=profile,
            follower=request.user
        ).delete()
        
        if deleted:
            CreatorProfile.objects.filter(pk=profile.pk).update(
                follower_count=F('follower_count') - 1
            )
            return Response({'status': 'unfollowed'})
        
        return Response({'status': 'not_following'})


class WhiteLabelConfigViewSet(viewsets.ModelViewSet):
    """White-label configuration management"""
    serializer_class = WhiteLabelConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WhiteLabelConfig.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify_domain(self, request, pk=None):
        """Verify custom domain ownership"""
        config = self.get_object()
        
        # In production, implement DNS verification
        # For now, just mark as verified
        config.domain_verified = True
        config.save()
        
        return Response({'status': 'verified'})
    
    @action(detail=True, methods=['get'])
    def clients(self, request, pk=None):
        """Get all clients for this white-label"""
        config = self.get_object()
        clients = config.clients.all()
        serializer = WhiteLabelClientSerializer(clients, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_client(self, request, pk=None):
        """Add a client to white-label"""
        config = self.get_object()
        
        # Check client limit
        current_count = config.clients.filter(is_active=True).count()
        if current_count >= config.max_clients:
            return Response(
                {'error': 'Client limit reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        client, created = WhiteLabelClient.objects.get_or_create(
            whitelabel=config,
            user=user,
            defaults={
                'max_projects': request.data.get('max_projects', config.max_projects_per_client),
                'max_storage_mb': request.data.get('max_storage_mb', 5000)
            }
        )
        
        if not created:
            client.is_active = True
            client.save()
        
        serializer = WhiteLabelClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_purchases(request):
    """Get current user's template purchases"""
    purchases = TemplatePurchase.objects.filter(
        user=request.user,
        status='completed'
    )
    serializer = TemplatePurchaseSerializer(purchases, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_sales(request):
    """Get current user's template sales (as creator)"""
    from django.db.models import Sum, Count
    
    purchases = TemplatePurchase.objects.filter(
        template__creator=request.user,
        status='completed'
    )
    
    stats = purchases.aggregate(
        total_sales=Count('id'),
        total_revenue=Sum('creator_revenue')
    )
    
    recent = purchases.order_by('-created_at')[:20]
    
    return Response({
        'total_sales': stats['total_sales'] or 0,
        'total_revenue': str(stats['total_revenue'] or 0),
        'recent_sales': TemplatePurchaseSerializer(recent, many=True).data
    })

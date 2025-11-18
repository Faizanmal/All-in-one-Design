"""
API Views for Subscription Management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta

from .models import (
    SubscriptionTier, Subscription, UsageQuota, 
    Payment, Invoice, Coupon, CouponUsage
)
from .coupon_serializers import (
    CouponSerializer, CouponValidationSerializer, CouponUsageSerializer
)
import logging

logger = logging.getLogger('subscriptions')


class SubscriptionTierViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for subscription tiers"""
    queryset = SubscriptionTier.objects.filter(is_active=True).order_by('sort_order')
    permission_classes = []  # Public endpoint
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class SubscriptionTierSerializer(serializers.ModelSerializer):
            features = serializers.SerializerMethodField()
            
            class Meta:
                model = SubscriptionTier
                fields = [
                    'id', 'name', 'slug', 'description',
                    'price_monthly', 'price_yearly',
                    'max_projects', 'max_ai_requests_per_month',
                    'max_storage_mb', 'max_collaborators_per_project',
                    'features', 'is_featured'
                ]
            
            def get_features(self, obj):
                features = []
                if obj.max_projects == -1:
                    features.append('Unlimited projects')
                else:
                    features.append(f'{obj.max_projects} projects')
                
                if obj.max_ai_requests_per_month == -1:
                    features.append('Unlimited AI requests')
                else:
                    features.append(f'{obj.max_ai_requests_per_month} AI requests/month')
                
                if obj.max_storage_mb == -1:
                    features.append('Unlimited storage')
                else:
                    features.append(f'{obj.max_storage_mb} MB storage')
                
                if obj.max_collaborators_per_project == -1:
                    features.append('Unlimited collaborators')
                else:
                    features.append(f'{obj.max_collaborators_per_project} collaborators/project')
                
                return features
        
        return SubscriptionTierSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class SubscriptionSerializer(serializers.ModelSerializer):
            tier_name = serializers.CharField(source='tier.name', read_only=True)
            
            class Meta:
                model = Subscription
                fields = [
                    'id', 'tier', 'tier_name', 'status', 'billing_period',
                    'start_date', 'end_date', 'trial_end_date', 
                    'next_billing_date', 'cancelled_at',
                    'stripe_customer_id', 'stripe_subscription_id',
                    'auto_renew', 'created_at', 'updated_at'
                ]
                read_only_fields = [
                    'stripe_customer_id', 'stripe_subscription_id',
                    'created_at', 'updated_at'
                ]
        
        return SubscriptionSerializer
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's subscription"""
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def usage(self, request):
        """Get subscription usage statistics"""
        try:
            subscription = Subscription.objects.get(user=request.user)
            
            # Calculate usage
            from projects.models import Project
            from assets.models import Asset
            from analytics.models import AIUsageMetrics
            from teams.models import TeamMembership
            from django.db.models import Sum
            
            projects_used = Project.objects.filter(user=request.user).count()
            storage_used = Asset.objects.filter(user=request.user).aggregate(
                total=Sum('file_size')
            )['total'] or 0
            
            # AI requests this month
            first_day = timezone.now().replace(day=1, hour=0, minute=0, second=0)
            ai_requests_used = AIUsageMetrics.objects.filter(
                user=request.user,
                timestamp__gte=first_day
            ).count()
            
            team_members_used = TeamMembership.objects.filter(
                team__owner=request.user
            ).count()
            
            return Response({
                'projects_used': projects_used,
                'projects_limit': subscription.tier.max_projects,
                'storage_used': storage_used,
                'storage_limit': subscription.tier.max_storage_mb * 1024 * 1024,
                'ai_requests_used': ai_requests_used,
                'ai_requests_limit': subscription.tier.max_ai_requests_per_month,
                'team_members_used': team_members_used,
                'team_members_limit': subscription.tier.max_collaborators_per_project,
            })
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Create a new subscription"""
        tier_slug = request.data.get('tier')
        billing_period = request.data.get('billing_period', 'monthly')
        coupon_code = request.data.get('coupon_code')
        
        try:
            tier = SubscriptionTier.objects.get(slug=tier_slug)
        except SubscriptionTier.DoesNotExist:
            return Response(
                {'error': 'Invalid subscription tier'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already has a subscription
        if Subscription.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'User already has a subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate billing dates
        start_date = timezone.now()
        if billing_period == 'yearly':
            next_billing = start_date + timedelta(days=365)
        else:
            next_billing = start_date + timedelta(days=30)
        
        # Create subscription
        subscription = Subscription.objects.create(
            user=request.user,
            tier=tier,
            status='active',
            billing_period=billing_period,
            start_date=start_date,
            next_billing_date=next_billing
        )
        
        # Apply coupon if provided
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid_for_user(request.user, tier):
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=request.user,
                        subscription=subscription
                    )
            except Coupon.DoesNotExist:
                pass
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['patch'])
    def update_subscription(self, request):
        """Update existing subscription"""
        try:
            subscription = Subscription.objects.get(user=request.user)
            tier_slug = request.data.get('tier')
            
            if tier_slug:
                tier = SubscriptionTier.objects.get(slug=tier_slug)
                subscription.tier = tier
                subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def cancel(self, request):
        """Cancel subscription"""
        immediate = request.data.get('immediate', False)
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.cancelled_at = timezone.now()
            
            if immediate:
                subscription.status = 'cancelled'
                subscription.end_date = timezone.now()
            else:
                subscription.auto_renew = False
                # Will be cancelled at end of billing period
            
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def resume(self, request):
        """Resume a cancelled subscription"""
        try:
            subscription = Subscription.objects.get(user=request.user)
            subscription.auto_renew = True
            subscription.cancelled_at = None
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'error': 'No active subscription'},
                status=status.HTTP_404_NOT_FOUND
            )


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for managing coupons"""
    serializer_class = CouponSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Coupon.objects.all()
        return Coupon.objects.filter(is_active=True)
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Validate a coupon code"""
        code = request.data.get('code') or request.query_params.get('code')
        tier_slug = request.data.get('tier') or request.query_params.get('tier')
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            
            # Check if valid for user
            if tier_slug:
                tier = SubscriptionTier.objects.get(slug=tier_slug)
                valid = coupon.is_valid_for_user(request.user, tier)
            else:
                valid = coupon.is_valid_for_user(request.user)
            
            if valid:
                # Calculate discount
                if tier_slug:
                    tier = SubscriptionTier.objects.get(slug=tier_slug)
                    price = tier.price_monthly
                    if coupon.discount_type == 'percentage':
                        discount = price * (coupon.discount_value / 100)
                    else:
                        discount = coupon.discount_value
                else:
                    discount = coupon.discount_value
                
                return Response({
                    'valid': True,
                    'coupon': CouponSerializer(coupon).data,
                    'discount_amount': discount
                })
            else:
                return Response({
                    'valid': False,
                    'error': 'Coupon not valid for this user or tier'
                })
        except Coupon.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid coupon code'
            })
        except SubscriptionTier.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid subscription tier'
            })
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get coupon usage history"""
        coupon = self.get_object()
        usages = CouponUsage.objects.filter(coupon=coupon)
        serializer = CouponUsageSerializer(usages, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_history(request):
    """Get billing history for user"""
    invoices = Invoice.objects.filter(subscription__user=request.user).order_by('-created_at')
    
    from rest_framework import serializers
    
    class InvoiceSerializer(serializers.ModelSerializer):
        class Meta:
            model = Invoice
            fields = '__all__'
    
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)

"""
Subscription Feature Gating

Provides decorators and utilities to enforce subscription tier features
at the view/endpoint level.

Features defined in SubscriptionTier.features JSON:
- advanced_ai: Access to advanced AI features
- priority_support: Priority support access
- custom_branding: Custom branding capabilities
- api_access: API key access
- white_label: White-label/agency features
"""
import logging
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('subscriptions')

# Free tier defaults (when no subscription exists)
FREE_TIER_FEATURES = {
    'advanced_ai': False,
    'priority_support': False,
    'custom_branding': False,
    'api_access': False,
    'white_label': False,
}


def get_user_features(user):
    """
    Get the feature flags for a user based on their subscription tier.
    
    Returns:
        dict: Feature flags (defaults to FREE_TIER_FEATURES if no subscription)
    """
    try:
        subscription = user.subscription
        if subscription.is_active():
            return subscription.tier.features or FREE_TIER_FEATURES.copy()
    except Exception:
        pass
    
    return FREE_TIER_FEATURES.copy()


def has_feature(user, feature_name: str) -> bool:
    """
    Check if a user has access to a specific feature.
    
    Args:
        user: Django User instance
        feature_name: Feature key from tier.features JSON
        
    Returns:
        bool: Whether the user has the feature
    """
    features = get_user_features(user)
    return features.get(feature_name, False)


def require_feature(feature_name: str, error_message: str = None):
    """
    Decorator for views that require a specific subscription feature.
    
    Usage:
        @require_feature('advanced_ai')
        @api_view(['POST'])
        @permission_classes([IsAuthenticated])
        def my_advanced_view(request):
            ...
    
    Args:
        feature_name: Feature key from tier.features JSON
        error_message: Custom error message (optional)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            if not has_feature(request.user, feature_name):
                msg = error_message or (
                    f"This feature requires the '{feature_name}' capability. "
                    "Please upgrade your subscription to access it."
                )
                return Response(
                    {
                        'error': 'feature_not_available',
                        'message': msg,
                        'required_feature': feature_name,
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_active_subscription(view_func):
    """
    Decorator for views that require any active subscription.
    
    Usage:
        @require_active_subscription
        @api_view(['POST'])
        @permission_classes([IsAuthenticated])
        def my_paid_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        try:
            subscription = request.user.subscription
            if not subscription.is_active():
                return Response(
                    {
                        'error': 'subscription_inactive',
                        'message': 'An active subscription is required. Please renew or upgrade.',
                    },
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )
        except Exception:
            return Response(
                {
                    'error': 'no_subscription',
                    'message': 'A subscription is required to access this feature. Please subscribe.',
                },
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


class FeatureGateMixin:
    """
    Mixin for ViewSets that require specific subscription features.
    
    Usage:
        class MyViewSet(FeatureGateMixin, viewsets.ModelViewSet):
            required_feature = 'advanced_ai'
            ...
    """
    required_feature = None
    
    def check_permissions(self, request):
        super().check_permissions(request)
        
        if self.required_feature and request.user.is_authenticated:
            if not has_feature(request.user, self.required_feature):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied(
                    f"This feature requires the '{self.required_feature}' capability. "
                    "Please upgrade your subscription."
                )

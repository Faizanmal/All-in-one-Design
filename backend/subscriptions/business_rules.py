"""
Business Rules & Free Tier Enforcement

Centralized service for checking subscription limits,
tracking usage, and enforcing business rules across all API endpoints.
"""
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.exceptions import PermissionDenied
from functools import wraps
import logging

logger = logging.getLogger('subscriptions')

# Default free tier limits
FREE_TIER_LIMITS = {
    'max_projects': 5,
    'max_ai_requests_per_month': 50,
    'max_exports_per_month': 10,
    'max_storage_mb': 100,
    'max_collaborators_per_project': 0,
    'max_file_upload_mb': 5,
    'features': {
        'advanced_ai': False,
        'priority_support': False,
        'custom_branding': False,
        'api_access': False,
        'white_label': False,
        'batch_export': False,
        'version_history': True,  # Limited to 10 versions
        'max_versions': 10,
        'pdf_export': True,
        'svg_export': True,
        'figma_export': False,
        'team_collaboration': False,
        'analytics_dashboard': False,
        'custom_fonts': False,
        'premium_templates': False,
    }
}


class BusinessRules:
    """Centralized business rules enforcement."""
    
    @staticmethod
    def get_user_limits(user: User) -> dict:
        """Get the effective limits for a user based on their subscription."""
        try:
            sub = user.subscription
            if sub.is_active():
                tier = sub.tier
                return {
                    'max_projects': tier.max_projects,
                    'max_ai_requests_per_month': tier.max_ai_requests_per_month,
                    'max_exports_per_month': tier.max_exports_per_month,
                    'max_storage_mb': tier.max_storage_mb,
                    'max_collaborators_per_project': tier.max_collaborators_per_project,
                    'max_file_upload_mb': getattr(settings, 'MAX_UPLOAD_SIZE_MB', 50),
                    'features': tier.features,
                    'tier_name': tier.name,
                    'is_free': False,
                }
        except Exception:
            pass
        
        # Free tier defaults
        limits = dict(FREE_TIER_LIMITS)
        limits['tier_name'] = 'Free'
        limits['is_free'] = True
        return limits
    
    @staticmethod
    def check_project_limit(user: User) -> bool:
        """Check if user can create more projects."""
        from projects.models import Project
        limits = BusinessRules.get_user_limits(user)
        max_projects = limits['max_projects']
        if max_projects == -1:
            return True
        current_count = Project.objects.filter(user=user).count()
        return current_count < max_projects
    
    @staticmethod
    def check_ai_quota(user: User) -> bool:
        """Check if user can make more AI requests this month."""
        limits = BusinessRules.get_user_limits(user)
        max_requests = limits['max_ai_requests_per_month']
        if max_requests == -1:
            return True
        
        first_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        try:
            from analytics.models import AIUsageMetrics
            count = AIUsageMetrics.objects.filter(
                user=user,
                timestamp__gte=first_of_month
            ).count()
        except Exception:
            count = 0
        
        return count < max_requests
    
    @staticmethod
    def check_export_quota(user: User) -> bool:
        """Check if user can make more exports this month."""
        limits = BusinessRules.get_user_limits(user)
        max_exports = limits['max_exports_per_month']
        if max_exports == -1:
            return True
        
        first_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        try:
            from analytics.models import UserActivity
            count = UserActivity.objects.filter(
                user=user,
                activity_type='project_export',
                timestamp__gte=first_of_month
            ).count()
        except Exception:
            count = 0
        
        return count < max_exports
    
    @staticmethod
    def check_feature(user: User, feature: str) -> bool:
        """Check if user has access to a specific feature."""
        limits = BusinessRules.get_user_limits(user)
        features = limits.get('features', {})
        return features.get(feature, False)
    
    @staticmethod
    def get_usage_summary(user: User) -> dict:
        """Get a summary of the user's current usage and limits."""
        from projects.models import Project
        
        limits = BusinessRules.get_user_limits(user)
        first_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        project_count = Project.objects.filter(user=user).count()
        
        try:
            from analytics.models import AIUsageMetrics, UserActivity
            ai_count = AIUsageMetrics.objects.filter(
                user=user, timestamp__gte=first_of_month
            ).count()
            export_count = UserActivity.objects.filter(
                user=user, activity_type='project_export',
                timestamp__gte=first_of_month
            ).count()
        except Exception:
            ai_count = 0
            export_count = 0
        
        return {
            'tier': limits['tier_name'],
            'is_free': limits.get('is_free', True),
            'projects': {
                'used': project_count,
                'limit': limits['max_projects'],
                'unlimited': limits['max_projects'] == -1,
            },
            'ai_requests': {
                'used': ai_count,
                'limit': limits['max_ai_requests_per_month'],
                'unlimited': limits['max_ai_requests_per_month'] == -1,
            },
            'exports': {
                'used': export_count,
                'limit': limits['max_exports_per_month'],
                'unlimited': limits['max_exports_per_month'] == -1,
            },
            'features': limits.get('features', {}),
            'reset_date': (first_of_month.replace(month=first_of_month.month % 12 + 1)
                          if first_of_month.month < 12
                          else first_of_month.replace(year=first_of_month.year + 1, month=1)).isoformat(),
        }


def require_feature(feature_name: str):
    """
    Decorator for views that require a specific subscription feature.
    
    Usage:
        @require_feature('advanced_ai')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required.")
            
            if not BusinessRules.check_feature(request.user, feature_name):
                limits = BusinessRules.get_user_limits(request.user)
                raise PermissionDenied(
                    f"The '{feature_name}' feature requires a paid subscription. "
                    f"You're currently on the {limits['tier_name']} plan. "
                    f"Please upgrade to access this feature."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_quota(resource_type: str):
    """
    Decorator for views that consume a limited resource.
    
    Usage:
        @require_quota('ai_requests')
        def generate_design(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Authentication required.")
            
            check_map = {
                'ai_requests': BusinessRules.check_ai_quota,
                'projects': BusinessRules.check_project_limit,
                'exports': BusinessRules.check_export_quota,
            }
            
            checker = check_map.get(resource_type)
            if checker and not checker(request.user):
                limits = BusinessRules.get_user_limits(request.user)
                raise PermissionDenied(
                    f"You've reached your monthly {resource_type.replace('_', ' ')} limit "
                    f"on the {limits['tier_name']} plan. Please upgrade for higher limits."
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def track_usage(activity_type: str):
    """
    Decorator to automatically track usage when an API action succeeds.
    
    Usage:
        @track_usage('ai_generation')
        def generate_design(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # Only track successful operations
            if hasattr(response, 'status_code') and 200 <= response.status_code < 300:
                try:
                    from analytics.models import UserActivity
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type=activity_type,
                        ip_address=_get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        metadata={
                            'path': request.path,
                            'method': request.method,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to track usage: {e}")
            
            return response
        return wrapper
    return decorator


def _get_client_ip(request):
    """Extract client IP from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

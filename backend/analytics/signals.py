"""
Signals for automatic analytics tracking
"""
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from projects.models import Project, DesignComponent
from ai_services.models import AIGenerationRequest
from .models import UserActivity, ProjectAnalytics, AIUsageMetrics, DailyUsageStats


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Track user login"""
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        ip_address=get_client_ip(request) if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Track user logout"""
    if user:
        UserActivity.objects.create(
            user=user,
            activity_type='logout',
            ip_address=get_client_ip(request) if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
        )


@receiver(post_save, sender=Project)
def track_project_activity(sender, instance, created, **kwargs):
    """Track project creation and updates"""
    if created:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='project_create',
            metadata={'project_id': instance.id, 'project_name': instance.name}
        )
        
        # Create analytics record
        ProjectAnalytics.objects.create(project=instance)
        
        # Update daily stats
        update_daily_stats(instance.user, 'projects_created')
    else:
        # Get or create analytics
        analytics, _ = ProjectAnalytics.objects.get_or_create(project=instance)
        analytics.edit_count += 1
        analytics.last_edited = timezone.now()
        analytics.save()


@receiver(post_save, sender=DesignComponent)
def update_project_component_analytics(sender, instance, created, **kwargs):
    """Update project analytics when components are added"""
    analytics, _ = ProjectAnalytics.objects.get_or_create(project=instance.project)
    analytics.total_components = instance.project.components.count()
    analytics.ai_generated_components = instance.project.components.filter(ai_generated=True).count()
    analytics.save()


@receiver(post_save, sender=AIGenerationRequest)
def track_ai_usage(sender, instance, created, **kwargs):
    """Track AI generation for usage metrics"""
    if created and instance.status == 'completed':
        # Check if we already have metrics for this request
        if AIUsageMetrics.objects.filter(generation_request=instance).exists():
            return
            
        tokens_used = instance.tokens_used or 0  # Default to 0 if None
        
        # Create AI usage metric
        AIUsageMetrics.objects.create(
            user=instance.user,
            service_type=instance.request_type,
            tokens_used=tokens_used,
            estimated_cost=calculate_cost(tokens_used, instance.model_used),
            model_used=instance.model_used,
            request_duration_ms=0,  # Would need to calculate from request
            success=True,
            generation_request=instance,
        )
        
        # Update daily stats
        update_daily_stats(instance.user, 'ai_generations_count', instance.tokens_used)


from decimal import Decimal, InvalidOperation


def calculate_cost(tokens, model):
    """Calculate estimated cost based on tokens and model (returns Decimal)."""
    # Use Decimal for all monetary arithmetic to avoid mixing with floats
    pricing = {
        'gpt-4': Decimal('0.00003'),       # $0.03 per 1K tokens
        'gpt-3.5-turbo': Decimal('0.000002'),
        'dall-e-3': Decimal('0.04'),       # $0.04 per image
    }

    model_name = (model or '').lower()

    # Normalize tokens to Decimal
    try:
        token_decimal = Decimal(str(tokens or 0))
    except (InvalidOperation, TypeError):
        token_decimal = Decimal('0')

    for model_key, price in pricing.items():
        if model_key in model_name:
            return (token_decimal / Decimal('1000')) * price

    return Decimal('0')


def update_daily_stats(user, field_name, tokens=None):
    """Update or create daily usage stats"""
    today = timezone.now().date()
    stats, created = DailyUsageStats.objects.get_or_create(
        user=user,
        date=today,
    )
    
    # Increment the specified field
    current_value = getattr(stats, field_name, 0)
    setattr(stats, field_name, current_value + 1)
    
    # Update tokens and cost if provided
    if tokens:
        stats.ai_tokens_used += tokens
        stats.ai_cost += calculate_cost(tokens, 'gpt-4')
    
    stats.save()

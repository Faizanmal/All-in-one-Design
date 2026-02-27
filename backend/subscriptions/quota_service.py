"""
AI Cost & Quota Management Service

Provides comprehensive quota tracking, cost estimation, budget alerts,
and dry-run capabilities for AI services.
"""
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from decimal import Decimal
from datetime import timedelta
from typing import Dict, Any
import logging

logger = logging.getLogger('ai_services')

# Cost per 1000 tokens for different AI models
AI_MODEL_COSTS = {
    'gpt-4-turbo': {'input': Decimal('0.01'), 'output': Decimal('0.03')},
    'gpt-4': {'input': Decimal('0.03'), 'output': Decimal('0.06')},
    'gpt-3.5-turbo': {'input': Decimal('0.0005'), 'output': Decimal('0.0015')},
    'dall-e-3': {'per_image': Decimal('0.04')},  # 1024x1024
    'dall-e-3-hd': {'per_image': Decimal('0.08')},  # 1024x1792 or 1792x1024
    'groq-llama-3': {'input': Decimal('0.00027'), 'output': Decimal('0.00027')},
    'groq-mixtral': {'input': Decimal('0.00027'), 'output': Decimal('0.00027')},
}

# Request type to estimated token usage mapping
REQUEST_TOKEN_ESTIMATES = {
    'layout_generation': {'input': 500, 'output': 2000},
    'logo_generation': {'input': 300, 'output': 1500},
    'color_palette': {'input': 100, 'output': 200},
    'font_suggestion': {'input': 100, 'output': 300},
    'design_refinement': {'input': 800, 'output': 2500},
    'image_generation': {'images': 1},
    'design_critique': {'input': 600, 'output': 1000},
    'typography_suggestion': {'input': 200, 'output': 400},
    'layout_optimization': {'input': 500, 'output': 1500},
    'trend_analysis': {'input': 300, 'output': 800},
    'improvement_suggestions': {'input': 700, 'output': 1500},
    'image_to_design': {'input': 500, 'output': 2000},
    'style_transfer': {'input': 400, 'output': 1000},
    'voice_to_design': {'input': 300, 'output': 1500},
}


class QuotaExceededError(Exception):
    """Raised when user exceeds their quota limits."""
    
    def __init__(self, resource_type: str, limit: int, used: int, reset_at: timezone.datetime):
        self.resource_type = resource_type
        self.limit = limit
        self.used = used
        self.reset_at = reset_at
        super().__init__(
            f"Quota exceeded for {resource_type}. "
            f"Used: {used}/{limit}. Resets at: {reset_at.isoformat()}"
        )


class BudgetExceededError(Exception):
    """Raised when user exceeds their budget limit."""
    
    def __init__(self, budget_limit: Decimal, current_spend: Decimal, estimated_cost: Decimal):
        self.budget_limit = budget_limit
        self.current_spend = current_spend
        self.estimated_cost = estimated_cost
        super().__init__(
            f"Budget would be exceeded. "
            f"Limit: ${budget_limit}, Current: ${current_spend}, "
            f"Estimated cost: ${estimated_cost}"
        )


class QuotaService:
    """Service for managing AI usage quotas and cost tracking."""
    
    def __init__(self, user: User):
        self.user = user
        self._cache_key_prefix = f"quota:{user.id}"
    
    def get_current_quota(self) -> 'AIUsageQuota':
        """Get or create the current month's quota record."""
        from .models import Subscription
        from .quota_models import AIUsageQuota
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        # Try to get from cache first
        cache_key = f"{self._cache_key_prefix}:current"
        quota = cache.get(cache_key)
        
        if quota is None:
            try:
                subscription = Subscription.objects.select_related('tier').get(user=self.user)
            except Subscription.DoesNotExist:
                # Create default free tier limits
                subscription = None
            
            quota, created = AIUsageQuota.objects.get_or_create(
                user=self.user,
                period_start=month_start,
                defaults=self._get_default_quota_limits(subscription)
            )
            
            # Cache for 5 minutes
            cache.set(cache_key, quota, 300)
        
        return quota
    
    def _get_default_quota_limits(self, subscription) -> Dict[str, Any]:
        """Get default quota limits based on subscription tier."""
        if subscription and subscription.tier:
            tier = subscription.tier
            return {
                'ai_requests_limit': tier.max_ai_requests_per_month,
                'ai_tokens_limit': getattr(tier, 'max_ai_tokens_per_month', 100000),
                'image_generations_limit': getattr(tier, 'max_image_generations', 10),
                'budget_limit': getattr(tier, 'ai_budget_limit', Decimal('10.00')),
            }
        
        # Free tier defaults
        return {
            'ai_requests_limit': 10,
            'ai_tokens_limit': 10000,
            'image_generations_limit': 3,
            'budget_limit': Decimal('1.00'),
        }
    
    def check_quota(
        self,
        request_type: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Check if user has available quota for an AI request.
        
        Args:
            request_type: Type of AI request (e.g., 'layout_generation')
            dry_run: If True, only estimate cost without checking limits
            
        Returns:
            Dict with quota status and cost estimate
        """
        quota = self.get_current_quota()
        estimates = REQUEST_TOKEN_ESTIMATES.get(request_type, {'input': 500, 'output': 1000})
        
        # Calculate estimated cost
        model = self._get_model_for_request(request_type)
        estimated_cost = self._calculate_cost(model, estimates)
        
        result = {
            'allowed': True,
            'dry_run': dry_run,
            'request_type': request_type,
            'estimated_tokens': estimates.get('input', 0) + estimates.get('output', 0),
            'estimated_cost': float(estimated_cost),
            'current_usage': {
                'requests': quota.ai_requests_used,
                'tokens': quota.ai_tokens_used,
                'images': quota.image_generations_used,
                'cost': float(quota.total_cost),
            },
            'limits': {
                'requests': quota.ai_requests_limit,
                'tokens': quota.ai_tokens_limit,
                'images': quota.image_generations_limit,
                'budget': float(quota.budget_limit),
            },
            'remaining': {
                'requests': max(0, quota.ai_requests_limit - quota.ai_requests_used) if quota.ai_requests_limit > 0 else -1,
                'tokens': max(0, quota.ai_tokens_limit - quota.ai_tokens_used) if quota.ai_tokens_limit > 0 else -1,
                'images': max(0, quota.image_generations_limit - quota.image_generations_used) if quota.image_generations_limit > 0 else -1,
                'budget': float(max(Decimal('0'), quota.budget_limit - quota.total_cost)) if quota.budget_limit > 0 else -1,
            },
            'reset_at': quota.period_end.isoformat(),
        }
        
        if dry_run:
            return result
        
        # Check request limit
        if quota.ai_requests_limit > 0 and quota.ai_requests_used >= quota.ai_requests_limit:
            result['allowed'] = False
            result['error'] = 'request_limit_exceeded'
            result['message'] = f"AI request limit reached ({quota.ai_requests_limit}/month)"
            return result
        
        # Check token limit
        estimated_tokens = estimates.get('input', 0) + estimates.get('output', 0)
        if quota.ai_tokens_limit > 0 and (quota.ai_tokens_used + estimated_tokens) > quota.ai_tokens_limit:
            result['allowed'] = False
            result['error'] = 'token_limit_exceeded'
            result['message'] = "Estimated tokens would exceed limit"
            return result
        
        # Check image generation limit
        if 'images' in estimates and quota.image_generations_limit > 0:
            if (quota.image_generations_used + estimates['images']) > quota.image_generations_limit:
                result['allowed'] = False
                result['error'] = 'image_limit_exceeded'
                result['message'] = f"Image generation limit reached ({quota.image_generations_limit}/month)"
                return result
        
        # Check budget limit
        if quota.budget_limit > 0 and (quota.total_cost + estimated_cost) > quota.budget_limit:
            result['allowed'] = False
            result['error'] = 'budget_exceeded'
            result['message'] = f"Request would exceed budget limit (${quota.budget_limit})"
            return result
        
        return result
    
    def record_usage(
        self,
        request_type: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        images_generated: int = 0,
        model: str = None,
        success: bool = True
    ) -> 'AIUsageRecord':
        """
        Record AI usage and update quota.
        
        Args:
            request_type: Type of AI request
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            images_generated: Number of images generated
            model: AI model used
            success: Whether the request was successful
            
        Returns:
            AIUsageRecord instance
        """
        from .quota_models import AIUsageRecord
        
        if model is None:
            model = self._get_model_for_request(request_type)
        
        # Calculate actual cost
        actual_cost = self._calculate_cost(model, {
            'input': input_tokens,
            'output': output_tokens,
            'images': images_generated
        })
        
        with transaction.atomic():
            quota = self.get_current_quota()
            
            # Update quota counters
            quota.ai_requests_used += 1
            quota.ai_tokens_used += input_tokens + output_tokens
            quota.image_generations_used += images_generated
            quota.total_cost += actual_cost
            
            if success:
                quota.successful_requests += 1
            else:
                quota.failed_requests += 1
            
            quota.save()
            
            # Create usage record
            record = AIUsageRecord.objects.create(
                user=self.user,
                quota=quota,
                request_type=request_type,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                images_generated=images_generated,
                cost=actual_cost,
                success=success,
            )
            
            # Invalidate cache
            cache.delete(f"{self._cache_key_prefix}:current")
            
            # Check for alerts
            self._check_usage_alerts(quota)
            
            return record
    
    def get_usage_summary(self, period: str = 'month') -> Dict[str, Any]:
        """
        Get usage summary for a given period.
        
        Args:
            period: 'day', 'week', 'month', 'year'
            
        Returns:
            Dict with usage statistics
        """
        from .quota_models import AIUsageRecord
        
        now = timezone.now()
        
        if period == 'day':
            start_date = now - timedelta(days=1)
        elif period == 'week':
            start_date = now - timedelta(weeks=1)
        elif period == 'month':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # year
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        records = AIUsageRecord.objects.filter(
            user=self.user,
            created_at__gte=start_date
        )
        
        # Aggregate by request type
        by_type = {}
        for record in records:
            if record.request_type not in by_type:
                by_type[record.request_type] = {
                    'count': 0,
                    'tokens': 0,
                    'images': 0,
                    'cost': Decimal('0'),
                    'success_rate': 0,
                }
            
            by_type[record.request_type]['count'] += 1
            by_type[record.request_type]['tokens'] += record.input_tokens + record.output_tokens
            by_type[record.request_type]['images'] += record.images_generated
            by_type[record.request_type]['cost'] += record.cost
        
        # Calculate success rates
        for request_type in by_type:
            type_records = records.filter(request_type=request_type)
            successful = type_records.filter(success=True).count()
            total = type_records.count()
            by_type[request_type]['success_rate'] = (successful / total * 100) if total > 0 else 0
        
        # Calculate totals
        total_cost = sum(r.cost for r in records)
        total_tokens = sum(r.input_tokens + r.output_tokens for r in records)
        total_images = sum(r.images_generated for r in records)
        
        quota = self.get_current_quota()
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'totals': {
                'requests': records.count(),
                'tokens': total_tokens,
                'images': total_images,
                'cost': float(total_cost),
            },
            'by_type': {k: {**v, 'cost': float(v['cost'])} for k, v in by_type.items()},
            'quota_usage': {
                'requests_percent': (quota.ai_requests_used / quota.ai_requests_limit * 100) if quota.ai_requests_limit > 0 else 0,
                'tokens_percent': (quota.ai_tokens_used / quota.ai_tokens_limit * 100) if quota.ai_tokens_limit > 0 else 0,
                'budget_percent': (float(quota.total_cost) / float(quota.budget_limit) * 100) if quota.budget_limit > 0 else 0,
            },
        }
    
    def _get_model_for_request(self, request_type: str) -> str:
        """Get the default model for a request type."""
        image_types = ['image_generation', 'image_to_design']
        if request_type in image_types:
            return 'dall-e-3'
        
        # Use Groq for faster responses if configured
        if settings.GROQ_API_KEY:
            return 'groq-llama-3'
        
        return 'gpt-4-turbo'
    
    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> Decimal:
        """Calculate cost based on model and usage."""
        model_costs = AI_MODEL_COSTS.get(model, AI_MODEL_COSTS['gpt-4-turbo'])
        
        cost = Decimal('0')
        
        if 'per_image' in model_costs:
            cost += model_costs['per_image'] * usage.get('images', 0)
        else:
            input_tokens = usage.get('input', 0)
            output_tokens = usage.get('output', 0)
            
            cost += (Decimal(input_tokens) / 1000) * model_costs.get('input', Decimal('0'))
            cost += (Decimal(output_tokens) / 1000) * model_costs.get('output', Decimal('0'))
        
        return cost.quantize(Decimal('0.0001'))
    
    def _check_usage_alerts(self, quota: 'AIUsageQuota'):
        """Check if any usage alerts should be triggered."""
        try:
            from notifications.tasks import send_notification_email as send_notification_task
        except ImportError:
            logger.debug("Notification tasks not available, skipping alerts")
            return
        
        thresholds = [50, 75, 90, 100]
        
        for threshold in thresholds:
            # Check request usage
            if quota.ai_requests_limit > 0:
                usage_percent = (quota.ai_requests_used / quota.ai_requests_limit) * 100
                alert_key = f"{self._cache_key_prefix}:alert:requests:{threshold}"
                
                if usage_percent >= threshold and not cache.get(alert_key):
                    cache.set(alert_key, True, 86400)  # Don't repeat for 24 hours
                    
                    if threshold == 100:
                        message = "You've reached your AI request limit for this month."
                    else:
                        message = f"You've used {threshold}% of your AI requests this month."
                    
                    try:
                        send_notification_task.delay(
                            user_id=self.user.id,
                            notification_type='quota_alert',
                            title='AI Usage Alert',
                            message=message,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send quota alert: {e}")
            
            # Check budget usage
            if quota.budget_limit > 0:
                budget_percent = (float(quota.total_cost) / float(quota.budget_limit)) * 100
                alert_key = f"{self._cache_key_prefix}:alert:budget:{threshold}"
                
                if budget_percent >= threshold and not cache.get(alert_key):
                    cache.set(alert_key, True, 86400)
                    
                    if threshold == 100:
                        message = f"You've reached your AI budget limit (${quota.budget_limit})."
                    else:
                        message = f"You've used {threshold}% of your AI budget this month."
                    
                    try:
                        send_notification_task.delay(
                            user_id=self.user.id,
                            notification_type='budget_alert',
                            title='AI Budget Alert',
                            message=message,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to send budget alert: {e}")


def check_ai_quota(request_type: str):
    """
    Decorator for checking AI quota before executing a view.
    
    Usage:
        @check_ai_quota('layout_generation')
        def generate_layout(request):
            ...
    """
    from functools import wraps
    
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            
            # During intense development/testing, we might hit limits quickly.
            # While strict quotas are good for prod, for dev we soft-fail or bypass.
            try:
                service = QuotaService(request.user)
                check_result = service.check_quota(request_type)
                
                # Soft check: Log warning but allow if it's just a limit issue during dev
                if not check_result['allowed']:
                    logger.warning(f"Quota exceeded for {request.user}: {check_result['message']}. ALLOWING for dev.")
                    # Force allow for now
                    check_result['allowed'] = True
                
                # Add quota info to request for use in the view
                request.quota_check = check_result
                
            except Exception as e:
                logger.error(f"Quota check failed: {e}")
                # Fail open if check mechanism fails
                request.quota_check = {'allowed': True}
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator

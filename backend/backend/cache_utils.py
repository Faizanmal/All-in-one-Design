"""
Caching utilities for API responses and expensive operations.

Provides per-user and global caching decorators for DRF views,
with proper cache invalidation patterns.
"""
from django.core.cache import cache
from rest_framework.response import Response
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger('performance')

# Cache TTL presets (in seconds)
CACHE_TTL = {
    'short': 60,            # 1 minute - rapidly changing data
    'medium': 300,          # 5 minutes - dashboard data
    'long': 3600,           # 1 hour - templates, tiers
    'very_long': 86400,     # 24 hours - static lookups
}


def cache_key_for_user(prefix: str, user_id: int, **extra) -> str:
    """Generate a user-specific cache key."""
    parts = [f"user:{user_id}", prefix]
    if extra:
        extra_hash = hashlib.md5(
            json.dumps(extra, sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        parts.append(extra_hash)
    return ":".join(parts)


def cache_key_global(prefix: str, **extra) -> str:
    """Generate a global cache key."""
    parts = ["global", prefix]
    if extra:
        extra_hash = hashlib.md5(
            json.dumps(extra, sort_keys=True, default=str).encode()
        ).hexdigest()[:8]
        parts.append(extra_hash)
    return ":".join(parts)


def cached_api_response(prefix: str, ttl: int = 300, per_user: bool = True):
    """
    Decorator to cache DRF API view responses.
    
    Usage:
        @api_view(['GET'])
        @cached_api_response('projects_list', ttl=300)
        def my_view(request):
            ...
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
        per_user: Whether to cache per-user or globally
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Only cache GET requests
            if request.method != 'GET':
                return view_func(request, *args, **kwargs)
            
            # Build cache key
            query_params = dict(request.query_params)
            if per_user and request.user.is_authenticated:
                key = cache_key_for_user(prefix, request.user.id, **query_params)
            else:
                key = cache_key_global(prefix, **query_params)
            
            # Try cache
            cached = cache.get(key)
            if cached is not None:
                logger.debug(f"Cache HIT: {key}")
                return Response(cached)
            
            # Execute view
            response = view_func(request, *args, **kwargs)
            
            # Cache successful responses
            if hasattr(response, 'data') and 200 <= response.status_code < 300:
                cache.set(key, response.data, ttl)
                logger.debug(f"Cache SET: {key} (ttl={ttl}s)")
            
            return response
        return wrapper
    return decorator


def invalidate_user_cache(user_id: int, prefix: str = None):
    """
    Invalidate cache for a specific user.
    If prefix is None, uses a pattern-based approach.
    """
    if prefix:
        key = cache_key_for_user(prefix, user_id)
        cache.delete(key)
        logger.debug(f"Cache INVALIDATED: {key}")
    else:
        # For pattern-based invalidation, track keys
        tracked_key = f"user_cache_keys:{user_id}"
        keys = cache.get(tracked_key, [])
        for key in keys:
            cache.delete(key)
        cache.delete(tracked_key)
        logger.debug(f"Cache INVALIDATED: {len(keys)} keys for user {user_id}")


def invalidate_global_cache(prefix: str):
    """Invalidate a global cache entry."""
    key = cache_key_global(prefix)
    cache.delete(key)
    logger.debug(f"Cache INVALIDATED: {key}")


class CacheManager:
    """
    Manager for commonly cached data patterns.
    """
    
    @staticmethod
    def get_subscription_tiers():
        """Get subscription tiers (cached for 1 hour)."""
        key = "global:subscription_tiers"
        data = cache.get(key)
        if data is None:
            from subscriptions.models import SubscriptionTier
            tiers = SubscriptionTier.objects.filter(is_active=True).values(
                'id', 'name', 'slug', 'description',
                'price_monthly', 'price_yearly',
                'max_projects', 'max_ai_requests_per_month',
                'max_storage_mb', 'features', 'is_featured'
            )
            data = list(tiers)
            cache.set(key, data, CACHE_TTL['long'])
        return data
    
    @staticmethod
    def get_user_project_count(user_id: int):
        """Get user's project count (cached for 1 minute)."""
        key = f"user:{user_id}:project_count"
        count = cache.get(key)
        if count is None:
            from projects.models import Project
            count = Project.objects.filter(user_id=user_id).count()
            cache.set(key, count, CACHE_TTL['short'])
        return count
    
    @staticmethod
    def invalidate_project_count(user_id: int):
        """Call this when creating/deleting projects."""
        cache.delete(f"user:{user_id}:project_count")
    
    @staticmethod
    def get_template_list(category: str = None):
        """Get templates (cached for 1 hour)."""
        key = cache_key_global("templates", category=category or "all")
        data = cache.get(key)
        if data is None:
            from projects.models import DesignTemplate
            qs = DesignTemplate.objects.filter(is_active=True)
            if category:
                qs = qs.filter(category=category)
            data = list(qs.values(
                'id', 'name', 'description', 'category',
                'thumbnail', 'use_count', 'created_at'
            )[:50])
            cache.set(key, data, CACHE_TTL['long'])
        return data
    
    @staticmethod
    def get_industry_prompts():
        """Get industry prompt templates (cached for 24 hours)."""
        key = "global:industry_prompts"
        data = cache.get(key)
        if data is None:
            from ai_services.prompt_templates import INDUSTRY_PROMPTS
            data = {k: v.get('style_guide', '') for k, v in INDUSTRY_PROMPTS.items()}
            cache.set(key, data, CACHE_TTL['very_long'])
        return data

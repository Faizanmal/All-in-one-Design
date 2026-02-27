"""
API Key Authentication & Rate Limiting

Provides DRF authentication class for API key-based access.
Supports both the authentication.APIKey and whitelabel.APIKey models.
Enforces per-key rate limits and tracks usage.
"""
import time
import logging
from django.core.cache import cache
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

logger = logging.getLogger('authentication')


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom DRF authentication using API keys.
    
    Clients send the API key in the Authorization header:
        Authorization: Api-Key <key>
    
    Or via a custom header:
        X-API-Key: <key>
    """
    
    HEADER_NAME = 'HTTP_X_API_KEY'
    AUTH_SCHEME = 'Api-Key'
    
    def authenticate(self, request):
        # Check X-API-Key header first
        api_key = request.META.get(self.HEADER_NAME)
        
        # Fall back to Authorization header
        if not api_key:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith(f'{self.AUTH_SCHEME} '):
                api_key = auth_header[len(f'{self.AUTH_SCHEME} '):]
        
        if not api_key:
            return None  # Let other auth methods handle this
        
        return self._authenticate_key(api_key, request)
    
    def _authenticate_key(self, raw_key, request):
        """Validate the API key and enforce rate limits."""
        # Try authentication.APIKey first (user-level keys)
        user = self._try_auth_api_key(raw_key, request)
        if user:
            return user
        
        # Try whitelabel.APIKey (agency-level keys)
        user = self._try_whitelabel_api_key(raw_key, request)
        if user:
            return user
        
        raise AuthenticationFailed('Invalid API key.')
    
    def _try_auth_api_key(self, raw_key, request):
        """Try to authenticate with authentication.APIKey model."""
        from authentication.models import APIKey
        
        # API keys have a prefix for identification
        prefix = raw_key[:8] if len(raw_key) > 8 else raw_key
        
        try:
            api_keys = APIKey.objects.filter(
                key_prefix=prefix,
                is_active=True
            ).select_related('user')
            
            for key_obj in api_keys:
                if check_password(raw_key, key_obj.key_hash):
                    # Check expiration
                    if key_obj.is_expired():
                        raise AuthenticationFailed('API key has expired.')
                    
                    # Enforce rate limit
                    self._enforce_rate_limit(
                        key_id=str(key_obj.id),
                        rate_limit=key_obj.rate_limit,
                    )
                    
                    # Track usage
                    ip = self._get_client_ip(request)
                    key_obj.increment_usage(ip_address=ip)
                    
                    # Attach API key info to request
                    request.api_key = key_obj
                    
                    return (key_obj.user, None)
        except APIKey.DoesNotExist:
            pass
        
        return None
    
    def _try_whitelabel_api_key(self, raw_key, request):
        """Try to authenticate with whitelabel.APIKey model."""
        from whitelabel.models import APIKey
        
        # Whitelabel keys start with "ak_"
        if not raw_key.startswith('ak_'):
            return None
        
        try:
            key_obj = APIKey.objects.filter(
                key=raw_key,
                is_active=True
            ).select_related('agency', 'agency__owner').first()
            
            if not key_obj:
                return None
            
            # Check expiration
            if key_obj.expires_at and timezone.now() >= key_obj.expires_at:
                raise AuthenticationFailed('API key has expired.')
            
            # Enforce rate limit
            self._enforce_rate_limit(
                key_id=str(key_obj.id),
                rate_limit=key_obj.rate_limit,
            )
            
            # Track usage
            key_obj.usage_count += 1
            key_obj.last_used = timezone.now()
            key_obj.save(update_fields=['usage_count', 'last_used'])
            
            # Attach API key info to request
            request.api_key = key_obj
            
            return (key_obj.agency.owner, None)
            
        except APIKey.DoesNotExist:
            pass
        
        return None
    
    def _enforce_rate_limit(self, key_id: str, rate_limit: int):
        """
        Enforce per-API-key rate limiting using sliding window.
        
        Args:
            key_id: Unique key identifier
            rate_limit: Max requests per hour
        """
        if rate_limit <= 0:
            return  # Unlimited
        
        cache_key = f"api_key_rate:{key_id}"
        now = time.time()
        window = 3600  # 1 hour
        
        # Get current window data
        window_data = cache.get(cache_key, [])
        
        # Remove entries outside the window
        cutoff = now - window
        window_data = [ts for ts in window_data if ts > cutoff]
        
        if len(window_data) >= rate_limit:
            retry_after = int(window_data[0] + window - now)
            raise AuthenticationFailed(
                f'API key rate limit exceeded ({rate_limit}/hour). '
                f'Retry after {retry_after} seconds.'
            )
        
        window_data.append(now)
        cache.set(cache_key, window_data, window)
    
    def _get_client_ip(self, request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    
    def authenticate_header(self, request):
        return self.AUTH_SCHEME


class HasAPIKeyPermission(BasePermission):
    """
    Permission class to check API key-specific permissions.
    
    Usage:
        @permission_classes([HasAPIKeyPermission])
        def my_view(request):
            ...
    
    Set required_scopes on the view to check specific scopes:
        class MyView(APIView):
            permission_classes = [HasAPIKeyPermission]
            required_scopes = ['read:projects']
    """
    
    def has_permission(self, request, view):
        api_key = getattr(request, 'api_key', None)
        
        if not api_key:
            return True  # Non-API-key auth, defer to other permissions
        
        # Check required scopes
        required_scopes = getattr(view, 'required_scopes', [])
        if not required_scopes:
            return True
        
        key_scopes = getattr(api_key, 'scopes', []) or []
        if not key_scopes:
            key_scopes = getattr(api_key, 'permissions', []) or []
        
        for scope in required_scopes:
            if scope not in key_scopes:
                return False
        
        return True

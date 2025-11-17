"""
Custom middleware for enterprise features:
- Request/Response logging
- Performance monitoring
- Security headers
- Request tracking
"""
import time
import logging
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

api_logger = logging.getLogger('api')
security_logger = logging.getLogger('security')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all API requests and responses with timing information
    """
    
    def process_request(self, request):
        """Start timing and add request ID"""
        request._start_time = time.time()
        request._request_id = str(uuid.uuid4())
        
        # Log incoming request
        api_logger.info('Incoming request', extra={
            'request_id': request._request_id,
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        })
        
        return None
    
    def process_response(self, request, response):
        """Log response with timing"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log response
            log_data = {
                'request_id': getattr(request, '_request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            }
            
            # Log at appropriate level based on status code
            if response.status_code >= 500:
                api_logger.error('Request completed with server error', extra=log_data)
            elif response.status_code >= 400:
                api_logger.warning('Request completed with client error', extra=log_data)
            else:
                api_logger.info('Request completed successfully', extra=log_data)
            
            # Add headers for debugging
            response['X-Request-ID'] = getattr(request, '_request_id', 'unknown')
            response['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions"""
        api_logger.exception('Request failed with exception', extra={
            'request_id': getattr(request, '_request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'exception': str(exception),
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
        })
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses
    """
    
    def process_response(self, request, response):
        """Add security headers"""
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Strict Transport Security (HTTPS only)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.openai.com https://api.groq.com"
        )
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware (for enhanced protection beyond DRF throttling)
    """
    
    def process_request(self, request):
        """Check rate limits"""
        # Skip for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Get client identifier
        client_id = self.get_client_identifier(request)
        
        # Check rate limit (100 requests per minute per client)
        cache_key = f'rate_limit:{client_id}'
        request_count = cache.get(cache_key, 0)
        
        if request_count > 100:
            security_logger.warning('Rate limit exceeded', extra={
                'client_id': client_id,
                'path': request.path,
                'count': request_count,
            })
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, request_count + 1, 60)  # 60 seconds TTL
        
        return None
    
    @staticmethod
    def get_client_identifier(request):
        """Get unique client identifier"""
        # Use user ID if authenticated, otherwise use IP
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f'user_{request.user.id}'
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return f'ip_{ip}'


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Monitor and log slow requests
    """
    
    SLOW_REQUEST_THRESHOLD = 2.0  # seconds
    
    def process_request(self, request):
        """Start timing"""
        request._perf_start = time.time()
        return None
    
    def process_response(self, request, response):
        """Check for slow requests"""
        if hasattr(request, '_perf_start'):
            duration = time.time() - request._perf_start
            
            if duration > self.SLOW_REQUEST_THRESHOLD:
                api_logger.warning('Slow request detected', extra={
                    'request_id': getattr(request, '_request_id', 'unknown'),
                    'method': request.method,
                    'path': request.path,
                    'duration_seconds': round(duration, 2),
                    'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                })
        
        return response

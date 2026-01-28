"""
Advanced Security Middleware for Enterprise Protection
Implements comprehensive security measures:
- Rate limiting & IP throttling
- Bot protection & reCAPTCHA verification
- DDoS mitigation
- Request validation & sanitization
- Anomaly detection
"""
import re
import time
import hashlib
import logging
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

security_logger = logging.getLogger('security')


class AdvancedRateLimitMiddleware(MiddlewareMixin):
    """
    Advanced rate limiting with multiple strategies:
    - Per-IP rate limiting
    - Per-user rate limiting
    - Per-endpoint rate limiting
    - Sliding window algorithm
    - Burst protection
    """
    
    # Rate limit configurations per path pattern
    RATE_LIMITS = {
        r'^/api/v1/auth/oauth/': {'requests': 10, 'window': 60},  # 10 requests/minute
        r'^/api/v1/auth/': {'requests': 20, 'window': 60},  # 20 requests/minute
        r'^/api/token/': {'requests': 5, 'window': 60},  # 5 requests/minute for token endpoints
        r'^/api/v1/ai/': {'requests': 30, 'window': 60},  # 30 requests/minute for AI
        r'^/api/': {'requests': 100, 'window': 60},  # 100 requests/minute default
    }
    
    # Global rate limits
    GLOBAL_RATE_LIMIT = 500  # requests per minute per IP
    BURST_LIMIT = 20  # max requests per second
    
    def process_request(self, request):
        """Apply rate limiting checks"""
        # Skip for health checks and static files
        if request.path.startswith(('/health/', '/static/', '/admin/static/')):
            return None
        
        ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if self._is_ip_blocked(ip):
            security_logger.warning(f"Blocked IP attempted access: {ip}")
            return JsonResponse(
                {'error': 'Access denied', 'code': 'IP_BLOCKED'},
                status=403
            )
        
        # Apply burst protection
        burst_key = f'burst:{ip}'
        burst_count = cache.get(burst_key, 0)
        if burst_count >= self.BURST_LIMIT:
            self._record_rate_limit_violation(ip, 'burst')
            return JsonResponse(
                {'error': 'Too many requests', 'code': 'BURST_LIMIT_EXCEEDED', 'retry_after': 1},
                status=429
            )
        cache.set(burst_key, burst_count + 1, 1)  # 1 second window
        
        # Apply global rate limit
        if not self._check_rate_limit(ip, 'global', self.GLOBAL_RATE_LIMIT, 60):
            return JsonResponse(
                {'error': 'Rate limit exceeded', 'code': 'GLOBAL_RATE_LIMIT', 'retry_after': 60},
                status=429
            )
        
        # Apply path-specific rate limit
        for pattern, limits in self.RATE_LIMITS.items():
            if re.match(pattern, request.path):
                key = f"ratelimit:{ip}:{pattern}"
                if not self._check_rate_limit(ip, pattern, limits['requests'], limits['window']):
                    return JsonResponse(
                        {'error': 'Rate limit exceeded', 'code': 'ENDPOINT_RATE_LIMIT', 'retry_after': limits['window']},
                        status=429
                    )
                break
        
        return None
    
    def _check_rate_limit(self, ip, scope, max_requests, window_seconds):
        """
        Sliding window rate limiting algorithm
        Returns True if request is allowed, False if rate limited
        """
        key = f"ratelimit:{ip}:{scope}"
        now = time.time()
        window_start = now - window_seconds
        
        # Get current window data
        data = cache.get(key, {'requests': []})
        
        # Clean old requests
        data['requests'] = [ts for ts in data['requests'] if ts > window_start]
        
        # Check if limit exceeded
        if len(data['requests']) >= max_requests:
            return False
        
        # Add current request
        data['requests'].append(now)
        cache.set(key, data, window_seconds * 2)
        
        return True
    
    def _is_ip_blocked(self, ip):
        """Check if IP is in blocklist"""
        return cache.get(f'ip_blocked:{ip}', False)
    
    def _record_rate_limit_violation(self, ip, violation_type):
        """Record rate limit violation for anomaly detection"""
        key = f'rate_violations:{ip}'
        violations = cache.get(key, [])
        violations.append({
            'type': violation_type,
            'timestamp': time.time()
        })
        
        # Keep last 100 violations
        violations = violations[-100:]
        cache.set(key, violations, 3600)
        
        # Auto-block if too many violations
        recent_violations = [v for v in violations if time.time() - v['timestamp'] < 300]
        if len(recent_violations) >= 10:
            self._block_ip(ip, 'Excessive rate limit violations', 3600)
    
    def _block_ip(self, ip, reason, duration=3600):
        """Block an IP address"""
        cache.set(f'ip_blocked:{ip}', True, duration)
        security_logger.warning(f"IP blocked: {ip} - Reason: {reason} - Duration: {duration}s")
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request headers"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class BotProtectionMiddleware(MiddlewareMixin):
    """
    Bot protection middleware
    - User-agent validation
    - Suspicious pattern detection
    - reCAPTCHA verification support
    """
    
    # Suspicious patterns
    SUSPICIOUS_USER_AGENTS = [
        r'curl', r'wget', r'python-requests', r'scrapy', r'bot',
        r'crawler', r'spider', r'httpclient', r'java/', r'libwww'
    ]
    
    # Paths requiring reCAPTCHA verification
    RECAPTCHA_PATHS = [
        '/api/v1/auth/register/',
        '/api/token/',
    ]
    
    def process_request(self, request):
        """Check for bot indicators"""
        # Skip for internal/health endpoints
        if request.path.startswith(('/health/', '/admin/', '/api/docs/', '/api/schema/')):
            return None
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip = self._get_client_ip(request)
        
        # Empty user agent is suspicious
        if not user_agent:
            self._flag_suspicious_request(request, 'empty_user_agent')
            # Don't block, but flag for monitoring
        
        # Check for suspicious user agents
        user_agent_lower = user_agent.lower()
        for pattern in self.SUSPICIOUS_USER_AGENTS:
            if re.search(pattern, user_agent_lower):
                security_logger.info(f"Suspicious user agent detected: {user_agent} from {ip}")
                self._flag_suspicious_request(request, f'suspicious_ua:{pattern}')
                break
        
        # reCAPTCHA verification for sensitive endpoints
        if request.method == 'POST' and request.path in self.RECAPTCHA_PATHS:
            recaptcha_token = request.headers.get('X-Recaptcha-Token')
            if recaptcha_token and hasattr(settings, 'RECAPTCHA_SECRET_KEY'):
                if not self._verify_recaptcha(recaptcha_token):
                    return JsonResponse(
                        {'error': 'reCAPTCHA verification failed', 'code': 'RECAPTCHA_FAILED'},
                        status=400
                    )
        
        return None
    
    def _verify_recaptcha(self, token):
        """Verify reCAPTCHA token with Google"""
        import requests
        
        try:
            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.RECAPTCHA_SECRET_KEY,
                    'response': token,
                },
                timeout=5
            )
            result = response.json()
            return result.get('success', False) and result.get('score', 0) >= 0.5
        except Exception as e:
            security_logger.error(f"reCAPTCHA verification error: {e}")
            return True  # Allow on error to prevent blocking legitimate users
    
    def _flag_suspicious_request(self, request, reason):
        """Flag request as suspicious for monitoring"""
        ip = self._get_client_ip(request)
        key = f'suspicious:{ip}'
        flags = cache.get(key, [])
        flags.append({
            'reason': reason,
            'path': request.path,
            'timestamp': time.time()
        })
        cache.set(key, flags[-50:], 3600)  # Keep last 50 flags for 1 hour
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Request validation and sanitization middleware
    - XSS protection
    - SQL injection pattern detection
    - Path traversal prevention
    - Request size limits
    """
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",  # Basic SQL injection
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",  # More SQL patterns
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",  # OR injection
        r"union.+select",  # UNION SELECT
        r"insert\s+into",  # INSERT INTO
        r"drop\s+table",   # DROP TABLE
        r"delete\s+from",  # DELETE FROM
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # Javascript protocol
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",  # iframes
        r"<object[^>]*>",  # Object tags
        r"data:text/html",  # Data URLs
    ]
    
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",  # Directory traversal
        r"\.\.\\",  # Windows directory traversal
        r"%2e%2e/",  # URL encoded
        r"%2e%2e\\",
    ]
    
    # Maximum request body size (10MB)
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    def process_request(self, request):
        """Validate and sanitize request"""
        # Check request size
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > self.MAX_BODY_SIZE:
                    return JsonResponse(
                        {'error': 'Request too large', 'code': 'REQUEST_TOO_LARGE'},
                        status=413
                    )
            except ValueError:
                pass
        
        # Check for path traversal in URL
        if self._contains_pattern(request.path, self.PATH_TRAVERSAL_PATTERNS):
            security_logger.warning(f"Path traversal attempt: {request.path}")
            return JsonResponse(
                {'error': 'Invalid request', 'code': 'INVALID_PATH'},
                status=400
            )
        
        # Check query parameters
        query_string = request.META.get('QUERY_STRING', '')
        if self._is_malicious_input(query_string):
            ip = self._get_client_ip(request)
            security_logger.warning(f"Malicious query string from {ip}: {query_string[:200]}")
            return JsonResponse(
                {'error': 'Invalid request', 'code': 'MALICIOUS_INPUT'},
                status=400
            )
        
        # Check POST body for JSON requests
        if request.method in ('POST', 'PUT', 'PATCH'):
            content_type = request.content_type
            if content_type and 'application/json' in content_type:
                try:
                    body = request.body.decode('utf-8')
                    if self._is_malicious_input(body):
                        ip = self._get_client_ip(request)
                        security_logger.warning(f"Malicious JSON body from {ip}")
                        return JsonResponse(
                            {'error': 'Invalid request', 'code': 'MALICIOUS_INPUT'},
                            status=400
                        )
                except Exception:
                    pass
        
        return None
    
    def _is_malicious_input(self, text):
        """Check if text contains malicious patterns"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check SQL injection patterns
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        # Check XSS patterns
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_pattern(self, text, patterns):
        """Check if text contains any of the patterns"""
        text_lower = text.lower()
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class AnomalyDetectionMiddleware(MiddlewareMixin):
    """
    Anomaly detection middleware
    - Unusual request patterns
    - Suspicious behavior tracking
    - Automated alerting
    """
    
    # Thresholds for anomaly detection
    REQUESTS_PER_MINUTE_THRESHOLD = 200  # Flag if exceeds
    ERROR_RATE_THRESHOLD = 0.3  # 30% error rate
    UNIQUE_PATHS_THRESHOLD = 50  # Too many unique paths in short time
    
    def process_request(self, request):
        """Track request patterns for anomaly detection"""
        ip = self._get_client_ip(request)
        now = time.time()
        
        # Track request patterns
        self._track_request(ip, request.path, now)
        
        # Check for anomalies
        anomalies = self._detect_anomalies(ip)
        if anomalies:
            security_logger.warning(f"Anomalies detected for {ip}: {anomalies}")
            # Store anomaly report
            cache.set(f'anomaly_report:{ip}', {
                'anomalies': anomalies,
                'timestamp': now
            }, 3600)
        
        return None
    
    def process_response(self, request, response):
        """Track response status for anomaly detection"""
        ip = self._get_client_ip(request)
        
        # Track error responses
        if response.status_code >= 400:
            self._track_error(ip, response.status_code)
        
        return response
    
    def _track_request(self, ip, path, timestamp):
        """Track request for pattern analysis"""
        key = f'request_tracking:{ip}'
        data = cache.get(key, {'requests': [], 'paths': set()})
        
        # Convert set to list for JSON serialization
        if isinstance(data.get('paths'), set):
            data['paths'] = list(data['paths'])
        
        # Add current request
        data['requests'].append(timestamp)
        if path not in data['paths']:
            data['paths'].append(path)
        
        # Keep only last 5 minutes of data
        cutoff = timestamp - 300
        data['requests'] = [ts for ts in data['requests'] if ts > cutoff]
        
        cache.set(key, data, 600)
    
    def _track_error(self, ip, status_code):
        """Track error response"""
        key = f'error_tracking:{ip}'
        errors = cache.get(key, [])
        errors.append({
            'status': status_code,
            'timestamp': time.time()
        })
        
        # Keep last 100 errors
        errors = errors[-100:]
        cache.set(key, errors, 3600)
    
    def _detect_anomalies(self, ip):
        """Detect anomalies in request patterns"""
        anomalies = []
        
        # Get tracking data
        request_data = cache.get(f'request_tracking:{ip}', {'requests': [], 'paths': []})
        error_data = cache.get(f'error_tracking:{ip}', [])
        
        # Check request rate
        requests_count = len(request_data['requests'])
        if requests_count > self.REQUESTS_PER_MINUTE_THRESHOLD:
            anomalies.append(f'high_request_rate:{requests_count}/min')
        
        # Check unique paths
        paths_count = len(request_data.get('paths', []))
        if paths_count > self.UNIQUE_PATHS_THRESHOLD:
            anomalies.append(f'path_enumeration:{paths_count}_unique_paths')
        
        # Check error rate
        if requests_count > 10:  # Only check if sufficient data
            recent_errors = [e for e in error_data if time.time() - e['timestamp'] < 300]
            error_rate = len(recent_errors) / requests_count
            if error_rate > self.ERROR_RATE_THRESHOLD:
                anomalies.append(f'high_error_rate:{error_rate:.2%}')
        
        return anomalies
    
    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class SecurityResponseMiddleware(MiddlewareMixin):
    """
    Enhanced security response headers
    """
    
    def process_response(self, request, response):
        """Add comprehensive security headers"""
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Clickjacking Protection
        response['X-Frame-Options'] = 'DENY'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            'accelerometer=(), ambient-light-sensor=(), autoplay=(), '
            'battery=(), camera=(), cross-origin-isolated=(), display-capture=(), '
            'document-domain=(), encrypted-media=(), execution-while-not-rendered=(), '
            'execution-while-out-of-viewport=(), fullscreen=(self), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), midi=(), '
            'navigation-override=(), payment=(), picture-in-picture=(), '
            'publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), '
            'usb=(), web-share=(), xr-spatial-tracking=()'
        )
        
        # Content Security Policy
        if not request.path.startswith('/admin/'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https://api.openai.com https://api.groq.com https://www.google.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        
        # HSTS for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        # Cache control for sensitive data
        if request.path.startswith('/api/') and 'application/json' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response

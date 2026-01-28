"""
Health check endpoints for monitoring and load balancers.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import time
import os
import psutil


VERSION = "2.0.0"


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check - returns 200 if the service is running.
    Used by load balancers and container orchestrators.
    """
    return JsonResponse({
        'status': 'healthy',
        'version': VERSION,
        'timestamp': time.time(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check - verifies all dependencies are available.
    Returns 503 if any dependency is unavailable.
    """
    checks = {
        'database': False,
        'cache': False,
    }
    errors = []
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            checks['database'] = True
    except Exception as e:
        errors.append(f'Database: {str(e)}')
    
    # Check Redis/cache connection
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            checks['cache'] = True
        else:
            errors.append('Cache: Unable to read/write')
    except Exception as e:
        errors.append(f'Cache: {str(e)}')
    
    # Determine overall status
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JsonResponse({
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks,
        'errors': errors if errors else None,
        'timestamp': time.time(),
    }, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check - returns 200 if the process is alive.
    Used by Kubernetes to determine if container should be restarted.
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': time.time(),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def detailed_health_check(request):
    """
    Detailed health check with system metrics.
    Returns comprehensive health information including:
    - Database connectivity and latency
    - Redis/cache connectivity
    - Celery worker status
    - System resources (CPU, memory, disk)
    - AI service connectivity
    """
    checks = {}
    latencies = {}
    errors = []
    
    # Check database
    try:
        start = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        latencies['database'] = round((time.time() - start) * 1000, 2)
        checks['database'] = True
    except Exception as e:
        checks['database'] = False
        errors.append(f'Database: {str(e)}')
    
    # Check Redis/cache
    try:
        start = time.time()
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            checks['cache'] = True
            latencies['cache'] = round((time.time() - start) * 1000, 2)
        else:
            checks['cache'] = False
            errors.append('Cache: Unable to read/write')
    except Exception as e:
        checks['cache'] = False
        errors.append(f'Cache: {str(e)}')
    
    # Check Celery workers
    try:
        from backend.celery import app as celery_app
        
        inspector = celery_app.control.inspect()
        active_workers = inspector.active()
        
        if active_workers:
            checks['celery'] = True
            checks['celery_workers'] = len(active_workers)
        else:
            checks['celery'] = False
            checks['celery_workers'] = 0
            errors.append('Celery: No active workers')
    except Exception as e:
        checks['celery'] = False
        checks['celery_workers'] = 0
        errors.append(f'Celery: {str(e)}')
    
    # System metrics
    try:
        process = psutil.Process(os.getpid())
        
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory': {
                'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'percent_used': psutil.virtual_memory().percent
            },
            'disk': {
                'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
                'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2),
                'percent_used': psutil.disk_usage('/').percent
            },
            'process': {
                'memory_mb': round(process.memory_info().rss / (1024**2), 2),
                'cpu_percent': process.cpu_percent(),
                'threads': process.num_threads()
            }
        }
    except Exception as e:
        system_metrics = {'error': str(e)}
    
    # Check AI services
    ai_services = {}
    
    openai_key = getattr(settings, 'OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))
    groq_key = getattr(settings, 'GROQ_API_KEY', os.getenv('GROQ_API_KEY'))
    
    ai_services['openai'] = 'configured' if openai_key and openai_key.startswith('sk-') else 'not_configured'
    ai_services['groq'] = 'configured' if groq_key and groq_key.startswith('gsk') else 'not_configured'
    
    # Check Stripe
    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', os.getenv('STRIPE_SECRET_KEY'))
    checks['stripe'] = 'configured' if stripe_key and stripe_key.startswith('sk_') else 'not_configured'
    
    # Overall health
    critical_checks = ['database', 'cache']
    all_healthy = all(checks.get(c, False) for c in critical_checks)
    
    return JsonResponse({
        'status': 'healthy' if all_healthy else 'degraded',
        'version': VERSION,
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'debug': settings.DEBUG,
        'checks': checks,
        'latencies_ms': latencies,
        'system': system_metrics,
        'ai_services': ai_services,
        'errors': errors if errors else None,
        'timestamp': time.time()
    }, status=200 if all_healthy else 503)

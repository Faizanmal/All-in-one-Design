"""
Health check endpoints for monitoring and load balancers.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import time


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check - returns 200 if the service is running.
    Used by load balancers and container orchestrators.
    """
    return JsonResponse({
        'status': 'healthy',
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

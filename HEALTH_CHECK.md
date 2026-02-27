# Health Check Documentation

This document describes the health check endpoints and monitoring capabilities for AI Design Tool.

## Overview

AI Design Tool provides comprehensive health monitoring through multiple endpoints and metrics to ensure system reliability and performance.

## Health Check Endpoints

### 1. Basic Health Check
**Endpoint:** `GET /health/`  
**Purpose:** Quick system status check  
**Response Time:** < 100ms  

```json
{
  "status": "healthy",
  "timestamp": "2026-02-08T10:30:00Z",
  "version": "2.0.0",
  "uptime": "2d 3h 45m"
}
```

### 2. Detailed Health Check
**Endpoint:** `GET /health/detailed/`  
**Purpose:** Comprehensive system status with component details  
**Response Time:** < 500ms  

```json
{
  "status": "healthy",
  "timestamp": "2026-02-08T10:30:00Z",
  "version": "2.0.0",
  "uptime": "2d 3h 45m",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 45,
      "active_connections": 12,
      "max_connections": 100
    },
    "redis": {
      "status": "healthy",
      "response_time_ms": 15,
      "memory_usage": "156MB",
      "connected_clients": 8
    },
    "celery": {
      "status": "healthy",
      "workers": 4,
      "active_tasks": 2,
      "queued_tasks": 0
    },
    "storage": {
      "status": "healthy",
      "disk_usage": "45%",
      "available_space": "55GB"
    },
    "ai_services": {
      "status": "healthy",
      "openai_api": "operational",
      "groq_api": "operational",
      "last_check": "2026-02-08T10:29:30Z"
    }
  }
}
```

### 3. Ready Check
**Endpoint:** `GET /health/ready/`  
**Purpose:** Kubernetes readiness probe  
**Response:** HTTP 200 if ready, 503 if not ready  

### 4. Live Check
**Endpoint:** `GET /health/live/`  
**Purpose:** Kubernetes liveness probe  
**Response:** HTTP 200 if alive, 503 if should restart  

### 5. Metrics Endpoint
**Endpoint:** `GET /metrics/`  
**Purpose:** Prometheus metrics in OpenMetrics format  

## Component Health Checks

### Database (PostgreSQL)
- **Check:** Connection test and query execution
- **Metrics:** Response time, active connections, connection pool status
- **Thresholds:**
  - Warning: Response time > 100ms
  - Critical: Response time > 1s or connection failures

### Redis Cache
- **Check:** Connection test and basic operations
- **Metrics:** Response time, memory usage, connected clients
- **Thresholds:**
  - Warning: Memory usage > 80%
  - Critical: Connection failures or memory > 95%

### Celery Task Queue
- **Check:** Worker status and queue health
- **Metrics:** Active workers, queued tasks, failed tasks
- **Thresholds:**
  - Warning: Queue length > 100
  - Critical: No active workers or queue length > 1000

### File Storage
- **Check:** Disk space and write permissions
- **Metrics:** Disk usage, available space, I/O performance
- **Thresholds:**
  - Warning: Disk usage > 80%
  - Critical: Disk usage > 95% or write failures

### AI Services
- **Check:** API connectivity and response validation
- **Metrics:** Response time, rate limits, error rates
- **Thresholds:**
  - Warning: Response time > 2s
  - Critical: API errors > 10% or rate limit exceeded

### Memory and CPU
- **Check:** System resource utilization
- **Metrics:** Memory usage, CPU load, process counts
- **Thresholds:**
  - Warning: Memory > 80% or CPU > 80%
  - Critical: Memory > 95% or CPU > 95%

## Monitoring Integration

### Prometheus Metrics

The application exposes metrics at `/metrics/` in Prometheus format:

```bash
# Application metrics
django_requests_total{method="GET",path="/api/projects/"} 1234
django_request_duration_seconds{method="GET",path="/api/projects/"} 0.145

# Database metrics
database_connections_active 12
database_queries_total{table="projects"} 5678
database_query_duration_seconds{table="projects"} 0.025

# Redis metrics
redis_memory_usage_bytes 163840000
redis_connected_clients 8
redis_keyspace_hits_total 9876

# Celery metrics
celery_workers_active 4
celery_tasks_queued 0
celery_tasks_failed_total 2

# AI Service metrics
ai_requests_total{service="openai",endpoint="chat"} 456
ai_request_duration_seconds{service="openai",endpoint="chat"} 1.234
ai_errors_total{service="openai",endpoint="chat"} 3

# Business metrics
users_active_total 234
projects_created_total 567
designs_generated_total 890
```

### Grafana Dashboard

Key metrics to monitor:

1. **Application Performance**
   - Request rate and response times
   - Error rates by endpoint
   - User activity metrics

2. **Infrastructure Health**
   - CPU and memory usage
   - Disk I/O and network metrics
   - Container/pod restart counts

3. **Database Performance**
   - Query performance and slow queries
   - Connection pool utilization
   - Lock contention

4. **AI Service Health**
   - API response times and error rates
   - Token usage and rate limits
   - Cost tracking

### Alerting Rules

#### Critical Alerts (PagerDuty)
- Health check endpoint returns 500
- Database connection failures
- Redis unavailable
- No active Celery workers
- Disk space > 95%
- Memory usage > 95%

#### Warning Alerts (Slack)
- Response time > 2s for 5 minutes
- Error rate > 5% for 10 minutes
- Queue length > 100
- Disk space > 80%
- AI service errors > 10%

## Load Balancer Health Checks

### Configuration Examples

#### NGINX
```nginx
upstream aidesigntool {
    server app1:8000 max_fails=3 fail_timeout=30s;
    server app2:8000 max_fails=3 fail_timeout=30s;
}

location /health {
    access_log off;
    return 200 "healthy\n";
    add_header Content-Type text/plain;
}
```

#### AWS ALB Target Group
```json
{
  "HealthCheckPath": "/health/ready/",
  "HealthCheckProtocol": "HTTP",
  "HealthCheckIntervalSeconds": 30,
  "HealthCheckTimeoutSeconds": 5,
  "HealthyThresholdCount": 2,
  "UnhealthyThresholdCount": 3
}
```

#### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health/live/
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready/
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

## Health Check Implementation

### Django Health Check Views

```python
# backend/backend/health.py
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.cache import cache
import time
import psutil

class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '2.0.0'
        })

class DetailedHealthView(View):
    def get(self, request):
        checks = {}
        overall_status = 'healthy'
        
        # Database check
        try:
            with connection.cursor() as cursor:
                start = time.time()
                cursor.execute('SELECT 1')
                response_time = (time.time() - start) * 1000
            
            checks['database'] = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            }
        except Exception:
            checks['database'] = {'status': 'unhealthy'}
            overall_status = 'unhealthy'
        
        # Redis check
        try:
            start = time.time()
            cache.set('health_check', 'ok', 10)
            cache.get('health_check')
            response_time = (time.time() - start) * 1000
            
            checks['redis'] = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2)
            }
        except Exception:
            checks['redis'] = {'status': 'unhealthy'}
            overall_status = 'unhealthy'
        
        return JsonResponse({
            'status': overall_status,
            'checks': checks
        })
```

### Custom Health Checks

```python
# backend/backend/health_checks.py
import subprocess
import requests
from celery import current_app

def check_celery():
    """Check Celery worker status"""
    try:
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        
        if not stats:
            return {'status': 'unhealthy', 'error': 'No workers found'}
        
        worker_count = len(stats)
        return {
            'status': 'healthy',
            'workers': worker_count
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

def check_ai_services():
    """Check AI service availability"""
    checks = {}
    
    # Check OpenAI
    try:
        # Simple API test (adjust based on your implementation)
        response = requests.get(
            'https://api.openai.com/v1/models',
            headers={'Authorization': f'Bearer {settings.OPENAI_API_KEY}'},
            timeout=5
        )
        checks['openai'] = 'healthy' if response.status_code == 200 else 'unhealthy'
    except Exception:
        checks['openai'] = 'unhealthy'
    
    return checks

def check_storage():
    """Check storage health"""
    import shutil
    
    try:
        usage = shutil.disk_usage(settings.MEDIA_ROOT)
        used_percent = (usage.used / usage.total) * 100
        
        return {
            'status': 'healthy' if used_percent < 90 else 'warning',
            'disk_usage_percent': round(used_percent, 2),
            'available_gb': round(usage.free / (1024**3), 2)
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}
```

## Troubleshooting

### Common Issues

1. **Database Connection Failures**
   - Check PostgreSQL service status
   - Verify connection parameters
   - Check connection pool settings

2. **Redis Unavailable**
   - Check Redis service status
   - Verify Redis configuration
   - Check memory usage

3. **Celery Workers Down**
   - Check Celery worker processes
   - Verify message broker connectivity
   - Check task queue configuration

4. **High Response Times**
   - Check database query performance
   - Verify cache hit rates
   - Monitor resource utilization

5. **AI Service Errors**
   - Check API key validity
   - Verify rate limit status
   - Check service status pages

### Health Check Commands

```bash
# Quick health check
curl -f http://localhost:8000/health/ || echo "Health check failed"

# Detailed health check
curl -s http://localhost:8000/health/detailed/ | jq '.'

# Check specific component
curl -s http://localhost:8000/health/detailed/ | jq '.checks.database'

# Monitor health continuously
watch -n 5 'curl -s http://localhost:8000/health/ | jq "."'
```

### Logs and Diagnostics

Health check failures are logged with detailed information:

```bash
# Check application logs
tail -f /var/log/aidesigntool/app.log

# Check health check specific logs
grep "health_check" /var/log/aidesigntool/app.log

# Check error logs
tail -f /var/log/aidesigntool/error.log

# Check Celery logs
tail -f /var/log/aidesigntool/celery.log
```

## Best Practices

1. **Response Times**
   - Keep basic health check < 100ms
   - Detailed health check < 500ms
   - Use timeouts for external service checks

2. **Error Handling**
   - Gracefully handle component failures
   - Provide meaningful error messages
   - Log failures with context

3. **Caching**
   - Cache expensive health checks
   - Use appropriate cache durations
   - Invalidate cache on configuration changes

4. **Security**
   - Don't expose sensitive information
   - Consider authentication for detailed endpoints
   - Rate limit health check endpoints

5. **Monitoring**
   - Set up appropriate alerting thresholds
   - Monitor trends, not just point-in-time status
   - Include business metrics alongside technical metrics

---

**Last Updated:** February 8, 2026  
**Version:** 2.0.0  

For questions about health monitoring, contact: ops@aidesigntool.com
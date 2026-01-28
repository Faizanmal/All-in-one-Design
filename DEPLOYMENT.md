# 🚀 Production Deployment Guide

> Complete guide for deploying AI Design Tool to production environments

## Table of Contents
- [Prerequisites](#prerequisites)
- [Infrastructure Setup](#infrastructure-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Providers](#cloud-providers)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling Guide](#scaling-guide)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 vCPU | 4+ vCPU |
| RAM | 4 GB | 8+ GB |
| Storage | 50 GB SSD | 100+ GB SSD |
| Bandwidth | 100 Mbps | 1 Gbps |

### Software Requirements

- Docker 24.0+ and Docker Compose 2.0+
- PostgreSQL 15+
- Redis 7+
- Node.js 20+ (for frontend builds)
- Python 3.11+

### External Services

- **Stripe** - Payment processing
- **OpenAI/Groq** - AI services
- **SendGrid/SES** - Email delivery
- **S3/GCS** - File storage (optional)
- **Sentry** - Error tracking (recommended)

---

## Infrastructure Setup

### Architecture Overview

```
                    ┌─────────────────────┐
                    │   Load Balancer     │
                    │   (Nginx/CloudFlare)│
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
    ┌─────────▼─────────┐ ┌────▼────┐ ┌────────▼────────┐
    │  Frontend (Next.js)│ │   API   │ │ Celery Workers  │
    │  Static/CDN        │ │ (Django)│ │ (Background)    │
    └───────────────────┘ └────┬────┘ └────────┬────────┘
                               │               │
              ┌────────────────┼───────────────┤
              │                │               │
    ┌─────────▼─────────┐ ┌────▼────┐ ┌────────▼────────┐
    │   PostgreSQL      │ │  Redis  │ │   Object Store  │
    │   (Primary DB)    │ │ (Cache) │ │   (S3/GCS)      │
    └───────────────────┘ └─────────┘ └─────────────────┘
```

---

## Docker Deployment

### Quick Start (Development)

```bash
# Clone repository
git clone https://github.com/Faizanmal/All-in-one-Design.git
cd All-in-one-Design

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs/
```

### Production Docker Setup

1. **Create production docker-compose override:**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    environment:
      - DEBUG=False
      - SECURE_SSL_REDIRECT=True
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  frontend:
    deploy:
      replicas: 2

  celery:
    deploy:
      replicas: 2
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - backend
      - frontend
```

2. **Deploy with production settings:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Kubernetes Deployment

### Helm Chart (Recommended)

```bash
# Add our Helm repository
helm repo add aidesign https://charts.aidesign.io

# Install with custom values
helm install aidesign aidesign/ai-design-tool \
  --namespace aidesign \
  --create-namespace \
  --values values-production.yaml
```

### Manual Kubernetes Deployment

1. **Create namespace:**
```bash
kubectl create namespace aidesign
```

2. **Apply secrets:**
```bash
kubectl apply -f k8s/secrets.yaml -n aidesign
```

3. **Deploy services:**
```bash
kubectl apply -f k8s/ -n aidesign
```

### Sample Kubernetes Manifests

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: aidesign
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: aidesign/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aidesign-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /api/health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Cloud Providers

### AWS Deployment

1. **Infrastructure with Terraform:**
```bash
cd terraform/aws
terraform init
terraform plan -var-file="production.tfvars"
terraform apply -var-file="production.tfvars"
```

2. **Services Used:**
   - ECS/EKS for containers
   - RDS for PostgreSQL
   - ElastiCache for Redis
   - S3 for file storage
   - CloudFront for CDN
   - ALB for load balancing
   - ACM for SSL certificates

### DigitalOcean Deployment

1. **Create App Platform:**
```bash
doctl apps create --spec .do/app.yaml
```

2. **Sample spec:**
```yaml
# .do/app.yaml
name: ai-design-tool
services:
  - name: backend
    github:
      repo: Faizanmal/All-in-one-Design
      branch: master
      deploy_on_push: true
    source_dir: backend
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-s
    
  - name: frontend
    github:
      repo: Faizanmal/All-in-one-Design
      branch: master
    source_dir: frontend
    build_command: npm run build
    run_command: npm start
    http_port: 3000

databases:
  - engine: PG
    name: db
    size: db-s-2vcpu-4gb
    
  - engine: REDIS
    name: redis
    size: db-s-1vcpu-1gb
```

### Vercel + Railway

**Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

**Backend (Railway):**
```bash
cd backend
railway up
```

---

## Environment Variables

### Required Variables

```bash
# Application
DEBUG=False
SECRET_KEY=your-production-secret-key-min-50-chars
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/aidesign
DB_NAME=aidesign
DB_USER=aidesign_user
DB_PASSWORD=secure-password
DB_HOST=db.example.com
DB_PORT=5432

# Redis
REDIS_URL=redis://redis.example.com:6379/0
CELERY_BROKER_URL=redis://redis.example.com:6379/1

# AI Services
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk-...

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxx
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Storage (S3)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=aidesign-assets
AWS_S3_REGION_NAME=us-east-1

# Security
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
SECURE_SSL_REDIRECT=True

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### Generating Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Database Setup

### PostgreSQL Configuration

```sql
-- Create database and user
CREATE USER aidesign_user WITH PASSWORD 'secure_password';
CREATE DATABASE aidesign OWNER aidesign_user;
GRANT ALL PRIVILEGES ON DATABASE aidesign TO aidesign_user;

-- Enable extensions
\c aidesign
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Run Migrations

```bash
# Via Docker
docker-compose exec backend python manage.py migrate

# Direct
python manage.py migrate

# Check for issues
python manage.py check --deploy
```

### Database Backups

```bash
# Manual backup
pg_dump -h localhost -U aidesign_user aidesign > backup_$(date +%Y%m%d).sql

# Automated backups (cron)
0 2 * * * /usr/bin/pg_dump -h localhost -U aidesign_user aidesign | gzip > /backups/aidesign_$(date +\%Y\%m\%d).sql.gz
```

---

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/aidesign
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Static files
    location /static/ {
        alias /var/www/aidesign/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/aidesign/media/;
        expires 7d;
    }
}
```

---

## Monitoring & Logging

### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

### Sentry Integration

```python
# settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment=os.getenv('ENVIRONMENT', 'production'),
)
```

### Application Logs

```bash
# View Django logs
docker-compose logs -f backend

# View Celery logs
docker-compose logs -f celery

# Log locations
/var/log/aidesign/django.log
/var/log/aidesign/celery.log
/var/log/aidesign/error.log
```

---

## Scaling Guide

### Horizontal Scaling

```bash
# Scale backend replicas
docker-compose up -d --scale backend=5 --scale celery=3

# Kubernetes scaling
kubectl scale deployment backend --replicas=5 -n aidesign
kubectl autoscale deployment backend --min=3 --max=10 --cpu-percent=70
```

### Database Scaling

1. **Read Replicas**: Set up PostgreSQL streaming replication
2. **Connection Pooling**: Use PgBouncer
3. **Query Optimization**: Enable query caching

### Caching Strategy

```python
# Redis cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
        }
    }
}
```

---

## Security Checklist

### Pre-Deployment

- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie settings
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable security headers (CSP, HSTS)
- [ ] Use environment variables for secrets
- [ ] Review database permissions

### Django Security Settings

```python
# Production security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Run Security Check

```bash
python manage.py check --deploy
```

---

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check connectivity
docker-compose exec backend python manage.py dbshell

# Reset connections
docker-compose restart backend
```

**Celery Tasks Not Running:**
```bash
# Check Celery status
docker-compose exec celery celery -A backend inspect active

# Restart workers
docker-compose restart celery celery-beat
```

**Static Files Not Loading:**
```bash
# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

**Memory Issues:**
```bash
# Check container memory usage
docker stats

# Increase limits in docker-compose.yml
```

### Health Checks

```bash
# API health
curl https://yourdomain.com/api/health/

# Database health
curl https://yourdomain.com/api/health/db/

# Redis health
curl https://yourdomain.com/api/health/redis/
```

---

## Support

- **Documentation**: [docs.aidesign.io](https://docs.aidesign.io)
- **Issues**: [GitHub Issues](https://github.com/Faizanmal/All-in-one-Design/issues)
- **Enterprise Support**: enterprise@aidesign.io
- **Community**: [Discord](https://discord.gg/aidesign)

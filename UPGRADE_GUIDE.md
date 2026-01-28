# ⬆️ Upgrade Guide: v1.0 to v2.0 (Enterprise Edition)

> Step-by-step migration guide for upgrading from AI Design Tool v1.0 to v2.0

## Overview

Version 2.0 introduces significant improvements and new enterprise features:

| Category | v1.0 | v2.0 |
|----------|------|------|
| Authentication | Basic JWT | JWT + OAuth + API Keys |
| Database | SQLite | PostgreSQL (production) |
| Caching | None | Redis + Django Cache |
| Background Tasks | None | Celery + Redis |
| Analytics | Basic | Advanced Dashboard |
| Subscriptions | None | 3-Tier Stripe Integration |
| Collaboration | Limited | Real-time + Comments |
| API | Basic REST | OpenAPI + Rate Limiting |

---

## Pre-Upgrade Checklist

### 1. Backup Everything

```bash
# Backup database
pg_dump -h localhost -U postgres aidesign > backup_v1_$(date +%Y%m%d).sql

# Backup uploaded files
tar -czvf media_backup_$(date +%Y%m%d).tar.gz media/

# Backup environment
cp .env .env.backup
```

### 2. Review Breaking Changes

#### API Changes

| Endpoint | v1.0 | v2.0 | Action Required |
|----------|------|------|-----------------|
| `/api/auth/login/` | Returns token | Returns access + refresh tokens | Update frontend |
| `/api/projects/` | No pagination | Paginated (20/page) | Handle pagination |
| `/api/ai/generate/` | Sync | Async (returns task ID) | Poll for results |
| `/api/users/me/` | Basic info | Extended profile + subscription | Update data handling |

#### Database Schema Changes

- New tables: `subscriptions_*`, `analytics_*`, `notifications_*`
- Modified tables: `projects_project` (new fields), `accounts_*`
- New indexes for performance

#### Configuration Changes

```python
# New required settings in settings.py
CELERY_BROKER_URL = os.getenv('REDIS_URL')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
EMAIL_HOST = os.getenv('EMAIL_HOST')
```

---

## Upgrade Steps

### Step 1: Stop Services

```bash
# Stop running containers
docker-compose down

# Or if running directly
supervisorctl stop all
```

### Step 2: Update Code

```bash
# Pull latest changes
git fetch origin
git checkout v2.0.0

# Or pull master
git pull origin master
```

### Step 3: Update Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Step 4: Update Environment Variables

Add these new variables to your `.env`:

```bash
# Redis (Required)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Stripe (Required for subscriptions)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (Required for notifications)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Sentry (Optional but recommended)
SENTRY_DSN=https://xxx@sentry.io/xxx

# Security (Production)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Step 5: Database Migration

```bash
cd backend

# Create new migrations if needed
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create subscription tiers
python manage.py setup_subscription_tiers

# Run data migrations
python manage.py migrate_user_data
```

### Step 6: Start New Services

```bash
# Start Redis
docker-compose up -d redis

# Or install locally
sudo apt install redis-server
sudo systemctl start redis
```

### Step 7: Start Celery Workers

```bash
# Development
celery -A backend worker -l info &
celery -A backend beat -l info &

# Production (via supervisor)
supervisorctl start celery celery-beat
```

### Step 8: Start Application

```bash
# Docker
docker-compose up -d

# Or directly
python manage.py runserver
```

### Step 9: Verify Upgrade

```bash
# Check API health
curl http://localhost:8000/api/health/

# Check migrations
python manage.py showmigrations

# Run tests
python manage.py test

# Check for deployment issues
python manage.py check --deploy
```

---

## Data Migration Scripts

### Migrate User Subscriptions

If you had custom user plans, migrate them:

```python
# backend/scripts/migrate_subscriptions.py
from django.contrib.auth.models import User
from subscriptions.models import Subscription, SubscriptionTier

def migrate_subscriptions():
    free_tier = SubscriptionTier.objects.get(slug='free')
    
    for user in User.objects.filter(subscription__isnull=True):
        Subscription.objects.create(
            user=user,
            tier=free_tier,
            status='active',
            billing_period='monthly'
        )
        print(f"Created subscription for {user.username}")

# Run: python manage.py shell < scripts/migrate_subscriptions.py
```

### Migrate Project Data

Update project data structure:

```python
# backend/scripts/migrate_projects.py
from projects.models import Project

def migrate_projects():
    for project in Project.objects.all():
        # Add version tracking
        if not project.version:
            project.version = 1
        
        # Migrate design_data structure
        design_data = project.design_data or {}
        if 'metadata' not in design_data:
            design_data['metadata'] = {
                'version': '2.0',
                'migratedFrom': '1.0',
                'migratedAt': timezone.now().isoformat()
            }
            project.design_data = design_data
        
        project.save()
        print(f"Migrated project: {project.name}")
```

### Migrate Analytics Data

```python
# backend/scripts/migrate_analytics.py
from analytics.models import ProjectAnalytics
from analytics.advanced_analytics_models import UserActivityLog
from projects.models import Project

def migrate_analytics():
    for project in Project.objects.all():
        # Create initial activity log
        UserActivityLog.objects.get_or_create(
            user=project.user,
            action_type='project_create',
            project=project,
            defaults={
                'created_at': project.created_at,
                'metadata': {'migrated': True}
            }
        )
```

---

## Frontend Updates

### Update API Calls

```typescript
// Before (v1.0)
const response = await api.post('/api/auth/login/', credentials);
localStorage.setItem('token', response.data.token);

// After (v2.0)
const response = await api.post('/api/auth/login/', credentials);
localStorage.setItem('accessToken', response.data.access);
localStorage.setItem('refreshToken', response.data.refresh);
```

### Handle Pagination

```typescript
// Before (v1.0)
const projects = await api.get('/api/projects/');
setProjects(projects.data);

// After (v2.0)
const response = await api.get('/api/projects/');
setProjects(response.data.results);
setPagination({
  count: response.data.count,
  next: response.data.next,
  previous: response.data.previous
});
```

### Update Axios Interceptors

```typescript
// src/lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Add token refresh logic
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/auth/refresh/', {
          refresh: refreshToken
        });
        
        localStorage.setItem('accessToken', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

---

## Rollback Procedure

If upgrade fails, rollback:

```bash
# 1. Stop services
docker-compose down

# 2. Restore code
git checkout v1.0.0

# 3. Restore database
psql -h localhost -U postgres aidesign < backup_v1_YYYYMMDD.sql

# 4. Restore environment
mv .env.backup .env

# 5. Reinstall dependencies
pip install -r requirements.txt
npm install

# 6. Start services
docker-compose up -d
```

---

## Post-Upgrade Tasks

### 1. Set Up Subscription Tiers

```bash
python manage.py shell

from subscriptions.models import SubscriptionTier

# Free Tier
SubscriptionTier.objects.create(
    name='Free',
    slug='free',
    price_monthly=0,
    price_yearly=0,
    max_projects=3,
    max_ai_requests_per_month=50,
    max_storage_mb=100,
    features={'basic_ai': True}
)

# Pro Tier
SubscriptionTier.objects.create(
    name='Pro',
    slug='pro',
    price_monthly=19,
    price_yearly=190,
    max_projects=50,
    max_ai_requests_per_month=500,
    max_storage_mb=5000,
    features={'advanced_ai': True, 'priority_support': True}
)

# Enterprise Tier
SubscriptionTier.objects.create(
    name='Enterprise',
    slug='enterprise',
    price_monthly=99,
    price_yearly=990,
    max_projects=-1,
    max_ai_requests_per_month=-1,
    max_storage_mb=-1,
    features={'advanced_ai': True, 'white_label': True, 'api_access': True}
)
```

### 2. Configure Stripe Webhooks

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://yourdomain.com/api/subscriptions/webhooks/stripe/`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 3. Test All Features

```bash
# Run full test suite
python manage.py test

# Test specific apps
python manage.py test subscriptions analytics notifications
```

### 4. Monitor for Issues

- Check application logs for errors
- Monitor Sentry for new issues
- Check Celery task queue
- Verify email delivery

---

## Getting Help

- **Documentation**: See [ENTERPRISE_FEATURES.md](ENTERPRISE_FEATURES.md)
- **Issues**: [GitHub Issues](https://github.com/Faizanmal/All-in-one-Design/issues)
- **Enterprise Support**: enterprise@aidesign.io

# Deployment

## Configure

```bash
cp .env.example .env
```

| File | Use |
|------|-----|
| `docker-compose.yml` | **Production** (Nginx 80/443) |
| `docker-compose.dev.yml` | **Local** |
| `scripts/deploy-production.sh` | Production bootstrap + Let's Encrypt |

---

## Local

```bash
cp .env.example .env
# Keep localhost URLs; set SECRET_KEY + at least one AI key

docker compose -f docker-compose.dev.yml up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000/api/ |
| Health | http://localhost:8000/health/ |
| API docs | http://localhost:8000/api/docs/ (DEBUG / ENABLE_API_DOCS) |

Postgres `:5432` and Redis `:6379` are published for local tools.

---

## Production checklist

Before first deploy, set in `.env`:

```env
DEBUG=False
FORCE_HTTPS=True
DOMAIN=yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,backend
FRONTEND_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://yourdomain.com/ws
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">
DB_PASSWORD=<strong>
REDIS_PASSWORD=<strong>
CERTBOT_EMAIL=admin@yourdomain.com
GROQ_API_KEY=<or another AI key>
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SENTRY_DSN=   # optional but recommended
ENABLE_API_DOCS=False
# Optional one-time admin (remove password after first boot):
# DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
# DJANGO_SUPERUSER_USERNAME=admin
# DJANGO_SUPERUSER_PASSWORD=...
```

DNS: `A`/`AAAA` for apex and `www` → your server. Open ports **80** and **443**.

### Deploy (recommended)

```bash
bash scripts/deploy-production.sh
# Windows: scripts\deploy-production.bat  (uses Git Bash if available)
```

The script:

1. Validates secrets, HTTPS URLs, and at least one AI key  
2. If no certs yet → HTTP-only nginx → Certbot for `DOMAIN` + `www` → HTTPS template  
3. `docker compose up --build -d`

App: **https://yourdomain.com** (only 80/443 published).

After changing `NEXT_PUBLIC_*`, rebuild: `docker compose up --build -d`.

### Ops

```bash
docker compose logs -f
docker compose exec backend python manage.py createsuperuser
python scripts/backup.py --type full
python scripts/restore.py backups/database_backup_YYYYMMDD_HHMMSS.sql.gz --yes
docker compose down
```

Remove `DJANGO_SUPERUSER_PASSWORD` from `.env` after the first successful boot.

### Manual TLS (if not using the script)

```bash
cp nginx/http-only.conf.template nginx/templates/default.conf.template
# temporarily FORCE_HTTPS=False
docker compose up --build -d
docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot -w /var/www/certbot \
  --email admin@yourdomain.com --agree-tos --no-eff-email \
  -d yourdomain.com -d www.yourdomain.com
cp nginx/default.conf.https.template nginx/templates/default.conf.template
# set FORCE_HTTPS=True
docker compose up -d --force-recreate nginx backend celery celery-beat
```

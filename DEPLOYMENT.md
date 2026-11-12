# Deployment

## Configure

```bash
cp .env.example .env
```

| File | Use |
|------|-----|
| `docker-compose.yml` | **Production default** — API on GCP VM (plain `docker compose …`) |
| `docker-compose.dev.yml` | **Local** |
| `docker-compose.full.yml` | Optional — frontend + API on one host |
| `scripts/deploy-gcp.sh` | Production bootstrap + Let's Encrypt (API host) |

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

## Deploy a validated commit from GitHub Actions

After the initial VM setup below, configure the GitHub `production` environment:

- Variables: `DEPLOY_HOST` (API VM hostname), `DEPLOY_USER` (SSH user), and `DEPLOY_PATH` (absolute path to this repository on the VM).
- Secrets: `DEPLOY_SSH_KEY` (the deployment user's private key) and `DEPLOY_KNOWN_HOSTS` (the VM's SSH host-key record, verified through a trusted channel).
- The VM checkout must have a configured `.env`, Docker access, and permission to fetch this repository from its `origin` remote. Keep tracked files clean; deployment refuses to overwrite local changes.

In Actions, run **CI/CD Pipeline** on `main` or `master` and enable **deploy_api**. Backend tests, migration checks, frontend tests, lint, type checking, and the production build must pass before deployment. The job checks out the exact tested commit on the VM and runs `scripts/deploy-gcp.sh`, including its health check. Ordinary pushes and pull requests do not invoke this deployment job. Netlify continues to deploy the frontend through its configured Git integration.

Deploying runs database migrations through the existing container entrypoint. Before a production release, create a database backup using your normal backup process; rollback involving migrations needs a migration-specific plan.

---

## Production — API on a GCP VM, site on Netlify

The VM runs Django, Celery, Postgres, and Redis. Nginx on the VM serves only the API host. Netlify serves the Next.js app.

### 1. Create the VM

From a machine with the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) signed in (`gcloud auth login`):

```powershell
$env:GCP_PROJECT = "your-project-id"
.\scripts\provision-gcp-vm.ps1
```

Defaults: `e2-medium` in `asia-south1-a` (Mumbai), 30 GB disk, static IP, ports 80 and 443. Override with `GCP_ZONE` or `GCP_MACHINE`.

The script prints a static IP. Create a DNS **A** record, for example `api.yourdomain.com`, pointing at that IP. Wait until it resolves, then SSH in:

```powershell
gcloud compute ssh aidesign-api --zone asia-south1-a --project your-project-id
```

### 2. Configure and start the API

On the VM, clone this repo and create `.env`:

```env
DEBUG=False
FORCE_HTTPS=True
DOMAIN=api.yourdomain.com
ALLOWED_HOSTS=api.yourdomain.com,localhost,127.0.0.1,backend
FRONTEND_URL=https://your-site.netlify.app
CORS_ALLOWED_ORIGINS=https://your-site.netlify.app
CSRF_TRUSTED_ORIGINS=https://your-site.netlify.app
SECRET_KEY=<long random>
DB_PASSWORD=<strong>
REDIS_PASSWORD=<strong>
CERTBOT_EMAIL=admin@yourdomain.com
GROQ_API_KEY=<or another AI key>
```

`NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` belong in **Netlify**, not on the VM.

```bash
bash scripts/deploy-gcp.sh
```

That validates `.env`, obtains a Let's Encrypt certificate for `DOMAIN`, and starts the stack. API: `https://api.yourdomain.com/api/`. Health: `https://api.yourdomain.com/health/`.

### 3. Point Netlify at the API

```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

Redeploy the Netlify site after saving those. They are baked in at build time.

### Ops (on the VM)

```bash
docker compose logs -f
docker compose exec backend python manage.py createsuperuser
python scripts/backup.py --type full
docker compose down
```

Remove `DJANGO_SUPERUSER_PASSWORD` from `.env` after the first successful boot. Snapshot the disk from the GCP console so Postgres and uploaded media survive a disk failure.

---

## Single-server / full VPS

`docker-compose.full.yml` plus `scripts/deploy-production.sh` runs Next.js + Django + Celery + Postgres + Redis + Nginx + TLS on one VPS.

If the apex domain already hosts a portfolio (or anything else), use a **subdomain** for this app — do not point `DOMAIN` at the portfolio hostname.

Before first deploy, set in `.env`:

```env
DEBUG=False
FORCE_HTTPS=True
# Subdomain example (recommended when apex is already used):
DOMAIN=app.yourdomain.com
ALLOWED_HOSTS=app.yourdomain.com,backend
FRONTEND_URL=https://app.yourdomain.com
NEXT_PUBLIC_API_URL=https://app.yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://app.yourdomain.com/ws
CORS_ALLOWED_ORIGINS=https://app.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://app.yourdomain.com
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">
DB_PASSWORD=<strong>
REDIS_PASSWORD=<strong>
CERTBOT_EMAIL=admin@yourdomain.com
GROQ_API_KEY=<or another AI key>
RESEND_API_KEY=re_...
# Or SMTP fallback if not using Resend:
# EMAIL_HOST=smtp.example.com
# EMAIL_HOST_USER=...
# EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
SENTRY_DSN=   # optional but recommended
ENABLE_API_DOCS=False
# Optional one-time admin (remove password after first boot):
# DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
# DJANGO_SUPERUSER_USERNAME=admin
# DJANGO_SUPERUSER_PASSWORD=...
```

DNS: create an **A** (and optional **AAAA**) record for the app host only, e.g. `app.yourdomain.com` → VPS IP. Leave apex/`www` pointing at the portfolio. Open ports **80** and **443** on the VPS.

**Port conflict:** this stack binds host **80/443**. If another Docker app already owns those ports on the same VPS, do **not** run `deploy-production.sh` as-is. Use the shared-proxy path instead:

```bash
# Find the network of the container that binds 80/443
docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Networks}}'

# .env additions:
# PROXY_NETWORK=<that-network-name>
# FORCE_HTTPS=False   # TLS terminates on the edge proxy

cp nginx/http-only.conf.template nginx/templates/default.conf.template
docker compose -f docker-compose.full.yml -f docker-compose.behind-proxy.yml up --build -d
```

Then add `nginx/behind-proxy-edge.example.conf` to the edge nginx (the one on 80/443), issue a cert for `aidesign.faizanmalik.me` there, and reload that nginx.

Certbot: for subdomains (2+ dots), the deploy script issues a cert for `DOMAIN` only. For apex domains it also includes `www` unless you set `INCLUDE_WWW=False`.

### Deploy

```bash
bash scripts/deploy-production.sh
# Windows: scripts\deploy-production.bat  (uses Git Bash if available)
```

The script:

1. Validates secrets, HTTPS URLs, and at least one AI key  
2. If no certs yet → HTTP-only nginx → Certbot for `DOMAIN` (and `www` when applicable) → HTTPS template  
3. `docker compose -f docker-compose.full.yml up --build -d`

App: **https://app.yourdomain.com** (or your chosen `DOMAIN`).

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

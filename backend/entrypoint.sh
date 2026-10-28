#!/bin/bash
set -euo pipefail

# Celery / beat: wait for DB only (backend runs migrate + collectstatic)
if [ "${SKIP_BOOTSTRAP:-false}" = "true" ] || [ "${SKIP_BOOTSTRAP:-False}" = "True" ]; then
  echo "==> SKIP_BOOTSTRAP set — waiting for database then starting"
  python <<'PY'
import os, sys, time
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from django.db import connection
from django.db.utils import OperationalError
deadline = time.time() + 90
while time.time() < deadline:
    try:
        connection.ensure_connection()
        print("Database is ready.")
        sys.exit(0)
    except OperationalError:
        time.sleep(2)
print("Database not ready after 90s", file=sys.stderr)
sys.exit(1)
PY
  echo "==> Starting: $*"
  exec "$@"
fi

echo "==> Waiting for database..."
python <<'PY'
import os, sys, time
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from django.db import connection
from django.db.utils import OperationalError

deadline = time.time() + 60
while time.time() < deadline:
    try:
        connection.ensure_connection()
        print("Database is ready.")
        sys.exit(0)
    except OperationalError:
        time.sleep(2)
print("Database not ready after 60s", file=sys.stderr)
sys.exit(1)
PY

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
mkdir -p /app/media /app/staticfiles /app/backups
python manage.py collectstatic --noinput

# Warn if no AI provider is configured (generation will fail)
python <<'PY'
import os, sys
keys = ("GROQ_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY", "NVIDIA_API_KEY", "ANTHROPIC_API_KEY")
if not any(os.getenv(k) for k in keys):
    print("WARNING: No AI API key set — design generation will fail until one is configured.", file=sys.stderr)
PY

if [ "${INIT_SUBSCRIPTION_TIERS:-False}" = "True" ] || [ "${INIT_SUBSCRIPTION_TIERS:-false}" = "true" ]; then
  echo "==> Initializing subscription tiers..."
  python manage.py init_subscription_tiers || true
fi

if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "==> Ensuring superuser exists..."
  python <<'PY'
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ["DJANGO_SUPERUSER_EMAIL"]
username = os.environ.get("DJANGO_SUPERUSER_USERNAME", email)
password = os.environ["DJANGO_SUPERUSER_PASSWORD"]
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser {username}")
else:
    print(f"Superuser {username} already exists")
PY
fi

echo "==> Starting: $*"
exec "$@"

#!/usr/bin/env bash
# Production deploy: validate .env -> HTTP bootstrap if needed -> Certbot -> HTTPS -> up
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose -f docker-compose.yml)
ENV_FILE="${ENV_FILE:-.env}"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

[[ -f "$ENV_FILE" ]] || die "Missing $ENV_FILE — copy .env.example and set production values"

# Load KEY=VAL from .env (strip CR for Windows-edited files)
set -a
while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line%$'\r'}"
  case "$line" in
    ''|\#*) continue ;;
  esac
  case "$line" in
    *=*) ;;
    *) continue ;;
  esac
  key="${line%%=*}"
  val="${line#*=}"
  # trim whitespace around key
  key="$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  export "$key=$val"
done < "$ENV_FILE"
set +a

require() {
  local k="$1"
  local v="${!k:-}"
  case "$v" in
    ''|change-me*) die "$k must be set to a real value in $ENV_FILE" ;;
  esac
}

require SECRET_KEY
require DB_PASSWORD
require REDIS_PASSWORD
require DOMAIN
require FRONTEND_URL
require NEXT_PUBLIC_API_URL
require NEXT_PUBLIC_WS_URL
require CORS_ALLOWED_ORIGINS
require CSRF_TRUSTED_ORIGINS
require ALLOWED_HOSTS

case "${DEBUG:-True}" in
  False|false|0) ;;
  *) die "DEBUG must be False for production" ;;
esac
[[ "$DOMAIN" != "localhost" ]] || die "DOMAIN must be your real domain"
case "$NEXT_PUBLIC_API_URL" in
  https://*) ;;
  *) die "NEXT_PUBLIC_API_URL must be https://..." ;;
esac
case "$NEXT_PUBLIC_WS_URL" in
  wss://*) ;;
  *) die "NEXT_PUBLIC_WS_URL must be wss://..." ;;
esac

AI_OK=0
for k in GROQ_API_KEY OPENAI_API_KEY GOOGLE_API_KEY NVIDIA_API_KEY ANTHROPIC_API_KEY; do
  if [[ -n "${!k:-}" ]]; then AI_OK=1; fi
done
[[ "$AI_OK" -eq 1 ]] || die "Set at least one AI API key (e.g. GROQ_API_KEY)"

CERT_DIR="ssl/certbot/conf/live/${DOMAIN}"
HTTPS_TMPL="nginx/default.conf.https.template"
HTTP_TMPL="nginx/http-only.conf.template"
ACTIVE_TMPL="nginx/templates/default.conf.template"

mkdir -p ssl/certbot/www ssl/certbot/conf

if [[ ! -f "${CERT_DIR}/fullchain.pem" ]]; then
  info "No TLS certs for ${DOMAIN} — starting HTTP-only bootstrap"
  cp "$HTTP_TMPL" "$ACTIVE_TMPL"
  export FORCE_HTTPS=False
  "${COMPOSE[@]}" up --build -d
  info "Waiting for nginx..."
  sleep 8
  EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"
  info "Issuing Let's Encrypt cert (email=$EMAIL)"
  "${COMPOSE[@]}" run --rm --entrypoint certbot certbot certonly \
    --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.${DOMAIN}" \
    || die "Certbot failed — check DNS A/AAAA for $DOMAIN and www.$DOMAIN"
  info "Installing HTTPS nginx template and enabling FORCE_HTTPS"
  cp "$HTTPS_TMPL" "$ACTIVE_TMPL"
  unset FORCE_HTTPS
  FORCE_HTTPS="$(grep -E '^FORCE_HTTPS=' "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '\r"'"'"'')"
  export FORCE_HTTPS="${FORCE_HTTPS:-True}"
  "${COMPOSE[@]}" up -d --force-recreate nginx backend celery celery-beat
else
  info "TLS certs found — deploying with HTTPS template"
  cp "$HTTPS_TMPL" "$ACTIVE_TMPL"
  "${COMPOSE[@]}" up --build -d
fi

info "Waiting for backend health..."
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1/health/" >/dev/null 2>&1 \
    || curl -fsSk "https://127.0.0.1/health/" >/dev/null 2>&1 \
    || "${COMPOSE[@]}" exec -T backend curl -fsS http://localhost:8000/health/ >/dev/null 2>&1; then
    info "Backend healthy"
    break
  fi
  sleep 3
  [[ "$i" -eq 30 ]] && die "Backend health check timed out"
done

info "Done. App: https://${DOMAIN}"
info "After first login, remove DJANGO_SUPERUSER_PASSWORD from $ENV_FILE"
info "Backup: python scripts/backup.py --type full"

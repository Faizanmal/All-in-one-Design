#!/usr/bin/env bash
# API deploy on the GCP VM. Frontend is Netlify; this stack is Django + workers + Postgres + Redis.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE=(docker compose)
ENV_FILE="${ENV_FILE:-.env}"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

command -v docker >/dev/null 2>&1 || die "Docker is not installed. On a new VM, wait for the startup script or install Docker, then re-run."
[[ -f "$ENV_FILE" ]] || die "Missing $ENV_FILE — copy .env.example and set the API host, Netlify origin, and secrets"

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
require CORS_ALLOWED_ORIGINS
require CSRF_TRUSTED_ORIGINS
require ALLOWED_HOSTS

case "${DEBUG:-True}" in
  False|false|0) ;;
  *) die "DEBUG must be False for production" ;;
esac
[[ "$DOMAIN" != "localhost" ]] || die "DOMAIN must be the API hostname, for example api.yourdomain.com"
case "$FRONTEND_URL" in
  https://*) ;;
  *) die "FRONTEND_URL must be the Netlify URL, https://..." ;;
esac
case ",${ALLOWED_HOSTS}," in
  *",${DOMAIN},"*) ;;
  *) die "ALLOWED_HOSTS must include ${DOMAIN}" ;;
esac
case ",${ALLOWED_HOSTS}," in
  *",localhost,"*) ;;
  *) die "ALLOWED_HOSTS must include localhost so the container health check can reach Django" ;;
esac
case "$CORS_ALLOWED_ORIGINS" in
  *"$FRONTEND_URL"*) ;;
  *) die "CORS_ALLOWED_ORIGINS must include FRONTEND_URL (${FRONTEND_URL})" ;;
esac

AI_OK=0
for k in GROQ_API_KEY OPENAI_API_KEY GOOGLE_API_KEY NVIDIA_API_KEY ANTHROPIC_API_KEY; do
  if [[ -n "${!k:-}" ]]; then AI_OK=1; fi
done
[[ "$AI_OK" -eq 1 ]] || die "Set at least one AI API key (for example GROQ_API_KEY)"

CERT_DIR="ssl/certbot/conf/live/${DOMAIN}"
HTTPS_TMPL="nginx/api-https.conf.template"
HTTP_TMPL="nginx/api-http.conf.template"
ACTIVE_DIR="nginx/prod-active"
ACTIVE_TMPL="${ACTIVE_DIR}/default.conf.template"

mkdir -p ssl/certbot/www ssl/certbot/conf "$ACTIVE_DIR"

if [[ ! -f "${CERT_DIR}/fullchain.pem" ]]; then
  info "No TLS cert for ${DOMAIN} — starting HTTP so Let's Encrypt can validate"
  cp "$HTTP_TMPL" "$ACTIVE_TMPL"
  export FORCE_HTTPS=False
  "${COMPOSE[@]}" up --build -d
  info "Waiting for nginx..."
  sleep 8
  EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"
  info "Issuing Let's Encrypt cert for ${DOMAIN} (email=${EMAIL})"
  "${COMPOSE[@]}" run --rm --entrypoint certbot certbot certonly \
    --webroot -w /var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    || die "Certbot failed. DNS A record for ${DOMAIN} must point at this VM, and port 80 must be open."
  info "Switching nginx to HTTPS"
  cp "$HTTPS_TMPL" "$ACTIVE_TMPL"
  unset FORCE_HTTPS
  FORCE_HTTPS="$(grep -E '^FORCE_HTTPS=' "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '\r"'"'"'' || true)"
  export FORCE_HTTPS="${FORCE_HTTPS:-True}"
  "${COMPOSE[@]}" up -d --force-recreate nginx backend celery celery-beat
else
  info "TLS cert found — deploying with HTTPS"
  cp "$HTTPS_TMPL" "$ACTIVE_TMPL"
  "${COMPOSE[@]}" up --build -d
fi

info "Waiting for backend health..."
for i in $(seq 1 30); do
  if "${COMPOSE[@]}" exec -T backend curl -fsS http://localhost:8000/health/ >/dev/null 2>&1; then
    info "Backend healthy"
    break
  fi
  sleep 3
  [[ "$i" -eq 30 ]] && die "Backend health check timed out. See: docker compose logs backend"
done

info "API is up: https://${DOMAIN}/api/"
info "Health: https://${DOMAIN}/health/"
info "Set Netlify NEXT_PUBLIC_API_URL=https://${DOMAIN}/api and NEXT_PUBLIC_WS_URL=wss://${DOMAIN}/ws then redeploy the site."
info "After the first admin is created, remove DJANGO_SUPERUSER_PASSWORD from $ENV_FILE"

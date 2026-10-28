@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if not exist ".env" (
  echo ERROR: Missing .env — copy .env.example and set production values
  exit /b 1
)

where docker >nul 2>&1 || (
  echo ERROR: Docker not found
  exit /b 1
)

REM Prefer Git Bash / WSL for the full TLS bootstrap script
where bash >nul 2>&1 && (
  bash scripts/deploy-production.sh
  exit /b %ERRORLEVEL%
)

echo.
echo Windows tip: install Git Bash or WSL and re-run for automatic Certbot.
echo Manual path:
echo   1. Set production values in .env (DEBUG=False, DOMAIN, HTTPS URLs, secrets, AI key)
echo   2. If no certs yet: copy nginx\http-only.conf.template to nginx\templates\default.conf.template
echo   3. docker compose up --build -d
echo   4. docker compose run --rm --entrypoint certbot certbot certonly --webroot -w /var/www/certbot -d YOUR_DOMAIN -d www.YOUR_DOMAIN --email YOU@YOUR_DOMAIN --agree-tos --no-eff-email
echo   5. copy nginx\default.conf.https.template to nginx\templates\default.conf.template
echo   6. Set FORCE_HTTPS=True and recreate: docker compose up -d --force-recreate nginx
echo.

set /p CONTINUE=Continue with docker compose up --build -d using current nginx template? [y/N] 
if /I not "%CONTINUE%"=="y" exit /b 1

docker compose -f docker-compose.yml up --build -d
exit /b %ERRORLEVEL%

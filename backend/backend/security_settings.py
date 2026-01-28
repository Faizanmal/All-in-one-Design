"""
Security Settings Configuration
Comprehensive security settings for production deployment
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ===================== AUTHENTICATION & OAUTH =====================

# Google OAuth 2.0
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')
GOOGLE_OAUTH_REDIRECT_URI = os.getenv('GOOGLE_OAUTH_REDIRECT_URI', '')

# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID = os.getenv('GITHUB_OAUTH_CLIENT_ID', '')
GITHUB_OAUTH_CLIENT_SECRET = os.getenv('GITHUB_OAUTH_CLIENT_SECRET', '')
GITHUB_OAUTH_REDIRECT_URI = os.getenv('GITHUB_OAUTH_REDIRECT_URI', '')

# Firebase Configuration
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', '')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', '')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '')

# ===================== ENCRYPTION =====================

# Master encryption key for data at rest (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_MASTER_KEY = os.getenv('ENCRYPTION_MASTER_KEY', '')

# Database encryption settings
DATABASE_ENCRYPTION_ENABLED = os.getenv('DATABASE_ENCRYPTION_ENABLED', 'True').lower() == 'true'

# ===================== RATE LIMITING =====================

# Global rate limits (requests per minute)
GLOBAL_RATE_LIMIT = int(os.getenv('GLOBAL_RATE_LIMIT', 500))
BURST_RATE_LIMIT = int(os.getenv('BURST_RATE_LIMIT', 20))

# API endpoint specific rate limits
API_RATE_LIMITS = {
    'auth': {'requests': 20, 'window': 60},
    'oauth': {'requests': 10, 'window': 60},
    'token': {'requests': 5, 'window': 60},
    'ai': {'requests': 30, 'window': 60},
    'default': {'requests': 100, 'window': 60},
}

# ===================== BOT PROTECTION =====================

# reCAPTCHA v3
RECAPTCHA_SITE_KEY = os.getenv('RECAPTCHA_SITE_KEY', '')
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')
RECAPTCHA_SCORE_THRESHOLD = float(os.getenv('RECAPTCHA_SCORE_THRESHOLD', 0.5))

# ===================== BACKUP CONFIGURATION =====================

# Local backup settings
BACKUP_LOCAL_DIR = os.path.join(BASE_DIR, 'backups')
BACKUP_RETENTION_DAILY = int(os.getenv('BACKUP_RETENTION_DAILY', 7))
BACKUP_RETENTION_WEEKLY = int(os.getenv('BACKUP_RETENTION_WEEKLY', 4))
BACKUP_RETENTION_MONTHLY = int(os.getenv('BACKUP_RETENTION_MONTHLY', 12))

# S3 backup settings
USE_S3_BACKUP = os.getenv('USE_S3_BACKUP', 'False').lower() == 'true'
S3_BACKUP_BUCKET = os.getenv('S3_BACKUP_BUCKET', '')
S3_BACKUP_PREFIX = os.getenv('S3_BACKUP_PREFIX', 'backups/')

# Backup notifications
BACKUP_NOTIFY_SUCCESS = os.getenv('BACKUP_NOTIFY_SUCCESS', 'False').lower() == 'true'
BACKUP_NOTIFY_FAILURE = os.getenv('BACKUP_NOTIFY_FAILURE', 'True').lower() == 'true'
BACKUP_NOTIFICATION_EMAIL = os.getenv('BACKUP_NOTIFICATION_EMAIL', '')

# ===================== SECURITY HEADERS =====================

# Content Security Policy
CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'", "https://www.google.com", "https://www.gstatic.com"]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"]
CSP_IMG_SRC = ["'self'", "data:", "https:", "blob:"]
CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com"]
CSP_CONNECT_SRC = ["'self'", "https://api.openai.com", "https://api.groq.com", "https://www.google.com"]
CSP_FRAME_ANCESTORS = ["'none'"]

# ===================== PASSWORD POLICY =====================

PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 12))
PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
PASSWORD_REQUIRE_DIGIT = os.getenv('PASSWORD_REQUIRE_DIGIT', 'True').lower() == 'true'
PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'True').lower() == 'true'

# ===================== SESSION SECURITY =====================

SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', 86400))  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===================== ACCOUNT LOCKOUT =====================

LOGIN_ATTEMPTS_LIMIT = int(os.getenv('LOGIN_ATTEMPTS_LIMIT', 5))
LOGIN_LOCKOUT_DURATION = int(os.getenv('LOGIN_LOCKOUT_DURATION', 30))  # minutes

# ===================== AUDIT LOGGING =====================

AUDIT_LOG_ENABLED = os.getenv('AUDIT_LOG_ENABLED', 'True').lower() == 'true'
AUDIT_LOG_RETENTION_DAYS = int(os.getenv('AUDIT_LOG_RETENTION_DAYS', 90))

# ===================== IP SECURITY =====================

# IP Blocklist (comma-separated)
IP_BLOCKLIST = [ip.strip() for ip in os.getenv('IP_BLOCKLIST', '').split(',') if ip.strip()]

# IP Allowlist for admin (comma-separated, empty means all allowed)
ADMIN_IP_ALLOWLIST = [ip.strip() for ip in os.getenv('ADMIN_IP_ALLOWLIST', '').split(',') if ip.strip()]

# ===================== FILE UPLOAD SECURITY =====================

MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB
ALLOWED_UPLOAD_EXTENSIONS = [
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.mp4', '.webm', '.mp3', '.wav',
]

# ===================== API KEY SETTINGS =====================

API_KEY_LENGTH = 44  # Length of generated API keys
API_KEY_PREFIX = 'aidt_'  # Prefix for API keys
API_KEY_DEFAULT_RATE_LIMIT = 1000  # Requests per hour

# ===================== MONITORING & ALERTING =====================

# Sentry DSN for error tracking
SENTRY_DSN = os.getenv('SENTRY_DSN', '')

# Security alert webhook
SECURITY_ALERT_WEBHOOK = os.getenv('SECURITY_ALERT_WEBHOOK', '')

# ===================== TLS/SSL SETTINGS =====================

# Minimum TLS version (for documentation)
MINIMUM_TLS_VERSION = 'TLS 1.2'
RECOMMENDED_TLS_VERSION = 'TLS 1.3'

# ===================== CORS SECURITY =====================

# Additional CORS settings for security
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = ['X-Request-ID', 'X-Response-Time']
CORS_PREFLIGHT_MAX_AGE = 86400  # 24 hours

# Production CORS origins (set in environment)
CORS_ALLOWED_ORIGINS_PRODUCTION = [
    origin.strip() for origin in 
    os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') 
    if origin.strip()
]

# ===================== CELERY BEAT SCHEDULE FOR SECURITY TASKS =====================

SECURITY_CELERY_BEAT_SCHEDULE = {
    'daily-backup': {
        'task': 'backup.create_daily_backup',
        'schedule': {
            'hour': 2,  # 2 AM
            'minute': 0,
        },
    },
    'cleanup-old-backups': {
        'task': 'backup.cleanup_old_backups',
        'schedule': {
            'hour': 3,  # 3 AM
            'minute': 0,
        },
    },
    'cleanup-expired-oauth-states': {
        'task': 'authentication.cleanup_expired_states',
        'schedule': {
            'hour': '*',
            'minute': 0,
        },
    },
    'cleanup-old-login-attempts': {
        'task': 'authentication.cleanup_old_login_attempts',
        'schedule': {
            'hour': 4,  # 4 AM
            'minute': 0,
        },
    },
    'security-audit-report': {
        'task': 'security.generate_audit_report',
        'schedule': {
            'day_of_week': 1,  # Monday
            'hour': 6,
            'minute': 0,
        },
    },
}

"""
Test / CI settings.

Usage:
  DJANGO_SETTINGS_MODULE=backend.settings_test pytest
  or: TESTING=True (backend.settings also detects pytest)
"""
import os

# Force test mode before importing base settings
os.environ['TESTING'] = 'True'

from backend.settings import *  # noqa: E402, F403

DEBUG = True
TESTING = True

# Prefer explicit test DB name for Postgres CI services
if DATABASES['default']['ENGINE'].endswith('postgresql'):  # noqa: F405
    DATABASES['default']['CONN_MAX_AGE'] = 0  # noqa: F405
    DATABASES['default']['CONN_HEALTH_CHECKS'] = False  # noqa: F405
    DATABASES['default'].setdefault('TEST', {})['NAME'] = os.getenv(  # noqa: F405
        'TEST_DB_NAME', 'test_aidesign'
    )

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Avoid HTTPS redirects / HSTS during APIClient tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

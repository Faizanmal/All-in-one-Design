"""
Root conftest.py - Shared fixtures for all backend tests.
"""
import os

# Ensure test settings/flags are visible before Django configures the DB.
os.environ.setdefault('TESTING', 'True')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings_test')

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Assert migrations created core tables after test DB setup."""
    with django_db_blocker.unblock():
        from django.db import connection, connections

        # Ensure we are not holding a pre-migrate connection snapshot.
        connections.close_all()
        tables = set(connection.introspection.table_names())
        if 'auth_user' not in tables:
            raise RuntimeError(
                "Test database is missing auth_user after migrate. "
                "Usually caused by INSTALLED_APPS with models but no migrations "
                "(Postgres syncdb runs before auth). "
                f"Tables present: {sorted(tables)[:20]}..."
            )


@pytest.fixture(autouse=True)
def disable_rate_limiting(settings):
    """Disable rate limiting middleware for all tests."""
    settings.MIDDLEWARE = [
        m for m in settings.MIDDLEWARE
        if 'RateLimit' not in m
        and 'BotProtection' not in m
        and 'AnomalyDetection' not in m
        and 'RequestValidation' not in m
    ]


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a standard test user."""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='SecurePass123!',
        first_name='Test',
        last_name='User',
    )
    return user


@pytest.fixture
def user2(db):
    """Create and return a second test user."""
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='SecurePass123!',
        first_name='Second',
        last_name='User',
    )


@pytest.fixture
def admin_user(db):
    """Create and return a superuser."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='AdminPass123!',
    )


@pytest.fixture
def auth_client(user):
    """Return an authenticated API client using JWT."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
def auth_client2(user2):
    """Return an authenticated API client for user2."""
    client = APIClient()
    refresh = RefreshToken.for_user(user2)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
def admin_client(admin_user):
    """Return an authenticated API client for admin."""
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
def token_auth_client(user):
    """Return an authenticated API client using Token auth."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return client


@pytest.fixture
def jwt_tokens(user):
    """Return JWT access and refresh tokens for the test user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }

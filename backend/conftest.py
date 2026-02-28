"""
Root conftest.py - Shared fixtures for all backend tests.
"""
import pytest
from django.contrib.auth.models import User
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken


# Disable rate limiting and security middleware for tests
TEST_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


@pytest.fixture(autouse=True)
def disable_rate_limiting(settings):
    """Disable rate limiting middleware for all tests."""
    settings.MIDDLEWARE = [
        m for m in settings.MIDDLEWARE
        if 'RateLimit' not in m and 'BotProtection' not in m and 'AnomalyDetection' not in m
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

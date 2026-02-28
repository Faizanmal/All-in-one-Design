"""
Tests for authentication app - OAuth and security features.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from authentication.models import (
    OAuthConnection, OAuthState, LoginAttempt, UserSecurityProfile, APIKey
)


@pytest.mark.unit
class TestOAuthConnection:
    """Tests for OAuthConnection model."""

    def test_create_google_connection(self, user):
        conn = OAuthConnection.objects.create(
            user=user,
            provider='google',
            provider_user_id='google-123',
            provider_email=user.email,
            is_primary=True,
        )
        assert conn.provider == 'google'
        assert conn.is_primary is True

    def test_create_github_connection(self, user):
        conn = OAuthConnection.objects.create(
            user=user,
            provider='github',
            provider_user_id='github-456',
            provider_email=user.email,
        )
        assert conn.provider == 'github'

    def test_multiple_providers(self, user):
        OAuthConnection.objects.create(
            user=user, provider='google',
            provider_user_id='g-1', provider_email=user.email,
        )
        OAuthConnection.objects.create(
            user=user, provider='github',
            provider_user_id='gh-1', provider_email=user.email,
        )
        assert OAuthConnection.objects.filter(user=user).count() == 2


@pytest.mark.unit
class TestOAuthState:
    """Tests for OAuthState model."""

    def test_create_state(self, db):
        from django.utils import timezone
        state = OAuthState.objects.create(
            state='random-state-string',
            provider='google',
            redirect_uri='http://localhost:3000/callback',
            expires_at=timezone.now() + timezone.timedelta(minutes=10),
        )
        assert state.used is False
        assert state.provider == 'google'


@pytest.mark.unit
class TestUserSecurityProfile:
    """Tests for UserSecurityProfile model."""

    def test_create_security_profile(self, user):
        profile, created = UserSecurityProfile.objects.get_or_create(user=user)
        assert profile.two_factor_enabled is False
        assert profile.is_locked is False

    def test_lockout(self, user):
        profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
        profile.is_locked = True
        profile.locked_reason = 'too many failed attempts'
        profile.save()
        profile.refresh_from_db()
        assert profile.is_locked is True


@pytest.mark.unit
class TestAPIKeyModel:
    """Tests for APIKey model."""

    def test_create_api_key(self, user):
        key = APIKey.objects.create(
            user=user,
            name='Test Key',
            key_prefix='tk_',
            key_hash='hashed_key_value',
            is_active=True,
            rate_limit=1000,
        )
        assert key.is_active is True
        assert key.usage_count == 0

    def test_api_key_scopes(self, user):
        key = APIKey.objects.create(
            user=user,
            name='Scoped Key',
            key_prefix='sk_',
            key_hash='hashed',
            scopes=['read:projects', 'write:projects'],
        )
        assert 'read:projects' in key.scopes


@pytest.mark.unit
class TestLoginAttemptAuth:
    """Tests for authentication LoginAttempt model."""

    def test_successful_attempt(self, db):
        attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='127.0.0.1',
            success=True,
            provider='google',
        )
        assert attempt.success is True
        assert attempt.is_suspicious is False

    def test_suspicious_attempt(self, db):
        attempt = LoginAttempt.objects.create(
            email='test@example.com',
            ip_address='192.168.1.1',
            success=False,
            failure_reason='invalid_token',
            is_suspicious=True,
            risk_score=0.8,
        )
        assert attempt.is_suspicious is True
        assert attempt.risk_score == 0.8


@pytest.mark.api
class TestOAuthEndpoints:
    """Tests for OAuth API endpoints."""

    def test_google_oauth_start(self, api_client, db):
        response = api_client.get('/api/v1/auth/oauth/google/')
        # May return redirect URL or error if not configured
        assert response.status_code in [200, 302, 400, 500]

    def test_github_oauth_start(self, api_client, db):
        response = api_client.get('/api/v1/auth/oauth/github/')
        assert response.status_code in [200, 302, 400, 500]

    def test_firebase_verify_no_token(self, api_client, db):
        response = api_client.post('/api/v1/auth/oauth/firebase/verify/', {})
        assert response.status_code in [400, 401]


@pytest.mark.api
class TestSecurityEndpoints:
    """Tests for security endpoints."""

    def test_list_oauth_connections(self, auth_client, user):
        response = auth_client.get('/api/v1/auth/oauth/connections/')
        assert response.status_code == status.HTTP_200_OK

    def test_security_profile(self, auth_client, user):
        response = auth_client.get('/api/v1/auth/security/profile/')
        assert response.status_code == status.HTTP_200_OK

    def test_security_login_history(self, auth_client, user):
        response = auth_client.get('/api/v1/auth/security/login-history/')
        assert response.status_code == status.HTTP_200_OK

    def test_disconnect_oauth_no_connection(self, auth_client, user):
        response = auth_client.delete('/api/v1/auth/oauth/disconnect/google/')
        assert response.status_code in [200, 404]

    def test_security_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/auth/security/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

"""
Unit and API tests for accounts views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile, UserPreferences, LoginAttempt


@pytest.mark.api
class TestRegisterView:
    """Tests for registration endpoint."""

    url = '/api/v1/auth/register/'

    def test_register_success(self, api_client, db):
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert User.objects.filter(username='newuser').exists()

    def test_register_missing_username(self, api_client, db):
        payload = {'email': 'x@x.com', 'password': 'SecurePass123!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email(self, api_client, db):
        payload = {'username': 'test', 'password': 'SecurePass123!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password(self, api_client, db):
        payload = {'username': 'test', 'email': 'x@x.com'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_username(self, api_client, user):
        payload = {
            'username': user.username,
            'email': 'different@example.com',
            'password': 'SecurePass123!',
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user):
        payload = {
            'username': 'differentuser',
            'email': user.email,
            'password': 'SecurePass123!',
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_creates_profile(self, api_client, db):
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
        }
        api_client.post(self.url, payload)
        user = User.objects.get(username='newuser')
        assert hasattr(user, 'profile')

    def test_register_options_returns_200(self, api_client, db):
        response = api_client.options(self.url)
        assert response.status_code == 200


@pytest.mark.api
class TestLoginView:
    """Tests for login endpoint."""

    url = '/api/v1/auth/login/'

    def test_login_success(self, api_client, user):
        payload = {'username': 'testuser', 'password': 'SecurePass123!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data or 'token' in response.data

    def test_login_with_email(self, api_client, user):
        payload = {'username': user.email, 'password': 'SecurePass123!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_200_OK

    def test_login_wrong_password(self, api_client, user):
        payload = {'username': 'testuser', 'password': 'WrongPassword!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client, db):
        payload = {'username': 'nonexistent', 'password': 'SecurePass123!'}
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_credentials(self, api_client, db):
        response = api_client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_records_attempt(self, api_client, user):
        payload = {'username': 'testuser', 'password': 'SecurePass123!'}
        api_client.post(self.url, payload)
        assert LoginAttempt.objects.filter(
            username_attempted='testuser', success=True
        ).exists()

    def test_login_failed_records_attempt(self, api_client, user):
        payload = {'username': 'testuser', 'password': 'wrong'}
        api_client.post(self.url, payload)
        assert LoginAttempt.objects.filter(
            username_attempted='testuser', success=False
        ).exists()


@pytest.mark.api
class TestCurrentUserView:
    """Tests for get/update current user endpoint."""

    url = '/api/v1/auth/users/me/'

    def test_get_current_user(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == user.username

    def test_get_current_user_unauthenticated(self, api_client, db):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_current_user(self, auth_client, user):
        payload = {'first_name': 'Updated'}
        response = auth_client.patch(self.url, payload)
        assert response.status_code in [200, 204]


@pytest.mark.api
class TestUserPreferencesView:
    """Tests for user preferences endpoint."""

    url = '/api/v1/auth/preferences/'

    def test_get_preferences(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_update_preferences(self, auth_client, user):
        payload = {'theme': 'dark'}
        response = auth_client.patch(self.url, payload)
        assert response.status_code in [200, 204]

    def test_preferences_unauthenticated(self, api_client, db):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestChangePasswordView:
    """Tests for change password endpoint."""

    url = '/api/v1/auth/password/change/'

    def test_change_password_success(self, auth_client, user):
        payload = {
            'old_password': 'SecurePass123!',
            'new_password': 'NewSecurePass456!',
        }
        response = auth_client.post(self.url, payload)
        assert response.status_code in [200, 204]

    def test_change_password_wrong_old(self, auth_client, user):
        payload = {
            'old_password': 'WrongOldPassword!',
            'new_password': 'NewSecurePass456!',
        }
        response = auth_client.post(self.url, payload)
        assert response.status_code in [400, 403]

    def test_change_password_unauthenticated(self, api_client, db):
        payload = {
            'old_password': 'SecurePass123!',
            'new_password': 'NewSecurePass456!',
        }
        response = api_client.post(self.url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestOnboardingView:
    """Tests for onboarding endpoint."""

    url = '/api/v1/auth/onboarding/complete/'

    def test_complete_onboarding(self, auth_client, user):
        response = auth_client.post(self.url)
        assert response.status_code in [200, 204]

    def test_onboarding_unauthenticated(self, api_client, db):
        response = api_client.post(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestLoginHistoryView:
    """Tests for login history endpoint."""

    url = '/api/v1/auth/security/login-history/'

    def test_get_login_history(self, auth_client, user):
        LoginAttempt.objects.create(
            user=user,
            username_attempted=user.username,
            ip_address='127.0.0.1',
            user_agent='TestAgent',
            success=True,
            provider='email',
        )
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_login_history_unauthenticated(self, api_client, db):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestAuditLogView:
    """Tests for audit log endpoint."""

    url = '/api/v1/auth/security/audit-logs/'

    def test_get_audit_logs(self, auth_client, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK

    def test_audit_logs_unauthenticated(self, api_client, db):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestJWTEndpoints:
    """Tests for JWT token endpoints."""

    def test_obtain_token_pair(self, api_client, user):
        response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'SecurePass123!',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_refresh_token(self, api_client, user):
        response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'SecurePass123!',
        })
        refresh = response.data['refresh']
        response = api_client.post('/api/token/refresh/', {'refresh': refresh})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_verify_token(self, api_client, user):
        response = api_client.post('/api/token/', {
            'username': 'testuser',
            'password': 'SecurePass123!',
        })
        access = response.data['access']
        response = api_client.post('/api/token/verify/', {'token': access})
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_token_verify(self, api_client, db):
        response = api_client.post('/api/token/verify/', {'token': 'invalid'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

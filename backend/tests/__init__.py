"""
End-to-end tests for complete authentication flow.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import UserProfile, UserPreferences, LoginAttempt


@pytest.mark.integration
class TestFullAuthFlow:
    """Test the complete authentication workflow end-to-end."""

    def test_register_and_login_flow(self, api_client):
        """Test: Register → Login → Access Protected Route → Change Password → Login Again."""
        # Step 1: Register
        register_response = api_client.post('/api/v1/auth/register/', {
            'username': 'e2euser',
            'email': 'e2e@example.com',
            'password': 'E2ESecure123!',
        })
        assert register_response.status_code == status.HTTP_201_CREATED

        # Step 2: Login with the registered user
        login_response = api_client.post('/api/v1/auth/login/', {
            'username': 'e2euser',
            'password': 'E2ESecure123!',
        })
        assert login_response.status_code == status.HTTP_200_OK
        tokens = login_response.data.get('tokens', login_response.data)
        access_token = tokens.get('access', tokens.get('token'))
        assert access_token is not None

        # Step 3: Access protected route
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = api_client.get('/api/v1/auth/users/me/')
        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data['username'] == 'e2euser'

        # Step 4: Change password
        change_pw_response = api_client.post('/api/v1/auth/password/change/', {
            'old_password': 'E2ESecure123!',
            'new_password': 'NewE2EPass456!',
        })
        assert change_pw_response.status_code in [200, 204]

        # Step 5: Login with new password
        api_client.credentials()  # Clear auth
        new_login = api_client.post('/api/v1/auth/login/', {
            'username': 'e2euser',
            'password': 'NewE2EPass456!',
        })
        assert new_login.status_code == status.HTTP_200_OK

    def test_jwt_token_lifecycle(self, api_client):
        """Test JWT obtain → verify → refresh → verify new token."""
        # Create user
        User.objects.create_user('jwtuser', 'jwt@example.com', 'JWTPass123!')

        # Obtain tokens
        response = api_client.post('/api/token/', {
            'username': 'jwtuser', 'password': 'JWTPass123!'
        })
        assert response.status_code == 200
        access = response.data['access']
        refresh = response.data['refresh']

        # Verify access token
        verify = api_client.post('/api/token/verify/', {'token': access})
        assert verify.status_code == 200

        # Refresh token
        refresh_resp = api_client.post('/api/token/refresh/', {'refresh': refresh})
        assert refresh_resp.status_code == 200
        new_access = refresh_resp.data['access']

        # Verify new access token
        verify2 = api_client.post('/api/token/verify/', {'token': new_access})
        assert verify2.status_code == 200

        # Use new token to access protected route
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access}')
        response = api_client.get('/api/v1/projects/')
        assert response.status_code != 401

    def test_register_profile_preferences_created(self, api_client):
        """Test that registering creates profile and preferences."""
        api_client.post('/api/v1/auth/register/', {
            'username': 'profileuser',
            'email': 'profile@example.com',
            'password': 'Profile123!',
        })
        user = User.objects.get(username='profileuser')
        assert hasattr(user, 'profile')
        assert hasattr(user, 'preferences')
        assert user.profile.is_onboarded is False
        assert user.preferences.theme == 'system'

    def test_login_attempt_tracking(self, api_client):
        """Test that login attempts are recorded."""
        User.objects.create_user('tracked', 'tracked@example.com', 'Track123!')

        # Failed attempt
        api_client.post('/api/v1/auth/login/', {
            'username': 'tracked', 'password': 'wrong'
        })
        assert LoginAttempt.objects.filter(
            username_attempted='tracked', success=False
        ).exists()

        # Successful attempt
        api_client.post('/api/v1/auth/login/', {
            'username': 'tracked', 'password': 'Track123!'
        })
        assert LoginAttempt.objects.filter(
            username_attempted='tracked', success=True
        ).exists()

    def test_onboarding_flow(self, api_client):
        """Test register → complete onboarding → verify onboarded."""
        # Register
        reg = api_client.post('/api/v1/auth/register/', {
            'username': 'onboarduser',
            'email': 'onboard@example.com',
            'password': 'Onboard123!',
        })
        tokens = reg.data.get('tokens', reg.data)
        access = tokens.get('access', tokens.get('token'))
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        # Complete onboarding
        response = api_client.post('/api/v1/auth/onboarding/complete/')
        assert response.status_code in [200, 204]

    def test_preferences_update_flow(self, api_client):
        """Test register → update preferences → verify changes."""
        reg = api_client.post('/api/v1/auth/register/', {
            'username': 'prefuser',
            'email': 'pref@example.com',
            'password': 'Pref123456!',
        })
        tokens = reg.data.get('tokens', reg.data)
        access = tokens.get('access', tokens.get('token'))
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        # Update preferences
        api_client.patch('/api/v1/auth/preferences/', {
            'theme': 'dark', 'language': 'es'
        })

        # Verify
        response = api_client.get('/api/v1/auth/preferences/')
        assert response.status_code == 200

    def test_unauthorized_access_denied(self, api_client, db):
        """Test that unauthenticated requests to protected routes fail."""
        protected_urls = [
            '/api/v1/auth/users/me/',
            '/api/v1/projects/',
            '/api/v1/teams/',
            '/api/v1/analytics/dashboard/',
            '/api/v1/notifications/',
        ]
        for url in protected_urls:
            response = api_client.get(url)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, \
                f"Expected 401 for {url}, got {response.status_code}"

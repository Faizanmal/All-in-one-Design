"""
Unit tests for accounts serializers.
"""
import pytest
from django.contrib.auth.models import User
from accounts.serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserPreferencesSerializer,
    ChangePasswordSerializer,
)


@pytest.mark.unit
class TestRegisterSerializer:
    """Tests for the RegisterSerializer."""

    def test_valid_data(self, db):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_username(self, db):
        data = {'email': 'x@x.com', 'password': 'SecurePass123!'}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_email(self, db):
        data = {'username': 'user', 'password': 'SecurePass123!'}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_password(self, db):
        data = {'username': 'user', 'email': 'x@x.com'}
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_duplicate_username(self, user):
        data = {
            'username': user.username,
            'email': 'other@example.com',
            'password': 'SecurePass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()

    def test_duplicate_email(self, user):
        data = {
            'username': 'otheruser',
            'email': user.email,
            'password': 'SecurePass123!',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.unit
class TestUserProfileSerializer:
    """Tests for UserProfileSerializer."""

    def test_serialize_profile(self, user):
        serializer = UserProfileSerializer(user.profile)
        data = serializer.data
        assert 'display_name' in data
        assert 'is_email_verified' in data

    def test_update_display_name(self, user):
        serializer = UserProfileSerializer(
            user.profile, data={'display_name': 'New Name'}, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        user.profile.refresh_from_db()
        assert user.profile.display_name == 'New Name'


@pytest.mark.unit
class TestUserPreferencesSerializer:
    """Tests for UserPreferencesSerializer."""

    def test_serialize_preferences(self, user):
        serializer = UserPreferencesSerializer(user.preferences)
        data = serializer.data
        assert data['theme'] == 'system'
        assert data['language'] == 'en'

    def test_update_theme(self, user):
        serializer = UserPreferencesSerializer(
            user.preferences, data={'theme': 'dark'}, partial=True
        )
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        user.preferences.refresh_from_db()
        assert user.preferences.theme == 'dark'

    def test_invalid_theme(self, user):
        serializer = UserPreferencesSerializer(
            user.preferences, data={'theme': 'invalid'}, partial=True
        )
        assert not serializer.is_valid()

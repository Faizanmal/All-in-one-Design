"""
Unit tests for accounts models.
"""
import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import (
    UserProfile, UserPreferences, EmailVerificationToken,
    PasswordResetToken, LoginAttempt, AuditLog
)


@pytest.mark.unit
class TestUserProfile:
    """Tests for UserProfile model."""

    def test_profile_auto_created_on_user_creation(self, user):
        """Profile should be auto-created via signal when user is created."""
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, UserProfile)

    def test_profile_str(self, user):
        assert str(user.profile) == f"Profile: {user.username}"

    def test_profile_default_values(self, user):
        profile = user.profile
        assert profile.display_name == '' or profile.display_name is not None
        assert profile.is_email_verified is False
        assert profile.is_onboarded is False
        assert profile.storage_used_bytes == 0
        assert profile.total_designs_created == 0
        assert profile.total_ai_requests == 0

    def test_full_name_with_display_name(self, user):
        user.profile.display_name = 'Custom Name'
        user.profile.save()
        assert user.profile.full_name == 'Custom Name'

    def test_full_name_without_display_name(self, user):
        user.profile.display_name = ''
        user.profile.save()
        expected = f"{user.first_name} {user.last_name}".strip() or user.username
        assert user.profile.full_name == expected

    def test_storage_used_mb(self, user):
        user.profile.storage_used_bytes = 10 * 1024 * 1024  # 10 MB
        user.profile.save()
        assert user.profile.storage_used_mb == 10.0

    def test_storage_used_mb_zero(self, user):
        assert user.profile.storage_used_mb == 0.0

    def test_profile_update_tracking(self, user):
        profile = user.profile
        profile.total_designs_created = 5
        profile.total_ai_requests = 10
        profile.save()
        profile.refresh_from_db()
        assert profile.total_designs_created == 5
        assert profile.total_ai_requests == 10


@pytest.mark.unit
class TestUserPreferences:
    """Tests for UserPreferences model."""

    def test_preferences_auto_created(self, user):
        assert hasattr(user, 'preferences')
        assert isinstance(user.preferences, UserPreferences)

    def test_default_theme(self, user):
        assert user.preferences.theme == 'system'

    def test_default_language(self, user):
        assert user.preferences.language == 'en'

    def test_default_canvas_size(self, user):
        prefs = user.preferences
        assert prefs.default_canvas_width == 1920
        assert prefs.default_canvas_height == 1080

    def test_default_auto_save(self, user):
        assert user.preferences.auto_save is True
        assert user.preferences.auto_save_interval == 30

    def test_update_theme(self, user):
        user.preferences.theme = 'dark'
        user.preferences.save()
        user.preferences.refresh_from_db()
        assert user.preferences.theme == 'dark'

    def test_notification_defaults(self, user):
        prefs = user.preferences
        assert prefs.email_notifications is True
        assert prefs.push_notifications is True


@pytest.mark.unit
class TestEmailVerificationToken:
    """Tests for EmailVerificationToken model."""

    def test_create_token(self, user):
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        assert token.token is not None
        assert token.is_used is False

    def test_token_uniqueness(self, user):
        t1 = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        t2 = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        assert t1.token != t2.token

    def test_token_expiry(self, user):
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() - timezone.timedelta(hours=1),
        )
        assert token.expires_at < timezone.now()


@pytest.mark.unit
class TestPasswordResetToken:
    """Tests for PasswordResetToken model."""

    def test_create_reset_token(self, user):
        token = PasswordResetToken.objects.create(
            user=user,
            token='abc123',
            expires_at=timezone.now() + timezone.timedelta(hours=1),
            ip_address='127.0.0.1',
        )
        assert token.is_used is False
        assert token.ip_address == '127.0.0.1'


@pytest.mark.unit
class TestLoginAttempt:
    """Tests for LoginAttempt model."""

    def test_successful_login_attempt(self, user):
        attempt = LoginAttempt.objects.create(
            user=user,
            username_attempted=user.username,
            ip_address='127.0.0.1',
            user_agent='TestAgent/1.0',
            success=True,
            provider='email',
        )
        assert attempt.success is True
        assert attempt.failure_reason == '' or attempt.failure_reason is None or attempt.failure_reason == ''

    def test_failed_login_attempt(self, db):
        attempt = LoginAttempt.objects.create(
            username_attempted='nonexistent',
            ip_address='192.168.1.1',
            user_agent='TestAgent/1.0',
            success=False,
            failure_reason='invalid_credentials',
            provider='email',
        )
        assert attempt.success is False
        assert attempt.user is None


@pytest.mark.unit
class TestAuditLog:
    """Tests for AuditLog model."""

    def test_create_audit_log(self, user):
        log = AuditLog.objects.create(
            user=user,
            action='login',
            resource_type='user',
            resource_id=str(user.id),
            ip_address='127.0.0.1',
        )
        assert log.action == 'login'
        assert log.user == user

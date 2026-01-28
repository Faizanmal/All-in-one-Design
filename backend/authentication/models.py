"""
Authentication Models for Multi-Provider OAuth Support
Supports Google OAuth, GitHub OAuth, and Firebase Authentication
"""
import uuid
import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class OAuthProvider(models.TextChoices):
    """Supported OAuth providers"""
    GOOGLE = 'google', 'Google'
    GITHUB = 'github', 'GitHub'
    FIREBASE = 'firebase', 'Firebase'


class OAuthConnection(models.Model):
    """
    Stores OAuth provider connections for users
    Allows multiple providers per user account
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='oauth_connections'
    )
    provider = models.CharField(
        max_length=20,
        choices=OAuthProvider.choices
    )
    provider_user_id = models.CharField(max_length=255)
    provider_email = models.EmailField(blank=True, null=True)
    provider_username = models.CharField(max_length=255, blank=True, null=True)
    access_token_encrypted = models.TextField(blank=True, null=True)
    refresh_token_encrypted = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    scopes = models.JSONField(default=list, blank=True)
    profile_data = models.JSONField(default=dict, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['provider', 'provider_user_id']
        indexes = [
            models.Index(fields=['user', 'provider']),
            models.Index(fields=['provider', 'provider_user_id']),
        ]
        ordering = ['-is_primary', '-last_used_at']

    def __str__(self):
        return f"{self.user.email} - {self.provider}"

    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

    def is_token_expired(self):
        """Check if access token is expired"""
        if not self.token_expires_at:
            return True
        return timezone.now() >= self.token_expires_at


class OAuthState(models.Model):
    """
    Temporary storage for OAuth state tokens
    Used to prevent CSRF attacks during OAuth flow
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(max_length=128, unique=True, db_index=True)
    provider = models.CharField(max_length=20, choices=OAuthProvider.choices)
    redirect_uri = models.URLField()
    code_verifier = models.CharField(max_length=128, blank=True, null=True)  # For PKCE
    nonce = models.CharField(max_length=128, blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['state']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"OAuth State for {self.provider} - {self.state[:8]}..."

    @classmethod
    def create_state(cls, provider, redirect_uri, ip_address=None, user_agent=None, **extra_data):
        """Create a new OAuth state with expiration"""
        state = secrets.token_urlsafe(48)
        code_verifier = secrets.token_urlsafe(64)  # For PKCE
        nonce = secrets.token_urlsafe(32)
        
        return cls.objects.create(
            state=state,
            provider=provider,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
            nonce=nonce,
            extra_data=extra_data,
            expires_at=timezone.now() + timedelta(minutes=10),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def is_expired(self):
        """Check if state is expired"""
        return timezone.now() >= self.expires_at

    def mark_used(self):
        """Mark state as used"""
        self.used = True
        self.save(update_fields=['used'])


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring and brute force prevention
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    user_agent = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True, null=True)
    provider = models.CharField(max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_suspicious = models.BooleanField(default=False)
    risk_score = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.email} - {status} - {self.timestamp}"

    @classmethod
    def get_failed_attempts(cls, email=None, ip_address=None, minutes=30):
        """Get count of failed attempts in time window"""
        since = timezone.now() - timedelta(minutes=minutes)
        query = cls.objects.filter(success=False, timestamp__gte=since)
        
        if email:
            query = query.filter(email=email)
        if ip_address:
            query = query.filter(ip_address=ip_address)
        
        return query.count()


class UserSecurityProfile(models.Model):
    """
    Extended security profile for users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='security_profile'
    )
    
    # Two-Factor Authentication
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret_encrypted = models.TextField(blank=True, null=True)
    two_factor_backup_codes_encrypted = models.TextField(blank=True, null=True)
    two_factor_method = models.CharField(
        max_length=20,
        choices=[
            ('totp', 'Authenticator App'),
            ('sms', 'SMS'),
            ('email', 'Email'),
        ],
        default='totp'
    )
    
    # Security Settings
    require_password_change = models.BooleanField(default=False)
    password_changed_at = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    last_login_user_agent = models.TextField(blank=True, null=True)
    
    # Account Status
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(blank=True, null=True)
    locked_reason = models.CharField(max_length=255, blank=True, null=True)
    failed_login_count = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(blank=True, null=True)
    
    # Trusted Devices
    trusted_devices = models.JSONField(default=list, blank=True)
    
    # Session Management
    active_sessions_count = models.IntegerField(default=0)
    max_sessions_allowed = models.IntegerField(default=5)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Security Profile'
        verbose_name_plural = 'User Security Profiles'

    def __str__(self):
        return f"Security Profile: {self.user.email}"

    def is_account_locked(self):
        """Check if account is locked"""
        if not self.is_locked:
            return False
        if self.lockout_until and timezone.now() >= self.lockout_until:
            # Auto-unlock if lockout period passed
            self.unlock_account()
            return False
        return True

    def lock_account(self, reason="Too many failed login attempts", duration_minutes=30):
        """Lock the account"""
        self.is_locked = True
        self.locked_at = timezone.now()
        self.locked_reason = reason
        self.lockout_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['is_locked', 'locked_at', 'locked_reason', 'lockout_until'])

    def unlock_account(self):
        """Unlock the account"""
        self.is_locked = False
        self.locked_at = None
        self.locked_reason = None
        self.lockout_until = None
        self.failed_login_count = 0
        self.save(update_fields=[
            'is_locked', 'locked_at', 'locked_reason', 
            'lockout_until', 'failed_login_count'
        ])

    def increment_failed_login(self):
        """Increment failed login counter"""
        self.failed_login_count += 1
        self.save(update_fields=['failed_login_count'])
        
        # Auto-lock after 5 failed attempts
        if self.failed_login_count >= 5:
            self.lock_account()

    def reset_failed_login(self):
        """Reset failed login counter"""
        self.failed_login_count = 0
        self.save(update_fields=['failed_login_count'])


class APIKey(models.Model):
    """
    API Keys for programmatic access
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    name = models.CharField(max_length=100)
    key_prefix = models.CharField(max_length=8)  # First 8 chars for identification
    key_hash = models.CharField(max_length=128)  # Hashed full key
    scopes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    last_used_ip = models.GenericIPAddressField(blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    rate_limit = models.IntegerField(default=1000)  # Requests per hour
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['key_prefix']),
            models.Index(fields=['user', 'is_active']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"

    @classmethod
    def generate_key(cls):
        """Generate a new API key"""
        return f"aidt_{secrets.token_urlsafe(32)}"

    def is_expired(self):
        """Check if key is expired"""
        if not self.expires_at:
            return False
        return timezone.now() >= self.expires_at

    def increment_usage(self, ip_address=None):
        """Increment usage counter"""
        self.usage_count += 1
        self.last_used_at = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.save(update_fields=['usage_count', 'last_used_at', 'last_used_ip'])


class SecurityAuditLog(models.Model):
    """
    Comprehensive security audit logging
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_audit_logs'
    )
    
    # Event Details
    event_type = models.CharField(max_length=50, db_index=True)
    event_category = models.CharField(
        max_length=30,
        choices=[
            ('authentication', 'Authentication'),
            ('authorization', 'Authorization'),
            ('data_access', 'Data Access'),
            ('data_modification', 'Data Modification'),
            ('security_change', 'Security Change'),
            ('system', 'System'),
        ]
    )
    event_status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failure', 'Failure'),
            ('warning', 'Warning'),
        ]
    )
    
    # Request Context
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    request_method = models.CharField(max_length=10, blank=True, null=True)
    request_path = models.TextField(blank=True, null=True)
    
    # Event Data
    description = models.TextField()
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Risk Assessment
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='low'
    )
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['risk_level', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"

    @classmethod
    def log_event(cls, event_type, event_category, event_status, description, 
                  user=None, request=None, risk_level='low', **kwargs):
        """Helper method to create audit log entries"""
        data = {
            'event_type': event_type,
            'event_category': event_category,
            'event_status': event_status,
            'description': description,
            'user': user,
            'risk_level': risk_level,
            'extra_data': kwargs.get('extra_data', {}),
        }
        
        if request:
            data['ip_address'] = cls._get_client_ip(request)
            data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            data['request_method'] = request.method
            data['request_path'] = request.path
        
        if 'old_value' in kwargs:
            data['old_value'] = kwargs['old_value']
        if 'new_value' in kwargs:
            data['new_value'] = kwargs['new_value']
        
        return cls.objects.create(**data)

    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

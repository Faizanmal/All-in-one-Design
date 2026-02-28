"""
User Profile, Preferences, and Account Management Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
import secrets
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal info
    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, default='')
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(
        max_length=20, blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    job_title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=150, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Account status
    is_email_verified = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)
    
    # Usage tracking
    storage_used_bytes = models.BigIntegerField(default=0)
    total_designs_created = models.PositiveIntegerField(default=0)
    total_ai_requests = models.PositiveIntegerField(default=0)
    last_active_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_email_verified']),
        ]
    
    def __str__(self):
        return f"Profile: {self.user.username}"
    
    @property
    def full_name(self):
        return self.display_name or f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def storage_used_mb(self):
        return round(self.storage_used_bytes / (1024 * 1024), 2)


class UserPreferences(models.Model):
    """User-specific preferences and settings"""
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ]
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('ja', 'Japanese'),
        ('zh', 'Chinese'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # UI Preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='system')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    
    # Editor Preferences
    default_canvas_width = models.IntegerField(default=1920)
    default_canvas_height = models.IntegerField(default=1080)
    default_background_color = models.CharField(max_length=20, default='#FFFFFF')
    show_grid = models.BooleanField(default=True)
    snap_to_grid = models.BooleanField(default=True)
    grid_size = models.IntegerField(default=10)
    show_rulers = models.BooleanField(default=True)
    auto_save = models.BooleanField(default=True)
    auto_save_interval = models.IntegerField(default=30, help_text="Auto-save interval in seconds")
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notify_on_comment = models.BooleanField(default=True)
    notify_on_mention = models.BooleanField(default=True)
    notify_on_share = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    weekly_digest = models.BooleanField(default=True)
    
    # AI Preferences
    preferred_ai_style = models.CharField(max_length=50, default='modern')
    preferred_design_type = models.CharField(max_length=50, default='ui_ux')
    ai_suggestions_enabled = models.BooleanField(default=True)
    
    # Accessibility
    high_contrast = models.BooleanField(default=False)
    reduced_motion = models.BooleanField(default=False)
    font_size_scale = models.FloatField(default=1.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User preferences"
    
    def __str__(self):
        return f"Preferences: {self.user.username}"


class EmailVerificationToken(models.Model):
    """Tokens for email verification"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"Email token for {self.user.username}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Tokens for password reset"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64, unique=True, editable=False)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    def __str__(self):
        return f"Password reset token for {self.user.username}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)


class LoginAttempt(models.Model):
    """Track login attempts for security"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_attempts', null=True, blank=True)
    username_attempted = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    provider = models.CharField(max_length=20, blank=True, default='email')
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['success']),
        ]
    
    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{status} login: {self.username_attempted} @ {self.ip_address}"


class AuditLog(models.Model):
    """Comprehensive audit logging for security and compliance"""
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('email_verify', 'Email Verification'),
        ('profile_update', 'Profile Update'),
        ('project_create', 'Project Created'),
        ('project_update', 'Project Updated'),
        ('project_delete', 'Project Deleted'),
        ('project_share', 'Project Shared'),
        ('export', 'Export'),
        ('ai_request', 'AI Request'),
        ('team_create', 'Team Created'),
        ('team_member_add', 'Team Member Added'),
        ('team_member_remove', 'Team Member Removed'),
        ('role_change', 'Role Changed'),
        ('subscription_change', 'Subscription Changed'),
        ('api_key_create', 'API Key Created'),
        ('api_key_revoke', 'API Key Revoked'),
        ('settings_change', 'Settings Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.user}: {self.get_action_display()} @ {self.timestamp}"
    
    @classmethod
    def log(cls, user, action, resource_type='', resource_id='', details=None, request=None):
        """Convenience method to create audit log entries"""
        ip_address = None
        user_agent = ''
        if request:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            if ip_address and ',' in ip_address:
                ip_address = ip_address.split(',')[0].strip()
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )


# Signal to auto-create profile and preferences


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile and UserPreferences when a new User is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserPreferences.objects.get_or_create(user=instance)

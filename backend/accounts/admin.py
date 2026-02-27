from django.contrib import admin
from .models import (
    UserProfile, UserPreferences, EmailVerificationToken,
    PasswordResetToken, LoginAttempt, AuditLog
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'is_email_verified', 'is_onboarded', 'total_designs_created', 'last_active_at']
    list_filter = ['is_email_verified', 'is_onboarded']
    search_fields = ['user__username', 'user__email', 'display_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'theme', 'language', 'auto_save']
    list_filter = ['theme', 'language']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['username_attempted', 'ip_address', 'success', 'provider', 'timestamp']
    list_filter = ['success', 'provider']
    search_fields = ['username_attempted', 'ip_address']
    readonly_fields = ['timestamp']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'resource_type', 'resource_id', 'ip_address', 'timestamp']
    list_filter = ['action', 'resource_type']
    search_fields = ['user__username', 'resource_id']
    readonly_fields = ['timestamp']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_used', 'created_at', 'expires_at']
    list_filter = ['is_used']
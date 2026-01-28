from django.contrib import admin
from .models import (
    IntegrationProvider, UserIntegration, SlackIntegration, JiraIntegration,
    AdobeIntegration, GoogleDriveIntegration, DropboxIntegration,
    NotionIntegration, WordPressIntegration, WebhookEndpoint, WebhookLog,
    ZapierIntegration, IntegrationSync
)


@admin.register(IntegrationProvider)
class IntegrationProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'provider_type', 'is_active', 'is_premium']
    list_filter = ['provider_type', 'is_active', 'is_premium']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserIntegration)
class UserIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'status', 'connected_at', 'last_sync']
    list_filter = ['provider', 'status', 'connected_at']
    search_fields = ['user__username', 'provider__name']
    readonly_fields = ['id', 'connected_at', 'last_sync']


@admin.register(SlackIntegration)
class SlackIntegrationAdmin(admin.ModelAdmin):
    list_display = ['workspace_name', 'notification_channel', 'created_at']
    search_fields = ['workspace_name']


@admin.register(JiraIntegration)
class JiraIntegrationAdmin(admin.ModelAdmin):
    list_display = ['site_url', 'default_project_key', 'created_at']
    search_fields = ['site_url']


@admin.register(AdobeIntegration)
class AdobeIntegrationAdmin(admin.ModelAdmin):
    list_display = ['adobe_user_id', 'photoshop_connected', 'illustrator_connected', 'created_at']


@admin.register(GoogleDriveIntegration)
class GoogleDriveIntegrationAdmin(admin.ModelAdmin):
    list_display = ['id', 'auto_backup', 'sync_direction', 'created_at']


@admin.register(DropboxIntegration)
class DropboxIntegrationAdmin(admin.ModelAdmin):
    list_display = ['account_id', 'default_path', 'auto_backup', 'created_at']


@admin.register(NotionIntegration)
class NotionIntegrationAdmin(admin.ModelAdmin):
    list_display = ['workspace_name', 'auto_export_to_notion', 'created_at']
    search_fields = ['workspace_name']


@admin.register(WordPressIntegration)
class WordPressIntegrationAdmin(admin.ModelAdmin):
    list_display = ['site_url', 'site_name', 'default_status', 'created_at']
    search_fields = ['site_url', 'site_name']


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'url', 'is_active', 'last_triggered', 'failure_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'url', 'user__username']


@admin.register(WebhookLog)
class WebhookLogAdmin(admin.ModelAdmin):
    list_display = ['webhook', 'event_type', 'status', 'response_code', 'triggered_at']
    list_filter = ['status', 'event_type', 'triggered_at']
    readonly_fields = ['id', 'triggered_at', 'completed_at']


@admin.register(ZapierIntegration)
class ZapierIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'trigger_type', 'is_active', 'created_at']
    list_filter = ['trigger_type', 'is_active']


@admin.register(IntegrationSync)
class IntegrationSyncAdmin(admin.ModelAdmin):
    list_display = ['user_integration', 'sync_type', 'status', 'items_synced', 'started_at']
    list_filter = ['sync_type', 'status', 'created_at']
    readonly_fields = ['id', 'started_at', 'completed_at', 'created_at']

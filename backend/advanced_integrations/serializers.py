from rest_framework import serializers
from .models import (
    IntegrationProvider, UserIntegration, SlackIntegration, JiraIntegration,
    AdobeIntegration, GoogleDriveIntegration, DropboxIntegration,
    NotionIntegration, WordPressIntegration, WebhookEndpoint, WebhookLog,
    ZapierIntegration, IntegrationSync
)


class IntegrationProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProvider
        fields = [
            'id', 'name', 'slug', 'provider_type', 'icon',
            'description', 'website', 'is_active', 'is_premium',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserIntegrationSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='provider.name')
    provider_type = serializers.ReadOnlyField(source='provider.provider_type')
    provider_icon = serializers.ImageField(source='provider.icon', read_only=True)
    
    class Meta:
        model = UserIntegration
        fields = [
            'id', 'provider', 'provider_name', 'provider_type', 'provider_icon',
            'status', 'error_message', 'external_username', 'metadata',
            'settings', 'connected_at', 'last_sync'
        ]
        read_only_fields = ['id', 'status', 'error_message', 'connected_at', 'last_sync']


class SlackIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlackIntegration
        fields = [
            'id', 'workspace_id', 'workspace_name', 'notification_channel',
            'notify_on_comment', 'notify_on_approval', 'notify_on_export',
            'created_at'
        ]
        read_only_fields = ['id', 'workspace_id', 'workspace_name', 'created_at']


class JiraIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraIntegration
        fields = [
            'id', 'cloud_id', 'site_url', 'default_project_key',
            'project_mappings', 'default_issue_type', 'auto_create_issues',
            'created_at'
        ]
        read_only_fields = ['id', 'cloud_id', 'site_url', 'created_at']


class AdobeIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdobeIntegration
        fields = [
            'id', 'adobe_user_id', 'photoshop_connected', 'illustrator_connected',
            'xd_connected', 'indesign_connected', 'library_ids', 'created_at'
        ]
        read_only_fields = ['id', 'adobe_user_id', 'created_at']


class GoogleDriveIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleDriveIntegration
        fields = [
            'id', 'default_folder_id', 'auto_backup', 'backup_folder_id',
            'sync_direction', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DropboxIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropboxIntegration
        fields = [
            'id', 'account_id', 'default_path', 'auto_backup', 'created_at'
        ]
        read_only_fields = ['id', 'account_id', 'created_at']


class NotionIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotionIntegration
        fields = [
            'id', 'workspace_id', 'workspace_name', 'workspace_icon',
            'database_mappings', 'auto_export_to_notion', 'created_at'
        ]
        read_only_fields = ['id', 'workspace_id', 'workspace_name', 'workspace_icon', 'created_at']


class WordPressIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordPressIntegration
        fields = [
            'id', 'site_url', 'site_name', 'api_base',
            'default_status', 'default_category', 'created_at'
        ]
        read_only_fields = ['id', 'site_url', 'site_name', 'created_at']


class WebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookLog
        fields = [
            'id', 'event_type', 'payload', 'status',
            'response_code', 'response_body', 'triggered_at', 'completed_at'
        ]
        read_only_fields = ['id', 'triggered_at', 'completed_at']


class WebhookEndpointSerializer(serializers.ModelSerializer):
    recent_logs = WebhookLogSerializer(source='logs', many=True, read_only=True)
    
    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'name', 'url', 'events', 'secret', 'is_active',
            'last_triggered', 'failure_count', 'custom_headers',
            'recent_logs', 'created_at'
        ]
        read_only_fields = ['id', 'last_triggered', 'failure_count', 'created_at']
        extra_kwargs = {'secret': {'write_only': True}}


class ZapierIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZapierIntegration
        fields = ['id', 'hook_url', 'trigger_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class IntegrationSyncSerializer(serializers.ModelSerializer):
    provider_name = serializers.ReadOnlyField(source='user_integration.provider.name')
    
    class Meta:
        model = IntegrationSync
        fields = [
            'id', 'user_integration', 'provider_name', 'sync_type', 'status',
            'items_synced', 'items_failed', 'error_details',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'items_synced', 'items_failed', 'error_details', 'created_at']

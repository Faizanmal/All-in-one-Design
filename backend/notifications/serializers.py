from rest_framework import serializers
from .models import Notification, Webhook, WebhookDelivery, UserPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'link',
            'read', 'read_at', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class WebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'active', 'secret_key', 'headers',
            'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'last_status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_deliveries', 'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'last_status', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }


class WebhookDeliverySerializer(serializers.ModelSerializer):
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event_type', 'payload',
            'status', 'status_code', 'response_body', 'error_message',
            'attempt_count', 'delivered_at', 'created_at'
        ]
        read_only_fields = ['id', 'webhook_name', 'created_at']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            'id', 'email_on_project_shared', 'email_on_ai_complete',
            'email_on_export_ready', 'email_on_subscription_update',
            'email_on_team_invite', 'email_weekly_summary',
            'notify_project_updates', 'notify_ai_completion',
            'notify_export_ready', 'notify_team_activity',
            'marketing_emails', 'product_updates',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

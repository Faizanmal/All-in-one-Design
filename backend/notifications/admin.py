from django.contrib import admin
from .models import Notification, Webhook, WebhookDelivery, UserPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'read', 'created_at']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'read_at']


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'url', 'active', 'total_deliveries', 'last_status', 'created_at']
    list_filter = ['active', 'last_status', 'created_at']
    search_fields = ['name', 'user__username', 'url']
    readonly_fields = ['total_deliveries', 'successful_deliveries', 'failed_deliveries', 
                      'last_delivery_at', 'last_status', 'created_at', 'updated_at']


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ['webhook', 'event_type', 'status', 'status_code', 'attempt_count', 'created_at']
    list_filter = ['status', 'event_type', 'created_at']
    search_fields = ['webhook__name', 'event_type']
    readonly_fields = ['created_at', 'delivered_at']


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_on_project_shared', 'notify_project_updates', 'marketing_emails']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('project_shared', 'Project Shared'),
        ('project_update', 'Project Updated'),
        ('ai_complete', 'AI Generation Complete'),
        ('export_ready', 'Export Ready'),
        ('subscription_update', 'Subscription Update'),
        ('team_invite', 'Team Invitation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'read']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()


class Webhook(models.Model):
    """Webhook subscriptions for external integrations"""
    EVENT_TYPES = [
        ('project.created', 'Project Created'),
        ('project.updated', 'Project Updated'),
        ('project.deleted', 'Project Deleted'),
        ('export.completed', 'Export Completed'),
        ('ai.generation.completed', 'AI Generation Completed'),
        ('subscription.updated', 'Subscription Updated'),
        ('user.activity', 'User Activity'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_webhooks')
    name = models.CharField(max_length=255)
    url = models.URLField()
    events = models.JSONField(default=list, help_text="List of event types to subscribe to")
    active = models.BooleanField(default=True)
    secret_key = models.CharField(max_length=255, blank=True, help_text="Secret for HMAC signature")
    headers = models.JSONField(default=dict, blank=True, help_text="Custom headers to include")
    
    # Statistics
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    last_delivery_at = models.DateTimeField(null=True, blank=True)
    last_status = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.url}"


class WebhookDelivery(models.Model):
    """Record of webhook delivery attempts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    attempt_count = models.IntegerField(default=0)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['webhook', '-created_at']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.webhook.name} - {self.event_type} - {self.status}"


class UserPreference(models.Model):
    """User notification and communication preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_on_project_shared = models.BooleanField(default=True)
    email_on_ai_complete = models.BooleanField(default=True)
    email_on_export_ready = models.BooleanField(default=True)
    email_on_subscription_update = models.BooleanField(default=True)
    email_on_team_invite = models.BooleanField(default=True)
    email_weekly_summary = models.BooleanField(default=True)
    
    # In-app notifications
    notify_project_updates = models.BooleanField(default=True)
    notify_ai_completion = models.BooleanField(default=True)
    notify_export_ready = models.BooleanField(default=True)
    notify_team_activity = models.BooleanField(default=True)
    
    # Marketing
    marketing_emails = models.BooleanField(default=False)
    product_updates = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


# Import workflow models so Django discovers them for migrations
from .workflow_models import (  # noqa: E402, F401
    Workflow,
    WorkflowTrigger,
    WorkflowAction,
    WorkflowRun,
    WorkflowActionLog,
)

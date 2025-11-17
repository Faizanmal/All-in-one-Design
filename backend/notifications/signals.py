from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Notification, UserPreference
from .tasks import send_webhook_for_event


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create notification preferences for new users"""
    if created:
        UserPreference.objects.create(user=instance)


def create_notification(user, notification_type, title, message, link=None, metadata=None):
    """
    Helper function to create notifications
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        metadata=metadata or {}
    )
    
    # Send real-time notification via WebSocket
    from .consumers import send_notification_to_user
    send_notification_to_user(user.id, notification)
    
    return notification


def trigger_webhook(user, event_type, payload):
    """
    Helper function to trigger webhooks for events
    """
    send_webhook_for_event.delay(user.id, event_type, payload)

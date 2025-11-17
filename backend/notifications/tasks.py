import hmac
import hashlib
import json
import requests
from celery import shared_task
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Webhook, WebhookDelivery


@shared_task(bind=True, max_retries=3)
def send_webhook(self, webhook_id, event_type, payload):
    """
    Send webhook to external URL
    """
    try:
        webhook = Webhook.objects.get(id=webhook_id, active=True)
    except Webhook.DoesNotExist:
        return {'status': 'error', 'message': 'Webhook not found or inactive'}

    # Create delivery record
    delivery = WebhookDelivery.objects.create(
        webhook=webhook,
        event_type=event_type,
        payload=payload,
        status='pending'
    )

    try:
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DesignPlatform-Webhook/1.0',
            'X-Webhook-Event': event_type,
            'X-Webhook-Delivery': str(delivery.id),
        }
        
        # Add custom headers
        if webhook.headers:
            headers.update(webhook.headers)
        
        # Add HMAC signature if secret key is set
        if webhook.secret_key:
            payload_json = json.dumps(payload)
            signature = hmac.new(
                webhook.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = f'sha256={signature}'
        
        # Send request
        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        # Update delivery record
        delivery.status = 'success' if response.status_code < 400 else 'failed'
        delivery.status_code = response.status_code
        delivery.response_body = response.text[:1000]  # Limit size
        delivery.attempt_count = self.request.retries + 1
        delivery.delivered_at = timezone.now()
        delivery.save()
        
        # Update webhook statistics
        webhook.total_deliveries += 1
        if delivery.status == 'success':
            webhook.successful_deliveries += 1
        else:
            webhook.failed_deliveries += 1
        webhook.last_delivery_at = timezone.now()
        webhook.last_status = delivery.status
        webhook.save()
        
        # Retry if failed
        if response.status_code >= 400:
            raise Exception(f'Webhook delivery failed with status {response.status_code}')
        
        return {
            'status': 'success',
            'delivery_id': delivery.id,
            'status_code': response.status_code
        }
        
    except Exception as exc:
        delivery.status = 'failed'
        delivery.error_message = str(exc)
        delivery.attempt_count = self.request.retries + 1
        delivery.save()
        
        webhook.failed_deliveries += 1
        webhook.last_status = 'failed'
        webhook.save()
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            delivery.status = 'retrying'
            delivery.save()
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        
        return {
            'status': 'error',
            'message': str(exc),
            'delivery_id': delivery.id
        }


@shared_task
def send_webhook_for_event(user_id, event_type, payload):
    """
    Send webhooks to all subscribed endpoints for a user and event
    """
    try:
        user = User.objects.get(id=user_id)
        webhooks = Webhook.objects.filter(
            user=user,
            active=True
        )
        
        # Filter webhooks subscribed to this event
        matching_webhooks = [
            w for w in webhooks 
            if event_type in w.events or '*' in w.events
        ]
        
        for webhook in matching_webhooks:
            send_webhook.delay(webhook.id, event_type, payload)
        
        return {
            'status': 'success',
            'webhooks_triggered': len(matching_webhooks)
        }
        
    except User.DoesNotExist:
        return {'status': 'error', 'message': 'User not found'}


@shared_task
def cleanup_old_webhook_deliveries():
    """
    Clean up webhook deliveries older than 30 days
    """
    from datetime import timedelta
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted = WebhookDelivery.objects.filter(created_at__lt=cutoff_date).delete()
    
    return {
        'status': 'success',
        'deleted_count': deleted[0]
    }


@shared_task
def send_notification_email(user_id, notification_type, title, message):
    """
    Send email notification to user
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        user = User.objects.get(id=user_id)
        
        # Check user preferences
        try:
            preferences = user.notification_preferences
            should_send = getattr(preferences, f'email_on_{notification_type}', True)
            if not should_send:
                return {'status': 'skipped', 'reason': 'User preference'}
        except:
            pass
        
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return {'status': 'success', 'email': user.email}
        
    except User.DoesNotExist:
        return {'status': 'error', 'message': 'User not found'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

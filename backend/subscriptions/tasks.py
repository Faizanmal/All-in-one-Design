"""
Subscription Background Tasks
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('subscriptions')


@shared_task(bind=True)
def update_subscription_statuses(self):
    """Update subscription statuses (check for expirations, trials ending, etc.)"""
    try:
        from subscriptions.models import Subscription
        
        now = timezone.now()
        updated_count = 0
        
        # Check for expired trials
        expired_trials = Subscription.objects.filter(
            status='trial',
            trial_end_date__lt=now
        )
        for sub in expired_trials:
            sub.status = 'expired'
            sub.save()
            updated_count += 1
            logger.info(f'Trial expired for user {sub.user.username}')
        
        # Check for expired subscriptions
        expired_subs = Subscription.objects.filter(
            status='active',
            end_date__lt=now,
            auto_renew=False
        )
        for sub in expired_subs:
            sub.status = 'expired'
            sub.save()
            updated_count += 1
            logger.info(f'Subscription expired for user {sub.user.username}')
        
        logger.info(f'Updated {updated_count} subscription statuses')
        return {'status': 'success', 'updated': updated_count}
        
    except Exception as exc:
        logger.error(f'Failed to update subscription statuses: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True)
def send_subscription_reminders(self):
    """Send reminders for expiring subscriptions"""
    try:
        from subscriptions.models import Subscription
        from backend.tasks import send_email_notification
        
        # Find subscriptions expiring in 7 days
        reminder_date = timezone.now() + timedelta(days=7)
        expiring_soon = Subscription.objects.filter(
            status='active',
            next_billing_date__date=reminder_date.date(),
            auto_renew=True
        )
        
        sent_count = 0
        for sub in expiring_soon:
            send_email_notification.delay(
                user_email=sub.user.email,
                subject='Subscription Renewal Reminder',
                message=f'Your {sub.tier.name} subscription will renew on {sub.next_billing_date.date()}'
            )
            sent_count += 1
        
        logger.info(f'Sent {sent_count} subscription reminders')
        return {'status': 'success', 'sent': sent_count}
        
    except Exception as exc:
        logger.error(f'Failed to send reminders: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True)
def reset_monthly_quotas(self):
    """Reset monthly usage quotas on the first day of each month"""
    try:
        from subscriptions.models import UsageQuota, Subscription
        from django.db.models import Sum
        from assets.models import Asset
        
        today = timezone.now().date()
        
        # Only run on the first day of the month
        if today.day != 1:
            return {'status': 'skipped', 'message': 'Not the first day of the month'}
        
        current_month = today.replace(day=1)
        created_count = 0
        
        # Create new quotas for all active subscriptions
        for sub in Subscription.objects.filter(status__in=['active', 'trial']):
            # Calculate current storage usage
            storage = Asset.objects.filter(user=sub.user).aggregate(
                total=Sum('file_size')
            )['total'] or 0
            
            UsageQuota.objects.create(
                user=sub.user,
                month=current_month,
                ai_requests_limit=sub.tier.max_ai_requests_per_month,
                exports_limit=sub.tier.max_exports_per_month,
                storage_bytes_limit=sub.tier.max_storage_mb * 1024 * 1024,
                storage_bytes_used=storage,
            )
            created_count += 1
        
        logger.info(f'Created {created_count} new monthly quotas')
        return {'status': 'success', 'created': created_count}
        
    except Exception as exc:
        logger.error(f'Failed to reset quotas: {exc}')
        return {'status': 'error', 'message': str(exc)}

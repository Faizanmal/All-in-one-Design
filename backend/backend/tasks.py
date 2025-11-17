"""
Background Tasks
"""
from celery import shared_task
from django.utils import timezone
from django.core.management import call_command
import logging

logger = logging.getLogger('celery')


@shared_task(bind=True, max_retries=3)
def cleanup_expired_sessions(self):
    """Clean up expired sessions"""
    try:
        call_command('clearsessions')
        logger.info('Expired sessions cleaned up')
        return {'status': 'success'}
    except Exception as exc:
        logger.error(f'Failed to cleanup sessions: {exc}')
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@shared_task(bind=True)
def cleanup_old_logs(self):
    """Clean up logs older than 90 days"""
    try:
        from pathlib import Path
        from datetime import timedelta
        
        logs_dir = Path(__file__).resolve().parent.parent / 'logs'
        cutoff_date = timezone.now() - timedelta(days=90)
        
        deleted_count = 0
        if logs_dir.exists():
            for log_file in logs_dir.glob('*.log.*'):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    deleted_count += 1
        
        logger.info(f'Cleaned up {deleted_count} old log files')
        return {'status': 'success', 'deleted': deleted_count}
    except Exception as exc:
        logger.error(f'Failed to cleanup logs: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True, max_retries=3)
def send_email_notification(self, user_email, subject, message):
    """Send email notification"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        logger.info(f'Email sent to {user_email}: {subject}')
        return {'status': 'success'}
    except Exception as exc:
        logger.error(f'Failed to send email: {exc}')
        raise self.retry(exc=exc, countdown=60)  # Retry after 1 minute


@shared_task(bind=True)
def generate_system_metrics(self):
    """Generate system-wide metrics"""
    try:
        from analytics.models import SystemMetrics
        from django.contrib.auth.models import User
        from projects.models import Project
        from ai_services.models import AIGenerationRequest
        from django.db.models import Sum
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_1h = now - timedelta(hours=1)
        
        # User metrics
        active_1h = User.objects.filter(last_login__gte=last_1h).count()
        active_24h = User.objects.filter(last_login__gte=last_24h).count()
        new_24h = User.objects.filter(date_joined__gte=last_24h).count()
        
        # Project metrics
        projects_created = Project.objects.filter(created_at__gte=last_24h).count()
        projects_edited = Project.objects.filter(updated_at__gte=last_24h).count()
        
        # AI metrics
        ai_requests = AIGenerationRequest.objects.filter(created_at__gte=last_24h)
        ai_count = ai_requests.count()
        ai_tokens = ai_requests.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0
        ai_errors = ai_requests.filter(status='failed').count()
        
        # Create metrics record
        SystemMetrics.objects.create(
            active_users_1h=active_1h,
            active_users_24h=active_24h,
            new_users_24h=new_24h,
            projects_created_24h=projects_created,
            projects_edited_24h=projects_edited,
            ai_requests_24h=ai_count,
            ai_tokens_used_24h=ai_tokens,
            ai_errors_24h=ai_errors,
        )
        
        logger.info('System metrics generated')
        return {'status': 'success'}
    except Exception as exc:
        logger.error(f'Failed to generate system metrics: {exc}')
        return {'status': 'error', 'message': str(exc)}

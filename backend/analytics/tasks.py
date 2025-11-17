"""
Analytics Background Tasks
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('analytics')


@shared_task(bind=True)
def generate_daily_analytics(self):
    """Generate daily analytics for all users"""
    try:
        from analytics.models import DailyUsageStats, AIUsageMetrics
        from django.contrib.auth.models import User
        from projects.models import Project
        from django.db.models import Sum, Count
        
        yesterday = (timezone.now() - timedelta(days=1)).date()
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        yesterday_end = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.max.time()))
        
        stats_created = 0
        
        # Generate stats for all active users
        for user in User.objects.filter(is_active=True):
            # Check if stats already exist
            if DailyUsageStats.objects.filter(user=user, date=yesterday).exists():
                continue
            
            # Calculate metrics for yesterday
            projects_created = Project.objects.filter(
                user=user,
                created_at__gte=yesterday_start,
                created_at__lte=yesterday_end
            ).count()
            
            projects_edited = Project.objects.filter(
                user=user,
                updated_at__gte=yesterday_start,
                updated_at__lte=yesterday_end
            ).count()
            
            ai_usage = AIUsageMetrics.objects.filter(
                user=user,
                timestamp__gte=yesterday_start,
                timestamp__lte=yesterday_end
            ).aggregate(
                count=Count('id'),
                tokens=Sum('tokens_used'),
                cost=Sum('estimated_cost')
            )
            
            # Create daily stats
            DailyUsageStats.objects.create(
                user=user,
                date=yesterday,
                projects_created=projects_created,
                projects_edited=projects_edited,
                ai_generations_count=ai_usage['count'] or 0,
                ai_tokens_used=ai_usage['tokens'] or 0,
                ai_cost=ai_usage['cost'] or 0,
            )
            stats_created += 1
        
        logger.info(f'Generated daily analytics for {stats_created} users')
        return {'status': 'success', 'stats_created': stats_created}
        
    except Exception as exc:
        logger.error(f'Failed to generate daily analytics: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True)
def aggregate_project_analytics(self):
    """Update aggregated analytics for all projects"""
    try:
        from analytics.models import ProjectAnalytics
        from projects.models import Project
        
        updated_count = 0
        
        for project in Project.objects.all():
            analytics, created = ProjectAnalytics.objects.get_or_create(project=project)
            
            # Update component counts
            analytics.total_components = project.components.count()
            analytics.ai_generated_components = project.components.filter(ai_generated=True).count()
            analytics.total_collaborators = project.collaborators.count()
            
            analytics.save()
            updated_count += 1
        
        logger.info(f'Updated analytics for {updated_count} projects')
        return {'status': 'success', 'updated': updated_count}
        
    except Exception as exc:
        logger.error(f'Failed to aggregate project analytics: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task(bind=True)
def cleanup_old_activities(self):
    """Clean up user activities older than 90 days"""
    try:
        from analytics.models import UserActivity
        
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count, _ = UserActivity.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        logger.info(f'Cleaned up {deleted_count} old activities')
        return {'status': 'success', 'deleted': deleted_count}
        
    except Exception as exc:
        logger.error(f'Failed to cleanup activities: {exc}')
        return {'status': 'error', 'message': str(exc)}

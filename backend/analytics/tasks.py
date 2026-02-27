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


@shared_task(bind=True, max_retries=3)
def generate_analytics_report(self, execution_id: int):
    """Generate an analytics report from a report definition"""
    try:
        from analytics.advanced_analytics_models import (
            ReportExecution, UserActivityLog
        )
        from projects.models import Project
        from django.db.models import Count, Sum
        
        execution = ReportExecution.objects.get(id=execution_id)
        report = execution.report
        
        execution.status = 'running'
        execution.started_at = timezone.now()
        execution.save()
        
        # Get date range
        date_range = report.config.get('date_range', {})
        days = date_range.get('days', 30)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Build report data based on metrics
        report_data = {
            'generated_at': timezone.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'metrics': {}
        }
        
        user = report.user
        metrics = report.config.get('metrics', ['projects_created', 'ai_usage'])
        
        for metric in metrics:
            if metric == 'projects_created':
                projects = Project.objects.filter(
                    user=user,
                    created_at__range=(start_date, end_date)
                )
                report_data['metrics']['projects_created'] = {
                    'count': projects.count(),
                    'breakdown': list(projects.values('project_type').annotate(count=Count('id')))
                }
            
            elif metric == 'ai_usage':
                ai_logs = UserActivityLog.objects.filter(
                    user=user,
                    action_type='ai_generate',
                    created_at__range=(start_date, end_date)
                )
                report_data['metrics']['ai_usage'] = {
                    'total_generations': ai_logs.count(),
                    'by_day': list(ai_logs.extra({'day': "date(created_at)"}).values('day').annotate(count=Count('id')).order_by('day'))
                }
            
            elif metric == 'activity':
                activities = UserActivityLog.objects.filter(
                    user=user,
                    created_at__range=(start_date, end_date)
                )
                report_data['metrics']['activity'] = {
                    'total_actions': activities.count(),
                    'total_duration_minutes': (activities.aggregate(total=Sum('duration'))['total'] or 0) / 60000,
                    'by_type': list(activities.values('action_type').annotate(count=Count('id')))
                }
            
            elif metric == 'exports':
                exports = UserActivityLog.objects.filter(
                    user=user,
                    action_type='project_export',
                    created_at__range=(start_date, end_date)
                )
                report_data['metrics']['exports'] = {
                    'count': exports.count(),
                    'by_format': list(exports.values('metadata__format').annotate(count=Count('id')))
                }
        
        # Update execution with results
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.result = report_data
        execution.save()
        
        # Update report last run time
        report.last_run = timezone.now()
        report.save()
        
        logger.info(f'Generated report {report.id} execution {execution_id}')
        return {'status': 'success', 'execution_id': execution_id}
        
    except ReportExecution.DoesNotExist:
        logger.error(f'Report execution {execution_id} not found')
        return {'status': 'error', 'message': 'Execution not found'}
    except Exception as exc:
        logger.error(f'Failed to generate report: {exc}')
        
        # Update execution status to failed
        try:
            execution = ReportExecution.objects.get(id=execution_id)
            execution.status = 'failed'
            execution.error_message = str(exc)
            execution.completed_at = timezone.now()
            execution.save()
        except Exception:
            pass
        
        self.retry(countdown=60, exc=exc)


@shared_task(bind=True)
def analyze_design_project(self, project_id: int):
    """Analyze a design project for insights using AI"""
    try:
        from projects.models import Project
        from analytics.advanced_analytics_models import DesignInsight
        
        project = Project.objects.get(id=project_id)
        design_data = project.design_data or {}
        elements = design_data.get('elements', [])
        
        insights = []
        
        # Accessibility checks
        for element in elements:
            elem_type = element.get('type')
            elem_id = element.get('id', '')
            style = element.get('style', {})
            
            # Check for missing alt text on images
            if elem_type == 'image' and not element.get('alt'):
                insights.append(DesignInsight(
                    project=project,
                    insight_type='accessibility',
                    severity='warning',
                    title='Missing alt text',
                    description='Image element is missing alternative text for accessibility.',
                    element_id=elem_id,
                    element_type='image',
                    suggestion='Add descriptive alt text to improve accessibility for screen readers.',
                    auto_fix_available=False
                ))
            
            # Check for small font sizes
            if elem_type == 'text':
                font_size = style.get('fontSize', '16px')
                try:
                    size_num = int(str(font_size).replace('px', '').replace('pt', ''))
                    if size_num < 12:
                        insights.append(DesignInsight(
                            project=project,
                            insight_type='accessibility',
                            severity='warning',
                            title='Small font size',
                            description=f'Text has font size of {size_num}px, which may be difficult to read.',
                            element_id=elem_id,
                            element_type='text',
                            suggestion='Consider increasing font size to at least 12px for better readability.',
                            auto_fix_available=True,
                            auto_fix_data={'style_changes': {'fontSize': '14px'}}
                        ))
                except ValueError:
                    pass
        
        # Design best practice checks
        if len(elements) > 0:
            # Check for alignment issues
            x_positions = [e.get('position', {}).get('x', 0) for e in elements if e.get('position')]
            if len(set(x_positions)) > len(x_positions) * 0.8:
                insights.append(DesignInsight(
                    project=project,
                    insight_type='design_best_practice',
                    severity='info',
                    title='Inconsistent alignment',
                    description='Elements appear to have inconsistent horizontal alignment.',
                    suggestion='Consider aligning elements to a grid for a cleaner layout.',
                    auto_fix_available=False
                ))
        
        # Bulk create insights
        if insights:
            DesignInsight.objects.bulk_create(insights)
        
        logger.info(f'Analyzed project {project_id}, created {len(insights)} insights')
        return {'status': 'success', 'insights_created': len(insights)}
        
    except Project.DoesNotExist:
        logger.error(f'Project {project_id} not found for analysis')
        return {'status': 'error', 'message': 'Project not found'}
    except Exception as exc:
        logger.error(f'Failed to analyze project {project_id}: {exc}')
        return {'status': 'error', 'message': str(exc)}


@shared_task
def send_weekly_analytics_digest():
    """Send weekly analytics digest to users"""
    try:
        from django.contrib.auth.models import User
        from projects.models import Project
        from analytics.advanced_analytics_models import UserActivityLog
        from notifications.email_service import email_service
        from django.db.models import Sum
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)
        
        sent_count = 0
        
        for user in User.objects.filter(is_active=True):
            # Skip users without activity
            activities = UserActivityLog.objects.filter(
                user=user,
                created_at__range=(start_date, end_date)
            )
            
            if not activities.exists():
                continue
            
            # Calculate weekly stats
            projects_created = Project.objects.filter(
                user=user,
                created_at__range=(start_date, end_date)
            ).count()
            
            ai_generations = activities.filter(action_type='ai_generate').count()
            total_time = (activities.aggregate(total=Sum('duration'))['total'] or 0) / 3600000  # Hours
            
            context = {
                'username': user.get_full_name() or user.username,
                'period': 'This Week',
                'projects_created': projects_created,
                'ai_generations': ai_generations,
                'total_time_hours': f'{total_time:.1f}',
                'action_url': f'{email_service.app_url}/analytics',
            }
            
            email_service.send_email(
                to_emails=[user.email],
                template='weekly_digest',
                context=context
            )
            sent_count += 1
        
        logger.info(f'Sent weekly digest to {sent_count} users')
        return {'status': 'success', 'sent': sent_count}
        
    except Exception as exc:
        logger.error(f'Failed to send weekly digests: {exc}')
        return {'status': 'error', 'message': str(exc)}

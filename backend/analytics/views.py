"""
Analytics API Views and Endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import timedelta
from .models import UserActivity, ProjectAnalytics, AIUsageMetrics, DailyUsageStats
from .serializers import (
    UserActivitySerializer,
    ProjectAnalyticsSerializer,
    AIUsageMetricsSerializer,
    DailyUsageStatsSerializer
)
import logging

logger = logging.getLogger('analytics')


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """View user activity history"""
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities (last 24 hours)"""
        cutoff = timezone.now() - timedelta(hours=24)
        activities = UserActivity.objects.filter(
            user=request.user,
            timestamp__gte=cutoff
        )[:50]
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)


class AIUsageMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """View AI usage metrics"""
    serializer_class = AIUsageMetricsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIUsageMetrics.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary"""
        # Get time period from query params (default: last 30 days)
        days = int(request.query_params.get('days', 30))
        cutoff = timezone.now() - timedelta(days=days)
        
        metrics = AIUsageMetrics.objects.filter(
            user=request.user,
            timestamp__gte=cutoff
        )
        
        summary = metrics.aggregate(
            total_requests=Count('id'),
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('estimated_cost'),
            success_rate=Avg('success'),
        )
        
        # Break down by service type
        by_service = {}
        for service in ['layout_generation', 'logo_generation', 'image_generation', 
                       'color_palette', 'font_suggestion', 'design_refinement']:
            service_metrics = metrics.filter(service_type=service).aggregate(
                count=Count('id'),
                tokens=Sum('tokens_used'),
                cost=Sum('estimated_cost'),
            )
            by_service[service] = service_metrics
        
        return Response({
            'period_days': days,
            'summary': summary,
            'by_service': by_service,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get comprehensive dashboard statistics
    """
    user = request.user
    
    # Time ranges
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Project stats
    from projects.models import Project
    total_projects = Project.objects.filter(user=user).count()
    projects_this_week = Project.objects.filter(user=user, created_at__gte=week_ago).count()
    projects_this_month = Project.objects.filter(user=user, created_at__gte=month_ago).count()
    
    # AI usage stats
    ai_usage_today = AIUsageMetrics.objects.filter(user=user, timestamp__gte=today).aggregate(
        requests=Count('id'),
        tokens=Sum('tokens_used'),
        cost=Sum('estimated_cost'),
    )
    
    ai_usage_month = AIUsageMetrics.objects.filter(user=user, timestamp__gte=month_ago).aggregate(
        requests=Count('id'),
        tokens=Sum('tokens_used'),
        cost=Sum('estimated_cost'),
    )
    
    # Activity stats
    activities_today = UserActivity.objects.filter(user=user, timestamp__gte=today).count()
    activities_week = UserActivity.objects.filter(user=user, timestamp__gte=week_ago).count()
    
    # Daily stats for charts (last 30 days)
    daily_stats = DailyUsageStats.objects.filter(
        user=user,
        date__gte=(today - timedelta(days=30))
    ).order_by('date')
    
    # Asset usage
    from assets.models import Asset
    total_assets = Asset.objects.filter(user=user).count()
    storage_used = Asset.objects.filter(user=user).aggregate(
        total=Sum('file_size')
    )['total'] or 0
    
    response_data = {
        'projects': {
            'total': total_projects,
            'this_week': projects_this_week,
            'this_month': projects_this_month,
        },
        'ai_usage': {
            'today': ai_usage_today,
            'this_month': ai_usage_month,
        },
        'activity': {
            'today': activities_today,
            'this_week': activities_week,
        },
        'assets': {
            'total': total_assets,
            'storage_bytes': storage_used,
            'storage_mb': round(storage_used / (1024 * 1024), 2) if storage_used else 0,
        },
        'daily_chart_data': DailyUsageStatsSerializer(daily_stats, many=True).data,
    }
    
    logger.info('Dashboard stats requested', extra={
        'user': user.username,
        'projects': total_projects,
        'ai_requests_month': ai_usage_month['requests'],
    })
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_analytics(request, project_id):
    """
    Get detailed analytics for a specific project
    """
    from projects.models import Project
    
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    analytics, created = ProjectAnalytics.objects.get_or_create(project=project)
    
    # Get activity timeline
    activities = UserActivity.objects.filter(
        user=request.user,
        metadata__project_id=project_id
    ).order_by('-timestamp')[:20]
    
    # Get AI generations for this project
    ai_generations = AIUsageMetrics.objects.filter(
        user=request.user,
        project=project
    ).count()
    
    return Response({
        'analytics': ProjectAnalyticsSerializer(analytics).data,
        'recent_activities': UserActivitySerializer(activities, many=True).data,
        'ai_generations': ai_generations,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_activity(request):
    """
    Manually track custom activities
    
    POST /api/analytics/track/
    {
        "activity_type": "project_export",
        "metadata": {"project_id": 123, "format": "pdf"}
    }
    """
    activity_type = request.data.get('activity_type')
    metadata = request.data.get('metadata', {})
    duration_ms = request.data.get('duration_ms')
    
    if not activity_type:
        return Response(
            {'error': 'activity_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    activity = UserActivity.objects.create(
        user=request.user,
        activity_type=activity_type,
        metadata=metadata,
        duration_ms=duration_ms,
        ip_address=ip,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    
    logger.info('Activity tracked', extra={
        'user': request.user.username,
        'activity_type': activity_type,
        'metadata': metadata,
    })
    
    return Response({
        'id': activity.id,
        'activity_type': activity.activity_type,
        'timestamp': activity.timestamp,
    })

"""
Advanced Analytics Views
REST API endpoints for analytics dashboards, reports, and insights
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta

from .advanced_analytics_models import (
    AnalyticsDashboard,
    AnalyticsWidget,
    AnalyticsReport,
    ReportExecution,
    UserActivityLog,
    PerformanceMetric,
    UsageQuota,
    DesignInsight
)
from .advanced_analytics_serializers import (
    AnalyticsDashboardSerializer,
    AnalyticsWidgetSerializer,
    AnalyticsReportSerializer,
    ReportExecutionSerializer,
    UserActivityLogSerializer,
    PerformanceMetricSerializer,
    UsageQuotaSerializer,
    DesignInsightSerializer
)


class AnalyticsDashboardViewSet(viewsets.ModelViewSet):
    """Analytics dashboard management"""
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        return AnalyticsDashboard.objects.filter(
            Q(user=self.request.user) |
            Q(shared_with=self.request.user) |
            Q(is_public=True)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a dashboard"""
        dashboard = self.get_object()
        
        new_dashboard = AnalyticsDashboard.objects.create(
            user=request.user,
            name=f"{dashboard.name} (Copy)",
            description=dashboard.description,
            layout=dashboard.layout
        )
        
        return Response(
            AnalyticsDashboardSerializer(new_dashboard).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share dashboard with users"""
        dashboard = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        from django.contrib.auth.models import User
        users = User.objects.filter(id__in=user_ids)
        dashboard.shared_with.add(*users)
        
        return Response({'shared_with': [u.username for u in dashboard.shared_with.all()]})
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set as default dashboard"""
        dashboard = self.get_object()
        
        # Remove default from other dashboards
        AnalyticsDashboard.objects.filter(user=request.user, is_default=True).update(is_default=False)
        
        dashboard.is_default = True
        dashboard.save()
        
        return Response({'is_default': True})


class AnalyticsWidgetViewSet(viewsets.ModelViewSet):
    """Analytics widget management"""
    serializer_class = AnalyticsWidgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsWidget.objects.filter(
            Q(is_system=True) | Q(id__in=self.request.user.analytics_dashboards.values_list('layout', flat=True))
        )
    
    @action(detail=True, methods=['get'])
    def data(self, request, pk=None):
        """Get widget data"""
        widget = self.get_object()
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        data = self._get_metric_data(
            widget.metric_type,
            request.user,
            start_date,
            end_date,
            widget.config
        )
        
        return Response(data)
    
    def _get_metric_data(self, metric_type, user, start_date, end_date, config):
        """Get data for a specific metric"""
        from projects.models import Project
        
        group_by = config.get('groupBy', 'day')
        
        if group_by == 'day':
            trunc_fn = TruncDate
        elif group_by == 'week':
            trunc_fn = TruncWeek
        else:
            trunc_fn = TruncMonth
        
        if metric_type == 'projects_created':
            queryset = Project.objects.filter(
                user=user,
                created_at__range=(start_date, end_date)
            ).annotate(
                date=trunc_fn('created_at')
            ).values('date').annotate(count=Count('id')).order_by('date')
            
            return {
                'labels': [item['date'].isoformat() for item in queryset],
                'data': [item['count'] for item in queryset],
                'total': sum(item['count'] for item in queryset)
            }
        
        elif metric_type == 'time_spent':
            queryset = UserActivityLog.objects.filter(
                user=user,
                created_at__range=(start_date, end_date)
            ).annotate(
                date=trunc_fn('created_at')
            ).values('date').annotate(
                total_duration=Sum('duration')
            ).order_by('date')
            
            return {
                'labels': [item['date'].isoformat() for item in queryset],
                'data': [item['total_duration'] / 60000 for item in queryset],  # Convert to minutes
                'total': sum(item['total_duration'] for item in queryset) / 60000
            }
        
        elif metric_type == 'ai_generations':
            queryset = UserActivityLog.objects.filter(
                user=user,
                action_type='ai_generate',
                created_at__range=(start_date, end_date)
            ).annotate(
                date=trunc_fn('created_at')
            ).values('date').annotate(count=Count('id')).order_by('date')
            
            return {
                'labels': [item['date'].isoformat() for item in queryset],
                'data': [item['count'] for item in queryset],
                'total': sum(item['count'] for item in queryset)
            }
        
        return {'labels': [], 'data': [], 'total': 0}


class AnalyticsReportViewSet(viewsets.ModelViewSet):
    """Analytics report management"""
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """Run report immediately"""
        report = self.get_object()
        
        # Create execution record
        execution = ReportExecution.objects.create(
            report=report,
            status='pending'
        )
        
        # Queue report generation task
        from .tasks import generate_analytics_report
        generate_analytics_report.delay(execution.id)
        
        return Response({
            'execution_id': execution.id,
            'status': 'queued'
        })
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get report execution history"""
        report = self.get_object()
        executions = report.executions.all()[:20]
        serializer = ReportExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class UserActivityLogViewSet(viewsets.ModelViewSet):
    """User activity log management"""
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head']  # No update/delete
    
    def get_queryset(self):
        queryset = UserActivityLog.objects.filter(user=self.request.user)
        
        # Filter by action type
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by project
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by date range
        days = self.request.query_params.get('days')
        if days:
            start_date = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(created_at__gte=start_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            device_type=self.request.META.get('HTTP_X_DEVICE_TYPE', ''),
            browser=self.request.META.get('HTTP_USER_AGENT', '')[:100]
        )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get activity summary"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        queryset = UserActivityLog.objects.filter(
            user=request.user,
            created_at__gte=start_date
        )
        
        summary = queryset.values('action_type').annotate(
            count=Count('id'),
            total_duration=Sum('duration')
        ).order_by('-count')
        
        total_time = queryset.aggregate(total=Sum('duration'))['total'] or 0
        
        return Response({
            'by_action': list(summary),
            'total_actions': queryset.count(),
            'total_time_minutes': total_time / 60000,
            'period_days': days
        })


class UsageQuotaViewSet(viewsets.ReadOnlyModelViewSet):
    """Usage quota viewing"""
    serializer_class = UsageQuotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UsageQuota.objects.filter(
            Q(user=self.request.user) |
            Q(team__members=self.request.user)
        ).filter(
            period_end__gte=timezone.now()
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current period quotas"""
        quotas = self.get_queryset().filter(
            period_start__lte=timezone.now(),
            period_end__gte=timezone.now()
        )
        serializer = self.get_serializer(quotas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get quota usage summary"""
        quotas = self.get_queryset().filter(
            period_start__lte=timezone.now(),
            period_end__gte=timezone.now()
        )
        
        summary = []
        for quota in quotas:
            summary.append({
                'type': quota.quota_type,
                'limit': quota.limit,
                'used': quota.used,
                'remaining': max(0, quota.limit - quota.used),
                'percentage': quota.usage_percentage,
                'is_exceeded': quota.is_exceeded
            })
        
        return Response(summary)


class DesignInsightViewSet(viewsets.ModelViewSet):
    """Design insight management"""
    serializer_class = DesignInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DesignInsight.objects.filter(project__user=self.request.user)
        
        # Filter by project
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by type
        insight_type = self.request.query_params.get('type')
        if insight_type:
            queryset = queryset.filter(insight_type=insight_type)
        
        # Filter dismissed
        include_dismissed = self.request.query_params.get('include_dismissed', 'false')
        if include_dismissed.lower() != 'true':
            queryset = queryset.filter(is_dismissed=False)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss an insight"""
        insight = self.get_object()
        insight.is_dismissed = True
        insight.save()
        return Response({'status': 'dismissed'})
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply auto-fix for insight"""
        insight = self.get_object()
        
        if not insight.auto_fix_available:
            return Response(
                {'error': 'No auto-fix available for this insight'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Apply the fix to the project
        project = insight.project
        design_data = project.design_data or {}
        
        # Apply the auto-fix based on insight type
        if insight.auto_fix_data:
            fix_data = insight.auto_fix_data
            
            # Handle different fix types
            if insight.insight_type == 'accessibility':
                design_data = self._apply_accessibility_fix(design_data, insight.element_id, fix_data)
            elif insight.insight_type == 'design_best_practice':
                design_data = self._apply_design_fix(design_data, insight.element_id, fix_data)
            elif insight.insight_type == 'performance':
                design_data = self._apply_performance_fix(design_data, insight.element_id, fix_data)
            
            project.design_data = design_data
            project.save()
        
        insight.is_applied = True
        insight.save()
        
        return Response({
            'status': 'applied',
            'fix_data': insight.auto_fix_data
        })
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze a project for insights"""
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from projects.models import Project
        
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Queue AI analysis task for background processing
        from .tasks import analyze_design_project
        analyze_design_project.delay(project.id)
        
        # For now, create some basic insights
        insights_created = self._create_basic_insights(project)
        
        return Response({
            'status': 'analyzed',
            'insights_count': insights_created
        })
    
    def _create_basic_insights(self, project):
        """Create basic design insights"""
        insights = []
        design_data = project.design_data or {}
        
        # Check for missing alt text on images
        elements = design_data.get('elements', [])
        for element in elements:
            if element.get('type') == 'image' and not element.get('alt'):
                insights.append(DesignInsight(
                    project=project,
                    insight_type='accessibility',
                    severity='warning',
                    title='Missing alt text',
                    description=f"Image element is missing alternative text for accessibility.",
                    element_id=element.get('id', ''),
                    element_type='image',
                    suggestion='Add descriptive alt text to improve accessibility.',
                    auto_fix_available=False
                ))
        
        # Check for color contrast
        insights.extend(self._check_color_contrast(project, elements))
        
        # Bulk create insights
        created = DesignInsight.objects.bulk_create(insights)
        return len(created)
    
    def _check_color_contrast(self, project, elements):
        """Check color contrast for accessibility compliance"""
        insights = []
        
        for element in elements:
            if element.get('type') == 'text':
                text_color = element.get('style', {}).get('color', '#000000')
                bg_color = element.get('style', {}).get('backgroundColor', '#FFFFFF')
                
                # Calculate contrast ratio
                contrast_ratio = self._calculate_contrast_ratio(text_color, bg_color)
                
                # WCAG AA requires 4.5:1 for normal text, 3:1 for large text
                font_size = element.get('style', {}).get('fontSize', '16px')
                font_size_num = int(str(font_size).replace('px', '').replace('pt', ''))
                
                min_ratio = 3.0 if font_size_num >= 24 else 4.5
                
                if contrast_ratio < min_ratio:
                    insights.append(DesignInsight(
                        project=project,
                        insight_type='accessibility',
                        severity='warning',
                        title='Low color contrast',
                        description=f"Text has contrast ratio of {contrast_ratio:.1f}:1, but WCAG AA requires at least {min_ratio}:1",
                        element_id=element.get('id', ''),
                        element_type='text',
                        suggestion=f'Increase contrast to at least {min_ratio}:1 for accessibility compliance.',
                        auto_fix_available=True,
                        auto_fix_data={
                            'type': 'adjust_contrast',
                            'current_contrast': contrast_ratio,
                            'required_contrast': min_ratio,
                            'suggested_color': self._suggest_accessible_color(text_color, bg_color, min_ratio)
                        }
                    ))
        
        return insights
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join([c*2 for c in hex_color])
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def relative_luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        try:
            l1 = relative_luminance(hex_to_rgb(color1))
            l2 = relative_luminance(hex_to_rgb(color2))
            
            lighter = max(l1, l2)
            darker = min(l1, l2)
            
            return (lighter + 0.05) / (darker + 0.05)
        except Exception:
            return 1.0
    
    def _suggest_accessible_color(self, text_color: str, bg_color: str, min_ratio: float) -> str:
        """Suggest an accessible text color"""
        # Simple approach: if current color is too light, darken it; if too dark, lighten it
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*[max(0, min(255, int(c))) for c in rgb])
        
        try:
            rgb = hex_to_rgb(text_color)
            bg_rgb = hex_to_rgb(bg_color)
            
            # Calculate background brightness
            bg_brightness = (bg_rgb[0] * 299 + bg_rgb[1] * 587 + bg_rgb[2] * 114) / 1000
            
            # If background is light, suggest darker text; if dark, suggest lighter text
            if bg_brightness > 128:
                # Darken the text color
                factor = 0.6
                return rgb_to_hex((rgb[0] * factor, rgb[1] * factor, rgb[2] * factor))
            else:
                # Lighten the text color
                factor = 1.4
                return rgb_to_hex((min(255, rgb[0] * factor), min(255, rgb[1] * factor), min(255, rgb[2] * factor)))
        except Exception:
            return '#000000' if bg_color.lower() != '#000000' else '#FFFFFF'
    
    def _apply_accessibility_fix(self, design_data, element_id, fix_data):
        """Apply accessibility-related auto-fixes"""
        elements = design_data.get('elements', [])
        
        for element in elements:
            if element.get('id') == element_id:
                if fix_data.get('type') == 'adjust_contrast':
                    if 'style' not in element:
                        element['style'] = {}
                    element['style']['color'] = fix_data.get('suggested_color', element['style'].get('color'))
                break
        
        design_data['elements'] = elements
        return design_data
    
    def _apply_design_fix(self, design_data, element_id, fix_data):
        """Apply design best practice fixes"""
        elements = design_data.get('elements', [])
        
        for element in elements:
            if element.get('id') == element_id:
                if 'style' not in element:
                    element['style'] = {}
                
                # Apply suggested style changes
                for key, value in fix_data.get('style_changes', {}).items():
                    element['style'][key] = value
                break
        
        design_data['elements'] = elements
        return design_data
    
    def _apply_performance_fix(self, design_data, element_id, fix_data):
        """Apply performance-related fixes"""
        elements = design_data.get('elements', [])
        
        for element in elements:
            if element.get('id') == element_id:
                # Apply performance optimizations
                if fix_data.get('type') == 'optimize_image':
                    element['optimized'] = True
                    element['optimizationSettings'] = fix_data.get('settings', {})
                break
        
        design_data['elements'] = elements
        return design_data


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_overview(request):
    """
    Get overall analytics overview
    """
    from projects.models import Project
    
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Projects stats
    projects_queryset = Project.objects.filter(user=request.user)
    total_projects = projects_queryset.count()
    new_projects = projects_queryset.filter(created_at__gte=start_date).count()
    
    # Activity stats
    activity_queryset = UserActivityLog.objects.filter(
        user=request.user,
        created_at__gte=start_date
    )
    total_actions = activity_queryset.count()
    total_time = activity_queryset.aggregate(total=Sum('duration'))['total'] or 0
    
    # AI usage
    ai_generations = activity_queryset.filter(action_type='ai_generate').count()
    
    # Exports
    exports = activity_queryset.filter(action_type='project_export').count()
    
    # Most used action types
    top_actions = activity_queryset.values('action_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Daily activity trend
    daily_activity = activity_queryset.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    return Response({
        'period_days': days,
        'projects': {
            'total': total_projects,
            'new': new_projects
        },
        'activity': {
            'total_actions': total_actions,
            'total_time_hours': total_time / 3600000,
            'ai_generations': ai_generations,
            'exports': exports
        },
        'top_actions': list(top_actions),
        'daily_trend': list(daily_activity)
    })

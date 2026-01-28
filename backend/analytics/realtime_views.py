from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from datetime import timedelta

from .realtime_models import (
    Heatmap, UserFlow, DesignSession, DesignInteraction, DesignMetric,
    ElementAnalytics, ConversionGoal, ConversionEvent, CompetitorAnalysis,
    RealtimeAnalyticsDashboard, RealtimeAnalyticsReport
)
from .realtime_serializers import (
    HeatmapSerializer, UserFlowSerializer, DesignSessionSerializer,
    DesignInteractionSerializer, DesignMetricSerializer, ElementAnalyticsSerializer,
    ConversionGoalSerializer, ConversionEventSerializer, CompetitorAnalysisSerializer,
    RealtimeAnalyticsDashboardSerializer, RealtimeAnalyticsReportSerializer
)


class HeatmapViewSet(viewsets.ModelViewSet):
    """ViewSet for heatmap data"""
    serializer_class = HeatmapSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Heatmap.objects.filter(project__owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate heatmap for a project"""
        project_id = request.data.get('project_id')
        heatmap_type = request.data.get('type', 'click')
        days = request.data.get('days', 30)
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # In production, aggregate interaction data
        heatmap = Heatmap.objects.create(
            project_id=project_id,
            heatmap_type=heatmap_type,
            width=1920,
            height=1080,
            data_points=[],
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(HeatmapSerializer(heatmap).data, status=status.HTTP_201_CREATED)


class UserFlowViewSet(viewsets.ModelViewSet):
    """ViewSet for user flow analysis"""
    serializer_class = UserFlowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFlow.objects.filter(project__owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """Analyze user flow for a project"""
        project_id = request.data.get('project_id')
        
        # In production, analyze session data
        flow = UserFlow.objects.create(
            project_id=project_id,
            name='User Flow Analysis',
            steps=[],
            total_users=0,
            completion_rate=0,
            average_time=0
        )
        
        return Response(UserFlowSerializer(flow).data, status=status.HTTP_201_CREATED)


class DesignSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for design sessions"""
    serializer_class = DesignSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DesignSession.objects.filter(project__owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """Start a new session"""
        session = DesignSession.objects.create(
            project_id=request.data.get('project_id'),
            session_id=request.data.get('session_id'),
            user=request.user if request.user.is_authenticated else None,
            device_type=request.data.get('device_type', ''),
            browser=request.data.get('browser', ''),
            os=request.data.get('os', ''),
            screen_width=request.data.get('screen_width'),
            screen_height=request.data.get('screen_height'),
            started_at=timezone.now()
        )
        return Response(DesignSessionSerializer(session).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session"""
        session = self.get_object()
        session.ended_at = timezone.now()
        session.total_duration = int((session.ended_at - session.started_at).total_seconds())
        session.save()
        return Response(DesignSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def track_interaction(self, request, pk=None):
        """Track an interaction"""
        session = self.get_object()
        
        interaction = DesignInteraction.objects.create(
            session=session,
            interaction_type=request.data.get('type'),
            x=request.data.get('x'),
            y=request.data.get('y'),
            element_id=request.data.get('element_id', ''),
            element_type=request.data.get('element_type', ''),
            page_id=request.data.get('page_id', ''),
            timestamp=timezone.now(),
            metadata=request.data.get('metadata', {})
        )
        
        if request.data.get('type') == 'click':
            session.click_count += 1
            session.save()
        
        return Response(DesignInteractionSerializer(interaction).data, status=status.HTTP_201_CREATED)


class DesignMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for design metrics"""
    serializer_class = DesignMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DesignMetric.objects.filter(project__owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Get metrics overview"""
        project_id = request.query_params.get('project_id')
        period = request.query_params.get('period', 'daily')
        
        # Get latest metrics
        metrics = self.get_queryset().filter(
            project_id=project_id,
            period_type=period
        ).order_by('-period_start')[:30]
        
        return Response(DesignMetricSerializer(metrics, many=True).data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics"""
        project_id = request.query_params.get('project_id')
        days = int(request.query_params.get('days', 30))
        
        start_date = timezone.now() - timedelta(days=days)
        sessions = DesignSession.objects.filter(
            project_id=project_id,
            started_at__gte=start_date
        )
        
        return Response({
            'total_sessions': sessions.count(),
            'unique_users': sessions.values('user').distinct().count(),
            'avg_duration': sessions.aggregate(Avg('total_duration'))['total_duration__avg'] or 0,
            'total_clicks': sessions.aggregate(Sum('click_count'))['click_count__sum'] or 0,
        })


class ElementAnalyticsViewSet(viewsets.ModelViewSet):
    """ViewSet for element analytics"""
    serializer_class = ElementAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ElementAnalytics.objects.filter(project__owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def top_elements(self, request):
        """Get top performing elements"""
        project_id = request.query_params.get('project_id')
        
        elements = self.get_queryset().filter(
            project_id=project_id
        ).order_by('-attention_score')[:10]
        
        return Response(ElementAnalyticsSerializer(elements, many=True).data)


class ConversionGoalViewSet(viewsets.ModelViewSet):
    """ViewSet for conversion goals"""
    serializer_class = ConversionGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConversionGoal.objects.filter(project__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def track_conversion(self, request, pk=None):
        """Track a conversion event"""
        goal = self.get_object()
        
        event = ConversionEvent.objects.create(
            goal=goal,
            session_id=request.data.get('session_id'),
            value=request.data.get('value'),
            metadata=request.data.get('metadata', {}),
            timestamp=timezone.now()
        )
        
        return Response(ConversionEventSerializer(event).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get goal events"""
        goal = self.get_object()
        events = goal.events.all()[:100]
        return Response(ConversionEventSerializer(events, many=True).data)


class CompetitorAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for competitor analysis"""
    serializer_class = CompetitorAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CompetitorAnalysis.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze_url(self, request):
        """Analyze a competitor URL"""
        url = request.data.get('url')
        name = request.data.get('name', url)
        
        # In production, use web scraping and AI analysis
        analysis = CompetitorAnalysis.objects.create(
            user=request.user,
            name=name,
            competitor_url=url,
            design_score=85.0,
            ux_score=78.0,
            accessibility_score=72.0,
            colors_used=['#3B82F6', '#10B981', '#F59E0B'],
            fonts_used=['Inter', 'Roboto'],
            technologies=['React', 'Tailwind CSS'],
            ai_insights=[
                {'type': 'positive', 'insight': 'Clean and modern design'},
                {'type': 'improvement', 'insight': 'Could improve mobile navigation'}
            ]
        )
        
        return Response(CompetitorAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)


class RealtimeAnalyticsDashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics dashboards"""
    serializer_class = RealtimeAnalyticsDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RealtimeAnalyticsDashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set as default dashboard"""
        dashboard = self.get_object()
        
        # Remove default from others
        self.get_queryset().update(is_default=False)
        
        dashboard.is_default = True
        dashboard.save()
        
        return Response({'status': 'set_as_default'})


class RealtimeAnalyticsReportViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics reports"""
    serializer_class = RealtimeAnalyticsReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RealtimeAnalyticsReport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        report = serializer.save(user=self.request.user, status='pending')
        
        # In production, trigger async report generation
        # For now, simulate completion
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate report"""
        report = self.get_object()
        report.status = 'generating'
        report.save()
        
        # In production, trigger async generation
        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()
        
        return Response(AnalyticsReportSerializer(report).data)

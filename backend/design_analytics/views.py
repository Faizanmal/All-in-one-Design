"""
Design Analytics Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta

from .models import (
    ComponentUsage, StyleUsage, AdoptionMetric, DesignSystemHealth,
    UsageEvent, DeprecationNotice, AnalyticsDashboard
)
from .serializers import (
    ComponentUsageSerializer, StyleUsageSerializer,
    AdoptionMetricSerializer, DesignSystemHealthSerializer,
    UsageEventSerializer, DeprecationNoticeSerializer,
    AnalyticsDashboardSerializer, TrackUsageSerializer,
    AnalyticsQuerySerializer, DeprecateItemSerializer
)
from .services import AnalyticsService, ComplianceChecker


class ComponentUsageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ComponentUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ComponentUsage.objects.all()
        
        ds_id = self.request.query_params.get('design_system')
        if ds_id:
            queryset = queryset.filter(design_system_id=ds_id)
        
        return queryset


class StyleUsageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StyleUsageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = StyleUsage.objects.all()
        
        ds_id = self.request.query_params.get('design_system')
        if ds_id:
            queryset = queryset.filter(design_system_id=ds_id)
        
        style_type = self.request.query_params.get('type')
        if style_type:
            queryset = queryset.filter(style_type=style_type)
        
        return queryset


class AdoptionMetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AdoptionMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AdoptionMetric.objects.all()
        
        ds_id = self.request.query_params.get('design_system')
        if ds_id:
            queryset = queryset.filter(design_system_id=ds_id)
        
        return queryset


class DesignSystemHealthViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DesignSystemHealthSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DesignSystemHealth.objects.all()
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate fresh health score."""
        ds_id = request.data.get('design_system_id')
        if not ds_id:
            return Response({'error': 'design_system_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        result = AnalyticsService.calculate_health_score(ds_id)
        
        # Save the score
        health, _ = DesignSystemHealth.objects.update_or_create(
            design_system_id=ds_id,
            assessed_at=timezone.now().date(),
            defaults={
                'overall_score': result['overall_score'],
                'adoption_score': result['scores']['adoption'],
                'consistency_score': result['scores']['consistency'],
                'coverage_score': result['scores']['coverage'],
                'freshness_score': result['scores']['freshness'],
                'documentation_score': result['scores']['documentation'],
                'issues': result['issues'],
                'recommendations': result['recommendations']
            }
        )
        
        return Response(DesignSystemHealthSerializer(health).data)


class UsageEventViewSet(viewsets.ModelViewSet):
    serializer_class = UsageEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = UsageEvent.objects.all()
        
        ds_id = self.request.query_params.get('design_system')
        if ds_id:
            queryset = queryset.filter(design_system_id=ds_id)
        
        event_type = self.request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        return queryset[:100]  # Limit to recent events
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TrackUsageView(APIView):
    """Track usage event."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = TrackUsageSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        event = UsageEvent.objects.create(
            design_system_id=data['design_system_id'],
            event_type=data['event_type'],
            component_id=data.get('component_id', ''),
            component_name=data.get('component_name', ''),
            style_id=data.get('style_id', ''),
            style_name=data.get('style_name', ''),
            user=request.user,
            project_id=data.get('project_id'),
            metadata=data.get('metadata', {})
        )
        
        # Update component usage count
        if data.get('component_id') and data['event_type'] == 'insert':
            usage, created = ComponentUsage.objects.get_or_create(
                design_system_id=data['design_system_id'],
                component_id=data['component_id'],
                defaults={'component_name': data.get('component_name', '')}
            )
            usage.usage_count += 1
            usage.last_used_at = timezone.now()
            usage.last_used_by = request.user
            if data.get('project_id'):
                usage.last_used_in_project_id = data['project_id']
            usage.save()
        
        return Response(UsageEventSerializer(event).data, status=status.HTTP_201_CREATED)


class DeprecationNoticeViewSet(viewsets.ModelViewSet):
    serializer_class = DeprecationNoticeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeprecationNotice.objects.all()
        
        ds_id = self.request.query_params.get('design_system')
        if ds_id:
            queryset = queryset.filter(design_system_id=ds_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def notify_users(self, request, pk=None):
        """Notify affected users about deprecation."""
        notice = self.get_object()
        # In production, this would send notifications
        return Response({'message': 'Notifications sent'})


class AnalyticsDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = AnalyticsDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnalyticsDashboard.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AnalyticsSummaryView(APIView):
    """Get analytics summary for a design system."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        ds_id = request.query_params.get('design_system_id')
        if not ds_id:
            return Response({'error': 'design_system_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get adoption metrics
        adoption = AnalyticsService.calculate_adoption_rate(ds_id)
        
        # Get top components
        top_components = AnalyticsService.get_top_components(ds_id, limit=5)
        
        # Get style consistency
        style_report = AnalyticsService.get_style_consistency_report(ds_id)
        
        # Get health score
        health = AnalyticsService.calculate_health_score(ds_id)
        
        return Response({
            'adoption': adoption,
            'top_components': top_components,
            'style_consistency': style_report,
            'health': health
        })


class UsageTimelineView(APIView):
    """Get usage timeline data."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        ds_id = request.query_params.get('design_system_id')
        if not ds_id:
            return Response({'error': 'design_system_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        timeline = AnalyticsService.get_usage_timeline(ds_id, days, group_by)
        
        return Response({'timeline': timeline})


class ComplianceCheckView(APIView):
    """Check project compliance with design system."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        project_id = request.data.get('project_id')
        ds_id = request.data.get('design_system_id')
        
        if not project_id or not ds_id:
            return Response(
                {'error': 'project_id and design_system_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = ComplianceChecker.check_project_compliance(project_id, ds_id)
        
        return Response(result)

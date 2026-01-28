"""
Analytics URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .advanced_analytics_views import (
    AnalyticsDashboardViewSet,
    AnalyticsWidgetViewSet,
    AnalyticsReportViewSet,
    UserActivityLogViewSet,
    UsageQuotaViewSet,
    DesignInsightViewSet,
    analytics_overview
)
from .realtime_views import (
    HeatmapViewSet,
    UserFlowViewSet,
    DesignSessionViewSet,
    DesignMetricViewSet,
    ElementAnalyticsViewSet,
    ConversionGoalViewSet,
    RealtimeAnalyticsReportViewSet as RealtimeReportViewSet
)

router = DefaultRouter()
router.register(r'activities', views.UserActivityViewSet, basename='activity')
router.register(r'ai-usage', views.AIUsageMetricsViewSet, basename='ai-usage')

# Advanced analytics routers
router.register(r'dashboards', AnalyticsDashboardViewSet, basename='analytics-dashboard')
router.register(r'widgets', AnalyticsWidgetViewSet, basename='analytics-widget')
router.register(r'reports', AnalyticsReportViewSet, basename='analytics-report')
router.register(r'activity-logs', UserActivityLogViewSet, basename='activity-log')
router.register(r'quotas', UsageQuotaViewSet, basename='usage-quota')
router.register(r'insights', DesignInsightViewSet, basename='design-insight')

# Real-time analytics routers
router.register(r'heatmaps', HeatmapViewSet, basename='heatmap')
router.register(r'user-flows', UserFlowViewSet, basename='user-flow')
router.register(r'sessions', DesignSessionViewSet, basename='design-session')
router.register(r'metrics', DesignMetricViewSet, basename='design-metric')
router.register(r'element-analytics', ElementAnalyticsViewSet, basename='element-analytics')
router.register(r'conversion-goals', ConversionGoalViewSet, basename='conversion-goal')
router.register(r'realtime-reports', RealtimeReportViewSet, basename='realtime-report')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('projects/<int:project_id>/', views.project_analytics, name='project-analytics'),
    path('track/', views.track_activity, name='track-activity'),
    
    # Advanced analytics endpoints
    path('overview/', analytics_overview, name='analytics-overview'),
]

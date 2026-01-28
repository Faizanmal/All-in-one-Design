from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'component-usage', views.ComponentUsageViewSet, basename='component-usage')
router.register(r'style-usage', views.StyleUsageViewSet, basename='style-usage')
router.register(r'adoption', views.AdoptionMetricViewSet, basename='adoption-metric')
router.register(r'health', views.DesignSystemHealthViewSet, basename='design-system-health')
router.register(r'events', views.UsageEventViewSet, basename='usage-event')
router.register(r'deprecations', views.DeprecationNoticeViewSet, basename='deprecation-notice')
router.register(r'dashboards', views.AnalyticsDashboardViewSet, basename='analytics-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('track/', views.TrackUsageView.as_view(), name='track-usage'),
    path('summary/', views.AnalyticsSummaryView.as_view(), name='analytics-summary'),
    path('timeline/', views.UsageTimelineView.as_view(), name='usage-timeline'),
    path('compliance/', views.ComplianceCheckView.as_view(), name='compliance-check'),
]

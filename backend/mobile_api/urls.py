"""
URL configuration for Mobile API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MobileDeviceViewSet, MobileSessionViewSet, OfflineCacheViewSet,
    MobileAnnotationViewSet, MobileNotificationViewSet,
    MobilePreferenceViewSet, MobileAppVersionViewSet,
    ProjectSyncView, MobileAnalyticsView
)

app_name = 'mobile_api'

router = DefaultRouter()
router.register(r'devices', MobileDeviceViewSet, basename='device')
router.register(r'sessions', MobileSessionViewSet, basename='session')
router.register(r'cache', OfflineCacheViewSet, basename='cache')
router.register(r'annotations', MobileAnnotationViewSet, basename='annotation')
router.register(r'notifications', MobileNotificationViewSet, basename='notification')
router.register(r'preferences', MobilePreferenceViewSet, basename='preference')
router.register(r'versions', MobileAppVersionViewSet, basename='version')

urlpatterns = [
    path('', include(router.urls)),
    path('sync/projects/', ProjectSyncView.as_view(), name='project-sync'),
    path('analytics/events/', MobileAnalyticsView.as_view(), name='analytics-events'),
]

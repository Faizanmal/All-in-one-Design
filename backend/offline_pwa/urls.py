from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OfflineProjectViewSet, SyncQueueViewSet, OfflineSettingsViewSet,
    SyncLogViewSet, CachedAssetViewSet, OfflineStatusView, PWAManifestView
)

router = DefaultRouter()
router.register(r'projects', OfflineProjectViewSet, basename='offline-project')
router.register(r'sync-queue', SyncQueueViewSet, basename='sync-queue')
router.register(r'settings', OfflineSettingsViewSet, basename='offline-settings')
router.register(r'logs', SyncLogViewSet, basename='sync-log')
router.register(r'cache', CachedAssetViewSet, basename='cached-asset')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', OfflineStatusView.as_view(), name='offline-status'),
    path('manifest.json', PWAManifestView.as_view(), name='pwa-manifest'),
]

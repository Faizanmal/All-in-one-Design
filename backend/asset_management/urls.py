from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetFolderViewSet, AssetTagViewSet, EnhancedAssetViewSet,
    AssetCollectionViewSet, CDNIntegrationViewSet, BulkOperationViewSet,
    UnusedAssetView, AssetStatsView
)

router = DefaultRouter()
router.register(r'folders', AssetFolderViewSet, basename='asset-folder')
router.register(r'tags', AssetTagViewSet, basename='asset-tag')
router.register(r'items', EnhancedAssetViewSet, basename='enhanced-asset')
router.register(r'collections', AssetCollectionViewSet, basename='asset-collection')
router.register(r'cdn', CDNIntegrationViewSet, basename='cdn-integration')
router.register(r'bulk-operations', BulkOperationViewSet, basename='bulk-operation')

urlpatterns = [
    path('', include(router.urls)),
    path('unused/', UnusedAssetView.as_view(), name='unused-assets'),
    path('stats/', AssetStatsView.as_view(), name='asset-stats'),
]

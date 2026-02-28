from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet,
    ColorPaletteViewSet,
    FontFamilyViewSet,
    upload_asset,
    delete_asset
)
from .version_views import (
    AssetVersionViewSet,
    AssetCommentViewSet,
    AssetCollectionViewSet
)
from .stock_views import search_stock_assets, stock_asset_download, stock_providers

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'palettes', ColorPaletteViewSet, basename='palette')
router.register(r'fonts', FontFamilyViewSet, basename='font')
router.register(r'versions', AssetVersionViewSet, basename='asset-version')
router.register(r'comments', AssetCommentViewSet, basename='asset-comment')
router.register(r'collections', AssetCollectionViewSet, basename='asset-collection')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_asset, name='upload-asset'),
    path('assets/<int:asset_id>/delete/', delete_asset, name='delete-asset'),
    # Stock asset integration (Unsplash, Pexels, Pixabay)
    path('stock/search/', search_stock_assets, name='stock-search'),
    path('stock/download/<str:provider>/<str:asset_id>/', stock_asset_download, name='stock-download'),
    path('stock/providers/', stock_providers, name='stock-providers'),
]

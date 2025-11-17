from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet,
    ColorPaletteViewSet,
    FontFamilyViewSet,
    upload_asset,
    delete_asset
)

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'palettes', ColorPaletteViewSet, basename='palette')
router.register(r'fonts', FontFamilyViewSet, basename='font')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', upload_asset, name='upload-asset'),
    path('assets/<int:asset_id>/delete/', delete_asset, name='delete-asset'),
]

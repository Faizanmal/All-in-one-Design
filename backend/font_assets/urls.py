from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FontFamilyViewSet, FontCollectionViewSet, IconSetViewSet, IconViewSet,
    AssetLibraryViewSet, LibraryAssetViewSet, StockProviderViewSet,
    StockSearchViewSet, ColorPaletteViewSet, GradientPresetViewSet
)

router = DefaultRouter()
router.register(r'fonts', FontFamilyViewSet, basename='font')
router.register(r'font-collections', FontCollectionViewSet, basename='font-collection')
router.register(r'icon-sets', IconSetViewSet, basename='icon-set')
router.register(r'icons', IconViewSet, basename='icon')
router.register(r'libraries', AssetLibraryViewSet, basename='library')
router.register(r'assets', LibraryAssetViewSet, basename='asset')
router.register(r'stock-providers', StockProviderViewSet, basename='stock-provider')
router.register(r'stock-search', StockSearchViewSet, basename='stock-search')
router.register(r'palettes', ColorPaletteViewSet, basename='palette')
router.register(r'gradients', GradientPresetViewSet, basename='gradient')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Integration URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExternalServiceConnectionViewSet,
    ImportedAssetViewSet,
    FigmaImportViewSet,
    search_stock_assets,
    import_stock_asset,
    import_from_figma,
    export_to_figma,
    get_figma_files,
)

router = DefaultRouter()
router.register(r'connections', ExternalServiceConnectionViewSet, basename='external-connection')
router.register(r'assets', ImportedAssetViewSet, basename='imported-asset')
router.register(r'figma-imports', FigmaImportViewSet, basename='figma-import')

urlpatterns = [
    path('', include(router.urls)),
    
    # Stock assets
    path('stock/search/', search_stock_assets, name='stock-search'),
    path('stock/import/', import_stock_asset, name='stock-import'),
    
    # Figma
    path('figma/import/', import_from_figma, name='figma-import'),
    path('figma/export/<int:project_id>/', export_to_figma, name='figma-export'),
    path('figma/files/', get_figma_files, name='figma-files'),
]

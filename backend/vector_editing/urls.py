"""
Vector Editing URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'paths', views.VectorPathViewSet, basename='vector-path')
router.register(r'patterns', views.VectorPatternViewSet, basename='vector-pattern')
router.register(r'shapes', views.VectorShapeViewSet, basename='vector-shape')
router.register(r'pen-sessions', views.PenToolSessionViewSet, basename='pen-session')

urlpatterns = [
    path('', include(router.urls)),
    
    # Boolean operations
    path('boolean/', views.BooleanOperationView.as_view(), name='boolean-operation'),
    
    # Path offset
    path('offset/', views.PathOffsetView.as_view(), name='path-offset'),
    
    # Corner rounding
    path('corner-rounding/', views.CornerRoundingView.as_view(), name='corner-rounding'),
    
    # Transformations
    path('transform/', views.PathTransformView.as_view(), name='path-transform'),
    path('align/', views.PathAlignView.as_view(), name='path-align'),
    
    # Import/Export
    path('import/svg/', views.SVGImportExportView.as_view(), name='svg-import'),
    path('export/svg/', views.SVGExportView.as_view(), name='svg-export'),
]

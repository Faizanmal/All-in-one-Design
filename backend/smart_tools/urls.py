"""
Smart Tools URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'selection-presets', views.SmartSelectionPresetViewSet, basename='selection-preset')
router.register(r'rename-templates', views.RenameTemplateViewSet, basename='rename-template')
router.register(r'resize-presets', views.ResizePresetViewSet, basename='resize-preset')
router.register(r'magic-wand', views.MagicWandViewSet, basename='magic-wand')
router.register(r'operations', views.BatchOperationHistoryViewSet, basename='batch-operation')
router.register(r'selection-history', views.SelectionHistoryViewSet, basename='selection-history')

urlpatterns = [
    path('', include(router.urls)),
    
    # Smart Selection
    path('select/', views.SmartSelectionView.as_view(), name='smart-select'),
    path('select-similar/', views.SelectSimilarView.as_view(), name='select-similar'),
    path('magic-wand-select/', views.MagicWandSelectView.as_view(), name='magic-wand-select'),
    
    # Batch Operations
    path('batch-rename/', views.BatchRenameView.as_view(), name='batch-rename'),
    path('batch-resize/', views.BatchResizeView.as_view(), name='batch-resize'),
    path('batch-style/', views.BatchStyleChangeView.as_view(), name='batch-style'),
    
    # Find & Replace
    path('find-replace/', views.FindReplaceView.as_view(), name='find-replace'),
]

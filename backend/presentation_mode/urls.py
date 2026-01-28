"""
URL configuration for presentation_mode app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'presentations', views.PresentationViewSet, basename='presentation')
router.register(r'public', views.PublicPresentationViewSet, basename='public-presentation')
router.register(r'slides', views.PresentationSlideViewSet, basename='presentation-slide')
router.register(r'annotations', views.SlideAnnotationViewSet, basename='slide-annotation')
router.register(r'viewers', views.PresentationViewerViewSet, basename='presentation-viewer')
router.register(r'dev-mode', views.DevModeProjectViewSet, basename='dev-mode-project')
router.register(r'inspections', views.DevModeInspectionViewSet, basename='dev-mode-inspection')
router.register(r'export-configs', views.CodeExportConfigViewSet, basename='code-export-config')
router.register(r'export-history', views.CodeExportHistoryViewSet, basename='code-export-history')
router.register(r'measurements', views.MeasurementOverlayViewSet, basename='measurement-overlay')
router.register(r'asset-exports', views.AssetExportQueueViewSet, basename='asset-export-queue')

app_name = 'presentation_mode'

urlpatterns = [
    path('', include(router.urls)),
]

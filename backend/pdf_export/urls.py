from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PDFExportPresetViewSet, PDFExportViewSet, PrintProfileViewSet,
    SpreadViewViewSet, ImpositionLayoutViewSet, PDFTemplateViewSet,
    QuickExportView, PreflightView
)

router = DefaultRouter()
router.register(r'presets', PDFExportPresetViewSet, basename='pdf-preset')
router.register(r'exports', PDFExportViewSet, basename='pdf-export')
router.register(r'profiles', PrintProfileViewSet, basename='print-profile')
router.register(r'spreads', SpreadViewViewSet, basename='spread-view')
router.register(r'impositions', ImpositionLayoutViewSet, basename='imposition-layout')
router.register(r'templates', PDFTemplateViewSet, basename='pdf-template')

urlpatterns = [
    path('', include(router.urls)),
    path('quick-export/', QuickExportView.as_view(), name='quick-export'),
    path('preflight/', PreflightView.as_view(), name='preflight-check'),
]

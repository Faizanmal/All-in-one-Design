from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExportConfigurationViewSet, CodeExportViewSet, GenerateCodeView,
    DesignSpecViewSet, ComponentLibraryViewSet, HandoffAnnotationViewSet,
    BulkExportView
)

router = DefaultRouter()
router.register(r'configurations', ExportConfigurationViewSet, basename='export-configuration')
router.register(r'exports', CodeExportViewSet, basename='code-export')
router.register(r'specs', DesignSpecViewSet, basename='design-spec')
router.register(r'libraries', ComponentLibraryViewSet, basename='component-library')
router.register(r'annotations', HandoffAnnotationViewSet, basename='handoff-annotation')

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', GenerateCodeView.as_view(), name='generate-code'),
    path('bulk-export/', BulkExportView.as_view(), name='bulk-export'),
]

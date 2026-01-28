from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.PDFDocumentViewSet, basename='pdf-document')
router.register(r'pages', views.PDFPageViewSet, basename='pdf-page')
router.register(r'annotations', views.PDFAnnotationViewSet, basename='pdf-annotation')
router.register(r'import-jobs', views.AnnotationImportJobViewSet, basename='annotation-import-job')
router.register(r'templates', views.MarkupTemplateViewSet, basename='markup-template')
router.register(r'exports', views.PDFExportViewSet, basename='pdf-export')

urlpatterns = [
    path('', include(router.urls)),
    path('import-annotations/', views.ImportAnnotationsView.as_view(), name='import-annotations'),
    path('export-pdf/', views.ExportPDFView.as_view(), name='export-pdf'),
]

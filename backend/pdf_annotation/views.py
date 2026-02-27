"""
PDF Annotation Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from .models import (
    PDFDocument, PDFPage, PDFAnnotation,
    AnnotationImportJob, MarkupTemplate, PDFExport
)
from .serializers import (
    PDFDocumentSerializer, PDFPageSerializer, PDFAnnotationSerializer,
    AnnotationImportJobSerializer, MarkupTemplateSerializer,
    PDFExportSerializer, ImportAnnotationsSerializer, ExportPDFSerializer
)


class PDFDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = PDFDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        queryset = PDFDocument.objects.filter(user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def perform_create(self, serializer):
        doc = serializer.save(user=self.request.user)
        
        # In production, queue processing task
        doc.status = 'processing'
        doc.save()
        
        # Simulate processing - in real implementation, use Celery
        # process_pdf.delay(doc.id)
    
    @action(detail=True, methods=['get'])
    def pages(self, request, pk=None):
        """Get all pages for a document."""
        document = self.get_object()
        pages = document.pages.all()
        return Response(PDFPageSerializer(pages, many=True).data)
    
    @action(detail=True, methods=['get'])
    def annotations(self, request, pk=None):
        """Get all annotations for a document."""
        document = self.get_object()
        annotations = PDFAnnotation.objects.filter(page__document=document)
        
        # Filter by type
        annotation_type = request.query_params.get('type')
        if annotation_type:
            annotations = annotations.filter(annotation_type=annotation_type)
        
        # Filter by page
        page = request.query_params.get('page')
        if page:
            annotations = annotations.filter(page__page_number=int(page))
        
        return Response(PDFAnnotationSerializer(annotations, many=True).data)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess the PDF."""
        document = self.get_object()
        document.status = 'processing'
        document.error_message = ''
        document.save()
        
        # Queue processing task
        return Response({'message': 'Reprocessing started'})


class PDFPageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PDFPageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PDFPage.objects.filter(document__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def annotations(self, request, pk=None):
        """Get annotations for a specific page."""
        page = self.get_object()
        return Response(PDFAnnotationSerializer(page.annotations.all(), many=True).data)
    
    @action(detail=True, methods=['get'])
    def text(self, request, pk=None):
        """Get extracted text from page."""
        page = self.get_object()
        return Response({
            'text_content': page.text_content,
            'text_blocks': page.text_blocks
        })


class PDFAnnotationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PDFAnnotationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PDFAnnotation.objects.filter(page__document__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def import_to_design(self, request, pk=None):
        """Import a single annotation to design."""
        annotation = self.get_object()
        
        # In production, create design element
        # For now, mark as imported
        annotation.imported_to_design = True
        annotation.design_element_id = f"imported_{annotation.id}"
        annotation.save()
        
        return Response(PDFAnnotationSerializer(annotation).data)


class AnnotationImportJobViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationImportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnnotationImportJob.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        job = serializer.save(user=self.request.user)
        
        # Queue import task
        job.status = 'processing'
        job.started_at = timezone.now()
        job.save()
        
        # In production: import_annotations.delay(job.id)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get import job status."""
        job = self.get_object()
        return Response({
            'status': job.status,
            'progress': job.progress,
            'annotations_found': job.annotations_found,
            'annotations_imported': job.annotations_imported
        })


class ImportAnnotationsView(APIView):
    """Start annotation import job."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ImportAnnotationsSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        job = AnnotationImportJob.objects.create(
            user=request.user,
            document_id=data['document_id'],
            project_id=data['project_id'],
            settings={
                'annotation_types': data.get('annotation_types', []),
                'pages': data.get('pages', []),
                'convert_to_comments': data.get('convert_to_comments', True),
                'convert_to_shapes': data.get('convert_to_shapes', True),
                'template_id': str(data.get('template_id', ''))
            },
            status='processing',
            started_at=timezone.now()
        )
        
        return Response(AnnotationImportJobSerializer(job).data, status=status.HTTP_201_CREATED)


class MarkupTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = MarkupTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MarkupTemplate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PDFExportViewSet(viewsets.ModelViewSet):
    serializer_class = PDFExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PDFExport.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get download URL for export."""
        export = self.get_object()
        
        if export.status != 'completed' or not export.output_file:
            return Response(
                {'error': 'Export not ready'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'download_url': export.output_file.url,
            'filename': f"{export.name}.pdf",
            'file_size': export.file_size
        })


class ExportPDFView(APIView):
    """Start PDF export job."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ExportPDFSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        export = PDFExport.objects.create(
            user=request.user,
            project_id=data['project_id'],
            name=data['name'],
            settings={
                'frames': data.get('frames', []),
                'include_comments': data.get('include_comments', True),
                'comments_as_annotations': data.get('comments_as_annotations', True),
                'include_links': data.get('include_links', True),
                'resolution': data.get('resolution', 150),
                'compress_images': data.get('compress_images', True)
            },
            status='processing',
            started_at=timezone.now()
        )
        
        return Response(PDFExportSerializer(export).data, status=status.HTTP_201_CREATED)

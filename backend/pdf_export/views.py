from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import (
    PDFExportPreset, PDFExport, PrintProfile,
    SpreadView, ImpositionLayout, PDFTemplate
)
from .serializers import (
    PDFExportPresetSerializer, PDFExportSerializer, PDFExportCreateSerializer,
    PrintProfileSerializer, SpreadViewSerializer, ImpositionLayoutSerializer,
    PDFTemplateSerializer, QuickExportSerializer
)
from .services import PDFGenerator, PreflightChecker, ImpositionService


class PDFExportPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for PDF export presets"""
    serializer_class = PDFExportPresetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PDFExportPreset.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set preset as default"""
        preset = self.get_object()
        
        # Unset other defaults
        PDFExportPreset.objects.filter(
            created_by=request.user, is_default=True
        ).update(is_default=False)
        
        preset.is_default = True
        preset.save()
        
        return Response({'status': 'set as default'})
    
    @action(detail=False, methods=['get'])
    def print_ready(self, request):
        """Get print-ready presets"""
        presets = PDFExportPreset.objects.filter(
            created_by=request.user,
            color_mode='cmyk',
            bleed_enabled=True
        )
        return Response(PDFExportPresetSerializer(presets, many=True).data)


class PDFExportViewSet(viewsets.ModelViewSet):
    """ViewSet for PDF exports"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PDFExportCreateSerializer
        return PDFExportSerializer
    
    def get_queryset(self):
        return PDFExport.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        export = serializer.save(user=self.request.user)
        
        # Start PDF generation (in production, would use Celery)
        generator = PDFGenerator(export)
        try:
            generator.generate()
        except Exception:
            pass  # Error handling is done in generator
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Get download URL"""
        export = self.get_object()
        
        if export.status != 'completed':
            return Response(
                {'error': 'Export not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'file_url': export.file_url,
            'file_size': export.file_size,
            'page_count': export.page_count,
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get export status"""
        export = self.get_object()
        
        return Response({
            'status': export.status,
            'progress': export.progress,
            'error_message': export.error_message,
        })


class PrintProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for print profiles (read-only, admin-managed)"""
    serializer_class = PrintProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PrintProfile.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def create_preset_from_profile(self, request, pk=None):
        """Create preset from print profile"""
        profile = self.get_object()
        
        preset = PDFExportPreset.objects.create(
            created_by=request.user,
            name=f"{profile.name} Preset",
            color_mode=profile.recommended_color_mode,
            quality=profile.recommended_dpi,
            bleed_enabled=True,
            bleed_top=profile.recommended_bleed,
            bleed_bottom=profile.recommended_bleed,
            bleed_left=profile.recommended_bleed,
            bleed_right=profile.recommended_bleed,
            pdf_standard=profile.pdf_standard,
            icc_profile=profile.icc_profile,
        )
        
        return Response(PDFExportPresetSerializer(preset).data)


class SpreadViewViewSet(viewsets.ModelViewSet):
    """ViewSet for spread views"""
    serializer_class = SpreadViewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = SpreadView.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class ImpositionLayoutViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for imposition layouts"""
    serializer_class = ImpositionLayoutSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ImpositionLayout.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate positions for pages"""
        layout = self.get_object()
        pages = request.data.get('pages', [])
        
        service = ImpositionService(layout)
        positions = service.calculate_positions(pages)
        
        return Response({'positions': positions})
    
    @action(detail=True, methods=['post'])
    def saddle_stitch_order(self, request, pk=None):
        """Get page order for saddle stitch"""
        layout = self.get_object()
        total_pages = request.data.get('total_pages', 8)
        
        service = ImpositionService(layout)
        order = service.generate_saddle_stitch_order(total_pages)
        
        return Response({'page_order': order})


class PDFTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for PDF templates"""
    serializer_class = PDFTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PDFTemplate.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class QuickExportView(APIView):
    """Quick PDF export with minimal settings"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = QuickExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from projects.models import Project
        
        project = get_object_or_404(
            Project, id=serializer.validated_data['project_id']
        )
        
        # Create export settings from quick options
        settings = {
            'paper_size': serializer.validated_data['paper_size'],
            'orientation': serializer.validated_data['orientation'],
            'color_mode': serializer.validated_data['color_mode'],
            'quality': serializer.validated_data['quality'],
            'bleed_enabled': serializer.validated_data['with_bleed'],
            'crop_marks': serializer.validated_data['with_crop_marks'],
        }
        
        if serializer.validated_data['with_bleed']:
            bleed = float(serializer.validated_data['bleed_amount'])
            settings.update({
                'bleed_top': bleed,
                'bleed_bottom': bleed,
                'bleed_left': bleed,
                'bleed_right': bleed,
            })
        
        # Create export job
        export = PDFExport.objects.create(
            user=request.user,
            project=project,
            pages=serializer.validated_data.get('pages', []),
            export_settings=settings,
        )
        
        # Generate PDF
        generator = PDFGenerator(export)
        try:
            generator.generate()
        except Exception:
            pass
        
        return Response(PDFExportSerializer(export).data)


class PreflightView(APIView):
    """Run preflight checks on a project"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        from projects.models import Project
        
        project_id = request.data.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        
        settings = request.data.get('settings', {
            'quality': 300,
            'color_mode': 'cmyk',
            'bleed_enabled': True,
            'bleed_top': 3.0,
            'pdf_standard': 'pdf_x_4',
        })
        
        checker = PreflightChecker(project, settings)
        results = checker.run_checks()
        
        return Response(results)

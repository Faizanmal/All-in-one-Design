"""
Views for Presentation Mode app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
import uuid

from .models import (
    Presentation, PresentationSlide, SlideAnnotation, PresentationViewer,
    DevModeProject, DevModeInspection, CodeExportConfig, CodeExportHistory,
    MeasurementOverlay, AssetExportQueue
)
from .serializers import (
    PresentationSerializer, PresentationListSerializer,
    PresentationSlideSerializer, PresentationSlideListSerializer,
    SlideAnnotationSerializer, PresentationViewerSerializer,
    DevModeProjectSerializer, DevModeInspectionSerializer,
    CodeExportConfigSerializer, CodeExportHistorySerializer,
    MeasurementOverlaySerializer, AssetExportQueueSerializer,
    InspectNodeSerializer, ExportCodeSerializer, ExportAssetSerializer,
    StartPresentationSerializer, SharePresentationSerializer
)
from .services import PresentationService, CodeGenerator, AssetExporter


class PresentationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing presentations."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'is_public', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PresentationListSerializer
        return PresentationSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Presentation.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().prefetch_related('slides')
    
    def perform_create(self, serializer):
        share_link = str(uuid.uuid4())[:8]
        serializer.save(created_by=self.request.user, share_link=share_link)
    
    @action(detail=True, methods=['post'])
    def add_slide(self, request, pk=None):
        """Add a slide to the presentation."""
        presentation = self.get_object()
        
        # Get next order
        max_order = presentation.slides.order_by('-order').first()
        order = (max_order.order + 1) if max_order else 0
        
        serializer = PresentationSlideSerializer(data={
            **request.data,
            'presentation': presentation.id,
            'order': order
        })
        if serializer.is_valid():
            serializer.save(presentation=presentation, order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reorder_slides(self, request, pk=None):
        """Reorder slides in the presentation."""
        presentation = self.get_object()
        slide_ids = request.data.get('slide_ids', [])
        
        for index, slide_id in enumerate(slide_ids):
            PresentationSlide.objects.filter(
                id=slide_id,
                presentation=presentation
            ).update(order=index)
        
        return Response({'status': 'reordered'})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start presentation mode."""
        presentation = self.get_object()
        serializer = StartPresentationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = str(uuid.uuid4())
        
        viewer = PresentationViewer.objects.create(
            presentation=presentation,
            user=request.user,
            session_id=session_id,
            current_slide=serializer.validated_data.get('start_slide', 0),
            is_presenter=serializer.validated_data.get('presenter_mode', False),
            can_control=True,
        )
        
        presentation.is_active = True
        presentation.save()
        
        return Response({
            'session_id': session_id,
            'viewer_id': str(viewer.id),
            'presentation': PresentationSerializer(presentation).data,
        })
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop presentation mode."""
        presentation = self.get_object()
        presentation.is_active = False
        presentation.save()
        
        # End all viewer sessions
        presentation.viewers.filter(left_at__isnull=True).update(left_at=timezone.now())
        
        return Response({'status': 'stopped'})
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Configure sharing settings."""
        presentation = self.get_object()
        serializer = SharePresentationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        presentation.is_public = serializer.validated_data['is_public']
        presentation.share_password = serializer.validated_data.get('password', '')
        presentation.allow_comments = serializer.validated_data['allow_comments']
        presentation.save()
        
        return Response({
            'share_link': f"/present/{presentation.share_link}",
            'is_public': presentation.is_public,
        })
    
    @action(detail=True, methods=['get'])
    def viewers(self, request, pk=None):
        """Get current viewers."""
        presentation = self.get_object()
        viewers = presentation.viewers.filter(left_at__isnull=True)
        return Response(PresentationViewerSerializer(viewers, many=True).data)
    
    @action(detail=True, methods=['post'])
    def navigate(self, request, pk=None):
        """Navigate to a specific slide (for presenter control)."""
        presentation = self.get_object()
        slide_index = request.data.get('slide_index')
        
        if slide_index is None:
            return Response({'error': 'slide_index required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update all viewers following the presenter
        presentation.viewers.filter(
            left_at__isnull=True,
            is_presenter=False
        ).update(current_slide=slide_index)
        
        # Broadcast via WebSocket would go here
        
        return Response({'current_slide': slide_index})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the presentation."""
        presentation = self.get_object()
        service = PresentationService(presentation)
        new_presentation = service.duplicate(request.user)
        return Response(PresentationSerializer(new_presentation).data, status=status.HTTP_201_CREATED)


class PublicPresentationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing public presentations."""
    serializer_class = PresentationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'share_link'
    
    def get_queryset(self):
        return Presentation.objects.filter(is_public=True)
    
    @action(detail=True, methods=['post'])
    def join(self, request, share_link=None):
        """Join a public presentation."""
        presentation = self.get_object()
        
        # Check password if set
        if presentation.share_password:
            password = request.data.get('password')
            if password != presentation.share_password:
                return Response({'error': 'Invalid password'}, status=status.HTTP_403_FORBIDDEN)
        
        session_id = str(uuid.uuid4())
        
        viewer = PresentationViewer.objects.create(
            presentation=presentation,
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id,
            current_slide=0,
            is_presenter=False,
            can_control=False,
        )
        
        return Response({
            'session_id': session_id,
            'viewer_id': str(viewer.id),
        })


class PresentationSlideViewSet(viewsets.ModelViewSet):
    """ViewSet for managing presentation slides."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['presentation', 'is_hidden']
    ordering = ['order']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PresentationSlideListSerializer
        return PresentationSlideSerializer
    
    def get_queryset(self):
        user = self.request.user
        return PresentationSlide.objects.filter(
            Q(presentation__project__owner=user) |
            Q(presentation__project__team__members=user)
        ).distinct().prefetch_related('annotations')
    
    @action(detail=True, methods=['post'])
    def add_annotation(self, request, pk=None):
        """Add an annotation to the slide."""
        slide = self.get_object()
        serializer = SlideAnnotationSerializer(data={
            **request.data,
            'slide': slide.id
        })
        if serializer.is_valid():
            serializer.save(slide=slide, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_hidden(self, request, pk=None):
        """Toggle slide hidden state."""
        slide = self.get_object()
        slide.is_hidden = not slide.is_hidden
        slide.save()
        return Response({'is_hidden': slide.is_hidden})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the slide."""
        slide = self.get_object()
        
        new_slide = PresentationSlide.objects.create(
            presentation=slide.presentation,
            frame_id=slide.frame_id,
            title=f"{slide.title} (copy)",
            notes=slide.notes,
            transition=slide.transition,
            transition_duration=slide.transition_duration,
            order=slide.order + 1,
        )
        
        return Response(PresentationSlideSerializer(new_slide).data, status=status.HTTP_201_CREATED)


class SlideAnnotationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing slide annotations."""
    serializer_class = SlideAnnotationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['slide', 'annotation_type', 'is_visible']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return SlideAnnotation.objects.filter(
            Q(slide__presentation__project__owner=user) |
            Q(slide__presentation__project__team__members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PresentationViewerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing presentation viewers."""
    serializer_class = PresentationViewerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['presentation', 'is_presenter']
    
    def get_queryset(self):
        user = self.request.user
        return PresentationViewer.objects.filter(
            Q(presentation__project__owner=user) |
            Q(presentation__project__team__members=user) |
            Q(user=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave the presentation."""
        viewer = self.get_object()
        viewer.left_at = timezone.now()
        viewer.save()
        return Response({'status': 'left'})


class DevModeProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing dev mode projects."""
    serializer_class = DevModeProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'is_enabled']
    
    def get_queryset(self):
        user = self.request.user
        return DevModeProject.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().prefetch_related('configs', 'inspections')
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle dev mode enabled state."""
        dev_mode = self.get_object()
        dev_mode.is_enabled = not dev_mode.is_enabled
        dev_mode.save()
        return Response({'is_enabled': dev_mode.is_enabled})
    
    @action(detail=True, methods=['post'])
    def inspect(self, request, pk=None):
        """Inspect a node and generate code."""
        dev_mode = self.get_object()
        serializer = InspectNodeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        generator = CodeGenerator(dev_mode)
        inspection = generator.inspect_node(
            node_id=serializer.validated_data['node_id'],
            formats=serializer.validated_data['formats'],
            user=request.user,
        )
        
        return Response(DevModeInspectionSerializer(inspection).data)
    
    @action(detail=True, methods=['post'])
    def export_code(self, request, pk=None):
        """Export code for multiple nodes."""
        dev_mode = self.get_object()
        serializer = ExportCodeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        generator = CodeGenerator(dev_mode)
        export = generator.export_code(
            node_ids=serializer.validated_data['node_ids'],
            format=serializer.validated_data['format'],
            config_id=serializer.validated_data.get('config_id'),
            user=request.user,
        )
        
        return Response(CodeExportHistorySerializer(export).data)
    
    @action(detail=True, methods=['post'])
    def export_assets(self, request, pk=None):
        """Queue asset exports."""
        dev_mode = self.get_object()
        serializer = ExportAssetSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        exporter = AssetExporter(dev_mode)
        exports = exporter.queue_exports(
            node_ids=serializer.validated_data['node_ids'],
            format=serializer.validated_data['format'],
            scales=serializer.validated_data['scales'],
            user=request.user,
        )
        
        return Response(AssetExportQueueSerializer(exports, many=True).data)
    
    @action(detail=True, methods=['post'])
    def add_measurement(self, request, pk=None):
        """Add a measurement overlay."""
        dev_mode = self.get_object()
        serializer = MeasurementOverlaySerializer(data={
            **request.data,
            'dev_mode_project': dev_mode.id
        })
        if serializer.is_valid():
            serializer.save(dev_mode_project=dev_mode)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DevModeInspectionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing dev mode inspections."""
    serializer_class = DevModeInspectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dev_mode_project', 'node_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return DevModeInspection.objects.filter(
            Q(dev_mode_project__project__owner=user) |
            Q(dev_mode_project__project__team__members=user)
        ).distinct()


class CodeExportConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing code export configs."""
    serializer_class = CodeExportConfigSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dev_mode_project', 'format', 'framework', 'is_default']
    
    def get_queryset(self):
        user = self.request.user
        return CodeExportConfig.objects.filter(
            Q(dev_mode_project__project__owner=user) |
            Q(dev_mode_project__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this config as default."""
        config = self.get_object()
        CodeExportConfig.objects.filter(
            dev_mode_project=config.dev_mode_project,
            is_default=True
        ).update(is_default=False)
        config.is_default = True
        config.save()
        return Response({'status': 'set as default'})


class CodeExportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing code export history."""
    serializer_class = CodeExportHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['config', 'export_format']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return CodeExportHistory.objects.filter(
            Q(config__dev_mode_project__project__owner=user) |
            Q(config__dev_mode_project__project__team__members=user)
        ).distinct()


class MeasurementOverlayViewSet(viewsets.ModelViewSet):
    """ViewSet for managing measurement overlays."""
    serializer_class = MeasurementOverlaySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dev_mode_project', 'measurement_type', 'is_pinned']
    
    def get_queryset(self):
        user = self.request.user
        return MeasurementOverlay.objects.filter(
            Q(dev_mode_project__project__owner=user) |
            Q(dev_mode_project__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle measurement pin state."""
        overlay = self.get_object()
        overlay.is_pinned = not overlay.is_pinned
        overlay.save()
        return Response({'is_pinned': overlay.is_pinned})


class AssetExportQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing asset export queue."""
    serializer_class = AssetExportQueueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dev_mode_project', 'format', 'status']
    ordering = ['-created_at']
    http_method_names = ['get', 'delete']
    
    def get_queryset(self):
        user = self.request.user
        return AssetExportQueue.objects.filter(
            Q(dev_mode_project__project__owner=user) |
            Q(dev_mode_project__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed export."""
        export = self.get_object()
        if export.status != 'failed':
            return Response({'error': 'Can only retry failed exports'}, status=status.HTTP_400_BAD_REQUEST)
        
        export.status = 'pending'
        export.error_message = ''
        export.save()
        
        # Queue the task
        from .tasks import export_asset_task
        export_asset_task.delay(str(export.id))
        
        return Response({'status': 'retrying'})

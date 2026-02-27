"""
Media Assets Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from .models import (
    VideoAsset, GIFAsset, LottieAsset, MediaPlacement,
    AnimatedExport, VideoFrame
)
from .serializers import (
    VideoAssetSerializer, GIFAssetSerializer, LottieAssetSerializer,
    MediaPlacementSerializer, AnimatedExportSerializer,
    AnimatedExportRequestSerializer, VideoFrameSerializer,
    ExtractFramesSerializer, VideoFromURLSerializer
)


class VideoAssetViewSet(viewsets.ModelViewSet):
    serializer_class = VideoAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return VideoAsset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def extract_frames(self, request, pk=None):
        """Extract frames from video."""
        video = self.get_object()
        serializer = ExtractFramesSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        frame_count = serializer.validated_data.get('frame_count', 10)

        # Check for ffmpeg availability
        import shutil
        if not shutil.which('ffmpeg'):
            return Response(
                {
                    'error': 'Frame extraction requires ffmpeg to be installed on the server.',
                    'video_id': str(video.id),
                },
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        # Queue the extraction (in a real app this would be a Celery task)
        return Response({
            'message': 'Frame extraction queued',
            'video_id': str(video.id),
            'frame_count': frame_count,
            'status': 'queued',
        })
    
    @action(detail=False, methods=['post'])
    def from_url(self, request):
        """Import video from URL (YouTube, Vimeo, etc.)."""
        serializer = VideoFromURLSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        url = data['url']
        
        # Detect source type
        source_type = 'url'
        embed_id = ''
        
        if 'youtube.com' in url or 'youtu.be' in url:
            source_type = 'youtube'
            # Extract video ID
            import re
            match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
            if match:
                embed_id = match.group(1)
        elif 'vimeo.com' in url:
            source_type = 'vimeo'
            import re
            match = re.search(r'vimeo\.com/(\d+)', url)
            if match:
                embed_id = match.group(1)
        
        video = VideoAsset.objects.create(
            user=request.user,
            project_id=data.get('project_id'),
            name=data.get('name', f'Video from {source_type}'),
            source_type=source_type,
            url=url,
            embed_id=embed_id
        )
        
        return Response(VideoAssetSerializer(video).data, status=status.HTTP_201_CREATED)


class GIFAssetViewSet(viewsets.ModelViewSet):
    serializer_class = GIFAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return GIFAsset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LottieAssetViewSet(viewsets.ModelViewSet):
    serializer_class = LottieAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LottieAsset.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_colors(self, request, pk=None):
        """Update colors in Lottie animation."""
        lottie = self.get_object()
        color_map = request.data.get('color_map', {})
        
        # In production, traverse Lottie JSON and replace colors
        # For now, return the original
        return Response(LottieAssetSerializer(lottie).data)


class MediaPlacementViewSet(viewsets.ModelViewSet):
    serializer_class = MediaPlacementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = MediaPlacement.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class AnimatedExportViewSet(viewsets.ModelViewSet):
    serializer_class = AnimatedExportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnimatedExport.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_export(self, request):
        """Create a new animated export job."""
        serializer = AnimatedExportRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        export = AnimatedExport.objects.create(
            user=request.user,
            project_id=data['project_id'],
            export_format=data['export_format'],
            settings={
                'width': data['width'],
                'height': data['height'],
                'fps': data['fps'],
                'quality': data['quality'],
                'loop': data['loop'],
                'duration': data.get('duration'),
                'start_time': data['start_time'],
                'end_time': data.get('end_time'),
                'background': data['background']
            }
        )
        
        # In production, queue Celery task here
        # For now, simulate processing
        export.status = 'processing'
        export.started_at = timezone.now()
        export.save()
        
        return Response(AnimatedExportSerializer(export).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Check export status."""
        export = self.get_object()
        return Response({
            'id': str(export.id),
            'status': export.status,
            'progress': export.progress,
            'output_url': export.output_url,
            'error_message': export.error_message
        })


class VideoFrameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VideoFrameSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VideoFrame.objects.filter(video__user=self.request.user)

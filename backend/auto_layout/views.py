"""
Auto-Layout System Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from .models import (
    AutoLayoutFrame, AutoLayoutChild, LayoutConstraint,
    ResponsiveBreakpoint, ResponsiveOverride, LayoutPreset
)
from .serializers import (
    AutoLayoutFrameSerializer, AutoLayoutChildSerializer,
    LayoutConstraintSerializer, ResponsiveBreakpointSerializer,
    ResponsiveOverrideSerializer, LayoutPresetSerializer
)
from .services import AutoLayoutEngine


class AutoLayoutFrameViewSet(viewsets.ModelViewSet):
    """ViewSet for managing auto-layout frames."""
    
    serializer_class = AutoLayoutFrameSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AutoLayoutFrame.objects.filter(
            project__user=self.request.user
        ).select_related('project', 'component', 'parent_frame', 'created_by')
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.prefetch_related('children')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_child(self, request, pk=None):
        """Add a child element to the auto-layout frame."""
        frame = self.get_object()
        serializer = AutoLayoutChildSerializer(data=request.data)
        
        if serializer.is_valid():
            max_order = frame.children.aggregate(models.Max('order'))['order__max'] or -1
            serializer.save(parent_frame=frame, order=max_order + 1)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reorder_children(self, request, pk=None):
        """Reorder children within the frame."""
        frame = self.get_object()
        child_ids = request.data.get('child_ids', [])
        
        for index, child_id in enumerate(child_ids):
            AutoLayoutChild.objects.filter(
                id=child_id, parent_frame=frame
            ).update(order=index)
        
        return Response({'status': 'reordered'})
    
    @action(detail=True, methods=['post'])
    def compute_layout(self, request, pk=None):
        """Compute the layout and return computed positions."""
        frame = self.get_object()
        viewport_width = request.data.get('viewport_width', 1920)
        viewport_height = request.data.get('viewport_height', 1080)
        
        engine = AutoLayoutEngine(frame, viewport_width, viewport_height)
        computed = engine.compute()
        
        return Response({
            'frame': AutoLayoutFrameSerializer(frame).data,
            'computed': computed
        })
    
    @action(detail=True, methods=['post'])
    def apply_preset(self, request, pk=None):
        """Apply a layout preset to this frame."""
        frame = self.get_object()
        preset_id = request.data.get('preset_id')
        
        preset = get_object_or_404(LayoutPreset, id=preset_id)
        preset.apply_to_frame(frame)
        frame.save()
        
        return Response(AutoLayoutFrameSerializer(frame).data)


class AutoLayoutChildViewSet(viewsets.ModelViewSet):
    """ViewSet for managing auto-layout children."""
    
    serializer_class = AutoLayoutChildSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutoLayoutChild.objects.filter(
            parent_frame__project__user=self.request.user
        ).select_related('parent_frame', 'component')
    
    @action(detail=True, methods=['post'])
    def set_sizing(self, request, pk=None):
        """Set sizing mode for a child."""
        child = self.get_object()
        
        horizontal = request.data.get('horizontal_sizing')
        vertical = request.data.get('vertical_sizing')
        
        if horizontal:
            child.horizontal_sizing = horizontal
        if vertical:
            child.vertical_sizing = vertical
        
        child.save()
        return Response(AutoLayoutChildSerializer(child).data)


class LayoutConstraintViewSet(viewsets.ModelViewSet):
    """ViewSet for managing layout constraints."""
    
    serializer_class = LayoutConstraintSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LayoutConstraint.objects.filter(
            component__project__user=self.request.user
        ).select_related('component')


class ResponsiveBreakpointViewSet(viewsets.ModelViewSet):
    """ViewSet for managing responsive breakpoints."""
    
    serializer_class = ResponsiveBreakpointSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ResponsiveBreakpoint.objects.filter(
            project__user=self.request.user
        )
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """Create default breakpoints for a project."""
        project_id = request.data.get('project_id')
        
        defaults = [
            {'name': 'Desktop', 'device_type': 'desktop', 'min_width': 1024, 'canvas_width': 1920, 'canvas_height': 1080},
            {'name': 'Tablet', 'device_type': 'tablet', 'min_width': 768, 'max_width': 1023, 'canvas_width': 768, 'canvas_height': 1024},
            {'name': 'Mobile', 'device_type': 'mobile', 'min_width': 0, 'max_width': 767, 'canvas_width': 375, 'canvas_height': 812},
        ]
        
        created = []
        for i, default in enumerate(defaults):
            bp, _ = ResponsiveBreakpoint.objects.get_or_create(
                project_id=project_id,
                name=default['name'],
                defaults={**default, 'priority': i}
            )
            created.append(bp)
        
        return Response(ResponsiveBreakpointSerializer(created, many=True).data)


class ResponsiveOverrideViewSet(viewsets.ModelViewSet):
    """ViewSet for managing responsive overrides."""
    
    serializer_class = ResponsiveOverrideSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ResponsiveOverride.objects.filter(
            frame__project__user=self.request.user
        ).select_related('frame', 'breakpoint')


class LayoutPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing layout presets."""
    
    serializer_class = LayoutPresetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db.models import Q
        return LayoutPreset.objects.filter(
            Q(user=self.request.user) | Q(is_public=True) | Q(is_system=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all preset categories with counts."""
        from django.db.models import Count
        categories = self.get_queryset().values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        return Response(list(categories))
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular presets."""
        presets = self.get_queryset().order_by('-use_count')[:20]
        return Response(LayoutPresetSerializer(presets, many=True).data)

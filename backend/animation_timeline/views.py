"""
Views for Animation Timeline app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    AnimationProject, AnimationComposition, AnimationLayer,
    AnimationTrack, AnimationKeyframe, EasingPreset,
    AnimationEffect, LottieExport, AnimationSequence
)
from .serializers import (
    AnimationProjectSerializer, AnimationProjectListSerializer,
    AnimationCompositionSerializer, AnimationCompositionListSerializer,
    AnimationLayerSerializer, AnimationLayerListSerializer,
    AnimationTrackSerializer, AnimationKeyframeSerializer,
    EasingPresetSerializer, AnimationEffectSerializer,
    LottieExportSerializer, AnimationSequenceSerializer,
    TimelineDataSerializer, KeyframeBatchSerializer, ExportLottieSerializer
)
from .services import AnimationTimelineService, LottieExporter


class AnimationProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation projects."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'is_published']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnimationProjectListSerializer
        return AnimationProjectSerializer
    
    def get_queryset(self):
        user = self.request.user
        return AnimationProject.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().prefetch_related('compositions')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_composition(self, request, pk=None):
        """Add a composition to the project."""
        animation_project = self.get_object()
        serializer = AnimationCompositionSerializer(data={
            **request.data,
            'project': animation_project.id
        })
        if serializer.is_valid():
            serializer.save(project=animation_project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the animation project."""
        project = self.get_object()
        service = AnimationTimelineService(project)
        new_project = service.duplicate_project(request.user)
        return Response(AnimationProjectSerializer(new_project).data, status=status.HTTP_201_CREATED)


class AnimationCompositionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation compositions."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'is_main']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnimationCompositionListSerializer
        return AnimationCompositionSerializer
    
    def get_queryset(self):
        user = self.request.user
        return AnimationComposition.objects.filter(
            Q(project__project__owner=user) |
            Q(project__project__team__members=user)
        ).distinct().prefetch_related('layers', 'sequences')
    
    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get full timeline data for the composition."""
        composition = self.get_object()
        serializer = TimelineDataSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = AnimationTimelineService(composition.project)
        timeline_data = service.get_timeline_data(
            composition,
            start_frame=serializer.validated_data.get('start_frame', 0),
            end_frame=serializer.validated_data.get('end_frame', composition.duration_frames),
            include_keyframes=serializer.validated_data.get('include_keyframes', True),
        )
        
        return Response(timeline_data)
    
    @action(detail=True, methods=['post'])
    def add_layer(self, request, pk=None):
        """Add a layer to the composition."""
        composition = self.get_object()
        serializer = AnimationLayerSerializer(data={
            **request.data,
            'composition': composition.id
        })
        if serializer.is_valid():
            # Set order to end
            max_order = composition.layers.order_by('-order').first()
            order = (max_order.order + 1) if max_order else 0
            serializer.save(composition=composition, order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reorder_layers(self, request, pk=None):
        """Reorder layers in the composition."""
        composition = self.get_object()
        layer_ids = request.data.get('layer_ids', [])
        
        for index, layer_id in enumerate(layer_ids):
            AnimationLayer.objects.filter(
                id=layer_id,
                composition=composition
            ).update(order=index)
        
        return Response({'status': 'reordered'})
    
    @action(detail=True, methods=['post'])
    def export_lottie(self, request, pk=None):
        """Export composition to Lottie format."""
        composition = self.get_object()
        serializer = ExportLottieSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        exporter = LottieExporter(composition)
        export = exporter.export(
            created_by=request.user,
            format=serializer.validated_data['format'],
            include_assets=serializer.validated_data['include_assets'],
            optimize=serializer.validated_data['optimize'],
            target_size=serializer.validated_data.get('target_size'),
        )
        
        return Response(LottieExportSerializer(export).data, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def set_main(self, request, pk=None):
        """Set this as the main composition."""
        composition = self.get_object()
        # Unset current main
        AnimationComposition.objects.filter(
            project=composition.project,
            is_main=True
        ).update(is_main=False)
        composition.is_main = True
        composition.save()
        return Response({'status': 'set as main'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the composition."""
        composition = self.get_object()
        service = AnimationTimelineService(composition.project)
        new_comp = service.duplicate_composition(composition)
        return Response(AnimationCompositionSerializer(new_comp).data, status=status.HTTP_201_CREATED)


class AnimationLayerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation layers."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['composition', 'layer_type', 'is_visible', 'is_locked']
    ordering = ['order']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AnimationLayerListSerializer
        return AnimationLayerSerializer
    
    def get_queryset(self):
        user = self.request.user
        return AnimationLayer.objects.filter(
            Q(composition__project__project__owner=user) |
            Q(composition__project__project__team__members=user)
        ).distinct().prefetch_related('tracks', 'effects')
    
    @action(detail=True, methods=['post'])
    def add_track(self, request, pk=None):
        """Add a track to the layer."""
        layer = self.get_object()
        serializer = AnimationTrackSerializer(data={
            **request.data,
            'layer': layer.id
        })
        if serializer.is_valid():
            serializer.save(layer=layer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_effect(self, request, pk=None):
        """Add an effect to the layer."""
        layer = self.get_object()
        serializer = AnimationEffectSerializer(data={
            **request.data,
            'layer': layer.id
        })
        if serializer.is_valid():
            max_order = layer.effects.order_by('-order').first()
            order = (max_order.order + 1) if max_order else 0
            serializer.save(layer=layer, order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_visibility(self, request, pk=None):
        """Toggle layer visibility."""
        layer = self.get_object()
        layer.is_visible = not layer.is_visible
        layer.save()
        return Response({'is_visible': layer.is_visible})
    
    @action(detail=True, methods=['post'])
    def toggle_lock(self, request, pk=None):
        """Toggle layer lock."""
        layer = self.get_object()
        layer.is_locked = not layer.is_locked
        layer.save()
        return Response({'is_locked': layer.is_locked})
    
    @action(detail=True, methods=['post'])
    def toggle_solo(self, request, pk=None):
        """Toggle layer solo."""
        layer = self.get_object()
        layer.is_solo = not layer.is_solo
        layer.save()
        return Response({'is_solo': layer.is_solo})
    
    @action(detail=True, methods=['post'])
    def set_parent(self, request, pk=None):
        """Set parent layer for parenting."""
        layer = self.get_object()
        parent_id = request.data.get('parent_id')
        
        if parent_id:
            try:
                parent = AnimationLayer.objects.get(id=parent_id, composition=layer.composition)
                layer.parent_layer = parent
            except AnimationLayer.DoesNotExist:
                return Response({'error': 'Parent layer not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            layer.parent_layer = None
        
        layer.save()
        return Response(AnimationLayerSerializer(layer).data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the layer."""
        layer = self.get_object()
        
        new_layer = AnimationLayer.objects.create(
            composition=layer.composition,
            name=f"{layer.name} (copy)",
            layer_type=layer.layer_type,
            source_node_id=layer.source_node_id,
            in_point=layer.in_point,
            out_point=layer.out_point,
            transform=layer.transform,
            opacity=layer.opacity,
            blend_mode=layer.blend_mode,
            order=layer.order + 1,
            color=layer.color,
        )
        
        # Duplicate tracks and keyframes
        for track in layer.tracks.all():
            new_track = AnimationTrack.objects.create(
                layer=new_layer,
                property_path=track.property_path,
                property_type=track.property_type,
                color=track.color,
            )
            for keyframe in track.keyframes.all():
                AnimationKeyframe.objects.create(
                    track=new_track,
                    frame_number=keyframe.frame_number,
                    time_ms=keyframe.time_ms,
                    value=keyframe.value,
                    interpolation=keyframe.interpolation,
                    bezier_control_points=keyframe.bezier_control_points,
                )
        
        return Response(AnimationLayerSerializer(new_layer).data, status=status.HTTP_201_CREATED)


class AnimationTrackViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation tracks."""
    serializer_class = AnimationTrackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['layer', 'property_type', 'is_locked', 'is_muted']
    
    def get_queryset(self):
        user = self.request.user
        return AnimationTrack.objects.filter(
            Q(layer__composition__project__project__owner=user) |
            Q(layer__composition__project__project__team__members=user)
        ).distinct().prefetch_related('keyframes')
    
    @action(detail=True, methods=['post'])
    def add_keyframe(self, request, pk=None):
        """Add a keyframe to the track."""
        track = self.get_object()
        serializer = AnimationKeyframeSerializer(data={
            **request.data,
            'track': track.id
        })
        if serializer.is_valid():
            serializer.save(track=track)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def batch_keyframes(self, request, pk=None):
        """Batch operations on keyframes."""
        track = self.get_object()
        serializer = KeyframeBatchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        operation = serializer.validated_data['operation']
        keyframes_data = serializer.validated_data['keyframes']
        
        results = []
        
        if operation == 'create':
            for kf_data in keyframes_data:
                kf = AnimationKeyframe.objects.create(
                    track=track,
                    frame_number=kf_data.get('frame_number', 0),
                    value=kf_data.get('value'),
                    interpolation=kf_data.get('interpolation', 'bezier'),
                )
                results.append(AnimationKeyframeSerializer(kf).data)
        
        elif operation == 'shift':
            shift = serializer.validated_data.get('shift_frames', 0)
            for kf_data in keyframes_data:
                kf_id = kf_data.get('id')
                AnimationKeyframe.objects.filter(
                    id=kf_id, track=track
                ).update(frame_number=models.F('frame_number') + shift)
            results = {'shifted': len(keyframes_data)}
        
        elif operation == 'delete':
            ids = [kf.get('id') for kf in keyframes_data]
            deleted = AnimationKeyframe.objects.filter(
                id__in=ids, track=track
            ).delete()
            results = {'deleted': deleted[0]}
        
        return Response(results)


class AnimationKeyframeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation keyframes."""
    serializer_class = AnimationKeyframeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['track', 'interpolation']
    ordering = ['frame_number']
    
    def get_queryset(self):
        user = self.request.user
        return AnimationKeyframe.objects.filter(
            Q(track__layer__composition__project__project__owner=user) |
            Q(track__layer__composition__project__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def set_easing(self, request, pk=None):
        """Set easing for the keyframe."""
        keyframe = self.get_object()
        
        preset_id = request.data.get('preset_id')
        if preset_id:
            try:
                preset = EasingPreset.objects.get(id=preset_id)
                keyframe.easing_preset = preset
                if preset.bezier_points:
                    keyframe.bezier_control_points = preset.bezier_points
            except EasingPreset.DoesNotExist:
                return Response({'error': 'Preset not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            keyframe.bezier_control_points = request.data.get('bezier_points', [0, 0, 1, 1])
            keyframe.easing_preset = None
        
        keyframe.save()
        return Response(AnimationKeyframeSerializer(keyframe).data)


class EasingPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing easing presets."""
    serializer_class = EasingPresetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['easing_type', 'is_system']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        user = self.request.user
        return EasingPreset.objects.filter(
            Q(is_system=True) | Q(created_by=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AnimationEffectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation effects."""
    serializer_class = AnimationEffectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['layer', 'effect_type', 'is_enabled']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return AnimationEffect.objects.filter(
            Q(layer__composition__project__project__owner=user) |
            Q(layer__composition__project__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle effect enabled state."""
        effect = self.get_object()
        effect.is_enabled = not effect.is_enabled
        effect.save()
        return Response({'is_enabled': effect.is_enabled})


class LottieExportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Lottie exports."""
    serializer_class = LottieExportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['composition', 'format', 'status']
    ordering = ['-created_at']
    http_method_names = ['get', 'delete']  # Read-only, exports created via composition
    
    def get_queryset(self):
        user = self.request.user
        return LottieExport.objects.filter(
            Q(composition__project__project__owner=user) |
            Q(composition__project__project__team__members=user)
        ).distinct()


class AnimationSequenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animation sequences."""
    serializer_class = AnimationSequenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['composition', 'source_composition']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return AnimationSequence.objects.filter(
            Q(composition__project__project__owner=user) |
            Q(composition__project__project__team__members=user)
        ).distinct()

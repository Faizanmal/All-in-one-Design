from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import json

from .models import (
    Animation, Keyframe, LottieAnimation, MicroInteraction,
    AnimationPreset, AnimationTimeline, TimelineItem
)
from .serializers import (
    AnimationSerializer, AnimationCreateSerializer, KeyframeSerializer,
    LottieAnimationSerializer, MicroInteractionSerializer,
    AnimationPresetSerializer, AnimationTimelineSerializer, TimelineItemSerializer,
    CSSExportSerializer, LottieExportSerializer
)


class AnimationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing animations"""
    serializer_class = AnimationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Animation.objects.filter(user=self.request.user)
        
        # Filter by project
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by type
        anim_type = self.request.query_params.get('type')
        if anim_type:
            queryset = queryset.filter(animation_type=anim_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AnimationCreateSerializer
        return AnimationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_keyframe(self, request, pk=None):
        """Add a keyframe to the animation"""
        animation = self.get_object()
        
        position = request.data.get('position', 0)
        properties = request.data.get('properties', {})
        easing = request.data.get('easing', '')
        
        keyframe = Keyframe.objects.create(
            animation=animation,
            position=position,
            properties=properties,
            easing=easing
        )
        
        return Response(KeyframeSerializer(keyframe).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['put'])
    def update_keyframe(self, request, pk=None):
        """Update a keyframe"""
        animation = self.get_object()
        keyframe_id = request.data.get('keyframe_id')
        
        keyframe = get_object_or_404(Keyframe, id=keyframe_id, animation=animation)
        
        if 'position' in request.data:
            keyframe.position = request.data['position']
        if 'properties' in request.data:
            keyframe.properties = request.data['properties']
        if 'easing' in request.data:
            keyframe.easing = request.data['easing']
        
        keyframe.save()
        return Response(KeyframeSerializer(keyframe).data)
    
    @action(detail=True, methods=['delete'])
    def delete_keyframe(self, request, pk=None):
        """Delete a keyframe"""
        animation = self.get_object()
        keyframe_id = request.data.get('keyframe_id')
        
        keyframe = get_object_or_404(Keyframe, id=keyframe_id, animation=animation)
        keyframe.delete()
        
        return Response({'status': 'Keyframe deleted'})
    
    @action(detail=True, methods=['get'])
    def export_css(self, request, pk=None):
        """Export animation as CSS"""
        animation = self.get_object()
        
        class_name = request.query_params.get('class_name', 'animation')
        vendor_prefixes = request.query_params.get('vendor_prefixes', 'true') == 'true'
        
        # Generate CSS
        css = self._generate_css(animation, class_name, vendor_prefixes)
        
        return Response({
            'css': css,
            'animation_name': animation.name,
            'class_name': class_name
        })
    
    @action(detail=True, methods=['get'])
    def export_lottie(self, request, pk=None):
        """Export animation as Lottie JSON"""
        animation = self.get_object()
        
        # Generate Lottie JSON
        lottie_data = self._convert_to_lottie(animation)
        
        return Response(lottie_data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate an animation"""
        original = self.get_object()
        
        new_animation = Animation.objects.create(
            user=request.user,
            project=original.project,
            name=f"{original.name} (Copy)",
            description=original.description,
            animation_type=original.animation_type,
            duration=original.duration,
            delay=original.delay,
            easing=original.easing,
            easing_params=original.easing_params,
            iterations=original.iterations,
            direction=original.direction,
            fill_mode=original.fill_mode,
            keyframes=original.keyframes,
            tags=original.tags,
            category=original.category,
        )
        
        # Copy keyframes
        for kf in original.keyframe_set.all():
            Keyframe.objects.create(
                animation=new_animation,
                position=kf.position,
                properties=kf.properties,
                easing=kf.easing
            )
        
        return Response(AnimationSerializer(new_animation, context={'request': request}).data)
    
    def _generate_css(self, animation, class_name, vendor_prefixes):
        """Generate CSS animation code"""
        css_lines = []
        
        # Animation class
        css_lines.append(f".{class_name} {{")
        css_lines.append(f"  animation-name: {animation.name.replace(' ', '-').lower()};")
        css_lines.append(f"  animation-duration: {animation.duration}s;")
        css_lines.append(f"  animation-delay: {animation.delay}s;")
        css_lines.append(f"  animation-timing-function: {animation.easing};")
        css_lines.append(f"  animation-iteration-count: {'infinite' if animation.iterations == -1 else animation.iterations};")
        css_lines.append(f"  animation-direction: {animation.direction};")
        css_lines.append(f"  animation-fill-mode: {animation.fill_mode};")
        css_lines.append("}")
        css_lines.append("")
        
        # Keyframes
        keyframe_name = animation.name.replace(' ', '-').lower()
        css_lines.append(f"@keyframes {keyframe_name} {{")
        
        for keyframe in animation.keyframe_set.all().order_by('position'):
            css_lines.append(f"  {keyframe.position}% {{")
            for prop, value in keyframe.properties.items():
                css_lines.append(f"    {prop}: {value};")
            css_lines.append("  }")
        
        css_lines.append("}")
        
        if vendor_prefixes:
            # Add webkit prefix
            css_lines.append("")
            css_lines.append(f"@-webkit-keyframes {keyframe_name} {{")
            for keyframe in animation.keyframe_set.all().order_by('position'):
                css_lines.append(f"  {keyframe.position}% {{")
                for prop, value in keyframe.properties.items():
                    css_lines.append(f"    {prop}: {value};")
                css_lines.append("  }")
            css_lines.append("}")
        
        return "\n".join(css_lines)
    
    def _convert_to_lottie(self, animation):
        """Convert animation to Lottie format"""
        fps = 60
        total_frames = int(animation.duration * fps)
        
        lottie_data = {
            "v": "5.7.1",
            "fr": fps,
            "ip": 0,
            "op": total_frames,
            "w": 1920,
            "h": 1080,
            "nm": animation.name,
            "ddd": 0,
            "assets": [],
            "layers": []
        }
        
        return lottie_data


class LottieAnimationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Lottie animations"""
    serializer_class = LottieAnimationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return LottieAnimation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        file = self.request.FILES.get('lottie_file')
        
        # Parse Lottie file for metadata
        metadata = {}
        if file:
            try:
                content = file.read()
                lottie_data = json.loads(content)
                metadata = {
                    'version': lottie_data.get('v', ''),
                    'frame_rate': lottie_data.get('fr', 30),
                    'in_point': lottie_data.get('ip', 0),
                    'out_point': lottie_data.get('op', 0),
                    'width': lottie_data.get('w', 0),
                    'height': lottie_data.get('h', 0),
                    'asset_count': len(lottie_data.get('assets', [])),
                    'layer_count': len(lottie_data.get('layers', [])),
                }
                file.seek(0)  # Reset file pointer
            except (json.JSONDecodeError, KeyError):
                pass
        
        serializer.save(
            user=self.request.user,
            file_size=file.size if file else 0,
            **metadata
        )
    
    @action(detail=True, methods=['get'])
    def json(self, request, pk=None):
        """Get raw Lottie JSON"""
        lottie = self.get_object()
        
        if lottie.lottie_file:
            content = lottie.lottie_file.read()
            return Response(json.loads(content))
        
        return Response({'error': 'No Lottie file'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def optimize(self, request, pk=None):
        """Optimize Lottie animation"""
        lottie = self.get_object()
        # In production, implement Lottie optimization
        return Response({'status': 'Optimization queued'})


class MicroInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for micro-interactions library"""
    serializer_class = MicroInteractionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = MicroInteraction.objects.all()
        
        # Filter by type
        interaction_type = self.request.query_params.get('type')
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        
        # Filter premium
        premium = self.request.query_params.get('premium')
        if premium is not None:
            queryset = queryset.filter(is_premium=premium == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Record usage of a micro-interaction"""
        interaction = self.get_object()
        interaction.usage_count += 1
        interaction.save(update_fields=['usage_count'])
        
        return Response({
            'animation_data': interaction.animation_data,
            'css_code': interaction.css_code,
            'js_code': interaction.js_code,
            'react_code': interaction.react_code,
            'vue_code': interaction.vue_code,
        })


class AnimationPresetViewSet(viewsets.ModelViewSet):
    """ViewSet for animation presets"""
    serializer_class = AnimationPresetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = AnimationPreset.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply preset to create a new animation"""
        preset = self.get_object()
        preset.usage_count += 1
        preset.save(update_fields=['usage_count'])
        
        # Get customized parameters
        custom_params = request.data.get('parameters', {})
        
        # Create new animation from preset
        animation_data = preset.animation_data.copy()
        
        # Apply custom parameters
        for param in preset.parameters:
            param_name = param['name']
            if param_name in custom_params:
                animation_data[param_name] = custom_params[param_name]
        
        animation = Animation.objects.create(
            user=request.user,
            name=f"{preset.name} Animation",
            animation_type=animation_data.get('type', 'keyframe'),
            duration=animation_data.get('duration', 1),
            easing=animation_data.get('easing', 'ease'),
            keyframes=animation_data.get('keyframes', []),
            is_preset=True,
        )
        
        return Response(AnimationSerializer(animation, context={'request': request}).data)


class AnimationTimelineViewSet(viewsets.ModelViewSet):
    """ViewSet for animation timelines"""
    serializer_class = AnimationTimelineSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AnimationTimeline.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to the timeline"""
        timeline = self.get_object()
        
        item = TimelineItem.objects.create(
            timeline=timeline,
            animation_id=request.data.get('animation_id'),
            lottie_id=request.data.get('lottie_id'),
            track_index=request.data.get('track_index', 0),
            start_time=request.data.get('start_time', 0),
            end_time=request.data.get('end_time', 1),
            target_element_id=request.data.get('target_element_id', ''),
            properties=request.data.get('properties', {})
        )
        
        return Response(TimelineItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export timeline as video or GIF"""
        timeline = self.get_object()
        export_format = request.query_params.get('format', 'mp4')
        
        # In production, trigger async export job
        return Response({
            'status': 'Export queued',
            'format': export_format,
            'timeline_id': str(timeline.id)
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_easing_presets(request):
    """Get available easing presets"""
    return Response({
        'basic': [
            {'name': 'linear', 'value': 'linear'},
            {'name': 'ease', 'value': 'ease'},
            {'name': 'ease-in', 'value': 'ease-in'},
            {'name': 'ease-out', 'value': 'ease-out'},
            {'name': 'ease-in-out', 'value': 'ease-in-out'},
        ],
        'cubic_bezier': [
            {'name': 'Ease In Quad', 'value': 'cubic-bezier(0.55, 0.085, 0.68, 0.53)'},
            {'name': 'Ease Out Quad', 'value': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'},
            {'name': 'Ease In Out Quad', 'value': 'cubic-bezier(0.455, 0.03, 0.515, 0.955)'},
            {'name': 'Ease In Cubic', 'value': 'cubic-bezier(0.55, 0.055, 0.675, 0.19)'},
            {'name': 'Ease Out Cubic', 'value': 'cubic-bezier(0.215, 0.61, 0.355, 1)'},
            {'name': 'Ease In Out Cubic', 'value': 'cubic-bezier(0.645, 0.045, 0.355, 1)'},
            {'name': 'Ease In Expo', 'value': 'cubic-bezier(0.95, 0.05, 0.795, 0.035)'},
            {'name': 'Ease Out Expo', 'value': 'cubic-bezier(0.19, 1, 0.22, 1)'},
            {'name': 'Ease In Out Expo', 'value': 'cubic-bezier(1, 0, 0, 1)'},
            {'name': 'Ease In Back', 'value': 'cubic-bezier(0.6, -0.28, 0.735, 0.045)'},
            {'name': 'Ease Out Back', 'value': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)'},
            {'name': 'Ease In Out Back', 'value': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'},
        ],
        'spring': [
            {'name': 'Spring Soft', 'value': 'spring(1, 100, 10, 0)'},
            {'name': 'Spring Medium', 'value': 'spring(1, 80, 10, 0)'},
            {'name': 'Spring Stiff', 'value': 'spring(1, 300, 20, 0)'},
            {'name': 'Spring Bouncy', 'value': 'spring(1, 180, 12, 0)'},
        ]
    })

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
import uuid

from .models import Model3D, Scene3D, SceneModel, Prototype3D, ARPreview, Conversion3DTo2D
from .serializers import (
    Model3DSerializer, Model3DUploadSerializer,
    Scene3DSerializer, Scene3DCreateSerializer, SceneModelSerializer,
    Prototype3DSerializer, ARPreviewSerializer, Conversion3DTo2DSerializer
)


class Model3DViewSet(viewsets.ModelViewSet):
    """ViewSet for managing 3D models"""
    serializer_class = Model3DSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        return Model3D.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return Model3DUploadSerializer
        return Model3DSerializer
    
    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        file_format = file.name.split('.')[-1].lower()
        serializer.save(
            user=self.request.user,
            file_format=file_format,
            file_size=file.size
        )
    
    @action(detail=True, methods=['post'])
    def generate_thumbnail(self, request, pk=None):
        """Generate thumbnail for 3D model"""
        model = self.get_object()
        # In production, this would trigger async thumbnail generation
        return Response({
            'status': 'Thumbnail generation queued',
            'model_id': str(model.id)
        })
    
    @action(detail=True, methods=['get'])
    def metadata(self, request, pk=None):
        """Get detailed metadata for 3D model"""
        model = self.get_object()
        return Response({
            'id': str(model.id),
            'name': model.name,
            'format': model.file_format,
            'file_size': model.file_size,
            'geometry': {
                'vertices': model.vertex_count,
                'faces': model.face_count,
            },
            'materials': model.material_count,
            'textures': model.texture_count,
            'animations': model.animation_count,
            'bounding_box': {
                'min': [model.bbox_min_x, model.bbox_min_y, model.bbox_min_z],
                'max': [model.bbox_max_x, model.bbox_max_y, model.bbox_max_z],
            },
            'ar_settings': {
                'enabled': model.ar_enabled,
                'scale': model.ar_scale,
                'anchor_type': model.ar_anchor_type,
            }
        })
    
    @action(detail=False, methods=['get'])
    def formats(self, request):
        """Get supported 3D file formats"""
        return Response({
            'import': ['gltf', 'glb', 'obj', 'fbx', 'stl', 'usdz'],
            'export': ['gltf', 'glb', 'obj', 'usdz'],
            'recommended': 'glb'
        })


class Scene3DViewSet(viewsets.ModelViewSet):
    """ViewSet for managing 3D scenes"""
    serializer_class = Scene3DSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Scene3D.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return Scene3DCreateSerializer
        return Scene3DSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_model(self, request, pk=None):
        """Add a 3D model to the scene"""
        scene = self.get_object()
        model_id = request.data.get('model_id')
        
        if not model_id:
            return Response({'error': 'model_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        model = get_object_or_404(Model3D, id=model_id, user=request.user)
        
        scene_model = SceneModel.objects.create(
            scene=scene,
            model=model,
            position_x=request.data.get('position_x', 0),
            position_y=request.data.get('position_y', 0),
            position_z=request.data.get('position_z', 0),
            rotation_x=request.data.get('rotation_x', 0),
            rotation_y=request.data.get('rotation_y', 0),
            rotation_z=request.data.get('rotation_z', 0),
            scale_x=request.data.get('scale_x', 1),
            scale_y=request.data.get('scale_y', 1),
            scale_z=request.data.get('scale_z', 1),
        )
        
        return Response(SceneModelSerializer(scene_model, context={'request': request}).data)
    
    @action(detail=True, methods=['put'])
    def update_model_transform(self, request, pk=None):
        """Update transform of a model in the scene"""
        scene = self.get_object()
        scene_model_id = request.data.get('scene_model_id')
        
        scene_model = get_object_or_404(SceneModel, id=scene_model_id, scene=scene)
        
        for field in ['position_x', 'position_y', 'position_z',
                      'rotation_x', 'rotation_y', 'rotation_z',
                      'scale_x', 'scale_y', 'scale_z',
                      'visible', 'cast_shadow', 'receive_shadow']:
            if field in request.data:
                setattr(scene_model, field, request.data[field])
        
        if 'material_overrides' in request.data:
            scene_model.material_overrides = request.data['material_overrides']
        
        scene_model.save()
        return Response(SceneModelSerializer(scene_model, context={'request': request}).data)
    
    @action(detail=True, methods=['delete'])
    def remove_model(self, request, pk=None):
        """Remove a model from the scene"""
        scene = self.get_object()
        scene_model_id = request.data.get('scene_model_id')
        
        scene_model = get_object_or_404(SceneModel, id=scene_model_id, scene=scene)
        scene_model.delete()
        
        return Response({'status': 'Model removed from scene'})
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a scene"""
        original_scene = self.get_object()
        
        new_scene = Scene3D.objects.create(
            user=request.user,
            project=original_scene.project,
            name=f"{original_scene.name} (Copy)",
            description=original_scene.description,
            scene_data=original_scene.scene_data,
            camera_settings=original_scene.camera_settings,
            lighting_settings=original_scene.lighting_settings,
            environment_settings=original_scene.environment_settings,
        )
        
        # Copy scene models
        for scene_model in original_scene.scene_models.all():
            SceneModel.objects.create(
                scene=new_scene,
                model=scene_model.model,
                position_x=scene_model.position_x,
                position_y=scene_model.position_y,
                position_z=scene_model.position_z,
                rotation_x=scene_model.rotation_x,
                rotation_y=scene_model.rotation_y,
                rotation_z=scene_model.rotation_z,
                scale_x=scene_model.scale_x,
                scale_y=scene_model.scale_y,
                scale_z=scene_model.scale_z,
                visible=scene_model.visible,
                cast_shadow=scene_model.cast_shadow,
                receive_shadow=scene_model.receive_shadow,
                material_overrides=scene_model.material_overrides,
                layer=scene_model.layer,
            )
        
        return Response(Scene3DSerializer(new_scene, context={'request': request}).data)


class Prototype3DViewSet(viewsets.ModelViewSet):
    """ViewSet for managing 3D prototypes"""
    serializer_class = Prototype3DSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Prototype3D.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        share_link = str(uuid.uuid4())[:8]
        serializer.save(user=self.request.user, share_link=share_link)
    
    @action(detail=True, methods=['post'])
    def regenerate_link(self, request, pk=None):
        """Regenerate share link"""
        prototype = self.get_object()
        prototype.share_link = str(uuid.uuid4())[:8]
        prototype.save()
        return Response({'share_link': prototype.share_link})
    
    @action(detail=True, methods=['get'])
    def preview_data(self, request, pk=None):
        """Get all data needed to render the prototype"""
        prototype = self.get_object()
        scene = prototype.scene
        
        return Response({
            'prototype': Prototype3DSerializer(prototype, context={'request': request}).data,
            'scene': Scene3DSerializer(scene, context={'request': request}).data,
        })


class ARPreviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing AR previews"""
    serializer_class = ARPreviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ARPreview.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        share_link = str(uuid.uuid4())[:8]
        serializer.save(user=self.request.user, share_link=share_link)
    
    @action(detail=True, methods=['post'])
    def generate_usdz(self, request, pk=None):
        """Generate USDZ file for iOS AR Quick Look"""
        ar_preview = self.get_object()
        # In production, this would trigger async USDZ generation
        return Response({
            'status': 'USDZ generation queued',
            'preview_id': str(ar_preview.id)
        })
    
    @action(detail=True, methods=['post'])
    def generate_qr(self, request, pk=None):
        """Generate QR code for easy mobile access"""
        ar_preview = self.get_object()
        # In production, this would generate and save QR code
        return Response({
            'status': 'QR code generation queued',
            'preview_id': str(ar_preview.id)
        })


class Conversion3DTo2DViewSet(viewsets.ModelViewSet):
    """ViewSet for 3D to 2D conversions"""
    serializer_class = Conversion3DTo2DSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversion3DTo2D.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')
        # In production, this would trigger async conversion job
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get conversion status"""
        conversion = self.get_object()
        return Response({
            'id': str(conversion.id),
            'status': conversion.status,
            'output_url': conversion.output_file.url if conversion.output_file else None,
            'error': conversion.error_message,
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_prototype(request, share_link):
    """Access a shared prototype"""
    prototype = get_object_or_404(Prototype3D, share_link=share_link, is_public=True)
    
    # Check password if set
    if prototype.password:
        provided_password = request.query_params.get('password')
        if provided_password != prototype.password:
            return Response({'error': 'Password required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Increment view count
    prototype.view_count += 1
    prototype.save(update_fields=['view_count'])
    
    scene = prototype.scene
    
    return Response({
        'prototype': {
            'id': str(prototype.id),
            'name': prototype.name,
            'description': prototype.description,
            'interactions': prototype.interactions,
            'animations': prototype.animations,
            'states': prototype.states,
            'triggers': prototype.triggers,
            'preview_mode': prototype.preview_mode,
            'auto_play': prototype.auto_play,
            'loop': prototype.loop,
        },
        'scene': {
            'id': str(scene.id),
            'name': scene.name,
            'scene_data': scene.scene_data,
            'camera_settings': scene.camera_settings,
            'lighting_settings': scene.lighting_settings,
            'environment_settings': scene.environment_settings,
        }
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_ar_preview(request, share_link):
    """Access a shared AR preview"""
    ar_preview = get_object_or_404(ARPreview, share_link=share_link, is_public=True)
    
    response_data = {
        'id': str(ar_preview.id),
        'name': ar_preview.name,
        'ar_type': ar_preview.ar_type,
        'scale': ar_preview.scale,
        'offset': [ar_preview.offset_x, ar_preview.offset_y, ar_preview.offset_z],
        'allow_scale': ar_preview.allow_scale,
        'allow_rotate': ar_preview.allow_rotate,
        'allow_move': ar_preview.allow_move,
    }
    
    # Add model/scene data
    if ar_preview.model_3d:
        response_data['model_url'] = request.build_absolute_uri(ar_preview.model_3d.file.url)
    
    if ar_preview.usdz_file:
        response_data['usdz_url'] = request.build_absolute_uri(ar_preview.usdz_file.url)
    
    return Response(response_data)

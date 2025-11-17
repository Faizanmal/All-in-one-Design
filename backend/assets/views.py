from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import models
from .models import Asset, ColorPalette, FontFamily
from .serializers import (
    AssetSerializer, AssetUploadSerializer,
    ColorPaletteSerializer, FontFamilySerializer
)
from .storage import get_storage_service
from projects.models import Project


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assets"""
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project_id')
        
        queryset = Asset.objects.filter(user=user)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_asset(request):
    """
    Upload an asset file (image, icon, font, etc.)
    
    POST /api/assets/upload/
    Content-Type: multipart/form-data
    Body:
        - file: File to upload
        - name: Asset name (optional)
        - asset_type: Type of asset (image, icon, font, etc.)
        - project_id: Project ID (optional)
        - tags: Array of tags (optional)
    """
    serializer = AssetUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    file_obj = serializer.validated_data['file']
    asset_type = serializer.validated_data['asset_type']
    name = serializer.validated_data.get('name', file_obj.name)
    project_id = serializer.validated_data.get('project_id')
    tags = serializer.validated_data.get('tags', [])
    
    # Validate project access if provided
    project = None
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
            if project.user != request.user and request.user not in project.collaborators.all():
                return Response(
                    {'error': 'You do not have access to this project'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    # Upload to storage
    storage_service = get_storage_service()
    file_url = storage_service.upload_asset(file_obj, asset_type)
    
    if not file_url:
        return Response(
            {'error': 'File upload failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Get file size
    file_size = file_obj.size
    
    # Get dimensions for images
    width = None
    height = None
    if asset_type in ['image', 'svg']:
        try:
            from PIL import Image
            import io
            
            file_obj.seek(0)
            image = Image.open(io.BytesIO(file_obj.read()))
            width, height = image.size
        except Exception:
            pass
    
    # Create asset record
    asset = Asset.objects.create(
        user=request.user,
        project=project,
        name=name,
        asset_type=asset_type,
        file_url=file_url,
        file_size=file_size,
        mime_type=file_obj.content_type,
        width=width,
        height=height,
        tags=tags
    )
    
    return Response(
        AssetSerializer(asset).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_asset(request, asset_id):
    """Delete an asset"""
    try:
        asset = Asset.objects.get(id=asset_id, user=request.user)
    except Asset.DoesNotExist:
        return Response(
            {'error': 'Asset not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Delete file from storage
    storage_service = get_storage_service()
    storage_service.delete_file(asset.file_url)
    
    # Delete database record
    asset.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)


class ColorPaletteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing color palettes"""
    serializer_class = ColorPaletteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Show public palettes and user's own palettes
        return ColorPalette.objects.filter(
            models.Q(is_public=True) | models.Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class FontFamilyViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for browsing available fonts"""
    queryset = FontFamily.objects.all()
    serializer_class = FontFamilySerializer
    permission_classes = [IsAuthenticated]

"""
API Views for Asset versioning and collections
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Asset, AssetVersion, AssetComment, AssetCollection
from .version_serializers import (
    AssetVersionSerializer, AssetCommentSerializer,
    AssetCollectionSerializer, AssetCollectionListSerializer
)


class AssetVersionViewSet(viewsets.ModelViewSet):
    """ViewSet for asset versions"""
    serializer_class = AssetVersionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        asset_id = self.request.query_params.get('asset')
        queryset = AssetVersion.objects.all()
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an asset to this version"""
        version = self.get_object()
        asset = version.asset
        
        # Create a new version from current state before restoring
        current_version_number = asset.versions.count() + 1
        AssetVersion.objects.create(
            asset=asset,
            version_number=current_version_number,
            file_url=asset.file_url,
            file_size=asset.file_size,
            change_description=f"Auto-save before restoring to v{version.version_number}",
            created_by=request.user
        )
        
        # Restore the asset to the selected version
        asset.file_url = version.file_url
        asset.file_size = version.file_size
        asset.save()
        
        return Response({
            'status': 'restored',
            'message': f'Asset restored to version {version.version_number}'
        })


class AssetCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for asset comments"""
    serializer_class = AssetCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        asset_id = self.request.query_params.get('asset')
        queryset = AssetComment.objects.filter(parent_comment__isnull=True)  # Top-level comments only
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a comment thread as resolved"""
        comment = self.get_object()
        # You can add a resolved field to the model if needed
        return Response({'status': 'comment resolved'})


class AssetCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for asset collections"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AssetCollectionListSerializer
        return AssetCollectionSerializer
    
    def get_queryset(self):
        return AssetCollection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_asset(self, request, pk=None):
        """Add an asset to the collection"""
        collection = self.get_object()
        asset_id = request.data.get('asset_id')
        
        try:
            asset = Asset.objects.get(id=asset_id, user=request.user)
            collection.assets.add(asset)
            return Response({'status': 'asset added to collection'})
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_asset(self, request, pk=None):
        """Remove an asset from the collection"""
        collection = self.get_object()
        asset_id = request.data.get('asset_id')
        
        try:
            asset = Asset.objects.get(id=asset_id)
            collection.assets.remove(asset)
            return Response({'status': 'asset removed from collection'})
        except Asset.DoesNotExist:
            return Response(
                {'error': 'Asset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

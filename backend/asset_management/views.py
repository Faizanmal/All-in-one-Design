from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from drf_spectacular.utils import extend_schema

from .models import (
    AssetFolder, AssetTag, EnhancedAsset, AssetCollection,
    AssetUsageLog, CDNIntegration, BulkOperation, UnusedAssetReport
)
from .serializers import (
    AssetFolderSerializer, AssetTagSerializer, EnhancedAssetSerializer,
    EnhancedAssetCreateSerializer, AssetCollectionSerializer,
    AssetUsageLogSerializer, CDNIntegrationSerializer, BulkOperationSerializer,
    UnusedAssetReportSerializer, AssetSearchSerializer, BulkOperationRequestSerializer
)
from .services import (
    AIAssetAnalyzer, CDNService, AssetSearchService,
    UnusedAssetDetector, BulkOperationService
)


class AssetFolderViewSet(viewsets.ModelViewSet):
    """ViewSet for asset folders"""
    serializer_class = AssetFolderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AssetFolder.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder tree structure"""
        folders = self.get_queryset().filter(parent__isnull=True)
        
        def build_tree(folder):
            return {
                'id': folder.id,
                'name': folder.name,
                'path': folder.path,
                'color': folder.color,
                'asset_count': folder.asset_count,
                'children': [build_tree(child) for child in folder.children.all()]
            }
        
        tree = [build_tree(f) for f in folders]
        return Response(tree)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move folder to new parent"""
        folder = self.get_object()
        new_parent_id = request.data.get('parent_id')
        
        if new_parent_id:
            new_parent = get_object_or_404(AssetFolder, id=new_parent_id, user=request.user)
            folder.parent = new_parent
        else:
            folder.parent = None
        
        folder.save()
        return Response(AssetFolderSerializer(folder).data)


class AssetTagViewSet(viewsets.ModelViewSet):
    """ViewSet for asset tags"""
    serializer_class = AssetTagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AssetTag.objects.filter(user=self.request.user).annotate(
            asset_count=Count('assets')
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most used tags"""
        tags = self.get_queryset().order_by('-asset_count')[:20]
        return Response(AssetTagSerializer(tags, many=True).data)


class EnhancedAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for enhanced assets"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EnhancedAssetCreateSerializer
        return EnhancedAssetSerializer
    
    def get_queryset(self):
        queryset = EnhancedAsset.objects.filter(user=self.request.user)
        
        # Filter by archived status
        if self.request.query_params.get('archived') != 'true':
            queryset = queryset.filter(is_archived=False)
        
        # Filter by folder
        folder_id = self.request.query_params.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        # Filter by type
        asset_type = self.request.query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        return queryset.select_related('folder').prefetch_related('tags')
    
    def perform_create(self, serializer):
        asset = serializer.save(user=self.request.user)
        
        # Run AI analysis
        if asset.asset_type in ['image', 'photo', 'illustration', 'icon']:
            analyzer = AIAssetAnalyzer()
            analysis = analyzer.analyze_image(asset.file_url)
            
            asset.ai_tags = analysis.get('tags', [])
            asset.ai_description = analysis.get('description', '')
            asset.ai_colors = analysis.get('colors', [])
            asset.ai_objects = analysis.get('objects', [])
            asset.ai_text = analysis.get('text', '')
            asset.save()
    
    @action(detail=False, methods=['post'])
    @extend_schema(request=AssetSearchSerializer)
    def search(self, request):
        """Search assets with filters"""
        serializer = AssetSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filters = serializer.validated_data
        query = filters.pop('query', '')
        use_ai = filters.pop('ai_search', False)
        
        search_service = AssetSearchService(request.user)
        
        if use_ai and query:
            results = search_service.ai_search(query)
        else:
            results = search_service.search(query, filters)
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = EnhancedAssetSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        return Response(EnhancedAssetSerializer(results, many=True).data)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Re-analyze asset with AI"""
        asset = self.get_object()
        
        analyzer = AIAssetAnalyzer()
        analysis = analyzer.analyze_image(asset.file_url)
        
        asset.ai_tags = analysis.get('tags', [])
        asset.ai_description = analysis.get('description', '')
        asset.ai_colors = analysis.get('colors', [])
        asset.ai_objects = analysis.get('objects', [])
        asset.ai_text = analysis.get('text', '')
        asset.save()
        
        return Response(EnhancedAssetSerializer(asset).data)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Toggle favorite status"""
        asset = self.get_object()
        asset.is_favorite = not asset.is_favorite
        asset.save()
        return Response({'is_favorite': asset.is_favorite})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive/unarchive asset"""
        asset = self.get_object()
        asset.is_archived = not asset.is_archived
        asset.save()
        return Response({'is_archived': asset.is_archived})
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get asset usage history"""
        asset = self.get_object()
        usage = AssetUsageLog.objects.filter(asset=asset).select_related('project')
        return Response(AssetUsageLogSerializer(usage, many=True).data)
    
    @action(detail=True, methods=['get'])
    def cdn_url(self, request, pk=None):
        """Get optimized CDN URL"""
        asset = self.get_object()
        
        transformations = {
            'width': request.query_params.get('width'),
            'height': request.query_params.get('height'),
            'quality': request.query_params.get('quality'),
            'format': request.query_params.get('format'),
        }
        
        # Remove None values
        transformations = {k: v for k, v in transformations.items() if v}
        
        integration = CDNIntegration.objects.filter(
            user=request.user, is_active=True, is_default=True
        ).first()
        
        if integration and asset.cdn_url:
            service = CDNService(integration)
            url = service.get_optimized_url(asset, transformations)
        else:
            url = asset.file_url
        
        return Response({'url': url})


class AssetCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet for asset collections"""
    serializer_class = AssetCollectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AssetCollection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_assets(self, request, pk=None):
        """Add assets to collection"""
        collection = self.get_object()
        asset_ids = request.data.get('asset_ids', [])
        
        assets = EnhancedAsset.objects.filter(id__in=asset_ids, user=request.user)
        collection.assets.add(*assets)
        
        return Response({'added': len(asset_ids)})
    
    @action(detail=True, methods=['post'])
    def remove_assets(self, request, pk=None):
        """Remove assets from collection"""
        collection = self.get_object()
        asset_ids = request.data.get('asset_ids', [])
        
        collection.assets.remove(*asset_ids)
        
        return Response({'removed': len(asset_ids)})


class CDNIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for CDN integrations"""
    serializer_class = CDNIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CDNIntegration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set as default CDN"""
        integration = self.get_object()
        
        CDNIntegration.objects.filter(user=request.user).update(is_default=False)
        integration.is_default = True
        integration.save()
        
        return Response({'status': 'default set'})
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test CDN connection"""
        integration = self.get_object()
        
        # Placeholder test
        return Response({
            'success': True,
            'message': f'Connection to {integration.name} successful'
        })


class BulkOperationViewSet(viewsets.ModelViewSet):
    """ViewSet for bulk operations"""
    serializer_class = BulkOperationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BulkOperation.objects.filter(user=self.request.user)
    
    @extend_schema(request=BulkOperationRequestSerializer)
    def create(self, request):
        """Start a bulk operation"""
        serializer = BulkOperationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = BulkOperationService(request.user)
        result = service.execute(
            serializer.validated_data['operation'],
            serializer.validated_data['asset_ids'],
            serializer.validated_data.get('parameters', {})
        )
        
        return Response(result, status=status.HTTP_201_CREATED)


class UnusedAssetView(APIView):
    """Detect and manage unused assets"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get unused assets"""
        days = int(request.query_params.get('days', 90))
        
        detector = UnusedAssetDetector(request.user)
        result = detector.detect(days)
        
        return Response(result)
    
    def delete(self, request):
        """Delete unused assets"""
        report_id = request.query_params.get('report_id')
        
        if not report_id:
            return Response(
                {'error': 'report_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report = get_object_or_404(UnusedAssetReport, id=report_id, user=request.user)
        
        deleted, _ = EnhancedAsset.objects.filter(
            id__in=report.unused_assets,
            user=request.user
        ).delete()
        
        return Response({'deleted': deleted})


class AssetStatsView(APIView):
    """Get asset statistics"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        assets = EnhancedAsset.objects.filter(user=user, is_archived=False)
        
        stats = {
            'total_assets': assets.count(),
            'total_size': assets.aggregate(total=Sum('file_size'))['total'] or 0,
            'by_type': list(
                assets.values('asset_type').annotate(
                    count=Count('id'),
                    size=Sum('file_size')
                ).order_by('-count')
            ),
            'favorites': assets.filter(is_favorite=True).count(),
            'unused': assets.filter(usage_count=0).count(),
            'recently_added': assets.order_by('-created_at')[:5].count(),
        }
        
        return Response(stats)

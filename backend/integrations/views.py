"""
Integration Views
REST API endpoints for third-party integrations
"""
import asyncio
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import ExternalServiceConnection, ImportedAsset, FigmaImport, StockAssetSearch
from .serializers import (
    ExternalServiceConnectionSerializer,
    ImportedAssetSerializer,
    FigmaImportSerializer,
    StockAssetSearchSerializer
)
from .stock_assets_service import StockAssetService, search_stock_assets_sync
from .figma_service import FigmaService
from projects.models import Project


class ExternalServiceConnectionViewSet(viewsets.ModelViewSet):
    """Manage external service connections"""
    serializer_class = ExternalServiceConnectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExternalServiceConnection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh OAuth token for a connection"""
        connection = self.get_object()
        
        from .oauth_service import oauth_service
        
        result = oauth_service.refresh_token(connection)
        
        if result['success']:
            return Response({
                'status': 'success',
                'message': 'Token refreshed successfully',
                'expires_at': result.get('expires_at')
            })
        else:
            return Response(
                {
                    'status': 'error',
                    'message': result.get('error', 'Token refresh failed')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect an external service"""
        connection = self.get_object()
        connection.is_active = False
        connection.save()
        return Response({'status': 'disconnected'})


class ImportedAssetViewSet(viewsets.ModelViewSet):
    """Manage imported assets"""
    serializer_class = ImportedAssetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ImportedAsset.objects.filter(user=self.request.user)
        
        # Filter by source
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        # Filter by asset type
        asset_type = self.request.query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        # Search by name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stock_assets(request):
    """
    Search for stock assets across multiple providers
    
    Query params:
        q: Search query (required)
        page: Page number (default: 1)
        per_page: Results per page (default: 20)
        providers: Comma-separated list of providers (default: all)
    """
    query = request.query_params.get('q', '')
    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 20))
    providers_str = request.query_params.get('providers', '')
    providers = providers_str.split(',') if providers_str else None
    
    # Track search
    StockAssetSearch.objects.create(
        user=request.user,
        provider=','.join(providers) if providers else 'all',
        query=query,
        filters={'page': page, 'per_page': per_page}
    )
    
    # Perform search
    results = search_stock_assets_sync(query, page, per_page, providers)
    
    return Response(results)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_stock_asset(request):
    """
    Import a stock asset to the user's library
    
    Body:
        provider: Asset provider (unsplash, pexels, pixabay)
        asset_id: Provider's asset ID
        download_url: URL to download the asset
        metadata: Asset metadata
    """
    provider = request.data.get('provider')
    asset_id = request.data.get('asset_id')
    download_url = request.data.get('download_url')
    metadata = request.data.get('metadata', {})
    
    if not all([provider, asset_id, download_url]):
        return Response(
            {'error': 'provider, asset_id, and download_url are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create imported asset record
    asset = ImportedAsset.objects.create(
        user=request.user,
        source=provider,
        asset_type='image',
        external_id=asset_id,
        external_url=download_url,
        name=metadata.get('description', f'{provider}_image_{asset_id}')[:255],
        description=metadata.get('description', ''),
        metadata=metadata,
        attribution_required=provider != 'pixabay',
        attribution_text=metadata.get('attribution', ''),
        tags=metadata.get('tags', [])
    )
    
    # Update search record if provided
    search_id = request.data.get('search_id')
    if search_id:
        StockAssetSearch.objects.filter(id=search_id).update(
            selected_asset_id=asset_id
        )
    
    return Response(ImportedAssetSerializer(asset).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def import_from_figma(request):
    """
    Import a design from Figma
    
    Body:
        file_key: Figma file key
        file_name: Name of the file
        node_ids: Optional list of specific nodes to import
        options: Import options
    """
    file_key = request.data.get('file_key')
    file_name = request.data.get('file_name', 'Figma Import')
    node_ids = request.data.get('node_ids', [])
    options = request.data.get('options', {})
    
    if not file_key:
        return Response(
            {'error': 'file_key is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's Figma connection
    connection = ExternalServiceConnection.objects.filter(
        user=request.user,
        service='figma',
        is_active=True
    ).first()
    
    if not connection:
        return Response(
            {'error': 'Figma account not connected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create import record
    figma_import = FigmaImport.objects.create(
        user=request.user,
        figma_file_key=file_key,
        figma_file_name=file_name,
        figma_node_ids=node_ids,
        import_images=options.get('import_images', True),
        import_vectors=options.get('import_vectors', True),
        import_styles=options.get('import_styles', True),
        import_components=options.get('import_components', True),
        status='processing'
    )
    
    try:
        # Initialize Figma service
        figma_service = FigmaService(access_token=connection.access_token)
        
        # Fetch Figma file
        if node_ids:
            figma_data = figma_service.get_file_nodes(file_key, node_ids)
        else:
            figma_data = figma_service.get_file(file_key)
        
        # Convert to our format
        design_data = figma_service.convert_figma_to_design_data(figma_data)
        
        # Create project
        project = Project.objects.create(
            user=request.user,
            name=file_name,
            description=f'Imported from Figma: {file_key}',
            project_type='ui_ux',
            design_data=design_data,
            ai_prompt=f'Imported from Figma file {file_name}'
        )
        
        # Update import record
        figma_import.status = 'completed'
        figma_import.result_project = project
        figma_import.completed_at = timezone.now()
        figma_import.save()
        
        return Response({
            'import_id': figma_import.id,
            'project_id': project.id,
            'status': 'completed',
            'message': f'Successfully imported {file_name}'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        figma_import.status = 'failed'
        figma_import.error_message = str(e)
        figma_import.save()
        
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_figma(request, project_id):
    """
    Export a project to Figma JSON format
    
    Returns Figma-compatible JSON that can be imported into Figma
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    figma_service = FigmaService()
    figma_json = figma_service.export_to_figma_json(
        project.design_data,
        project.name
    )
    
    return Response({
        'figma_json': figma_json,
        'filename': f'{project.name}.fig.json'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_figma_files(request):
    """Get list of Figma files accessible by the user"""
    # Get user's Figma connection
    connection = ExternalServiceConnection.objects.filter(
        user=request.user,
        service='figma',
        is_active=True
    ).first()
    
    if not connection:
        return Response(
            {'error': 'Figma account not connected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    team_id = request.query_params.get('team_id')
    project_id = request.query_params.get('project_id')
    
    figma_service = FigmaService(access_token=connection.access_token)
    
    try:
        if project_id:
            files = figma_service.get_project_files(project_id)
        elif team_id:
            projects = figma_service.get_team_projects(team_id)
            return Response(projects)
        else:
            return Response(
                {'error': 'team_id or project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(files)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class FigmaImportViewSet(viewsets.ReadOnlyModelViewSet):
    """View Figma import history"""
    serializer_class = FigmaImportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return FigmaImport.objects.filter(user=self.request.user)

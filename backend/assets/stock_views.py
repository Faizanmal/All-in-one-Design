"""
Stock Assets API Views
Provides REST endpoints for searching and importing stock assets
from Unsplash, Pexels, and Pixabay.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .stock_service import StockAssetService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_stock_assets(request):
    """
    Search stock photos, videos, and illustrations.

    GET /api/v1/assets/stock/search/?q=nature&provider=all&type=photo&page=1

    Query params:
        q (required): Search keywords
        provider: 'unsplash', 'pexels', 'pixabay', or 'all' (default: 'all')
        type: 'photo', 'video', 'illustration', 'vector' (default: 'photo')
        page: Page number (default: 1)
        per_page: Results per page, max 30 (default: 20)
        orientation: 'landscape', 'portrait', 'squarish'
        color: Color filter
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response(
            {'error': 'Search query (q) is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = StockAssetService()
    result = service.search(
        query=query,
        provider=request.query_params.get('provider', 'all'),
        media_type=request.query_params.get('type', 'photo'),
        page=int(request.query_params.get('page', 1)),
        per_page=int(request.query_params.get('per_page', 20)),
        orientation=request.query_params.get('orientation'),
        color=request.query_params.get('color'),
    )
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_asset_download(request, provider, asset_id):
    """
    Get the download URL for a stock asset.

    GET /api/v1/assets/stock/download/<provider>/<asset_id>/

    This endpoint triggers download tracking where required by the
    provider's API guidelines (e.g., Unsplash).
    """
    service = StockAssetService()
    url = service.get_download_url(provider, asset_id)
    if not url:
        return Response(
            {'error': 'Could not retrieve download URL'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response({'download_url': url, 'provider': provider, 'asset_id': asset_id})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stock_providers(request):
    """
    List available stock asset providers and their status.

    GET /api/v1/assets/stock/providers/
    """
    import os
    providers = [
        {
            'id': 'unsplash',
            'name': 'Unsplash',
            'types': ['photo'],
            'configured': bool(os.getenv('UNSPLASH_ACCESS_KEY')),
            'license': 'Unsplash License (free for commercial use)',
            'attribution_required': True,
        },
        {
            'id': 'pexels',
            'name': 'Pexels',
            'types': ['photo', 'video'],
            'configured': bool(os.getenv('PEXELS_API_KEY')),
            'license': 'Pexels License (free for commercial use)',
            'attribution_required': False,
        },
        {
            'id': 'pixabay',
            'name': 'Pixabay',
            'types': ['photo', 'illustration', 'vector', 'video'],
            'configured': bool(os.getenv('PIXABAY_API_KEY')),
            'license': 'Pixabay License (free for commercial use)',
            'attribution_required': False,
        },
    ]
    return Response({'providers': providers})

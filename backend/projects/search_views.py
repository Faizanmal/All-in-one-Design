"""
Advanced search API views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_datetime
from .search_service import SearchService
from .serializers import ProjectSerializer
from analytics.models import UserActivity


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def search_projects(request):
    """
    Advanced project search with multiple filters
    
    GET/POST /api/v1/projects/search/
    
    Query Parameters / Body:
    - q: Search query string
    - project_types: List of project types
    - created_after: ISO datetime string
    - created_before: ISO datetime string
    - min_width: Minimum canvas width
    - max_width: Maximum canvas width
    - min_height: Minimum canvas height
    - max_height: Maximum canvas height
    - has_ai_prompt: Boolean
    - is_public: Boolean
    - owner_username: Username filter
    - colors: List of hex colors
    - sort_by: Sort field (default: -updated_at)
    - page: Page number
    - page_size: Results per page
    """
    # Get parameters from query string or request body
    if request.method == 'POST':
        params = request.data
    else:
        params = request.query_params
    
    query = params.get('q', '').strip()
    page = int(params.get('page', 1))
    page_size = int(params.get('page_size', 20))
    
    # Build filters dictionary
    filters = {}
    
    # Project types (can be comma-separated or list)
    if 'project_types' in params:
        project_types = params.get('project_types')
        if isinstance(project_types, str):
            project_types = [pt.strip() for pt in project_types.split(',') if pt.strip()]
        filters['project_types'] = project_types
    
    # Date filters
    if 'created_after' in params:
        filters['created_after'] = parse_datetime(params['created_after'])
    
    if 'created_before' in params:
        filters['created_before'] = parse_datetime(params['created_before'])
    
    if 'updated_after' in params:
        filters['updated_after'] = parse_datetime(params['updated_after'])
    
    if 'updated_before' in params:
        filters['updated_before'] = parse_datetime(params['updated_before'])
    
    # Canvas size filters
    if 'min_width' in params:
        filters['min_width'] = int(params['min_width'])
    
    if 'max_width' in params:
        filters['max_width'] = int(params['max_width'])
    
    if 'min_height' in params:
        filters['min_height'] = int(params['min_height'])
    
    if 'max_height' in params:
        filters['max_height'] = int(params['max_height'])
    
    # Boolean filters
    if 'has_ai_prompt' in params:
        filters['has_ai_prompt'] = params['has_ai_prompt'] in ['true', 'True', '1', True]
    
    if 'is_public' in params:
        filters['is_public'] = params['is_public'] in ['true', 'True', '1', True]
    
    # Owner filter
    if 'owner_username' in params:
        filters['owner_username'] = params['owner_username']
    
    # Color filters
    if 'colors' in params:
        colors = params.get('colors')
        if isinstance(colors, str):
            colors = [c.strip() for c in colors.split(',') if c.strip()]
        filters['colors'] = colors
    
    # Sort order
    if 'sort_by' in params:
        filters['sort_by'] = params['sort_by']
    
    # Get user for permission filtering
    user = request.user if request.user.is_authenticated else None
    
    # Execute search
    if query:
        results = SearchService.search_projects(query, user=user, filters=filters)
    else:
        results = SearchService.filter_projects_advanced(user=user, filters=filters)
    
    # Track search activity
    if user and user.is_authenticated:
        UserActivity.objects.create(
            user=user,
            action='search',
            description=f"Searched for: {query}" if query else "Browsed projects",
            metadata={
                'query': query,
                'filters': filters,
                'result_count': results.count()
            }
        )
    
    # Pagination
    total_count = results.count()
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    paginated_results = results[start_idx:end_idx]
    
    # Serialize results
    serializer = ProjectSerializer(paginated_results, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'has_next': end_idx < total_count,
        'has_previous': page > 1
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def autocomplete(request):
    """
    Get autocomplete suggestions for search
    
    GET /api/v1/projects/autocomplete/?q=search+term
    """
    query = request.query_params.get('q', '').strip()
    limit = int(request.query_params.get('limit', 10))
    
    if not query:
        return Response({'suggestions': []})
    
    user = request.user if request.user.is_authenticated else None
    suggestions = SearchService.autocomplete_projects(query, user=user, limit=limit)
    
    return Response({
        'suggestions': list(suggestions)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """
    Get general search suggestions
    
    GET /api/v1/projects/search-suggestions/?q=partial
    """
    query = request.query_params.get('q', '').strip()
    limit = int(request.query_params.get('limit', 5))
    
    suggestions = SearchService.get_search_suggestions(query, limit=limit)
    
    return Response({
        'suggestions': suggestions
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def popular_searches(request):
    """
    Get popular search terms
    
    GET /api/v1/projects/popular-searches/
    """
    limit = int(request.query_params.get('limit', 10))
    
    popular = SearchService.get_popular_searches(limit=limit)
    
    return Response({
        'popular_searches': popular
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_filters(request):
    """
    Get available filter options for search
    
    GET /api/v1/projects/search-filters/
    """
    from projects.models import Project
    from django.db.models import Min, Max
    
    # Get unique project types
    project_types = Project.objects.filter(
        is_public=True
    ).values_list('project_type', flat=True).distinct()
    
    # Get canvas size ranges
    size_stats = Project.objects.filter(
        is_public=True
    ).aggregate(
        min_width=Min('canvas_width'),
        max_width=Max('canvas_width'),
        min_height=Min('canvas_height'),
        max_height=Max('canvas_height')
    )
    
    # Get date range
    date_stats = Project.objects.filter(
        is_public=True
    ).aggregate(
        oldest=Min('created_at'),
        newest=Max('created_at')
    )
    
    return Response({
        'project_types': list(project_types),
        'canvas_size_ranges': size_stats,
        'date_range': {
            'oldest': date_stats['oldest'],
            'newest': date_stats['newest']
        },
        'sort_options': [
            {'value': '-updated_at', 'label': 'Most Recently Updated'},
            {'value': '-created_at', 'label': 'Newest First'},
            {'value': 'created_at', 'label': 'Oldest First'},
            {'value': 'name', 'label': 'Name (A-Z)'},
            {'value': '-name', 'label': 'Name (Z-A)'},
        ]
    })

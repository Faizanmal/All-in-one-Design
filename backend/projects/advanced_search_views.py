"""
Advanced Search API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .advanced_search_service import AdvancedSearchService
from .serializers import ProjectSerializer
from assets.serializers import AssetSerializer
from .template_serializers import DesignTemplateListSerializer
from teams.serializers import TeamSerializer


class AdvancedProjectSearchView(APIView):
    """Advanced search endpoint for projects"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Search projects with filters"""
        queryset = AdvancedSearchService.search_projects(
            user=request.user,
            query_params=request.query_params
        )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        paginated_queryset = queryset[start:end]
        
        serializer = ProjectSerializer(paginated_queryset, many=True)
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': serializer.data
        })


class AdvancedAssetSearchView(APIView):
    """Advanced search endpoint for assets"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Search assets with filters"""
        queryset = AdvancedSearchService.search_assets(
            user=request.user,
            query_params=request.query_params
        )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        paginated_queryset = queryset[start:end]
        
        serializer = AssetSerializer(paginated_queryset, many=True)
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': serializer.data
        })


class AdvancedTemplateSearchView(APIView):
    """Advanced search endpoint for templates"""
    
    def get(self, request):
        """Search templates with filters"""
        queryset = AdvancedSearchService.search_templates(
            query_params=request.query_params
        )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        paginated_queryset = queryset[start:end]
        
        serializer = DesignTemplateListSerializer(paginated_queryset, many=True)
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': serializer.data
        })


class AdvancedTeamSearchView(APIView):
    """Advanced search endpoint for teams"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Search teams with filters"""
        queryset = AdvancedSearchService.search_teams(
            user=request.user,
            query_params=request.query_params
        )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = queryset.count()
        paginated_queryset = queryset[start:end]
        
        serializer = TeamSerializer(paginated_queryset, many=True)
        
        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': serializer.data
        })


class GlobalSearchView(APIView):
    """Global search across all content types"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Search across projects, assets, templates, and teams"""
        search_text = request.query_params.get('q', '').strip()
        
        if not search_text or len(search_text) < 2:
            return Response(
                {'error': 'Search query must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = AdvancedSearchService.global_search(
            user=request.user,
            search_text=search_text
        )
        
        return Response(results)

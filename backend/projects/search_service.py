"""
Search and filtering service for projects and designs
"""
from django.db.models import Q
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank,
    TrigramSimilarity
)
from projects.models import Project, DesignComponent


class SearchService:
    """Service for searching projects and components"""
    
    @staticmethod
    def search_projects(query, user=None, filters=None):
        """
        Full-text search for projects
        
        Args:
            query: Search query string
            user: User object (for permission filtering)
            filters: Additional filters (dict)
            
        Returns:
            QuerySet of matching projects
        """
        # Base queryset
        queryset = Project.objects.all()
        
        # User permission filtering
        if user and user.is_authenticated:
            queryset = queryset.filter(
                Q(user=user) | 
                Q(is_public=True) |
                Q(collaborators=user)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        # Apply filters
        if filters:
            if 'project_type' in filters and filters['project_type']:
                queryset = queryset.filter(project_type=filters['project_type'])
            
            if 'created_after' in filters and filters['created_after']:
                queryset = queryset.filter(created_at__gte=filters['created_after'])
            
            if 'created_before' in filters and filters['created_before']:
                queryset = queryset.filter(created_at__lte=filters['created_before'])
            
            if 'has_ai' in filters and filters['has_ai']:
                queryset = queryset.exclude(ai_prompt='')
        
        # Full-text search if query provided
        if query:
            # Create search vector for multiple fields
            search_vector = (
                SearchVector('name', weight='A') +
                SearchVector('description', weight='B') +
                SearchVector('ai_prompt', weight='C')
            )
            search_query = SearchQuery(query)
            
            queryset = queryset.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by('-rank')
        else:
            queryset = queryset.order_by('-updated_at')
        
        return queryset
    
    @staticmethod
    def autocomplete_projects(query, user=None, limit=10):
        """
        Autocomplete suggestions for project names
        
        Args:
            query: Search query string
            user: User object
            limit: Maximum number of results
            
        Returns:
            List of project name suggestions
        """
        # Base queryset
        queryset = Project.objects.all()
        
        # User permission filtering
        if user and user.is_authenticated:
            queryset = queryset.filter(
                Q(user=user) | 
                Q(is_public=True) |
                Q(collaborators=user)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        if not query:
            return queryset.order_by('-updated_at')[:limit]
        
        # Use trigram similarity for fuzzy matching
        queryset = queryset.annotate(
            similarity=TrigramSimilarity('name', query)
        ).filter(similarity__gt=0.1).order_by('-similarity')
        
        return queryset[:limit]
    
    @staticmethod
    def filter_projects_advanced(user=None, filters=None):
        """
        Advanced filtering with multiple criteria
        
        Args:
            user: User object
            filters: Dict of filter criteria
            
        Returns:
            Filtered QuerySet
        """
        queryset = Project.objects.all()
        
        # User permission filtering
        if user and user.is_authenticated:
            queryset = queryset.filter(
                Q(user=user) | 
                Q(is_public=True) |
                Q(collaborators=user)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        if not filters:
            return queryset.order_by('-updated_at')
        
        # Project type filter
        if 'project_types' in filters and filters['project_types']:
            queryset = queryset.filter(project_type__in=filters['project_types'])
        
        # Date range filters
        if 'created_after' in filters and filters['created_after']:
            queryset = queryset.filter(created_at__gte=filters['created_after'])
        
        if 'created_before' in filters and filters['created_before']:
            queryset = queryset.filter(created_at__lte=filters['created_before'])
        
        if 'updated_after' in filters and filters['updated_after']:
            queryset = queryset.filter(updated_at__gte=filters['updated_after'])
        
        if 'updated_before' in filters and filters['updated_before']:
            queryset = queryset.filter(updated_at__lte=filters['updated_before'])
        
        # Canvas size filters
        if 'min_width' in filters and filters['min_width']:
            queryset = queryset.filter(canvas_width__gte=filters['min_width'])
        
        if 'max_width' in filters and filters['max_width']:
            queryset = queryset.filter(canvas_width__lte=filters['max_width'])
        
        if 'min_height' in filters and filters['min_height']:
            queryset = queryset.filter(canvas_height__gte=filters['min_height'])
        
        if 'max_height' in filters and filters['max_height']:
            queryset = queryset.filter(canvas_height__lte=filters['max_height'])
        
        # AI-related filters
        if 'has_ai_prompt' in filters:
            if filters['has_ai_prompt']:
                queryset = queryset.exclude(ai_prompt='')
            else:
                queryset = queryset.filter(ai_prompt='')
        
        if 'has_color_palette' in filters and filters['has_color_palette']:
            queryset = queryset.exclude(color_palette=[])
        
        # Public/private filter
        if 'is_public' in filters and filters['is_public'] is not None:
            queryset = queryset.filter(is_public=filters['is_public'])
        
        # Owner filter
        if 'owner_username' in filters and filters['owner_username']:
            queryset = queryset.filter(user__username__icontains=filters['owner_username'])
        
        # Tags/color palette search
        if 'colors' in filters and filters['colors']:
            # Search for projects with specific colors in palette
            for color in filters['colors']:
                queryset = queryset.filter(color_palette__contains=[color])
        
        # Sort order
        sort_by = filters.get('sort_by', '-updated_at')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @staticmethod
    def search_components(query, project_id=None):
        """
        Search design components
        
        Args:
            query: Search query string
            project_id: Optional project ID to filter by
            
        Returns:
            QuerySet of matching components
        """
        queryset = DesignComponent.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        if query:
            queryset = queryset.filter(
                Q(component_type__icontains=query) |
                Q(ai_prompt__icontains=query) |
                Q(properties__icontains=query)
            )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_search_suggestions(query, limit=5):
        """
        Get search suggestions based on query
        
        Args:
            query: Partial search query
            limit: Maximum suggestions
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Get project name suggestions
        projects = Project.objects.filter(
            name__icontains=query,
            is_public=True
        ).values_list('name', flat=True)[:limit]
        suggestions.extend(list(projects))
        
        # Get unique project types
        if len(suggestions) < limit:
            types = Project.objects.filter(
                is_public=True
            ).values_list('project_type', flat=True).distinct()[:limit - len(suggestions)]
            suggestions.extend(list(types))
        
        return suggestions[:limit]
    
    @staticmethod
    def get_popular_searches(limit=10):
        """
        Get most popular search terms (would need analytics integration)
        
        Args:
            limit: Maximum results
            
        Returns:
            List of popular search terms
        """
        # This would integrate with analytics to track searches
        # For now, return most common project types
        from django.db.models import Count
        
        popular = Project.objects.filter(
            is_public=True
        ).values('project_type').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        return [p['project_type'] for p in popular]

"""
Enhanced semantic search service for projects
"""
from typing import List, Dict, Any, Optional
from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from projects.models import Project, DesignComponent
from templates.models import Template


class SemanticSearchService:
    """
    Enhanced search service with semantic capabilities
    """
    
    @staticmethod
    def search_projects(
        query: str,
        user=None,
        filters: Optional[Dict] = None,
        limit: int = 20
    ) -> List[Project]:
        """
        Search projects with semantic understanding
        
        Args:
            query: Search query string
            user: Optional user to filter by permissions
            filters: Additional filters (project_type, tags, etc.)
            limit: Maximum results to return
            
        Returns:
            List of matching projects
        """
        # Base queryset
        queryset = Project.objects.all()
        
        # Filter by user permissions
        if user:
            queryset = queryset.filter(
                Q(user=user) |
                Q(collaborators=user) |
                Q(is_public=True)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        # Apply filters
        if filters:
            if 'project_type' in filters:
                queryset = queryset.filter(project_type=filters['project_type'])
            
            if 'tags' in filters:
                # Assuming tags are stored in design_data or a tags field
                for tag in filters['tags']:
                    queryset = queryset.filter(design_data__tags__contains=[tag])
            
            if 'date_from' in filters:
                queryset = queryset.filter(created_at__gte=filters['date_from'])
            
            if 'date_to' in filters:
                queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        # Text search across multiple fields
        search_results = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(ai_prompt__icontains=query)
        )
        
        # Order by relevance (prioritize name matches)
        search_results = search_results.annotate(
            name_match=Count('id', filter=Q(name__icontains=query))
        ).order_by('-name_match', '-updated_at')
        
        return list(search_results[:limit])
    
    @staticmethod
    def search_by_color(
        hex_color: str,
        tolerance: int = 30,
        user=None,
        limit: int = 20
    ) -> List[Project]:
        """
        Search projects by color palette
        
        Args:
            hex_color: Hex color to search for
            tolerance: Color matching tolerance (0-255)
            user: Optional user filter
            limit: Maximum results
            
        Returns:
            List of projects with matching colors
        """
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        target_r = int(hex_color[0:2], 16)
        target_g = int(hex_color[2:4], 16)
        target_b = int(hex_color[4:6], 16)
        
        # Base queryset
        queryset = Project.objects.all()
        
        if user:
            queryset = queryset.filter(
                Q(user=user) | Q(collaborators=user) | Q(is_public=True)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        # Filter projects with color palette
        matching_projects = []
        
        for project in queryset.filter(color_palette__isnull=False):
            for color in project.color_palette:
                if isinstance(color, str):
                    try:
                        color = color.lstrip('#')
                        r = int(color[0:2], 16)
                        g = int(color[2:4], 16)
                        b = int(color[4:6], 16)
                        
                        # Check if color is within tolerance
                        if (abs(r - target_r) <= tolerance and
                            abs(g - target_g) <= tolerance and
                            abs(b - target_b) <= tolerance):
                            matching_projects.append(project)
                            break
                    except (ValueError, IndexError):
                        continue
        
        return matching_projects[:limit]
    
    @staticmethod
    def search_templates(
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 20
    ) -> List[Template]:
        """
        Search templates with filters
        
        Args:
            query: Search query
            filters: Additional filters
            limit: Maximum results
            
        Returns:
            List of matching templates
        """
        queryset = Template.objects.filter(is_public=True)
        
        # Apply filters
        if filters:
            if 'category' in filters:
                queryset = queryset.filter(category=filters['category'])
            
            if 'is_premium' in filters:
                queryset = queryset.filter(is_premium=filters['is_premium'])
            
            if 'tags' in filters:
                for tag in filters['tags']:
                    queryset = queryset.filter(tags__contains=[tag])
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__contains=[query])
            )
        
        return list(queryset.order_by('-use_count', '-created_at')[:limit])
    
    @staticmethod
    def get_similar_projects(
        project: Project,
        limit: int = 10
    ) -> List[Project]:
        """
        Find similar projects based on various attributes
        
        Args:
            project: Source project
            limit: Maximum similar projects to return
            
        Returns:
            List of similar projects
        """
        similar_projects = Project.objects.filter(
            is_public=True
        ).exclude(id=project.id)
        
        # Filter by project type
        similar_projects = similar_projects.filter(
            project_type=project.project_type
        )
        
        # Filter by similar colors (if color palette exists)
        if project.color_palette:
            # This is a simplified approach
            # In production, you'd use more sophisticated color matching
            similar_projects = similar_projects.filter(
                color_palette__overlap=project.color_palette
            )
        
        # Order by recency and use count
        similar_projects = similar_projects.order_by('-updated_at')
        
        return list(similar_projects[:limit])
    
    @staticmethod
    def search_by_ai_prompt(
        prompt_keywords: List[str],
        user=None,
        limit: int = 20
    ) -> List[Project]:
        """
        Search projects by AI prompt keywords
        
        Args:
            prompt_keywords: List of keywords to search in AI prompts
            user: Optional user filter
            limit: Maximum results
            
        Returns:
            List of matching projects
        """
        queryset = Project.objects.filter(ai_prompt__isnull=False).exclude(ai_prompt='')
        
        if user:
            queryset = queryset.filter(
                Q(user=user) | Q(collaborators=user) | Q(is_public=True)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        # Search for any keyword in AI prompt
        query = Q()
        for keyword in prompt_keywords:
            query |= Q(ai_prompt__icontains=keyword)
        
        queryset = queryset.filter(query)
        
        return list(queryset.order_by('-created_at')[:limit])
    
    @staticmethod
    def advanced_search(
        text_query: Optional[str] = None,
        project_type: Optional[str] = None,
        color_palette: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        min_components: Optional[int] = None,
        max_components: Optional[int] = None,
        user=None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Advanced search with multiple criteria
        
        Returns:
            Dictionary with search results and metadata
        """
        queryset = Project.objects.all()
        
        # User permissions
        if user:
            queryset = queryset.filter(
                Q(user=user) | Q(collaborators=user) | Q(is_public=True)
            ).distinct()
        else:
            queryset = queryset.filter(is_public=True)
        
        # Apply filters
        if text_query:
            queryset = queryset.filter(
                Q(name__icontains=text_query) |
                Q(description__icontains=text_query) |
                Q(ai_prompt__icontains=text_query)
            )
        
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        if color_palette:
            for color in color_palette:
                queryset = queryset.filter(color_palette__contains=[color])
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Annotate with component count
        queryset = queryset.annotate(component_count=Count('components'))
        
        if min_components is not None:
            queryset = queryset.filter(component_count__gte=min_components)
        
        if max_components is not None:
            queryset = queryset.filter(component_count__lte=max_components)
        
        # Get total count
        total_count = queryset.count()
        
        # Get results
        results = list(queryset.order_by('-updated_at')[:limit])
        
        # Get facets for filtering
        facets = {
            'project_types': queryset.values('project_type').annotate(
                count=Count('id')
            ).order_by('-count'),
            'total_results': total_count,
            'returned_results': len(results)
        }
        
        return {
            'results': results,
            'facets': facets,
            'total': total_count
        }

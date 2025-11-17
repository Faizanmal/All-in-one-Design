"""
Advanced Search Service with filtering and full-text search
"""
from django.db.models import Q, Count, Avg
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from projects.models import Project, DesignTemplate, ProjectTag
from assets.models import Asset
from teams.models import Team


class AdvancedSearchService:
    """
    Advanced search service with filters, sorting, and full-text search
    """
    
    @staticmethod
    def search_projects(user, query_params):
        """
        Search projects with advanced filters
        
        Args:
            user: The requesting user
            query_params: Dictionary of search parameters
        
        Returns:
            QuerySet of filtered projects
        """
        queryset = Project.objects.filter(
            Q(user=user) | Q(collaborators=user) | Q(is_public=True)
        ).distinct()
        
        # Text search
        search_text = query_params.get('q', '').strip()
        if search_text:
            queryset = queryset.filter(
                Q(name__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(ai_prompt__icontains=search_text)
            )
        
        # Filters
        project_type = query_params.get('type')
        if project_type:
            queryset = queryset.filter(project_type=project_type)
        
        # Date range
        date_from = query_params.get('date_from')
        date_to = query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Tags
        tags = query_params.getlist('tags')
        if tags:
            for tag in tags:
                queryset = queryset.filter(tag_associations__tag__slug=tag)
        
        # Has AI content
        has_ai = query_params.get('has_ai')
        if has_ai == 'true':
            queryset = queryset.exclude(ai_prompt='')
        
        # Collaborators filter
        min_collaborators = query_params.get('min_collaborators')
        if min_collaborators:
            queryset = queryset.annotate(
                collab_count=Count('collaborators')
            ).filter(collab_count__gte=int(min_collaborators))
        
        # Sorting
        sort_by = query_params.get('sort', '-updated_at')
        valid_sorts = [
            'name', '-name', 'created_at', '-created_at', 
            'updated_at', '-updated_at'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @staticmethod
    def search_assets(user, query_params):
        """
        Search assets with advanced filters
        
        Args:
            user: The requesting user
            query_params: Dictionary of search parameters
        
        Returns:
            QuerySet of filtered assets
        """
        queryset = Asset.objects.filter(user=user)
        
        # Text search
        search_text = query_params.get('q', '').strip()
        if search_text:
            queryset = queryset.filter(
                Q(name__icontains=search_text) |
                Q(tags__contains=[search_text]) |
                Q(ai_prompt__icontains=search_text)
            )
        
        # Asset type filter
        asset_type = query_params.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        
        # Size filters
        min_size = query_params.get('min_size')
        max_size = query_params.get('max_size')
        if min_size:
            queryset = queryset.filter(file_size__gte=int(min_size))
        if max_size:
            queryset = queryset.filter(file_size__lte=int(max_size))
        
        # Dimensions (for images)
        min_width = query_params.get('min_width')
        max_width = query_params.get('max_width')
        min_height = query_params.get('min_height')
        max_height = query_params.get('max_height')
        
        if min_width:
            queryset = queryset.filter(width__gte=int(min_width))
        if max_width:
            queryset = queryset.filter(width__lte=int(max_width))
        if min_height:
            queryset = queryset.filter(height__gte=int(min_height))
        if max_height:
            queryset = queryset.filter(height__lte=int(max_height))
        
        # AI generated filter
        ai_generated = query_params.get('ai_generated')
        if ai_generated == 'true':
            queryset = queryset.filter(ai_generated=True)
        elif ai_generated == 'false':
            queryset = queryset.filter(ai_generated=False)
        
        # Tags
        tags = query_params.getlist('tags')
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
        
        # Project filter
        project_id = query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Collection filter
        collection_id = query_params.get('collection')
        if collection_id:
            queryset = queryset.filter(collections__id=collection_id)
        
        # Date range
        date_from = query_params.get('date_from')
        date_to = query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Sorting
        sort_by = query_params.get('sort', '-created_at')
        valid_sorts = [
            'name', '-name', 'created_at', '-created_at',
            'file_size', '-file_size', 'width', '-width', 'height', '-height'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @staticmethod
    def search_templates(query_params):
        """
        Search design templates with filters
        
        Args:
            query_params: Dictionary of search parameters
        
        Returns:
            QuerySet of filtered templates
        """
        queryset = DesignTemplate.objects.filter(is_public=True)
        
        # Text search
        search_text = query_params.get('q', '').strip()
        if search_text:
            queryset = queryset.filter(
                Q(name__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(tags__contains=[search_text])
            )
        
        # Category filter
        category = query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Premium/Featured filters
        is_premium = query_params.get('premium')
        if is_premium == 'true':
            queryset = queryset.filter(is_premium=True)
        elif is_premium == 'false':
            queryset = queryset.filter(is_premium=False)
        
        is_featured = query_params.get('featured')
        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Rating filter
        min_rating = query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(rating__gte=float(min_rating))
        
        # Tags
        tags = query_params.getlist('tags')
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
        
        # Color palette filter (search for specific colors)
        colors = query_params.getlist('colors')
        if colors:
            for color in colors:
                queryset = queryset.filter(color_palette__contains=[color])
        
        # Sorting
        sort_by = query_params.get('sort', '-use_count')
        valid_sorts = [
            'name', '-name', 'use_count', '-use_count',
            'favorite_count', '-favorite_count', 'rating', '-rating',
            'created_at', '-created_at'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @staticmethod
    def search_teams(user, query_params):
        """
        Search teams
        
        Args:
            user: The requesting user
            query_params: Dictionary of search parameters
        
        Returns:
            QuerySet of filtered teams
        """
        # User's teams or public teams
        queryset = Team.objects.filter(
            Q(members=user) | Q(is_active=True)
        ).distinct()
        
        # Text search
        search_text = query_params.get('q', '').strip()
        if search_text:
            queryset = queryset.filter(
                Q(name__icontains=search_text) |
                Q(description__icontains=search_text)
            )
        
        # Member count filters
        min_members = query_params.get('min_members')
        max_members = query_params.get('max_members')
        
        if min_members or max_members:
            queryset = queryset.annotate(member_count=Count('members'))
            if min_members:
                queryset = queryset.filter(member_count__gte=int(min_members))
            if max_members:
                queryset = queryset.filter(member_count__lte=int(max_members))
        
        # Active filter
        is_active = query_params.get('active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active == 'false':
            queryset = queryset.filter(is_active=False)
        
        # Sorting
        sort_by = query_params.get('sort', '-created_at')
        valid_sorts = ['name', '-name', 'created_at', '-created_at']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    @staticmethod
    def global_search(user, search_text):
        """
        Search across all content types
        
        Args:
            user: The requesting user
            search_text: Search query
        
        Returns:
            Dictionary with results from each content type
        """
        results = {
            'projects': [],
            'assets': [],
            'templates': [],
            'teams': []
        }
        
        if not search_text or len(search_text) < 2:
            return results
        
        # Search projects
        projects = Project.objects.filter(
            Q(user=user) | Q(collaborators=user) | Q(is_public=True)
        ).filter(
            Q(name__icontains=search_text) |
            Q(description__icontains=search_text)
        ).distinct()[:10]
        
        results['projects'] = [
            {'id': p.id, 'name': p.name, 'type': 'project'} 
            for p in projects
        ]
        
        # Search assets
        assets = Asset.objects.filter(user=user).filter(
            Q(name__icontains=search_text) |
            Q(tags__contains=[search_text])
        )[:10]
        
        results['assets'] = [
            {'id': a.id, 'name': a.name, 'type': 'asset'} 
            for a in assets
        ]
        
        # Search templates
        templates = DesignTemplate.objects.filter(
            is_public=True
        ).filter(
            Q(name__icontains=search_text) |
            Q(description__icontains=search_text)
        )[:10]
        
        results['templates'] = [
            {'id': t.id, 'name': t.name, 'type': 'template'} 
            for t in templates
        ]
        
        # Search teams
        teams = Team.objects.filter(
            Q(members=user) | Q(is_active=True)
        ).filter(
            Q(name__icontains=search_text) |
            Q(description__icontains=search_text)
        ).distinct()[:10]
        
        results['teams'] = [
            {'id': t.id, 'name': t.name, 'type': 'team'} 
            for t in teams
        ]
        
        return results

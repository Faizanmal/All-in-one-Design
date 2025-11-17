"""
API Views for Design Templates
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Avg

from .models import (
    DesignTemplate, TemplateFavorite, TemplateRating, 
    ProjectTag, Project
)
from .template_serializers import (
    DesignTemplateSerializer, DesignTemplateListSerializer,
    TemplateFavoriteSerializer, TemplateRatingSerializer,
    ProjectTagSerializer
)


class DesignTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for design templates"""
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DesignTemplateListSerializer
        return DesignTemplateSerializer
    
    def get_queryset(self):
        queryset = DesignTemplate.objects.filter(is_public=True)
        
        # Filters
        category = self.request.query_params.get('category')
        is_premium = self.request.query_params.get('premium')
        is_featured = self.request.query_params.get('featured')
        search = self.request.query_params.get('search')
        tags = self.request.query_params.getlist('tags')
        
        if category:
            queryset = queryset.filter(category=category)
        if is_premium is not None:
            queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(tags__contains=[search])
            )
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a new project from this template"""
        template = self.get_object()
        
        # Increment use count
        template.use_count += 1
        template.save()
        
        # Create project from template
        project = Project.objects.create(
            user=request.user,
            name=request.data.get('name', f"{template.name} - Copy"),
            description=template.description,
            project_type=request.data.get('project_type', 'graphic'),
            canvas_width=template.canvas_width,
            canvas_height=template.canvas_height,
            canvas_background=template.canvas_background,
            design_data=template.design_data.copy(),
            color_palette=template.color_palette.copy(),
            suggested_fonts=template.suggested_fonts.copy()
        )
        
        return Response({
            'status': 'project created',
            'project_id': project.id,
            'project_name': project.name
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Add template to favorites"""
        template = self.get_object()
        
        favorite, created = TemplateFavorite.objects.get_or_create(
            user=request.user,
            template=template
        )
        
        if created:
            template.favorite_count += 1
            template.save()
            return Response({'status': 'added to favorites'})
        else:
            return Response({'status': 'already favorited'})
    
    @action(detail=True, methods=['post'])
    def unfavorite(self, request, pk=None):
        """Remove template from favorites"""
        template = self.get_object()
        
        deleted = TemplateFavorite.objects.filter(
            user=request.user,
            template=template
        ).delete()
        
        if deleted[0] > 0:
            template.favorite_count = max(0, template.favorite_count - 1)
            template.save()
            return Response({'status': 'removed from favorites'})
        else:
            return Response({'status': 'not in favorites'})
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a template"""
        template = self.get_object()
        rating_value = request.data.get('rating')
        review_text = request.data.get('review', '')
        
        if not rating_value or not (1 <= int(rating_value) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rating, created = TemplateRating.objects.update_or_create(
            user=request.user,
            template=template,
            defaults={'rating': rating_value, 'review': review_text}
        )
        
        # Update template average rating
        avg_rating = template.ratings.aggregate(Avg('rating'))['rating__avg']
        template.rating = round(avg_rating, 2) if avg_rating else 0
        template.save()
        
        serializer = TemplateRatingSerializer(rating)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_favorites(self, request):
        """Get user's favorite templates"""
        favorites = TemplateFavorite.objects.filter(user=request.user)
        template_ids = favorites.values_list('template_id', flat=True)
        templates = DesignTemplate.objects.filter(id__in=template_ids)
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)


class ProjectTagViewSet(viewsets.ModelViewSet):
    """ViewSet for project tags"""
    serializer_class = ProjectTagSerializer
    permission_classes = [IsAuthenticated]
    queryset = ProjectTag.objects.all()
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular tags"""
        tags = ProjectTag.objects.order_by('-project_count')[:20]
        serializer = self.get_serializer(tags, many=True)
        return Response(serializer.data)

"""
Enhanced template management with marketplace features
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404

from .models import DesignTemplate as Template, Project
from .template_serializers import (
    DesignTemplateSerializer as TemplateSerializer,
    DesignTemplateListSerializer as TemplateListSerializer,
)


class TemplateComponentSerializer:
    """Placeholder serializer"""
    pass


class TemplateCreateFromProjectSerializer:
    """Placeholder serializer"""
    pass


class TemplateComponent:
    """Placeholder model - templates can have components"""
    pass


class TemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for design templates with marketplace features
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'tags']
    ordering_fields = ['created_at', 'use_count', 'name']
    ordering = ['-use_count', '-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'popular', 'featured', 'categories']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TemplateListSerializer
        return TemplateSerializer
    
    def get_queryset(self):
        queryset = Template.objects.select_related('created_by')
        
        # Public templates by default
        if not self.request.user.is_authenticated or self.action in ['list', 'retrieve']:
            queryset = queryset.filter(is_public=True)
        else:
            # Show user's own templates plus public ones
            queryset = queryset.filter(
                Q(is_public=True) | Q(created_by=self.request.user)
            )
        
        # Filters
        category = self.request.query_params.get('category')
        is_premium = self.request.query_params.get('premium')
        tags = self.request.query_params.getlist('tags')
        
        if category:
            queryset = queryset.filter(category=category)
        if is_premium is not None:
            queryset = queryset.filter(is_premium=is_premium.lower() == 'true')
        if tags:
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular templates"""
        limit = int(request.query_params.get('limit', 10))
        templates = Template.objects.filter(
            is_public=True
        ).order_by('-use_count')[:limit]
        
        serializer = TemplateListSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured templates (AI-generated or curated)"""
        limit = int(request.query_params.get('limit', 10))
        templates = Template.objects.filter(
            is_public=True,
            ai_generated=True
        ).order_by('-created_at')[:limit]
        
        serializer = TemplateListSerializer(templates, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all template categories with counts"""
        categories = Template.objects.filter(
            is_public=True
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response(categories)
    
    @action(detail=False, methods=['get'])
    def my_templates(self, request):
        """Get templates created by the current user"""
        templates = Template.objects.filter(
            created_by=request.user
        ).order_by('-created_at')
        
        serializer = self.get_serializer(templates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Create a new project from this template"""
        template = self.get_object()
        
        # Increment use count
        template.use_count += 1
        template.save(update_fields=['use_count'])
        
        # Create project from template
        project = Project.objects.create(
            user=request.user,
            name=request.data.get('name', f"{template.name} - Copy"),
            description=request.data.get('description', template.description),
            project_type=request.data.get('project_type', 'graphic'),
            canvas_width=template.width,
            canvas_height=template.height,
            design_data=template.design_data.copy() if template.design_data else {},
            color_palette=template.color_palette.copy() if template.color_palette else []
        )
        
        return Response({
            'status': 'success',
            'message': 'Project created from template',
            'project_id': project.id,
            'project_name': project.name
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def create_from_project(self, request):
        """Create a template from an existing project"""
        serializer = TemplateCreateFromProjectSerializer(data=request.data)
        
        if serializer.is_valid():
            project_id = serializer.validated_data['project_id']
            project = get_object_or_404(Project, id=project_id, user=request.user)
            
            # Create template from project
            template = Template.objects.create(
                name=serializer.validated_data.get('name', f"{project.name} Template"),
                description=serializer.validated_data.get('description', project.description),
                category=serializer.validated_data.get('category', 'social_media'),
                design_data=project.design_data.copy() if project.design_data else {},
                width=project.canvas_width,
                height=project.canvas_height,
                tags=serializer.validated_data.get('tags', []),
                color_palette=project.color_palette.copy() if project.color_palette else [],
                is_premium=serializer.validated_data.get('is_premium', False),
                is_public=serializer.validated_data.get('is_public', False),
                created_by=request.user
            )
            
            return Response(
                TemplateSerializer(template, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template"""
        template = self.get_object()
        
        # Create a copy
        new_template = Template.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            category=template.category,
            design_data=template.design_data.copy() if template.design_data else {},
            width=template.width,
            height=template.height,
            tags=template.tags.copy() if template.tags else [],
            color_palette=template.color_palette.copy() if template.color_palette else [],
            is_premium=False,
            is_public=False,
            created_by=request.user
        )
        
        return Response(
            TemplateSerializer(new_template, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class TemplateComponentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for reusable template components
    """
    serializer_class = TemplateComponentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'component_type']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = TemplateComponent.objects.filter(is_public=True)
        
        # Filter by component type
        component_type = self.request.query_params.get('type')
        if component_type:
            queryset = queryset.filter(component_type=component_type)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get all component types with counts"""
        types = TemplateComponent.objects.filter(
            is_public=True
        ).values('component_type').annotate(
            count=Count('id')
        ).order_by('component_type')
        
        return Response(types)

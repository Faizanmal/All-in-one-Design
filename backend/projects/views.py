from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import models
import json
from .models import Project, DesignComponent, ProjectVersion
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer, 
    DesignComponentSerializer, ProjectVersionSerializer
)
from .export_service import ExportService
from .search_service import SearchService


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing design projects.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can see their own projects and public projects
        user = self.request.user
        return Project.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(collaborators=user)
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def save_design(self, request, pk=None):
        """Save current design state"""
        project = self.get_object()
        design_data = request.data.get('design_data')
        
        if not design_data:
            return Response(
                {'error': 'design_data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.design_data = design_data
        project.save()
        
        return Response(ProjectSerializer(project).data)
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the project"""
        project = self.get_object()
        
        # Get latest version number
        latest_version = project.versions.first()
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        version = ProjectVersion.objects.create(
            project=project,
            version_number=next_version,
            design_data=project.design_data,
            created_by=request.user
        )
        
        return Response(ProjectVersionSerializer(version).data)
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a project"""
        project = self.get_object()
        versions = project.versions.all()
        serializer = ProjectVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """Restore a specific version"""
        project = self.get_object()
        version_number = request.data.get('version_number')
        
        if not version_number:
            return Response(
                {'error': 'version_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        version = get_object_or_404(
            ProjectVersion,
            project=project,
            version_number=version_number
        )
        
        project.design_data = version.design_data
        project.save()
        
        return Response(ProjectSerializer(project).data)
    
    @action(detail=True, methods=['post'])
    def add_collaborator(self, request, pk=None):
        """Add a collaborator to the project"""
        project = self.get_object()
        
        # Only owner can add collaborators
        if project.user != request.user:
            return Response(
                {'error': 'Only the project owner can add collaborators'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username = request.data.get('username')
        if not username:
            return Response(
                {'error': 'username is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.contrib.auth.models import User
        collaborator = get_object_or_404(User, username=username)
        project.collaborators.add(collaborator)
        
        return Response(ProjectSerializer(project).data)
    
    @action(detail=False, methods=['get'])
    def my_projects(self, request):
        """Get current user's projects"""
        projects = Project.objects.filter(user=request.user)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def export_svg(self, request, pk=None):
        """Export project as SVG"""
        project = self.get_object()
        
        try:
            svg_content = ExportService.export_to_svg(project.design_data)
            
            response = HttpResponse(svg_content, content_type='image/svg+xml')
            response['Content-Disposition'] = f'attachment; filename="{project.name}.svg"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export project as PDF"""
        project = self.get_object()
        
        try:
            pdf_bytes = ExportService.export_to_pdf(
                project.design_data,
                project.canvas_width,
                project.canvas_height
            )
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{project.name}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def export_figma(self, request, pk=None):
        """Export project as Figma JSON"""
        project = self.get_object()
        
        try:
            figma_json = ExportService.export_to_figma_json(project.design_data)
            
            response = HttpResponse(
                json.dumps(figma_json, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="{project.name}_figma.json"'
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search projects with full-text search"""
        query = request.query_params.get('q', '')
        filters = {
            'project_type': request.query_params.get('project_type'),
            'created_after': request.query_params.get('created_after'),
            'created_before': request.query_params.get('created_before'),
            'has_ai': request.query_params.get('has_ai') == 'true'
        }
        
        projects = SearchService.search_projects(query, request.user, filters)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def autocomplete(self, request):
        """Autocomplete project names"""
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        projects = SearchService.autocomplete_projects(query, request.user, limit)
        data = [{'id': p.id, 'name': p.name} for p in projects]
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def advanced_filter(self, request):
        """Advanced filtering with multiple criteria"""
        filters = request.data
        projects = SearchService.filter_projects_advanced(request.user, filters)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')
        suggestions = SearchService.get_search_suggestions(query)
        return Response({'suggestions': suggestions})
    
    @action(detail=False, methods=['get'])
    def popular_searches(self, request):
        """Get popular search terms"""
        popular = SearchService.get_popular_searches()
        return Response({'searches': popular})


class DesignComponentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing design components.
    """
    serializer_class = DesignComponentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            return DesignComponent.objects.filter(project_id=project_id)
        return DesignComponent.objects.none()
    
    def perform_create(self, serializer):
        # Verify user has access to the project
        project = serializer.validated_data['project']
        if project.user != self.request.user and self.request.user not in project.collaborators.all():
            raise PermissionError("You don't have permission to add components to this project")
        serializer.save()


class ExportTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing export templates
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from .models import ExportTemplate
        user = self.request.user
        # Users can see their own templates and public templates
        return ExportTemplate.objects.filter(
            models.Q(user=user) | models.Q(is_public=True)
        )
    
    def get_serializer_class(self):
        from .serializers import ExportTemplateSerializer
        return ExportTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Export a project using this template"""
        template = self.get_object()
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, id=project_id)
        
        # Check permission
        if project.user != request.user and request.user not in project.collaborators.all():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Create template data
            template_data = {
                'format': template.format,
                'quality': template.quality,
                'optimize': template.optimize,
                'include_metadata': template.include_metadata,
                'compression': template.compression,
                'dimensions': {
                    'width': template.width,
                    'height': template.height,
                    'scale': template.scale
                },
                'options': template.format_options
            }
            
            template_obj = ExportService.create_export_template(template.name, template_data)
            export_bytes = ExportService.export_with_template(project.design_data, template_obj)
            
            # Update use count
            template.use_count += 1
            template.save()
            
            # Determine content type
            content_types = {
                'svg': 'image/svg+xml',
                'pdf': 'application/pdf',
                'png': 'image/png',
                'figma': 'application/json'
            }
            content_type = content_types.get(template.format, 'application/octet-stream')
            
            response = HttpResponse(export_bytes, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{project.name}.{template.format}"'
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportJobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing export jobs
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from .models import ExportJob
        return ExportJob.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        from .serializers import ExportJobSerializer
        return ExportJobSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def batch_export(self, request):
        """Create a batch export job"""
        from .models import ExportJob
        from .tasks import process_batch_export
        
        project_ids = request.data.get('project_ids', [])
        format = request.data.get('format', 'svg')
        template_id = request.data.get('template_id')
        
        if not project_ids:
            return Response(
                {'error': 'project_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create export job
        export_job = ExportJob.objects.create(
            user=request.user,
            format=format,
            status='pending'
        )
        
        if template_id:
            from .models import ExportTemplate
            template = get_object_or_404(ExportTemplate, id=template_id)
            export_job.template = template
            export_job.save()
        
        # Add projects
        projects = Project.objects.filter(id__in=project_ids)
        
        # Check permissions
        for project in projects:
            if project.user != request.user and request.user not in project.collaborators.all():
                export_job.delete()
                return Response(
                    {'error': f'Permission denied for project: {project.name}'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        export_job.projects.set(projects)
        
        # Queue background task
        process_batch_export.delay(export_job.id)
        
        from .serializers import ExportJobSerializer
        return Response(
            ExportJobSerializer(export_job).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download export job result"""
        export_job = self.get_object()
        
        if export_job.status != 'completed':
            return Response(
                {'error': f'Export job is {export_job.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not export_job.output_file:
            return Response(
                {'error': 'Export file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(
            export_job.output_file.read(),
            content_type='application/zip'
        )
        response['Content-Disposition'] = f'attachment; filename="batch_export_{export_job.id}.zip"'
        return response
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get export job status"""
        export_job = self.get_object()
        from .serializers import ExportJobSerializer
        return Response(ExportJobSerializer(export_job).data)

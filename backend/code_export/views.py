from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema

from projects.models import Project
from .models import (
    ExportConfiguration, CodeExport, DesignSpec,
    ComponentLibrary, HandoffAnnotation
)
from .serializers import (
    ExportConfigurationSerializer, CodeExportSerializer, CodeExportCreateSerializer,
    DesignSpecSerializer, ComponentLibrarySerializer, HandoffAnnotationSerializer,
    GeneratedCodeSerializer, BulkExportSerializer
)
from .services import CodeExportService


class ExportConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing export configurations.
    """
    serializer_class = ExportConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExportConfiguration.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # If setting as default, unset other defaults
        if serializer.validated_data.get('is_default'):
            ExportConfiguration.objects.filter(
                user=self.request.user, is_default=True
            ).update(is_default=False)
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get or create default configuration"""
        config, created = ExportConfiguration.objects.get_or_create(
            user=request.user,
            is_default=True,
            defaults={
                'name': 'Default Configuration',
                'framework': 'react',
                'styling': 'tailwind',
                'typescript_enabled': True,
            }
        )
        return Response(ExportConfigurationSerializer(config).data)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set configuration as default"""
        config = self.get_object()
        ExportConfiguration.objects.filter(
            user=request.user, is_default=True
        ).update(is_default=False)
        config.is_default = True
        config.save()
        return Response({'status': 'default set'})


class CodeExportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing code exports.
    """
    serializer_class = CodeExportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CodeExport.objects.filter(user=self.request.user).select_related(
            'project', 'config'
        )
    
    @extend_schema(request=CodeExportCreateSerializer, responses=CodeExportSerializer)
    def create(self, request):
        """Create a new code export"""
        serializer = CodeExportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project = get_object_or_404(
            Project.objects.filter(user=request.user) | 
            Project.objects.filter(collaborators=request.user),
            id=serializer.validated_data['project_id']
        )
        
        config = None
        if serializer.validated_data.get('config_id'):
            config = get_object_or_404(
                ExportConfiguration,
                id=serializer.validated_data['config_id'],
                user=request.user
            )
        
        # Create export record
        export = CodeExport.objects.create(
            user=request.user,
            project=project,
            config=config,
            framework=serializer.validated_data.get('framework', 'react'),
            styling=serializer.validated_data.get('styling', 'tailwind'),
            status='processing'
        )
        
        try:
            # Generate code
            service = CodeExportService(project, {
                'framework': export.framework,
                'styling': export.styling,
                'typescript_enabled': serializer.validated_data.get('typescript_enabled', True),
            })
            
            result = service.generate_code()
            
            export.generated_code = result['files']
            export.file_count = result['file_count']
            export.total_lines = result['total_lines']
            export.export_size = result['total_size']
            export.status = 'completed'
            export.completed_at = timezone.now()
            export.save()
            
        except Exception as e:
            export.status = 'failed'
            export.error_message = str(e)
            export.save()
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response(CodeExportSerializer(export).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download exported code as ZIP"""
        export = self.get_object()
        
        if export.status != 'completed':
            return Response(
                {'error': 'Export not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CodeExportService(export.project, {})
        zip_content = service.create_zip(export.generated_code)
        
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{export.project.name}_export.zip"'
        return response
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Get code preview"""
        export = self.get_object()
        
        if export.status != 'completed':
            return Response(
                {'error': 'Export not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Return first few files as preview
        preview_files = dict(list(export.generated_code.items())[:5])
        
        return Response({
            'files': preview_files,
            'total_files': len(export.generated_code),
            'file_list': list(export.generated_code.keys())
        })


class GenerateCodeView(APIView):
    """
    Generate code directly without saving export record.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=CodeExportCreateSerializer,
        responses=GeneratedCodeSerializer
    )
    def post(self, request):
        serializer = CodeExportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project = get_object_or_404(
            Project.objects.filter(user=request.user) | 
            Project.objects.filter(collaborators=request.user),
            id=serializer.validated_data['project_id']
        )
        
        service = CodeExportService(project, {
            'framework': serializer.validated_data.get('framework', 'react'),
            'styling': serializer.validated_data.get('styling', 'tailwind'),
            'typescript_enabled': serializer.validated_data.get('typescript_enabled', True),
        })
        
        result = service.generate_code()
        
        return Response(GeneratedCodeSerializer(result).data)


class DesignSpecViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing design specifications.
    """
    serializer_class = DesignSpecSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DesignSpec.objects.select_related('project', 'component')
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.filter(
            project__user=self.request.user
        ) | queryset.filter(
            project__collaborators=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate design specs for a project"""
        project_id = request.data.get('project_id')
        project = get_object_or_404(
            Project.objects.filter(user=request.user) | 
            Project.objects.filter(collaborators=request.user),
            id=project_id
        )
        
        service = CodeExportService(project, {})
        specs = service.generate_design_specs()
        
        # Save specs
        created_specs = []
        for spec_data in specs:
            spec, created = DesignSpec.objects.update_or_create(
                project=project,
                component_id=spec_data['id'],
                defaults={
                    'name': spec_data['name'],
                    'dimensions': spec_data['dimensions'],
                    'colors': spec_data['colors'],
                    'typography': spec_data['typography'],
                    'spacing': spec_data['spacing'],
                    'effects': spec_data['effects'],
                    'computed_styles': {'css': spec_data['css']},
                }
            )
            created_specs.append(spec)
        
        return Response(DesignSpecSerializer(created_specs, many=True).data)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export all specs for a project"""
        project_id = request.query_params.get('project_id')
        project = get_object_or_404(
            Project.objects.filter(user=request.user) | 
            Project.objects.filter(collaborators=request.user),
            id=project_id
        )
        
        specs = DesignSpec.objects.filter(project=project)
        
        # Compile CSS
        css_output = []
        for spec in specs:
            if spec.computed_styles.get('css'):
                css_output.append(f"/* {spec.name} */\n{spec.computed_styles['css']}")
        
        # Extract design tokens
        tokens = {
            'colors': {},
            'typography': {},
            'spacing': {},
        }
        
        for spec in specs:
            for key, value in spec.colors.items():
                if value:
                    tokens['colors'][f"{spec.name}-{key}"] = value
            for key, value in spec.typography.items():
                if value:
                    tokens['typography'][f"{spec.name}-{key}"] = value
        
        return Response({
            'specs': DesignSpecSerializer(specs, many=True).data,
            'css': '\n\n'.join(css_output),
            'tokens': tokens
        })


class ComponentLibraryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing component libraries.
    """
    serializer_class = ComponentLibrarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ComponentLibrary.objects.filter(user=self.request.user)
        
        # Include team libraries
        user_teams = self.request.user.teams.all()
        if user_teams.exists():
            queryset = queryset | ComponentLibrary.objects.filter(team__in=user_teams)
        
        # Include public libraries
        queryset = queryset | ComponentLibrary.objects.filter(is_public=True)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_component(self, request, pk=None):
        """Add a component to the library"""
        library = self.get_object()
        
        component_data = request.data.get('component')
        if not component_data:
            return Response(
                {'error': 'Component data required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        components = library.components or []
        components.append(component_data)
        library.components = components
        library.save()
        
        return Response(ComponentLibrarySerializer(library).data)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """Export component library as package"""
        library = self.get_object()
        
        framework = request.data.get('framework', library.default_framework)
        styling = request.data.get('styling', library.default_styling)
        
        # service variable unused
        _ = CodeExportService(None, {
            'framework': framework,
            'styling': styling,
            'typescript_enabled': True,
        })
        
        # Generate package.json
        package_json = {
            'name': library.package_name or f"@design/{library.name.lower().replace(' ', '-')}",
            'version': library.version,
            'main': 'dist/index.js',
            'types': 'dist/index.d.ts',
            'peerDependencies': {
                'react': '^18.0.0',
                'react-dom': '^18.0.0',
            }
        }
        
        return Response({
            'package_json': package_json,
            'component_count': len(library.components or []),
        })


class HandoffAnnotationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing handoff annotations.
    """
    serializer_class = HandoffAnnotationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = HandoffAnnotation.objects.select_related('project', 'component', 'created_by')
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.filter(
            project__user=self.request.user
        ) | queryset.filter(
            project__collaborators=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an annotation"""
        annotation = self.get_object()
        annotation.resolved = True
        annotation.resolved_by = request.user
        annotation.resolved_at = timezone.now()
        annotation.save()
        return Response(HandoffAnnotationSerializer(annotation).data)
    
    @action(detail=True, methods=['post'])
    def unresolve(self, request, pk=None):
        """Unresolve an annotation"""
        annotation = self.get_object()
        annotation.resolved = False
        annotation.resolved_by = None
        annotation.resolved_at = None
        annotation.save()
        return Response(HandoffAnnotationSerializer(annotation).data)
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved annotations for a project"""
        project_id = request.query_params.get('project_id')
        annotations = self.get_queryset().filter(
            project_id=project_id,
            resolved=False
        )
        return Response(HandoffAnnotationSerializer(annotations, many=True).data)


class BulkExportView(APIView):
    """
    Bulk export multiple projects at once.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(request=BulkExportSerializer)
    def post(self, request):
        serializer = BulkExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project_ids = serializer.validated_data['project_ids']
        framework = serializer.validated_data.get('framework', 'react')
        styling = serializer.validated_data.get('styling', 'tailwind')
        
        projects = Project.objects.filter(
            id__in=project_ids
        ).filter(
            user=request.user
        ) | Project.objects.filter(
            id__in=project_ids
        ).filter(
            collaborators=request.user
        )
        
        results = []
        for project in projects:
            service = CodeExportService(project, {
                'framework': framework,
                'styling': styling,
                'typescript_enabled': True,
            })
            
            result = service.generate_code()
            results.append({
                'project_id': project.id,
                'project_name': project.name,
                'files': result['files'],
                'file_count': result['file_count'],
            })
        
        return Response({'exports': results})

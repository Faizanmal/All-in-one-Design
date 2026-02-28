"""
Developer Handoff Views
REST API endpoints for code export and design systems
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
import zipfile
import io

from .models import Project
from .developer_handoff_models import (
    CodeExport,
    DesignSystem,
    DesignSystemExport,
    ComponentSpec,
    HandoffAnnotation
)
from .developer_handoff_serializers import (
    CodeExportSerializer,
    DesignSystemSerializer,
    ComponentSpecSerializer,
    HandoffAnnotationSerializer
)
from .code_export_service import CodeExportService
from .design_system_service import DesignSystemService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_to_code(request, project_id):
    """
    Export a project to code
    
    Body:
        format: Export format (react, vue, html_css, tailwind, scss)
        options: Export options
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    export_format = request.data.get('format', 'react')
    options = request.data.get('options', {})
    options['component_name'] = options.get('component_name', project.name.replace(' ', ''))
    
    # Create export record
    code_export = CodeExport.objects.create(
        user=request.user,
        project=project,
        format=export_format,
        options=options,
        status='processing'
    )
    
    try:
        service = CodeExportService()
        
        # Generate code based on format
        if export_format == 'react':
            files = service.export_to_react(project.design_data, options)
        elif export_format == 'react_typescript':
            options['typescript'] = True
            files = service.export_to_react(project.design_data, options)
        elif export_format == 'vue':
            files = service.export_to_vue(project.design_data, options)
        elif export_format == 'html_css':
            files = service.export_to_html_css(project.design_data, options)
        elif export_format == 'tailwind':
            files = service.export_to_tailwind(project.design_data, options)
        elif export_format == 'scss':
            files = service.export_to_scss(project.design_data, options)
        elif export_format == 'styled_components':
            options['styled_components'] = True
            files = service.export_to_react(project.design_data, options)
        else:
            raise ValueError(f'Unsupported format: {export_format}')
        
        # Update export record
        code_export.output_files = files
        code_export.status = 'completed'
        code_export.completed_at = timezone.now()
        code_export.lines_of_code = sum(len(content.split('\n')) for content in files.values())
        code_export.components_generated = len(files)
        code_export.save()
        
        return Response({
            'export_id': code_export.id,
            'format': export_format,
            'files': files,
            'lines_of_code': code_export.lines_of_code
        })
        
    except Exception as e:
        code_export.status = 'failed'
        code_export.error_message = str(e)
        code_export.save()
        
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_code_export(request, export_id):
    """
    Download code export as a ZIP file
    """
    try:
        code_export = CodeExport.objects.get(
            id=export_id,
            user=request.user,
            status='completed'
        )
    except CodeExport.DoesNotExist:
        return Response(
            {'error': 'Export not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in code_export.output_files.items():
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{code_export.project.name}_{code_export.format}.zip"'
    
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_design_system(request, project_id=None):
    """
    Create a design system from a project or from scratch
    """
    name = request.data.get('name', 'Design System')
    description = request.data.get('description', '')
    
    service = DesignSystemService()
    
    if project_id:
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extract design system from project
        system_data = service.extract_design_system(project.design_data, name)
        
        design_system = DesignSystem.objects.create(
            user=request.user,
            name=name,
            description=description,
            colors=system_data['colors'],
            typography=system_data['typography'],
            spacing=system_data['spacing'],
            radii=system_data['radii'],
            shadows=system_data['shadows'],
            breakpoints=system_data['breakpoints']
        )
        design_system.source_projects.add(project)
    else:
        # Create empty design system
        design_system = DesignSystem.objects.create(
            user=request.user,
            name=name,
            description=description,
            colors=request.data.get('colors', {}),
            typography=request.data.get('typography', {}),
            spacing=request.data.get('spacing', {}),
            radii=request.data.get('radii', {}),
            shadows=request.data.get('shadows', {}),
            breakpoints=request.data.get('breakpoints', {})
        )
    
    serializer = DesignSystemSerializer(design_system)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_design_system(request, system_id):
    """
    Export design system to various formats
    
    Body:
        format: Export format (css_variables, scss_variables, tailwind_config, json_tokens, figma_tokens, style_dictionary)
    """
    try:
        design_system = DesignSystem.objects.get(id=system_id, user=request.user)
    except DesignSystem.DoesNotExist:
        return Response(
            {'error': 'Design system not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    export_format = request.data.get('format', 'css_variables')
    
    service = DesignSystemService()
    
    # Build design system data
    system_data = {
        'colors': design_system.colors,
        'typography': design_system.typography,
        'spacing': design_system.spacing,
        'radii': design_system.radii,
        'shadows': design_system.shadows,
        'breakpoints': design_system.breakpoints
    }
    
    # Export based on format
    if export_format == 'css_variables':
        content = service.export_to_css_variables(system_data)
        filename = 'design-tokens.css'
        content_type = 'text/css'
    elif export_format == 'scss_variables':
        content = service.export_to_scss_variables(system_data)
        filename = '_tokens.scss'
        content_type = 'text/x-scss'
    elif export_format == 'tailwind_config':
        content = service.export_to_tailwind_config(system_data)
        filename = 'tailwind.config.js'
        content_type = 'application/javascript'
    elif export_format == 'json_tokens':
        content = service.export_to_json_tokens(system_data)
        filename = 'tokens.json'
        content_type = 'application/json'
    elif export_format == 'figma_tokens':
        content = service.export_to_figma_tokens(system_data)
        filename = 'figma-tokens.json'
        content_type = 'application/json'
    elif export_format == 'style_dictionary':
        content = service.export_to_style_dictionary(system_data)
        filename = 'style-dictionary.json'
        content_type = 'application/json'
    else:
        return Response(
            {'error': f'Unsupported format: {export_format}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save export record
    DesignSystemExport.objects.create(
        design_system=design_system,
        format=export_format,
        output_content=content
    )
    
    return Response({
        'format': export_format,
        'filename': filename,
        'content': content,
        'content_type': content_type
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_component_specs(request, project_id):
    """
    Generate component specifications for a project
    """
    try:
        project = Project.objects.get(id=project_id, user=request.user)
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    elements = project.design_data.get('elements', [])
    specs = []
    
    def process_element(elem, parent_name=''):
        elem_id = elem.get('id', '')
        elem_type = elem.get('type', 'unknown')
        name = elem.get('name', f'{elem_type}_{elem_id}')
        
        if parent_name:
            full_name = f'{parent_name}/{name}'
        else:
            full_name = name
        
        # Generate CSS styles
        styles = generate_element_styles(elem)
        
        spec, created = ComponentSpec.objects.update_or_create(
            project=project,
            element_id=elem_id,
            defaults={
                'name': full_name,
                'description': f'{elem_type} component',
                'dimensions': {
                    'width': elem.get('size', {}).get('width', 100),
                    'height': elem.get('size', {}).get('height', 100),
                    'x': elem.get('position', {}).get('x', 0),
                    'y': elem.get('position', {}).get('y', 0),
                },
                'styles': styles,
                'responsive_variants': {},
                'states': {},
                'props': [],
                'assets': [],
                'code_snippets': generate_code_snippets(elem)
            }
        )
        
        specs.append(spec)
        
        # Process children
        for child in elem.get('children', []):
            process_element(child, full_name)
    
    for elem in elements:
        process_element(elem)
    
    serializer = ComponentSpecSerializer(specs, many=True)
    return Response({
        'project_id': project.id,
        'specs_count': len(specs),
        'specs': serializer.data
    })


def generate_element_styles(elem: dict) -> dict:
    """Generate CSS styles for an element"""
    styles = {
        'position': 'absolute',
        'left': f"{elem.get('position', {}).get('x', 0)}px",
        'top': f"{elem.get('position', {}).get('y', 0)}px",
        'width': f"{elem.get('size', {}).get('width', 100)}px",
        'height': f"{elem.get('size', {}).get('height', 100)}px",
    }
    
    fills = elem.get('fills', [])
    if fills:
        fill = fills[0]
        if elem.get('type') == 'text':
            styles['color'] = fill.get('color', '#000000')
        else:
            styles['backgroundColor'] = fill.get('color', '#FFFFFF')
    
    if elem.get('borderRadius'):
        styles['borderRadius'] = f"{elem['borderRadius']}px"
    
    if elem.get('opacity') and elem['opacity'] != 1:
        styles['opacity'] = elem['opacity']
    
    if elem.get('type') == 'text':
        text_style = elem.get('textStyle', {})
        styles['fontFamily'] = text_style.get('fontFamily', 'Inter')
        styles['fontSize'] = f"{text_style.get('fontSize', 16)}px"
        styles['fontWeight'] = text_style.get('fontWeight', 400)
    
    return styles


def generate_code_snippets(elem: dict) -> dict:
    """Generate code snippets for an element"""
    
    return {
        'react': generate_react_snippet(elem),
        'html': generate_html_snippet(elem),
        'css': generate_css_snippet(elem)
    }


def generate_react_snippet(elem: dict) -> str:
    """Generate React code snippet"""
    elem_type = elem.get('type', 'div')
    tag = 'div'
    if elem_type == 'text':
        tag = 'p'
    elif elem_type == 'button':
        tag = 'button'
    elif elem_type == 'image':
        tag = 'img'
    
    styles = generate_element_styles(elem)
    style_str = ', '.join([f"'{k}': '{v}'" for k, v in styles.items()])
    
    if elem_type == 'text':
        text = elem.get('text', '')
        return f"<{tag} style={{{{{style_str}}}}}>{text}</{tag}>"
    else:
        return f"<{tag} style={{{{{style_str}}}}} />"


def generate_html_snippet(elem: dict) -> str:
    """Generate HTML code snippet"""
    elem_type = elem.get('type', 'div')
    elem_id = elem.get('id', '')
    
    tag = 'div'
    if elem_type == 'text':
        tag = 'p'
    elif elem_type == 'button':
        tag = 'button'
    elif elem_type == 'image':
        tag = 'img'
    
    if elem_type == 'text':
        text = elem.get('text', '')
        return f'<{tag} id="{elem_id}" class="{elem_type}">{text}</{tag}>'
    else:
        return f'<{tag} id="{elem_id}" class="{elem_type}"></{tag}>'


def generate_css_snippet(elem: dict) -> str:
    """Generate CSS code snippet"""
    elem_id = elem.get('id', '')
    styles = generate_element_styles(elem)
    
    rules = [f"#{elem_id} {{"]
    for prop, value in styles.items():
        # Convert camelCase to kebab-case
        css_prop = ''.join([f'-{c.lower()}' if c.isupper() else c for c in prop]).lstrip('-')
        rules.append(f"  {css_prop}: {value};")
    rules.append("}")
    
    return '\n'.join(rules)


class DesignSystemViewSet(viewsets.ModelViewSet):
    """Manage design systems"""
    serializer_class = DesignSystemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = DesignSystem.objects.filter(user=self.request.user)
        
        # Include public design systems
        if self.request.query_params.get('include_public', 'false').lower() == 'true':
            from django.db.models import Q
            queryset = DesignSystem.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ComponentSpecViewSet(viewsets.ModelViewSet):
    """Manage component specifications"""
    serializer_class = ComponentSpecSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ComponentSpec.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class HandoffAnnotationViewSet(viewsets.ModelViewSet):
    """Manage handoff annotations"""
    serializer_class = HandoffAnnotationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = HandoffAnnotation.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        unresolved_only = self.request.query_params.get('unresolved', 'false').lower() == 'true'
        if unresolved_only:
            queryset = queryset.filter(is_resolved=False)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark annotation as resolved"""
        annotation = self.get_object()
        annotation.is_resolved = True
        annotation.resolved_by = request.user
        annotation.resolved_at = timezone.now()
        annotation.save()
        
        return Response({'status': 'resolved'})


class CodeExportViewSet(viewsets.ReadOnlyModelViewSet):
    """View code export history"""
    serializer_class = CodeExportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CodeExport.objects.filter(user=self.request.user)

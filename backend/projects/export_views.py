"""
Advanced export views for multiple formats and batch operations
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Project, ExportTemplate
from .export_service import ExportService
from .serializers import ExportTemplateSerializer
from analytics.models import UserActivity


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_project_pdf(request, project_id):
    """
    Export a project to PDF format with options
    
    POST /api/v1/projects/{id}/export/pdf/
    Body: {
        "quality": "high",
        "page_size": "A4",
        "orientation": "portrait",
        "compress": true,
        "include_metadata": true
    }
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    options = request.data
    quality = options.get('quality', 'high')
    
    try:
        # Export to PDF
        pdf_bytes = ExportService.export_to_pdf(
            project.design_data,
            project.canvas_width,
            project.canvas_height
        )
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='export_pdf',
            description=f"Exported project '{project.name}' to PDF",
            metadata={
                'project_id': project.id,
                'format': 'pdf',
                'quality': quality
            }
        )
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{project.name}.pdf"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_project_figma(request, project_id):
    """
    Export a project to Figma JSON format
    
    POST /api/v1/projects/{id}/export/figma/
    Body: {
        "include_constraints": true,
        "flatten_groups": false,
        "convert_effects": true
    }
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    try:
        # Export to Figma JSON
        figma_json = ExportService.export_to_figma_json(project.design_data)
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='export_figma',
            description=f"Exported project '{project.name}' to Figma JSON",
            metadata={
                'project_id': project.id,
                'format': 'figma_json'
            }
        )
        
        return Response({
            'success': True,
            'figma_json': figma_json,
            'project_name': project.name
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_project_svg_optimized(request, project_id):
    """
    Export a project to optimized SVG format
    
    POST /api/v1/projects/{id}/export/svg/optimized/
    Body: {
        "remove_ids": true,
        "round_coordinates": true,
        "decimal_places": 2,
        "minify": true
    }
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    try:
        # Export to SVG
        svg_content = ExportService.export_to_svg(project.design_data)
        
        # Optimize SVG
        optimized_svg = ExportService.optimize_svg(svg_content)
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='export_svg',
            description=f"Exported project '{project.name}' to optimized SVG",
            metadata={
                'project_id': project.id,
                'format': 'svg_optimized',
                'original_size': len(svg_content),
                'optimized_size': len(optimized_svg),
                'reduction': f"{(1 - len(optimized_svg)/len(svg_content)) * 100:.1f}%"
            }
        )
        
        response = HttpResponse(optimized_svg, content_type='image/svg+xml')
        response['Content-Disposition'] = f'attachment; filename="{project.name}.svg"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_export_projects(request):
    """
    Export multiple projects in a single ZIP file
    
    POST /api/v1/projects/export/batch/
    Body: {
        "project_ids": [1, 2, 3],
        "format": "svg",
        "optimize": true
    }
    """
    project_ids = request.data.get('project_ids', [])
    export_format = request.data.get('format', 'svg')
    
    if not project_ids:
        return Response(
            {'error': 'No project IDs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get projects owned by user
    projects = Project.objects.filter(
        id__in=project_ids,
        user=request.user
    )
    
    if not projects.exists():
        return Response(
            {'error': 'No valid projects found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        # Create ZIP with all exports
        zip_bytes = ExportService.export_batch(projects, format=export_format)
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='batch_export',
            description=f"Batch exported {projects.count()} projects as {export_format.upper()}",
            metadata={
                'project_ids': list(project_ids),
                'format': export_format,
                'count': projects.count()
            }
        )
        
        response = HttpResponse(zip_bytes, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="batch_export_{export_format}.zip"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_export_template(request):
    """
    Create a reusable export template
    
    POST /api/v1/projects/export/templates/
    Body: {
        "name": "High Quality PDF",
        "format": "pdf",
        "quality": "high",
        "options": {...}
    }
    """
    name = request.data.get('name')
    template_data = request.data
    
    if not name:
        return Response(
            {'error': 'Template name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create template using service
        template_config = ExportService.create_export_template(name, template_data)
        
        # Save to database
        export_template = ExportTemplate.objects.create(
            user=request.user,
            name=name,
            format=template_config['format'],
            settings=template_config
        )
        
        serializer = ExportTemplateSerializer(export_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_with_template(request, project_id, template_id):
    """
    Export project using a saved template
    
    POST /api/v1/projects/{id}/export/template/{template_id}/
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    template = get_object_or_404(ExportTemplate, id=template_id, user=request.user)
    
    try:
        # Export using template
        export_bytes = ExportService.export_with_template(
            project.design_data,
            template.settings
        )
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='template_export',
            description=f"Exported '{project.name}' using template '{template.name}'",
            metadata={
                'project_id': project.id,
                'template_id': template.id,
                'format': template.format
            }
        )
        
        # Determine content type and extension
        content_types = {
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'png': 'image/png',
            'figma': 'application/json'
        }
        
        content_type = content_types.get(template.format, 'application/octet-stream')
        ext = template.format if template.format != 'figma' else 'figma.json'
        
        response = HttpResponse(export_bytes, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{project.name}.{ext}"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_export_templates(request):
    """
    List all export templates for the user
    
    GET /api/v1/projects/export/templates/
    """
    templates = ExportTemplate.objects.filter(user=request.user)
    serializer = ExportTemplateSerializer(templates, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_export_template(request, template_id):
    """
    Delete an export template
    
    DELETE /api/v1/projects/export/templates/{id}/
    """
    template = get_object_or_404(ExportTemplate, id=template_id, user=request.user)
    template.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_social_media_pack(request, project_id):
    """
    Export project in multiple social media sizes in one ZIP
    
    POST /api/v1/projects/{id}/export/social-pack/
    Body: {
        "platforms": ["instagram", "facebook", "twitter", "linkedin"]
    }
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    platforms = request.data.get('platforms', ['instagram', 'facebook', 'twitter'])
    
    # Social media dimensions
    dimensions = {
        'instagram': {
            'post': (1080, 1080),
            'story': (1080, 1920),
            'profile': (320, 320)
        },
        'facebook': {
            'post': (1200, 630),
            'cover': (820, 312),
            'profile': (180, 180)
        },
        'twitter': {
            'post': (1200, 675),
            'header': (1500, 500),
            'profile': (400, 400)
        },
        'linkedin': {
            'post': (1200, 627),
            'cover': (1584, 396),
            'profile': (400, 400)
        }
    }
    
    import io
    import zipfile
    
    buffer = io.BytesIO()
    
    try:
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for platform in platforms:
                if platform in dimensions:
                    for size_type, (width, height) in dimensions[platform].items():
                        # Export at specific size
                        png_bytes = ExportService.export_to_png(
                            project.design_data,
                            width,
                            height
                        )
                        
                        filename = f"{platform}_{size_type}_{width}x{height}.png"
                        zip_file.writestr(filename, png_bytes)
        
        buffer.seek(0)
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='social_pack_export',
            description=f"Exported '{project.name}' as social media pack",
            metadata={
                'project_id': project.id,
                'platforms': platforms
            }
        )
        
        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{project.name}_social_pack.zip"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_print_ready(request, project_id):
    """
    Export project in print-ready format with bleed marks
    
    POST /api/v1/projects/{id}/export/print-ready/
    Body: {
        "format": "pdf",
        "size": "A4",
        "bleed": 3,  // mm
        "crop_marks": true,
        "color_mode": "CMYK"
    }
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
    options = request.data
    size = options.get('size', 'A4')
    bleed = options.get('bleed', 3)  # mm
    crop_marks = options.get('crop_marks', True)
    
    try:
        # For now, export as high-quality PDF
        # Future: Add actual bleed and crop marks
        pdf_bytes = ExportService.export_to_pdf(
            project.design_data,
            project.canvas_width,
            project.canvas_height
        )
        
        # Track export activity
        UserActivity.objects.create(
            user=request.user,
            action='print_ready_export',
            description=f"Exported '{project.name}' as print-ready PDF",
            metadata={
                'project_id': project.id,
                'size': size,
                'bleed': bleed,
                'crop_marks': crop_marks
            }
        )
        
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{project.name}_print_ready.pdf"'
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_formats_info(request):
    """
    Get information about available export formats and options
    
    GET /api/v1/projects/export/formats/
    """
    formats = {
        'svg': {
            'name': 'SVG (Scalable Vector Graphics)',
            'extensions': ['.svg'],
            'supports_optimization': True,
            'vector': True,
            'best_for': 'Web graphics, icons, logos',
            'options': {
                'optimize': 'Remove unnecessary data',
                'pretty_print': 'Human-readable formatting',
                'embed_fonts': 'Include font data'
            }
        },
        'pdf': {
            'name': 'PDF (Portable Document Format)',
            'extensions': ['.pdf'],
            'supports_optimization': True,
            'vector': True,
            'best_for': 'Print, documents, presentations',
            'options': {
                'page_size': 'A4, Letter, Custom',
                'compression': 'Reduce file size',
                'embed_images': 'Include images in PDF'
            }
        },
        'png': {
            'name': 'PNG (Portable Network Graphics)',
            'extensions': ['.png'],
            'supports_optimization': True,
            'vector': False,
            'best_for': 'Web images, screenshots',
            'options': {
                'quality': '1-100',
                'optimize': 'Reduce file size',
                'transparent': 'Support transparency'
            }
        },
        'figma': {
            'name': 'Figma JSON',
            'extensions': ['.figma.json'],
            'supports_optimization': False,
            'vector': True,
            'best_for': 'Import into Figma',
            'options': {
                'include_constraints': 'Auto-layout data',
                'convert_effects': 'Shadows, blurs'
            }
        }
    }
    
    return Response({
        'formats': formats,
        'batch_export': True,
        'template_export': True,
        'social_media_pack': True,
        'print_ready': True
    })

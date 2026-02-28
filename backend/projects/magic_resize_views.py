"""
Magic Resize API Views

Provides endpoints for one-click design resizing to multiple formats.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Project
from .magic_resize_service import MagicResizeService, FORMAT_PRESETS


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resize_presets(request):
    """
    List all available resize format presets.
    
    GET /api/v1/projects/resize/presets/
    Query params:
        category: Filter by category (social, ads, print, presentation, web)
    """
    service = MagicResizeService()
    category = request.query_params.get('category')
    presets = service.get_presets(category=category)
    categories = service.get_categories()
    return Response({
        'presets': presets,
        'categories': categories,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resize_project(request, project_id):
    """
    Resize a project's design to one or more target formats.
    
    POST /api/v1/projects/resize/<project_id>/
    Body:
        formats: list of format keys (e.g. ["instagram_post", "facebook_cover"])
        strategy: 'smart' (default), 'scale', 'center', 'fill'
        create_copies: bool (default True) — create new projects for each format
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Check access
    user = request.user
    if project.user != user and user not in project.collaborators.all():
        return Response(
            {'error': 'You do not have access to this project'},
            status=status.HTTP_403_FORBIDDEN,
        )

    formats = request.data.get('formats', [])
    strategy = request.data.get('strategy', 'smart')
    create_copies = request.data.get('create_copies', True)

    if not formats:
        return Response(
            {'error': 'At least one target format is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate formats
    invalid = [f for f in formats if f not in FORMAT_PRESETS]
    if invalid:
        return Response(
            {'error': f'Unknown formats: {", ".join(invalid)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = MagicResizeService()
    results = service.batch_resize(
        design_data=project.design_data or {},
        source_width=project.canvas_width,
        source_height=project.canvas_height,
        target_formats=formats,
        strategy=strategy,
    )

    created_projects = []
    if create_copies:
        for fmt_key, resized_data in results.items():
            if 'error' in resized_data:
                continue
            preset = FORMAT_PRESETS[fmt_key]
            new_project = Project.objects.create(
                user=user,
                name=f"{project.name} — {preset['name']}",
                description=f"Auto-resized from '{project.name}' to {preset['name']}",
                project_type=project.project_type,
                canvas_width=preset['width'],
                canvas_height=preset['height'],
                canvas_background=project.canvas_background,
                design_data=resized_data,
                ai_prompt=project.ai_prompt,
                color_palette=project.color_palette,
                suggested_fonts=project.suggested_fonts,
            )
            created_projects.append({
                'id': new_project.id,
                'name': new_project.name,
                'format': fmt_key,
                'width': preset['width'],
                'height': preset['height'],
            })

    return Response({
        'source_project': project.id,
        'strategy': strategy,
        'resized_formats': list(results.keys()),
        'created_projects': created_projects,
        'results': {k: v for k, v in results.items() if 'error' not in v} if not create_copies else {},
        'errors': {k: v['error'] for k, v in results.items() if 'error' in v},
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resize_preview(request):
    """
    Preview a resize without saving — returns the resized design data.
    
    POST /api/v1/projects/resize/preview/
    Body:
        design_data: dict
        source_width: int
        source_height: int
        target_format: str
        strategy: str (default 'smart')
    """
    design_data = request.data.get('design_data', {})
    source_width = request.data.get('source_width', 1920)
    source_height = request.data.get('source_height', 1080)
    target_format = request.data.get('target_format')
    strategy = request.data.get('strategy', 'smart')

    if not target_format:
        return Response(
            {'error': 'target_format is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = MagicResizeService()
    try:
        result = service.resize(design_data, source_width, source_height, target_format, strategy)
        preset = FORMAT_PRESETS.get(target_format, {})
        return Response({
            'design_data': result,
            'target_width': preset.get('width'),
            'target_height': preset.get('height'),
            'format': target_format,
            'strategy': strategy,
        })
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

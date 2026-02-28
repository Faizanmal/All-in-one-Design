"""
Background Remover API Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .background_remover import BackgroundRemoverService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def remove_background(request):
    """
    Remove background from an uploaded image.

    POST /api/v1/ai/background-remover/remove/
    Body (multipart/form-data):
        - image: Image file (required)
        - method: 'auto' | 'rembg' | 'remove_bg_api' | 'basic' (default: 'auto')
        - output_format: 'png' | 'jpg' | 'webp' (default: 'png')
        - refine_edges: true/false (default: true)
        - background_color: Hex color to replace background (optional)
    """
    image_file = request.FILES.get('image')
    if not image_file:
        return Response(
            {'error': 'No image file provided'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate file type
    ext = image_file.name.rsplit('.', 1)[-1].lower() if '.' in image_file.name else ''
    if ext not in BackgroundRemoverService.SUPPORTED_FORMATS:
        return Response(
            {'error': f'Unsupported format: {ext}. Supported: {", ".join(BackgroundRemoverService.SUPPORTED_FORMATS)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    method = request.data.get('method', 'auto')
    output_format = request.data.get('output_format', 'png')
    refine_edges = request.data.get('refine_edges', 'true').lower() in ('true', '1', 'yes')
    background_color = request.data.get('background_color')

    try:
        service = BackgroundRemoverService()
        result = service.remove_background(
            image_data=image_file.read(),
            method=method,
            output_format=output_format,
            refine_edges=refine_edges,
            background_color=background_color,
        )

        return Response({
            'success': True,
            'image_base64': result['image_base64'],
            'format': result['format'],
            'width': result['width'],
            'height': result['height'],
            'method_used': result['method_used'],
            'file_size': result['file_size'],
        })
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except RuntimeError as e:
        return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except Exception as e:
        return Response(
            {'error': 'Background removal failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def replace_background(request):
    """
    Remove background and replace with a new background image.

    POST /api/v1/ai/background-remover/replace/
    Body (multipart/form-data):
        - image: Foreground image file (required)
        - background: Background image file (required)
    """
    image_file = request.FILES.get('image')
    bg_file = request.FILES.get('background')

    if not image_file:
        return Response({'error': 'No foreground image provided'}, status=status.HTTP_400_BAD_REQUEST)
    if not bg_file:
        return Response({'error': 'No background image provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = BackgroundRemoverService()
        result = service.replace_background(
            image_data=image_file.read(),
            background_image_data=bg_file.read(),
        )

        return Response({
            'success': True,
            'image_base64': result['image_base64'],
            'format': result['format'],
            'width': result['width'],
            'height': result['height'],
            'method_used': result['method_used'],
            'file_size': result['file_size'],
        })
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'error': 'Background replacement failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def remover_info(request):
    """
    Get info about available background removal methods.

    GET /api/v1/ai/background-remover/info/
    """
    methods = [
        {
            'id': 'auto',
            'name': 'Auto (Recommended)',
            'description': 'Automatically selects the best available method',
        },
        {
            'id': 'basic',
            'name': 'Basic',
            'description': 'Color-based removal for simple/solid backgrounds. No dependencies required.',
        },
    ]

    # Check rembg availability
    try:
        import rembg
        methods.insert(1, {
            'id': 'rembg',
            'name': 'AI (Local)',
            'description': 'High-quality AI removal using U2-Net. Runs locally, no API costs.',
        })
    except ImportError:
        pass

    # Check Remove.bg API
    import os
    if os.environ.get('REMOVE_BG_API_KEY'):
        methods.insert(1, {
            'id': 'remove_bg_api',
            'name': 'Remove.bg API',
            'description': 'Professional-grade removal via Remove.bg cloud API.',
        })

    return Response({
        'methods': methods,
        'supported_formats': list(BackgroundRemoverService.SUPPORTED_FORMATS),
        'max_file_size_mb': BackgroundRemoverService.MAX_IMAGE_SIZE // (1024 * 1024),
        'max_dimension': BackgroundRemoverService.MAX_DIMENSION,
    })

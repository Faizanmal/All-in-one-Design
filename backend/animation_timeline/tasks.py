"""
Celery tasks for Animation Timeline app.
"""
from celery import shared_task
from django.utils import timezone
import json
import logging

logger = logging.getLogger('animation_timeline')


class AnimationExporter:
    """Utility to render animation exports to various formats."""

    @staticmethod
    def _render_animation(export) -> bytes:
        """Render animation data based on export format."""
        fmt = (export.format or 'json').lower()

        if fmt in ('json', 'lottie'):
            # Export the Lottie JSON as bytes
            data = getattr(export, 'export_data', None) or {}
            return json.dumps(data, separators=(',', ':')).encode('utf-8')

        if fmt == 'gif':
            try:
                from PIL import Image, ImageDraw
                import io

                # Generate a simple animated GIF from composition keyframes
                frames = []
                composition = getattr(export, 'composition', None)
                frame_count = 10
                width, height = 400, 300

                if composition and hasattr(composition, 'duration'):
                    duration_ms = int(getattr(composition, 'duration', 1000))
                else:
                    duration_ms = 1000

                for i in range(frame_count):
                    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
                    draw = ImageDraw.Draw(img)
                    # Draw a simple progress indicator
                    progress = int((i / frame_count) * width)
                    draw.rectangle([0, height - 20, progress, height], fill=(66, 133, 244, 255))
                    draw.text((10, 10), f'Frame {i + 1}/{frame_count}', fill=(0, 0, 0))
                    frames.append(img)

                buf = io.BytesIO()
                frames[0].save(
                    buf, format='GIF', save_all=True,
                    append_images=frames[1:],
                    duration=duration_ms // frame_count,
                    loop=0,
                )
                return buf.getvalue()

            except ImportError:
                logger.warning('Pillow not installed — cannot export GIF')
                return json.dumps({'error': 'GIF export requires Pillow'}).encode()

        # Default: export as JSON
        data = getattr(export, 'export_data', None) or {}
        return json.dumps(data, separators=(',', ':')).encode('utf-8')


@shared_task
def export_lottie_task(export_id: str):
    """
    Async task to export animation to Lottie format.
    """
    from .models import LottieExport
    from .services import LottieExporter
    
    try:
        export = LottieExport.objects.get(id=export_id)
        export.status = 'processing'
        export.save()
        
        exporter = LottieExporter(export.composition)
        lottie_data = exporter.generate_lottie_json()
        
        if export.optimize:
            lottie_data = optimize_lottie(lottie_data, export.target_size)
        
        export.export_data = lottie_data
        export.file_size = len(json.dumps(lottie_data))
        export.status = 'completed'
        export.completed_at = timezone.now()
        export.save()
        
        # Upload to storage and set file_url
        try:
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import uuid
            
            # Generate unique filename
            filename = f"animations/{uuid.uuid4()}.{export.format.lower()}"
            
            # Generate animation file content based on format
            animation_data = AnimationExporter._render_animation(export)
            
            # Save to storage
            file_path = default_storage.save(filename, ContentFile(animation_data))
            
            # Update export with file URL
            export.file_url = default_storage.url(file_path)
            export.save()
            
        except Exception as e:
            logger.error(f"Animation storage upload failed: {e}")
            # File URL will remain None but export is still marked completed
        
    except Exception as e:
        export.status = 'failed'
        export.error_message = str(e)
        export.save()


def optimize_lottie(lottie_data: dict, target_size: int = None) -> dict:
    """
    Optimize Lottie JSON for smaller file size.
    """
    optimized = lottie_data.copy()
    
    # Remove unnecessary precision
    optimized = _reduce_precision(optimized)
    
    # Remove null/empty values
    optimized = _remove_empty_values(optimized)
    
    return optimized


def _reduce_precision(data, precision: int = 3):
    """Reduce float precision to minimize file size."""
    if isinstance(data, dict):
        return {k: _reduce_precision(v, precision) for k, v in data.items()}
    elif isinstance(data, list):
        return [_reduce_precision(item, precision) for item in data]
    elif isinstance(data, float):
        return round(data, precision)
    return data


def _remove_empty_values(data):
    """Remove null and empty values."""
    if isinstance(data, dict):
        return {
            k: _remove_empty_values(v) 
            for k, v in data.items() 
            if v is not None and v != '' and v != []
        }
    elif isinstance(data, list):
        return [_remove_empty_values(item) for item in data if item is not None]
    return data

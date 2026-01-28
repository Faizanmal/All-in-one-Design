"""
Celery tasks for Animation Timeline app.
"""
from celery import shared_task
from django.utils import timezone
import json


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
        
        # TODO: Upload to storage and set file_url
        
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

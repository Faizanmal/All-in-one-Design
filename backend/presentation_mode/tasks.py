"""
Celery tasks for Presentation Mode app.
"""
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger('presentation_mode')


@shared_task
def export_asset_task(export_id: str):
    """
    Async task to export presentation assets.
    """
    from .models import AssetExportQueue

    try:
        export = AssetExportQueue.objects.get(id=export_id)
        export.status = 'processing'
        export.save()

        from .services import AssetExportService
        export_service = AssetExportService()
        result = export_service.export_presentation_assets(
            presentation_id=export.presentation_id,
            export_format=export.format,
            scale=export.scale or 1.0,
        )

        export.file_url = result.get('file_url', '')
        export.file_size = result.get('file_size', 0)
        export.status = 'completed'
        export.completed_at = timezone.now()
        export.save()

    except Exception as e:
        logger.exception('Presentation export failed for export_id=%s', export_id)
        try:
            export.status = 'failed'
            export.error_message = str(e)[:500]
            export.save()
        except Exception:
            pass

"""
Celery tasks for background export processing
"""
from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile
from .models import ExportJob, Project
from .export_service import ExportService
from notifications.signals import create_notification
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_batch_export(self, export_job_id):
    """
    Process batch export job in background
    
    Args:
        export_job_id: ExportJob ID
    """
    try:
        export_job = ExportJob.objects.get(id=export_job_id)
        export_job.status = 'processing'
        export_job.started_at = timezone.now()
        export_job.save()
        
        # Get projects to export
        projects = list(export_job.projects.all())
        export_job.total_projects = len(projects)
        export_job.save()
        
        # Get format
        format = export_job.format
        
        try:
            # Export batch
            zip_bytes = ExportService.export_batch(projects, format)
            
            # Save file
            filename = f"batch_export_{export_job.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
            export_job.output_file.save(filename, ContentFile(zip_bytes))
            export_job.file_size = len(zip_bytes)
            export_job.completed_projects = len(projects)
            export_job.status = 'completed'
            export_job.completed_at = timezone.now()
            export_job.save()
            
            # Send notification
            create_notification(
                user=export_job.user,
                notification_type='export_ready',
                title='Export Complete',
                message=f'Your batch export of {len(projects)} projects is ready to download.',
                metadata={
                    'export_job_id': export_job.id,
                    'file_size': export_job.file_size,
                    'format': format
                }
            )
            
            logger.info(f"Export job {export_job_id} completed successfully")
            
        except Exception as e:
            export_job.status = 'failed'
            export_job.error_message = str(e)
            export_job.completed_at = timezone.now()
            export_job.save()
            
            # Send error notification
            create_notification(
                user=export_job.user,
                notification_type='error',
                title='Export Failed',
                message=f'Export job failed: {str(e)}',
                metadata={'export_job_id': export_job.id}
            )
            
            logger.error(f"Export job {export_job_id} failed: {str(e)}")
            raise
            
    except ExportJob.DoesNotExist:
        logger.error(f"Export job {export_job_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error processing export job {export_job_id}: {str(e)}")
        self.retry(countdown=60, exc=e)


@shared_task
def process_single_export(project_id, format, template_id=None):
    """
    Export a single project
    
    Args:
        project_id: Project ID
        format: Export format
        template_id: Optional ExportTemplate ID
    """
    try:
        project = Project.objects.get(id=project_id)
        design_data = project.design_data
        
        if template_id:
            from .models import ExportTemplate
            template = ExportTemplate.objects.get(id=template_id)
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
            export_bytes = ExportService.export_with_template(design_data, template_obj)
            
            # Update template use count
            template.use_count += 1
            template.save()
        else:
            # Export without template
            if format == 'svg':
                content = ExportService.export_to_svg(design_data)
                export_bytes = content.encode('utf-8')
            elif format == 'pdf':
                export_bytes = ExportService.export_to_pdf(
                    design_data,
                    project.canvas_width,
                    project.canvas_height
                )
            elif format == 'png':
                export_bytes = ExportService.export_to_png(
                    design_data,
                    project.canvas_width,
                    project.canvas_height
                )
            elif format == 'figma':
                import json
                content = ExportService.export_to_figma_json(design_data)
                export_bytes = json.dumps(content, indent=2).encode('utf-8')
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        # Send notification
        create_notification(
            user=project.user,
            notification_type='export_ready',
            title='Export Complete',
            message=f'Your export of "{project.name}" is ready.',
            metadata={
                'project_id': project.id,
                'format': format,
                'size': len(export_bytes)
            }
        )
        
        logger.info(f"Project {project_id} exported successfully to {format}")
        return {'success': True, 'size': len(export_bytes)}
        
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return {'success': False, 'error': 'Project not found'}
    except Exception as e:
        logger.error(f"Error exporting project {project_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_old_exports():
    """
    Clean up old export files (older than 7 days)
    """
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=7)
    old_jobs = ExportJob.objects.filter(
        created_at__lt=cutoff_date,
        status='completed'
    )
    
    deleted_count = 0
    for job in old_jobs:
        if job.output_file:
            try:
                job.output_file.delete()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting file for job {job.id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted_count} old export files")
    return {'deleted': deleted_count}


@shared_task
def optimize_svg_file(project_id):
    """
    Optimize SVG export for a project
    
    Args:
        project_id: Project ID
    """
    try:
        project = Project.objects.get(id=project_id)
        design_data = project.design_data
        
        # Export to SVG
        svg_content = ExportService.export_to_svg(design_data)
        
        # Optimize
        optimized_svg = ExportService.optimize_svg(svg_content)
        
        # Calculate size reduction
        original_size = len(svg_content.encode('utf-8'))
        optimized_size = len(optimized_svg.encode('utf-8'))
        reduction = ((original_size - optimized_size) / original_size) * 100
        
        logger.info(f"Optimized SVG for project {project_id}, reduced by {reduction:.2f}%")
        
        return {
            'success': True,
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_percentage': reduction
        }
        
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return {'success': False, 'error': 'Project not found'}
    except Exception as e:
        logger.error(f"Error optimizing SVG for project {project_id}: {str(e)}")
        return {'success': False, 'error': str(e)}

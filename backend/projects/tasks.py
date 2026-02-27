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


@shared_task
def auto_save_version(project_id, user_id=None):
    """
    Create an automatic version snapshot for a project.
    Called periodically or on significant changes.
    
    Args:
        project_id: Project ID
        user_id: Optional user ID who triggered the save
    """
    from django.contrib.auth.models import User
    from .models import ProjectVersion
    
    try:
        project = Project.objects.get(id=project_id)
        
        if not project.design_data:
            return {'success': False, 'error': 'No design data to version'}
        
        # Check if latest version has same data (skip duplicate saves)
        latest_version = project.versions.first()
        if latest_version and latest_version.design_data == project.design_data:
            logger.info(f"Skipping auto-save for project {project_id} - no changes")
            return {'success': True, 'skipped': True, 'reason': 'no_changes'}
        
        next_version = (latest_version.version_number + 1) if latest_version else 1
        
        # Cap versions at 100, delete oldest beyond that
        version_count = project.versions.count()
        if version_count >= 100:
            oldest_versions = project.versions.order_by('version_number')[:version_count - 99]
            for v in oldest_versions:
                v.delete()
        
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        version = ProjectVersion.objects.create(
            project=project,
            version_number=next_version,
            design_data=project.design_data,
            created_by=user
        )
        
        logger.info(f"Auto-saved version {next_version} for project {project_id}")
        return {
            'success': True,
            'version_number': next_version,
            'project_id': project_id
        }
        
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found for auto-save")
        return {'success': False, 'error': 'Project not found'}
    except Exception as e:
        logger.error(f"Error auto-saving project {project_id}: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def cleanup_inactive_projects():
    """
    Clean up draft projects that haven't been updated in 90 days
    and have no design data. Sends warning notifications 7 days before.
    """
    from datetime import timedelta
    
    warning_cutoff = timezone.now() - timedelta(days=83)  # 7 days before deletion
    delete_cutoff = timezone.now() - timedelta(days=90)
    
    # Warn about projects approaching deletion
    warning_projects = Project.objects.filter(
        updated_at__lt=warning_cutoff,
        updated_at__gte=delete_cutoff,
        design_data={},
    )
    
    warned_count = 0
    for project in warning_projects:
        try:
            create_notification(
                user=project.user,
                notification_type='warning',
                title='Project Cleanup Warning',
                message=f'Your empty project "{project.name}" will be removed in 7 days. '
                        f'Open it to keep it.',
                metadata={'project_id': project.id}
            )
            warned_count += 1
        except Exception as e:
            logger.error(f"Error sending cleanup warning for project {project.id}: {str(e)}")
    
    # Delete truly inactive empty projects
    old_empty = Project.objects.filter(
        updated_at__lt=delete_cutoff,
        design_data={},
    )
    deleted_count = old_empty.count()
    old_empty.delete()
    
    logger.info(f"Cleanup: warned {warned_count}, deleted {deleted_count} empty projects")
    return {'warned': warned_count, 'deleted': deleted_count}


@shared_task
def generate_project_thumbnail(project_id):
    """
    Generate a thumbnail image for a project (for dashboard previews).
    
    Args:
        project_id: Project ID
    """
    try:
        project = Project.objects.get(id=project_id)
        
        if not project.design_data:
            return {'success': False, 'error': 'No design data'}
        
        # Generate a small PNG thumbnail
        thumbnail_bytes = ExportService.export_to_png(
            project.design_data,
            width=400,
            height=300
        )
        
        # Save thumbnail
        from django.core.files.base import ContentFile
        filename = f"thumbnails/project_{project.id}.png"
        
        # Store as project metadata
        project.design_data.setdefault('_meta', {})
        project.design_data['_meta']['thumbnail_size'] = len(thumbnail_bytes)
        project.design_data['_meta']['thumbnail_generated_at'] = timezone.now().isoformat()
        project.save(update_fields=['design_data'])
        
        logger.info(f"Generated thumbnail for project {project_id}")
        return {'success': True, 'size': len(thumbnail_bytes)}
        
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return {'success': False, 'error': 'Project not found'}
    except Exception as e:
        logger.error(f"Error generating thumbnail for project {project_id}: {str(e)}")
        return {'success': False, 'error': str(e)}

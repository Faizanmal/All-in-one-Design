"""
Export Presets & Automation Models and Service

Provides saveable export configurations, scheduled exports,
and bulk export capabilities with format presets.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import json
import zipfile
import io


class ExportPreset(models.Model):
    """
    Saved export configuration that can be reused.
    """
    FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('jpg', 'JPEG'),
        ('svg', 'SVG'),
        ('pdf', 'PDF'),
        ('webp', 'WebP'),
        ('gif', 'GIF'),
        ('ico', 'ICO'),
    ]
    
    SCALE_CHOICES = [
        ('0.5x', '0.5x'),
        ('1x', '1x'),
        ('1.5x', '1.5x'),
        ('2x', '2x'),
        ('3x', '3x'),
        ('4x', '4x'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_presets'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Export settings
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='png')
    scale = models.CharField(max_length=10, choices=SCALE_CHOICES, default='1x')
    quality = models.IntegerField(default=90)  # For JPG/WebP
    
    # Size constraints
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    maintain_aspect_ratio = models.BooleanField(default=True)
    
    # Additional options
    include_background = models.BooleanField(default=True)
    flatten_layers = models.BooleanField(default=False)
    optimize_for_web = models.BooleanField(default=True)
    
    # Naming convention
    file_naming_pattern = models.CharField(
        max_length=255,
        default='{name}_{scale}',
        help_text='Variables: {name}, {scale}, {format}, {date}, {time}, {index}'
    )
    
    # Output settings
    create_subfolder = models.BooleanField(default=False)
    subfolder_pattern = models.CharField(max_length=255, default='{format}_{scale}')
    
    # Metadata
    is_default = models.BooleanField(default=False)
    is_shared = models.BooleanField(default=False)  # Share with team
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.format} @ {self.scale})"
    
    def save(self, *args, **kwargs):
        # Ensure only one default preset per user
        if self.is_default:
            ExportPreset.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def to_config(self):
        """Convert preset to export configuration dict."""
        return {
            'format': self.format,
            'scale': self.scale,
            'quality': self.quality,
            'width': self.width,
            'height': self.height,
            'maintain_aspect_ratio': self.maintain_aspect_ratio,
            'include_background': self.include_background,
            'flatten_layers': self.flatten_layers,
            'optimize_for_web': self.optimize_for_web,
            'file_naming_pattern': self.file_naming_pattern,
        }


class ExportPresetBundle(models.Model):
    """
    A bundle of export presets for multi-format exports.
    E.g., "iOS Assets" bundle with 1x, 2x, 3x PNG exports.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_bundles'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    presets = models.ManyToManyField(ExportPreset, related_name='bundles')
    
    # Platform-specific bundles
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
        ('desktop', 'Desktop'),
        ('social', 'Social Media'),
        ('print', 'Print'),
        ('custom', 'Custom'),
    ]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='custom')
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.presets.count()} presets)"


class ScheduledExport(models.Model):
    """
    Scheduled/automated export configuration.
    """
    SCHEDULE_CHOICES = [
        ('once', 'One-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('on_change', 'On Change'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_exports'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='scheduled_exports'
    )
    
    name = models.CharField(max_length=255)
    preset = models.ForeignKey(
        ExportPreset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    bundle = models.ForeignKey(
        ExportPresetBundle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Schedule settings
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_CHOICES, default='once')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Timing
    next_run = models.DateTimeField(null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    run_count = models.IntegerField(default=0)
    
    # What to export
    export_all = models.BooleanField(default=True)
    component_ids = models.JSONField(default=list)  # Specific components if not export_all
    
    # Delivery method
    DELIVERY_CHOICES = [
        ('download', 'Download Link'),
        ('email', 'Email'),
        ('webhook', 'Webhook'),
        ('s3', 'S3 Bucket'),
        ('dropbox', 'Dropbox'),
        ('gdrive', 'Google Drive'),
    ]
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='download')
    delivery_config = models.JSONField(default=dict)  # Method-specific config
    
    # Error handling
    retry_on_failure = models.BooleanField(default=True)
    max_retries = models.IntegerField(default=3)
    retry_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.schedule_type})"
    
    def calculate_next_run(self):
        """Calculate next run time based on schedule type."""
        now = timezone.now()
        
        if self.schedule_type == 'once':
            return None  # No next run after one-time
        elif self.schedule_type == 'hourly':
            return now + timedelta(hours=1)
        elif self.schedule_type == 'daily':
            return now + timedelta(days=1)
        elif self.schedule_type == 'weekly':
            return now + timedelta(weeks=1)
        elif self.schedule_type == 'monthly':
            return now + timedelta(days=30)
        elif self.schedule_type == 'on_change':
            return None  # Triggered by changes
        
        return None


class ExportHistory(models.Model):
    """
    History of completed exports.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='export_history'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='export_history'
    )
    scheduled_export = models.ForeignKey(
        ScheduledExport,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='history'
    )
    
    preset = models.ForeignKey(
        ExportPreset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export details
    format = models.CharField(max_length=10)
    component_count = models.IntegerField(default=0)
    file_count = models.IntegerField(default=0)
    total_size = models.BigIntegerField(default=0)  # Bytes
    
    # File storage
    file_path = models.CharField(max_length=500, blank=True)
    download_url = models.URLField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    
    # Error info
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Export histories'
    
    def __str__(self):
        return f"Export {self.id} - {self.status}"


class ExportService:
    """
    Service for handling exports with presets and automation.
    """
    
    def __init__(self, project, user):
        self.project = project
        self.user = user
    
    def export_with_preset(self, preset, component_ids=None):
        """
        Export components using a preset configuration.
        """
        from projects.models import Component
        
        # Create history record
        history = ExportHistory.objects.create(
            user=self.user,
            project=self.project,
            preset=preset,
            status='processing',
            format=preset.format,
            started_at=timezone.now()
        )
        
        try:
            # Get components to export
            if component_ids:
                components = Component.objects.filter(
                    project=self.project,
                    id__in=component_ids
                )
            else:
                components = Component.objects.filter(project=self.project)
            
            history.component_count = components.count()
            
            # Apply preset configuration
            config = preset.to_config()
            
            # Export each component
            exported_files = []
            for index, component in enumerate(components):
                file_name = self._generate_filename(
                    preset.file_naming_pattern,
                    component.name,
                    preset.scale,
                    preset.format,
                    index
                )
                
                # Simulate export (actual implementation would render component)
                file_data = self._render_component(component, config)
                exported_files.append({
                    'name': file_name,
                    'data': file_data,
                    'component_id': component.id
                })
            
            # Create ZIP if multiple files
            if len(exported_files) > 1:
                output = self._create_zip(exported_files, preset)
                history.file_path = output['path']
            else:
                output = exported_files[0] if exported_files else {'size': 0}
            
            history.file_count = len(exported_files)
            history.total_size = output.get('size', 0)
            history.status = 'completed'
            history.completed_at = timezone.now()
            history.duration_ms = int(
                (history.completed_at - history.started_at).total_seconds() * 1000
            )
            history.save()
            
            return {
                'success': True,
                'history_id': history.id,
                'file_count': len(exported_files),
                'total_size': history.total_size,
            }
            
        except Exception as e:
            history.status = 'failed'
            history.error_message = str(e)
            history.completed_at = timezone.now()
            history.save()
            
            return {
                'success': False,
                'error': str(e),
                'history_id': history.id
            }
    
    def export_with_bundle(self, bundle, component_ids=None):
        """
        Export components using multiple presets from a bundle.
        """
        results = []
        
        for preset in bundle.presets.all():
            result = self.export_with_preset(preset, component_ids)
            results.append({
                'preset_name': preset.name,
                'result': result
            })
        
        return {
            'bundle_name': bundle.name,
            'preset_count': len(results),
            'results': results,
            'all_successful': all(r['result']['success'] for r in results)
        }
    
    def quick_export(self, format='png', scale='1x', component_ids=None):
        """
        Quick export without a preset.
        """
        # Create temporary preset
        config = {
            'format': format,
            'scale': scale,
            'quality': 90,
            'include_background': True,
            'optimize_for_web': True,
        }
        
        history = ExportHistory.objects.create(
            user=self.user,
            project=self.project,
            status='processing',
            format=format,
            started_at=timezone.now()
        )
        
        try:
            from projects.models import Component
            
            if component_ids:
                components = Component.objects.filter(
                    project=self.project,
                    id__in=component_ids
                )
            else:
                components = Component.objects.filter(project=self.project)
            
            history.component_count = components.count()
            
            exported_files = []
            for component in components:
                file_data = self._render_component(component, config)
                exported_files.append({
                    'name': f"{component.name}.{format}",
                    'data': file_data,
                    'component_id': component.id
                })
            
            history.file_count = len(exported_files)
            history.status = 'completed'
            history.completed_at = timezone.now()
            history.save()
            
            return {
                'success': True,
                'history_id': history.id,
                'files': exported_files
            }
            
        except Exception as e:
            history.status = 'failed'
            history.error_message = str(e)
            history.save()
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_scheduled_export(self, scheduled):
        """
        Execute a scheduled export.
        """
        try:
            if scheduled.bundle:
                result = self.export_with_bundle(
                    scheduled.bundle,
                    scheduled.component_ids if not scheduled.export_all else None
                )
            elif scheduled.preset:
                result = self.export_with_preset(
                    scheduled.preset,
                    scheduled.component_ids if not scheduled.export_all else None
                )
            else:
                result = self.quick_export()
            
            # Update scheduled export
            scheduled.last_run = timezone.now()
            scheduled.run_count += 1
            scheduled.next_run = scheduled.calculate_next_run()
            scheduled.retry_count = 0
            scheduled.last_error = ''
            
            if scheduled.schedule_type == 'once':
                scheduled.status = 'completed'
            
            scheduled.save()
            
            # Handle delivery
            if result.get('success'):
                self._deliver_export(scheduled, result)
            
            return result
            
        except Exception as e:
            scheduled.retry_count += 1
            scheduled.last_error = str(e)
            
            if scheduled.retry_count >= scheduled.max_retries:
                scheduled.status = 'error'
            
            scheduled.save()
            return {'success': False, 'error': str(e)}
    
    def _generate_filename(self, pattern, name, scale, format, index):
        """Generate filename from pattern."""
        now = timezone.now()
        return pattern.format(
            name=name,
            scale=scale,
            format=format,
            date=now.strftime('%Y-%m-%d'),
            time=now.strftime('%H-%M-%S'),
            index=index
        ) + f'.{format}'
    
    def _render_component(self, component, config):
        """
        Render a component to the specified format.
        Uses Pillow for raster formats, or SVG for vector output.
        Falls back to JSON data if rendering libraries are unavailable.
        """
        fmt = config.get('format', 'png').lower()

        # SVG export: serialize to basic SVG markup
        if fmt == 'svg':
            width = component.properties.get('width', 100)
            height = component.properties.get('height', 100)
            fill = component.properties.get('fill', '#CCCCCC')
            name = getattr(component, 'name', 'Component')
            svg = (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
                f'<rect width="{width}" height="{height}" fill="{fill}" />'
                f'<text x="10" y="20" font-size="14" fill="#333">{name}</text>'
                f'</svg>'
            )
            return svg.encode('utf-8')

        # Raster export via Pillow
        try:
            from PIL import Image, ImageDraw
            import io

            scale = config.get('scale', 1)
            if isinstance(scale, str):
                scale = float(scale.replace('x', ''))
            width = int(component.properties.get('width', 200) * scale)
            height = int(component.properties.get('height', 200) * scale)
            fill = component.properties.get('fill', '#CCCCCC')

            img = Image.new('RGBA', (width, height), fill)
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), getattr(component, 'name', ''), fill='#333333')

            buf = io.BytesIO()
            img_fmt = 'PNG' if fmt == 'png' else 'JPEG'
            img.save(buf, format=img_fmt)
            return buf.getvalue()

        except ImportError:
            # Pillow not available — fall back to JSON
            return json.dumps({
                'component_id': component.id,
                'name': component.name,
                'properties': component.properties,
                'config': config,
                'notice': 'Install Pillow for raster rendering',
            }).encode('utf-8')
    
    def _create_zip(self, files, preset):
        """Create a ZIP file from exported files."""
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_info in files:
                if preset.create_subfolder:
                    folder = preset.subfolder_pattern.format(
                        format=preset.format,
                        scale=preset.scale
                    )
                    path = f"{folder}/{file_info['name']}"
                else:
                    path = file_info['name']
                
                zf.writestr(path, file_info['data'])
        
        buffer.seek(0)
        return {
            'data': buffer.getvalue(),
            'size': buffer.getbuffer().nbytes,
            'path': f"exports/{self.project.id}/export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
        }
    
    def _deliver_export(self, scheduled, result):
        """Deliver export based on delivery method."""
        method = scheduled.delivery_method
        config = scheduled.delivery_config
        
        if method == 'email':
            self._send_email_delivery(config, result)
        elif method == 'webhook':
            self._send_webhook_delivery(config, result)
        elif method == 's3':
            self._upload_to_s3(config, result)
        # Add more delivery methods as needed
    
    def _send_email_delivery(self, config, result):
        """Send export via email using Django's email system."""
        from django.core.mail import EmailMessage

        recipient = config.get('email') or config.get('to')
        if not recipient:
            return

        subject = config.get('subject', 'Your design export is ready')
        body = config.get('body', 'Please find your exported design attached.')

        email = EmailMessage(
            subject=subject,
            body=body,
            to=[recipient],
        )

        # Attach the export file if data is available
        export_data = result.get('data')
        if export_data:
            filename = result.get('path', 'export.zip').rsplit('/', 1)[-1]
            email.attach(filename, export_data, 'application/octet-stream')

        email.send(fail_silently=False)
    
    def _send_webhook_delivery(self, config, result):
        """Send export notification to webhook."""
        import requests
        webhook_url = config.get('url')
        if webhook_url:
            requests.post(webhook_url, json={
                'event': 'export_complete',
                'result': result
            })
    
    def _upload_to_s3(self, config, result):
        """Upload export to S3."""
        try:
            import boto3
        except ImportError:
            raise NotImplementedError(
                'S3 upload requires boto3. Install with: pip install boto3'
            )

        bucket = config.get('bucket')
        key = config.get('key') or result.get('path', 'exports/export.zip')
        region = config.get('region', 'us-east-1')

        s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=config.get('access_key_id'),
            aws_secret_access_key=config.get('secret_access_key'),
        )

        export_data = result.get('data', b'')
        s3_client.put_object(Bucket=bucket, Key=key, Body=export_data)
        return {'bucket': bucket, 'key': key}
    
    @staticmethod
    def get_default_presets():
        """Return list of default preset configurations."""
        return [
            {
                'name': 'Web 1x',
                'format': 'png',
                'scale': '1x',
                'optimize_for_web': True,
            },
            {
                'name': 'Web 2x (Retina)',
                'format': 'png',
                'scale': '2x',
                'optimize_for_web': True,
            },
            {
                'name': 'SVG Vector',
                'format': 'svg',
                'scale': '1x',
            },
            {
                'name': 'Print PDF',
                'format': 'pdf',
                'scale': '1x',
                'quality': 100,
                'optimize_for_web': False,
            },
            {
                'name': 'WebP Optimized',
                'format': 'webp',
                'scale': '1x',
                'quality': 85,
                'optimize_for_web': True,
            },
        ]
    
    @staticmethod
    def get_platform_bundles():
        """Return platform-specific bundle configurations."""
        return {
            'ios': {
                'name': 'iOS Assets',
                'presets': [
                    {'format': 'png', 'scale': '1x', 'file_naming_pattern': '{name}'},
                    {'format': 'png', 'scale': '2x', 'file_naming_pattern': '{name}@2x'},
                    {'format': 'png', 'scale': '3x', 'file_naming_pattern': '{name}@3x'},
                ]
            },
            'android': {
                'name': 'Android Assets',
                'presets': [
                    {'format': 'png', 'scale': '1x', 'subfolder_pattern': 'drawable-mdpi'},
                    {'format': 'png', 'scale': '1.5x', 'subfolder_pattern': 'drawable-hdpi'},
                    {'format': 'png', 'scale': '2x', 'subfolder_pattern': 'drawable-xhdpi'},
                    {'format': 'png', 'scale': '3x', 'subfolder_pattern': 'drawable-xxhdpi'},
                    {'format': 'png', 'scale': '4x', 'subfolder_pattern': 'drawable-xxxhdpi'},
                ]
            },
            'web': {
                'name': 'Web Assets',
                'presets': [
                    {'format': 'png', 'scale': '1x'},
                    {'format': 'png', 'scale': '2x'},
                    {'format': 'webp', 'scale': '1x'},
                    {'format': 'svg', 'scale': '1x'},
                ]
            },
            'social': {
                'name': 'Social Media',
                'presets': [
                    {'format': 'png', 'width': 1200, 'height': 630, 'file_naming_pattern': '{name}_og'},
                    {'format': 'png', 'width': 1080, 'height': 1080, 'file_naming_pattern': '{name}_square'},
                    {'format': 'png', 'width': 1500, 'height': 500, 'file_naming_pattern': '{name}_twitter'},
                ]
            }
        }

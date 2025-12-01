"""
Export Presets API Views

REST API endpoints for export presets and automation.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from projects.models import Project
from .export_presets import (
    ExportPreset,
    ExportPresetBundle,
    ScheduledExport,
    ExportHistory,
    ExportService
)


class ExportPresetViewSet(viewsets.ViewSet):
    """
    ViewSet for managing export presets.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List user's export presets.
        
        GET /api/v1/projects/export-presets/
        """
        presets = ExportPreset.objects.filter(user=request.user)
        
        return Response({
            'presets': [
                {
                    'id': preset.id,
                    'name': preset.name,
                    'description': preset.description,
                    'format': preset.format,
                    'scale': preset.scale,
                    'quality': preset.quality,
                    'width': preset.width,
                    'height': preset.height,
                    'is_default': preset.is_default,
                    'include_background': preset.include_background,
                    'optimize_for_web': preset.optimize_for_web,
                    'file_naming_pattern': preset.file_naming_pattern,
                    'created_at': preset.created_at.isoformat(),
                }
                for preset in presets
            ],
            'default_presets': ExportService.get_default_presets()
        })
    
    def create(self, request):
        """
        Create a new export preset.
        
        POST /api/v1/projects/export-presets/
        """
        try:
            preset = ExportPreset.objects.create(
                user=request.user,
                name=request.data.get('name', 'Untitled Preset'),
                description=request.data.get('description', ''),
                format=request.data.get('format', 'png'),
                scale=request.data.get('scale', '1x'),
                quality=request.data.get('quality', 90),
                width=request.data.get('width'),
                height=request.data.get('height'),
                maintain_aspect_ratio=request.data.get('maintain_aspect_ratio', True),
                include_background=request.data.get('include_background', True),
                flatten_layers=request.data.get('flatten_layers', False),
                optimize_for_web=request.data.get('optimize_for_web', True),
                file_naming_pattern=request.data.get('file_naming_pattern', '{name}_{scale}'),
                is_default=request.data.get('is_default', False),
            )
            
            return Response({
                'id': preset.id,
                'name': preset.name,
                'format': preset.format,
                'scale': preset.scale,
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def retrieve(self, request, pk=None):
        """
        Get preset details.
        
        GET /api/v1/projects/export-presets/{id}/
        """
        preset = get_object_or_404(ExportPreset, pk=pk, user=request.user)
        
        return Response({
            'id': preset.id,
            'name': preset.name,
            'description': preset.description,
            'format': preset.format,
            'scale': preset.scale,
            'quality': preset.quality,
            'width': preset.width,
            'height': preset.height,
            'maintain_aspect_ratio': preset.maintain_aspect_ratio,
            'include_background': preset.include_background,
            'flatten_layers': preset.flatten_layers,
            'optimize_for_web': preset.optimize_for_web,
            'file_naming_pattern': preset.file_naming_pattern,
            'create_subfolder': preset.create_subfolder,
            'subfolder_pattern': preset.subfolder_pattern,
            'is_default': preset.is_default,
            'is_shared': preset.is_shared,
            'created_at': preset.created_at.isoformat(),
            'updated_at': preset.updated_at.isoformat(),
        })
    
    def update(self, request, pk=None):
        """
        Update a preset.
        
        PUT /api/v1/projects/export-presets/{id}/
        """
        preset = get_object_or_404(ExportPreset, pk=pk, user=request.user)
        
        for field in [
            'name', 'description', 'format', 'scale', 'quality',
            'width', 'height', 'maintain_aspect_ratio', 'include_background',
            'flatten_layers', 'optimize_for_web', 'file_naming_pattern',
            'create_subfolder', 'subfolder_pattern', 'is_default', 'is_shared'
        ]:
            if field in request.data:
                setattr(preset, field, request.data[field])
        
        preset.save()
        
        return Response({
            'id': preset.id,
            'name': preset.name,
            'updated_at': preset.updated_at.isoformat(),
        })
    
    def destroy(self, request, pk=None):
        """
        Delete a preset.
        
        DELETE /api/v1/projects/export-presets/{id}/
        """
        preset = get_object_or_404(ExportPreset, pk=pk, user=request.user)
        preset.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        Set as default preset.
        
        POST /api/v1/projects/export-presets/{id}/set_default/
        """
        preset = get_object_or_404(ExportPreset, pk=pk, user=request.user)
        preset.is_default = True
        preset.save()
        
        return Response({
            'success': True,
            'message': f'{preset.name} is now the default preset'
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a preset.
        
        POST /api/v1/projects/export-presets/{id}/duplicate/
        """
        preset = get_object_or_404(ExportPreset, pk=pk, user=request.user)
        
        new_preset = ExportPreset.objects.create(
            user=request.user,
            name=f"{preset.name} (Copy)",
            description=preset.description,
            format=preset.format,
            scale=preset.scale,
            quality=preset.quality,
            width=preset.width,
            height=preset.height,
            maintain_aspect_ratio=preset.maintain_aspect_ratio,
            include_background=preset.include_background,
            flatten_layers=preset.flatten_layers,
            optimize_for_web=preset.optimize_for_web,
            file_naming_pattern=preset.file_naming_pattern,
            create_subfolder=preset.create_subfolder,
            subfolder_pattern=preset.subfolder_pattern,
        )
        
        return Response({
            'id': new_preset.id,
            'name': new_preset.name,
        }, status=status.HTTP_201_CREATED)


class ExportBundleViewSet(viewsets.ViewSet):
    """
    ViewSet for managing export preset bundles.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List user's export bundles and platform bundles.
        
        GET /api/v1/projects/export-bundles/
        """
        bundles = ExportPresetBundle.objects.filter(user=request.user)
        
        return Response({
            'bundles': [
                {
                    'id': bundle.id,
                    'name': bundle.name,
                    'description': bundle.description,
                    'platform': bundle.platform,
                    'preset_count': bundle.presets.count(),
                    'is_default': bundle.is_default,
                }
                for bundle in bundles
            ],
            'platform_bundles': ExportService.get_platform_bundles()
        })
    
    def create(self, request):
        """
        Create a new export bundle.
        
        POST /api/v1/projects/export-bundles/
        """
        bundle = ExportPresetBundle.objects.create(
            user=request.user,
            name=request.data.get('name', 'Untitled Bundle'),
            description=request.data.get('description', ''),
            platform=request.data.get('platform', 'custom'),
        )
        
        preset_ids = request.data.get('preset_ids', [])
        if preset_ids:
            presets = ExportPreset.objects.filter(
                id__in=preset_ids,
                user=request.user
            )
            bundle.presets.set(presets)
        
        return Response({
            'id': bundle.id,
            'name': bundle.name,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_preset(self, request, pk=None):
        """
        Add preset to bundle.
        
        POST /api/v1/projects/export-bundles/{id}/add_preset/
        """
        bundle = get_object_or_404(ExportPresetBundle, pk=pk, user=request.user)
        preset_id = request.data.get('preset_id')
        preset = get_object_or_404(ExportPreset, pk=preset_id, user=request.user)
        
        bundle.presets.add(preset)
        
        return Response({
            'success': True,
            'preset_count': bundle.presets.count()
        })
    
    @action(detail=True, methods=['post'])
    def remove_preset(self, request, pk=None):
        """
        Remove preset from bundle.
        
        POST /api/v1/projects/export-bundles/{id}/remove_preset/
        """
        bundle = get_object_or_404(ExportPresetBundle, pk=pk, user=request.user)
        preset_id = request.data.get('preset_id')
        preset = get_object_or_404(ExportPreset, pk=preset_id, user=request.user)
        
        bundle.presets.remove(preset)
        
        return Response({
            'success': True,
            'preset_count': bundle.presets.count()
        })


class ScheduledExportViewSet(viewsets.ViewSet):
    """
    ViewSet for managing scheduled exports.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List scheduled exports.
        
        GET /api/v1/projects/scheduled-exports/
        """
        project_id = request.query_params.get('project_id')
        
        queryset = ScheduledExport.objects.filter(user=request.user)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return Response({
            'scheduled_exports': [
                {
                    'id': se.id,
                    'name': se.name,
                    'project_id': se.project_id,
                    'schedule_type': se.schedule_type,
                    'status': se.status,
                    'next_run': se.next_run.isoformat() if se.next_run else None,
                    'last_run': se.last_run.isoformat() if se.last_run else None,
                    'run_count': se.run_count,
                    'preset_name': se.preset.name if se.preset else None,
                    'bundle_name': se.bundle.name if se.bundle else None,
                }
                for se in queryset
            ]
        })
    
    def create(self, request):
        """
        Create a scheduled export.
        
        POST /api/v1/projects/scheduled-exports/
        """
        project_id = request.data.get('project_id')
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        
        preset_id = request.data.get('preset_id')
        bundle_id = request.data.get('bundle_id')
        
        scheduled = ScheduledExport.objects.create(
            user=request.user,
            project=project,
            name=request.data.get('name', 'Scheduled Export'),
            preset_id=preset_id,
            bundle_id=bundle_id,
            schedule_type=request.data.get('schedule_type', 'once'),
            export_all=request.data.get('export_all', True),
            component_ids=request.data.get('component_ids', []),
            delivery_method=request.data.get('delivery_method', 'download'),
            delivery_config=request.data.get('delivery_config', {}),
            next_run=request.data.get('next_run'),
        )
        
        return Response({
            'id': scheduled.id,
            'name': scheduled.name,
            'schedule_type': scheduled.schedule_type,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """
        Pause a scheduled export.
        
        POST /api/v1/projects/scheduled-exports/{id}/pause/
        """
        scheduled = get_object_or_404(ScheduledExport, pk=pk, user=request.user)
        scheduled.status = 'paused'
        scheduled.save()
        
        return Response({'status': 'paused'})
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """
        Resume a scheduled export.
        
        POST /api/v1/projects/scheduled-exports/{id}/resume/
        """
        scheduled = get_object_or_404(ScheduledExport, pk=pk, user=request.user)
        scheduled.status = 'active'
        scheduled.save()
        
        return Response({'status': 'active'})
    
    @action(detail=True, methods=['post'])
    def run_now(self, request, pk=None):
        """
        Run a scheduled export immediately.
        
        POST /api/v1/projects/scheduled-exports/{id}/run_now/
        """
        scheduled = get_object_or_404(ScheduledExport, pk=pk, user=request.user)
        
        service = ExportService(scheduled.project, request.user)
        result = service.run_scheduled_export(scheduled)
        
        return Response(result)


class ExportHistoryViewSet(viewsets.ViewSet):
    """
    ViewSet for viewing export history.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List export history.
        
        GET /api/v1/projects/export-history/
        """
        project_id = request.query_params.get('project_id')
        
        queryset = ExportHistory.objects.filter(user=request.user)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        history = queryset[:100]
        
        return Response({
            'history': [
                {
                    'id': h.id,
                    'project_id': h.project_id,
                    'status': h.status,
                    'format': h.format,
                    'component_count': h.component_count,
                    'file_count': h.file_count,
                    'total_size': h.total_size,
                    'duration_ms': h.duration_ms,
                    'download_url': h.download_url,
                    'created_at': h.created_at.isoformat(),
                }
                for h in history
            ]
        })
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Get download URL for an export.
        
        GET /api/v1/projects/export-history/{id}/download/
        """
        history = get_object_or_404(ExportHistory, pk=pk, user=request.user)
        
        if history.status != 'completed':
            return Response(
                {'error': 'Export not completed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'download_url': history.download_url,
            'file_path': history.file_path,
            'expires_at': history.expires_at.isoformat() if history.expires_at else None,
        })


class ExportViewSet(viewsets.ViewSet):
    """
    Main export ViewSet for direct exports.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def quick(self, request):
        """
        Quick export without a preset.
        
        POST /api/v1/projects/export/quick/
        {
            "project_id": 1,
            "format": "png",
            "scale": "2x",
            "component_ids": [1, 2, 3]
        }
        """
        project_id = request.data.get('project_id')
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        
        service = ExportService(project, request.user)
        result = service.quick_export(
            format=request.data.get('format', 'png'),
            scale=request.data.get('scale', '1x'),
            component_ids=request.data.get('component_ids')
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def with_preset(self, request):
        """
        Export using a preset.
        
        POST /api/v1/projects/export/with_preset/
        {
            "project_id": 1,
            "preset_id": 1,
            "component_ids": [1, 2, 3]
        }
        """
        project_id = request.data.get('project_id')
        preset_id = request.data.get('preset_id')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        preset = get_object_or_404(ExportPreset, pk=preset_id, user=request.user)
        
        service = ExportService(project, request.user)
        result = service.export_with_preset(
            preset,
            component_ids=request.data.get('component_ids')
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def with_bundle(self, request):
        """
        Export using a bundle (multiple formats).
        
        POST /api/v1/projects/export/with_bundle/
        {
            "project_id": 1,
            "bundle_id": 1,
            "component_ids": [1, 2, 3]
        }
        """
        project_id = request.data.get('project_id')
        bundle_id = request.data.get('bundle_id')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        bundle = get_object_or_404(ExportPresetBundle, pk=bundle_id, user=request.user)
        
        service = ExportService(project, request.user)
        result = service.export_with_bundle(
            bundle,
            component_ids=request.data.get('component_ids')
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def formats(self, request):
        """
        Get available export formats.
        
        GET /api/v1/projects/export/formats/
        """
        return Response({
            'formats': [
                {'value': 'png', 'label': 'PNG', 'supports_transparency': True},
                {'value': 'jpg', 'label': 'JPEG', 'supports_transparency': False},
                {'value': 'svg', 'label': 'SVG', 'supports_transparency': True, 'vector': True},
                {'value': 'pdf', 'label': 'PDF', 'supports_transparency': True, 'vector': True},
                {'value': 'webp', 'label': 'WebP', 'supports_transparency': True},
                {'value': 'gif', 'label': 'GIF', 'supports_transparency': True},
                {'value': 'ico', 'label': 'ICO', 'supports_transparency': True},
            ],
            'scales': ['0.5x', '1x', '1.5x', '2x', '3x', '4x'],
            'default_presets': ExportService.get_default_presets(),
            'platform_bundles': ExportService.get_platform_bundles(),
        })

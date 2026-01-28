from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from drf_spectacular.utils import extend_schema

from projects.models import Project
from .models import OfflineProject, SyncQueue, OfflineSettings, SyncLog, CachedAsset
from .serializers import (
    OfflineProjectSerializer, SyncQueueSerializer, SyncQueueCreateSerializer,
    OfflineSettingsSerializer, SyncLogSerializer, CachedAssetSerializer,
    SyncDataSerializer, BulkSyncSerializer, ConflictResolutionSerializer,
    OfflineStatusSerializer
)


class OfflineProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offline projects"""
    serializer_class = OfflineProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OfflineProject.objects.filter(user=self.request.user).select_related('project')
    
    def create(self, request):
        """Enable offline mode for a project"""
        project_id = request.data.get('project')
        project = get_object_or_404(
            Project.objects.filter(user=request.user) |
            Project.objects.filter(collaborators=request.user),
            id=project_id
        )
        
        offline_project, created = OfflineProject.objects.get_or_create(
            user=request.user,
            project=project,
            defaults={
                'cached_data': {
                    'name': project.name,
                    'description': project.description,
                    'design_data': project.design_data,
                    'canvas_width': project.canvas_width,
                    'canvas_height': project.canvas_height,
                    'canvas_background': project.canvas_background,
                },
                'is_enabled': True,
            }
        )
        
        return Response(
            OfflineProjectSerializer(offline_project).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync offline project with server"""
        offline_project = self.get_object()
        
        # Get latest project data
        project = offline_project.project
        
        # Update cached data
        offline_project.cached_data = {
            'name': project.name,
            'description': project.description,
            'design_data': project.design_data,
            'canvas_width': project.canvas_width,
            'canvas_height': project.canvas_height,
            'canvas_background': project.canvas_background,
            'updated_at': project.updated_at.isoformat(),
        }
        
        # Get component data
        components = list(project.components.values('id', 'component_type', 'properties', 'z_index'))
        offline_project.cached_data['components'] = components
        
        # Get asset URLs
        assets = list(project.assets.values('id', 'file_url', 'asset_type'))
        offline_project.cached_assets = [a['file_url'] for a in assets]
        
        offline_project.sync_version += 1
        offline_project.needs_sync = False
        offline_project.save()
        
        return Response(OfflineProjectSerializer(offline_project).data)
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable offline mode for a project"""
        offline_project = self.get_object()
        offline_project.is_enabled = False
        offline_project.save()
        return Response({'status': 'disabled'})
    
    @action(detail=False, methods=['get'])
    def download_bundle(self, request):
        """Get all offline data as a bundle"""
        offline_projects = self.get_queryset().filter(is_enabled=True)
        
        bundle = {
            'projects': [],
            'assets': [],
            'version': 1,
            'created_at': timezone.now().isoformat(),
        }
        
        for op in offline_projects:
            bundle['projects'].append({
                'id': op.project.id,
                'data': op.cached_data,
                'sync_version': op.sync_version,
            })
            bundle['assets'].extend(op.cached_assets)
        
        # Remove duplicates from assets
        bundle['assets'] = list(set(bundle['assets']))
        
        return Response(bundle)


class SyncQueueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sync queue"""
    serializer_class = SyncQueueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SyncQueue.objects.filter(user=self.request.user)
    
    @extend_schema(request=SyncQueueCreateSerializer)
    def create(self, request):
        """Add item to sync queue"""
        serializer = SyncQueueCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        queue_item = SyncQueue.objects.create(
            user=request.user,
            **serializer.validated_data
        )
        
        return Response(SyncQueueSerializer(queue_item).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    @extend_schema(request=BulkSyncSerializer)
    def bulk_add(self, request):
        """Add multiple items to sync queue"""
        serializer = BulkSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items = []
        for item_data in serializer.validated_data['items']:
            items.append(SyncQueue(user=request.user, **item_data))
        
        SyncQueue.objects.bulk_create(items)
        
        return Response({'created': len(items)})
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        """Process pending sync queue items"""
        pending_items = self.get_queryset().filter(status='pending').order_by('sequence', 'created_at')
        
        log = SyncLog.objects.create(user=request.user)
        
        synced = 0
        failed = 0
        conflicts = 0
        
        for item in pending_items:
            try:
                item.status = 'syncing'
                item.save()
                
                result = self._process_sync_item(item)
                
                if result['success']:
                    item.status = 'completed'
                    item.synced_at = timezone.now()
                    synced += 1
                elif result.get('conflict'):
                    item.status = 'conflict'
                    item.conflict_data = result.get('remote_data')
                    conflicts += 1
                else:
                    item.status = 'failed'
                    item.error_message = result.get('error', 'Unknown error')
                    item.retry_count += 1
                    failed += 1
                
                item.save()
                
            except Exception as e:
                item.status = 'failed'
                item.error_message = str(e)
                item.retry_count += 1
                item.save()
                failed += 1
        
        log.completed_at = timezone.now()
        log.items_synced = synced
        log.items_failed = failed
        log.conflicts_resolved = 0
        log.success = failed == 0 and conflicts == 0
        log.save()
        
        return Response(SyncLogSerializer(log).data)
    
    def _process_sync_item(self, item):
        """Process a single sync queue item"""
        from projects.models import Project, DesignComponent
        from assets.models import Asset
        
        try:
            if item.entity_type == 'project':
                if item.operation == 'update':
                    project = Project.objects.get(id=item.entity_id, user=item.user)
                    
                    # Check for conflicts
                    if project.updated_at.isoformat() > item.data.get('local_updated_at', ''):
                        return {
                            'success': False,
                            'conflict': True,
                            'remote_data': {
                                'design_data': project.design_data,
                                'updated_at': project.updated_at.isoformat(),
                            }
                        }
                    
                    # Apply update
                    for key, value in item.data.items():
                        if key not in ['local_updated_at'] and hasattr(project, key):
                            setattr(project, key, value)
                    project.save()
                    
                elif item.operation == 'create':
                    project = Project.objects.create(
                        user=item.user,
                        **item.data
                    )
                    
            elif item.entity_type == 'component':
                if item.operation == 'create':
                    project = Project.objects.get(id=item.data['project_id'], user=item.user)
                    DesignComponent.objects.create(
                        project=project,
                        component_type=item.data['component_type'],
                        properties=item.data['properties'],
                        z_index=item.data.get('z_index', 0),
                    )
                elif item.operation == 'update':
                    component = DesignComponent.objects.get(
                        id=item.entity_id,
                        project__user=item.user
                    )
                    component.properties = item.data.get('properties', component.properties)
                    component.z_index = item.data.get('z_index', component.z_index)
                    component.save()
                elif item.operation == 'delete':
                    DesignComponent.objects.filter(
                        id=item.entity_id,
                        project__user=item.user
                    ).delete()
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @action(detail=True, methods=['post'])
    @extend_schema(request=ConflictResolutionSerializer)
    def resolve_conflict(self, request, pk=None):
        """Resolve a sync conflict"""
        item = self.get_object()
        
        if item.status != 'conflict':
            return Response(
                {'error': 'Item is not in conflict'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution = request.data.get('resolution', 'remote')
        merged_data = request.data.get('merged_data')
        
        if resolution == 'local':
            # Keep local, retry sync with force
            item.data['force'] = True
            result = self._process_sync_item(item)
        elif resolution == 'remote':
            # Discard local changes
            item.status = 'completed'
            item.resolved_by = 'remote'
        elif resolution == 'merged' and merged_data:
            # Use merged data
            item.data = merged_data
            result = self._process_sync_item(item)
        
        item.conflict_data = None
        item.resolved_by = resolution
        item.save()
        
        return Response(SyncQueueSerializer(item).data)
    
    @action(detail=False, methods=['delete'])
    def clear_completed(self, request):
        """Clear completed sync items"""
        deleted, _ = self.get_queryset().filter(status='completed').delete()
        return Response({'deleted': deleted})


class OfflineSettingsViewSet(viewsets.ModelViewSet):
    """ViewSet for offline settings"""
    serializer_class = OfflineSettingsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OfflineSettings.objects.filter(user=self.request.user)
    
    def get_object(self):
        obj, created = OfflineSettings.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request):
        obj = self.get_object()
        return Response(OfflineSettingsSerializer(obj).data)
    
    def create(self, request):
        return self.update(request)
    
    def update(self, request, pk=None):
        obj = self.get_object()
        serializer = OfflineSettingsSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for sync logs"""
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SyncLog.objects.filter(user=self.request.user)


class CachedAssetViewSet(viewsets.ModelViewSet):
    """ViewSet for cached assets"""
    serializer_class = CachedAssetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CachedAsset.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Clean up expired or unused cached assets"""
        # Get settings
        settings, _ = OfflineSettings.objects.get_or_create(user=request.user)
        
        # Delete expired assets
        expired = self.get_queryset().filter(expires_at__lt=timezone.now())
        expired_count = expired.count()
        expired_size = expired.aggregate(total=Sum('file_size'))['total'] or 0
        expired.delete()
        
        # Check storage limit
        current_size = self.get_queryset().aggregate(total=Sum('file_size'))['total'] or 0
        
        cleaned_size = 0
        if current_size > settings.max_offline_storage:
            # Delete least recently accessed until under limit
            over_limit = current_size - settings.max_offline_storage
            assets_to_delete = self.get_queryset().order_by('last_accessed')
            
            for asset in assets_to_delete:
                if cleaned_size >= over_limit:
                    break
                cleaned_size += asset.file_size
                asset.delete()
        
        return Response({
            'expired_deleted': expired_count,
            'expired_size': expired_size,
            'cleaned_size': cleaned_size,
        })


class OfflineStatusView(APIView):
    """Get current offline status"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        pending_syncs = SyncQueue.objects.filter(user=user, status='pending').count()
        total_cache = CachedAsset.objects.filter(user=user).aggregate(
            total=Sum('file_size')
        )['total'] or 0
        projects_cached = OfflineProject.objects.filter(user=user, is_enabled=True).count()
        
        last_sync = SyncLog.objects.filter(user=user, success=True).first()
        
        return Response({
            'is_online': True,  # Server-side always online
            'pending_syncs': pending_syncs,
            'total_cache_size': total_cache,
            'projects_cached': projects_cached,
            'last_sync': last_sync.completed_at if last_sync else None,
        })


class PWAManifestView(APIView):
    """Generate PWA manifest"""
    permission_classes = []
    
    def get(self, request):
        manifest = {
            'name': 'AI Design Tool',
            'short_name': 'Design Tool',
            'description': 'Professional design tool with AI-powered features',
            'start_url': '/',
            'display': 'standalone',
            'background_color': '#ffffff',
            'theme_color': '#3B82F6',
            'orientation': 'any',
            'icons': [
                {
                    'src': '/icons/icon-72.png',
                    'sizes': '72x72',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-96.png',
                    'sizes': '96x96',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-128.png',
                    'sizes': '128x128',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-144.png',
                    'sizes': '144x144',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-152.png',
                    'sizes': '152x152',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-192.png',
                    'sizes': '192x192',
                    'type': 'image/png',
                    'purpose': 'any maskable'
                },
                {
                    'src': '/icons/icon-384.png',
                    'sizes': '384x384',
                    'type': 'image/png'
                },
                {
                    'src': '/icons/icon-512.png',
                    'sizes': '512x512',
                    'type': 'image/png'
                }
            ],
            'categories': ['design', 'graphics', 'productivity'],
            'screenshots': [
                {
                    'src': '/screenshots/desktop.png',
                    'sizes': '1920x1080',
                    'type': 'image/png',
                    'form_factor': 'wide'
                },
                {
                    'src': '/screenshots/mobile.png',
                    'sizes': '750x1334',
                    'type': 'image/png',
                    'form_factor': 'narrow'
                }
            ],
            'shortcuts': [
                {
                    'name': 'New Project',
                    'url': '/projects/new',
                    'icons': [{'src': '/icons/new-project.png', 'sizes': '96x96'}]
                },
                {
                    'name': 'Recent Projects',
                    'url': '/projects?filter=recent',
                    'icons': [{'src': '/icons/recent.png', 'sizes': '96x96'}]
                }
            ],
            'share_target': {
                'action': '/share',
                'method': 'POST',
                'enctype': 'multipart/form-data',
                'params': {
                    'title': 'name',
                    'text': 'description',
                    'files': [
                        {
                            'name': 'image',
                            'accept': ['image/*']
                        }
                    ]
                }
            }
        }
        
        return Response(manifest)

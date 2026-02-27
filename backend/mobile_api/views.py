"""
Views for Mobile API app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import (
    MobileDevice, MobileSession, OfflineCache, MobileAnnotation,
    MobileNotification, MobilePreference, MobileAppVersion
)
from .serializers import (
    MobileDeviceSerializer, MobileDeviceRegisterSerializer,
    MobileSessionSerializer, CreateSessionSerializer, RefreshSessionSerializer,
    OfflineCacheSerializer, CacheContentSerializer, MobileAnnotationSerializer, VoiceAnnotationSerializer,
    MobileNotificationSerializer, NotificationListSerializer, MarkReadSerializer,
    MobilePreferenceSerializer, UpdatePreferencesSerializer,
    MobileAppVersionSerializer, AppVersionCheckSerializer, BiometricAuthSerializer,
    ProjectSyncRequestSerializer, MobileViewEventSerializer
)


class MobileDeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mobile devices."""
    serializer_class = MobileDeviceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['platform', 'is_active', 'trusted']
    ordering = ['-last_active']
    
    def get_queryset(self):
        return MobileDevice.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new mobile device."""
        serializer = MobileDeviceRegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create or update device
        device, created = MobileDevice.objects.update_or_create(
            device_id=data['device_id'],
            defaults={
                'user': request.user,
                'device_name': data.get('device_name', ''),
                'platform': data['platform'],
                'os_version': data.get('os_version', ''),
                'app_version': data.get('app_version', ''),
                'push_token': data.get('push_token', ''),
                'screen_width': data.get('screen_width'),
                'screen_height': data.get('screen_height'),
                'screen_scale': data.get('screen_scale'),
                'supports_biometrics': data.get('supports_biometrics', False),
                'is_active': True,
                'last_ip': self._get_client_ip(request),
            }
        )
        
        return Response(
            MobileDeviceSerializer(device).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def update_push_token(self, request, pk=None):
        """Update push notification token."""
        device = self.get_object()
        token = request.data.get('push_token', '')
        
        device.push_token = token
        device.push_enabled = bool(token)
        device.save()
        
        return Response({'status': 'updated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a device."""
        device = self.get_object()
        device.is_active = False
        device.save()
        
        # Also invalidate sessions
        MobileSession.objects.filter(device=device).update(is_active=False)
        
        return Response({'status': 'deactivated'})
    
    @action(detail=True, methods=['post'])
    def trust(self, request, pk=None):
        """Mark device as trusted."""
        device = self.get_object()
        device.trusted = True
        device.save()
        return Response({'status': 'trusted'})
    
    @action(detail=True, methods=['post'])
    def setup_biometrics(self, request, pk=None):
        """Setup biometric authentication."""
        device = self.get_object()
        serializer = BiometricAuthSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device.biometrics_enabled = serializer.validated_data['enable']
        device.save()
        
        return Response({
            'biometrics_enabled': device.biometrics_enabled,
            'status': 'enabled' if device.biometrics_enabled else 'disabled'
        })
    
    def _get_client_ip(self, request) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


class MobileSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mobile sessions."""
    serializer_class = MobileSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['device', 'is_active']
    
    def get_queryset(self):
        return MobileSession.objects.filter(device__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_session(self, request):
        """Create a new mobile session."""
        serializer = CreateSessionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device_id = serializer.validated_data['device_id']
        duration = serializer.validated_data['session_duration_hours']
        
        try:
            device = MobileDevice.objects.get(device_id=device_id, user=request.user)
        except MobileDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Invalidate old sessions
        MobileSession.objects.filter(device=device).update(is_active=False)
        
        # Create new session
        session = MobileSession.objects.create(
            device=device,
            session_token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=duration),
            is_active=True,
        )
        
        return Response(
            MobileSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Refresh an existing session."""
        serializer = RefreshSessionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = MobileSession.objects.get(
                session_token=serializer.validated_data['session_token'],
                device__user=request.user,
                is_active=True
            )
        except MobileSession.DoesNotExist:
            return Response(
                {'error': 'Session not found or expired'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        session.expires_at = timezone.now() + timedelta(
            hours=serializer.validated_data['extend_hours']
        )
        session.save()
        
        return Response(MobileSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session."""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'status': 'ended'})
    
    @action(detail=True, methods=['post'])
    def update_activity(self, request, pk=None):
        """Update session activity."""
        session = self.get_object()
        
        session.current_project_id = request.data.get('project_id', session.current_project_id)
        session.current_view = request.data.get('view', session.current_view)
        session.save()
        
        return Response({'status': 'updated'})


class OfflineCacheViewSet(viewsets.ModelViewSet):
    """ViewSet for managing offline cache."""
    serializer_class = OfflineCacheSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'cache_type', 'is_stale']
    ordering = ['-priority', '-cached_at']
    
    def get_queryset(self):
        return OfflineCache.objects.filter(device__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def cache_content(self, request):
        """Add content to offline cache."""
        serializer = CacheContentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device_id = request.data.get('device_id')
        try:
            device = MobileDevice.objects.get(device_id=device_id, user=request.user)
        except MobileDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cache_entry, created = OfflineCache.objects.update_or_create(
            device=device,
            cache_type=serializer.validated_data['cache_type'],
            content_id=serializer.validated_data['content_id'],
            defaults={
                'priority': serializer.validated_data.get('priority', 0),
                'server_updated_at': timezone.now(),
                'is_stale': False,
            }
        )
        
        return Response(OfflineCacheSerializer(cache_entry).data)
    
    @action(detail=False, methods=['post'])
    def check_sync_status(self, request):
        """Check sync status for cached content."""
        device_id = request.data.get('device_id')
        content_ids = request.data.get('content_ids', [])
        
        try:
            device = MobileDevice.objects.get(device_id=device_id, user=request.user)
        except MobileDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        cache_entries = OfflineCache.objects.filter(
            device=device,
            content_id__in=content_ids
        )
        
        # Build sync status response
        status_list = []
        for entry in cache_entries:
            # In production, check actual server version
            server_version = entry.version  # Would query actual content version
            status_list.append({
                'content_id': entry.content_id,
                'cache_type': entry.cache_type,
                'local_version': entry.version,
                'server_version': server_version,
                'is_stale': entry.is_stale,
                'needs_update': entry.is_stale or entry.version < server_version,
            })
        
        return Response(status_list)
    
    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """Clear offline cache for a device."""
        device_id = request.data.get('device_id')
        cache_type = request.data.get('cache_type')
        
        try:
            device = MobileDevice.objects.get(device_id=device_id, user=request.user)
        except MobileDevice.DoesNotExist:
            return Response(
                {'error': 'Device not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = OfflineCache.objects.filter(device=device)
        if cache_type:
            queryset = queryset.filter(cache_type=cache_type)
        
        count, _ = queryset.delete()
        
        return Response({'cleared': count})


class MobileAnnotationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mobile annotations."""
    serializer_class = MobileAnnotationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'annotation_type', 'is_resolved', 'synced']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return MobileAnnotation.objects.filter(
            Q(user=user) |
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        device_id = self.request.data.get('device_id')
        device = None
        if device_id:
            device = MobileDevice.objects.filter(
                device_id=device_id,
                user=self.request.user
            ).first()
        
        serializer.save(user=self.request.user, device=device)
    
    @action(detail=False, methods=['post'])
    def create_voice_annotation(self, request):
        """Create a voice annotation."""
        serializer = VoiceAnnotationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device_id = request.data.get('device_id')
        device = None
        if device_id:
            device = MobileDevice.objects.filter(
                device_id=device_id,
                user=request.user
            ).first()
        
        annotation = MobileAnnotation.objects.create(
            project_id=serializer.validated_data['project_id'],
            user=request.user,
            device=device,
            annotation_type=MobileAnnotation.ANNOTATION_TYPE_VOICE,
            position_x=serializer.validated_data['position_x'],
            position_y=serializer.validated_data['position_y'],
            screen_id=serializer.validated_data.get('screen_id', ''),
            voice_recording=serializer.validated_data['voice_file'],
            voice_duration=serializer.validated_data['duration'],
        )
        
        return Response(
            MobileAnnotationSerializer(annotation).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an annotation."""
        annotation = self.get_object()
        annotation.is_resolved = True
        annotation.resolved_by = request.user
        annotation.save()
        return Response({'status': 'resolved'})
    
    @action(detail=False, methods=['post'])
    def batch_sync(self, request):
        """Sync multiple annotations at once."""
        annotations_data = request.data.get('annotations', [])
        
        device_id = request.data.get('device_id')
        device = None
        if device_id:
            device = MobileDevice.objects.filter(
                device_id=device_id,
                user=request.user
            ).first()
        
        created_annotations = []
        for data in annotations_data:
            annotation = MobileAnnotation.objects.create(
                project_id=data.get('project_id'),
                user=request.user,
                device=device,
                annotation_type=data.get('annotation_type', 'pin'),
                position_x=data.get('position_x', 0),
                position_y=data.get('position_y', 0),
                screen_id=data.get('screen_id', ''),
                comment=data.get('comment', ''),
                drawing_data=data.get('drawing_data'),
            )
            created_annotations.append(annotation)
        
        return Response(
            MobileAnnotationSerializer(created_annotations, many=True).data,
            status=status.HTTP_201_CREATED
        )


class MobileNotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mobile notifications."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['device', 'notification_type', 'read', 'sent']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationListSerializer
        return MobileNotificationSerializer
    
    def get_queryset(self):
        return MobileNotification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """Mark notifications as read."""
        serializer = MarkReadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset()
        
        if serializer.validated_data.get('mark_all'):
            queryset.filter(read=False).update(read=True, read_at=timezone.now())
        else:
            notification_ids = serializer.validated_data.get('notification_ids', [])
            queryset.filter(id__in=notification_ids).update(
                read=True,
                read_at=timezone.now()
            )
        
        return Response({'status': 'marked'})
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark single notification as read."""
        notification = self.get_object()
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'status': 'read'})


class MobilePreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing mobile preferences."""
    serializer_class = MobilePreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MobilePreference.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_preferences(self, request):
        """Get current user's preferences."""
        preferences, created = MobilePreference.objects.get_or_create(
            user=request.user
        )
        return Response(MobilePreferenceSerializer(preferences).data)
    
    @action(detail=False, methods=['post', 'patch'])
    def update_preferences(self, request):
        """Update user preferences."""
        serializer = UpdatePreferencesSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        preferences, created = MobilePreference.objects.get_or_create(
            user=request.user
        )
        
        for key, value in serializer.validated_data.items():
            if key == 'max_cache_size_mb':
                setattr(preferences, 'max_cache_size', value * 1024 * 1024)
            else:
                setattr(preferences, key, value)
        
        preferences.save()
        
        return Response(MobilePreferenceSerializer(preferences).data)


class MobileAppVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for mobile app versions."""
    serializer_class = MobileAppVersionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['platform', 'is_latest', 'is_deprecated']
    
    def get_queryset(self):
        return MobileAppVersion.objects.all()
    
    @action(detail=False, methods=['post'])
    def check_version(self, request):
        """Check if app version is up to date."""
        serializer = AppVersionCheckSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        platform = serializer.validated_data['platform']
        current_build = serializer.validated_data['build_number']
        
        # Get latest version
        try:
            latest = MobileAppVersion.objects.filter(
                platform=platform,
                is_latest=True
            ).first()
        except MobileAppVersion.DoesNotExist:
            return Response(
                {'error': 'No version info available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not latest:
            return Response(
                {'error': 'No version info available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check for required updates
        required_update = MobileAppVersion.objects.filter(
            platform=platform,
            is_required=True,
            build_number__gt=current_build
        ).exists()
        
        return Response({
            'current_version': serializer.validated_data['current_version'],
            'latest_version': latest.version,
            'is_latest': current_build >= latest.build_number,
            'update_required': required_update,
            'update_available': current_build < latest.build_number,
            'store_url': latest.store_url,
            'release_notes': latest.release_notes,
        })


class ProjectSyncView(APIView):
    """View for syncing projects to mobile."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Get projects that need syncing."""
        serializer = ProjectSyncRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Import here to avoid circular import
        from projects.models import Project
        
        queryset = Project.objects.filter(
            Q(owner=request.user) |
            Q(team__members=request.user)
        ).distinct()
        
        project_ids = serializer.validated_data.get('project_ids')
        if project_ids:
            queryset = queryset.filter(id__in=project_ids)
        
        last_sync = serializer.validated_data.get('last_sync')
        if last_sync:
            queryset = queryset.filter(updated_at__gt=last_sync)
        
        # Build response
        projects_data = []
        for project in queryset[:50]:  # Limit to 50
            projects_data.append({
                'project_id': str(project.id),
                'name': project.name,
                'version': 1,  # Would come from version tracking
                'updated_at': project.updated_at,
                'thumbnail_url': getattr(project, 'thumbnail_url', ''),
                'needs_download': True,
                'size_bytes': 0,  # Would calculate actual size
            })
        
        return Response(projects_data)


class MobileAnalyticsView(APIView):
    """View for tracking mobile analytics events."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Track a mobile view event."""
        serializer = MobileViewEventSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # In production, would save to analytics service
        event_data = {
            'user_id': str(request.user.id),
            'event_type': serializer.validated_data['event_type'],
            'project_id': str(serializer.validated_data.get('project_id', '')),
            'screen_id': serializer.validated_data.get('screen_id', ''),
            'duration': serializer.validated_data.get('duration_seconds'),
            'metadata': serializer.validated_data.get('metadata', {}),
            'timestamp': timezone.now().isoformat(),
        }
        
        # Would send to analytics backend
        return Response({'status': 'tracked', 'event': event_data})


"""
Enhanced Collaboration Views
REST API endpoints for video conferencing, guest access, and design reviews
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models import Q
import secrets

from .models import Project
from .enhanced_collaboration_models import (
    VideoConferenceRoom,
    VideoConferenceParticipant,
    GuestAccess,
    GuestAccessLog,
    DesignReviewSession,
    ReviewSessionParticipant,
    ReviewAnnotation,
    CollaborationPresence
)
from .enhanced_collaboration_serializers import (
    VideoConferenceRoomSerializer,
    VideoConferenceRoomCreateSerializer,
    VideoConferenceParticipantSerializer,
    GuestAccessSerializer,
    GuestAccessCreateSerializer,
    GuestAccessLogSerializer,
    DesignReviewSessionSerializer,
    DesignReviewSessionCreateSerializer,
    ReviewSessionParticipantSerializer,
    ReviewAnnotationSerializer,
    CollaborationPresenceSerializer,
    InviteReviewerSerializer
)


class VideoConferenceRoomViewSet(viewsets.ModelViewSet):
    """Video conference room management"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['scheduled_start', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VideoConferenceRoomCreateSerializer
        return VideoConferenceRoomSerializer
    
    def get_queryset(self):
        return VideoConferenceRoom.objects.filter(
            Q(host=self.request.user) |
            Q(participants__user=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        room = serializer.save(host=self.request.user)
        
        # Add host as participant
        VideoConferenceParticipant.objects.create(
            room=room,
            user=self.request.user,
            role='host',
            can_edit_canvas=True
        )
        
        # Invite other users
        invite_users = serializer.validated_data.get('invite_users', [])
        for user_id in invite_users:
            try:
                user = User.objects.get(id=user_id)
                VideoConferenceParticipant.objects.create(
                    room=room,
                    user=user,
                    role='participant'
                )
            except User.DoesNotExist:
                pass
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the conference"""
        room = self.get_object()
        
        if room.host != request.user:
            return Response(
                {'error': 'Only the host can start the conference'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        room.status = 'active'
        room.actual_start = timezone.now()
        room.save()
        
        return Response({'status': 'active', 'room_code': room.room_code})
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End the conference"""
        room = self.get_object()
        
        if room.host != request.user:
            return Response(
                {'error': 'Only the host can end the conference'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        room.status = 'ended'
        room.actual_end = timezone.now()
        room.save()
        
        # Mark all participants as inactive
        room.participants.filter(is_active=True).update(
            is_active=False,
            left_at=timezone.now()
        )
        
        return Response({'status': 'ended'})
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a conference room"""
        room = self.get_object()
        
        if room.status not in ['scheduled', 'active']:
            return Response(
                {'error': 'Conference is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        participant, created = VideoConferenceParticipant.objects.get_or_create(
            room=room,
            user=request.user,
            defaults={'role': 'participant'}
        )
        
        participant.is_active = True
        participant.joined_at = timezone.now()
        participant.save()
        
        return Response({
            'status': 'joined',
            'role': participant.role,
            'room_code': room.room_code
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a conference room"""
        room = self.get_object()
        
        try:
            participant = VideoConferenceParticipant.objects.get(
                room=room,
                user=request.user
            )
            participant.is_active = False
            participant.left_at = timezone.now()
            participant.save()
            
            return Response({'status': 'left'})
        except VideoConferenceParticipant.DoesNotExist:
            return Response(
                {'error': 'Not a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )


class GuestAccessViewSet(viewsets.ModelViewSet):
    """Guest access management"""
    serializer_class = GuestAccessSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return GuestAccess.objects.filter(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = GuestAccessCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Validate project/asset ownership
        project = None
        asset = None
        
        if data.get('project'):
            try:
                project = Project.objects.get(id=data['project'], user=request.user)
            except Project.DoesNotExist:
                return Response(
                    {'error': 'Project not found or not owned by you'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Calculate expiration
        expires_at = None
        if data.get('expires_in_hours'):
            expires_at = timezone.now() + timezone.timedelta(hours=data['expires_in_hours'])
        
        # Create guest access
        guest_access = GuestAccess.objects.create(
            project=project,
            asset=asset,
            created_by=request.user,
            guest_email=data.get('guest_email', ''),
            access_level=data['access_level'],
            password_protected=bool(data.get('password')),
            password_hash=make_password(data['password']) if data.get('password') else '',
            max_views=data.get('max_views'),
            expires_at=expires_at,
            allow_download=data.get('allow_download', False),
            allow_copy=data.get('allow_copy', False),
            watermark_enabled=data.get('watermark_enabled', False)
        )
        
        return Response(
            GuestAccessSerializer(guest_access, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke guest access"""
        guest_access = self.get_object()
        guest_access.is_active = False
        guest_access.save()
        return Response({'status': 'revoked'})
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get access logs"""
        guest_access = self.get_object()
        logs = guest_access.access_logs.all()[:100]
        serializer = GuestAccessLogSerializer(logs, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def guest_access_view(request, token):
    """
    Public endpoint for guest access
    GET: Verify and access shared content
    POST: Submit password if protected
    """
    try:
        guest_access = GuestAccess.objects.get(access_token=token)
    except GuestAccess.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired link'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if active
    if not guest_access.is_active:
        return Response(
            {'error': 'This link has been revoked'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check expiration
    if guest_access.is_expired:
        return Response(
            {'error': 'This link has expired'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check view limit
    if guest_access.is_view_limit_reached:
        return Response(
            {'error': 'View limit reached'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Handle password protection
    if guest_access.password_protected:
        if request.method == 'GET':
            return Response({'password_required': True})
        
        password = request.data.get('password', '')
        if not check_password(password, guest_access.password_hash):
            return Response(
                {'error': 'Invalid password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # Log access
    GuestAccessLog.objects.create(
        guest_access=guest_access,
        event_type='view',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', '')
    )
    
    # Update view count and last accessed
    guest_access.view_count += 1
    guest_access.last_accessed_at = timezone.now()
    guest_access.save()
    
    # Return content data
    response_data = {
        'access_level': guest_access.access_level,
        'allow_download': guest_access.allow_download,
        'allow_copy': guest_access.allow_copy,
        'watermark_enabled': guest_access.watermark_enabled
    }
    
    if guest_access.project:
        response_data['project'] = {
            'id': guest_access.project.id,
            'name': guest_access.project.name,
            'design_data': guest_access.project.design_data
        }
    
    if guest_access.asset:
        response_data['asset'] = {
            'id': guest_access.asset.id,
            'name': guest_access.asset.name,
            'file_url': guest_access.asset.file.url if guest_access.asset.file else None
        }
    
    return Response(response_data)


class DesignReviewSessionViewSet(viewsets.ModelViewSet):
    """Design review session management"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DesignReviewSessionCreateSerializer
        return DesignReviewSessionSerializer
    
    def get_queryset(self):
        return DesignReviewSession.objects.filter(
            Q(created_by=self.request.user) |
            Q(participants__user=self.request.user)
        ).distinct()
    
    def create(self, request, *args, **kwargs):
        serializer = DesignReviewSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Validate project ownership
        try:
            project = Project.objects.get(id=data['project'], user=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create review session
        session = DesignReviewSession.objects.create(
            project=project,
            created_by=request.user,
            title=data['title'],
            description=data.get('description', ''),
            version_number=data.get('version_number', ''),
            deadline=data.get('deadline'),
            require_all_approvals=data.get('require_all_approvals', False),
            allow_anonymous_feedback=data.get('allow_anonymous_feedback', False)
        )
        
        # Add reviewers
        for reviewer_data in data.get('reviewers', []):
            if reviewer_data.get('user_id'):
                try:
                    user = User.objects.get(id=reviewer_data['user_id'])
                    ReviewSessionParticipant.objects.create(
                        session=session,
                        user=user,
                        role=reviewer_data.get('role', 'reviewer')
                    )
                except User.DoesNotExist:
                    pass
            elif reviewer_data.get('email'):
                ReviewSessionParticipant.objects.create(
                    session=session,
                    guest_email=reviewer_data['email'],
                    guest_name=reviewer_data.get('name', ''),
                    role=reviewer_data.get('role', 'reviewer')
                )
        
        return Response(
            DesignReviewSessionSerializer(session).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def open(self, request, pk=None):
        """Open review session for feedback"""
        session = self.get_object()
        session.status = 'open'
        session.save()
        
        # Send notification emails to participants
        from notifications.email_service import send_review_session_invite_email
        
        for participant in session.participants.all():
            if participant.user:
                email = participant.user.email
            elif participant.guest_email:
                email = participant.guest_email
            else:
                continue
            
            send_review_session_invite_email.delay(session.id, email)
        
        return Response({'status': 'open'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close review session"""
        session = self.get_object()
        session.status = 'closed'
        session.closed_at = timezone.now()
        session.save()
        return Response({'status': 'closed'})
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite additional reviewers"""
        session = self.get_object()
        serializer = InviteReviewerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        participant = None
        if data.get('user_id'):
            try:
                user = User.objects.get(id=data['user_id'])
                participant, _ = ReviewSessionParticipant.objects.get_or_create(
                    session=session,
                    user=user,
                    defaults={'role': data.get('role', 'reviewer')}
                )
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif data.get('email'):
            participant, _ = ReviewSessionParticipant.objects.get_or_create(
                session=session,
                guest_email=data['email'],
                defaults={
                    'guest_name': data.get('name', ''),
                    'role': data.get('role', 'reviewer')
                }
            )
        
        return Response(ReviewSessionParticipantSerializer(participant).data)


class ReviewAnnotationViewSet(viewsets.ModelViewSet):
    """Review annotation management"""
    serializer_class = ReviewAnnotationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ReviewAnnotation.objects.filter(parent__isnull=True)
        session_id = self.request.query_params.get('session_id')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset
    
    def perform_create(self, serializer):
        # Get or create participant for current user
        session = serializer.validated_data['session']
        participant, _ = ReviewSessionParticipant.objects.get_or_create(
            session=session,
            user=self.request.user,
            defaults={'role': 'reviewer'}
        )
        serializer.save(participant=participant)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark annotation as resolved"""
        annotation = self.get_object()
        annotation.is_resolved = True
        annotation.resolved_by = request.user
        annotation.resolved_at = timezone.now()
        annotation.save()
        return Response({'status': 'resolved'})
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to an annotation"""
        parent = self.get_object()
        
        # Get participant
        participant, _ = ReviewSessionParticipant.objects.get_or_create(
            session=parent.session,
            user=request.user,
            defaults={'role': 'reviewer'}
        )
        
        reply = ReviewAnnotation.objects.create(
            session=parent.session,
            participant=participant,
            annotation_type='pin',
            position_data=parent.position_data,
            comment=request.data.get('comment', ''),
            parent=parent
        )
        
        return Response(ReviewAnnotationSerializer(reply).data)


class CollaborationPresenceViewSet(viewsets.ModelViewSet):
    """Collaboration presence management"""
    serializer_class = CollaborationPresenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CollaborationPresence.objects.filter(project__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def heartbeat(self, request):
        """Update presence heartbeat"""
        project_id = request.data.get('project_id')
        session_id = request.data.get('session_id')
        
        if not project_id or not session_id:
            return Response(
                {'error': 'project_id and session_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        presence, created = CollaborationPresence.objects.update_or_create(
            user=request.user,
            project_id=project_id,
            session_id=session_id,
            defaults={
                'cursor_x': request.data.get('cursor_x'),
                'cursor_y': request.data.get('cursor_y'),
                'selected_elements': request.data.get('selected_elements', []),
                'activity_status': request.data.get('activity_status', 'active'),
                'color': request.data.get('color', '')
            }
        )
        
        # Get other active users
        others = CollaborationPresence.objects.filter(
            project_id=project_id
        ).exclude(user=request.user)
        
        # Filter to online users (heartbeat within 30 seconds)
        cutoff = timezone.now() - timezone.timedelta(seconds=30)
        others = others.filter(last_heartbeat__gte=cutoff)
        
        return Response({
            'presence_id': presence.id,
            'collaborators': CollaborationPresenceSerializer(others, many=True).data
        })
    
    @action(detail=False, methods=['post'])
    def disconnect(self, request):
        """Remove presence on disconnect"""
        project_id = request.data.get('project_id')
        session_id = request.data.get('session_id')
        
        CollaborationPresence.objects.filter(
            user=request.user,
            project_id=project_id,
            session_id=session_id
        ).delete()
        
        return Response({'status': 'disconnected'})

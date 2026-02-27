"""
Views for Whiteboard app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

from .models import (
    Whiteboard, WhiteboardCollaborator, StickyNote, StickyNoteVote,
    WhiteboardShape, Connector, WhiteboardText, WhiteboardImage,
    WhiteboardGroup, WhiteboardSection, Timer, WhiteboardComment,
    WhiteboardEmoji, WhiteboardTemplate
)
from .serializers import (
    WhiteboardSerializer, WhiteboardListSerializer,
    WhiteboardCollaboratorSerializer, StickyNoteSerializer,
    StickyNoteVoteSerializer, WhiteboardShapeSerializer,
    ConnectorSerializer, WhiteboardTextSerializer,
    WhiteboardImageSerializer, WhiteboardGroupSerializer,
    WhiteboardSectionSerializer, TimerSerializer,
    WhiteboardCommentSerializer, WhiteboardEmojiSerializer,
    WhiteboardTemplateSerializer, CreateFromTemplateSerializer,
    InviteCollaboratorSerializer, UpdateCursorSerializer
)

User = get_user_model()


class WhiteboardViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboards."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'whiteboard_type', 'is_public', 'is_template']
    search_fields = ['name', 'description']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WhiteboardListSerializer
        return WhiteboardSerializer
    
    def get_queryset(self):
        user = self.request.user
        return Whiteboard.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user) |
            Q(collaborators__user=user) |
            Q(is_public=True)
        ).distinct().prefetch_related(
            'collaborators', 'sticky_notes', 'shapes'
        )
    
    def perform_create(self, serializer):
        share_link = str(uuid.uuid4())[:12]
        whiteboard = serializer.save(created_by=self.request.user, share_link=share_link)
        
        # Add creator as admin collaborator
        WhiteboardCollaborator.objects.create(
            whiteboard=whiteboard,
            user=self.request.user,
            role='admin',
            is_online=True,
        )
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join the whiteboard session."""
        whiteboard = self.get_object()
        
        collaborator, created = WhiteboardCollaborator.objects.get_or_create(
            whiteboard=whiteboard,
            user=request.user,
            defaults={
                'role': 'editor' if whiteboard.allow_anonymous_edit else 'viewer',
                'cursor_color': self._generate_cursor_color(),
            }
        )
        
        collaborator.is_online = True
        collaborator.last_active = timezone.now()
        collaborator.save()
        
        return Response(WhiteboardCollaboratorSerializer(collaborator).data)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave the whiteboard session."""
        whiteboard = self.get_object()
        
        WhiteboardCollaborator.objects.filter(
            whiteboard=whiteboard,
            user=request.user
        ).update(is_online=False, last_active=timezone.now())
        
        return Response({'status': 'left'})
    
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite a collaborator."""
        whiteboard = self.get_object()
        serializer = InviteCollaboratorSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        role = serializer.validated_data['role']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Send invitation email
            self._send_invitation_email(email, whiteboard, role)
            return Response({'status': 'invitation_sent', 'email': email})
        
        collaborator, created = WhiteboardCollaborator.objects.get_or_create(
            whiteboard=whiteboard,
            user=user,
            defaults={
                'role': role,
                'cursor_color': self._generate_cursor_color(),
            }
        )
        
        if not created:
            collaborator.role = role
            collaborator.save()
        
        return Response(WhiteboardCollaboratorSerializer(collaborator).data)
    
    @action(detail=True, methods=['post'])
    def update_cursor(self, request, pk=None):
        """Update cursor position."""
        whiteboard = self.get_object()
        serializer = UpdateCursorSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        WhiteboardCollaborator.objects.filter(
            whiteboard=whiteboard,
            user=request.user
        ).update(
            cursor_x=serializer.validated_data['x'],
            cursor_y=serializer.validated_data['y'],
            last_active=timezone.now(),
        )
        
        # Broadcast via WebSocket would happen here
        return Response({'status': 'updated'})
    
    @action(detail=True, methods=['get'])
    def collaborators(self, request, pk=None):
        """Get all collaborators."""
        whiteboard = self.get_object()
        collaborators = whiteboard.collaborators.all()
        return Response(WhiteboardCollaboratorSerializer(collaborators, many=True).data)
    
    @action(detail=True, methods=['get'])
    def elements(self, request, pk=None):
        """Get all whiteboard elements."""
        whiteboard = self.get_object()
        
        return Response({
            'sticky_notes': StickyNoteSerializer(whiteboard.sticky_notes.all(), many=True).data,
            'shapes': WhiteboardShapeSerializer(whiteboard.shapes.all(), many=True).data,
            'connectors': ConnectorSerializer(whiteboard.connectors.all(), many=True).data,
            'texts': WhiteboardTextSerializer(whiteboard.texts.all(), many=True).data,
            'images': WhiteboardImageSerializer(whiteboard.images.all(), many=True).data,
            'groups': WhiteboardGroupSerializer(whiteboard.groups.all(), many=True).data,
            'sections': WhiteboardSectionSerializer(whiteboard.sections.all(), many=True).data,
        })
    
    @action(detail=True, methods=['post'])
    def add_sticky_note(self, request, pk=None):
        """Add a sticky note."""
        whiteboard = self.get_object()
        serializer = StickyNoteSerializer(data={
            **request.data,
            'whiteboard': whiteboard.id
        })
        if serializer.is_valid():
            serializer.save(whiteboard=whiteboard, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_shape(self, request, pk=None):
        """Add a shape."""
        whiteboard = self.get_object()
        serializer = WhiteboardShapeSerializer(data={
            **request.data,
            'whiteboard': whiteboard.id
        })
        if serializer.is_valid():
            serializer.save(whiteboard=whiteboard, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_connector(self, request, pk=None):
        """Add a connector."""
        whiteboard = self.get_object()
        serializer = ConnectorSerializer(data={
            **request.data,
            'whiteboard': whiteboard.id
        })
        if serializer.is_valid():
            serializer.save(whiteboard=whiteboard, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start_timer(self, request, pk=None):
        """Start a timer."""
        whiteboard = self.get_object()
        duration = request.data.get('duration_seconds', 300)
        
        timer = Timer.objects.create(
            whiteboard=whiteboard,
            duration_seconds=duration,
            is_running=True,
            started_at=timezone.now(),
            started_by=request.user,
        )
        
        return Response(TimerSerializer(timer).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def save_as_template(self, request, pk=None):
        """Save whiteboard as template."""
        whiteboard = self.get_object()
        name = request.data.get('name', f"{whiteboard.name} Template")
        
        template_data = self._export_whiteboard_data(whiteboard)
        
        template = WhiteboardTemplate.objects.create(
            name=name,
            description=request.data.get('description', ''),
            category=request.data.get('category', 'custom'),
            template_data=template_data,
            created_by=request.user,
        )
        
        return Response(WhiteboardTemplateSerializer(template).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def create_from_template(self, request):
        """Create whiteboard from template."""
        serializer = CreateFromTemplateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template = WhiteboardTemplate.objects.get(id=serializer.validated_data['template_id'])
        
        whiteboard = Whiteboard.objects.create(
            project_id=request.data.get('project_id'),
            name=serializer.validated_data['name'],
            created_by=request.user,
            share_link=str(uuid.uuid4())[:12],
        )
        
        self._import_template_data(whiteboard, template.template_data, request.user)
        
        template.usage_count += 1
        template.save()
        
        return Response(WhiteboardSerializer(whiteboard).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the whiteboard."""
        whiteboard = self.get_object()
        
        new_whiteboard = Whiteboard.objects.create(
            project=whiteboard.project,
            name=f"{whiteboard.name} (copy)",
            description=whiteboard.description,
            whiteboard_type=whiteboard.whiteboard_type,
            background_color=whiteboard.background_color,
            background_pattern=whiteboard.background_pattern,
            grid_size=whiteboard.grid_size,
            created_by=request.user,
            share_link=str(uuid.uuid4())[:12],
        )
        
        # Duplicate elements
        template_data = self._export_whiteboard_data(whiteboard)
        self._import_template_data(new_whiteboard, template_data, request.user)
        
        return Response(WhiteboardSerializer(new_whiteboard).data, status=status.HTTP_201_CREATED)
    
    def _generate_cursor_color(self) -> str:
        """Generate a random cursor color."""
        import random
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        return random.choice(colors)
    
    def _export_whiteboard_data(self, whiteboard) -> dict:
        """Export whiteboard data for templates."""
        return {
            'sticky_notes': list(whiteboard.sticky_notes.values(
                'content', 'color', 'position_x', 'position_y', 'width', 'height'
            )),
            'shapes': list(whiteboard.shapes.values(
                'shape_type', 'position_x', 'position_y', 'width', 'height',
                'fill_color', 'stroke_color', 'stroke_width'
            )),
            'connectors': list(whiteboard.connectors.values(
                'start_node_id', 'end_node_id', 'connector_type', 'stroke_color'
            )),
            'texts': list(whiteboard.texts.values(
                'content', 'position_x', 'position_y', 'font_size', 'text_color'
            )),
            'sections': list(whiteboard.sections.values(
                'title', 'position_x', 'position_y', 'width', 'height', 'background_color'
            )),
        }
    
    def _import_template_data(self, whiteboard, data: dict, user):
        """Import template data into whiteboard."""
        for note_data in data.get('sticky_notes', []):
            StickyNote.objects.create(whiteboard=whiteboard, created_by=user, **note_data)
        
        for shape_data in data.get('shapes', []):
            WhiteboardShape.objects.create(whiteboard=whiteboard, created_by=user, **shape_data)
        
        for text_data in data.get('texts', []):
            WhiteboardText.objects.create(whiteboard=whiteboard, created_by=user, **text_data)
        
        for section_data in data.get('sections', []):
            WhiteboardSection.objects.create(whiteboard=whiteboard, created_by=user, **section_data)


class PublicWhiteboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing public whiteboards."""
    serializer_class = WhiteboardSerializer
    permission_classes = [AllowAny]
    lookup_field = 'share_link'
    
    def get_queryset(self):
        return Whiteboard.objects.filter(is_public=True)


class WhiteboardCollaboratorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard collaborators."""
    serializer_class = WhiteboardCollaboratorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'role', 'is_online']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardCollaborator.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(user=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change collaborator role."""
        collaborator = self.get_object()
        role = request.data.get('role')
        
        if role not in ['viewer', 'editor', 'admin']:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        
        collaborator.role = role
        collaborator.save()
        
        return Response(WhiteboardCollaboratorSerializer(collaborator).data)
    
    @action(detail=True, methods=['post'])
    def remove(self, request, pk=None):
        """Remove collaborator."""
        collaborator = self.get_object()
        collaborator.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StickyNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sticky notes."""
    serializer_class = StickyNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'color', 'is_locked', 'group', 'section']
    
    def get_queryset(self):
        user = self.request.user
        return StickyNote.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct().prefetch_related('votes')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a sticky note."""
        sticky_note = self.get_object()
        vote_type = request.data.get('vote_type', 'upvote')
        
        vote, created = StickyNoteVote.objects.update_or_create(
            sticky_note=sticky_note,
            user=request.user,
            defaults={'vote_type': vote_type}
        )
        
        return Response(StickyNoteVoteSerializer(vote).data)
    
    @action(detail=True, methods=['post'])
    def toggle_lock(self, request, pk=None):
        """Toggle lock state."""
        sticky_note = self.get_object()
        sticky_note.is_locked = not sticky_note.is_locked
        sticky_note.save()
        return Response({'is_locked': sticky_note.is_locked})


class WhiteboardShapeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard shapes."""
    serializer_class = WhiteboardShapeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'shape_type', 'is_locked', 'group', 'section']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardShape.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ConnectorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing connectors."""
    serializer_class = ConnectorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'connector_type', 'is_locked']
    
    def get_queryset(self):
        user = self.request.user
        return Connector.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WhiteboardTextViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard text."""
    serializer_class = WhiteboardTextSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_locked', 'group', 'section']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardText.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WhiteboardImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard images."""
    serializer_class = WhiteboardImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_locked', 'group', 'section']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardImage.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WhiteboardGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard groups."""
    serializer_class = WhiteboardGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_locked']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardGroup.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get group members."""
        group = self.get_object()
        return Response({
            'sticky_notes': StickyNoteSerializer(group.sticky_notes.all(), many=True).data,
            'shapes': WhiteboardShapeSerializer(group.shapes.all(), many=True).data,
            'texts': WhiteboardTextSerializer(group.texts.all(), many=True).data,
            'images': WhiteboardImageSerializer(group.images.all(), many=True).data,
        })


class WhiteboardSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard sections."""
    serializer_class = WhiteboardSectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['whiteboard', 'is_collapsed', 'is_locked']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardSection.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_collapse(self, request, pk=None):
        """Toggle section collapse state."""
        section = self.get_object()
        section.is_collapsed = not section.is_collapsed
        section.save()
        return Response({'is_collapsed': section.is_collapsed})


class TimerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing timers."""
    serializer_class = TimerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_running']
    
    def get_queryset(self):
        user = self.request.user
        return Timer.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause the timer."""
        timer = self.get_object()
        timer.is_running = False
        timer.paused_at = timezone.now()
        timer.save()
        return Response(TimerSerializer(timer).data)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume the timer."""
        timer = self.get_object()
        if timer.paused_at and timer.started_at:
            # Adjust start time to account for pause
            pause_duration = timer.paused_at - timer.started_at
            timer.started_at = timezone.now() - pause_duration
        timer.is_running = True
        timer.paused_at = None
        timer.save()
        return Response(TimerSerializer(timer).data)
    
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """Reset the timer."""
        timer = self.get_object()
        timer.is_running = False
        timer.started_at = None
        timer.paused_at = None
        timer.save()
        return Response(TimerSerializer(timer).data)


class WhiteboardCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard comments."""
    serializer_class = WhiteboardCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_resolved', 'attached_to_type']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardComment.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user),
            parent_comment__isnull=True  # Only top-level comments
        ).distinct().prefetch_related('replies')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve the comment."""
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save()
        return Response({'status': 'resolved'})
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Reply to a comment."""
        parent = self.get_object()
        serializer = WhiteboardCommentSerializer(data={
            'whiteboard': parent.whiteboard.id,
            'parent_comment': parent.id,
            'content': request.data.get('content', ''),
        })
        if serializer.is_valid():
            serializer.save(
                whiteboard=parent.whiteboard,
                parent_comment=parent,
                author=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WhiteboardEmojiViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard emojis."""
    serializer_class = WhiteboardEmojiSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['whiteboard', 'is_reaction', 'attached_to_type']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardEmoji.objects.filter(
            Q(whiteboard__project__owner=user) |
            Q(whiteboard__project__team__members=user) |
            Q(whiteboard__collaborators__user=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WhiteboardTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing whiteboard templates."""
    serializer_class = WhiteboardTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_system']
    search_fields = ['name', 'description']
    ordering = ['-usage_count', '-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return WhiteboardTemplate.objects.filter(
            Q(is_system=True) | Q(created_by=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def _send_invitation_email(self, email, whiteboard, role):
        """Send invitation email to user"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Invitation to collaborate on {whiteboard.title}"
            message = f"""
            You've been invited to collaborate on the whiteboard "{whiteboard.title}" with {role} permissions.
            
            Click here to join: {settings.FRONTEND_URL}/whiteboard/{whiteboard.id}/accept-invite
            
            Best regards,
            AI Design Tool Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send invitation email: {e}")

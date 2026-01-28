"""
Commenting Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import (
    CommentThread, Comment, Mention, Reaction,
    ReviewSession, Reviewer, CommentNotification, CommentTemplate
)
from .serializers import (
    CommentThreadSerializer, CommentThreadDetailSerializer,
    CommentSerializer, ReviewSessionSerializer, ReviewerSerializer,
    CommentNotificationSerializer, CommentTemplateSerializer,
    CreateCommentSerializer, ResolveThreadSerializer,
    AssignThreadSerializer, AddReactionSerializer, ReviewDecisionSerializer
)

User = get_user_model()


class CommentThreadViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CommentThread.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        frame_id = self.request.query_params.get('frame')
        if frame_id:
            queryset = queryset.filter(frame_id=frame_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CommentThreadDetailSerializer
        return CommentThreadSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a comment thread."""
        thread = self.get_object()
        serializer = ResolveThreadSerializer(data=request.data)
        
        if serializer.is_valid():
            thread.status = 'resolved'
            thread.resolved_by = request.user
            thread.resolved_at = timezone.now()
            thread.save()
            
            # Add resolution comment if provided
            if serializer.validated_data.get('resolution_comment'):
                Comment.objects.create(
                    thread=thread,
                    author=request.user,
                    content=serializer.validated_data['resolution_comment']
                )
            
            return Response(CommentThreadSerializer(thread).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a resolved thread."""
        thread = self.get_object()
        thread.status = 'open'
        thread.resolved_by = None
        thread.resolved_at = None
        thread.save()
        return Response(CommentThreadSerializer(thread).data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign thread to a user."""
        thread = self.get_object()
        serializer = AssignThreadSerializer(data=request.data)
        
        if serializer.is_valid():
            assignee_id = serializer.validated_data.get('assignee_id')
            if assignee_id:
                thread.assignee = get_object_or_404(User, pk=assignee_id)
                thread.status = 'in_progress'
            else:
                thread.assignee = None
            thread.save()
            return Response(CommentThreadSerializer(thread).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        queryset = Comment.objects.filter(thread__project__user=self.request.user)
        
        thread_id = self.request.query_params.get('thread')
        if thread_id:
            queryset = queryset.filter(thread_id=thread_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(is_edited=True, edited_at=timezone.now())
    
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add reaction to comment."""
        comment = self.get_object()
        serializer = AddReactionSerializer(data=request.data)
        
        if serializer.is_valid():
            emoji = serializer.validated_data['emoji']
            
            # Toggle reaction
            existing = Reaction.objects.filter(
                comment=comment,
                user=request.user,
                emoji=emoji
            ).first()
            
            if existing:
                existing.delete()
                return Response({'removed': True})
            else:
                Reaction.objects.create(
                    comment=comment,
                    user=request.user,
                    emoji=emoji
                )
                return Response({'added': True})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateCommentView(APIView):
    """Create a comment (and optionally a thread)."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = CreateCommentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get or create thread
        if data.get('thread_id'):
            thread = get_object_or_404(CommentThread, pk=data['thread_id'])
        else:
            thread = CommentThread.objects.create(
                project_id=data['project_id'],
                frame_id=data.get('frame_id', ''),
                element_id=data.get('element_id', ''),
                x=data.get('x', 0),
                y=data.get('y', 0),
                created_by=request.user
            )
        
        # Create comment
        comment = Comment.objects.create(
            thread=thread,
            parent_id=data.get('parent_id'),
            author=request.user,
            comment_type=data.get('comment_type', 'text'),
            content=data.get('content', ''),
            annotation_data=data.get('annotation_data', {}),
            is_internal=data.get('is_internal', False)
        )
        
        # Handle mentions
        mentions = data.get('mentions', [])
        for mention_str in mentions:
            try:
                if mention_str.isdigit():
                    user = User.objects.get(pk=int(mention_str))
                else:
                    user = User.objects.get(username=mention_str)
                
                Mention.objects.create(
                    comment=comment,
                    user=user
                )
            except User.DoesNotExist:
                pass
        
        return Response({
            'thread': CommentThreadSerializer(thread).data,
            'comment': CommentSerializer(comment).data
        }, status=status.HTTP_201_CREATED)


class ReviewSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ReviewSession.objects.filter(project__user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_reviewers(self, request, pk=None):
        """Add reviewers to session."""
        session = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        added = []
        for user_id in user_ids:
            try:
                user = User.objects.get(pk=user_id)
                reviewer, created = Reviewer.objects.get_or_create(
                    session=session,
                    user=user
                )
                if created:
                    added.append(ReviewerSerializer(reviewer).data)
            except User.DoesNotExist:
                pass
        
        return Response({'added': added})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start the review session."""
        session = self.get_object()
        session.status = 'in_review'
        session.started_at = timezone.now()
        session.save()
        return Response(ReviewSessionSerializer(session).data)
    
    @action(detail=True, methods=['post'])
    def submit_decision(self, request, pk=None):
        """Submit reviewer decision."""
        session = self.get_object()
        serializer = ReviewDecisionSerializer(data=request.data)
        
        if serializer.is_valid():
            reviewer = get_object_or_404(
                Reviewer,
                session=session,
                user=request.user
            )
            
            reviewer.decision = serializer.validated_data['decision']
            reviewer.feedback = serializer.validated_data.get('feedback', '')
            reviewer.decided_at = timezone.now()
            reviewer.save()
            
            # Check if review is complete
            all_decided = not session.reviewers.filter(decision='pending').exists()
            if all_decided:
                approved_count = session.reviewers.filter(decision='approved').count()
                
                if session.require_all_approvals:
                    if approved_count == session.reviewers.count():
                        session.status = 'approved'
                    else:
                        session.status = 'changes_requested'
                else:
                    if approved_count >= session.approval_count_needed:
                        session.status = 'approved'
                    else:
                        session.status = 'changes_requested'
                
                session.completed_at = timezone.now()
                session.save()
            
            return Response(ReviewSessionSerializer(session).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CommentNotification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'success': True})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(read=False).update(
            read=True,
            read_at=timezone.now()
        )
        return Response({'success': True})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count."""
        count = self.get_queryset().filter(read=False).count()
        return Response({'count': count})


class CommentTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = CommentTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CommentTemplate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

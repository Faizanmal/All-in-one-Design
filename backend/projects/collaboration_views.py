"""
Views for collaboration, comments, and reviews
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Project
from .collaboration_models import (
    CollaborationSession,
    CanvasEdit,
    Comment,
    Review,
    DesignFeedback
)
from .collaboration_serializers import (
    CollaborationSessionSerializer,
    CanvasEditSerializer,
    CommentSerializer,
    ReviewSerializer,
    DesignFeedbackSerializer,
    CommentResolveSerializer,
    ReviewRequestSerializer
)
from notifications.models import Notification


class CollaborationSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for collaboration sessions
    Read-only as sessions are managed via WebSocket
    """
    serializer_class = CollaborationSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CollaborationSession.objects.filter(
            project__user=self.request.user
        ).select_related('user', 'project')
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active collaboration sessions"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sessions = CollaborationSession.objects.filter(
            project_id=project_id,
            is_active=True
        ).select_related('user')
        
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)


class CanvasEditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for canvas edit history
    Useful for debugging and undo/redo functionality
    """
    serializer_class = CanvasEditSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        queryset = CanvasEdit.objects.select_related('user', 'project')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user's projects
        queryset = queryset.filter(
            project__user=self.request.user
        )
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent edits for a project"""
        project_id = request.query_params.get('project_id')
        limit = int(request.query_params.get('limit', 50))
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        edits = CanvasEdit.objects.filter(
            project_id=project_id
        ).select_related('user').order_by('-created_at')[:limit]
        
        serializer = self.get_serializer(edits, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for project comments
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        queryset = Comment.objects.select_related('user', 'resolved_by').prefetch_related('mentioned_users')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user's projects or projects they collaborate on
        queryset = queryset.filter(
            project__user=self.request.user
        ) | queryset.filter(
            project__collaborators=self.request.user
        )
        
        # Filter by resolution status
        is_resolved = self.request.query_params.get('is_resolved')
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        return queryset.distinct().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Send notifications to mentioned users
        comment = serializer.instance
        for mentioned_user in comment.mentioned_users.all():
            if mentioned_user != self.request.user:
                Notification.objects.create(
                    user=mentioned_user,
                    notification_type='comment_mention',
                    title=f'{self.request.user.username} mentioned you',
                    message=f'in a comment on {comment.project.name}',
                    link=f'/projects/{comment.project.id}'
                )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve or unresolve a comment"""
        comment = self.get_object()
        serializer = CommentResolveSerializer(data=request.data)
        
        if serializer.is_valid():
            is_resolved = serializer.validated_data['is_resolved']
            comment.is_resolved = is_resolved
            
            if is_resolved:
                comment.resolved_by = request.user
                comment.resolved_at = timezone.now()
            else:
                comment.resolved_by = None
                comment.resolved_at = None
            
            comment.save()
            
            return Response(
                CommentSerializer(comment, context={'request': request}).data
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved comments for a project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comments = self.get_queryset().filter(
            project_id=project_id,
            is_resolved=False,
            parent_comment__isnull=True  # Only top-level comments
        )
        
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for design reviews
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        queryset = Review.objects.select_related('reviewer', 'requested_by', 'project')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by reviews user requested or was asked to give
        queryset = queryset.filter(
            requested_by=self.request.user
        ) | queryset.filter(
            reviewer=self.request.user
        )
        
        return queryset.distinct().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
    
    @action(detail=False, methods=['post'])
    def request_review(self, request):
        """Request a review from another user"""
        serializer = ReviewRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            project_id = request.data.get('project_id')
            reviewer_id = serializer.validated_data['reviewer_id']
            message = serializer.validated_data.get('message', '')
            
            project = get_object_or_404(Project, id=project_id, user=request.user)
            reviewer = get_object_or_404(User, id=reviewer_id)
            
            # Create review request
            review = Review.objects.create(
                project=project,
                reviewer=reviewer,
                requested_by=request.user,
                status='pending'
            )
            
            # Send notification
            Notification.objects.create(
                user=reviewer,
                notification_type='review_request',
                title='Review Request',
                message=f'{request.user.username} requested your review on {project.name}',
                link=f'/projects/{project.id}/reviews/{review.id}',
                metadata={'message': message}
            )
            
            return Response(
                ReviewSerializer(review, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a review with status and ratings"""
        review = self.get_object()
        
        if review.reviewer != request.user:
            return Response(
                {'error': 'Only the reviewer can submit this review'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(review, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            # Notify project owner
            Notification.objects.create(
                user=review.requested_by,
                notification_type='review_submitted',
                title='Review Submitted',
                message=f'{review.reviewer.username} reviewed {review.project.name} - {review.get_status_display()}',
                link=f'/projects/{review.project.id}/reviews/{review.id}'
            )
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending reviews for the current user"""
        reviews = Review.objects.filter(
            reviewer=request.user,
            status='pending'
        ).select_related('project', 'requested_by')
        
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)


class DesignFeedbackViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI-generated design feedback
    """
    serializer_class = DesignFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        queryset = DesignFeedback.objects.select_related('project')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by user's projects
        queryset = queryset.filter(project__user=self.request.user)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate feedback as helpful or not"""
        feedback = self.get_object()
        is_helpful = request.data.get('is_helpful')
        
        if is_helpful is not None:
            feedback.is_helpful = is_helpful
            feedback.save()
            
            return Response(self.get_serializer(feedback).data)
        
        return Response(
            {'error': 'is_helpful field is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

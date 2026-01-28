"""
Views for Design Branches app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import (
    DesignBranch, DesignCommit, BranchMerge, MergeConflict,
    BranchReview, ReviewComment, DesignTag, BranchComparison
)
from .serializers import (
    DesignBranchSerializer, DesignBranchListSerializer,
    DesignCommitSerializer, DesignCommitListSerializer,
    BranchMergeSerializer, MergeConflictSerializer,
    BranchReviewSerializer, ReviewCommentSerializer,
    DesignTagSerializer, BranchComparisonSerializer,
    CreateBranchSerializer, MergeRequestSerializer, ConflictResolutionSerializer
)
from .services import BranchingService


class DesignBranchViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design branches."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'branch_type', 'status', 'is_default', 'is_protected']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DesignBranchListSerializer
        return DesignBranchSerializer
    
    def get_queryset(self):
        user = self.request.user
        return DesignBranch.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().select_related('parent_branch', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def commits(self, request, pk=None):
        """Get commits for this branch."""
        branch = self.get_object()
        commits = branch.commits.order_by('-created_at')
        
        # Pagination
        page = self.paginate_queryset(commits)
        if page is not None:
            serializer = DesignCommitListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DesignCommitListSerializer(commits, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def commit(self, request, pk=None):
        """Create a new commit on this branch."""
        branch = self.get_object()
        
        if branch.is_protected and not branch.allow_direct_commits:
            if not request.user.is_staff:
                return Response(
                    {'error': 'Direct commits to protected branches are not allowed'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        service = BranchingService(branch)
        commit = service.create_commit(
            author=request.user,
            message=request.data.get('message', 'Update'),
            description=request.data.get('description', ''),
            snapshot_data=request.data.get('snapshot_data', {}),
        )
        
        return Response(DesignCommitSerializer(commit).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def create_branch(self, request, pk=None):
        """Create a new branch from this branch."""
        parent_branch = self.get_object()
        serializer = CreateBranchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = BranchingService(parent_branch)
        new_branch = service.create_child_branch(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            branch_type=serializer.validated_data['branch_type'],
            created_by=request.user,
            from_commit_id=serializer.validated_data.get('from_commit'),
        )
        
        return Response(DesignBranchSerializer(new_branch).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def merge(self, request, pk=None):
        """Merge this branch into target branch."""
        source_branch = self.get_object()
        serializer = MergeRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_branch = DesignBranch.objects.get(
                id=serializer.validated_data['target_branch_id']
            )
        except DesignBranch.DoesNotExist:
            return Response({'error': 'Target branch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        service = BranchingService(source_branch)
        merge = service.merge_into(
            target_branch=target_branch,
            merged_by=request.user,
            strategy=serializer.validated_data['merge_strategy'],
            squash_message=serializer.validated_data.get('squash_message', ''),
            auto_resolve=serializer.validated_data.get('auto_resolve', False),
        )
        
        return Response(BranchMergeSerializer(merge).data)
    
    @action(detail=True, methods=['get'])
    def compare(self, request, pk=None):
        """Compare this branch with another."""
        base_branch = self.get_object()
        compare_id = request.query_params.get('with')
        
        if not compare_id:
            return Response({'error': 'Specify branch to compare with'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            compare_branch = DesignBranch.objects.get(id=compare_id)
        except DesignBranch.DoesNotExist:
            return Response({'error': 'Compare branch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        service = BranchingService(base_branch)
        comparison = service.compare_with(compare_branch)
        
        return Response(BranchComparisonSerializer(comparison).data)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive this branch."""
        branch = self.get_object()
        if branch.is_default:
            return Response({'error': 'Cannot archive default branch'}, status=status.HTTP_400_BAD_REQUEST)
        
        branch.status = 'archived'
        branch.archived_at = timezone.now()
        branch.save()
        
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an archived branch."""
        branch = self.get_object()
        if branch.status != 'archived':
            return Response({'error': 'Branch is not archived'}, status=status.HTTP_400_BAD_REQUEST)
        
        branch.status = 'active'
        branch.archived_at = None
        branch.save()
        
        return Response({'status': 'restored'})
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set this branch as the default."""
        branch = self.get_object()
        
        # Unset current default
        DesignBranch.objects.filter(
            project=branch.project,
            is_default=True
        ).update(is_default=False)
        
        branch.is_default = True
        branch.save()
        
        return Response({'status': 'set as default'})
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get reviews for this branch."""
        branch = self.get_object()
        reviews = branch.reviews.order_by('-created_at')
        serializer = BranchReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class DesignCommitViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design commits."""
    serializer_class = DesignCommitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['branch', 'author']
    search_fields = ['message', 'description', 'commit_sha']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return DesignCommit.objects.filter(
            Q(branch__project__owner=user) |
            Q(branch__project__team__members=user)
        ).distinct().select_related('branch', 'author', 'parent')
    
    @action(detail=True, methods=['get'])
    def diff(self, request, pk=None):
        """Get diff for this commit."""
        commit = self.get_object()
        return Response({
            'commit_sha': commit.commit_sha,
            'diff_data': commit.diff_data,
            'files_changed': commit.files_changed,
            'insertions': commit.insertions,
            'deletions': commit.deletions,
        })
    
    @action(detail=True, methods=['post'])
    def revert(self, request, pk=None):
        """Create a revert commit."""
        commit = self.get_object()
        branch = commit.branch
        
        service = BranchingService(branch)
        revert_commit = service.create_commit(
            author=request.user,
            message=f"Revert: {commit.message}",
            description=f"Reverts commit {commit.commit_sha}",
            snapshot_data=commit.parent.snapshot_data if commit.parent else {},
        )
        
        return Response(DesignCommitSerializer(revert_commit).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def cherry_pick(self, request, pk=None):
        """Cherry-pick this commit to another branch."""
        commit = self.get_object()
        target_branch_id = request.data.get('target_branch_id')
        
        if not target_branch_id:
            return Response({'error': 'Target branch required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_branch = DesignBranch.objects.get(id=target_branch_id)
        except DesignBranch.DoesNotExist:
            return Response({'error': 'Target branch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        service = BranchingService(target_branch)
        new_commit = service.cherry_pick(commit, request.user)
        
        return Response(DesignCommitSerializer(new_commit).data, status=status.HTTP_201_CREATED)


class BranchMergeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing branch merges."""
    serializer_class = BranchMergeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['source_branch', 'target_branch', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return BranchMerge.objects.filter(
            Q(source_branch__project__owner=user) |
            Q(source_branch__project__team__members=user)
        ).distinct().select_related(
            'source_branch', 'target_branch', 'merged_by'
        ).prefetch_related('conflicts')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete the merge after resolving conflicts."""
        merge = self.get_object()
        
        if merge.status == 'completed':
            return Response({'error': 'Merge already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        pending_conflicts = merge.conflicts.filter(resolution='pending')
        if pending_conflicts.exists():
            return Response(
                {'error': f'{pending_conflicts.count()} unresolved conflicts'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = BranchingService(merge.source_branch)
        service.complete_merge(merge, request.user)
        
        return Response(BranchMergeSerializer(merge).data)
    
    @action(detail=True, methods=['post'])
    def abort(self, request, pk=None):
        """Abort the merge."""
        merge = self.get_object()
        
        if merge.status in ['completed', 'aborted']:
            return Response({'error': 'Cannot abort this merge'}, status=status.HTTP_400_BAD_REQUEST)
        
        merge.status = 'aborted'
        merge.save()
        
        return Response({'status': 'aborted'})


class MergeConflictViewSet(viewsets.ModelViewSet):
    """ViewSet for managing merge conflicts."""
    serializer_class = MergeConflictSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['merge', 'conflict_type', 'resolution']
    
    def get_queryset(self):
        user = self.request.user
        return MergeConflict.objects.filter(
            Q(merge__source_branch__project__owner=user) |
            Q(merge__source_branch__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a conflict."""
        conflict = self.get_object()
        serializer = ConflictResolutionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        resolution = serializer.validated_data['resolution']
        
        if resolution == 'source':
            conflict.resolved_value = conflict.source_value
        elif resolution == 'target':
            conflict.resolved_value = conflict.target_value
        else:  # manual
            conflict.resolved_value = serializer.validated_data.get('resolved_value')
        
        conflict.resolution = resolution
        conflict.resolved_by = request.user
        conflict.resolved_at = timezone.now()
        conflict.save()
        
        return Response(MergeConflictSerializer(conflict).data)


class BranchReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing branch reviews."""
    serializer_class = BranchReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['branch', 'reviewer', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return BranchReview.objects.filter(
            Q(branch__project__owner=user) |
            Q(branch__project__team__members=user)
        ).distinct().select_related('branch', 'reviewer').prefetch_related('comments')
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve the branch changes."""
        review = self.get_object()
        review.status = 'approved'
        review.save()
        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'])
    def request_changes(self, request, pk=None):
        """Request changes to the branch."""
        review = self.get_object()
        review.status = 'changes_requested'
        review.summary = request.data.get('summary', '')
        review.save()
        return Response({'status': 'changes requested'})
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to the review."""
        review = self.get_object()
        serializer = ReviewCommentSerializer(data={
            **request.data,
            'review': review.id
        })
        if serializer.is_valid():
            serializer.save(review=review, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing review comments."""
    serializer_class = ReviewCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['review', 'author', 'is_resolved']
    
    def get_queryset(self):
        user = self.request.user
        return ReviewComment.objects.filter(
            Q(review__branch__project__owner=user) |
            Q(review__branch__project__team__members=user)
        ).distinct().select_related('author', 'review')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a comment."""
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
        serializer = ReviewCommentSerializer(data={
            'review': parent.review.id,
            'parent_comment': parent.id,
            'comment': request.data.get('comment', ''),
        })
        if serializer.is_valid():
            serializer.save(
                review=parent.review,
                parent_comment=parent,
                author=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignTagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design tags."""
    serializer_class = DesignTagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'is_release']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return DesignTag.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().select_related('commit', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BranchComparisonViewSet(viewsets.ModelViewSet):
    """ViewSet for managing branch comparisons."""
    serializer_class = BranchComparisonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['base_branch', 'compare_branch']
    
    def get_queryset(self):
        user = self.request.user
        return BranchComparison.objects.filter(
            Q(base_branch__project__owner=user) |
            Q(base_branch__project__team__members=user)
        ).distinct().select_related('base_branch', 'compare_branch')

"""
Serializers for Design Branches app.
"""
from rest_framework import serializers
from .models import (
    DesignBranch, DesignCommit, BranchMerge, MergeConflict,
    BranchReview, ReviewComment, DesignTag, BranchComparison
)


class DesignCommitSerializer(serializers.ModelSerializer):
    """Serializer for design commits."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    parent_sha = serializers.CharField(source='parent.commit_sha', read_only=True, allow_null=True)
    
    class Meta:
        model = DesignCommit
        fields = [
            'id', 'branch', 'commit_sha', 'parent', 'parent_sha',
            'message', 'description', 'snapshot_data', 'diff_data',
            'author', 'author_name', 'files_changed', 'insertions',
            'deletions', 'created_at'
        ]
        read_only_fields = ['id', 'commit_sha', 'author', 'created_at']


class DesignCommitListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for commit lists."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = DesignCommit
        fields = [
            'id', 'commit_sha', 'message', 'author_name',
            'files_changed', 'created_at'
        ]


class MergeConflictSerializer(serializers.ModelSerializer):
    """Serializer for merge conflicts."""
    
    class Meta:
        model = MergeConflict
        fields = [
            'id', 'merge', 'node_id', 'node_type', 'node_name',
            'source_value', 'target_value', 'conflict_type',
            'resolution', 'resolved_value', 'resolved_by',
            'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BranchMergeSerializer(serializers.ModelSerializer):
    """Serializer for branch merges."""
    source_branch_name = serializers.CharField(source='source_branch.name', read_only=True)
    target_branch_name = serializers.CharField(source='target_branch.name', read_only=True)
    merged_by_name = serializers.CharField(source='merged_by.username', read_only=True, allow_null=True)
    conflicts = MergeConflictSerializer(many=True, read_only=True)
    conflict_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BranchMerge
        fields = [
            'id', 'source_branch', 'source_branch_name', 'target_branch',
            'target_branch_name', 'merge_strategy', 'status', 'merge_commit',
            'merged_by', 'merged_by_name', 'merged_at', 'squash_message',
            'auto_resolve_conflicts', 'created_at', 'conflicts', 'conflict_count'
        ]
        read_only_fields = ['id', 'merge_commit', 'merged_by', 'merged_at', 'created_at']
    
    def get_conflict_count(self, obj):
        return obj.conflicts.filter(resolution='pending').count()


class ReviewCommentSerializer(serializers.ModelSerializer):
    """Serializer for review comments."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ReviewComment
        fields = [
            'id', 'review', 'parent_comment', 'author', 'author_name',
            'comment', 'node_id', 'line_number', 'is_resolved',
            'resolved_by', 'resolved_at', 'created_at', 'updated_at',
            'replies'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return ReviewCommentSerializer(obj.replies.all(), many=True).data
        return []


class BranchReviewSerializer(serializers.ModelSerializer):
    """Serializer for branch reviews."""
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    comments = ReviewCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BranchReview
        fields = [
            'id', 'branch', 'branch_name', 'reviewer', 'reviewer_name',
            'status', 'summary', 'created_at', 'updated_at',
            'comments', 'comment_count'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(is_resolved=False).count()


class DesignTagSerializer(serializers.ModelSerializer):
    """Serializer for design tags."""
    commit_sha = serializers.CharField(source='commit.commit_sha', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DesignTag
        fields = [
            'id', 'project', 'name', 'commit', 'commit_sha',
            'description', 'is_release', 'release_notes',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class BranchComparisonSerializer(serializers.ModelSerializer):
    """Serializer for branch comparisons."""
    base_branch_name = serializers.CharField(source='base_branch.name', read_only=True)
    compare_branch_name = serializers.CharField(source='compare_branch.name', read_only=True)
    
    class Meta:
        model = BranchComparison
        fields = [
            'id', 'base_branch', 'base_branch_name', 'compare_branch',
            'compare_branch_name', 'diff_summary', 'nodes_added',
            'nodes_modified', 'nodes_deleted', 'has_conflicts',
            'conflict_nodes', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'expires_at']


class DesignBranchSerializer(serializers.ModelSerializer):
    """Serializer for design branches."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    parent_branch_name = serializers.CharField(source='parent_branch.name', read_only=True, allow_null=True)
    commit_count = serializers.SerializerMethodField()
    latest_commit = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignBranch
        fields = [
            'id', 'project', 'name', 'description', 'branch_type',
            'status', 'parent_branch', 'parent_branch_name', 'base_commit',
            'head_commit', 'is_default', 'is_protected', 'allow_direct_commits',
            'require_review', 'require_all_approvals', 'minimum_approvals',
            'color', 'created_by', 'created_by_name', 'created_at',
            'updated_at', 'merged_at', 'archived_at', 'commit_count',
            'latest_commit'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'merged_at', 'archived_at']
    
    def get_commit_count(self, obj):
        return obj.commits.count()
    
    def get_latest_commit(self, obj):
        latest = obj.commits.order_by('-created_at').first()
        if latest:
            return DesignCommitListSerializer(latest).data
        return None


class DesignBranchListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for branch lists."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    commit_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignBranch
        fields = [
            'id', 'name', 'branch_type', 'status', 'is_default',
            'is_protected', 'color', 'created_by_name', 'updated_at',
            'commit_count'
        ]
    
    def get_commit_count(self, obj):
        return obj.commits.count()


class CreateBranchSerializer(serializers.Serializer):
    """Serializer for creating a branch from a commit."""
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    branch_type = serializers.ChoiceField(
        choices=['feature', 'experiment', 'release', 'hotfix'],
        default='feature'
    )
    from_commit = serializers.UUIDField(required=False)


class MergeRequestSerializer(serializers.Serializer):
    """Serializer for merge requests."""
    target_branch_id = serializers.UUIDField()
    merge_strategy = serializers.ChoiceField(
        choices=['fast_forward', 'merge', 'squash', 'rebase'],
        default='merge'
    )
    squash_message = serializers.CharField(required=False, allow_blank=True)
    auto_resolve = serializers.BooleanField(default=False)


class ConflictResolutionSerializer(serializers.Serializer):
    """Serializer for resolving conflicts."""
    resolution = serializers.ChoiceField(choices=['source', 'target', 'manual'])
    resolved_value = serializers.JSONField(required=False)

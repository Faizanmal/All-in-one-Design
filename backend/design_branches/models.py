"""
Design Branching System

Git-like branching for design exploration, allowing designers to
create feature branches, experiment safely, and merge changes.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid
import hashlib
import json


class DesignBranch(models.Model):
    """
    A branch represents an independent line of design development.
    Similar to Git branches for version control.
    """
    
    STATUS_ACTIVE = 'active'
    STATUS_MERGED = 'merged'
    STATUS_CLOSED = 'closed'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_MERGED, 'Merged'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_ARCHIVED, 'Archived'),
    ]
    
    BRANCH_TYPE_MAIN = 'main'
    BRANCH_TYPE_FEATURE = 'feature'
    BRANCH_TYPE_EXPERIMENT = 'experiment'
    BRANCH_TYPE_HOTFIX = 'hotfix'
    BRANCH_TYPE_REVIEW = 'review'
    BRANCH_TYPE_CHOICES = [
        (BRANCH_TYPE_MAIN, 'Main'),
        (BRANCH_TYPE_FEATURE, 'Feature'),
        (BRANCH_TYPE_EXPERIMENT, 'Experiment'),
        (BRANCH_TYPE_HOTFIX, 'Hotfix'),
        (BRANCH_TYPE_REVIEW, 'Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='design_branches'
    )
    
    # Branch info
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    branch_type = models.CharField(
        max_length=20,
        choices=BRANCH_TYPE_CHOICES,
        default=BRANCH_TYPE_FEATURE
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )
    
    # Branching hierarchy
    parent_branch = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_branches'
    )
    
    # Branch point (commit from which this branch was created)
    branch_point = models.ForeignKey(
        'DesignCommit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branched_from'
    )
    
    # Current head commit
    head_commit = models.ForeignKey(
        'DesignCommit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    # Is this the main/default branch
    is_default = models.BooleanField(default=False)
    
    # Protection settings
    is_protected = models.BooleanField(default=False)
    require_review = models.BooleanField(default=False)
    required_reviewers = models.IntegerField(default=0)
    
    # Access control
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_branches'
    )
    collaborators = models.ManyToManyField(
        User,
        blank=True,
        related_name='branch_access'
    )
    
    # Color for visual identification
    color = models.CharField(max_length=50, default='#6366f1')
    icon = models.CharField(max_length=50, default='git-branch')
    
    # Metadata
    tags = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    merged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Design Branch'
        verbose_name_plural = 'Design Branches'
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.project.name}/{self.name}"
    
    def get_commit_count(self):
        """Get number of commits in this branch."""
        return self.commits.count()
    
    def get_ahead_behind(self, target_branch):
        """Calculate commits ahead/behind compared to target branch."""
        if not target_branch:
            return {'ahead': 0, 'behind': 0}
        
        # Get common ancestor
        common_ancestor = self._find_common_ancestor(target_branch)
        
        # Count commits since common ancestor
        our_commits = self._get_commits_since(common_ancestor)
        their_commits = target_branch._get_commits_since(common_ancestor)
        
        return {
            'ahead': len(our_commits),
            'behind': len(their_commits)
        }
    
    def _find_common_ancestor(self, other_branch):
        """Find the common ancestor commit between two branches."""
        our_commits = set(str(c.id) for c in self.commits.all())
        
        current = other_branch.head_commit
        while current:
            if str(current.id) in our_commits:
                return current
            current = current.parent_commit
        
        return None
    
    def _get_commits_since(self, ancestor):
        """Get all commits since an ancestor."""
        if not ancestor:
            return list(self.commits.all())
        
        commits = []
        current = self.head_commit
        while current and current != ancestor:
            commits.append(current)
            current = current.parent_commit
        
        return commits


class DesignCommit(models.Model):
    """
    A commit represents a snapshot of the design at a point in time.
    Similar to Git commits.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='commits'
    )
    
    # Commit metadata
    message = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Hash for integrity verification
    commit_hash = models.CharField(max_length=64, unique=True, editable=False)
    short_hash = models.CharField(max_length=8, editable=False)
    
    # Parent commit (for history tracking)
    parent_commit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_commits'
    )
    
    # For merge commits (second parent)
    merge_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merged_into'
    )
    
    # Full design snapshot
    design_data = models.JSONField(default=dict)
    
    # Component snapshots (for efficient diffing)
    components_snapshot = models.JSONField(default=dict)
    
    # Canvas metadata
    canvas_state = models.JSONField(default=dict)
    # Example: {"zoom": 1.0, "scrollX": 0, "scrollY": 0, "selectedElements": []}
    
    # Author information
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='design_commits'
    )
    
    # Co-authors (for collaborative work)
    co_authors = models.ManyToManyField(
        User,
        blank=True,
        related_name='co_authored_commits'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Is this an auto-save commit
    is_auto_save = models.BooleanField(default=False)
    
    # Tags/labels
    tags = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Design Commit'
        verbose_name_plural = 'Design Commits'
    
    def __str__(self):
        return f"{self.short_hash}: {self.message[:50]}"
    
    def save(self, *args, **kwargs):
        if not self.commit_hash:
            self.commit_hash = self._generate_hash()
            self.short_hash = self.commit_hash[:8]
        super().save(*args, **kwargs)
    
    def _generate_hash(self):
        """Generate a unique hash for this commit."""
        content = {
            'design_data': self.design_data,
            'parent': str(self.parent_commit.id) if self.parent_commit else None,
            'message': self.message,
            'author_id': self.author.id if self.author else None,
        }
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


class BranchMerge(models.Model):
    """
    Records merge operations between branches.
    """
    
    MERGE_STATUS_PENDING = 'pending'
    MERGE_STATUS_IN_PROGRESS = 'in_progress'
    MERGE_STATUS_COMPLETED = 'completed'
    MERGE_STATUS_CONFLICTED = 'conflicted'
    MERGE_STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (MERGE_STATUS_PENDING, 'Pending'),
        (MERGE_STATUS_IN_PROGRESS, 'In Progress'),
        (MERGE_STATUS_COMPLETED, 'Completed'),
        (MERGE_STATUS_CONFLICTED, 'Conflicted'),
        (MERGE_STATUS_CANCELLED, 'Cancelled'),
    ]
    
    MERGE_STRATEGY_FAST_FORWARD = 'fast_forward'
    MERGE_STRATEGY_MERGE_COMMIT = 'merge_commit'
    MERGE_STRATEGY_SQUASH = 'squash'
    MERGE_STRATEGY_REBASE = 'rebase'
    STRATEGY_CHOICES = [
        (MERGE_STRATEGY_FAST_FORWARD, 'Fast Forward'),
        (MERGE_STRATEGY_MERGE_COMMIT, 'Merge Commit'),
        (MERGE_STRATEGY_SQUASH, 'Squash'),
        (MERGE_STRATEGY_REBASE, 'Rebase'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Branches involved
    source_branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='merges_as_source'
    )
    target_branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='merges_as_target'
    )
    
    # Merge details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=MERGE_STATUS_PENDING
    )
    
    # Strategy
    merge_strategy = models.CharField(
        max_length=20,
        choices=STRATEGY_CHOICES,
        default=MERGE_STRATEGY_MERGE_COMMIT
    )
    
    # Resulting commit (for merge_commit strategy)
    merge_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )
    
    # Commits being merged
    source_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    target_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    
    # User who initiated the merge
    merged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='design_merges'
    )
    
    # Delete source branch after merge
    delete_source_after_merge = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Branch Merge'
        verbose_name_plural = 'Branch Merges'
    
    def __str__(self):
        return f"Merge {self.source_branch.name} → {self.target_branch.name}"


class MergeConflict(models.Model):
    """
    Records conflicts that arise during merge operations.
    """
    
    CONFLICT_TYPE_PROPERTY = 'property'
    CONFLICT_TYPE_POSITION = 'position'
    CONFLICT_TYPE_DELETION = 'deletion'
    CONFLICT_TYPE_CREATION = 'creation'
    CONFLICT_TYPE_STYLE = 'style'
    TYPE_CHOICES = [
        (CONFLICT_TYPE_PROPERTY, 'Property Conflict'),
        (CONFLICT_TYPE_POSITION, 'Position Conflict'),
        (CONFLICT_TYPE_DELETION, 'Deletion Conflict'),
        (CONFLICT_TYPE_CREATION, 'Creation Conflict'),
        (CONFLICT_TYPE_STYLE, 'Style Conflict'),
    ]
    
    RESOLUTION_NONE = 'none'
    RESOLUTION_OURS = 'ours'
    RESOLUTION_THEIRS = 'theirs'
    RESOLUTION_MANUAL = 'manual'
    RESOLUTION_CHOICES = [
        (RESOLUTION_NONE, 'Unresolved'),
        (RESOLUTION_OURS, 'Keep Ours'),
        (RESOLUTION_THEIRS, 'Keep Theirs'),
        (RESOLUTION_MANUAL, 'Manual Resolution'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merge = models.ForeignKey(
        BranchMerge,
        on_delete=models.CASCADE,
        related_name='conflicts'
    )
    
    # Conflict details
    conflict_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Element that has conflict
    element_id = models.CharField(max_length=100)
    element_type = models.CharField(max_length=50)
    element_name = models.CharField(max_length=255, blank=True)
    
    # Path to conflicting property
    property_path = models.CharField(max_length=255, blank=True)
    
    # Values
    our_value = models.JSONField(null=True, blank=True)
    their_value = models.JSONField(null=True, blank=True)
    base_value = models.JSONField(null=True, blank=True)  # Common ancestor value
    
    # Resolution
    resolution = models.CharField(
        max_length=20,
        choices=RESOLUTION_CHOICES,
        default=RESOLUTION_NONE
    )
    resolved_value = models.JSONField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_conflicts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Description of conflict
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['element_type', 'element_name']
        verbose_name = 'Merge Conflict'
        verbose_name_plural = 'Merge Conflicts'
    
    def __str__(self):
        return f"Conflict: {self.element_name} - {self.property_path}"


class BranchReview(models.Model):
    """
    Design review for a branch before merging.
    Similar to Pull Request reviews.
    """
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_CHANGES_REQUESTED = 'changes_requested'
    STATUS_COMMENTED = 'commented'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_CHANGES_REQUESTED, 'Changes Requested'),
        (STATUS_COMMENTED, 'Commented'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    merge_request = models.ForeignKey(
        BranchMerge,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reviews'
    )
    
    # Reviewer
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='design_reviews'
    )
    
    # Review content
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    summary = models.TextField(blank=True)
    
    # Commit reviewed (to track if branch has new commits since review)
    reviewed_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    
    # Is review stale (branch has new commits)
    is_stale = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Branch Review'
        verbose_name_plural = 'Branch Reviews'
    
    def __str__(self):
        return f"Review by {self.reviewer.username} on {self.branch.name}"


class ReviewComment(models.Model):
    """
    Comments on specific elements or general review comments.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(
        BranchReview,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Author
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='design_review_comments'
    )
    
    # Comment content
    body = models.TextField()
    
    # Position on canvas (for contextual comments)
    position_x = models.FloatField(null=True, blank=True)
    position_y = models.FloatField(null=True, blank=True)
    
    # Target element
    element_id = models.CharField(max_length=100, blank=True)
    
    # Thread support
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Resolution
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_review_comments'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Review Comment'
        verbose_name_plural = 'Review Comments'
    
    def __str__(self):
        return f"Comment by {self.author.username}"


class DesignTag(models.Model):
    """
    Tags for marking specific commits (like Git tags).
    Useful for marking releases, milestones, etc.
    """
    
    TAG_TYPE_VERSION = 'version'
    TAG_TYPE_MILESTONE = 'milestone'
    TAG_TYPE_RELEASE = 'release'
    TAG_TYPE_SNAPSHOT = 'snapshot'
    TYPE_CHOICES = [
        (TAG_TYPE_VERSION, 'Version'),
        (TAG_TYPE_MILESTONE, 'Milestone'),
        (TAG_TYPE_RELEASE, 'Release'),
        (TAG_TYPE_SNAPSHOT, 'Snapshot'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='design_tags'
    )
    commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.CASCADE,
        related_name='tags_applied'
    )
    
    # Tag info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tag_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TAG_TYPE_VERSION
    )
    
    # Visual
    color = models.CharField(max_length=50, default='#6366f1')
    icon = models.CharField(max_length=50, default='tag')
    
    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_design_tags'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Design Tag'
        verbose_name_plural = 'Design Tags'
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.name} @ {self.commit.short_hash}"


class BranchComparison(models.Model):
    """
    Cached comparison data between two branches for faster diffing.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Branches being compared
    base_branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='comparisons_as_base'
    )
    compare_branch = models.ForeignKey(
        DesignBranch,
        on_delete=models.CASCADE,
        related_name='comparisons_as_compare'
    )
    
    # Commits at time of comparison
    base_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    compare_commit = models.ForeignKey(
        DesignCommit,
        on_delete=models.SET_NULL,
        null=True,
        related_name='+'
    )
    
    # Comparison results
    diff_data = models.JSONField(default=dict)
    # Structure:
    # {
    #   "added": [{"id": "...", "type": "...", "name": "..."}],
    #   "removed": [{"id": "...", "type": "...", "name": "..."}],
    #   "modified": [{"id": "...", "changes": [...]}],
    #   "unchanged": 42
    # }
    
    # Stats
    additions_count = models.IntegerField(default=0)
    deletions_count = models.IntegerField(default=0)
    modifications_count = models.IntegerField(default=0)
    
    # Is comparison still valid
    is_stale = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Branch Comparison'
        verbose_name_plural = 'Branch Comparisons'
    
    def __str__(self):
        return f"{self.base_branch.name}...{self.compare_branch.name}"

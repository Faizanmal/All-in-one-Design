"""
Enhanced version control with branching support
"""
from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
import json


class VersionBranch(models.Model):
    """
    Version control branch for projects
    Enables parallel development and experimentation
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Branch hierarchy
    parent_branch = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_branches'
    )
    
    # Branch metadata
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_branches')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = ['project', 'name']
        indexes = [
            models.Index(fields=['project', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"


class VersionCommit(models.Model):
    """
    Individual version commit within a branch
    """
    branch = models.ForeignKey(VersionBranch, on_delete=models.CASCADE, related_name='commits')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='version_commits')
    
    # Commit details
    commit_hash = models.CharField(max_length=40, unique=True)
    message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='version_commits')
    
    # Version data
    design_data = models.JSONField()
    canvas_config = models.JSONField(default=dict)  # width, height, background
    
    # Commit hierarchy
    parent_commit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_commits'
    )
    
    # Diff/changes
    changes_summary = models.JSONField(default=dict)
    # {
    #   "elements_added": 5,
    #   "elements_modified": 3,
    #   "elements_deleted": 1,
    #   "properties_changed": ["color", "position"]
    # }
    
    # Tags
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['branch', '-created_at']),
            models.Index(fields=['commit_hash']),
        ]
    
    def __str__(self):
        return f"{self.commit_hash[:8]} - {self.message[:50]}"


class MergeRequest(models.Model):
    """
    Merge request for merging branches
    """
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('merged', 'Merged'),
        ('closed', 'Closed'),
        ('conflicted', 'Has Conflicts'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='merge_requests')
    
    # Source and target branches
    source_branch = models.ForeignKey(
        VersionBranch,
        on_delete=models.CASCADE,
        related_name='merge_requests_as_source'
    )
    target_branch = models.ForeignKey(
        VersionBranch,
        on_delete=models.CASCADE,
        related_name='merge_requests_as_target'
    )
    
    # Request details
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Users
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_merge_requests')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_merge_requests'
    )
    merged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merged_merge_requests'
    )
    
    # Conflict resolution
    has_conflicts = models.BooleanField(default=False)
    conflicts_data = models.JSONField(default=dict)
    resolution_data = models.JSONField(default=dict)
    
    # Merge metadata
    merge_commit = models.ForeignKey(
        VersionCommit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merge_requests'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    merged_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
        ]
    
    def __str__(self):
        return f"MR: {self.source_branch.name} → {self.target_branch.name}"


class VersionTag(models.Model):
    """
    Named tags for important versions/milestones
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='version_tags')
    commit = models.ForeignKey(VersionCommit, on_delete=models.CASCADE, related_name='version_tags')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Tag types
    TAG_TYPES = (
        ('release', 'Release'),
        ('milestone', 'Milestone'),
        ('backup', 'Backup'),
        ('review', 'Review Point'),
    )
    tag_type = models.CharField(max_length=20, choices=TAG_TYPES, default='milestone')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"


class VersionDiff(models.Model):
    """
    Store computed diffs between versions
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='version_diffs')
    
    from_commit = models.ForeignKey(
        VersionCommit,
        on_delete=models.CASCADE,
        related_name='diffs_as_source'
    )
    to_commit = models.ForeignKey(
        VersionCommit,
        on_delete=models.CASCADE,
        related_name='diffs_as_target'
    )
    
    # Diff data
    diff_data = models.JSONField()
    # {
    #   "added": [<elements>],
    #   "modified": [{"element_id": "...", "changes": {...}}],
    #   "deleted": [<elements>],
    #   "summary": "Brief summary"
    # }
    
    computed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_commit', 'to_commit']
        indexes = [
            models.Index(fields=['project', '-computed_at']),
        ]
    
    def __str__(self):
        return f"Diff: {self.from_commit.commit_hash[:8]} → {self.to_commit.commit_hash[:8]}"

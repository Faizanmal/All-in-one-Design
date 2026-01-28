"""
Enhanced Commenting & Review Models

Threaded comments, video comments, mentions, reactions, review workflows.
"""

from django.db import models
from django.conf import settings
import uuid


class CommentThread(models.Model):
    """A thread of comments on a specific location."""
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('wont_fix', "Won't Fix"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='comment_threads')
    
    # Location
    frame_id = models.CharField(max_length=100, blank=True)
    element_id = models.CharField(max_length=100, blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    
    # Status and assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_threads')
    
    # Priority
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    # Categorization
    label = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_threads')
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_threads')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Version tracking
    version_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
        ]


class Comment(models.Model):
    """Individual comment in a thread."""
    
    COMMENT_TYPES = [
        ('text', 'Text'),
        ('voice', 'Voice'),
        ('video', 'Video'),
        ('annotation', 'Annotation'),
        ('emoji', 'Emoji'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(CommentThread, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='text')
    
    # Content
    content = models.TextField(blank=True)
    
    # Media attachments for voice/video comments
    media_file = models.FileField(upload_to='comment_media/', null=True, blank=True)
    media_duration = models.FloatField(null=True, blank=True)  # Duration in seconds
    thumbnail = models.ImageField(upload_to='comment_thumbnails/', null=True, blank=True)
    
    # Annotation data (for visual markup)
    annotation_data = models.JSONField(default=dict, blank=True)
    # {
    #   "type": "rectangle|circle|arrow|freehand",
    #   "points": [...],
    #   "color": "#ff0000",
    #   "stroke_width": 2
    # }
    
    # Author
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_comments')
    
    # Editing
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Visibility
    is_internal = models.BooleanField(default=False)  # Only visible to team
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']


class Mention(models.Model):
    """User mention in a comment."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='mentions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentions')
    
    # Position in comment text
    start_index = models.IntegerField(default=0)
    end_index = models.IntegerField(default=0)
    
    # Notification tracking
    notified = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)


class Reaction(models.Model):
    """Emoji reaction to a comment."""
    
    REACTION_TYPES = [
        ('👍', 'thumbs_up'),
        ('👎', 'thumbs_down'),
        ('❤️', 'heart'),
        ('😄', 'smile'),
        ('🎉', 'celebration'),
        ('🤔', 'thinking'),
        ('👀', 'eyes'),
        ('✅', 'check'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    
    emoji = models.CharField(max_length=10)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user', 'emoji']


class ReviewSession(models.Model):
    """Formal review session for design approval."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='review_sessions')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Scope
    frame_ids = models.JSONField(default=list)  # Frames to review
    version_id = models.CharField(max_length=100, blank=True)
    
    # Review settings
    require_all_approvals = models.BooleanField(default=True)
    approval_count_needed = models.IntegerField(default=1)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timeline
    due_date = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Creator
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_reviews')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class Reviewer(models.Model):
    """Reviewer in a review session."""
    
    DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('changes_requested', 'Changes Requested'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ReviewSession, on_delete=models.CASCADE, related_name='reviewers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_assignments')
    
    # Review status
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    
    # Notification
    invited_at = models.DateTimeField(auto_now_add=True)
    reminded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['session', 'user']


class CommentNotification(models.Model):
    """Notification for comment activity."""
    
    NOTIFICATION_TYPES = [
        ('mention', 'Mentioned'),
        ('reply', 'Reply'),
        ('thread_update', 'Thread Update'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
        ('review_request', 'Review Request'),
        ('approval', 'Approval'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_notifications')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    
    # Related objects
    thread = models.ForeignKey(CommentThread, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey(ReviewSession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Actor
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='actions')
    
    # Status
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class CommentTemplate(models.Model):
    """Reusable comment template."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comment_templates')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='comment_templates')
    
    name = models.CharField(max_length=100)
    content = models.TextField()
    shortcut = models.CharField(max_length=20, blank=True)  # e.g., "/approved"
    
    # Categorization
    category = models.CharField(max_length=50, blank=True)
    
    is_shared = models.BooleanField(default=False)  # Share with team
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']

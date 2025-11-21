"""
Collaboration models for real-time editing, comments, and reviews
"""
from django.db import models
from django.contrib.auth.models import User
from .models import Project


class CollaborationSession(models.Model):
    """Track active collaboration sessions for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='collaboration_sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Session tracking
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    
    # Cursor/presence data
    cursor_position = models.JSONField(default=dict)  # {"x": 100, "y": 200}
    selected_elements = models.JSONField(default=list)  # [element_id1, element_id2]
    viewport = models.JSONField(default=dict)  # {"zoom": 1.0, "pan": {"x": 0, "y": 0}}
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity']
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.project.name}"


class CanvasEdit(models.Model):
    """Track individual canvas edits for operational transformation"""
    EDIT_TYPES = (
        ('create', 'Create Element'),
        ('update', 'Update Element'),
        ('delete', 'Delete Element'),
        ('move', 'Move Element'),
        ('resize', 'Resize Element'),
        ('style', 'Style Change'),
        ('group', 'Group Elements'),
        ('ungroup', 'Ungroup Elements'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='canvas_edits')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(CollaborationSession, on_delete=models.SET_NULL, null=True)
    
    # Edit details
    edit_type = models.CharField(max_length=20, choices=EDIT_TYPES)
    element_id = models.CharField(max_length=100, blank=True)
    
    # Change data
    previous_data = models.JSONField(default=dict)
    new_data = models.JSONField(default=dict)
    
    # Operational transformation
    vector_clock = models.JSONField(default=dict)  # For conflict resolution
    parent_edit_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['element_id']),
        ]
    
    def __str__(self):
        return f"{self.edit_type} by {self.user.username}"


class Comment(models.Model):
    """Comments and feedback on designs"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_comments')
    
    # Comment content
    content = models.TextField()
    
    # Position on canvas (optional - for anchored comments)
    anchor_position = models.JSONField(null=True, blank=True)  # {"x": 100, "y": 200}
    anchor_element_id = models.CharField(max_length=100, blank=True)
    
    # Threading
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Mentions
    mentioned_users = models.ManyToManyField(User, related_name='mentioned_in_comments', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"


class Review(models.Model):
    """Design reviews with approval workflow"""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
        ('rejected', 'Rejected'),
    )
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_requested')
    
    # Review details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    summary = models.TextField(blank=True)
    
    # Ratings
    design_quality = models.IntegerField(null=True, blank=True, help_text="1-10 rating")
    creativity = models.IntegerField(null=True, blank=True, help_text="1-10 rating")
    usability = models.IntegerField(null=True, blank=True, help_text="1-10 rating")
    overall_rating = models.IntegerField(null=True, blank=True, help_text="1-10 rating")
    
    # Version tracking
    reviewed_version = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'reviewer']
    
    def __str__(self):
        return f"Review by {self.reviewer.username} - {self.status}"


class DesignFeedback(models.Model):
    """AI-generated design feedback and suggestions"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ai_feedback')
    
    # Feedback type
    FEEDBACK_TYPES = (
        ('critique', 'Design Critique'),
        ('color_suggestion', 'Color Suggestions'),
        ('typography_suggestion', 'Typography Suggestions'),
        ('layout_suggestion', 'Layout Suggestions'),
        ('accessibility', 'Accessibility Check'),
        ('brand_consistency', 'Brand Consistency'),
    )
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    
    # AI-generated content
    feedback_data = models.JSONField(default=dict)
    # {
    #   "overall_score": 8.5,
    #   "suggestions": [...],
    #   "strengths": [...],
    #   "improvements": [...]
    # }
    
    # User interaction
    is_helpful = models.BooleanField(null=True, blank=True)
    user_notes = models.TextField(blank=True)
    
    # AI metadata
    model_used = models.CharField(max_length=50, default='gpt-4')
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(default=0.0, help_text="Seconds")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} for {self.project.name}"

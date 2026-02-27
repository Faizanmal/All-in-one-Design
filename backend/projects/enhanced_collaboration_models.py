"""
Enhanced Collaboration Models
Video conferencing, guest access, and advanced sharing features
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


class VideoConferenceRoom(models.Model):
    """Video conference rooms for design collaboration"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    )
    
    # Host and project
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_conferences')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='video_conferences',
        null=True,
        blank=True
    )
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.CASCADE,
        related_name='video_conferences',
        null=True,
        blank=True
    )
    
    # Room details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    room_code = models.CharField(max_length=32, unique=True)
    
    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    
    # Settings
    max_participants = models.IntegerField(default=10)
    is_recording_enabled = models.BooleanField(default=False)
    is_screen_share_enabled = models.BooleanField(default=True)
    is_canvas_sync_enabled = models.BooleanField(default=True)
    waiting_room_enabled = models.BooleanField(default=True)
    
    # External integration
    external_provider = models.CharField(max_length=50, blank=True)  # 'zoom', 'meet', 'teams'
    external_room_id = models.CharField(max_length=255, blank=True)
    external_join_url = models.URLField(blank=True)
    
    # Recording
    recording_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_start']
    
    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class VideoConferenceParticipant(models.Model):
    """Participants in video conferences"""
    ROLE_CHOICES = (
        ('host', 'Host'),
        ('co-host', 'Co-host'),
        ('presenter', 'Presenter'),
        ('participant', 'Participant'),
        ('viewer', 'Viewer'),
    )
    
    room = models.ForeignKey(VideoConferenceRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conference_participations')
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    
    # Status
    is_active = models.BooleanField(default=False)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    # Permissions
    can_share_screen = models.BooleanField(default=True)
    can_annotate = models.BooleanField(default=True)
    can_edit_canvas = models.BooleanField(default=False)
    
    # Connection info
    connection_quality = models.CharField(max_length=20, blank=True)  # 'good', 'fair', 'poor'
    
    class Meta:
        unique_together = ['room', 'user']


class GuestAccess(models.Model):
    """Guest access tokens for sharing designs"""
    ACCESS_LEVELS = (
        ('view', 'View Only'),
        ('comment', 'View & Comment'),
        ('edit', 'View & Edit'),
        ('full', 'Full Access'),
    )
    
    # What is being shared
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='guest_accesses',
        null=True,
        blank=True
    )
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.CASCADE,
        related_name='guest_accesses',
        null=True,
        blank=True
    )
    
    # Who created and who can access
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_guest_accesses')
    guest_email = models.EmailField(blank=True)  # For tracked guest access
    
    # Access token
    access_token = models.CharField(max_length=64, unique=True)
    
    # Access level
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='view')
    
    # Restrictions
    password_protected = models.BooleanField(default=False)
    password_hash = models.CharField(max_length=255, blank=True)
    
    max_views = models.IntegerField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Allowed operations
    allow_download = models.BooleanField(default=False)
    allow_copy = models.BooleanField(default=False)
    watermark_enabled = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Guest accesses'
    
    def save(self, *args, **kwargs):
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_view_limit_reached(self):
        if self.max_views:
            return self.view_count >= self.max_views
        return False
    
    def __str__(self):
        return f"Guest access for {self.project or self.asset}"


class GuestAccessLog(models.Model):
    """Log guest access events"""
    EVENT_TYPES = (
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('comment', 'Commented'),
        ('edit', 'Edited'),
    )
    
    guest_access = models.ForeignKey(GuestAccess, on_delete=models.CASCADE, related_name='access_logs')
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Visitor info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Event details
    event_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class DesignReviewSession(models.Model):
    """Design review sessions for stakeholder feedback"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
    )
    
    # Project and reviewer
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='design_review_sessions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_design_review_sessions')
    
    # Review details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Version being reviewed
    version_number = models.CharField(max_length=50, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Deadline
    deadline = models.DateTimeField(null=True, blank=True)
    
    # Settings
    require_all_approvals = models.BooleanField(default=False)
    allow_anonymous_feedback = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class ReviewSessionParticipant(models.Model):
    """Participants in design review sessions"""
    ROLE_CHOICES = (
        ('approver', 'Approver'),
        ('reviewer', 'Reviewer'),
        ('viewer', 'Viewer'),
    )
    
    DECISION_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('approved_with_comments', 'Approved with Comments'),
        ('changes_requested', 'Changes Requested'),
        ('rejected', 'Rejected'),
    )
    
    session = models.ForeignKey(DesignReviewSession, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_participations', null=True, blank=True)
    
    # For guest reviewers
    guest_email = models.EmailField(blank=True)
    guest_name = models.CharField(max_length=255, blank=True)
    invite_token = models.CharField(max_length=64, blank=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reviewer')
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES, default='pending')
    
    # Feedback
    feedback = models.TextField(blank=True)
    
    # Status
    is_notified = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['session', 'user', 'guest_email']
    
    def save(self, *args, **kwargs):
        if not self.invite_token and (self.guest_email or not self.user):
            self.invite_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)


class ReviewAnnotation(models.Model):
    """Annotations on design reviews"""
    ANNOTATION_TYPES = (
        ('pin', 'Pin Comment'),
        ('area', 'Area Selection'),
        ('arrow', 'Arrow'),
        ('drawing', 'Freehand Drawing'),
    )
    
    session = models.ForeignKey(DesignReviewSession, on_delete=models.CASCADE, related_name='annotations')
    participant = models.ForeignKey(ReviewSessionParticipant, on_delete=models.CASCADE, related_name='annotations')
    
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES, default='pin')
    
    # Position and shape
    position_data = models.JSONField(default=dict)
    # For pin: {"x": 100, "y": 200}
    # For area: {"x": 100, "y": 200, "width": 300, "height": 150}
    # For arrow: {"x1": 100, "y1": 200, "x2": 300, "y2": 150}
    # For drawing: {"points": [[x1, y1], [x2, y2], ...]}
    
    # Comment
    comment = models.TextField()
    
    # Threading
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_resolved_annotations')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']


class CollaborationPresence(models.Model):
    """Track user presence in collaborative sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presences')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='presences')
    
    # Connection info
    session_id = models.CharField(max_length=255)
    
    # Cursor position
    cursor_x = models.FloatField(null=True, blank=True)
    cursor_y = models.FloatField(null=True, blank=True)
    
    # Selection
    selected_elements = models.JSONField(default=list)
    
    # User activity
    activity_status = models.CharField(max_length=50, default='active')  # 'active', 'idle', 'typing', 'editing'
    
    # Color for user indicator
    color = models.CharField(max_length=7, blank=True)  # Hex color
    
    last_heartbeat = models.DateTimeField(auto_now=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'project', 'session_id']
    
    @property
    def is_online(self):
        # Consider user offline if no heartbeat in 30 seconds
        return (timezone.now() - self.last_heartbeat).seconds < 30

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Team(models.Model):
    """Team model for multi-user collaboration"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Team owner
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    
    # Team members
    members = models.ManyToManyField(User, through='TeamMembership', related_name='teams')
    
    # Settings
    is_active = models.BooleanField(default=True)
    max_members = models.IntegerField(default=10, help_text="Maximum number of team members")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['owner']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate team"""
        if self.members.count() >= self.max_members:
            raise ValidationError(f"Team has reached maximum members limit ({self.max_members})")
    
    @property
    def member_count(self):
        """Get total member count"""
        return self.members.count()
    
    @property
    def project_count(self):
        """Get total project count"""
        return self.projects.count()


class TeamMembership(models.Model):
    """Team membership with roles and permissions"""
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    )
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    
    # Permissions
    can_create_projects = models.BooleanField(default=True)
    can_edit_projects = models.BooleanField(default=True)
    can_delete_projects = models.BooleanField(default=False)
    can_invite_members = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['team', 'user']
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['team', 'user']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-assign permissions based on role"""
        if self.role == 'owner':
            self.can_create_projects = True
            self.can_edit_projects = True
            self.can_delete_projects = True
            self.can_invite_members = True
            self.can_manage_members = True
        elif self.role == 'admin':
            self.can_create_projects = True
            self.can_edit_projects = True
            self.can_delete_projects = True
            self.can_invite_members = True
            self.can_manage_members = True
        elif self.role == 'member':
            self.can_create_projects = True
            self.can_edit_projects = True
            self.can_delete_projects = False
            self.can_invite_members = False
            self.can_manage_members = False
        elif self.role == 'viewer':
            self.can_create_projects = False
            self.can_edit_projects = False
            self.can_delete_projects = False
            self.can_invite_members = False
            self.can_manage_members = False
        
        super().save(*args, **kwargs)


class TeamInvitation(models.Model):
    """Team invitation model"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    )
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    role = models.CharField(max_length=20, choices=TeamMembership.ROLE_CHOICES, default='member')
    
    # Invitation details
    message = models.TextField(blank=True)
    token = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['token']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.team.name}"
    
    @property
    def is_expired(self):
        """Check if invitation is expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at


class TeamProject(models.Model):
    """Link projects to teams"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_projects')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='team_associations')
    
    # Permissions
    is_shared = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team', 'project']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project.name} in {self.team.name}"


class Comment(models.Model):
    """Comments on projects for team collaboration"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    # Comment details
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Position (for design comments)
    position_x = models.IntegerField(null=True, blank=True)
    position_y = models.IntegerField(null=True, blank=True)
    
    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_comments')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Mentions
    mentions = models.ManyToManyField(User, related_name='mentioned_in_comments', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['is_resolved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"
    
    @property
    def reply_count(self):
        """Get number of replies"""
        return self.replies.count()


class TeamActivity(models.Model):
    """Activity feed for teams"""
    ACTION_CHOICES = (
        ('project_created', 'Project Created'),
        ('project_updated', 'Project Updated'),
        ('project_deleted', 'Project Deleted'),
        ('member_joined', 'Member Joined'),
        ('member_left', 'Member Left'),
        ('member_role_changed', 'Member Role Changed'),
        ('comment_added', 'Comment Added'),
        ('comment_resolved', 'Comment Resolved'),
        ('export_created', 'Export Created'),
    )
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Related objects
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Activity details
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Team activities'
        indexes = [
            models.Index(fields=['team', 'created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} in {self.team.name}"

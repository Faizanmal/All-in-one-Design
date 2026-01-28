from django.db import models
from django.contrib.auth.models import User


class Role(models.Model):
    """Custom roles with granular permissions"""
    ROLE_TYPES = (
        ('system', 'System Role'),
        ('team', 'Team Role'),
        ('project', 'Project Role'),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default='team')
    
    # Team (for team-scoped roles)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='custom_roles')
    
    # Role hierarchy
    is_admin = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=False)
    
    # Display
    color = models.CharField(max_length=20, default='#6B7280')
    icon = models.CharField(max_length=50, default='user')
    
    # System flags
    is_default = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)  # Can't be deleted
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['team', 'slug']
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """Individual permissions"""
    PERMISSION_CATEGORIES = (
        ('project', 'Project'),
        ('design', 'Design'),
        ('asset', 'Asset'),
        ('team', 'Team'),
        ('billing', 'Billing'),
        ('export', 'Export'),
        ('comment', 'Comment'),
        ('admin', 'Admin'),
    )
    
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=PERMISSION_CATEGORIES)
    
    # Hierarchy
    implies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='implied_by')
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category}: {self.name}"


class RolePermission(models.Model):
    """Permission assignments to roles"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    # Scope
    allow = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['role', 'permission']
    
    def __str__(self):
        action = "Allow" if self.allow else "Deny"
        return f"{self.role.name}: {action} {self.permission.codename}"


class UserRole(models.Model):
    """Role assignments to users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_assignments')
    
    # Scope
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    
    # Assignment metadata
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='role_assignments_made')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'role', 'team', 'project']
    
    def __str__(self):
        scope = self.project or self.team or "Global"
        return f"{self.user.username} - {self.role.name} ({scope})"


class ProjectPermission(models.Model):
    """Direct permission assignments at project level"""
    PERMISSION_LEVELS = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('commenter', 'Commenter'),
        ('viewer', 'Viewer'),
        ('custom', 'Custom'),
    )
    
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='project_permissions')
    email = models.EmailField(blank=True)  # For pending invites
    
    # Permission level
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS, default='viewer')
    custom_permissions = models.JSONField(default=dict)  # For custom level
    
    # Specific permissions
    can_edit = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=True)
    can_export = models.BooleanField(default=False)
    can_share = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_manage_permissions = models.BooleanField(default=False)
    
    # Page-level restrictions
    restricted_pages = models.JSONField(default=list)  # List of page IDs user cannot access
    
    # Invite status
    is_pending = models.BooleanField(default=False)
    invite_token = models.CharField(max_length=100, blank=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invites_sent')
    invited_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['project', 'user']
    
    def __str__(self):
        return f"{self.user or self.email} - {self.permission_level} on {self.project}"


class PagePermission(models.Model):
    """Page-level permissions within a project"""
    page_id = models.CharField(max_length=100)  # Page ID within project
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='page_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_permissions')
    
    # Permissions
    can_view = models.BooleanField(default=True)
    can_edit = models.BooleanField(default=False)
    can_comment = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['page_id', 'project', 'user']
    
    def __str__(self):
        return f"{self.user.username} on page {self.page_id}"


class BranchProtection(models.Model):
    """Protection rules for design branches"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='branch_protections')
    branch_pattern = models.CharField(max_length=255)  # glob pattern like "main" or "release/*"
    
    # Protection settings
    require_review = models.BooleanField(default=False)
    required_reviewers = models.IntegerField(default=1)
    
    dismiss_stale_reviews = models.BooleanField(default=True)
    require_owner_review = models.BooleanField(default=False)
    
    # Merge restrictions
    allowed_merge_roles = models.ManyToManyField(Role, blank=True, related_name='can_merge_branches')
    allowed_merge_users = models.ManyToManyField(User, blank=True, related_name='can_merge_branches')
    
    # Push restrictions
    allow_force_push = models.BooleanField(default=False)
    allowed_push_roles = models.ManyToManyField(Role, blank=True, related_name='can_push_branches')
    allowed_push_users = models.ManyToManyField(User, blank=True, related_name='can_push_branches')
    
    # Status checks
    require_status_checks = models.BooleanField(default=False)
    required_checks = models.JSONField(default=list)  # List of required check names
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['branch_pattern']
    
    def __str__(self):
        return f"Protection for {self.branch_pattern} in {self.project}"


class AccessLog(models.Model):
    """Audit log for permission-related actions"""
    ACTION_TYPES = (
        ('view', 'View'),
        ('edit', 'Edit'),
        ('export', 'Export'),
        ('share', 'Share'),
        ('permission_change', 'Permission Change'),
        ('role_assign', 'Role Assignment'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    
    # Target
    target_type = models.CharField(max_length=50)  # project, page, asset, etc.
    target_id = models.CharField(max_length=100)
    target_name = models.CharField(max_length=255, blank=True)
    
    # Details
    details = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.target_type}"


class PermissionTemplate(models.Model):
    """Templates for quick permission setup"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Template owner
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Permission settings
    permission_level = models.CharField(max_length=20, default='viewer')
    custom_permissions = models.JSONField(default=dict)
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ShareLink(models.Model):
    """Shareable links with permission settings"""
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='share_links')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Link
    token = models.CharField(max_length=100, unique=True)
    
    # Permissions
    permission_level = models.CharField(max_length=20, default='viewer')
    can_comment = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    
    # Restrictions
    password = models.CharField(max_length=255, blank=True)  # Hashed
    allowed_domains = models.JSONField(default=list)  # Email domains
    max_uses = models.IntegerField(null=True, blank=True)
    use_count = models.IntegerField(default=0)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Pages
    allowed_pages = models.JSONField(default=list)  # Empty = all pages
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Share link for {self.project.name}"

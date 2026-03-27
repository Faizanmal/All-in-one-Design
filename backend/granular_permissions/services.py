from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.db.models import Q
from .models import (
    Role, Permission, UserRole, ProjectPermission,
    PagePermission, BranchProtection, AccessLog, ShareLink
)


class PermissionChecker:
    """
    Enterprise Policy Enforcement Engine (Zanzibar-inspired structure).
    Uses Redis to perform instantaneous Authorization checks without hitting the database on every check.
    """
    
    # Permission level hierarchy
    PERMISSION_HIERARCHY = {
        'owner': ['admin', 'editor', 'commenter', 'viewer'],
        'admin': ['editor', 'commenter', 'viewer'],
        'editor': ['commenter', 'viewer'],
        'commenter': ['viewer'],
        'viewer': [],
    }

    def __init__(self, user: User):
        from django.core.cache import cache
        self.user = user
        self.cache = cache
        self.ttl = 60 * 15 # 15 minutes TTL for permission tuples

    def _get_cache_key(self, resource_type: str, resource_id: str, permission: str) -> str:
        return f"authz:{self.user.id}:{resource_type}:{resource_id}:{permission}"
    
    def has_project_permission(
        self,
        project,
        permission: str,
        page_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission on project or page using high-speed distributed cache"""
        if project.owner_id == self.user.id:
            return True

        # Construct Zanzibar-style tuple cache key
        target_id = page_id if page_id else str(project.id)
        target_type = "page" if page_id else "project"
        cache_key = self._get_cache_key(target_type, target_id, permission)
        
        # O(1) Redis Lookup
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Cache Miss - Compute Permission Tuple mathematically
        has_perm = self._compute_project_permission(project, permission, page_id)
        
        # Store in Redis
        self.cache.set(cache_key, has_perm, self.ttl)
        return has_perm

    def _compute_project_permission(self, project, permission: str, page_id: Optional[str]) -> bool:
        """Heavy duty computation that resolves the permission graph through PG"""
        try:
            # Query optimized to prefetch efficiently
            perm = ProjectPermission.objects.select_related('project').get(project=project, user=self.user)
        except ProjectPermission.DoesNotExist:
            return self._check_role_permission(project, permission)
        
        if not self._check_permission_level(perm.permission_level, permission):
            return False
        
        if page_id and page_id in perm.restricted_pages:
            return self._check_page_permission(project, page_id, permission)
        
        return True
    
    def _check_permission_level(self, level: str, permission: str) -> bool:
        permission_map = {
            'view': ['owner', 'admin', 'editor', 'commenter', 'viewer'],
            'comment': ['owner', 'admin', 'editor', 'commenter'],
            'edit': ['owner', 'admin', 'editor'],
            'export': ['owner', 'admin', 'editor'],
            'share': ['owner', 'admin'],
            'delete': ['owner', 'admin'],
            'manage_permissions': ['owner', 'admin'],
        }
        return level in permission_map.get(permission, [])
    
    def _check_page_permission(self, project, page_id: str, permission: str) -> bool:
        try:
            page_perm = PagePermission.objects.get(project=project, page_id=page_id, user=self.user)
        except PagePermission.DoesNotExist:
            return False
            
        mapping = {'view': page_perm.can_view, 'edit': page_perm.can_edit, 'comment': page_perm.can_comment}
        return mapping.get(permission, False)
    
    def _check_role_permission(self, project, permission: str) -> bool:
        # Heavily optimized bulk role check query
        return UserRole.objects.filter(
            user=self.user
        ).filter(
            Q(project=project) | Q(team=project.team_id) | Q(team__isnull=True, project__isnull=True)
        ).filter(
            Q(role__is_admin=True) | 
            Q(role__role_permissions__permission__codename=permission, role__role_permissions__allow=True)
        ).exists()
    
    def get_effective_permissions(self, project) -> Dict[str, Any]:
        """Get all effective permissions for user on project"""
        if project.owner_id == self.user.id:
            return {
                'level': 'owner',
                'can_view': True, 'can_edit': True, 'can_comment': True,
                'can_export': True, 'can_share': True, 'can_delete': True,
                'can_manage_permissions': True,
            }
        
        cache_key = self._get_cache_key("project", str(project.id), "effective_perms")
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        try:
            perm = ProjectPermission.objects.get(project=project, user=self.user)
            result = {
                'level': perm.permission_level,
                'can_view': True,
                'can_edit': perm.can_edit,
                'can_comment': perm.can_comment,
                'can_export': perm.can_export,
                'can_share': perm.can_share,
                'can_delete': perm.can_delete,
                'can_manage_permissions': perm.can_manage_permissions,
                'restricted_pages': perm.restricted_pages,
            }
        except ProjectPermission.DoesNotExist:
            result = {
                'level': 'none',
                'can_view': False, 'can_edit': False, 'can_comment': False,
                'can_export': False, 'can_share': False, 'can_delete': False,
                'can_manage_permissions': False,
            }
            
        self.cache.set(cache_key, result, self.ttl)
        return result
    
    def can_merge_branch(self, project, branch: str) -> bool:
        """Check if user can merge to protected branch"""
        protections = BranchProtection.objects.filter(
            project=project,
            is_active=True
        )
        
        for protection in protections:
            if self._match_branch_pattern(branch, protection.branch_pattern):
                # Check if user is allowed
                if self.user in protection.allowed_merge_users.all():
                    return True
                
                # Check if user has allowed role
                user_roles = UserRole.objects.filter(user=self.user).values_list('role', flat=True)
                if protection.allowed_merge_roles.filter(id__in=user_roles).exists():
                    return True
                
                return False
        
        return True  # No protection, allow merge
    
    def _match_branch_pattern(self, branch: str, pattern: str) -> bool:
        """Match branch name against pattern"""
        import fnmatch
        return fnmatch.fnmatch(branch, pattern)


class PermissionManager:
    """Service for managing permissions"""
    
    @staticmethod
    def grant_project_permission(
        project,
        user: User,
        level: str,
        granted_by: User,
        expires_at=None
    ) -> ProjectPermission:
        """Grant project permission to user"""
        
        # Define permission flags based on level
        level_permissions = {
            'owner': {
                'can_edit': True,
                'can_comment': True,
                'can_export': True,
                'can_share': True,
                'can_delete': True,
                'can_manage_permissions': True,
            },
            'admin': {
                'can_edit': True,
                'can_comment': True,
                'can_export': True,
                'can_share': True,
                'can_delete': True,
                'can_manage_permissions': True,
            },
            'editor': {
                'can_edit': True,
                'can_comment': True,
                'can_export': True,
                'can_share': False,
                'can_delete': False,
                'can_manage_permissions': False,
            },
            'commenter': {
                'can_edit': False,
                'can_comment': True,
                'can_export': False,
                'can_share': False,
                'can_delete': False,
                'can_manage_permissions': False,
            },
            'viewer': {
                'can_edit': False,
                'can_comment': False,
                'can_export': False,
                'can_share': False,
                'can_delete': False,
                'can_manage_permissions': False,
            },
        }
        
        perms = level_permissions.get(level, level_permissions['viewer'])
        
        perm, created = ProjectPermission.objects.update_or_create(
            project=project,
            user=user,
            defaults={
                'permission_level': level,
                'expires_at': expires_at,
                **perms
            }
        )
        
        # Log the action
        AccessLog.objects.create(
            user=granted_by,
            action='permission_change',
            target_type='project',
            target_id=str(project.id),
            target_name=project.name,
            details={
                'granted_to': user.username,
                'level': level,
            }
        )
        
        return perm
    
    @staticmethod
    def revoke_project_permission(project, user: User, revoked_by: User):
        """Revoke project permission from user"""
        ProjectPermission.objects.filter(project=project, user=user).delete()
        
        # Log the action
        AccessLog.objects.create(
            user=revoked_by,
            action='permission_change',
            target_type='project',
            target_id=str(project.id),
            target_name=project.name,
            details={
                'revoked_from': user.username,
                'action': 'revoke',
            }
        )
    
    @staticmethod
    def assign_role(
        user: User,
        role: Role,
        assigned_by: User,
        team=None,
        project=None,
        expires_at=None
    ) -> UserRole:
        """Assign role to user"""
        user_role, created = UserRole.objects.update_or_create(
            user=user,
            role=role,
            team=team,
            project=project,
            defaults={
                'assigned_by': assigned_by,
                'expires_at': expires_at,
            }
        )
        
        # Log the action
        AccessLog.objects.create(
            user=assigned_by,
            action='role_assign',
            target_type='user',
            target_id=str(user.id),
            target_name=user.username,
            details={
                'role': role.name,
                'scope': str(project or team or 'global'),
            }
        )
        
        return user_role
    
    @staticmethod
    def create_share_link(
        project,
        created_by: User,
        permission_level: str = 'viewer',
        **kwargs
    ) -> ShareLink:
        """Create a share link for project"""
        from .models import ShareLink
        import secrets
        
        token = secrets.token_urlsafe(32)
        
        link = ShareLink.objects.create(
            project=project,
            created_by=created_by,
            token=token,
            permission_level=permission_level,
            **kwargs
        )
        
        return link
    
    @staticmethod
    def validate_share_link(token: str) -> Optional[Dict[str, Any]]:
        """Validate and return share link info"""
        from .models import ShareLink
        from django.utils import timezone
        
        try:
            link = ShareLink.objects.get(token=token, is_active=True)
        except ShareLink.DoesNotExist:
            return None
        
        # Check expiration
        if link.expires_at and link.expires_at < timezone.now():
            return None
        
        # Check usage limit
        if link.max_uses and link.use_count >= link.max_uses:
            return None
        
        return {
            'project_id': link.project_id,
            'permission_level': link.permission_level,
            'can_comment': link.can_comment,
            'can_export': link.can_export,
            'allowed_pages': link.allowed_pages,
            'requires_password': bool(link.password),
        }


def setup_default_permissions():
    """Create default permissions and roles"""
    
    # Create default permissions
    default_permissions = [
        # Project permissions
        ('project.view', 'View Project', 'project'),
        ('project.edit', 'Edit Project', 'project'),
        ('project.delete', 'Delete Project', 'project'),
        ('project.share', 'Share Project', 'project'),
        ('project.export', 'Export Project', 'project'),
        
        # Design permissions
        ('design.view', 'View Design', 'design'),
        ('design.edit', 'Edit Design', 'design'),
        ('design.comment', 'Comment on Design', 'design'),
        
        # Asset permissions
        ('asset.view', 'View Assets', 'asset'),
        ('asset.upload', 'Upload Assets', 'asset'),
        ('asset.delete', 'Delete Assets', 'asset'),
        
        # Team permissions
        ('team.view', 'View Team', 'team'),
        ('team.manage_members', 'Manage Team Members', 'team'),
        ('team.manage_settings', 'Manage Team Settings', 'team'),
        
        # Admin permissions
        ('admin.manage_roles', 'Manage Roles', 'admin'),
        ('admin.view_logs', 'View Audit Logs', 'admin'),
    ]
    
    for codename, name, category in default_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            defaults={'name': name, 'category': category}
        )
    
    # Create default roles
    default_roles = [
        {
            'name': 'Owner',
            'slug': 'owner',
            'is_admin': True,
            'is_system': True,
            'color': '#DC2626',
        },
        {
            'name': 'Admin',
            'slug': 'admin',
            'is_admin': True,
            'can_manage_members': True,
            'is_system': True,
            'color': '#7C3AED',
        },
        {
            'name': 'Editor',
            'slug': 'editor',
            'is_system': True,
            'color': '#2563EB',
        },
        {
            'name': 'Commenter',
            'slug': 'commenter',
            'is_system': True,
            'color': '#059669',
        },
        {
            'name': 'Viewer',
            'slug': 'viewer',
            'is_default': True,
            'is_system': True,
            'color': '#6B7280',
        },
    ]
    
    for role_data in default_roles:
        Role.objects.get_or_create(
            slug=role_data['slug'],
            role_type='system',
            team=None,
            defaults=role_data
        )

from rest_framework import permissions
from .models import TeamMembership
import logging

logger = logging.getLogger('teams')


class IsTeamMember(permissions.BasePermission):
    """Permission to check if user is a team member"""
    
    def has_object_permission(self, request, view, obj):
        # For Team objects
        if hasattr(obj, 'members'):
            return obj.members.filter(id=request.user.id).exists()
        
        # For objects with team FK
        if hasattr(obj, 'team'):
            return obj.team.members.filter(id=request.user.id).exists()
        
        return False


class IsTeamAdmin(permissions.BasePermission):
    """Permission to check if user is team admin or owner"""
    
    def has_object_permission(self, request, view, obj):
        team = obj if hasattr(obj, 'members') else obj.team
        
        try:
            membership = TeamMembership.objects.get(
                team=team,
                user=request.user,
                is_active=True
            )
            return membership.role in ['owner', 'admin']
        except TeamMembership.DoesNotExist:
            return False


class IsTeamOwner(permissions.BasePermission):
    """Permission to check if user is team owner"""
    
    def has_object_permission(self, request, view, obj):
        team = obj if hasattr(obj, 'owner') else obj.team
        return team.owner == request.user


class CanCreateProject(permissions.BasePermission):
    """Permission to check if user can create projects in team"""
    
    def has_object_permission(self, request, view, obj):
        try:
            membership = TeamMembership.objects.get(
                team=obj.team,
                user=request.user,
                is_active=True
            )
            return membership.can_create_projects
        except TeamMembership.DoesNotExist:
            return False


class CanEditProject(permissions.BasePermission):
    """Permission to check if user can edit projects"""
    
    def has_object_permission(self, request, view, obj):
        team_project = obj.team_associations.first()
        if not team_project:
            return obj.user == request.user
        
        try:
            membership = TeamMembership.objects.get(
                team=team_project.team,
                user=request.user,
                is_active=True
            )
            return membership.can_edit_projects
        except TeamMembership.DoesNotExist:
            return False


class CanDeleteProject(permissions.BasePermission):
    """Permission to check if user can delete projects"""
    
    def has_object_permission(self, request, view, obj):
        team_project = obj.team_associations.first()
        if not team_project:
            return obj.user == request.user
        
        try:
            membership = TeamMembership.objects.get(
                team=team_project.team,
                user=request.user,
                is_active=True
            )
            return membership.can_delete_projects
        except TeamMembership.DoesNotExist:
            return False


class CanInviteMembers(permissions.BasePermission):
    """Permission to check if user can invite members to the team"""
    
    def has_object_permission(self, request, view, obj):
        team = obj if hasattr(obj, 'members') else getattr(obj, 'team', None)
        if not team:
            return False
        
        try:
            membership = TeamMembership.objects.get(
                team=team,
                user=request.user,
                is_active=True
            )
            return membership.can_invite_members
        except TeamMembership.DoesNotExist:
            return False


class CanManageMembers(permissions.BasePermission):
    """Permission to check if user can manage (update/remove) members"""
    
    def has_object_permission(self, request, view, obj):
        team = obj if hasattr(obj, 'members') else getattr(obj, 'team', None)
        if not team:
            return False
        
        try:
            membership = TeamMembership.objects.get(
                team=team,
                user=request.user,
                is_active=True
            )
            return membership.can_manage_members
        except TeamMembership.DoesNotExist:
            return False


# --- Utility Functions ---

def get_user_team_permissions(user, team_id: int) -> dict:
    """
    Get a complete permissions summary for a user in a team.
    Returns role, all granular permissions, and membership status.
    """
    try:
        membership = TeamMembership.objects.select_related('team').get(
            team_id=team_id,
            user=user,
            is_active=True
        )
        return {
            'is_member': True,
            'role': membership.role,
            'role_display': membership.get_role_display(),
            'permissions': {
                'can_create_projects': membership.can_create_projects,
                'can_edit_projects': membership.can_edit_projects,
                'can_delete_projects': membership.can_delete_projects,
                'can_invite_members': membership.can_invite_members,
                'can_manage_members': membership.can_manage_members,
            },
            'joined_at': membership.joined_at.isoformat(),
        }
    except TeamMembership.DoesNotExist:
        return {
            'is_member': False,
            'role': None,
            'role_display': None,
            'permissions': {},
            'joined_at': None,
        }


def log_team_activity(team_id: int, user, action: str,
                      project=None, description: str = '', metadata: dict = None):
    """
    Log an activity to the team audit trail.
    
    Usage:
        log_team_activity(team.id, request.user, 'project_created',
                         project=project, description='Created new landing page')
    """
    from .models import TeamActivity
    try:
        TeamActivity.objects.create(
            team_id=team_id,
            user=user,
            action=action,
            project=project,
            description=description,
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Failed to log team activity: {e}")


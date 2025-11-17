from rest_framework import permissions
from .models import TeamMembership


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

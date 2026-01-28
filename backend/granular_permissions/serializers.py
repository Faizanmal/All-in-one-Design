from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Role, Permission, RolePermission, UserRole, ProjectPermission,
    PagePermission, BranchProtection, AccessLog, PermissionTemplate, ShareLink
)


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for permissions"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description', 'category']


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for role permissions"""
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'permission', 'permission_name', 'permission_codename', 'allow']


class RoleListSerializer(serializers.ModelSerializer):
    """Serializer for role listings"""
    permission_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'slug', 'description', 'role_type',
            'is_admin', 'color', 'icon', 'is_default', 'is_system',
            'permission_count', 'member_count'
        ]
    
    def get_permission_count(self, obj) -> int:
        return obj.role_permissions.filter(allow=True).count()
    
    def get_member_count(self, obj) -> int:
        return obj.user_assignments.count()


class RoleSerializer(serializers.ModelSerializer):
    """Full serializer for roles"""
    permissions = RolePermissionSerializer(source='role_permissions', many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'slug', 'description', 'role_type', 'team',
            'is_admin', 'can_manage_members', 'color', 'icon',
            'is_default', 'is_system', 'permissions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_system', 'created_at', 'updated_at']


class RoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating roles"""
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = [
            'name', 'slug', 'description', 'role_type', 'team',
            'is_admin', 'can_manage_members', 'color', 'icon',
            'is_default', 'permission_ids'
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for user role assignments"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'role', 'role_name',
            'team', 'team_name', 'project', 'project_name',
            'assigned_by', 'assigned_by_name', 'assigned_at', 'expires_at'
        ]
        read_only_fields = ['assigned_by', 'assigned_at']


class ProjectPermissionSerializer(serializers.ModelSerializer):
    """Serializer for project permissions"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.username', read_only=True)
    
    class Meta:
        model = ProjectPermission
        fields = [
            'id', 'project', 'user', 'user_name', 'email',
            'permission_level', 'custom_permissions',
            'can_edit', 'can_comment', 'can_export', 'can_share',
            'can_delete', 'can_manage_permissions', 'restricted_pages',
            'is_pending', 'invited_by', 'invited_by_name',
            'invited_at', 'accepted_at', 'expires_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'is_pending', 'invite_token', 'invited_by',
            'invited_at', 'accepted_at', 'created_at', 'updated_at'
        ]


class ProjectPermissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating project permissions"""
    
    class Meta:
        model = ProjectPermission
        fields = [
            'project', 'user', 'email', 'permission_level',
            'custom_permissions', 'restricted_pages', 'expires_at'
        ]
    
    def validate(self, data):
        if not data.get('user') and not data.get('email'):
            raise serializers.ValidationError("Either user or email must be provided")
        return data


class PagePermissionSerializer(serializers.ModelSerializer):
    """Serializer for page permissions"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PagePermission
        fields = [
            'id', 'page_id', 'project', 'user', 'user_name',
            'can_view', 'can_edit', 'can_comment', 'created_at'
        ]
        read_only_fields = ['created_at']


class BranchProtectionSerializer(serializers.ModelSerializer):
    """Serializer for branch protection rules"""
    
    class Meta:
        model = BranchProtection
        fields = [
            'id', 'project', 'branch_pattern',
            'require_review', 'required_reviewers',
            'dismiss_stale_reviews', 'require_owner_review',
            'allowed_merge_roles', 'allowed_merge_users',
            'allow_force_push', 'allowed_push_roles', 'allowed_push_users',
            'require_status_checks', 'required_checks',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AccessLogSerializer(serializers.ModelSerializer):
    """Serializer for access logs"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AccessLog
        fields = [
            'id', 'user', 'user_name', 'action',
            'target_type', 'target_id', 'target_name',
            'details', 'ip_address', 'success', 'error_message',
            'created_at'
        ]


class PermissionTemplateSerializer(serializers.ModelSerializer):
    """Serializer for permission templates"""
    
    class Meta:
        model = PermissionTemplate
        fields = [
            'id', 'name', 'description', 'team',
            'permission_level', 'custom_permissions', 'is_default',
            'created_at'
        ]
        read_only_fields = ['created_at']


class ShareLinkSerializer(serializers.ModelSerializer):
    """Serializer for share links"""
    url = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ShareLink
        fields = [
            'id', 'project', 'token', 'url',
            'permission_level', 'can_comment', 'can_export',
            'password', 'allowed_domains', 'max_uses', 'use_count',
            'expires_at', 'allowed_pages', 'is_active',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['token', 'use_count', 'created_by', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_url(self, obj) -> str:
        return f"/share/{obj.token}"


class ShareLinkCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating share links"""
    
    class Meta:
        model = ShareLink
        fields = [
            'project', 'permission_level', 'can_comment', 'can_export',
            'password', 'allowed_domains', 'max_uses',
            'expires_at', 'allowed_pages'
        ]


class PermissionCheckSerializer(serializers.Serializer):
    """Serializer for permission checks"""
    has_permission = serializers.BooleanField()
    permission_level = serializers.CharField()
    source = serializers.CharField()


class BulkPermissionUpdateSerializer(serializers.Serializer):
    """Serializer for bulk permission updates"""
    user_ids = serializers.ListField(child=serializers.IntegerField())
    permission_level = serializers.CharField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)


class InviteUserSerializer(serializers.Serializer):
    """Serializer for inviting users"""
    email = serializers.EmailField()
    permission_level = serializers.ChoiceField(
        choices=['admin', 'editor', 'commenter', 'viewer']
    )
    message = serializers.CharField(required=False, allow_blank=True)

from django.contrib import admin
from .models import (
    Role, Permission, RolePermission, UserRole, ProjectPermission,
    PagePermission, BranchProtection, AccessLog, PermissionTemplate, ShareLink
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'role_type', 'team', 'is_admin', 'is_default', 'is_system']
    list_filter = ['role_type', 'is_admin', 'is_default', 'is_system']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'category']
    list_filter = ['category']
    search_fields = ['name', 'codename']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'allow']
    list_filter = ['allow', 'role']
    search_fields = ['role__name', 'permission__name']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'team', 'project', 'assigned_by', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__username', 'role__name']


@admin.register(ProjectPermission)
class ProjectPermissionAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'email', 'permission_level', 'is_pending', 'created_at']
    list_filter = ['permission_level', 'is_pending']
    search_fields = ['project__name', 'user__username', 'email']


@admin.register(PagePermission)
class PagePermissionAdmin(admin.ModelAdmin):
    list_display = ['page_id', 'project', 'user', 'can_view', 'can_edit', 'can_comment']
    list_filter = ['can_view', 'can_edit', 'can_comment']
    search_fields = ['project__name', 'user__username']


@admin.register(BranchProtection)
class BranchProtectionAdmin(admin.ModelAdmin):
    list_display = ['project', 'branch_pattern', 'require_review', 'required_reviewers', 'is_active']
    list_filter = ['require_review', 'is_active']
    search_fields = ['project__name', 'branch_pattern']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'target_type', 'target_name', 'success', 'created_at']
    list_filter = ['action', 'target_type', 'success', 'created_at']
    search_fields = ['user__username', 'target_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(PermissionTemplate)
class PermissionTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'permission_level', 'is_default']
    list_filter = ['permission_level', 'is_default']
    search_fields = ['name']


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ['project', 'permission_level', 'use_count', 'max_uses', 'is_active', 'created_at']
    list_filter = ['permission_level', 'is_active', 'created_at']
    search_fields = ['project__name', 'token']
    readonly_fields = ['token', 'use_count']

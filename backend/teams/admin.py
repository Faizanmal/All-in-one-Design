from django.contrib import admin
from .models import Team, TeamMembership, TeamInvitation, TeamProject, Comment, TeamActivity


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'member_count', 'project_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__username']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'member_count', 'project_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'owner')
        }),
        ('Settings', {
            'fields': ('is_active', 'max_members')
        }),
        ('Statistics', {
            'fields': ('member_count', 'project_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'team__name']
    readonly_fields = ['joined_at', 'updated_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('team', 'user', 'role', 'is_active')
        }),
        ('Permissions', {
            'fields': (
                'can_create_projects',
                'can_edit_projects',
                'can_delete_projects',
                'can_invite_members',
                'can_manage_members'
            )
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'team', 'invited_by', 'role', 'status', 'created_at', 'expires_at']
    list_filter = ['status', 'role', 'created_at']
    search_fields = ['email', 'team__name', 'invited_by__username']
    readonly_fields = ['token', 'created_at', 'responded_at']
    
    fieldsets = (
        ('Invitation', {
            'fields': ('team', 'email', 'invited_by', 'role')
        }),
        ('Details', {
            'fields': ('message', 'status', 'token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'responded_at')
        })
    )


@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    list_display = ['project', 'team', 'is_shared', 'created_by', 'created_at']
    list_filter = ['is_shared', 'created_at']
    search_fields = ['project__name', 'team__name']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'is_resolved', 'reply_count', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['content', 'user__username', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'reply_count']
    filter_horizontal = ['mentions']
    
    fieldsets = (
        ('Comment', {
            'fields': ('project', 'user', 'content', 'parent')
        }),
        ('Position', {
            'fields': ('position_x', 'position_y'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
        ('Mentions', {
            'fields': ('mentions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TeamActivity)
class TeamActivityAdmin(admin.ModelAdmin):
    list_display = ['team', 'user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['team__name', 'user__username', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Activity', {
            'fields': ('team', 'user', 'action', 'description')
        }),
        ('Related Objects', {
            'fields': ('project', 'comment'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        })
    )

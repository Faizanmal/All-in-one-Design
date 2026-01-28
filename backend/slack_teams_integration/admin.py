from django.contrib import admin
from .models import (
    SlackWorkspace, SlackChannel, MicrosoftTeamsWorkspace, TeamsChannel,
    IntegrationMessage, BotCommand, NotificationPreference
)


@admin.register(SlackWorkspace)
class SlackWorkspaceAdmin(admin.ModelAdmin):
    list_display = ['workspace_name', 'user', 'is_active', 'connected_at']
    list_filter = ['is_active', 'connected_at']
    search_fields = ['workspace_name', 'user__username']
    readonly_fields = ['connected_at', 'updated_at']


@admin.register(SlackChannel)
class SlackChannelAdmin(admin.ModelAdmin):
    list_display = ['channel_name', 'workspace', 'project', 'is_active']
    list_filter = ['is_active', 'notify_on_comment', 'notify_on_update']
    search_fields = ['channel_name', 'workspace__workspace_name']


@admin.register(MicrosoftTeamsWorkspace)
class MicrosoftTeamsWorkspaceAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'user', 'is_active', 'connected_at']
    list_filter = ['is_active', 'connected_at']
    search_fields = ['team_name', 'user__username']
    readonly_fields = ['connected_at', 'updated_at']


@admin.register(TeamsChannel)
class TeamsChannelAdmin(admin.ModelAdmin):
    list_display = ['channel_name', 'workspace', 'project', 'is_active']
    list_filter = ['is_active', 'notify_on_comment', 'notify_on_update']
    search_fields = ['channel_name', 'workspace__team_name']


@admin.register(IntegrationMessage)
class IntegrationMessageAdmin(admin.ModelAdmin):
    list_display = ['platform', 'message_type', 'project', 'sent', 'created_at']
    list_filter = ['platform', 'message_type', 'sent', 'created_at']
    search_fields = ['project__name']
    readonly_fields = ['created_at']


@admin.register(BotCommand)
class BotCommandAdmin(admin.ModelAdmin):
    list_display = ['platform', 'command', 'user', 'response_sent', 'created_at']
    list_filter = ['platform', 'response_sent', 'created_at']
    readonly_fields = ['created_at', 'processed_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'slack_enabled', 'teams_enabled', 'quiet_hours_enabled']
    list_filter = ['slack_enabled', 'teams_enabled', 'quiet_hours_enabled']
    search_fields = ['user__username']

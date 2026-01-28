from django.contrib import admin
from .models import OfflineProject, SyncQueue, OfflineSettings, SyncLog, CachedAsset


@admin.register(OfflineProject)
class OfflineProjectAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'is_enabled', 'needs_sync', 'last_synced']
    list_filter = ['is_enabled', 'needs_sync']
    search_fields = ['project__name', 'user__username']


@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ['operation', 'entity_type', 'entity_id', 'status', 'created_at']
    list_filter = ['operation', 'entity_type', 'status']
    search_fields = ['entity_id', 'user__username']


@admin.register(OfflineSettings)
class OfflineSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'max_offline_storage', 'auto_sync_on_connect']
    search_fields = ['user__username']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'started_at', 'success', 'items_synced', 'items_failed']
    list_filter = ['success', 'started_at']
    search_fields = ['user__username']


@admin.register(CachedAsset)
class CachedAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_type', 'user', 'file_size', 'last_accessed']
    list_filter = ['asset_type', 'last_accessed']
    search_fields = ['original_url', 'user__username']

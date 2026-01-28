from django.contrib import admin
from .models import (
    AssetFolder, AssetTag, EnhancedAsset, AssetCollection,
    AssetUsageLog, CDNIntegration, BulkOperation, UnusedAssetReport
)


@admin.register(AssetFolder)
class AssetFolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'parent', 'is_smart', 'asset_count']
    list_filter = ['is_smart', 'created_at']
    search_fields = ['name', 'path']


@admin.register(AssetTag)
class AssetTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'ai_generated', 'created_at']
    list_filter = ['ai_generated', 'created_at']
    search_fields = ['name']


@admin.register(EnhancedAsset)
class EnhancedAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'user', 'usage_count', 'is_favorite', 'created_at']
    list_filter = ['asset_type', 'is_favorite', 'is_archived', 'created_at']
    search_fields = ['name', 'description', 'ai_description']
    readonly_fields = ['ai_tags', 'ai_colors', 'ai_objects', 'usage_count', 'last_used']


@admin.register(AssetCollection)
class AssetCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description']


@admin.register(AssetUsageLog)
class AssetUsageLogAdmin(admin.ModelAdmin):
    list_display = ['asset', 'project', 'user', 'usage_type', 'added_at']
    list_filter = ['usage_type', 'added_at']


@admin.register(CDNIntegration)
class CDNIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'user', 'is_active', 'is_default']
    list_filter = ['provider', 'is_active', 'is_default']
    search_fields = ['name']


@admin.register(BulkOperation)
class BulkOperationAdmin(admin.ModelAdmin):
    list_display = ['operation', 'user', 'status', 'total_assets', 'created_at']
    list_filter = ['operation', 'status', 'created_at']


@admin.register(UnusedAssetReport)
class UnusedAssetReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_unused', 'total_size', 'generated_at']
    list_filter = ['generated_at']

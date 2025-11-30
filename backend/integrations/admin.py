from django.contrib import admin
from .models import ExternalServiceConnection, ImportedAsset, FigmaImport, StockAssetSearch


@admin.register(ExternalServiceConnection)
class ExternalServiceConnectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'is_active', 'last_synced', 'created_at']
    list_filter = ['service', 'is_active']
    search_fields = ['user__username', 'service_username']


@admin.register(ImportedAsset)
class ImportedAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'source', 'asset_type', 'created_at']
    list_filter = ['source', 'asset_type']
    search_fields = ['name', 'description', 'user__username']


@admin.register(FigmaImport)
class FigmaImportAdmin(admin.ModelAdmin):
    list_display = ['figma_file_name', 'user', 'status', 'created_at', 'completed_at']
    list_filter = ['status']
    search_fields = ['figma_file_name', 'user__username']


@admin.register(StockAssetSearch)
class StockAssetSearchAdmin(admin.ModelAdmin):
    list_display = ['query', 'provider', 'user', 'results_count', 'created_at']
    list_filter = ['provider']
    search_fields = ['query', 'user__username']

from django.contrib import admin
from .models import VideoAsset, GIFAsset, LottieAsset, MediaPlacement, AnimatedExport

@admin.register(VideoAsset)
class VideoAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'user', 'duration', 'created_at']
    list_filter = ['source_type', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(GIFAsset)
class GIFAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'frame_count', 'duration', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(LottieAsset)
class LottieAssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'duration', 'frame_rate', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(AnimatedExport)
class AnimatedExportAdmin(admin.ModelAdmin):
    list_display = ['project', 'export_format', 'status', 'progress', 'created_at']
    list_filter = ['export_format', 'status', 'created_at']

from django.contrib import admin
from .models import (
    PDFExportPreset, PDFExport, PrintProfile,
    SpreadView, ImpositionLayout, PDFTemplate
)


@admin.register(PDFExportPreset)
class PDFExportPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'paper_size', 'color_mode', 'quality', 'is_default']
    list_filter = ['paper_size', 'color_mode', 'bleed_enabled', 'pdf_standard']
    search_fields = ['name', 'created_by__username']


@admin.register(PDFExport)
class PDFExportAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'user', 'status', 'progress', 'page_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['project__name', 'user__username']
    readonly_fields = ['file_url', 'file_size', 'page_count', 'started_at', 'completed_at']


@admin.register(PrintProfile)
class PrintProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'profile_type', 'recommended_dpi', 'recommended_color_mode', 'is_active']
    list_filter = ['profile_type', 'is_active']
    search_fields = ['name']


@admin.register(SpreadView)
class SpreadViewAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'spread_type', 'order']
    list_filter = ['spread_type']
    search_fields = ['name', 'project__name']


@admin.register(ImpositionLayout)
class ImpositionLayoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'imposition_type', 'sheet_width', 'sheet_height', 'columns', 'rows', 'is_active']
    list_filter = ['imposition_type', 'is_active']
    search_fields = ['name']


@admin.register(PDFTemplate)
class PDFTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'header_enabled', 'footer_enabled', 'page_numbers', 'is_default']
    list_filter = ['header_enabled', 'footer_enabled', 'page_numbers']
    search_fields = ['name', 'created_by__username']

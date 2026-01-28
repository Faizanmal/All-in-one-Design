from django.contrib import admin
from .models import (
    ExportConfiguration, CodeExport, DesignSpec,
    ComponentLibrary, HandoffAnnotation
)


@admin.register(ExportConfiguration)
class ExportConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'framework', 'styling', 'is_default', 'created_at']
    list_filter = ['framework', 'styling', 'is_default', 'typescript_enabled']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CodeExport)
class CodeExportAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'user', 'framework', 'status', 'file_count', 'created_at']
    list_filter = ['status', 'framework', 'styling', 'created_at']
    search_fields = ['project__name', 'user__username']
    readonly_fields = ['created_at', 'completed_at']


@admin.register(DesignSpec)
class DesignSpecAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'component', 'auto_generated', 'version', 'created_at']
    list_filter = ['auto_generated', 'created_at']
    search_fields = ['name', 'project__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComponentLibrary)
class ComponentLibraryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'version', 'default_framework', 'is_public', 'created_at']
    list_filter = ['is_public', 'default_framework', 'created_at']
    search_fields = ['name', 'user__username', 'package_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HandoffAnnotation)
class HandoffAnnotationAdmin(admin.ModelAdmin):
    list_display = ['title', 'annotation_type', 'project', 'created_by', 'resolved', 'created_at']
    list_filter = ['annotation_type', 'resolved', 'created_at']
    search_fields = ['title', 'content', 'project__name']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']

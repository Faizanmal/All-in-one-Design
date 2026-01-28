from django.contrib import admin
from .models import (
    DesignSystem, DesignToken, ComponentDefinition, ComponentVariant,
    StyleGuide, DocumentationPage, DesignSystemExport, DesignSystemSync
)


@admin.register(DesignSystem)
class DesignSystemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'version', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DesignToken)
class DesignTokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'design_system', 'category', 'token_type', 'is_deprecated']
    list_filter = ['category', 'token_type', 'is_deprecated']
    search_fields = ['name', 'description', 'design_system__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ComponentDefinition)
class ComponentDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'design_system', 'category', 'status', 'version']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['name', 'description', 'design_system__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ComponentVariant)
class ComponentVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'component', 'order']
    list_filter = ['component__design_system']
    search_fields = ['name', 'component__name']


@admin.register(StyleGuide)
class StyleGuideAdmin(admin.ModelAdmin):
    list_display = ['design_system', 'created_at', 'updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DocumentationPage)
class DocumentationPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'design_system', 'parent', 'is_published', 'order']
    list_filter = ['is_published', 'design_system']
    search_fields = ['title', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(DesignSystemExport)
class DesignSystemExportAdmin(admin.ModelAdmin):
    list_display = ['design_system', 'export_format', 'status', 'created_at']
    list_filter = ['export_format', 'status', 'created_at']
    readonly_fields = ['id', 'created_at', 'completed_at']


@admin.register(DesignSystemSync)
class DesignSystemSyncAdmin(admin.ModelAdmin):
    list_display = ['design_system', 'source', 'direction', 'status', 'started_at']
    list_filter = ['source', 'status', 'started_at']
    readonly_fields = ['id', 'started_at', 'completed_at']

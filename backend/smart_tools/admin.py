from django.contrib import admin
from .models import (
    SmartSelectionPreset, BatchOperation, RenameTemplate,
    FindReplaceOperation, ResizePreset, SelectionHistory, MagicWand
)


@admin.register(SmartSelectionPreset)
class SmartSelectionPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'preset_type', 'use_count', 'is_favorite', 'is_system']
    list_filter = ['preset_type', 'is_favorite', 'is_system']
    search_fields = ['name', 'user__username']


@admin.register(BatchOperation)
class BatchOperationAdmin(admin.ModelAdmin):
    list_display = ['operation_type', 'user', 'project', 'component_count', 'status', 'created_at']
    list_filter = ['operation_type', 'status', 'created_at']
    search_fields = ['user__username', 'project__name']


@admin.register(RenameTemplate)
class RenameTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'pattern', 'case_transform', 'use_count']
    list_filter = ['case_transform', 'is_favorite']
    search_fields = ['name', 'user__username']


@admin.register(FindReplaceOperation)
class FindReplaceOperationAdmin(admin.ModelAdmin):
    list_display = ['target_type', 'user', 'find_value', 'replace_value', 'replacements_made', 'created_at']
    list_filter = ['target_type', 'scope', 'created_at']
    search_fields = ['user__username', 'find_value']


@admin.register(ResizePreset)
class ResizePresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'resize_mode', 'width', 'height', 'use_count']
    list_filter = ['resize_mode', 'is_favorite']
    search_fields = ['name', 'user__username']


@admin.register(SelectionHistory)
class SelectionHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'component_count', 'action_taken', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'project__name']


@admin.register(MagicWand)
class MagicWandAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'color_tolerance', 'search_scope']
    list_filter = ['search_scope']
    search_fields = ['user__username', 'project__name']

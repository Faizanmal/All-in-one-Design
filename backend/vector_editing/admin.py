from django.contrib import admin
from .models import (
    VectorPath, PathPoint, BooleanOperation, PathOffset,
    VectorPattern, VectorShape, PenToolSession
)


class PathPointInline(admin.TabularInline):
    model = PathPoint
    extra = 0
    fields = ['x', 'y', 'point_type', 'corner_radius', 'order']


@admin.register(VectorPath)
class VectorPathAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'project', 'path_type', 'is_visible', 'created_at']
    list_filter = ['path_type', 'is_visible', 'is_locked', 'created_at']
    search_fields = ['name', 'user__username', 'project__name']
    inlines = [PathPointInline]
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(PathPoint)
class PathPointAdmin(admin.ModelAdmin):
    list_display = ['path', 'x', 'y', 'point_type', 'corner_radius', 'order']
    list_filter = ['point_type']
    search_fields = ['path__name']


@admin.register(BooleanOperation)
class BooleanOperationAdmin(admin.ModelAdmin):
    list_display = ['operation_type', 'user', 'project', 'created_at']
    list_filter = ['operation_type', 'created_at']
    search_fields = ['user__username', 'project__name']
    readonly_fields = ['id', 'created_at']


@admin.register(PathOffset)
class PathOffsetAdmin(admin.ModelAdmin):
    list_display = ['source_path', 'offset_type', 'offset_value', 'created_at']
    list_filter = ['offset_type', 'join_type', 'created_at']


@admin.register(VectorPattern)
class VectorPatternAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'pattern_type', 'is_public', 'created_at']
    list_filter = ['pattern_type', 'is_public', 'created_at']
    search_fields = ['name', 'user__username']


@admin.register(VectorShape)
class VectorShapeAdmin(admin.ModelAdmin):
    list_display = ['name', 'shape_type', 'project', 'x', 'y', 'created_at']
    list_filter = ['shape_type', 'created_at']
    search_fields = ['name', 'project__name']


@admin.register(PenToolSession)
class PenToolSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'is_active', 'is_closed', 'started_at']
    list_filter = ['is_active', 'is_closed', 'started_at']
    search_fields = ['user__username', 'project__name']

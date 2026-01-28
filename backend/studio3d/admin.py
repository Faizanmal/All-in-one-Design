from django.contrib import admin
from .models import Model3D, Scene3D, SceneModel, Prototype3D, ARPreview, Conversion3DTo2D


@admin.register(Model3D)
class Model3DAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'file_format', 'file_size', 'created_at']
    list_filter = ['file_format', 'created_at', 'ar_enabled']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'file_size', 'vertex_count', 'face_count', 
                       'material_count', 'texture_count', 'animation_count',
                       'created_at', 'updated_at']


@admin.register(Scene3D)
class Scene3DAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'project', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(SceneModel)
class SceneModelAdmin(admin.ModelAdmin):
    list_display = ['scene', 'model', 'visible', 'layer', 'created_at']
    list_filter = ['visible', 'created_at']


@admin.register(Prototype3D)
class Prototype3DAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'scene', 'is_public', 'view_count', 'created_at']
    list_filter = ['is_public', 'preview_mode', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['id', 'share_link', 'view_count', 'created_at', 'updated_at']


@admin.register(ARPreview)
class ARPreviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'ar_type', 'is_public', 'created_at']
    list_filter = ['ar_type', 'is_public', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['id', 'share_link', 'created_at', 'updated_at']


@admin.register(Conversion3DTo2D)
class Conversion3DTo2DAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'view', 'output_format', 'status', 'created_at']
    list_filter = ['status', 'view', 'output_format', 'created_at']
    readonly_fields = ['id', 'created_at', 'completed_at']

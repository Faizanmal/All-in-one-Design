from django.contrib import admin
from .models import Project, DesignComponent, ProjectVersion, ExportTemplate, ExportJob


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'project_type', 'is_public', 'created_at', 'updated_at']
    list_filter = ['project_type', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    date_hierarchy = 'created_at'
    filter_horizontal = ['collaborators']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'project_type')
        }),
        ('Canvas Settings', {
            'fields': ('canvas_width', 'canvas_height', 'canvas_background')
        }),
        ('Design Data', {
            'fields': ('design_data',),
            'classes': ('collapse',)
        }),
        ('AI Metadata', {
            'fields': ('ai_prompt', 'color_palette', 'suggested_fonts'),
            'classes': ('collapse',)
        }),
        ('Collaboration', {
            'fields': ('is_public', 'collaborators')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(DesignComponent)
class DesignComponentAdmin(admin.ModelAdmin):
    list_display = ['id', 'component_type', 'project', 'z_index', 'ai_generated', 'created_at']
    list_filter = ['component_type', 'ai_generated', 'created_at']
    search_fields = ['project__name', 'ai_prompt']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProjectVersion)
class ProjectVersionAdmin(admin.ModelAdmin):
    list_display = ['project', 'version_number', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__name', 'created_by__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'format', 'quality', 'optimize', 'is_public', 'use_count', 'created_at']
    list_filter = ['format', 'quality', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'use_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'is_public')
        }),
        ('Export Settings', {
            'fields': ('format', 'quality', 'optimize', 'include_metadata', 'compression')
        }),
        ('Dimensions', {
            'fields': ('width', 'height', 'scale')
        }),
        ('Format Options', {
            'fields': ('format_options',),
            'classes': ('collapse',)
        }),
        ('Usage Stats', {
            'fields': ('use_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'format', 'status', 'progress_display', 'file_size_display', 'created_at']
    list_filter = ['status', 'format', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'started_at', 'completed_at', 'progress_percentage', 'duration']
    filter_horizontal = ['projects']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('user', 'format', 'template', 'status')
        }),
        ('Projects', {
            'fields': ('projects',)
        }),
        ('Progress', {
            'fields': ('total_projects', 'completed_projects', 'failed_projects', 'progress_percentage')
        }),
        ('Output', {
            'fields': ('output_file', 'file_size')
        }),
        ('Errors', {
            'fields': ('error_message', 'error_details'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at', 'duration')
        })
    )
    
    def progress_display(self, obj):
        return f"{obj.progress_percentage}%"
    progress_display.short_description = 'Progress'
    
    def file_size_display(self, obj):
        if obj.file_size == 0:
            return '-'
        # Convert bytes to human readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if obj.file_size < 1024.0:
                return f"{obj.file_size:.2f} {unit}"
            obj.file_size /= 1024.0
        return f"{obj.file_size:.2f} TB"
    file_size_display.short_description = 'File Size'

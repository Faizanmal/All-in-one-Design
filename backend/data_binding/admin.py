from django.contrib import admin
from .models import DataSource, DataVariable, DataBinding, DataCollection, DataTransform

@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'user', 'is_active', 'last_fetched', 'created_at']
    list_filter = ['source_type', 'is_active', 'auth_type']
    search_fields = ['name', 'user__username']

@admin.register(DataVariable)
class DataVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'variable_type', 'project', 'data_source', 'created_at']
    list_filter = ['variable_type']
    search_fields = ['name', 'project__name']

@admin.register(DataBinding)
class DataBindingAdmin(admin.ModelAdmin):
    list_display = ['element_id', 'binding_type', 'variable', 'project']
    list_filter = ['binding_type']

@admin.register(DataCollection)
class DataCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'data_source', 'project', 'page_size']

@admin.register(DataTransform)
class DataTransformAdmin(admin.ModelAdmin):
    list_display = ['name', 'transform_type', 'user', 'created_at']
    list_filter = ['transform_type']

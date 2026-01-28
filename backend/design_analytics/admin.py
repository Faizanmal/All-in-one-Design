from django.contrib import admin
from .models import (
    ComponentUsage, StyleUsage, AdoptionMetric,
    DesignSystemHealth, UsageEvent, DeprecationNotice
)

@admin.register(ComponentUsage)
class ComponentUsageAdmin(admin.ModelAdmin):
    list_display = ['component_name', 'design_system', 'usage_count', 'project_count', 'last_used_at']
    list_filter = ['component_type']
    search_fields = ['component_name', 'component_id']

@admin.register(StyleUsage)
class StyleUsageAdmin(admin.ModelAdmin):
    list_display = ['style_name', 'style_type', 'design_system', 'usage_count', 'direct_usage', 'hardcoded_usage']
    list_filter = ['style_type']
    search_fields = ['style_name', 'style_id']

@admin.register(AdoptionMetric)
class AdoptionMetricAdmin(admin.ModelAdmin):
    list_display = ['design_system', 'team', 'project', 'period_start', 'adoption_rate']
    list_filter = ['period_type']

@admin.register(DesignSystemHealth)
class DesignSystemHealthAdmin(admin.ModelAdmin):
    list_display = ['design_system', 'assessed_at', 'overall_score', 'adoption_score', 'consistency_score']

@admin.register(UsageEvent)
class UsageEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'design_system', 'user', 'created_at']
    list_filter = ['event_type', 'created_at']

@admin.register(DeprecationNotice)
class DeprecationNoticeAdmin(admin.ModelAdmin):
    list_display = ['deprecated_name', 'deprecated_type', 'design_system', 'deprecated_at', 'removal_date']
    list_filter = ['deprecated_type']

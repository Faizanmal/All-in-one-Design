from django.contrib import admin
from .models import UserActivity, ProjectAnalytics, AIUsageMetrics, DailyUsageStats, SystemMetrics


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp', 'ip_address', 'duration_ms')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__username', 'user__email', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(ProjectAnalytics)
class ProjectAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('project', 'view_count', 'edit_count', 'export_count', 'total_components', 'last_edited')
    list_filter = ('last_edited', 'last_viewed')
    search_fields = ('project__name', 'project__user__username')
    readonly_fields = ('updated_at',)


@admin.register(AIUsageMetrics)
class AIUsageMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'tokens_used', 'estimated_cost', 'success', 'timestamp')
    list_filter = ('service_type', 'success', 'timestamp')
    search_fields = ('user__username', 'user__email', 'model_used')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(DailyUsageStats)
class DailyUsageStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'projects_created', 'ai_generations_count', 'ai_tokens_used', 'ai_cost')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'date'


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'active_users_24h', 'ai_requests_24h', 'avg_response_time_ms', 'error_rate_percentage')
    list_filter = ('timestamp',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

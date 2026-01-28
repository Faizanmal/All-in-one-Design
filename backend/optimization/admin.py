from django.contrib import admin
from .models import (
    ABTest, ABTestVariant, PerformanceAnalysis, DeviceCompatibility,
    UserBehaviorPrediction, SmartLayoutSuggestion, OptimizationReport
)


@admin.register(ABTest)
class ABTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'project', 'status', 'goal', 'created_at']
    list_filter = ['status', 'goal', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ABTestVariant)
class ABTestVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'ab_test', 'is_control', 'impressions', 'conversions', 'conversion_rate']
    list_filter = ['is_control', 'ab_test']
    readonly_fields = ['id', 'conversion_rate', 'click_rate', 'created_at']


@admin.register(PerformanceAnalysis)
class PerformanceAnalysisAdmin(admin.ModelAdmin):
    list_display = ['project', 'analysis_type', 'overall_score', 'created_at']
    list_filter = ['analysis_type', 'created_at']


@admin.register(DeviceCompatibility)
class DeviceCompatibilityAdmin(admin.ModelAdmin):
    list_display = ['project', 'overall_score', 'created_at']
    list_filter = ['created_at']


@admin.register(UserBehaviorPrediction)
class UserBehaviorPredictionAdmin(admin.ModelAdmin):
    list_display = ['project', 'predicted_engagement_score', 'predicted_conversion_rate', 'created_at']
    list_filter = ['created_at']


@admin.register(SmartLayoutSuggestion)
class SmartLayoutSuggestionAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'user', 'created_at']
    list_filter = ['content_type', 'created_at']


@admin.register(OptimizationReport)
class OptimizationReportAdmin(admin.ModelAdmin):
    list_display = ['project', 'overall_score', 'performance_score', 'accessibility_score', 'created_at']
    list_filter = ['created_at']

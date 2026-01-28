from django.contrib import admin
from .models import (
    AccessibilityTest, AccessibilityIssue, ColorBlindnessSimulation,
    ScreenReaderPreview, FocusOrderTest, ContrastCheck
)

@admin.register(AccessibilityTest)
class AccessibilityTestAdmin(admin.ModelAdmin):
    list_display = ['project', 'target_level', 'status', 'accessibility_score', 'total_issues', 'created_at']
    list_filter = ['status', 'target_level', 'passed']
    search_fields = ['project__name']

@admin.register(AccessibilityIssue)
class AccessibilityIssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity', 'category', 'wcag_criterion', 'is_fixed', 'ignored']
    list_filter = ['severity', 'category', 'is_fixed', 'ignored']
    search_fields = ['title', 'description']

@admin.register(ColorBlindnessSimulation)
class ColorBlindnessSimulationAdmin(admin.ModelAdmin):
    list_display = ['project', 'simulation_type', 'created_at']
    list_filter = ['simulation_type']

@admin.register(ScreenReaderPreview)
class ScreenReaderPreviewAdmin(admin.ModelAdmin):
    list_display = ['project', 'frame_id', 'created_at']

@admin.register(FocusOrderTest)
class FocusOrderTestAdmin(admin.ModelAdmin):
    list_display = ['project', 'frame_id', 'created_at']

@admin.register(ContrastCheck)
class ContrastCheckAdmin(admin.ModelAdmin):
    list_display = ['element_id', 'contrast_ratio', 'passes_aa', 'passes_aaa', 'created_at']
    list_filter = ['passes_aa', 'passes_aaa']

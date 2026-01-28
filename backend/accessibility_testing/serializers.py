"""
Accessibility Testing Serializers
"""

from rest_framework import serializers
from .models import (
    AccessibilityTest, AccessibilityIssue, ColorBlindnessSimulation,
    ScreenReaderPreview, FocusOrderTest, ContrastCheck,
    AccessibilityReport, AccessibilityGuideline
)


class AccessibilityIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityIssue
        fields = [
            'id', 'test', 'severity', 'category',
            'wcag_criterion', 'wcag_level',
            'title', 'description', 'how_to_fix',
            'element_id', 'element_type', 'element_name',
            'current_value', 'suggested_fix', 'auto_fixable',
            'is_fixed', 'ignored', 'ignore_reason',
            'created_at'
        ]


class AccessibilityTestSerializer(serializers.ModelSerializer):
    issues_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = AccessibilityTest
        fields = [
            'id', 'project', 'target_level', 'test_categories',
            'status', 'progress', 'passed',
            'total_issues', 'errors', 'warnings', 'notices',
            'accessibility_score', 'issues_summary',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'progress', 'passed',
            'total_issues', 'errors', 'warnings', 'notices',
            'accessibility_score', 'started_at', 'completed_at', 'created_at'
        ]
    
    def get_issues_summary(self, obj):
        issues = obj.issues.all()
        return {
            'by_category': self._group_by_field(issues, 'category'),
            'by_severity': self._group_by_field(issues, 'severity'),
        }
    
    def _group_by_field(self, queryset, field):
        result = {}
        for item in queryset:
            key = getattr(item, field)
            result[key] = result.get(key, 0) + 1
        return result
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AccessibilityTestDetailSerializer(AccessibilityTestSerializer):
    issues = AccessibilityIssueSerializer(many=True, read_only=True)
    
    class Meta(AccessibilityTestSerializer.Meta):
        fields = AccessibilityTestSerializer.Meta.fields + ['issues', 'results']


class ColorBlindnessSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorBlindnessSimulation
        fields = [
            'id', 'project', 'simulation_type', 'frame_id',
            'original_image', 'simulated_image',
            'color_mapping', 'issues', 'created_at'
        ]


class ScreenReaderPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreenReaderPreview
        fields = [
            'id', 'project', 'frame_id',
            'content', 'speech_text',
            'reading_order_issues', 'missing_alt_text',
            'aria_analysis', 'created_at'
        ]


class FocusOrderTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusOrderTest
        fields = [
            'id', 'project', 'frame_id',
            'focus_order', 'issues',
            'focus_indicator_issues', 'visualization_data',
            'created_at'
        ]


class ContrastCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContrastCheck
        fields = [
            'id', 'test', 'project',
            'element_id', 'element_type', 'element_name',
            'foreground_color', 'background_color',
            'contrast_ratio', 'font_size', 'is_large_text', 'is_bold',
            'passes_aa', 'passes_aaa',
            'suggested_foreground', 'suggested_background',
            'created_at'
        ]


class AccessibilityReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityReport
        fields = [
            'id', 'test', 'format', 'file',
            'include_summary', 'include_issues',
            'include_screenshots', 'include_recommendations',
            'created_at'
        ]


class AccessibilityGuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessibilityGuideline
        fields = [
            'id', 'principle', 'guideline', 'criterion', 'level',
            'description', 'understanding_url', 'how_to_meet_url',
            'sufficient_techniques', 'advisory_techniques', 'failures'
        ]


# Request Serializers

class RunTestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    target_level = serializers.ChoiceField(choices=['A', 'AA', 'AAA'], default='AA')
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'contrast', 'focus', 'screen_reader', 'color_blindness',
            'alt_text', 'semantics', 'keyboard', 'motion'
        ]),
        required=False
    )
    frame_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class SimulateColorBlindnessSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    simulation_type = serializers.ChoiceField(choices=[
        'protanopia', 'deuteranopia', 'tritanopia',
        'protanomaly', 'deuteranomaly', 'tritanomaly',
        'achromatopsia', 'achromatomaly'
    ])
    frame_id = serializers.CharField(required=False)
    colors = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class GenerateScreenReaderPreviewSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    frame_id = serializers.CharField(required=False)


class CheckContrastSerializer(serializers.Serializer):
    foreground = serializers.CharField()
    background = serializers.CharField()
    font_size = serializers.FloatField(default=16)
    is_bold = serializers.BooleanField(default=False)


class FixIssueSerializer(serializers.Serializer):
    apply_suggestion = serializers.BooleanField(default=True)
    custom_fix = serializers.JSONField(required=False)


class IgnoreIssueSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)

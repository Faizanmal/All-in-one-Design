"""
Serializers for Design QA app.
"""
from rest_framework import serializers
from .models import (
    LintRuleSet, LintRule, DesignLintReport, LintIssue,
    AccessibilityCheck, AccessibilityReport, AccessibilityIssue,
    StyleUsageReport, LintIgnoreRule
)


class LintRuleSerializer(serializers.ModelSerializer):
    """Serializer for lint rules."""
    
    class Meta:
        model = LintRule
        fields = [
            'id', 'rule_set', 'name', 'description', 'category',
            'severity', 'rule_type', 'configuration', 'error_message',
            'suggestion', 'documentation_url', 'is_enabled', 'is_auto_fixable',
            'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LintRuleSetSerializer(serializers.ModelSerializer):
    """Serializer for lint rule sets."""
    rules = LintRuleSerializer(many=True, read_only=True)
    rule_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = LintRuleSet
        fields = [
            'id', 'name', 'description', 'design_system', 'is_default',
            'is_strict', 'extends', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'rules', 'rule_count'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_rule_count(self, obj):
        return obj.rules.filter(is_enabled=True).count()


class LintRuleSetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for rule set lists."""
    rule_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LintRuleSet
        fields = [
            'id', 'name', 'description', 'is_default', 'is_strict',
            'rule_count', 'updated_at'
        ]
    
    def get_rule_count(self, obj):
        return obj.rules.filter(is_enabled=True).count()


class LintIssueSerializer(serializers.ModelSerializer):
    """Serializer for lint issues."""
    rule_name = serializers.CharField(source='rule.name', read_only=True, allow_null=True)
    rule_category = serializers.CharField(source='rule.category', read_only=True, allow_null=True)
    
    class Meta:
        model = LintIssue
        fields = [
            'id', 'report', 'rule', 'rule_name', 'rule_category',
            'node_id', 'node_type', 'node_name', 'node_path',
            'severity', 'message', 'suggestion', 'current_value',
            'expected_value', 'auto_fix_available', 'auto_fix_data',
            'is_ignored', 'ignored_by', 'ignored_reason', 'ignored_at',
            'is_resolved', 'resolved_by', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DesignLintReportSerializer(serializers.ModelSerializer):
    """Serializer for design lint reports."""
    issues = LintIssueSerializer(many=True, read_only=True)
    issue_summary = serializers.SerializerMethodField()
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = DesignLintReport
        fields = [
            'id', 'project', 'rule_set', 'status', 'total_issues',
            'errors', 'warnings', 'info', 'nodes_checked', 'duration_ms',
            'triggered_by', 'triggered_by_name', 'trigger_type',
            'created_at', 'completed_at', 'issues', 'issue_summary'
        ]
        read_only_fields = ['id', 'status', 'total_issues', 'errors', 'warnings', 'info', 'nodes_checked', 'duration_ms', 'created_at', 'completed_at']
    
    def get_issue_summary(self, obj):
        return {
            'by_category': self._count_by_category(obj),
            'by_severity': {
                'error': obj.errors,
                'warning': obj.warnings,
                'info': obj.info,
            },
            'unresolved': obj.issues.filter(is_resolved=False, is_ignored=False).count(),
        }
    
    def _count_by_category(self, obj):
        from django.db.models import Count
        return dict(
            obj.issues.values('rule__category').annotate(count=Count('id')).values_list('rule__category', 'count')
        )


class DesignLintReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for report lists."""
    
    class Meta:
        model = DesignLintReport
        fields = [
            'id', 'status', 'total_issues', 'errors', 'warnings',
            'info', 'trigger_type', 'created_at', 'completed_at'
        ]


class AccessibilityCheckSerializer(serializers.ModelSerializer):
    """Serializer for accessibility checks."""
    
    class Meta:
        model = AccessibilityCheck
        fields = [
            'id', 'name', 'description', 'wcag_criterion', 'wcag_level',
            'check_type', 'configuration', 'is_enabled', 'severity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AccessibilityIssueSerializer(serializers.ModelSerializer):
    """Serializer for accessibility issues."""
    check_name = serializers.CharField(source='accessibility_check.name', read_only=True)
    wcag_criterion = serializers.CharField(source='accessibility_check.wcag_criterion', read_only=True)
    
    class Meta:
        model = AccessibilityIssue
        fields = [
            'id', 'report', 'accessibility_check', 'check_name', 'wcag_criterion',
            'node_id', 'node_type', 'node_name', 'severity', 'message',
            'impact', 'affected_users', 'remediation', 'code_snippet',
            'is_resolved', 'resolved_by', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AccessibilityReportSerializer(serializers.ModelSerializer):
    """Serializer for accessibility reports."""
    issues = AccessibilityIssueSerializer(many=True, read_only=True)
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True, allow_null=True)
    score_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = AccessibilityReport
        fields = [
            'id', 'project', 'wcag_version', 'target_level', 'status',
            'overall_score', 'level_a_score', 'level_aa_score', 'level_aaa_score',
            'total_issues', 'critical_issues', 'serious_issues', 'moderate_issues',
            'minor_issues', 'nodes_checked', 'duration_ms', 'triggered_by',
            'triggered_by_name', 'created_at', 'completed_at', 'issues',
            'score_breakdown'
        ]
        read_only_fields = ['id', 'status', 'overall_score', 'level_a_score', 'level_aa_score', 'level_aaa_score', 'total_issues', 'critical_issues', 'serious_issues', 'moderate_issues', 'minor_issues', 'nodes_checked', 'duration_ms', 'created_at', 'completed_at']
    
    def get_score_breakdown(self, obj):
        return {
            'wcag_a': obj.level_a_score,
            'wcag_aa': obj.level_aa_score,
            'wcag_aaa': obj.level_aaa_score,
            'issues_by_impact': {
                'critical': obj.critical_issues,
                'serious': obj.serious_issues,
                'moderate': obj.moderate_issues,
                'minor': obj.minor_issues,
            }
        }


class AccessibilityReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for accessibility report lists."""
    
    class Meta:
        model = AccessibilityReport
        fields = [
            'id', 'wcag_version', 'target_level', 'status', 'overall_score',
            'total_issues', 'critical_issues', 'created_at', 'completed_at'
        ]


class StyleUsageReportSerializer(serializers.ModelSerializer):
    """Serializer for style usage reports."""
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = StyleUsageReport
        fields = [
            'id', 'project', 'design_system', 'status', 'color_usage',
            'typography_usage', 'spacing_usage', 'component_usage',
            'detached_styles', 'unused_styles', 'override_count',
            'consistency_score', 'triggered_by', 'triggered_by_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'status', 'color_usage', 'typography_usage', 'spacing_usage', 'component_usage', 'detached_styles', 'unused_styles', 'override_count', 'consistency_score', 'created_at', 'completed_at']


class LintIgnoreRuleSerializer(serializers.ModelSerializer):
    """Serializer for lint ignore rules."""
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = LintIgnoreRule
        fields = [
            'id', 'project', 'rule', 'node_id', 'node_path_pattern',
            'reason', 'expires_at', 'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class RunLintSerializer(serializers.Serializer):
    """Serializer for running lint checks."""
    rule_set_id = serializers.UUIDField(required=False)
    node_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Specific nodes to check. If empty, checks entire project."
    )
    categories = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'spacing', 'alignment', 'color', 'typography',
            'accessibility', 'naming', 'consistency', 'performance'
        ]),
        required=False,
        help_text="Categories to check. If empty, checks all."
    )


class RunAccessibilityCheckSerializer(serializers.Serializer):
    """Serializer for running accessibility checks."""
    wcag_version = serializers.ChoiceField(
        choices=['2.0', '2.1', '2.2'],
        default='2.1'
    )
    target_level = serializers.ChoiceField(
        choices=['A', 'AA', 'AAA'],
        default='AA'
    )
    node_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class AutoFixSerializer(serializers.Serializer):
    """Serializer for auto-fix request."""
    issue_ids = serializers.ListField(
        child=serializers.UUIDField()
    )
    preview = serializers.BooleanField(
        default=True,
        help_text="If true, returns preview without applying changes."
    )

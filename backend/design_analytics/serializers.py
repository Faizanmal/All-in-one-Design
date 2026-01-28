"""
Design Analytics Serializers
"""

from rest_framework import serializers
from .models import (
    ComponentUsage, StyleUsage, AdoptionMetric, DesignSystemHealth,
    UsageEvent, DeprecationNotice, AnalyticsDashboard
)


class ComponentUsageSerializer(serializers.ModelSerializer):
    override_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ComponentUsage
        fields = [
            'id', 'design_system', 'component_id', 'component_name', 'component_type',
            'usage_count', 'project_count', 'weekly_usage', 'monthly_usage',
            'last_used_at', 'override_count', 'override_rate',
            'created_at', 'updated_at'
        ]
    
    def get_override_rate(self, obj):
        if obj.usage_count > 0:
            return round(obj.override_count / obj.usage_count * 100, 1)
        return 0


class StyleUsageSerializer(serializers.ModelSerializer):
    consistency_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = StyleUsage
        fields = [
            'id', 'design_system', 'style_type', 'style_id', 'style_name', 'style_value',
            'usage_count', 'project_count', 'direct_usage', 'hardcoded_usage',
            'consistency_rate', 'created_at', 'updated_at'
        ]
    
    def get_consistency_rate(self, obj):
        total = obj.direct_usage + obj.hardcoded_usage
        if total > 0:
            return round(obj.direct_usage / total * 100, 1)
        return 100


class AdoptionMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionMetric
        fields = [
            'id', 'design_system', 'team', 'project',
            'period_start', 'period_end', 'period_type',
            'total_elements', 'system_elements', 'adoption_rate',
            'total_styles', 'linked_styles', 'style_consistency',
            'total_components', 'unmodified_components', 'component_consistency',
            'detach_count', 'created_at'
        ]


class DesignSystemHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSystemHealth
        fields = [
            'id', 'design_system', 'assessed_at',
            'overall_score', 'adoption_score', 'consistency_score',
            'coverage_score', 'freshness_score', 'documentation_score',
            'issues', 'recommendations'
        ]


class UsageEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = UsageEvent
        fields = [
            'id', 'design_system', 'event_type',
            'component_id', 'component_name', 'style_id', 'style_name',
            'user', 'user_name', 'project', 'project_name',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeprecationNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeprecationNotice
        fields = [
            'id', 'design_system', 'deprecated_type',
            'deprecated_id', 'deprecated_name',
            'replacement_id', 'replacement_name',
            'deprecated_at', 'removal_date',
            'current_usage_count', 'affected_projects',
            'migration_guide'
        ]


class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsDashboard
        fields = [
            'id', 'design_system', 'name', 'is_default',
            'widgets', 'default_period', 'team_filter',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# Request Serializers

class TrackUsageSerializer(serializers.Serializer):
    design_system_id = serializers.UUIDField()
    event_type = serializers.ChoiceField(choices=[
        'insert', 'update', 'delete', 'detach', 'swap',
        'style_apply', 'style_detach', 'library_publish', 'library_update'
    ])
    component_id = serializers.CharField(required=False, allow_blank=True)
    component_name = serializers.CharField(required=False, allow_blank=True)
    style_id = serializers.CharField(required=False, allow_blank=True)
    style_name = serializers.CharField(required=False, allow_blank=True)
    project_id = serializers.IntegerField(required=False)
    metadata = serializers.JSONField(default=dict)


class AnalyticsQuerySerializer(serializers.Serializer):
    design_system_id = serializers.UUIDField()
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    period = serializers.ChoiceField(
        choices=['7d', '30d', '90d', '365d', 'all'],
        default='30d'
    )
    group_by = serializers.ChoiceField(
        choices=['day', 'week', 'month'],
        default='day'
    )
    team_id = serializers.IntegerField(required=False)
    project_id = serializers.IntegerField(required=False)


class DeprecateItemSerializer(serializers.Serializer):
    design_system_id = serializers.UUIDField()
    deprecated_type = serializers.ChoiceField(choices=['component', 'style', 'variant'])
    deprecated_id = serializers.CharField()
    deprecated_name = serializers.CharField()
    replacement_id = serializers.CharField(required=False, allow_blank=True)
    replacement_name = serializers.CharField(required=False, allow_blank=True)
    removal_date = serializers.DateField(required=False)
    migration_guide = serializers.CharField(required=False, allow_blank=True)

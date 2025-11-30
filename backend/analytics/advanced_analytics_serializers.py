"""
Advanced Analytics Serializers
Serializers for analytics dashboards, reports, and insights
"""
from rest_framework import serializers
from .advanced_analytics_models import (
    AnalyticsDashboard,
    AnalyticsWidget,
    AnalyticsReport,
    ReportExecution,
    UserActivityLog,
    PerformanceMetric,
    UsageQuota,
    DesignInsight
)


class AnalyticsWidgetSerializer(serializers.ModelSerializer):
    """Serializer for analytics widgets"""
    
    class Meta:
        model = AnalyticsWidget
        fields = [
            'id', 'name', 'description', 'widget_type', 'metric_type',
            'config', 'default_width', 'default_height', 'is_system',
            'created_at'
        ]
        read_only_fields = ['id', 'is_system', 'created_at']


class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    """Serializer for analytics dashboards"""
    owner_name = serializers.CharField(source='user.username', read_only=True)
    shared_with_names = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsDashboard
        fields = [
            'id', 'user', 'owner_name', 'team', 'name', 'description',
            'layout', 'is_public', 'shared_with', 'shared_with_names',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_shared_with_names(self, obj):
        return [u.username for u in obj.shared_with.all()]


class ReportExecutionSerializer(serializers.ModelSerializer):
    """Serializer for report executions"""
    
    class Meta:
        model = ReportExecution
        fields = [
            'id', 'report', 'status', 'file_url', 'file_size',
            'started_at', 'completed_at', 'error_message', 'created_at'
        ]
        read_only_fields = fields


class AnalyticsReportSerializer(serializers.ModelSerializer):
    """Serializer for analytics reports"""
    dashboard_name = serializers.CharField(
        source='dashboard.name',
        read_only=True,
        allow_null=True
    )
    last_execution = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyticsReport
        fields = [
            'id', 'user', 'dashboard', 'dashboard_name', 'name',
            'description', 'metrics', 'filters', 'frequency', 'send_day',
            'send_time', 'format', 'recipients', 'is_active',
            'last_sent_at', 'next_send_at', 'last_execution',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'last_sent_at', 'next_send_at', 
                          'created_at', 'updated_at']
    
    def get_last_execution(self, obj):
        execution = obj.executions.first()
        if execution:
            return ReportExecutionSerializer(execution).data
        return None


class UserActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for user activity logs"""
    project_name = serializers.CharField(
        source='project.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'user', 'project', 'project_name', 'action_type',
            'details', 'session_id', 'device_type', 'browser',
            'duration', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'ip_address', 'device_type', 
                          'browser', 'created_at']


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for performance metrics"""
    
    class Meta:
        model = PerformanceMetric
        fields = [
            'id', 'user', 'category', 'name', 'value', 'unit',
            'context', 'device_type', 'browser', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer for usage quotas"""
    usage_percentage = serializers.FloatField(read_only=True)
    is_exceeded = serializers.BooleanField(read_only=True)
    remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UsageQuota
        fields = [
            'id', 'user', 'team', 'quota_type', 'limit', 'used',
            'remaining', 'usage_percentage', 'is_exceeded',
            'period_start', 'period_end', 'alert_threshold',
            'alert_sent', 'updated_at'
        ]
        read_only_fields = fields
    
    def get_remaining(self, obj):
        return max(0, obj.limit - obj.used)


class DesignInsightSerializer(serializers.ModelSerializer):
    """Serializer for design insights"""
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = DesignInsight
        fields = [
            'id', 'project', 'project_name', 'insight_type', 'severity',
            'title', 'description', 'element_id', 'element_type',
            'suggestion', 'auto_fix_available', 'is_dismissed',
            'is_applied', 'created_at'
        ]
        read_only_fields = ['id', 'project', 'auto_fix_data', 'created_at']


class DashboardLayoutItemSerializer(serializers.Serializer):
    """Serializer for dashboard layout items"""
    widget_id = serializers.CharField()
    widget_type = serializers.CharField()
    position = serializers.DictField()
    config = serializers.DictField(required=False)


class MetricDataSerializer(serializers.Serializer):
    """Serializer for metric data response"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    total = serializers.FloatField()


class ActivitySummarySerializer(serializers.Serializer):
    """Serializer for activity summary"""
    by_action = serializers.ListField()
    total_actions = serializers.IntegerField()
    total_time_minutes = serializers.FloatField()
    period_days = serializers.IntegerField()


class OverviewResponseSerializer(serializers.Serializer):
    """Serializer for analytics overview response"""
    period_days = serializers.IntegerField()
    projects = serializers.DictField()
    activity = serializers.DictField()
    top_actions = serializers.ListField()
    daily_trend = serializers.ListField()

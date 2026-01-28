from rest_framework import serializers
from .realtime_models import (
    Heatmap, UserFlow, DesignSession, DesignInteraction, DesignMetric,
    ElementAnalytics, ConversionGoal, ConversionEvent, CompetitorAnalysis,
    RealtimeAnalyticsDashboard, RealtimeAnalyticsReport
)


class HeatmapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heatmap
        fields = [
            'id', 'project', 'heatmap_type', 'width', 'height',
            'data_points', 'total_interactions', 'start_date', 'end_date',
            'heatmap_image', 'created_at'
        ]
        read_only_fields = ['id', 'heatmap_image', 'created_at']


class UserFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFlow
        fields = [
            'id', 'project', 'name', 'description', 'steps',
            'entry_point', 'exit_points', 'total_users', 'completion_rate',
            'average_time', 'drop_off_points', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DesignInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignInteraction
        fields = [
            'id', 'interaction_type', 'x', 'y', 'element_id',
            'element_type', 'page_id', 'timestamp', 'metadata'
        ]
        read_only_fields = ['id']


class DesignSessionSerializer(serializers.ModelSerializer):
    interactions = DesignInteractionSerializer(many=True, read_only=True)
    interaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignSession
        fields = [
            'id', 'project', 'session_id', 'user', 'device_type',
            'browser', 'os', 'screen_width', 'screen_height',
            'country', 'city', 'started_at', 'ended_at', 'total_duration',
            'pages_viewed', 'click_count', 'scroll_depth',
            'interactions', 'interaction_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_interaction_count(self, obj):
        return obj.interactions.count()


class DesignMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignMetric
        fields = [
            'id', 'project', 'metric_type', 'period_type', 'period_start',
            'value', 'previous_value', 'change_percent', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ElementAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementAnalytics
        fields = [
            'id', 'project', 'element_id', 'element_type', 'element_name',
            'click_count', 'hover_count', 'hover_duration_avg',
            'visibility_count', 'attention_score', 'period_start', 'period_end',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionEvent
        fields = ['id', 'session', 'value', 'metadata', 'timestamp']
        read_only_fields = ['id']


class ConversionGoalSerializer(serializers.ModelSerializer):
    event_count = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversionGoal
        fields = [
            'id', 'project', 'name', 'description', 'goal_type',
            'target_element_id', 'target_page_id', 'target_value',
            'is_active', 'event_count', 'conversion_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_event_count(self, obj):
        return obj.events.count()
    
    def get_conversion_rate(self, obj):
        # Calculate conversion rate
        total_sessions = DesignSession.objects.filter(project=obj.project).count()
        if total_sessions == 0:
            return 0
        return (obj.events.count() / total_sessions) * 100


class CompetitorAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorAnalysis
        fields = [
            'id', 'name', 'competitor_url', 'design_score', 'ux_score',
            'accessibility_score', 'colors_used', 'fonts_used', 'technologies',
            'screenshot', 'ai_insights', 'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


class RealtimeAnalyticsDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealtimeAnalyticsDashboard
        fields = [
            'id', 'name', 'description', 'widgets', 'default_filters',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RealtimeAnalyticsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealtimeAnalyticsReport
        fields = [
            'id', 'project', 'name', 'report_format', 'metrics_included',
            'date_range_start', 'date_range_end', 'file', 'status',
            'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'file', 'status', 'error_message', 'created_at', 'completed_at']

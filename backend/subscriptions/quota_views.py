"""
AI Quota Management API Views and Serializers
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.utils import timezone
from .quota_models import AIUsageQuota, AIUsageRecord, BudgetAlert, AIModelPricing
from .quota_service import QuotaService


# ============================================
# SERIALIZERS
# ============================================

class AIUsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer for AI usage quota."""
    requests_remaining = serializers.ReadOnlyField()
    tokens_remaining = serializers.ReadOnlyField()
    budget_remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    success_rate = serializers.ReadOnlyField()
    is_request_limit_reached = serializers.ReadOnlyField()
    is_budget_exceeded = serializers.ReadOnlyField()
    
    class Meta:
        model = AIUsageQuota
        fields = [
            'id', 'period_start', 'period_end',
            'ai_requests_used', 'ai_requests_limit', 'requests_remaining',
            'ai_tokens_used', 'ai_tokens_limit', 'tokens_remaining',
            'image_generations_used', 'image_generations_limit',
            'total_cost', 'budget_limit', 'budget_remaining',
            'successful_requests', 'failed_requests', 'success_rate',
            'is_request_limit_reached', 'is_budget_exceeded',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'ai_requests_used', 'ai_tokens_used', 
            'image_generations_used', 'total_cost',
            'successful_requests', 'failed_requests',
            'created_at', 'updated_at',
        ]


class AIUsageRecordSerializer(serializers.ModelSerializer):
    """Serializer for AI usage records."""
    total_tokens = serializers.ReadOnlyField()
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    
    class Meta:
        model = AIUsageRecord
        fields = [
            'id', 'request_type', 'request_type_display', 'model',
            'input_tokens', 'output_tokens', 'total_tokens',
            'images_generated', 'cost', 'success', 'error_message',
            'latency_ms', 'project_id', 'prompt_preview',
            'metadata', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class BudgetAlertSerializer(serializers.ModelSerializer):
    """Serializer for budget alerts."""
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    
    class Meta:
        model = BudgetAlert
        fields = [
            'id', 'alert_type', 'alert_type_display',
            'threshold_percent', 'spending_limit',
            'email_enabled', 'push_enabled',
            'is_active', 'last_triggered',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'last_triggered', 'created_at', 'updated_at']


class QuotaCheckSerializer(serializers.Serializer):
    """Serializer for quota check requests."""
    request_type = serializers.CharField(required=True)
    dry_run = serializers.BooleanField(default=False)


class UsageSummarySerializer(serializers.Serializer):
    """Serializer for usage summary."""
    period = serializers.ChoiceField(
        choices=['day', 'week', 'month', 'year'],
        default='month'
    )


class AIModelPricingSerializer(serializers.ModelSerializer):
    """Serializer for AI model pricing."""
    
    class Meta:
        model = AIModelPricing
        fields = [
            'id', 'model_name', 'display_name',
            'input_cost_per_1k', 'output_cost_per_1k', 'cost_per_image',
            'max_tokens', 'supports_images', 'supports_vision',
            'is_active',
        ]


# ============================================
# VIEWS
# ============================================

class AIUsageQuotaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing AI usage quotas."""
    serializer_class = AIUsageQuotaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIUsageQuota.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current month's quota."""
        service = QuotaService(request.user)
        quota = service.get_current_quota()
        serializer = self.get_serializer(quota)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def check(self, request):
        """
        Check if a request would be allowed.
        
        POST /api/v1/subscriptions/quotas/check/
        Body: {"request_type": "layout_generation", "dry_run": true}
        """
        serializer = QuotaCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = QuotaService(request.user)
        result = service.check_quota(
            request_type=serializer.validated_data['request_type'],
            dry_run=serializer.validated_data['dry_run']
        )
        
        return Response(result)


class AIUsageRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing AI usage records."""
    serializer_class = AIUsageRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['request_type', 'model', 'success']
    
    def get_queryset(self):
        queryset = AIUsageRecord.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset


class BudgetAlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budget alerts."""
    serializer_class = BudgetAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return BudgetAlert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usage_summary(request):
    """
    Get usage summary for a given period.
    
    GET /api/v1/subscriptions/quota/usage-summary/?period=month
    """
    serializer = UsageSummarySerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    service = QuotaService(request.user)
    summary = service.get_usage_summary(
        period=serializer.validated_data.get('period', 'month')
    )
    
    return Response(summary)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def quota_dashboard(request):
    """
    Get comprehensive quota dashboard data.
    
    GET /api/v1/subscriptions/quota/dashboard/
    """
    service = QuotaService(request.user)
    quota = service.get_current_quota()
    
    # Get usage breakdown
    month_summary = service.get_usage_summary('month')
    week_summary = service.get_usage_summary('week')
    
    # Get recent records
    recent_records = AIUsageRecord.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    # Get alerts
    alerts = BudgetAlert.objects.filter(
        user=request.user,
        is_active=True
    )
    
    return Response({
        'quota': AIUsageQuotaSerializer(quota).data,
        'monthly_summary': month_summary,
        'weekly_summary': week_summary,
        'recent_usage': AIUsageRecordSerializer(recent_records, many=True).data,
        'active_alerts': BudgetAlertSerializer(alerts, many=True).data,
        'recommendations': _get_usage_recommendations(quota, month_summary),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cost_estimate(request):
    """
    Estimate cost for a series of AI operations.
    
    GET /api/v1/subscriptions/quota/estimate/?operations=layout_generation,image_generation,color_palette
    """
    operations = request.query_params.get('operations', '').split(',')
    operations = [op.strip() for op in operations if op.strip()]
    
    if not operations:
        return Response(
            {'error': 'No operations specified'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = QuotaService(request.user)
    estimates = []
    total_cost = 0
    total_tokens = 0
    
    for operation in operations:
        result = service.check_quota(operation, dry_run=True)
        estimates.append({
            'operation': operation,
            'estimated_cost': result['estimated_cost'],
            'estimated_tokens': result['estimated_tokens'],
        })
        total_cost += result['estimated_cost']
        total_tokens += result['estimated_tokens']
    
    quota = service.get_current_quota()
    
    return Response({
        'operations': estimates,
        'total_estimated_cost': total_cost,
        'total_estimated_tokens': total_tokens,
        'budget_remaining': float(quota.budget_remaining),
        'tokens_remaining': quota.tokens_remaining,
        'within_budget': total_cost <= float(quota.budget_remaining) if quota.budget_limit > 0 else True,
        'within_token_limit': total_tokens <= quota.tokens_remaining if quota.ai_tokens_limit > 0 else True,
    })


@api_view(['GET'])
def ai_model_pricing(request):
    """
    Get current AI model pricing information.
    
    GET /api/v1/subscriptions/quota/pricing/
    """
    models = AIModelPricing.objects.filter(is_active=True)
    return Response(AIModelPricingSerializer(models, many=True).data)


def _get_usage_recommendations(quota, summary):
    """Generate usage recommendations based on patterns."""
    recommendations = []
    
    # High usage warning
    if quota.ai_requests_limit > 0:
        usage_percent = (quota.ai_requests_used / quota.ai_requests_limit) * 100
        if usage_percent > 80:
            recommendations.append({
                'type': 'warning',
                'title': 'High Usage Alert',
                'message': f"You've used {usage_percent:.0f}% of your monthly AI requests. Consider upgrading your plan.",
                'action': 'upgrade_plan'
            })
    
    # Cost optimization
    by_type = summary.get('by_type', {})
    if by_type:
        most_expensive = max(by_type.items(), key=lambda x: x[1]['cost'], default=None)
        if most_expensive and most_expensive[1]['cost'] > 0:
            recommendations.append({
                'type': 'tip',
                'title': 'Cost Optimization',
                'message': f"'{most_expensive[0]}' is your highest cost operation. Consider batching requests for efficiency.",
                'action': None
            })
    
    # Low success rate
    if quota.success_rate < 90 and (quota.successful_requests + quota.failed_requests) > 5:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Success Rate',
            'message': f"Your AI request success rate is {quota.success_rate:.1f}%. Check your prompts or inputs.",
            'action': 'view_failed_requests'
        })
    
    return recommendations

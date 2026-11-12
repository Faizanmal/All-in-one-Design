"""
Tests for analytics models and views.
"""
import pytest
from rest_framework import status
from analytics.models import (
    UserActivity, ProjectAnalytics, AIUsageMetrics,
    FeatureUsage
)
from projects.models import Project


@pytest.fixture
def project(user):
    return Project.objects.create(user=user, name='Analytics Test')


@pytest.fixture
def user_activity(user):
    return UserActivity.objects.create(
        user=user,
        activity_type='login',
        ip_address='127.0.0.1',
        metadata={'source': 'web'},
    )


@pytest.mark.unit
class TestUserActivity:
    """Tests for UserActivity model."""

    def test_create_activity(self, user_activity):
        assert user_activity.activity_type == 'login'

    def test_activity_types(self, user):
        types = ['login', 'logout', 'project_create', 'project_update',
                 'project_delete', 'project_export', 'ai_generation',
                 'asset_upload', 'template_use']
        for t in types:
            a = UserActivity.objects.create(
                user=user, activity_type=t, ip_address='127.0.0.1'
            )
            assert a.activity_type == t

    def test_activity_metadata(self, user):
        a = UserActivity.objects.create(
            user=user, activity_type='project_create',
            ip_address='127.0.0.1',
            metadata={'project_id': 1, 'project_type': 'graphic'},
        )
        assert a.metadata['project_id'] == 1

    def test_activity_duration(self, user):
        a = UserActivity.objects.create(
            user=user, activity_type='project_update',
            ip_address='127.0.0.1', duration_ms=5000,
        )
        assert a.duration_ms == 5000


@pytest.mark.unit
class TestProjectAnalytics:
    """Tests for ProjectAnalytics model."""

    def test_create_analytics(self, project):
        analytics, _ = ProjectAnalytics.objects.update_or_create(
            project=project,
            defaults={'view_count': 10, 'edit_count': 5, 'export_count': 2},
        )
        assert analytics.view_count == 10
        assert analytics.edit_count == 5

    def test_analytics_counters(self, project):
        analytics = ProjectAnalytics.objects.get(project=project)
        analytics.view_count += 1
        analytics.save()
        analytics.refresh_from_db()
        assert analytics.view_count == 1


@pytest.mark.unit
class TestAIUsageMetrics:
    """Tests for AIUsageMetrics model."""

    def test_create_ai_metrics(self, user, project):
        metrics = AIUsageMetrics.objects.create(
            user=user,
            service_type='logo_generation',
            tokens_used=500,
            estimated_cost=0.05,
            model_used='gpt-4',
            request_duration_ms=2000,
            success=True,
            project=project,
        )
        assert metrics.service_type == 'logo_generation'
        assert metrics.success is True

    def test_failed_ai_request(self, user):
        metrics = AIUsageMetrics.objects.create(
            user=user,
            service_type='image_generation',
            tokens_used=0,
            model_used='test',
            request_duration_ms=10,
            success=False,
        )
        assert metrics.success is False


@pytest.mark.unit
class TestFeatureUsage:
    """Tests for FeatureUsage model."""

    def test_track_feature(self, user):
        usage = FeatureUsage.objects.create(
            user=user,
            feature_name='auto_layout',
            feature_category='design_tools',
            usage_count=1,
        )
        assert usage.feature_name == 'auto_layout'


@pytest.mark.api
class TestAnalyticsAPI:
    """Tests for analytics API endpoints."""

    def test_list_activities(self, auth_client, user_activity):
        response = auth_client.get('/api/v1/analytics/activities/')
        assert response.status_code == status.HTTP_200_OK

    def test_recent_activities(self, auth_client, user_activity):
        response = auth_client.get('/api/v1/analytics/activities/recent/')
        assert response.status_code == status.HTTP_200_OK

    def test_dashboard_stats(self, auth_client, user):
        response = auth_client.get('/api/v1/analytics/dashboard/')
        assert response.status_code == status.HTTP_200_OK

    def test_track_activity(self, auth_client, user):
        payload = {
            'activity_type': 'project_create',
            'metadata': {'project_type': 'graphic'},
        }
        response = auth_client.post(
            '/api/v1/analytics/track/', payload, format='json'
        )
        assert response.status_code in [200, 201]

    def test_ai_usage_list(self, auth_client, user):
        response = auth_client.get('/api/v1/analytics/ai-usage/')
        assert response.status_code == status.HTTP_200_OK

    def test_ai_usage_summary(self, auth_client, user):
        response = auth_client.get('/api/v1/analytics/ai-usage/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['summary']['total_requests'] == 0
        assert response.data['summary']['total_tokens'] == 0
        assert response.data['summary']['total_cost'] == 0
        assert response.data['summary']['success_rate'] is None

    def test_pending_generation_is_tracked_once_when_completed(self, auth_client, user):
        from ai_services.models import AIGenerationRequest
        from analytics.models import DailyUsageStats
        request = AIGenerationRequest.objects.create(user=user, request_type='layout', prompt='Test', status='pending')
        assert not AIUsageMetrics.objects.filter(generation_request=request).exists()
        request.status = 'completed'
        request.tokens_used = 120
        request.save()
        request.save()
        metrics = AIUsageMetrics.objects.filter(generation_request=request)
        assert metrics.count() == 1
        assert metrics.get().service_type == 'layout_generation'
        assert DailyUsageStats.objects.get(user=user).ai_generations_count == 1
        response = auth_client.get('/api/v1/analytics/ai-usage/summary/')
        assert response.data['by_service']['layout_generation']['count'] == 1

    def test_failed_generation_and_assistant_services_are_reported(self, auth_client, user):
        from ai_services.models import AIGenerationRequest
        request = AIGenerationRequest.objects.create(user=user, request_type='layout_optimization', prompt='Test', status='processing')
        request.status = 'failed'
        request.error_message = 'Provider unavailable'
        request.save()
        response = auth_client.get('/api/v1/analytics/ai-usage/summary/')
        assert response.data['summary']['total_requests'] == 1
        assert response.data['summary']['success_rate'] == 0
        assert response.data['by_service']['layout_optimization']['count'] == 1

    @pytest.mark.parametrize('days', ['invalid', '0', '-1', '366'])
    def test_usage_summary_rejects_invalid_period(self, auth_client, days):
        response = auth_client.get(f'/api/v1/analytics/ai-usage/summary/?days={days}')
        assert response.status_code == 400

    def test_usage_summary_reports_fraction_and_isolates_users(self, auth_client, user, user2):
        for owner, success in [(user, True), (user, False), (user2, True)]:
            AIUsageMetrics.objects.create(
                user=owner, service_type='layout_generation', tokens_used=100,
                estimated_cost='0.01', model_used='test', request_duration_ms=10,
                success=success,
            )
        response = auth_client.get('/api/v1/analytics/ai-usage/summary/')
        assert response.status_code == 200
        assert response.data['summary']['total_requests'] == 2
        assert response.data['summary']['total_tokens'] == 200
        assert response.data['summary']['success_rate'] == 0.5
        assert response.data['by_service']['layout_generation']['count'] == 2

    def test_project_analytics(self, auth_client, project):
        response = auth_client.get(
            f'/api/v1/analytics/projects/{project.id}/'
        )
        assert response.status_code in [200, 404]

    def test_analytics_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/analytics/dashboard/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

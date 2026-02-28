"""
End-to-end tests for the complete project lifecycle.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from projects.models import Project


@pytest.mark.integration
class TestProjectWorkflow:
    """Test complete project creation → edit → version → collaborate → export."""

    def test_full_project_lifecycle(self, auth_client, user, user2):
        """Create → Update → Version → Add Collaborator → Search → Delete."""
        # Step 1: Create project
        create_resp = auth_client.post('/api/v1/projects/', {
            'name': 'E2E Project',
            'description': 'End-to-end test project',
            'project_type': 'graphic',
            'canvas_width': 1920,
            'canvas_height': 1080,
        })
        assert create_resp.status_code == status.HTTP_201_CREATED
        project_id = create_resp.data['id']

        # Step 2: Update project
        update_resp = auth_client.patch(f'/api/v1/projects/{project_id}/', {
            'name': 'E2E Project Updated',
            'description': 'Updated description',
        })
        assert update_resp.status_code == status.HTTP_200_OK
        assert update_resp.data['name'] == 'E2E Project Updated'

        # Step 3: Save design data
        save_resp = auth_client.post(
            f'/api/v1/projects/{project_id}/save_design/',
            {'design_data': {
                'layers': [
                    {'type': 'text', 'content': 'Hello', 'x': 100, 'y': 100},
                    {'type': 'shape', 'shape': 'rectangle', 'x': 200, 'y': 200},
                ]
            }},
            format='json',
        )
        assert save_resp.status_code in [200, 201]

        # Step 4: Create version
        version_resp = auth_client.post(
            f'/api/v1/projects/{project_id}/create_version/',
            {'design_data': {'v': 1}},
            format='json',
        )
        assert version_resp.status_code in [200, 201]

        # Step 5: List versions
        versions_resp = auth_client.get(
            f'/api/v1/projects/{project_id}/versions/'
        )
        assert versions_resp.status_code == status.HTTP_200_OK

        # Step 6: Add collaborator
        collab_resp = auth_client.post(
            f'/api/v1/projects/{project_id}/add_collaborator/',
            {'user_id': user2.id},
        )
        assert collab_resp.status_code in [200, 201]

        # Step 7: Search for project
        search_resp = auth_client.get('/api/v1/projects/search/', {'q': 'E2E'})
        assert search_resp.status_code == status.HTTP_200_OK

        # Step 8: My projects
        my_resp = auth_client.get('/api/v1/projects/my_projects/')
        assert my_resp.status_code == status.HTTP_200_OK

        # Step 9: Delete project
        delete_resp = auth_client.delete(f'/api/v1/projects/{project_id}/')
        assert delete_resp.status_code in [200, 204]

    def test_multiple_projects_workflow(self, auth_client, user):
        """Create multiple projects and verify listing/filtering."""
        project_ids = []
        for i in range(3):
            resp = auth_client.post('/api/v1/projects/', {
                'name': f'Multi Project {i}',
                'project_type': ['graphic', 'ui_ux', 'logo'][i],
            })
            assert resp.status_code == status.HTTP_201_CREATED
            project_ids.append(resp.data['id'])

        # List all projects
        list_resp = auth_client.get('/api/v1/projects/')
        assert list_resp.status_code == status.HTTP_200_OK

        # Clean up
        for pid in project_ids:
            auth_client.delete(f'/api/v1/projects/{pid}/')

    def test_design_component_workflow(self, auth_client, user):
        """Create project → Add components → List → Update → Delete."""
        # Create project
        proj_resp = auth_client.post('/api/v1/projects/', {
            'name': 'Component Test',
            'project_type': 'ui_ux',
        })
        project_id = proj_resp.data['id']

        # Add text component
        comp_resp = auth_client.post('/api/v1/projects/components/', {
            'project': project_id,
            'component_type': 'text',
            'properties': {'text': 'Welcome', 'fontSize': 24, 'color': '#333'},
            'z_index': 1,
        }, format='json')
        assert comp_resp.status_code == status.HTTP_201_CREATED

        # Add shape component
        shape_resp = auth_client.post('/api/v1/projects/components/', {
            'project': project_id,
            'component_type': 'shape',
            'properties': {'shape': 'circle', 'r': 50, 'fill': '#FF0000'},
            'z_index': 2,
        }, format='json')
        assert shape_resp.status_code == status.HTTP_201_CREATED

        # List components
        list_resp = auth_client.get('/api/v1/projects/components/')
        assert list_resp.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestTeamCollaborationWorkflow:
    """Test team creation → invite → manage → share projects."""

    def test_full_team_workflow(self, auth_client, user, user2):
        """Create team → Invite → List members → Add project → Activity."""
        # Step 1: Create team
        team_resp = auth_client.post('/api/v1/teams/', {
            'name': 'E2E Team',
            'slug': 'e2e-team',
            'description': 'End-to-end test team',
        })
        assert team_resp.status_code == status.HTTP_201_CREATED
        team_id = team_resp.data['id']

        # Step 2: List members
        members_resp = auth_client.get(f'/api/v1/teams/{team_id}/members/')
        assert members_resp.status_code == status.HTTP_200_OK

        # Step 3: Invite member
        invite_resp = auth_client.post(
            f'/api/v1/teams/{team_id}/invite_member/',
            {'email': 'newmember@example.com', 'role': 'member'},
        )
        assert invite_resp.status_code in [200, 201]

        # Step 4: Check permissions
        perm_resp = auth_client.get(
            f'/api/v1/teams/{team_id}/my_permissions/'
        )
        assert perm_resp.status_code == status.HTTP_200_OK

        # Step 5: List team projects
        projects_resp = auth_client.get(f'/api/v1/teams/{team_id}/projects/')
        assert projects_resp.status_code == status.HTTP_200_OK

        # Step 6: View activity
        activity_resp = auth_client.get(f'/api/v1/teams/{team_id}/activity/')
        assert activity_resp.status_code == status.HTTP_200_OK

        # Clean up
        auth_client.delete(f'/api/v1/teams/{team_id}/')


@pytest.mark.integration
class TestSubscriptionWorkflow:
    """Test subscription tier browsing and management."""

    def test_subscription_browsing(self, api_client, db):
        """Public users can browse subscription tiers."""
        from decimal import Decimal
        from subscriptions.models import SubscriptionTier

        SubscriptionTier.objects.create(
            name='Free', slug='free-e2e',
            price_monthly=Decimal('0'), price_yearly=Decimal('0'),
            max_projects=5, max_ai_requests_per_month=50,
            max_storage_mb=500, max_collaborators_per_project=1,
            max_exports_per_month=10, is_active=True,
        )
        SubscriptionTier.objects.create(
            name='Pro', slug='pro-e2e',
            price_monthly=Decimal('19.99'), price_yearly=Decimal('199.99'),
            max_projects=100, max_ai_requests_per_month=1000,
            max_storage_mb=10000, max_collaborators_per_project=10,
            max_exports_per_month=500, is_active=True,
        )

        # List tiers (public)
        response = api_client.get('/api/v1/subscriptions/tiers/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestNotificationWorkflow:
    """Test notification lifecycle."""

    def test_notification_lifecycle(self, auth_client, user):
        """Create notifications → Read → Mark all read → Clear."""
        from notifications.models import Notification

        # Create some notifications
        for i in range(3):
            Notification.objects.create(
                user=user,
                notification_type='info',
                title=f'Test Notification {i}',
                message=f'Test message {i}',
            )

        # List notifications
        list_resp = auth_client.get('/api/v1/notifications/')
        assert list_resp.status_code == status.HTTP_200_OK

        # Get unread
        unread_resp = auth_client.get('/api/v1/notifications/unread/')
        assert unread_resp.status_code == status.HTTP_200_OK

        # Mark all read
        mark_resp = auth_client.post('/api/v1/notifications/mark_all_read/')
        assert mark_resp.status_code == status.HTTP_200_OK

        # Clear all
        clear_resp = auth_client.delete('/api/v1/notifications/clear_all/')
        assert clear_resp.status_code in [200, 204]


@pytest.mark.integration
class TestAnalyticsWorkflow:
    """Test analytics tracking and retrieval."""

    def test_analytics_tracking(self, auth_client, user):
        """Track activity → View dashboard → Check AI usage."""
        # Track activities
        auth_client.post('/api/v1/analytics/track/', {
            'activity_type': 'login',
            'metadata': {'source': 'e2e_test'},
        }, format='json')

        auth_client.post('/api/v1/analytics/track/', {
            'activity_type': 'project_create',
            'metadata': {'project_type': 'graphic'},
        }, format='json')

        # View dashboard
        dashboard_resp = auth_client.get('/api/v1/analytics/dashboard/')
        assert dashboard_resp.status_code == status.HTTP_200_OK

        # List activities
        activities_resp = auth_client.get('/api/v1/analytics/activities/')
        assert activities_resp.status_code == status.HTTP_200_OK

        # View AI usage
        ai_resp = auth_client.get('/api/v1/analytics/ai-usage/')
        assert ai_resp.status_code == status.HTTP_200_OK


@pytest.mark.integration
class TestDesignSystemWorkflow:
    """Test design system creation and management."""

    def test_design_system_lifecycle(self, auth_client, user):
        """Create system → Add tokens → Add components → Export."""
        # Create design system
        ds_resp = auth_client.post('/api/v1/design-systems/systems/', {
            'name': 'E2E Design System',
            'description': 'Full lifecycle test',
            'version': '1.0.0',
        })
        assert ds_resp.status_code == status.HTTP_201_CREATED
        ds_id = ds_resp.data['id']

        # Add design tokens
        token_resp = auth_client.post(
            f'/api/v1/design-systems/systems/{ds_id}/tokens/',
            {
                'name': 'primary',
                'category': 'colors',
                'token_type': 'color',
                'value': {'hex': '#3B82F6'},
            },
            format='json',
        )
        assert token_resp.status_code == status.HTTP_201_CREATED

        # Add component
        comp_resp = auth_client.post(
            f'/api/v1/design-systems/systems/{ds_id}/components/',
            {
                'name': 'Button',
                'description': 'Primary action button',
                'category': 'actions',
            },
        )
        assert comp_resp.status_code == status.HTTP_201_CREATED

        # Export tokens
        export_resp = auth_client.get(
            f'/api/v1/design-systems/systems/{ds_id}/export_tokens/',
            {'format': 'css'}
        )
        assert export_resp.status_code == status.HTTP_200_OK

        # List all
        list_resp = auth_client.get('/api/v1/design-systems/systems/')
        assert list_resp.status_code == status.HTTP_200_OK

        # Clean up
        auth_client.delete(f'/api/v1/design-systems/systems/{ds_id}/')

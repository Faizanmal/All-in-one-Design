"""
Unit tests for teams models and API views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from teams.models import Team, TeamMembership, TeamInvitation, TeamProject


@pytest.fixture
def team(user):
    """Create a test team."""
    team = Team.objects.create(
        name='Test Team',
        slug='test-team',
        description='A test team',
        owner=user,
    )
    TeamMembership.objects.create(
        team=team, user=user, role='owner',
        can_create_projects=True, can_edit_projects=True,
        can_delete_projects=True, can_invite_members=True,
        can_manage_members=True,
    )
    return team


@pytest.mark.unit
class TestTeamModel:
    """Tests for Team model."""

    def test_create_team(self, user):
        team = Team.objects.create(
            name='New Team', slug='new-team', owner=user
        )
        assert team.name == 'New Team'
        assert team.owner == user

    def test_team_str(self, team):
        assert 'Test Team' in str(team)

    def test_team_slug_unique(self, user, team):
        with pytest.raises(Exception):
            Team.objects.create(
                name='Another Team', slug='test-team', owner=user
            )

    def test_team_is_active_default(self, team):
        assert team.is_active is True


@pytest.mark.unit
class TestTeamMembership:
    """Tests for TeamMembership model."""

    def test_membership_roles(self, team, user2):
        membership = TeamMembership.objects.create(
            team=team, user=user2, role='member'
        )
        assert membership.role == 'member'

    def test_owner_permissions(self, team, user):
        membership = TeamMembership.objects.get(team=team, user=user)
        assert membership.role == 'owner'
        assert membership.can_manage_members is True

    def test_member_default_permissions(self, team, user2):
        membership = TeamMembership.objects.create(
            team=team, user=user2, role='viewer'
        )
        assert membership.role == 'viewer'


@pytest.mark.unit
class TestTeamInvitation:
    """Tests for TeamInvitation model."""

    def test_create_invitation(self, team, user):
        invitation = TeamInvitation.objects.create(
            team=team,
            email='invitee@example.com',
            invited_by=user,
            role='member',
        )
        assert invitation.status == 'pending'
        assert invitation.token is not None or invitation.token != ''

    def test_invitation_status_choices(self, team, user):
        invitation = TeamInvitation.objects.create(
            team=team, email='x@x.com', invited_by=user, role='member',
            status='pending',
        )
        assert invitation.status == 'pending'


@pytest.mark.api
class TestTeamViewSet:
    """Tests for Team API endpoints."""

    def test_list_teams(self, auth_client, team):
        response = auth_client.get('/api/v1/teams/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_team(self, auth_client, user):
        payload = {
            'name': 'API Team',
            'slug': 'api-team',
            'description': 'Created via API',
        }
        response = auth_client.post('/api/v1/teams/', payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_team(self, auth_client, team):
        response = auth_client.get(f'/api/v1/teams/{team.id}/')
        assert response.status_code == status.HTTP_200_OK

    def test_update_team(self, auth_client, team):
        payload = {'name': 'Updated Team'}
        response = auth_client.patch(f'/api/v1/teams/{team.id}/', payload)
        assert response.status_code == status.HTTP_200_OK

    def test_delete_team(self, auth_client, team):
        response = auth_client.delete(f'/api/v1/teams/{team.id}/')
        assert response.status_code in [200, 204]

    def test_create_team_unauthenticated(self, api_client, db):
        payload = {'name': 'No Auth', 'slug': 'no-auth'}
        response = api_client.post('/api/v1/teams/', payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestTeamMembers:
    """Tests for team member management."""

    def test_list_members(self, auth_client, team):
        response = auth_client.get(f'/api/v1/teams/{team.id}/members/')
        assert response.status_code == status.HTTP_200_OK

    def test_invite_member(self, auth_client, team):
        payload = {'email': 'new@example.com', 'role': 'member'}
        response = auth_client.post(
            f'/api/v1/teams/{team.id}/invite_member/', payload
        )
        assert response.status_code in [200, 201]

    def test_my_permissions(self, auth_client, team):
        response = auth_client.get(
            f'/api/v1/teams/{team.id}/my_permissions/'
        )
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestTeamProjects:
    """Tests for team project management."""

    def test_list_team_projects(self, auth_client, team):
        response = auth_client.get(f'/api/v1/teams/{team.id}/projects/')
        assert response.status_code == status.HTTP_200_OK

    def test_team_activity(self, auth_client, team):
        response = auth_client.get(f'/api/v1/teams/{team.id}/activity/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestTeamInvitationViewSet:
    """Tests for invitation endpoints."""

    def test_list_invitations(self, auth_client, team, user):
        TeamInvitation.objects.create(
            team=team, email='x@x.com', invited_by=user, role='member'
        )
        response = auth_client.get('/api/v1/teams/invitations/')
        assert response.status_code == status.HTTP_200_OK

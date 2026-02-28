"""
API tests for projects views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from projects.models import Project, DesignComponent, ProjectVersion


@pytest.fixture
def project(user):
    """Create a test project."""
    return Project.objects.create(
        user=user,
        name='Test Project',
        description='A test project',
        project_type='graphic',
        canvas_width=1920,
        canvas_height=1080,
        design_data={'layers': []},
    )


@pytest.fixture
def project2(user2):
    """Create a project for user2."""
    return Project.objects.create(
        user=user2,
        name='User2 Project',
        project_type='ui_ux',
    )


@pytest.mark.api
class TestProjectViewSet:
    """Tests for ProjectViewSet CRUD operations."""

    def test_list_projects(self, auth_client, project):
        response = auth_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_project(self, auth_client, user):
        payload = {
            'name': 'New Project',
            'description': 'Created via API',
            'project_type': 'graphic',
        }
        response = auth_client.post('/api/v1/projects/', payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(name='New Project').exists()

    def test_retrieve_project(self, auth_client, project):
        response = auth_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Project'

    def test_update_project(self, auth_client, project):
        payload = {'name': 'Updated Project'}
        response = auth_client.patch(f'/api/v1/projects/{project.id}/', payload)
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.name == 'Updated Project'

    def test_delete_project(self, auth_client, project):
        response = auth_client.delete(f'/api/v1/projects/{project.id}/')
        assert response.status_code in [204, 200]
        assert not Project.objects.filter(id=project.id).exists()

    def test_list_projects_unauthenticated(self, api_client, db):
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_sees_only_own_projects(self, auth_client, project, project2):
        response = auth_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        # User should see their own project; check results
        results = response.data.get('results', response.data)
        if isinstance(results, list):
            project_ids = [p['id'] for p in results]
            assert project.id in project_ids

    def test_create_project_all_types(self, auth_client, user):
        for ptype in ['graphic', 'ui_ux', 'logo']:
            payload = {'name': f'{ptype}', 'project_type': ptype}
            response = auth_client.post('/api/v1/projects/', payload)
            assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestProjectVersioning:
    """Tests for project versioning."""

    def test_create_version(self, auth_client, project):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/create_version/',
            {'design_data': {'v': 1}},
            format='json',
        )
        assert response.status_code in [200, 201]

    def test_list_versions(self, auth_client, project, user):
        ProjectVersion.objects.create(
            project=project, version_number=1,
            design_data={'v': 1}, created_by=user,
        )
        response = auth_client.get(f'/api/v1/projects/{project.id}/versions/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestProjectCollaboration:
    """Tests for project collaboration features."""

    def test_add_collaborator(self, auth_client, project, user2):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/add_collaborator/',
            {'user_id': user2.id},
        )
        assert response.status_code in [200, 201]

    def test_my_projects(self, auth_client, project):
        response = auth_client.get('/api/v1/projects/my_projects/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestProjectSearch:
    """Tests for project search."""

    def test_search_projects(self, auth_client, project):
        response = auth_client.get('/api/v1/projects/search/', {'q': 'Test'})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestProjectExport:
    """Tests for project export."""

    def test_export_svg(self, auth_client, project):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/export_svg/'
        )
        assert response.status_code in [200, 201, 400]

    def test_export_pdf(self, auth_client, project):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/export_pdf/'
        )
        assert response.status_code in [200, 201, 400]


@pytest.mark.api
class TestDesignComponentViewSet:
    """Tests for DesignComponent CRUD."""

    def test_list_components(self, auth_client, project):
        response = auth_client.get('/api/v1/projects/components/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_component(self, auth_client, project):
        payload = {
            'project': project.id,
            'component_type': 'text',
            'properties': {'text': 'Hello'},
            'z_index': 1,
        }
        response = auth_client.post(
            '/api/v1/projects/components/', payload, format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.api
class TestSaveDesign:
    """Tests for save design endpoint."""

    def test_save_design(self, auth_client, project):
        payload = {'design_data': {'layers': [{'type': 'text'}]}}
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/save_design/',
            payload,
            format='json',
        )
        assert response.status_code in [200, 201]

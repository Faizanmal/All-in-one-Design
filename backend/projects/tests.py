"""
Tests for the projects app - project CRUD and permissions.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Project, DesignComponent, ProjectVersion


class ProjectCRUDTests(APITestCase):
    """Test project CRUD operations."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.projects_url = '/api/v1/projects/'
    
    def test_create_project(self):
        """Test creating a new project."""
        payload = {
            'name': 'Test Project',
            'description': 'A test project',
            'project_type': 'graphic',
            'canvas_width': 1920,
            'canvas_height': 1080,
        }
        response = self.client.post(self.projects_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Project')
        self.assertEqual(Project.objects.count(), 1)
    
    def test_list_projects(self):
        """Test listing user's projects."""
        # Create some projects
        Project.objects.create(user=self.user, name='Project 1', project_type='graphic')
        Project.objects.create(user=self.user, name='Project 2', project_type='ui_ux')
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_project(self):
        """Test retrieving a single project."""
        project = Project.objects.create(
            user=self.user, 
            name='Test Project', 
            project_type='graphic'
        )
        
        response = self.client.get(f'{self.projects_url}{project.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Project')
    
    def test_update_project(self):
        """Test updating a project."""
        project = Project.objects.create(
            user=self.user, 
            name='Original Name', 
            project_type='graphic'
        )
        
        payload = {'name': 'Updated Name'}
        response = self.client.patch(f'{self.projects_url}{project.id}/', payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
    
    def test_delete_project(self):
        """Test deleting a project."""
        project = Project.objects.create(
            user=self.user, 
            name='To Delete', 
            project_type='graphic'
        )
        
        response = self.client.delete(f'{self.projects_url}{project.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)


class ProjectPermissionTests(APITestCase):
    """Test project permission enforcement."""
    
    def setUp(self):
        # Create two users
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'pass123!')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'pass123!')
        
        self.token1, _ = Token.objects.get_or_create(user=self.user1)
        self.token2, _ = Token.objects.get_or_create(user=self.user2)
        
        # Create project for user1
        self.project = Project.objects.create(
            user=self.user1,
            name='User1 Project',
            project_type='graphic'
        )
        
        self.projects_url = '/api/v1/projects/'
    
    def test_user_cannot_access_others_project(self):
        """Test that users cannot access other users' projects."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        
        response = self.client.get(f'{self.projects_url}{self.project.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_update_others_project(self):
        """Test that users cannot update other users' projects."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        
        response = self.client.patch(
            f'{self.projects_url}{self.project.id}/',
            {'name': 'Hacked Name'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_delete_others_project(self):
        """Test that users cannot delete other users' projects."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        
        response = self.client.delete(f'{self.projects_url}{self.project.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify project still exists
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())
    
    def test_user_only_sees_own_projects(self):
        """Test that users only see their own projects in list."""
        # Create project for user2
        Project.objects.create(
            user=self.user2,
            name='User2 Project',
            project_type='ui_ux'
        )
        
        # Login as user1
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get(self.projects_url)
        
        # Should only see user1's project
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'User1 Project')


class ProjectValidationTests(APITestCase):
    """Test project input validation."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.projects_url = '/api/v1/projects/'
    
    def test_create_project_without_name(self):
        """Test creating project without name fails."""
        payload = {
            'project_type': 'graphic'
        }
        response = self.client.post(self.projects_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_project_invalid_type(self):
        """Test creating project with invalid type fails."""
        payload = {
            'name': 'Test Project',
            'project_type': 'invalid_type'
        }
        response = self.client.post(self.projects_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_project_with_valid_types(self):
        """Test creating projects with all valid types."""
        valid_types = ['graphic', 'ui_ux', 'logo']
        
        for project_type in valid_types:
            payload = {
                'name': f'{project_type} Project',
                'project_type': project_type
            }
            response = self.client.post(self.projects_url, payload)
            
            self.assertEqual(
                response.status_code, 
                status.HTTP_201_CREATED,
                f"Failed to create {project_type} project"
            )


class ProjectModelTests(TestCase):
    """Test Project model behavior."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='modeltest', email='model@example.com', password='TestPass123!'
        )

    def test_str_representation(self):
        project = Project.objects.create(
            user=self.user, name='My Design', project_type='graphic'
        )
        self.assertEqual(str(project), 'My Design (Graphic Design)')

    def test_default_canvas_values(self):
        project = Project.objects.create(
            user=self.user, name='Defaults', project_type='ui_ux'
        )
        self.assertEqual(project.canvas_width, 1920)
        self.assertEqual(project.canvas_height, 1080)
        self.assertEqual(project.canvas_background, '#FFFFFF')

    def test_json_fields_defaults(self):
        project = Project.objects.create(
            user=self.user, name='JSON Test', project_type='graphic'
        )
        self.assertEqual(project.design_data, {})
        self.assertEqual(project.color_palette, [])
        self.assertEqual(project.suggested_fonts, [])

    def test_collaborators_m2m(self):
        project = Project.objects.create(
            user=self.user, name='Collab', project_type='graphic'
        )
        collab = User.objects.create_user('collab', 'c@example.com', 'Pass123!')
        project.collaborators.add(collab)
        self.assertEqual(project.collaborators.count(), 1)

    def test_ordering_by_updated(self):
        p1 = Project.objects.create(user=self.user, name='First', project_type='graphic')
        p2 = Project.objects.create(user=self.user, name='Second', project_type='graphic')
        projects = list(Project.objects.all())
        self.assertEqual(projects[0].name, 'Second')


class DesignComponentModelTests(TestCase):
    """Test DesignComponent model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='comp', email='comp@example.com', password='TestPass123!'
        )
        self.project = Project.objects.create(
            user=self.user, name='Comp Project', project_type='graphic'
        )

    def test_create_text_component(self):
        comp = DesignComponent.objects.create(
            project=self.project,
            component_type='text',
            properties={'text': 'Hello', 'fontSize': 24},
        )
        self.assertEqual(comp.component_type, 'text')
        self.assertEqual(comp.properties['fontSize'], 24)

    def test_create_shape_component(self):
        comp = DesignComponent.objects.create(
            project=self.project,
            component_type='shape',
            properties={'type': 'rectangle', 'fill': '#FF0000'},
        )
        self.assertEqual(comp.component_type, 'shape')

    def test_cascade_delete_with_project(self):
        DesignComponent.objects.create(
            project=self.project, component_type='text', properties={}
        )
        self.project.delete()
        self.assertEqual(DesignComponent.objects.count(), 0)

    def test_multiple_components_per_project(self):
        for i in range(5):
            DesignComponent.objects.create(
                project=self.project,
                component_type='text',
                properties={'text': f'Element {i}'},
            )
        self.assertEqual(self.project.components.count(), 5)


class ProjectVersionTests(APITestCase):
    """Test project version control via API."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='versionuser', email='v@example.com', password='TestPass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.project = Project.objects.create(
            user=self.user,
            name='Versioned',
            project_type='graphic',
            design_data={'v': 'original'},
        )

    def test_version_created_on_save(self):
        response = self.client.post(
            f'/api/v1/projects/{self.project.id}/save_design/',
            {'design_data': {'v': 'updated'}},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ProjectVersion.objects.filter(project=self.project).count(), 1
        )

    def test_no_version_when_data_unchanged(self):
        response = self.client.post(
            f'/api/v1/projects/{self.project.id}/save_design/',
            {'design_data': {'v': 'original'}},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ProjectVersion.objects.filter(project=self.project).count(), 0
        )

    def test_save_design_requires_data(self):
        response = self.client.post(
            f'/api/v1/projects/{self.project.id}/save_design/',
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectDesignSaveTests(APITestCase):
    """Test design save endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='saveuser', email='s@example.com', password='TestPass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_save_complex_design_data(self):
        project = Project.objects.create(
            user=self.user, name='Complex', project_type='graphic'
        )
        design_data = {
            'elements': [
                {'type': 'rect', 'x': 0, 'y': 0, 'width': 100, 'height': 100, 'fill': '#FF0000'},
                {'type': 'text', 'x': 50, 'y': 50, 'text': 'Hello', 'fontSize': 24},
                {'type': 'circle', 'x': 200, 'y': 200, 'radius': 50, 'fill': '#00FF00'},
            ],
            'canvas': {'width': 1920, 'height': 1080, 'background': '#FFFFFF'},
        }
        response = self.client.post(
            f'/api/v1/projects/{project.id}/save_design/',
            {'design_data': design_data},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(len(project.design_data['elements']), 3)


class PublicProjectTests(APITestCase):
    """Test public project access."""

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'u1@example.com', 'Pass123!')
        self.user2 = User.objects.create_user('user2', 'u2@example.com', 'Pass123!')
        self.token2, _ = Token.objects.get_or_create(user=self.user2)

    def test_public_projects_visible(self):
        Project.objects.create(
            user=self.user1, name='Public', project_type='graphic', is_public=True
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        response = self.client.get('/api/v1/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_projects_hidden(self):
        Project.objects.create(
            user=self.user1, name='Private', project_type='graphic', is_public=False
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token2.key}')
        response = self.client.get('/api/v1/projects/')
        names = [p['name'] for p in response.data] if isinstance(response.data, list) else []
        self.assertNotIn('Private', names)
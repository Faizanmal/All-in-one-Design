"""
Tests for the projects app - project CRUD and permissions.
"""
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import Project


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
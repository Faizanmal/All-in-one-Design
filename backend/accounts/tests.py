"""
Tests for the accounts app - authentication and user management.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


class UserRegistrationTests(APITestCase):
    """Test user registration functionality."""
    
    def setUp(self):
        self.register_url = '/api/v1/auth/register/'
        self.valid_payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
    
    def test_register_user_success(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.valid_payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        
        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='testuser').exists())
    
    def test_register_missing_username(self):
        """Test registration fails without username."""
        payload = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_register_missing_email(self):
        """Test registration fails without email."""
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_missing_password(self):
        """Test registration fails without password."""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_username(self):
        """Test registration fails with duplicate username."""
        # Create first user
        User.objects.create_user('testuser', 'first@example.com', 'password123')
        
        response = self.client.post(self.register_url, self.valid_payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username already exists', response.data['error'])
    
    def test_register_duplicate_email(self):
        """Test registration fails with duplicate email."""
        # Create first user
        User.objects.create_user('firstuser', 'test@example.com', 'password123')
        
        response = self.client.post(self.register_url, self.valid_payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email already exists', response.data['error'])
    
    def test_register_weak_password(self):
        """Test registration fails with weak password."""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'  # Too short and simple
        }
        response = self.client.post(self.register_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Test user login functionality."""
    
    def setUp(self):
        self.login_url = '/api/v1/auth/login/'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
    
    def test_login_success(self):
        """Test successful login."""
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_id'], self.user.id)
    
    def test_login_wrong_password(self):
        """Test login fails with wrong password."""
        payload = {
            'username': 'testuser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Test login fails with nonexistent user."""
        payload = {
            'username': 'nonexistent',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.login_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_credentials(self):
        """Test login fails without credentials."""
        response = self.client.post(self.login_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationTests(APITestCase):
    """Test JWT authentication."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        self.token_url = '/api/token/'
        self.refresh_url = '/api/token/refresh/'
        self.verify_url = '/api/token/verify/'
    
    def test_obtain_token_pair(self):
        """Test obtaining JWT token pair."""
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.token_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_refresh_token(self):
        """Test refreshing JWT token."""
        # First get token pair
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.token_url, payload)
        refresh_token = response.data['refresh']
        
        # Refresh the token
        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_verify_token(self):
        """Test verifying JWT token."""
        # First get token pair
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.token_url, payload)
        access_token = response.data['access']
        
        # Verify the token
        response = self.client.post(self.verify_url, {'token': access_token})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_access_protected_endpoint(self):
        """Test accessing protected endpoint with JWT."""
        # Get token
        payload = {
            'username': 'testuser',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.token_url, payload)
        access_token = response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/v1/projects/')
        
        # Should not be 401 or 403
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenAuthenticationTests(APITestCase):
    """Test Token authentication."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
    
    def test_access_with_token(self):
        """Test accessing protected endpoint with Token auth."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/v1/projects/')
        
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_access_without_token(self):
        """Test accessing protected endpoint without token."""
        response = self.client.get('/api/v1/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_access_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = self.client.get('/api/v1/projects/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
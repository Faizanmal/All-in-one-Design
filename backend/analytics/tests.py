"""
Analytics Tests
"""
from django.test import TestCase
from django.contrib.auth.models import User
from analytics.models import UserActivity


class UserActivityTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
    
    def test_create_activity(self):
        """Test creating user activity"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='login',
            ip_address='127.0.0.1'
        )
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.activity_type, 'login')
    
    def test_activity_ordering(self):
        """Test activities are ordered by timestamp"""
        UserActivity.objects.create(user=self.user, activity_type='login')
        UserActivity.objects.create(user=self.user, activity_type='logout')
        
        activities = UserActivity.objects.filter(user=self.user)
        self.assertEqual(activities.count(), 2)
        # Most recent first
        self.assertEqual(activities.first().activity_type, 'logout')

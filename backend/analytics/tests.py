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

    def test_activity_metadata(self):
        """Test activity metadata JSON field"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='project_create',
            metadata={'project_id': 1, 'project_name': 'Test'}
        )
        self.assertEqual(activity.metadata['project_id'], 1)

    def test_activity_types(self):
        """Test all activity types can be created"""
        types = ['login', 'logout', 'project_create', 'project_update',
                 'project_delete', 'project_export', 'ai_generation',
                 'asset_upload', 'template_use', 'collaboration_invite']
        for activity_type in types:
            UserActivity.objects.create(user=self.user, activity_type=activity_type)
        self.assertEqual(UserActivity.objects.filter(user=self.user).count(), len(types))

    def test_activity_str(self):
        """Test activity string representation"""
        activity = UserActivity.objects.create(
            user=self.user, activity_type='login'
        )
        self.assertIn('testuser', str(activity))
        self.assertIn('login', str(activity))

    def test_activity_duration(self):
        """Test activity duration tracking"""
        activity = UserActivity.objects.create(
            user=self.user,
            activity_type='ai_generation',
            duration_ms=1500
        )
        self.assertEqual(activity.duration_ms, 1500)


class ProjectAnalyticsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        from projects.models import Project
        self.project = Project.objects.create(
            user=self.user, name='Test', project_type='graphic'
        )

    def test_create_analytics(self):
        from analytics.models import ProjectAnalytics
        analytics = ProjectAnalytics.objects.create(
            project=self.project,
            view_count=10,
            edit_count=5,
        )
        self.assertEqual(analytics.view_count, 10)
        self.assertEqual(analytics.edit_count, 5)
        self.assertEqual(analytics.export_count, 0)

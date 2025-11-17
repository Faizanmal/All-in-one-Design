from django.test import TestCase
from django.contrib.auth.models import User
from .models import Team, TeamMembership, Comment


class TeamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.team = Team.objects.create(
            name='Test Team',
            slug='test-team',
            owner=self.user
        )
    
    def test_team_creation(self):
        """Test team is created successfully"""
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.owner, self.user)
    
    def test_team_membership(self):
        """Test team membership creation"""
        membership = TeamMembership.objects.create(
            team=self.team,
            user=self.user,
            role='owner'
        )
        self.assertEqual(membership.role, 'owner')
        self.assertTrue(membership.can_create_projects)
        self.assertTrue(membership.can_manage_members)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        from projects.models import Project
        self.project = Project.objects.create(
            name='Test Project',
            user=self.user,
            project_type='graphic'
        )
    
    def test_comment_creation(self):
        """Test comment is created successfully"""
        comment = Comment.objects.create(
            project=self.project,
            user=self.user,
            content='Test comment'
        )
        self.assertEqual(comment.content, 'Test comment')
        self.assertFalse(comment.is_resolved)

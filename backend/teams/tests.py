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


    def test_team_str(self):
        """Test team string representation"""
        self.assertEqual(str(self.team), 'Test Team')

    def test_team_member_count(self):
        """Test member count property"""
        self.assertEqual(self.team.member_count, 0)
        TeamMembership.objects.create(team=self.team, user=self.user, role='owner')
        self.assertEqual(self.team.member_count, 1)

    def test_admin_permissions(self):
        """Test admin role auto-assigns correct permissions"""
        admin_user = User.objects.create_user(username='admin', email='admin@example.com')
        membership = TeamMembership.objects.create(
            team=self.team, user=admin_user, role='admin'
        )
        self.assertTrue(membership.can_create_projects)
        self.assertTrue(membership.can_edit_projects)
        self.assertTrue(membership.can_invite_members)

    def test_viewer_permissions(self):
        """Test viewer role auto-assigns limited permissions"""
        viewer = User.objects.create_user(username='viewer', email='viewer@example.com')
        membership = TeamMembership.objects.create(
            team=self.team, user=viewer, role='viewer'
        )
        self.assertFalse(membership.can_create_projects)
        self.assertFalse(membership.can_delete_projects)
        self.assertFalse(membership.can_manage_members)

    def test_unique_membership(self):
        """Test user can't join same team twice"""
        TeamMembership.objects.create(team=self.team, user=self.user, role='owner')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TeamMembership.objects.create(team=self.team, user=self.user, role='member')


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

    def test_resolve_comment(self):
        """Test resolving a comment"""
        comment = Comment.objects.create(
            project=self.project,
            user=self.user,
            content='Fix this'
        )
        comment.is_resolved = True
        comment.save()
        comment.refresh_from_db()
        self.assertTrue(comment.is_resolved)


class TeamAPITests(TestCase):
    """Test team API patterns"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='Pass123!'
        )
        self.team = Team.objects.create(
            name='API Team', slug='api-team', owner=self.user
        )

    def test_team_is_active_default(self):
        self.assertTrue(self.team.is_active)

    def test_max_members_default(self):
        self.assertEqual(self.team.max_members, 10)

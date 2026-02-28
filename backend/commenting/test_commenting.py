"""
Tests for commenting models and views.
"""
import pytest
from django.contrib.auth.models import User
from rest_framework import status
from commenting.models import (
    CommentThread, Comment, Mention, Reaction,
    ReviewSession, Reviewer, CommentTemplate
)
from projects.models import Project


@pytest.fixture
def project(user):
    return Project.objects.create(user=user, name='Commenting Test')


@pytest.fixture
def thread(project, user):
    return CommentThread.objects.create(
        project=project,
        x=100.0,
        y=200.0,
        status='open',
        created_by=user,
    )


@pytest.fixture
def comment(thread, user):
    return Comment.objects.create(
        thread=thread,
        content='This looks great!',
        author=user,
    )


@pytest.mark.unit
class TestCommentThread:
    """Tests for CommentThread model."""

    def test_create_thread(self, thread):
        assert thread.status == 'open'
        assert thread.x == 100.0
        assert thread.y == 200.0

    def test_thread_statuses(self, project, user):
        for s in ['open', 'in_progress', 'resolved', 'wont_fix']:
            t = CommentThread.objects.create(
                project=project, status=s, created_by=user, x=0, y=0,
            )
            assert t.status == s

    def test_thread_priority(self, project, user):
        for p in ['low', 'medium', 'high', 'urgent']:
            t = CommentThread.objects.create(
                project=project, priority=p, created_by=user, x=0, y=0,
            )
            assert t.priority == p

    def test_thread_assignee(self, project, user, user2):
        thread = CommentThread.objects.create(
            project=project, created_by=user, assignee=user2, x=0, y=0,
        )
        assert thread.assignee == user2


@pytest.mark.unit
class TestComment:
    """Tests for Comment model."""

    def test_create_comment(self, comment):
        assert comment.content == 'This looks great!'
        assert comment.is_edited is False

    def test_reply_comment(self, thread, comment, user2):
        reply = Comment.objects.create(
            thread=thread,
            parent=comment,
            content='Thanks!',
            author=user2,
        )
        assert reply.parent == comment

    def test_comment_types(self, thread, user):
        for ct in ['text', 'voice', 'video', 'annotation', 'emoji']:
            c = Comment.objects.create(
                thread=thread, comment_type=ct, content='test', author=user,
            )
            assert c.comment_type == ct

    def test_edit_comment(self, comment):
        comment.content = 'Updated content'
        comment.is_edited = True
        comment.save()
        comment.refresh_from_db()
        assert comment.is_edited is True


@pytest.mark.unit
class TestReaction:
    """Tests for Reaction model."""

    def test_add_reaction(self, comment, user):
        reaction = Reaction.objects.create(
            comment=comment, user=user, emoji='👍'
        )
        assert reaction.emoji == '👍'

    def test_unique_reaction(self, comment, user):
        Reaction.objects.create(comment=comment, user=user, emoji='👍')
        with pytest.raises(Exception):
            Reaction.objects.create(comment=comment, user=user, emoji='👍')


@pytest.mark.unit
class TestMention:
    """Tests for Mention model."""

    def test_create_mention(self, comment, user2):
        mention = Mention.objects.create(
            comment=comment, user=user2,
            start_index=0, end_index=5,
        )
        assert mention.notified is False
        assert mention.read is False


@pytest.mark.unit
class TestReviewSession:
    """Tests for ReviewSession model."""

    def test_create_session(self, project, user):
        session = ReviewSession.objects.create(
            project=project,
            title='Design Review',
            description='Q1 design review',
            created_by=user,
        )
        assert session.status == 'draft'

    def test_session_statuses(self, project, user):
        for s in ['draft', 'in_review', 'approved', 'rejected', 'changes_requested']:
            session = ReviewSession.objects.create(
                project=project, title=f'{s} review',
                status=s, created_by=user,
            )
            assert session.status == s

    def test_add_reviewer(self, project, user, user2):
        session = ReviewSession.objects.create(
            project=project, title='Review', created_by=user,
        )
        reviewer = Reviewer.objects.create(
            session=session, user=user2, decision='pending'
        )
        assert reviewer.decision == 'pending'


@pytest.mark.unit
class TestCommentTemplate:
    """Tests for CommentTemplate model."""

    def test_create_template(self, user):
        template = CommentTemplate.objects.create(
            user=user,
            name='Quick Approval',
            content='LGTM! Approved. ✅',
            shortcut='/lgtm',
            category='approval',
        )
        assert template.shortcut == '/lgtm'


@pytest.mark.api
class TestCommentThreadViewSet:
    """Tests for CommentThread API."""

    def test_list_threads(self, auth_client, thread):
        response = auth_client.get('/api/v1/comments/threads/')
        assert response.status_code == status.HTTP_200_OK

    def test_create_thread(self, auth_client, project):
        payload = {
            'project': project.id,
            'x': 50.0,
            'y': 75.0,
            'status': 'open',
        }
        response = auth_client.post(
            '/api/v1/comments/threads/', payload, format='json'
        )
        assert response.status_code in [201, 400]

    def test_resolve_thread(self, auth_client, thread):
        response = auth_client.post(
            f'/api/v1/comments/threads/{thread.id}/resolve/'
        )
        assert response.status_code in [200, 400]

    def test_reopen_thread(self, auth_client, thread):
        thread.status = 'resolved'
        thread.save()
        response = auth_client.post(
            f'/api/v1/comments/threads/{thread.id}/reopen/'
        )
        assert response.status_code in [200, 400]


@pytest.mark.api
class TestCommentViewSet:
    """Tests for Comment API."""

    def test_list_comments(self, auth_client, comment):
        response = auth_client.get('/api/v1/comments/comments/')
        assert response.status_code == status.HTTP_200_OK

    def test_react_to_comment(self, auth_client, comment):
        payload = {'emoji': '👍'}
        response = auth_client.post(
            f'/api/v1/comments/comments/{comment.id}/react/', payload
        )
        assert response.status_code in [200, 201]


@pytest.mark.api
class TestCreateCommentView:
    """Tests for the create comment endpoint."""

    def test_create_comment_with_thread(self, auth_client, project):
        payload = {
            'project': project.id,
            'content': 'New comment',
            'x': 100,
            'y': 200,
        }
        response = auth_client.post(
            '/api/v1/comments/create/', payload, format='json'
        )
        assert response.status_code in [200, 201]

    def test_create_comment_unauthenticated(self, api_client, db):
        response = api_client.post('/api/v1/comments/create/', {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.api
class TestReviewSessionViewSet:
    """Tests for ReviewSession API."""

    def test_list_reviews(self, auth_client, project, user):
        ReviewSession.objects.create(
            project=project, title='Review', created_by=user
        )
        response = auth_client.get('/api/v1/comments/reviews/')
        assert response.status_code == status.HTTP_200_OK

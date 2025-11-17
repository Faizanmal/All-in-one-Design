from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamInvitationViewSet, CommentViewSet, TeamActivityViewSet
from .collaboration_views import TaskViewSet, TeamChatViewSet, TeamChatMessageViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'invitations', TeamInvitationViewSet, basename='invitation')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'activities', TeamActivityViewSet, basename='activity')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'chats', TeamChatViewSet, basename='team-chat')
router.register(r'messages', TeamChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
]

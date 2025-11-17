from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, TeamInvitationViewSet, CommentViewSet, TeamActivityViewSet

router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'invitations', TeamInvitationViewSet, basename='invitation')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'activities', TeamActivityViewSet, basename='activity')

urlpatterns = [
    path('', include(router.urls)),
]

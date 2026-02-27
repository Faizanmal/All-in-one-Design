from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialAccountViewSet, ScheduledPostViewSet

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='social-account')
router.register(r'posts', ScheduledPostViewSet, basename='scheduled-post')

urlpatterns = [
    path('', include(router.urls)),
]

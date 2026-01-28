from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'threads', views.CommentThreadViewSet, basename='comment-thread')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'reviews', views.ReviewSessionViewSet, basename='review-session')
router.register(r'notifications', views.CommentNotificationViewSet, basename='comment-notification')
router.register(r'templates', views.CommentTemplateViewSet, basename='comment-template')

urlpatterns = [
    path('', include(router.urls)),
    path('create/', views.CreateCommentView.as_view(), name='create-comment'),
]

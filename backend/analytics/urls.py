"""
Analytics URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'activities', views.UserActivityViewSet, basename='activity')
router.register(r'ai-usage', views.AIUsageMetricsViewSet, basename='ai-usage')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats, name='dashboard-stats'),
    path('projects/<int:project_id>/', views.project_analytics, name='project-analytics'),
    path('track/', views.track_activity, name='track-activity'),
]

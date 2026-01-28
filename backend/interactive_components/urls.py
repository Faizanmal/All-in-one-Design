"""
Interactive Components URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'components', views.InteractiveComponentViewSet, basename='interactive-component')
router.register(r'states', views.ComponentStateViewSet, basename='component-state')
router.register(r'interactions', views.ComponentInteractionViewSet, basename='component-interaction')
router.register(r'templates', views.InteractiveTemplateViewSet, basename='interactive-template')

urlpatterns = [
    path('', include(router.urls)),
    path('preview/', views.InteractionPreviewView.as_view(), name='interaction-preview'),
]

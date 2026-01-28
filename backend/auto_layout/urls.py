"""
URL configuration for auto_layout app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'frames', views.AutoLayoutFrameViewSet, basename='auto-layout-frame')
router.register(r'children', views.AutoLayoutChildViewSet, basename='auto-layout-child')
router.register(r'constraints', views.LayoutConstraintViewSet, basename='layout-constraint')
router.register(r'breakpoints', views.ResponsiveBreakpointViewSet, basename='responsive-breakpoint')
router.register(r'overrides', views.ResponsiveOverrideViewSet, basename='responsive-override')
router.register(r'presets', views.LayoutPresetViewSet, basename='layout-preset')

app_name = 'auto_layout'

urlpatterns = [
    path('', include(router.urls)),
]

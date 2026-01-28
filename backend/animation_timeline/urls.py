"""
URL configuration for animation_timeline app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.AnimationProjectViewSet, basename='animation-project')
router.register(r'compositions', views.AnimationCompositionViewSet, basename='animation-composition')
router.register(r'layers', views.AnimationLayerViewSet, basename='animation-layer')
router.register(r'tracks', views.AnimationTrackViewSet, basename='animation-track')
router.register(r'keyframes', views.AnimationKeyframeViewSet, basename='animation-keyframe')
router.register(r'easing-presets', views.EasingPresetViewSet, basename='easing-preset')
router.register(r'effects', views.AnimationEffectViewSet, basename='animation-effect')
router.register(r'exports', views.LottieExportViewSet, basename='lottie-export')
router.register(r'sequences', views.AnimationSequenceViewSet, basename='animation-sequence')

app_name = 'animation_timeline'

urlpatterns = [
    path('', include(router.urls)),
]

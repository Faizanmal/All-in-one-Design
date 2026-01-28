from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnimationViewSet, LottieAnimationViewSet, MicroInteractionViewSet,
    AnimationPresetViewSet, AnimationTimelineViewSet, get_easing_presets
)

router = DefaultRouter()
router.register(r'animations', AnimationViewSet, basename='animation')
router.register(r'lottie', LottieAnimationViewSet, basename='lottie')
router.register(r'interactions', MicroInteractionViewSet, basename='micro-interaction')
router.register(r'presets', AnimationPresetViewSet, basename='animation-preset')
router.register(r'timelines', AnimationTimelineViewSet, basename='animation-timeline')

urlpatterns = [
    path('', include(router.urls)),
    path('easing-presets/', get_easing_presets, name='easing-presets'),
]

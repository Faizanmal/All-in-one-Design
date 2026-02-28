from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .video_timeline_views import (
    create_timeline, add_track, add_clip, split_clip, trim_clip,
    set_transition, add_text_overlay, add_keyframe, validate_timeline,
    get_transitions, get_export_presets, get_text_effects, preview_frames,
)

router = DefaultRouter()
router.register(r'videos', views.VideoAssetViewSet, basename='video-asset')
router.register(r'gifs', views.GIFAssetViewSet, basename='gif-asset')
router.register(r'lottie', views.LottieAssetViewSet, basename='lottie-asset')
router.register(r'placements', views.MediaPlacementViewSet, basename='media-placement')
router.register(r'exports', views.AnimatedExportViewSet, basename='animated-export')
router.register(r'frames', views.VideoFrameViewSet, basename='video-frame')

urlpatterns = [
    path('', include(router.urls)),

    # Video Timeline Editing endpoints
    path('timeline/create/', create_timeline, name='timeline-create'),
    path('timeline/track/', add_track, name='timeline-add-track'),
    path('timeline/clip/', add_clip, name='timeline-add-clip'),
    path('timeline/clip/split/', split_clip, name='timeline-split-clip'),
    path('timeline/clip/trim/', trim_clip, name='timeline-trim-clip'),
    path('timeline/clip/transition/', set_transition, name='timeline-set-transition'),
    path('timeline/text/', add_text_overlay, name='timeline-add-text'),
    path('timeline/keyframe/', add_keyframe, name='timeline-add-keyframe'),
    path('timeline/validate/', validate_timeline, name='timeline-validate'),
    path('timeline/transitions/', get_transitions, name='timeline-transitions'),
    path('timeline/export-presets/', get_export_presets, name='timeline-export-presets'),
    path('timeline/text-effects/', get_text_effects, name='timeline-text-effects'),
    path('timeline/preview/', preview_frames, name='timeline-preview'),
]

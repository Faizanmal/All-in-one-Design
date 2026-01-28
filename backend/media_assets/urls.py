from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'videos', views.VideoAssetViewSet, basename='video-asset')
router.register(r'gifs', views.GIFAssetViewSet, basename='gif-asset')
router.register(r'lottie', views.LottieAssetViewSet, basename='lottie-asset')
router.register(r'placements', views.MediaPlacementViewSet, basename='media-placement')
router.register(r'exports', views.AnimatedExportViewSet, basename='animated-export')
router.register(r'frames', views.VideoFrameViewSet, basename='video-frame')

urlpatterns = [
    path('', include(router.urls)),
]

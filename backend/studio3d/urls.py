from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    Model3DViewSet, Scene3DViewSet, Prototype3DViewSet,
    ARPreviewViewSet, Conversion3DTo2DViewSet,
    public_prototype, public_ar_preview
)

router = DefaultRouter()
router.register(r'models', Model3DViewSet, basename='model-3d')
router.register(r'scenes', Scene3DViewSet, basename='scene-3d')
router.register(r'prototypes', Prototype3DViewSet, basename='prototype-3d')
router.register(r'ar-previews', ARPreviewViewSet, basename='ar-preview')
router.register(r'conversions', Conversion3DTo2DViewSet, basename='conversion-3d-to-2d')

urlpatterns = [
    path('', include(router.urls)),
    # Public access endpoints
    path('share/prototype/<str:share_link>/', public_prototype, name='public-prototype'),
    path('share/ar/<str:share_link>/', public_ar_preview, name='public-ar-preview'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tests', views.AccessibilityTestViewSet, basename='accessibility-test')
router.register(r'issues', views.AccessibilityIssueViewSet, basename='accessibility-issue')
router.register(r'color-blindness', views.ColorBlindnessSimulationViewSet, basename='color-blindness-simulation')
router.register(r'screen-reader', views.ScreenReaderPreviewViewSet, basename='screen-reader-preview')
router.register(r'focus-order', views.FocusOrderTestViewSet, basename='focus-order-test')
router.register(r'contrast-checks', views.ContrastCheckViewSet, basename='contrast-check')
router.register(r'guidelines', views.AccessibilityGuidelineViewSet, basename='accessibility-guideline')

urlpatterns = [
    path('', include(router.urls)),
    path('simulate-color-blindness/', views.SimulateColorBlindnessView.as_view(), name='simulate-color-blindness'),
    path('generate-screen-reader-preview/', views.GenerateScreenReaderPreviewView.as_view(), name='generate-screen-reader-preview'),
    path('test-focus-order/', views.TestFocusOrderView.as_view(), name='test-focus-order'),
    path('check-contrast/', views.CheckContrastView.as_view(), name='check-contrast'),
]

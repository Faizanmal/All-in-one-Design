from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ABTestViewSet, PerformanceAnalysisViewSet, DeviceCompatibilityViewSet,
    SmartLayoutSuggestionViewSet, OptimizationReportViewSet,
    analyze_design, predict_behavior
)

router = DefaultRouter()
router.register(r'ab-tests', ABTestViewSet, basename='ab-test')
router.register(r'performance', PerformanceAnalysisViewSet, basename='performance-analysis')
router.register(r'device-compatibility', DeviceCompatibilityViewSet, basename='device-compatibility')
router.register(r'layout-suggestions', SmartLayoutSuggestionViewSet, basename='layout-suggestion')
router.register(r'reports', OptimizationReportViewSet, basename='optimization-report')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/', analyze_design, name='analyze-design'),
    path('predict-behavior/', predict_behavior, name='predict-behavior'),
]

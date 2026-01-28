"""
URL configuration for design_qa app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rule-sets', views.LintRuleSetViewSet, basename='lint-rule-set')
router.register(r'rules', views.LintRuleViewSet, basename='lint-rule')
router.register(r'lint-reports', views.DesignLintReportViewSet, basename='design-lint-report')
router.register(r'lint-issues', views.LintIssueViewSet, basename='lint-issue')
router.register(r'accessibility-checks', views.AccessibilityCheckViewSet, basename='accessibility-check')
router.register(r'accessibility-reports', views.AccessibilityReportViewSet, basename='accessibility-report')
router.register(r'accessibility-issues', views.AccessibilityIssueViewSet, basename='accessibility-issue')
router.register(r'style-reports', views.StyleUsageReportViewSet, basename='style-usage-report')
router.register(r'ignore-rules', views.LintIgnoreRuleViewSet, basename='lint-ignore-rule')

app_name = 'design_qa'

urlpatterns = [
    path('', include(router.urls)),
]

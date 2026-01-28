from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TimeTrackerViewSet, TimeEntryViewSet, TaskViewSet, TaskCommentViewSet,
    ProjectEstimateViewSet, InvoiceViewSet, TimeReportViewSet,
    WeeklyGoalViewSet, DashboardView
)

router = DefaultRouter()
router.register(r'trackers', TimeTrackerViewSet, basename='time-tracker')
router.register(r'entries', TimeEntryViewSet, basename='time-entry')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', TaskCommentViewSet, basename='task-comment')
router.register(r'estimates', ProjectEstimateViewSet, basename='project-estimate')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'reports', TimeReportViewSet, basename='time-report')
router.register(r'goals', WeeklyGoalViewSet, basename='weekly-goal')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='time-dashboard'),
]

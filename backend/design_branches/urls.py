"""
URL configuration for design_branches app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'branches', views.DesignBranchViewSet, basename='design-branch')
router.register(r'commits', views.DesignCommitViewSet, basename='design-commit')
router.register(r'merges', views.BranchMergeViewSet, basename='branch-merge')
router.register(r'conflicts', views.MergeConflictViewSet, basename='merge-conflict')
router.register(r'reviews', views.BranchReviewViewSet, basename='branch-review')
router.register(r'comments', views.ReviewCommentViewSet, basename='review-comment')
router.register(r'tags', views.DesignTagViewSet, basename='design-tag')
router.register(r'comparisons', views.BranchComparisonViewSet, basename='branch-comparison')

app_name = 'design_branches'

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, PermissionViewSet, UserRoleViewSet,
    ProjectPermissionViewSet, PagePermissionViewSet,
    BranchProtectionViewSet, AccessLogViewSet, ShareLinkViewSet,
    PermissionCheckView, EffectivePermissionsView, ValidateShareLinkView
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'project-permissions', ProjectPermissionViewSet, basename='project-permission')
router.register(r'page-permissions', PagePermissionViewSet, basename='page-permission')
router.register(r'branch-protections', BranchProtectionViewSet, basename='branch-protection')
router.register(r'logs', AccessLogViewSet, basename='access-log')
router.register(r'share-links', ShareLinkViewSet, basename='share-link')

urlpatterns = [
    path('', include(router.urls)),
    path('check/', PermissionCheckView.as_view(), name='permission-check'),
    path('effective/', EffectivePermissionsView.as_view(), name='effective-permissions'),
    path('validate-link/', ValidateShareLinkView.as_view(), name='validate-share-link'),
]

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

from .models import (
    Role, Permission, RolePermission, UserRole, ProjectPermission,
    PagePermission, BranchProtection, AccessLog, PermissionTemplate, ShareLink
)
from .serializers import (
    RoleListSerializer, RoleSerializer, RoleCreateSerializer,
    PermissionSerializer, UserRoleSerializer,
    ProjectPermissionSerializer, ProjectPermissionCreateSerializer,
    PagePermissionSerializer, BranchProtectionSerializer,
    AccessLogSerializer, PermissionTemplateSerializer,
    ShareLinkSerializer, ShareLinkCreateSerializer,
    PermissionCheckSerializer, BulkPermissionUpdateSerializer, InviteUserSerializer
)
from .services import PermissionChecker, PermissionManager


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for roles"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RoleCreateSerializer
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer
    
    def get_queryset(self):
        queryset = Role.objects.all()
        
        # Filter by team
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(Q(team_id=team_id) | Q(team__isnull=True))
        
        # Filter by type
        role_type = self.request.query_params.get('type')
        if role_type:
            queryset = queryset.filter(role_type=role_type)
        
        return queryset
    
    def perform_create(self, serializer):
        role = serializer.save()
        
        # Assign permissions if provided
        permission_ids = self.request.data.get('permission_ids', [])
        for perm_id in permission_ids:
            RolePermission.objects.create(
                role=role,
                permission_id=perm_id,
                allow=True
            )
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Add permission to role"""
        role = self.get_object()
        
        if role.is_system:
            return Response(
                {'error': 'Cannot modify system roles'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permission_id = request.data.get('permission_id')
        RolePermission.objects.get_or_create(
            role=role,
            permission_id=permission_id,
            defaults={'allow': True}
        )
        
        return Response({'status': 'permission added'})
    
    @action(detail=True, methods=['post'])
    def remove_permission(self, request, pk=None):
        """Remove permission from role"""
        role = self.get_object()
        
        if role.is_system:
            return Response(
                {'error': 'Cannot modify system roles'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permission_id = request.data.get('permission_id')
        RolePermission.objects.filter(role=role, permission_id=permission_id).delete()
        
        return Response({'status': 'permission removed'})
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get role members"""
        role = self.get_object()
        assignments = UserRole.objects.filter(role=role).select_related('user')
        return Response(UserRoleSerializer(assignments, many=True).data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for permissions (read-only)"""
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all()
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get permissions grouped by category"""
        permissions = Permission.objects.all()
        
        by_category = {}
        for perm in permissions:
            if perm.category not in by_category:
                by_category[perm.category] = []
            by_category[perm.category].append(PermissionSerializer(perm).data)
        
        return Response(by_category)


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for user role assignments"""
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = UserRole.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by team
        team_id = self.request.query_params.get('team')
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        
        return queryset.select_related('user', 'role', 'team', 'project')
    
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_roles(self, request):
        """Get current user's roles"""
        roles = UserRole.objects.filter(user=request.user).select_related('role')
        return Response(UserRoleSerializer(roles, many=True).data)


class ProjectPermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for project permissions"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectPermissionCreateSerializer
        return ProjectPermissionSerializer
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = ProjectPermission.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('user', 'project', 'invited_by')
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        
        # Set permission flags based on level
        PermissionManager.grant_project_permission(
            project=data['project'],
            user=data.get('user'),
            level=data['permission_level'],
            granted_by=self.request.user,
            expires_at=data.get('expires_at')
        )
    
    @action(detail=False, methods=['post'])
    def invite(self, request):
        """Invite user by email"""
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project_id = request.data.get('project_id')
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user exists
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Grant permission directly
            perm = PermissionManager.grant_project_permission(
                project=project,
                user=user,
                level=serializer.validated_data['permission_level'],
                granted_by=request.user
            )
        except User.DoesNotExist:
            # Create pending invite
            import secrets
            perm = ProjectPermission.objects.create(
                project=project,
                email=email,
                permission_level=serializer.validated_data['permission_level'],
                is_pending=True,
                invite_token=secrets.token_urlsafe(32),
                invited_by=request.user,
                invited_at=timezone.now()
            )
            # TODO: Send invite email
        
        return Response(ProjectPermissionSerializer(perm).data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update permissions"""
        serializer = BulkPermissionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project_id = request.data.get('project_id')
        user_ids = serializer.validated_data['user_ids']
        level = serializer.validated_data['permission_level']
        
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)
            PermissionManager.grant_project_permission(
                project=project,
                user=user,
                level=level,
                granted_by=request.user,
                expires_at=serializer.validated_data.get('expires_at')
            )
        
        return Response({'updated': len(user_ids)})


class PagePermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for page permissions"""
    serializer_class = PagePermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = PagePermission.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('user', 'project')


class BranchProtectionViewSet(viewsets.ModelViewSet):
    """ViewSet for branch protection rules"""
    serializer_class = BranchProtectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = BranchProtection.objects.all()
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset


class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for access logs (read-only)"""
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AccessLog.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by target
        target_type = self.request.query_params.get('target_type')
        target_id = self.request.query_params.get('target_id')
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        
        return queryset.select_related('user')[:1000]


class ShareLinkViewSet(viewsets.ModelViewSet):
    """ViewSet for share links"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ShareLinkCreateSerializer
        return ShareLinkSerializer
    
    def get_queryset(self):
        project_id = self.request.query_params.get('project')
        queryset = ShareLink.objects.filter(created_by=self.request.user)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.select_related('project')
    
    def perform_create(self, serializer):
        import secrets
        serializer.save(
            created_by=self.request.user,
            token=secrets.token_urlsafe(32)
        )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate share link"""
        link = self.get_object()
        link.is_active = False
        link.save()
        return Response({'status': 'deactivated'})


class PermissionCheckView(APIView):
    """Check permissions for current user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        project_id = request.data.get('project_id')
        permission = request.data.get('permission', 'view')
        page_id = request.data.get('page_id')
        
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        checker = PermissionChecker(request.user)
        has_permission = checker.has_project_permission(project, permission, page_id)
        effective = checker.get_effective_permissions(project)
        
        return Response({
            'has_permission': has_permission,
            'permission_level': effective['level'],
            'source': 'project_permission' if effective['level'] != 'none' else 'no_access',
        })


class EffectivePermissionsView(APIView):
    """Get effective permissions for current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        project_id = request.query_params.get('project_id')
        
        from projects.models import Project
        project = get_object_or_404(Project, id=project_id)
        
        checker = PermissionChecker(request.user)
        permissions = checker.get_effective_permissions(project)
        
        return Response(permissions)


class ValidateShareLinkView(APIView):
    """Validate a share link"""
    permission_classes = []  # Public endpoint
    
    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        
        result = PermissionManager.validate_share_link(token)
        
        if not result:
            return Response(
                {'error': 'Invalid or expired link'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if result['requires_password']:
            link = ShareLink.objects.get(token=token)
            # In production, use proper password hashing
            if password != link.password:
                return Response(
                    {'error': 'Invalid password'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # Increment use count
        ShareLink.objects.filter(token=token).update(
            use_count=models.F('use_count') + 1
        )
        
        return Response(result)


from django.db import models  # Import at end to avoid circular import

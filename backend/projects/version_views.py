"""
Version Control API Views and Serializers
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .version_models import ProjectSnapshot, VersionDiff, VersionComment, VersionService
from .models import Project


# ============================================
# SERIALIZERS
# ============================================

class ProjectSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for project snapshots."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectSnapshot
        fields = [
            'id', 'version_number', 'version_label',
            'canvas_settings', 'components_count', 'content_hash',
            'data_size_bytes', 'change_summary', 'change_type',
            'created_by', 'created_by_username',
            'parent_snapshot', 'branch_name', 'is_branch_head',
            'thumbnail_url', 'created_at',
        ]
        read_only_fields = [
            'id', 'version_number', 'content_hash', 'data_size_bytes',
            'created_at', 'created_by',
        ]
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None


class ProjectSnapshotDetailSerializer(ProjectSnapshotSerializer):
    """Detailed serializer including design data."""
    
    class Meta(ProjectSnapshotSerializer.Meta):
        fields = ProjectSnapshotSerializer.Meta.fields + ['design_data']


class VersionCommentSerializer(serializers.ModelSerializer):
    """Serializer for version comments."""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = VersionComment
        fields = [
            'id', 'snapshot', 'user', 'username',
            'content', 'component_id',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class CreateSnapshotSerializer(serializers.Serializer):
    """Serializer for creating snapshots."""
    label = serializers.CharField(max_length=100, required=False, default='')
    change_summary = serializers.CharField(required=False, default='')
    branch_name = serializers.CharField(max_length=100, default='main')


class RestoreSnapshotSerializer(serializers.Serializer):
    """Serializer for restore requests."""
    create_backup = serializers.BooleanField(default=True)


class CreateBranchSerializer(serializers.Serializer):
    """Serializer for creating branches."""
    branch_name = serializers.CharField(max_length=100)
    from_version = serializers.IntegerField(required=False)


class DiffRequestSerializer(serializers.Serializer):
    """Serializer for diff requests."""
    from_version = serializers.IntegerField()
    to_version = serializers.IntegerField()


# ============================================
# VIEWS
# ============================================

class ProjectVersionViewSet(viewsets.ViewSet):
    """
    ViewSet for managing project versions.
    """
    permission_classes = [IsAuthenticated]
    
    def get_project(self, project_id):
        """Get project and verify access."""
        project = get_object_or_404(Project, id=project_id)
        
        # Check access
        if project.user != self.request.user and \
           self.request.user not in project.collaborators.all():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have access to this project")
        
        return project
    
    def list(self, request, project_id=None):
        """
        List version history for a project.
        
        GET /api/v1/projects/{project_id}/versions/
        """
        project = self.get_project(project_id)
        service = VersionService(project)
        
        branch = request.query_params.get('branch')
        limit = int(request.query_params.get('limit', 50))
        include_diff = request.query_params.get('include_diff', 'false').lower() == 'true'
        
        history = service.get_history(
            branch_name=branch,
            limit=limit,
            include_diff=include_diff
        )
        
        return Response({
            'project_id': project_id,
            'versions': history,
            'branches': service.get_branches(),
        })
    
    def retrieve(self, request, project_id=None, pk=None):
        """
        Get a specific version's details.
        
        GET /api/v1/projects/{project_id}/versions/{version_number}/
        """
        project = self.get_project(project_id)
        snapshot = get_object_or_404(
            ProjectSnapshot,
            project=project,
            version_number=pk
        )
        
        serializer = ProjectSnapshotDetailSerializer(snapshot)
        return Response(serializer.data)
    
    def create(self, request, project_id=None):
        """
        Create a new version snapshot.
        
        POST /api/v1/projects/{project_id}/versions/
        Body: {"label": "Final design", "change_summary": "Updated colors"}
        """
        project = self.get_project(project_id)
        serializer = CreateSnapshotSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = VersionService(project)
        snapshot = service.create_snapshot(
            user=request.user,
            label=serializer.validated_data.get('label', ''),
            change_summary=serializer.validated_data.get('change_summary', ''),
            branch_name=serializer.validated_data.get('branch_name', 'main'),
        )
        
        return Response(
            ProjectSnapshotSerializer(snapshot).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, project_id=None, pk=None):
        """
        Restore project to a specific version.
        
        POST /api/v1/projects/{project_id}/versions/{version_number}/restore/
        Body: {"create_backup": true}
        """
        project = self.get_project(project_id)
        snapshot = get_object_or_404(
            ProjectSnapshot,
            project=project,
            version_number=pk
        )
        
        serializer = RestoreSnapshotSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = VersionService(project)
        new_snapshot = service.restore_snapshot(
            snapshot=snapshot,
            user=request.user,
            create_backup=serializer.validated_data['create_backup']
        )
        
        return Response({
            'message': f'Restored to version {pk}',
            'new_version': ProjectSnapshotSerializer(new_snapshot).data,
        })
    
    @action(detail=False, methods=['post'])
    def branch(self, request, project_id=None):
        """
        Create a new branch from a version.
        
        POST /api/v1/projects/{project_id}/versions/branch/
        Body: {"branch_name": "experiment", "from_version": 5}
        """
        project = self.get_project(project_id)
        serializer = CreateBranchSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from_version = serializer.validated_data.get('from_version')
        
        if from_version:
            from_snapshot = get_object_or_404(
                ProjectSnapshot,
                project=project,
                version_number=from_version
            )
        else:
            # Use latest version
            from_snapshot = project.snapshots.order_by('-version_number').first()
            if not from_snapshot:
                return Response(
                    {'error': 'No versions exist to branch from'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = VersionService(project)
        
        try:
            new_snapshot = service.create_branch(
                from_snapshot=from_snapshot,
                branch_name=serializer.validated_data['branch_name'],
                user=request.user
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            ProjectSnapshotSerializer(new_snapshot).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def branches(self, request, project_id=None):
        """
        List all branches for a project.
        
        GET /api/v1/projects/{project_id}/versions/branches/
        """
        project = self.get_project(project_id)
        service = VersionService(project)
        
        return Response(service.get_branches())
    
    @action(detail=False, methods=['post'])
    def diff(self, request, project_id=None):
        """
        Get diff between two versions.
        
        POST /api/v1/projects/{project_id}/versions/diff/
        Body: {"from_version": 3, "to_version": 5}
        """
        project = self.get_project(project_id)
        serializer = DiffRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from_snapshot = get_object_or_404(
            ProjectSnapshot,
            project=project,
            version_number=serializer.validated_data['from_version']
        )
        to_snapshot = get_object_or_404(
            ProjectSnapshot,
            project=project,
            version_number=serializer.validated_data['to_version']
        )
        
        service = VersionService(project)
        diff_data = service.get_diff(from_snapshot, to_snapshot)
        
        return Response({
            'from_version': from_snapshot.version_number,
            'to_version': to_snapshot.version_number,
            'diff': diff_data,
        })
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, project_id=None, pk=None):
        """
        Get or add comments on a version.
        
        GET/POST /api/v1/projects/{project_id}/versions/{version_number}/comments/
        """
        project = self.get_project(project_id)
        snapshot = get_object_or_404(
            ProjectSnapshot,
            project=project,
            version_number=pk
        )
        
        if request.method == 'GET':
            comments = snapshot.comments.select_related('user')
            return Response(VersionCommentSerializer(comments, many=True).data)
        
        # POST
        serializer = VersionCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        comment = VersionComment.objects.create(
            snapshot=snapshot,
            user=request.user,
            content=serializer.validated_data['content'],
            component_id=serializer.validated_data.get('component_id', ''),
        )
        
        return Response(
            VersionCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def compare_versions(request, project_id):
    """
    Visual comparison endpoint for versions.
    
    GET /api/v1/projects/{project_id}/versions/compare/?v1=3&v2=5
    """
    project = get_object_or_404(Project, id=project_id)
    
    # Check access
    if project.user != request.user and request.user not in project.collaborators.all():
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    v1 = request.query_params.get('v1')
    v2 = request.query_params.get('v2')
    
    if not v1 or not v2:
        return Response(
            {'error': 'Both v1 and v2 parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    snapshot1 = get_object_or_404(ProjectSnapshot, project=project, version_number=v1)
    snapshot2 = get_object_or_404(ProjectSnapshot, project=project, version_number=v2)
    
    service = VersionService(project)
    diff_data = service.get_diff(snapshot1, snapshot2)
    
    return Response({
        'version1': ProjectSnapshotSerializer(snapshot1).data,
        'version2': ProjectSnapshotSerializer(snapshot2).data,
        'diff': diff_data,
        'identical': snapshot1.is_identical_to(snapshot2),
    })

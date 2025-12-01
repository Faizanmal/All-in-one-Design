"""
Batch Operations API Views

REST API endpoints for batch operations on components.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from projects.models import Project
from .batch_operations import BatchOperation, BatchOperationService


class BatchOperationViewSet(viewsets.ViewSet):
    """
    ViewSet for batch operations.
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        List recent batch operations.
        
        GET /api/v1/projects/batch-operations/
        """
        project_id = request.query_params.get('project_id')
        
        queryset = BatchOperation.objects.filter(user=request.user)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        operations = queryset[:50]
        
        return Response({
            'operations': [
                {
                    'id': op.id,
                    'operation_type': op.operation_type,
                    'status': op.status,
                    'component_count': op.component_count,
                    'success_count': op.success_count,
                    'error_count': op.error_count,
                    'created_at': op.created_at.isoformat(),
                    'completed_at': op.completed_at.isoformat() if op.completed_at else None,
                }
                for op in operations
            ]
        })
    
    @action(detail=False, methods=['post'])
    def move(self, request):
        """
        Move multiple components.
        
        POST /api/v1/projects/batch-operations/move/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "delta_x": 100,
            "delta_y": 50
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        delta_x = request.data.get('delta_x', 0)
        delta_y = request.data.get('delta_y', 0)
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_move(component_ids, delta_x, delta_y)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def resize(self, request):
        """
        Resize multiple components.
        
        POST /api/v1/projects/batch-operations/resize/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "scale_x": 1.5,
            "scale_y": 1.5,
            "anchor": "center"
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        scale_x = request.data.get('scale_x', 1.0)
        scale_y = request.data.get('scale_y', 1.0)
        anchor = request.data.get('anchor', 'center')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_resize(component_ids, scale_x, scale_y, anchor)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def style(self, request):
        """
        Apply style changes to multiple components.
        
        POST /api/v1/projects/batch-operations/style/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "style_updates": {
                "fill": "#FF0000",
                "opacity": 0.8,
                "style.borderRadius": 8
            }
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        style_updates = request.data.get('style_updates', {})
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_style(component_ids, style_updates)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def delete(self, request):
        """
        Delete multiple components.
        
        POST /api/v1/projects/batch-operations/delete/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3]
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_delete(component_ids)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def duplicate(self, request):
        """
        Duplicate multiple components.
        
        POST /api/v1/projects/batch-operations/duplicate/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "offset_x": 20,
            "offset_y": 20
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        offset_x = request.data.get('offset_x', 20)
        offset_y = request.data.get('offset_y', 20)
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_duplicate(component_ids, offset_x, offset_y)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'new_component_ids': operation.after_state.get('new_component_ids', []),
        })
    
    @action(detail=False, methods=['post'])
    def align(self, request):
        """
        Align multiple components.
        
        POST /api/v1/projects/batch-operations/align/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "alignment": "center"  // left, center, right, top, middle, bottom
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        alignment = request.data.get('alignment', 'left')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_align(component_ids, alignment)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def distribute(self, request):
        """
        Distribute components evenly.
        
        POST /api/v1/projects/batch-operations/distribute/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3, 4],
            "direction": "horizontal",  // horizontal, vertical
            "spacing": null  // null = equal spacing
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        direction = request.data.get('direction', 'horizontal')
        spacing = request.data.get('spacing')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_distribute(component_ids, direction, spacing)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def change_order(self, request):
        """
        Change z-order of components.
        
        POST /api/v1/projects/batch-operations/change-order/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "action": "bring_front"  // bring_front, send_back, bring_forward, send_backward
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        action = request.data.get('action', 'bring_front')
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.bulk_change_order(component_ids, action)
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=False, methods=['post'])
    def find_replace(self, request):
        """
        Find and replace property values.
        
        POST /api/v1/projects/batch-operations/find-replace/
        {
            "project_id": 1,
            "component_ids": [1, 2, 3],
            "property_path": "fill",
            "find_value": "#000000",
            "replace_value": "#333333",
            "use_regex": false
        }
        """
        project_id = request.data.get('project_id')
        component_ids = request.data.get('component_ids', [])
        property_path = request.data.get('property_path')
        find_value = request.data.get('find_value')
        replace_value = request.data.get('replace_value')
        use_regex = request.data.get('use_regex', False)
        
        if not property_path:
            return Response(
                {'error': 'property_path is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operation = service.find_and_replace(
            component_ids, property_path, find_value, replace_value, use_regex
        )
        
        return Response({
            'operation_id': operation.id,
            'status': operation.status,
            'success_count': operation.success_count,
            'error_count': operation.error_count,
            'errors': operation.errors,
        })
    
    @action(detail=True, methods=['post'])
    def undo(self, request, pk=None):
        """
        Undo a batch operation.
        
        POST /api/v1/projects/batch-operations/{id}/undo/
        """
        operation = get_object_or_404(BatchOperation, pk=pk, user=request.user)
        
        service = BatchOperationService(operation.project, request.user)
        success = service.undo(operation)
        
        if success:
            return Response({
                'success': True,
                'message': 'Operation undone successfully'
            })
        else:
            return Response(
                {'error': 'Failed to undo operation'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Get operation history for a project.
        
        GET /api/v1/projects/batch-operations/history/?project_id=1
        """
        project_id = request.query_params.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project = get_object_or_404(Project, pk=project_id, user=request.user)
        service = BatchOperationService(project, request.user)
        
        operations = service.get_operation_history(limit=50)
        
        return Response({
            'history': [
                {
                    'id': op.id,
                    'operation_type': op.operation_type,
                    'operation_label': op.get_operation_type_display(),
                    'status': op.status,
                    'component_count': op.component_count,
                    'success_count': op.success_count,
                    'can_undo': op.status == 'completed',
                    'created_at': op.created_at.isoformat(),
                }
                for op in operations
            ]
        })

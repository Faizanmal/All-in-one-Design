"""
Workflow Automation Engine Views.

Provides REST API endpoints for managing workflows, triggers, actions,
and workflow execution.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .workflow_models import (
    Workflow,
    WorkflowTrigger,
    WorkflowAction,
    WorkflowRun,
    WorkflowActionLog,
)
from .workflow_serializers import (
    WorkflowListSerializer,
    WorkflowDetailSerializer,
    WorkflowCreateSerializer,
    WorkflowTriggerSerializer,
    WorkflowActionSerializer,
    WorkflowRunSerializer,
)
from .workflow_service import WorkflowEngine

engine = WorkflowEngine()


class WorkflowViewSet(viewsets.ModelViewSet):
    """CRUD + execute for workflows."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkflowListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return WorkflowCreateSerializer
        return WorkflowDetailSerializer

    def get_queryset(self):
        return Workflow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Manually trigger a workflow execution."""
        workflow = self.get_object()

        if workflow.status != 'active':
            return Response(
                {'error': 'Workflow must be active to execute'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trigger_data = request.data.get('trigger_data', {})

        # Create run record
        run = WorkflowRun.objects.create(
            workflow=workflow,
            triggered_by=request.user,
            status='running',
            trigger_type='manual',
            trigger_data=trigger_data,
            started_at=timezone.now(),
        )

        # Build workflow execution payload
        actions_data = []
        for action_obj in workflow.actions.all():
            actions_data.append({
                'id': str(action_obj.id),
                'action_type': action_obj.action_type,
                'config': action_obj.config,
                'order': action_obj.order,
                'next_action_on_failure': action_obj.next_action_on_failure_id,
            })

        workflow_data = {
            'id': str(workflow.id),
            'actions': actions_data,
        }

        # Execute
        result = engine.execute_workflow(workflow_data, trigger_data)

        # Log individual action results
        for action_result in result.get('action_results', []):
            action_id = action_result.get('action_id')
            if action_id:
                try:
                    action_obj = WorkflowAction.objects.get(id=action_id)
                    WorkflowActionLog.objects.create(
                        workflow_run=run,
                        action=action_obj,
                        status='completed' if action_result.get('success') else 'failed',
                        started_at=timezone.now(),
                        completed_at=timezone.now(),
                        duration_ms=action_result.get('duration_ms', 0),
                        output_data=action_result.get('output', {}),
                        error_message=action_result.get('error', ''),
                    )
                except WorkflowAction.DoesNotExist:
                    pass

        # Update run
        run.status = 'completed' if result['success'] else 'failed'
        run.completed_at = timezone.now()
        run.duration_ms = result['duration_ms']
        run.output = result
        run.save()

        # Update workflow stats
        workflow.total_runs += 1
        if result['success']:
            workflow.successful_runs += 1
        else:
            workflow.failed_runs += 1
        workflow.last_run_at = timezone.now()
        workflow.save()

        return Response(WorkflowRunSerializer(run).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a workflow."""
        original = self.get_object()

        new_workflow = Workflow.objects.create(
            user=request.user,
            name=f"{original.name} (Copy)",
            description=original.description,
            status='draft',
            graph_data=original.graph_data,
            max_retries=original.max_retries,
            retry_delay_seconds=original.retry_delay_seconds,
            timeout_seconds=original.timeout_seconds,
            run_as_async=original.run_as_async,
        )

        # Duplicate triggers
        for trigger in original.triggers.all():
            WorkflowTrigger.objects.create(
                workflow=new_workflow,
                trigger_type=trigger.trigger_type,
                config=trigger.config,
                cron_expression=trigger.cron_expression,
                is_active=trigger.is_active,
            )

        # Duplicate actions
        action_map = {}
        for action_obj in original.actions.all():
            new_action = WorkflowAction.objects.create(
                workflow=new_workflow,
                action_type=action_obj.action_type,
                name=action_obj.name,
                config=action_obj.config,
                position_x=action_obj.position_x,
                position_y=action_obj.position_y,
                order=action_obj.order,
                condition_expression=action_obj.condition_expression,
            )
            action_map[str(action_obj.id)] = new_action

        # Reconnect action links
        for old_action in original.actions.all():
            if old_action.next_action_on_success_id:
                new_action = action_map[str(old_action.id)]
                success_target = action_map.get(str(old_action.next_action_on_success_id))
                if success_target:
                    new_action.next_action_on_success = success_target
                    new_action.save()
            if old_action.next_action_on_failure_id:
                new_action = action_map[str(old_action.id)]
                failure_target = action_map.get(str(old_action.next_action_on_failure_id))
                if failure_target:
                    new_action.next_action_on_failure = failure_target
                    new_action.save()

        return Response(
            WorkflowDetailSerializer(new_workflow).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Validate workflow definition."""
        workflow = self.get_object()
        serializer = WorkflowDetailSerializer(workflow)
        result = engine.validate_workflow(serializer.data)
        return Response(result)

    @action(detail=True, methods=['get'])
    def runs(self, request, pk=None):
        """Get run history for a workflow."""
        workflow = self.get_object()
        runs = WorkflowRun.objects.filter(workflow=workflow)
        page = self.paginate_queryset(runs)
        if page is not None:
            serializer = WorkflowRunSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(WorkflowRunSerializer(runs, many=True).data)

    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle workflow between active/paused."""
        workflow = self.get_object()
        if workflow.status == 'active':
            workflow.status = 'paused'
        elif workflow.status in ('paused', 'draft'):
            workflow.status = 'active'
        workflow.save()
        return Response({'status': workflow.status})


class WorkflowTriggerViewSet(viewsets.ModelViewSet):
    """CRUD for workflow triggers."""
    serializer_class = WorkflowTriggerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkflowTrigger.objects.filter(
            workflow__user=self.request.user,
            workflow_id=self.kwargs.get('workflow_pk'),
        )

    def perform_create(self, serializer):
        workflow = get_object_or_404(
            Workflow, id=self.kwargs['workflow_pk'], user=self.request.user
        )
        serializer.save(workflow=workflow)


class WorkflowActionViewSet(viewsets.ModelViewSet):
    """CRUD for workflow actions."""
    serializer_class = WorkflowActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkflowAction.objects.filter(
            workflow__user=self.request.user,
            workflow_id=self.kwargs.get('workflow_pk'),
        )

    def perform_create(self, serializer):
        workflow = get_object_or_404(
            Workflow, id=self.kwargs['workflow_pk'], user=self.request.user
        )
        serializer.save(workflow=workflow)


# --- Function-based views for metadata ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trigger_types(request):
    """Return all available trigger types."""
    return Response(engine.get_trigger_types())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def action_types(request):
    """Return all available action types."""
    return Response(engine.get_action_types())


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workflow_templates(request):
    """Return pre-built workflow templates."""
    return Response(engine.get_workflow_templates())


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_from_template(request):
    """Create a workflow from a pre-built template."""
    template_id = request.data.get('template_id')
    templates = engine.get_workflow_templates()
    template = next((t for t in templates if t['id'] == template_id), None)

    if not template:
        return Response(
            {'error': f'Template not found: {template_id}'},
            status=status.HTTP_404_NOT_FOUND,
        )

    workflow = Workflow.objects.create(
        user=request.user,
        name=template['name'],
        description=template['description'],
        status='draft',
    )

    WorkflowTrigger.objects.create(
        workflow=workflow,
        trigger_type=template['trigger'],
        config={},
    )

    for i, action_type in enumerate(template['actions']):
        action_info = engine.ACTION_TYPES.get(action_type, {})
        WorkflowAction.objects.create(
            workflow=workflow,
            action_type=action_type,
            name=action_info.get('name', action_type),
            config={},
            order=i,
            position_x=300,
            position_y=100 + i * 120,
        )

    return Response(
        WorkflowDetailSerializer(workflow).data,
        status=status.HTTP_201_CREATED,
    )

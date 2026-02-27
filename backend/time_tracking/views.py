from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import uuid

from .models import (
    TimeTracker, TimeEntry, Task, TaskComment,
    ProjectEstimate, Invoice, TimeReport, WeeklyGoal
)
from .serializers import (
    TimeTrackerSerializer, TimeEntrySerializer, TimeEntryCreateSerializer,
    TaskListSerializer, TaskSerializer, TaskCreateSerializer, TaskCommentSerializer,
    ProjectEstimateSerializer, InvoiceListSerializer, InvoiceSerializer,
    InvoiceCreateSerializer, TimeReportSerializer, WeeklyGoalSerializer,
    BulkTimeEntrySerializer
)
from .services import TimeReportGenerator


class TimeTrackerViewSet(viewsets.ModelViewSet):
    """ViewSet for time trackers"""
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TimeTracker.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Stop any active timers first
        TimeTracker.objects.filter(user=self.request.user, is_active=True).delete()
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active timer"""
        timer = TimeTracker.objects.filter(user=request.user, is_active=True).first()
        if timer:
            return Response(TimeTrackerSerializer(timer).data)
        return Response(None)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop timer and create time entry"""
        tracker = self.get_object()
        
        if not tracker.is_active:
            return Response({'error': 'Timer not active'}, status=status.HTTP_400_BAD_REQUEST)
        
        ended_at = timezone.now()
        duration = int((ended_at - tracker.started_at).total_seconds() / 60)
        
        if duration < 1:
            duration = 1
        
        # Create time entry
        entry = TimeEntry.objects.create(
            user=request.user,
            project=tracker.project,
            task=tracker.task,
            description=tracker.description,
            started_at=tracker.started_at,
            ended_at=ended_at,
            duration_minutes=duration,
        )
        
        # Delete tracker
        tracker.delete()
        
        return Response(TimeEntrySerializer(entry).data)
    
    @action(detail=True, methods=['post'])
    def discard(self, request, pk=None):
        """Discard timer without creating entry"""
        tracker = self.get_object()
        tracker.delete()
        return Response({'status': 'discarded'})


class TimeEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for time entries"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TimeEntryCreateSerializer
        return TimeEntrySerializer
    
    def get_queryset(self):
        queryset = TimeEntry.objects.filter(user=self.request.user)
        
        # Date filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(started_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(started_at__date__lte=end_date)
        
        # Project filter
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        return queryset.select_related('project', 'task')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple time entries"""
        serializer = BulkTimeEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        entries = []
        for entry_data in serializer.validated_data['entries']:
            entry_data['user'] = request.user
            entries.append(TimeEntry(**entry_data))
        
        TimeEntry.objects.bulk_create(entries)
        return Response({'created': len(entries)})
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get time entry summary"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        entries = TimeEntry.objects.filter(user=request.user)
        
        today_minutes = entries.filter(
            started_at__date=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        week_minutes = entries.filter(
            started_at__date__gte=week_start
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        month_minutes = entries.filter(
            started_at__date__gte=month_start
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        return Response({
            'today': Decimal(today_minutes) / Decimal('60'),
            'week': Decimal(week_minutes) / Decimal('60'),
            'month': Decimal(month_minutes) / Decimal('60'),
        })


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for tasks"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_queryset(self):
        queryset = Task.objects.filter(
            Q(project__owner=self.request.user) |
            Q(project__collaborators=self.request.user) |
            Q(assignee=self.request.user)
        ).distinct()
        
        # Project filter
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        # Status filter
        task_status = self.request.query_params.get('status')
        if task_status:
            queryset = queryset.filter(status=task_status)
        
        # Assignee filter
        assignee = self.request.query_params.get('assignee')
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)
        
        return queryset.select_related('assignee', 'project')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update task status"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Task.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = new_status
        if new_status == 'done':
            task.completed_at = timezone.now()
        else:
            task.completed_at = None
        task.save()
        
        return Response(TaskSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder task"""
        task = self.get_object()
        new_order = request.data.get('order', 0)
        
        task.order = new_order
        task.save()
        
        return Response({'status': 'reordered'})
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        tasks = Task.objects.filter(
            assignee=request.user
        ).exclude(status='done')
        
        return Response(TaskListSerializer(tasks, many=True).data)
    
    @action(detail=False, methods=['get'])
    def board(self, request):
        """Get Kanban board data"""
        project = request.query_params.get('project')
        queryset = Task.objects.filter(parent__isnull=True)
        
        if project:
            queryset = queryset.filter(project_id=project)
        
        board = {
            'todo': TaskListSerializer(queryset.filter(status='todo'), many=True).data,
            'in_progress': TaskListSerializer(queryset.filter(status='in_progress'), many=True).data,
            'review': TaskListSerializer(queryset.filter(status='review'), many=True).data,
            'done': TaskListSerializer(queryset.filter(status='done'), many=True).data,
        }
        
        return Response(board)


class TaskCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for task comments"""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task = self.request.query_params.get('task')
        queryset = TaskComment.objects.all()
        
        if task:
            queryset = queryset.filter(task_id=task)
        
        return queryset.select_related('user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProjectEstimateViewSet(viewsets.ModelViewSet):
    """ViewSet for project estimates"""
    serializer_class = ProjectEstimateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        project = self.request.query_params.get('project')
        queryset = ProjectEstimate.objects.all()
        
        if project:
            queryset = queryset.filter(project_id=project)
        
        return queryset.select_related('project', 'created_by', 'approved_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an estimate"""
        estimate = self.get_object()
        
        estimate.is_approved = True
        estimate.approved_by = request.user
        estimate.approved_at = timezone.now()
        estimate.save()
        
        return Response(ProjectEstimateSerializer(estimate).data)


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for invoices"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.objects.filter(
            created_by=self.request.user
        ).select_related('project')
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        
        # Calculate totals
        tax_amount = data['subtotal'] * (data.get('tax_rate', Decimal('0')) / Decimal('100'))
        total = data['subtotal'] + tax_amount - data.get('discount', Decimal('0'))
        
        # Generate invoice number
        invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        
        invoice = serializer.save(
            created_by=self.request.user,
            invoice_number=invoice_number,
            tax_amount=tax_amount,
            total=total,
        )
        
        # Link time entries if provided
        time_entry_ids = self.request.data.get('time_entry_ids', [])
        if time_entry_ids:
            entries = TimeEntry.objects.filter(id__in=time_entry_ids, user=self.request.user)
            invoice.time_entries.set(entries)
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send invoice to client"""
        invoice = self.get_object()
        
        if invoice.status == 'draft':
            invoice.status = 'sent'
            invoice.save()
            # Send email notification
            self._send_invoice_notification(invoice)
        
        return Response(InvoiceSerializer(invoice).data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        
        invoice.status = 'paid'
        invoice.paid_at = timezone.now()
        invoice.save()
        
        return Response(InvoiceSerializer(invoice).data)
    
    @action(detail=False, methods=['post'])
    def from_time_entries(self, request):
        """Generate invoice from time entries"""
        entry_ids = request.data.get('time_entry_ids', [])
        entries = TimeEntry.objects.filter(
            id__in=entry_ids,
            user=request.user,
            is_billable=True
        )
        
        if not entries.exists():
            return Response({'error': 'No billable entries found'}, status=status.HTTP_400_BAD_REQUEST)
        
        line_items = []
        subtotal = Decimal('0')
        
        for entry in entries:
            amount = entry.billable_amount
            line_items.append({
                'description': entry.description or f"Work on {entry.project.name if entry.project else 'project'}",
                'date': entry.started_at.date().isoformat(),
                'hours': str(Decimal(entry.duration_minutes) / Decimal('60')),
                'rate': str(entry.hourly_rate),
                'amount': str(amount),
            })
            subtotal += amount
        
        return Response({
            'line_items': line_items,
            'subtotal': str(subtotal),
            'time_entry_ids': list(entries.values_list('id', flat=True)),
        })


class TimeReportViewSet(viewsets.ModelViewSet):
    """ViewSet for time reports"""
    serializer_class = TimeReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TimeReport.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        report = serializer.save(created_by=self.request.user)
        
        # Generate report data
        generator = TimeReportGenerator(report)
        generator.generate()


class WeeklyGoalViewSet(viewsets.ModelViewSet):
    """ViewSet for weekly goals"""
    serializer_class = WeeklyGoalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return WeeklyGoal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current week's goal"""
        today = timezone.now().date()
        year, week, _ = today.isocalendar()
        
        goal, created = WeeklyGoal.objects.get_or_create(
            user=request.user,
            year=year,
            week=week,
            defaults={'target_hours': Decimal('40.00')}
        )
        
        # Update logged hours
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        entries = TimeEntry.objects.filter(
            user=request.user,
            started_at__date__gte=week_start,
            started_at__date__lte=week_end
        )
        
        goal.logged_hours = Decimal(entries.aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0) / Decimal('60')
        
        goal.billable_hours = Decimal(entries.filter(is_billable=True).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0) / Decimal('60')
        
        goal.save()
        
        return Response(WeeklyGoalSerializer(goal).data)


class DashboardView(APIView):
    """Time tracking dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        entries = TimeEntry.objects.filter(user=request.user)
        
        # Calculate hours
        today_minutes = entries.filter(
            started_at__date=today
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        week_minutes = entries.filter(
            started_at__date__gte=week_start
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        month_minutes = entries.filter(
            started_at__date__gte=month_start
        ).aggregate(total=Sum('duration_minutes'))['total'] or 0
        
        # Billable
        billable_entries = entries.filter(
            started_at__date__gte=month_start,
            is_billable=True
        )
        billable_minutes = billable_entries.aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        billable_amount = sum(e.billable_amount for e in billable_entries)
        
        # Active timer
        active_timer = TimeTracker.objects.filter(
            user=request.user, is_active=True
        ).first()
        
        # Recent entries
        recent_entries = entries.order_by('-started_at')[:10]
        
        # Projects breakdown
        projects_breakdown = entries.filter(
            started_at__date__gte=week_start
        ).values('project__name').annotate(
            total_minutes=Sum('duration_minutes')
        ).order_by('-total_minutes')[:5]
        
        return Response({
            'today_hours': Decimal(today_minutes) / Decimal('60'),
            'week_hours': Decimal(week_minutes) / Decimal('60'),
            'month_hours': Decimal(month_minutes) / Decimal('60'),
            'billable_hours': Decimal(billable_minutes) / Decimal('60'),
            'billable_amount': billable_amount,
            'active_timer': TimeTrackerSerializer(active_timer).data if active_timer else None,
            'recent_entries': TimeEntrySerializer(recent_entries, many=True).data,
            'projects_breakdown': [
                {
                    'project': p['project__name'] or 'No project',
                    'hours': Decimal(p['total_minutes']) / Decimal('60'),
                }
                for p in projects_breakdown
            ],
        })
    
    def _send_invoice_notification(self, invoice):
        """Send invoice notification email"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Invoice #{invoice.number} - {invoice.client_name}"
            message = f"""
            Your invoice #{invoice.number} for {invoice.amount} has been sent.
            
            Due Date: {invoice.due_date}
            Amount: ${invoice.amount}
            
            View invoice: {settings.FRONTEND_URL}/invoices/{invoice.id}
            
            Best regards,
            AI Design Tool Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invoice.client_email],
                fail_silently=True
            )
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send invoice notification: {e}")

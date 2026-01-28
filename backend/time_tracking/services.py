from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta
import json


class TimeReportGenerator:
    """Generate time tracking reports"""
    
    def __init__(self, report):
        self.report = report
    
    def generate(self):
        """Generate report based on type"""
        if self.report.report_type == 'project':
            data = self._generate_project_report()
        elif self.report.report_type == 'user':
            data = self._generate_user_report()
        elif self.report.report_type == 'team':
            data = self._generate_team_report()
        else:
            data = self._generate_client_report()
        
        self.report.report_data = data
        self.report.save()
        
        return data
    
    def _generate_project_report(self):
        """Generate project-focused report"""
        from .models import TimeEntry, Task
        
        entries = TimeEntry.objects.filter(
            project=self.report.project,
            started_at__date__gte=self.report.start_date,
            started_at__date__lte=self.report.end_date
        )
        
        # Aggregate data
        total_minutes = entries.aggregate(total=Sum('duration_minutes'))['total'] or 0
        billable_minutes = entries.filter(is_billable=True).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        total_hours = Decimal(total_minutes) / Decimal('60')
        billable_hours = Decimal(billable_minutes) / Decimal('60')
        
        # Calculate amount
        total_amount = sum(e.billable_amount for e in entries.filter(is_billable=True))
        
        # Update report
        self.report.total_hours = total_hours
        self.report.billable_hours = billable_hours
        self.report.total_amount = total_amount
        
        # By user breakdown
        by_user = entries.values('user__username').annotate(
            minutes=Sum('duration_minutes')
        ).order_by('-minutes')
        
        # By task breakdown
        by_task = entries.values('task__title').annotate(
            minutes=Sum('duration_minutes')
        ).order_by('-minutes')
        
        # Daily breakdown
        daily = {}
        for entry in entries:
            date_str = entry.started_at.date().isoformat()
            if date_str not in daily:
                daily[date_str] = 0
            daily[date_str] += entry.duration_minutes
        
        return {
            'project_name': self.report.project.name if self.report.project else None,
            'period': {
                'start': self.report.start_date.isoformat(),
                'end': self.report.end_date.isoformat(),
            },
            'summary': {
                'total_hours': str(total_hours),
                'billable_hours': str(billable_hours),
                'total_amount': str(total_amount),
                'entry_count': entries.count(),
            },
            'by_user': [
                {'user': u['user__username'], 'hours': str(Decimal(u['minutes']) / Decimal('60'))}
                for u in by_user
            ],
            'by_task': [
                {'task': t['task__title'] or 'No task', 'hours': str(Decimal(t['minutes']) / Decimal('60'))}
                for t in by_task
            ],
            'daily': {
                date: str(Decimal(minutes) / Decimal('60'))
                for date, minutes in daily.items()
            },
        }
    
    def _generate_user_report(self):
        """Generate user-focused report"""
        from .models import TimeEntry
        
        entries = TimeEntry.objects.filter(
            user=self.report.user,
            started_at__date__gte=self.report.start_date,
            started_at__date__lte=self.report.end_date
        )
        
        total_minutes = entries.aggregate(total=Sum('duration_minutes'))['total'] or 0
        billable_minutes = entries.filter(is_billable=True).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        total_hours = Decimal(total_minutes) / Decimal('60')
        billable_hours = Decimal(billable_minutes) / Decimal('60')
        total_amount = sum(e.billable_amount for e in entries.filter(is_billable=True))
        
        self.report.total_hours = total_hours
        self.report.billable_hours = billable_hours
        self.report.total_amount = total_amount
        
        # By project breakdown
        by_project = entries.values('project__name').annotate(
            minutes=Sum('duration_minutes')
        ).order_by('-minutes')
        
        return {
            'user': self.report.user.username if self.report.user else None,
            'period': {
                'start': self.report.start_date.isoformat(),
                'end': self.report.end_date.isoformat(),
            },
            'summary': {
                'total_hours': str(total_hours),
                'billable_hours': str(billable_hours),
                'total_amount': str(total_amount),
            },
            'by_project': [
                {'project': p['project__name'] or 'No project', 'hours': str(Decimal(p['minutes']) / Decimal('60'))}
                for p in by_project
            ],
        }
    
    def _generate_team_report(self):
        """Generate team report"""
        from .models import TimeEntry
        
        entries = TimeEntry.objects.filter(
            started_at__date__gte=self.report.start_date,
            started_at__date__lte=self.report.end_date
        )
        
        if self.report.project:
            entries = entries.filter(project=self.report.project)
        
        total_minutes = entries.aggregate(total=Sum('duration_minutes'))['total'] or 0
        billable_minutes = entries.filter(is_billable=True).aggregate(
            total=Sum('duration_minutes')
        )['total'] or 0
        
        total_hours = Decimal(total_minutes) / Decimal('60')
        billable_hours = Decimal(billable_minutes) / Decimal('60')
        total_amount = sum(e.billable_amount for e in entries.filter(is_billable=True))
        
        self.report.total_hours = total_hours
        self.report.billable_hours = billable_hours
        self.report.total_amount = total_amount
        
        # By user breakdown
        by_user = entries.values('user__username').annotate(
            minutes=Sum('duration_minutes')
        ).order_by('-minutes')
        
        return {
            'period': {
                'start': self.report.start_date.isoformat(),
                'end': self.report.end_date.isoformat(),
            },
            'summary': {
                'total_hours': str(total_hours),
                'billable_hours': str(billable_hours),
                'total_amount': str(total_amount),
            },
            'by_user': [
                {'user': u['user__username'], 'hours': str(Decimal(u['minutes']) / Decimal('60'))}
                for u in by_user
            ],
        }
    
    def _generate_client_report(self):
        """Generate client-facing report"""
        return self._generate_project_report()

"""
Views for Design QA app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import (
    LintRuleSet, LintRule, DesignLintReport, LintIssue,
    AccessibilityCheck, AccessibilityReport, AccessibilityIssue,
    StyleUsageReport, LintIgnoreRule
)
from .serializers import (
    LintRuleSetSerializer, LintRuleSetListSerializer, LintRuleSerializer,
    DesignLintReportSerializer, DesignLintReportListSerializer, LintIssueSerializer,
    AccessibilityCheckSerializer, AccessibilityReportSerializer,
    AccessibilityReportListSerializer, AccessibilityIssueSerializer,
    StyleUsageReportSerializer, LintIgnoreRuleSerializer,
    RunLintSerializer, RunAccessibilityCheckSerializer, AutoFixSerializer
)
from .services import DesignLinter, AccessibilityChecker, StyleAnalyzer


class LintRuleSetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lint rule sets."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['design_system', 'is_default', 'is_strict']
    search_fields = ['name', 'description']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LintRuleSetListSerializer
        return LintRuleSetSerializer
    
    def get_queryset(self):
        user = self.request.user
        return LintRuleSet.objects.filter(
            Q(design_system__project__owner=user) |
            Q(design_system__project__team__members=user) |
            Q(is_default=True)
        ).distinct().prefetch_related('rules')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_rule(self, request, pk=None):
        """Add a rule to the rule set."""
        rule_set = self.get_object()
        serializer = LintRuleSerializer(data={
            **request.data,
            'rule_set': rule_set.id
        })
        if serializer.is_valid():
            serializer.save(rule_set=rule_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate the rule set."""
        rule_set = self.get_object()
        
        new_set = LintRuleSet.objects.create(
            name=f"{rule_set.name} (copy)",
            description=rule_set.description,
            design_system=rule_set.design_system,
            is_strict=rule_set.is_strict,
            created_by=request.user,
        )
        
        for rule in rule_set.rules.all():
            LintRule.objects.create(
                rule_set=new_set,
                name=rule.name,
                description=rule.description,
                category=rule.category,
                severity=rule.severity,
                rule_type=rule.rule_type,
                configuration=rule.configuration,
                error_message=rule.error_message,
                suggestion=rule.suggestion,
                is_enabled=rule.is_enabled,
                is_auto_fixable=rule.is_auto_fixable,
                order=rule.order,
            )
        
        return Response(LintRuleSetSerializer(new_set).data, status=status.HTTP_201_CREATED)


class LintRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lint rules."""
    serializer_class = LintRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rule_set', 'category', 'severity', 'is_enabled', 'is_auto_fixable']
    search_fields = ['name', 'description']
    ordering = ['order']
    
    def get_queryset(self):
        user = self.request.user
        return LintRule.objects.filter(
            Q(rule_set__design_system__project__owner=user) |
            Q(rule_set__design_system__project__team__members=user) |
            Q(rule_set__is_default=True)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle rule enabled state."""
        rule = self.get_object()
        rule.is_enabled = not rule.is_enabled
        rule.save()
        return Response({'is_enabled': rule.is_enabled})


class DesignLintReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design lint reports."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'rule_set', 'status', 'trigger_type']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DesignLintReportListSerializer
        return DesignLintReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        return DesignLintReport.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().prefetch_related('issues')
    
    @action(detail=False, methods=['post'])
    def run(self, request):
        """Run a new lint check."""
        serializer = RunLintSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        linter = DesignLinter(project)
        report = linter.run(
            triggered_by=request.user,
            rule_set_id=serializer.validated_data.get('rule_set_id'),
            node_ids=serializer.validated_data.get('node_ids'),
            categories=serializer.validated_data.get('categories'),
        )
        
        return Response(DesignLintReportSerializer(report).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def auto_fix(self, request, pk=None):
        """Auto-fix issues in the report."""
        report = self.get_object()
        serializer = AutoFixSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        issue_ids = serializer.validated_data['issue_ids']
        preview = serializer.validated_data['preview']
        
        linter = DesignLinter(report.project)
        result = linter.auto_fix(
            issue_ids=issue_ids,
            preview=preview,
            user=request.user,
        )
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def issues_by_node(self, request, pk=None):
        """Get issues grouped by node."""
        report = self.get_object()
        
        issues_by_node = {}
        for issue in report.issues.filter(is_ignored=False, is_resolved=False):
            node_id = issue.node_id
            if node_id not in issues_by_node:
                issues_by_node[node_id] = {
                    'node_id': node_id,
                    'node_name': issue.node_name,
                    'node_type': issue.node_type,
                    'issues': []
                }
            issues_by_node[node_id]['issues'].append(LintIssueSerializer(issue).data)
        
        return Response(list(issues_by_node.values()))


class LintIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lint issues."""
    serializer_class = LintIssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'severity', 'is_ignored', 'is_resolved', 'auto_fix_available']
    ordering = ['-severity', 'node_name']
    
    def get_queryset(self):
        user = self.request.user
        return LintIssue.objects.filter(
            Q(report__project__owner=user) |
            Q(report__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """Ignore this issue."""
        issue = self.get_object()
        issue.is_ignored = True
        issue.ignored_by = request.user
        issue.ignored_reason = request.data.get('reason', '')
        issue.ignored_at = timezone.now()
        issue.save()
        return Response({'status': 'ignored'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark issue as resolved."""
        issue = self.get_object()
        issue.is_resolved = True
        issue.resolved_by = request.user
        issue.resolved_at = timezone.now()
        issue.save()
        return Response({'status': 'resolved'})
    
    @action(detail=True, methods=['post'])
    def fix(self, request, pk=None):
        """Apply auto-fix for this issue."""
        issue = self.get_object()
        
        if not issue.auto_fix_available:
            return Response({'error': 'No auto-fix available'}, status=status.HTTP_400_BAD_REQUEST)
        
        linter = DesignLinter(issue.report.project)
        result = linter.auto_fix(
            issue_ids=[issue.id],
            preview=False,
            user=request.user,
        )
        
        return Response(result)


class AccessibilityCheckViewSet(viewsets.ModelViewSet):
    """ViewSet for managing accessibility checks."""
    serializer_class = AccessibilityCheckSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['wcag_level', 'check_type', 'is_enabled', 'severity']
    search_fields = ['name', 'description', 'wcag_criterion']
    
    def get_queryset(self):
        return AccessibilityCheck.objects.all()


class AccessibilityReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing accessibility reports."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'wcag_version', 'target_level', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AccessibilityReportListSerializer
        return AccessibilityReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        return AccessibilityReport.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct().prefetch_related('issues')
    
    @action(detail=False, methods=['post'])
    def run(self, request):
        """Run a new accessibility check."""
        serializer = RunAccessibilityCheckSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        checker = AccessibilityChecker(project)
        report = checker.run(
            triggered_by=request.user,
            wcag_version=serializer.validated_data['wcag_version'],
            target_level=serializer.validated_data['target_level'],
            node_ids=serializer.validated_data.get('node_ids'),
        )
        
        return Response(AccessibilityReportSerializer(report).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def wcag_summary(self, request, pk=None):
        """Get WCAG criterion summary."""
        report = self.get_object()
        
        from django.db.models import Count
        summary = report.issues.values('check__wcag_criterion').annotate(
            count=Count('id')
        ).order_by('check__wcag_criterion')
        
        return Response(list(summary))


class AccessibilityIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for managing accessibility issues."""
    serializer_class = AccessibilityIssueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'check', 'severity', 'is_resolved']
    ordering = ['-severity', 'node_name']
    
    def get_queryset(self):
        user = self.request.user
        return AccessibilityIssue.objects.filter(
            Q(report__project__owner=user) |
            Q(report__project__team__members=user)
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark issue as resolved."""
        issue = self.get_object()
        issue.is_resolved = True
        issue.resolved_by = request.user
        issue.resolved_at = timezone.now()
        issue.save()
        return Response({'status': 'resolved'})


class StyleUsageReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing style usage reports."""
    serializer_class = StyleUsageReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['project', 'design_system', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return StyleUsageReport.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct()
    
    @action(detail=False, methods=['post'])
    def run(self, request):
        """Run style usage analysis."""
        project_id = request.data.get('project_id')
        design_system_id = request.data.get('design_system_id')
        
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        analyzer = StyleAnalyzer(project)
        report = analyzer.run(
            triggered_by=request.user,
            design_system_id=design_system_id,
        )
        
        return Response(StyleUsageReportSerializer(report).data, status=status.HTTP_201_CREATED)


class LintIgnoreRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lint ignore rules."""
    serializer_class = LintIgnoreRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project', 'rule']
    
    def get_queryset(self):
        user = self.request.user
        return LintIgnoreRule.objects.filter(
            Q(project__owner=user) |
            Q(project__team__members=user)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

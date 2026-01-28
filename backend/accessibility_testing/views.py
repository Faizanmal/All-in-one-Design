"""
Accessibility Testing Views
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import (
    AccessibilityTest, AccessibilityIssue, ColorBlindnessSimulation,
    ScreenReaderPreview, FocusOrderTest, ContrastCheck,
    AccessibilityReport, AccessibilityGuideline
)
from .serializers import (
    AccessibilityTestSerializer, AccessibilityTestDetailSerializer,
    AccessibilityIssueSerializer, ColorBlindnessSimulationSerializer,
    ScreenReaderPreviewSerializer, FocusOrderTestSerializer,
    ContrastCheckSerializer, AccessibilityReportSerializer,
    AccessibilityGuidelineSerializer,
    RunTestSerializer, SimulateColorBlindnessSerializer,
    GenerateScreenReaderPreviewSerializer, CheckContrastSerializer,
    FixIssueSerializer, IgnoreIssueSerializer
)
from .services import (
    ColorBlindnessSimulator, ScreenReaderAnalyzer,
    FocusOrderAnalyzer, ContrastChecker
)


class AccessibilityTestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AccessibilityTest.objects.filter(user=self.request.user)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccessibilityTestDetailSerializer
        return AccessibilityTestSerializer
    
    def perform_create(self, serializer):
        test = serializer.save(user=self.request.user)
        test.status = 'running'
        test.started_at = timezone.now()
        test.save()
        # In production: run_accessibility_test.delay(test.id)
    
    @action(detail=True, methods=['get'])
    def issues(self, request, pk=None):
        """Get all issues for a test."""
        test = self.get_object()
        issues = test.issues.all()
        
        # Filter by severity
        severity = request.query_params.get('severity')
        if severity:
            issues = issues.filter(severity=severity)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            issues = issues.filter(category=category)
        
        return Response(AccessibilityIssueSerializer(issues, many=True).data)
    
    @action(detail=True, methods=['post'])
    def rerun(self, request, pk=None):
        """Rerun the accessibility test."""
        test = self.get_object()
        
        # Clear previous results
        test.issues.all().delete()
        test.status = 'running'
        test.progress = 0
        test.started_at = timezone.now()
        test.completed_at = None
        test.save()
        
        return Response(AccessibilityTestSerializer(test).data)
    
    @action(detail=True, methods=['post'])
    def generate_report(self, request, pk=None):
        """Generate accessibility report."""
        test = self.get_object()
        format = request.data.get('format', 'html')
        
        report = AccessibilityReport.objects.create(
            test=test,
            format=format,
            include_summary=request.data.get('include_summary', True),
            include_issues=request.data.get('include_issues', True),
            include_screenshots=request.data.get('include_screenshots', True),
            include_recommendations=request.data.get('include_recommendations', True)
        )
        
        # In production: generate_report.delay(report.id)
        
        return Response(AccessibilityReportSerializer(report).data)


class AccessibilityIssueViewSet(viewsets.ModelViewSet):
    serializer_class = AccessibilityIssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AccessibilityIssue.objects.filter(test__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def fix(self, request, pk=None):
        """Apply fix for an issue."""
        issue = self.get_object()
        serializer = FixIssueSerializer(data=request.data)
        
        if serializer.is_valid():
            if serializer.validated_data.get('apply_suggestion') and issue.auto_fixable:
                # Apply the suggested fix
                # In production: apply_accessibility_fix(issue)
                issue.is_fixed = True
                issue.save()
                return Response({'fixed': True, 'fix_applied': issue.suggested_fix})
            
            custom_fix = serializer.validated_data.get('custom_fix')
            if custom_fix:
                issue.is_fixed = True
                issue.save()
                return Response({'fixed': True, 'fix_applied': custom_fix})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """Ignore an issue."""
        issue = self.get_object()
        serializer = IgnoreIssueSerializer(data=request.data)
        
        if serializer.is_valid():
            issue.ignored = True
            issue.ignore_reason = serializer.validated_data['reason']
            issue.save()
            return Response({'ignored': True})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorBlindnessSimulationViewSet(viewsets.ModelViewSet):
    serializer_class = ColorBlindnessSimulationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ColorBlindnessSimulation.objects.filter(project__user=self.request.user)


class SimulateColorBlindnessView(APIView):
    """Simulate color blindness for colors."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SimulateColorBlindnessSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        simulation_type = data['simulation_type']
        colors = data.get('colors', [])
        
        results = {}
        for color in colors:
            results[color] = ColorBlindnessSimulator.simulate_color(color, simulation_type)
        
        # Find confusing color pairs
        confusing = ColorBlindnessSimulator.find_confusing_colors(colors, simulation_type)
        
        # Create simulation record
        simulation = ColorBlindnessSimulation.objects.create(
            project_id=data['project_id'],
            simulation_type=simulation_type,
            frame_id=data.get('frame_id', ''),
            color_mapping=results,
            issues=confusing
        )
        
        return Response({
            'simulation': ColorBlindnessSimulationSerializer(simulation).data,
            'color_mapping': results,
            'confusing_pairs': confusing
        })


class ScreenReaderPreviewViewSet(viewsets.ModelViewSet):
    serializer_class = ScreenReaderPreviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ScreenReaderPreview.objects.filter(project__user=self.request.user)


class GenerateScreenReaderPreviewView(APIView):
    """Generate screen reader preview for a design."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = GenerateScreenReaderPreviewSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # In production, fetch elements from the design
        elements = request.data.get('elements', [])
        
        reading_order = ScreenReaderAnalyzer.extract_reading_order(elements)
        speech_text = ScreenReaderAnalyzer.generate_speech_text(reading_order)
        issues = ScreenReaderAnalyzer.find_issues(elements)
        
        preview = ScreenReaderPreview.objects.create(
            project_id=data['project_id'],
            frame_id=data.get('frame_id', ''),
            content=reading_order,
            speech_text=speech_text,
            reading_order_issues=[i for i in issues if i['type'] in ['order_mismatch']],
            missing_alt_text=[i for i in issues if i['type'] == 'missing_alt_text']
        )
        
        return Response(ScreenReaderPreviewSerializer(preview).data)


class FocusOrderTestViewSet(viewsets.ModelViewSet):
    serializer_class = FocusOrderTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FocusOrderTest.objects.filter(project__user=self.request.user)


class TestFocusOrderView(APIView):
    """Test focus order for a design."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        project_id = request.data.get('project_id')
        frame_id = request.data.get('frame_id', '')
        elements = request.data.get('elements', [])
        
        focusable = FocusOrderAnalyzer.extract_focusable_elements(elements)
        issues = FocusOrderAnalyzer.validate_focus_order(focusable)
        focus_issues = FocusOrderAnalyzer.check_focus_indicators(elements)
        
        test = FocusOrderTest.objects.create(
            project_id=project_id,
            frame_id=frame_id,
            focus_order=focusable,
            issues=issues,
            focus_indicator_issues=focus_issues
        )
        
        return Response(FocusOrderTestSerializer(test).data)


class ContrastCheckViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContrastCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ContrastCheck.objects.filter(project__user=self.request.user)


class CheckContrastView(APIView):
    """Check contrast between two colors."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CheckContrastSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        result = ContrastChecker.check_contrast(
            data['foreground'],
            data['background'],
            data['font_size'],
            data['is_bold']
        )
        
        # Get suggestions if failing
        if not result['passes_aa']:
            suggestions = ContrastChecker.suggest_better_colors(
                data['foreground'],
                data['background'],
                result['required_for_aa']
            )
            result['suggestions'] = suggestions
        
        return Response(result)


class AccessibilityGuidelineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AccessibilityGuidelineSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AccessibilityGuideline.objects.all()
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Get guidelines grouped by level."""
        level = request.query_params.get('level', 'AA')
        
        if level == 'A':
            guidelines = self.queryset.filter(level='A')
        elif level == 'AA':
            guidelines = self.queryset.filter(level__in=['A', 'AA'])
        else:
            guidelines = self.queryset.all()
        
        return Response(AccessibilityGuidelineSerializer(guidelines, many=True).data)

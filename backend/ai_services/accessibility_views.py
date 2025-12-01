"""
Accessibility Audit API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .accessibility_service import AccessibilityAuditor, WCAGLevel


class AuditRequestSerializer(serializers.Serializer):
    """Serializer for audit requests."""
    target_level = serializers.ChoiceField(
        choices=['A', 'AA', 'AAA'],
        default='AA'
    )


class AutoFixRequestSerializer(serializers.Serializer):
    """Serializer for auto-fix requests."""
    apply_all = serializers.BooleanField(default=False)
    issue_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def audit_project(request, project_id):
    """
    Perform accessibility audit on a project.
    
    GET /api/v1/ai/accessibility/projects/{project_id}/audit/
    POST /api/v1/ai/accessibility/projects/{project_id}/audit/
    Body: {"target_level": "AA"}
    """
    from projects.models import Project, DesignComponent
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check access
    if project.user != request.user and request.user not in project.collaborators.all():
        return Response(
            {'error': 'Access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Parse target level
    if request.method == 'POST':
        serializer = AuditRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        target_level = WCAGLevel(serializer.validated_data['target_level'])
    else:
        target_level = WCAGLevel.AA
    
    # Gather design data
    components = DesignComponent.objects.filter(project=project)
    
    design_data = {
        'components': [
            {
                'id': str(c.id),
                'type': c.component_type,
                'properties': c.properties,
                'z_index': c.z_index,
            }
            for c in components
        ],
        'canvas_background': project.canvas_background,
        'color_palette': project.color_palette,
    }
    
    # Perform audit
    auditor = AccessibilityAuditor(target_level=target_level)
    results = auditor.audit_design(design_data)
    
    # Add project info
    results['project_id'] = project_id
    results['project_name'] = project.name
    
    return Response(results)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_auto_fixes(request, project_id):
    """
    Apply auto-fixes to accessibility issues.
    
    POST /api/v1/ai/accessibility/projects/{project_id}/fix/
    Body: {"apply_all": true} or {"issue_ids": ["A11Y-0001", "A11Y-0002"]}
    """
    from projects.models import Project, DesignComponent
    
    project = get_object_or_404(Project, id=project_id)
    
    # Check access (must be owner or collaborator with edit rights)
    if project.user != request.user:
        return Response(
            {'error': 'Only project owner can apply auto-fixes'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AutoFixRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Gather current design data
    components = DesignComponent.objects.filter(project=project)
    components_by_id = {str(c.id): c for c in components}
    
    design_data = {
        'components': [
            {
                'id': str(c.id),
                'type': c.component_type,
                'properties': c.properties,
                'z_index': c.z_index,
            }
            for c in components
        ],
        'canvas_background': project.canvas_background,
        'color_palette': project.color_palette,
    }
    
    # Apply fixes
    auditor = AccessibilityAuditor()
    fix_results = auditor.apply_auto_fixes(design_data)
    
    # Filter fixes if specific issue_ids provided
    if not serializer.validated_data['apply_all']:
        requested_ids = set(serializer.validated_data.get('issue_ids', []))
        fix_results['fixes_applied'] = [
            f for f in fix_results['fixes_applied']
            if f['issue_id'] in requested_ids
        ]
    
    # Apply to database
    for fix in fix_results['fixes_applied']:
        comp_id = fix['component_id']
        if comp_id in components_by_id:
            component = components_by_id[comp_id]
            if 'properties' in fix['fix_applied']:
                component.properties.update(fix['fix_applied']['properties'])
                component.save()
    
    # Return new audit results
    updated_design = {
        'components': [
            {
                'id': str(c.id),
                'type': c.component_type,
                'properties': c.properties,
                'z_index': c.z_index,
            }
            for c in DesignComponent.objects.filter(project=project)
        ],
        'canvas_background': project.canvas_background,
        'color_palette': project.color_palette,
    }
    
    new_results = auditor.audit_design(updated_design)
    
    return Response({
        'fixes_applied': fix_results['fixes_applied'],
        'fixes_count': len(fix_results['fixes_applied']),
        'updated_audit': new_results,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_contrast(request):
    """
    Check color contrast between two colors.
    
    POST /api/v1/ai/accessibility/check-contrast/
    Body: {"foreground": "#333333", "background": "#FFFFFF", "font_size": 16}
    """
    from .accessibility_service import ColorUtils
    
    foreground = request.data.get('foreground', '#000000')
    background = request.data.get('background', '#FFFFFF')
    font_size = request.data.get('font_size', 16)
    font_weight = request.data.get('font_weight', 400)
    
    try:
        ratio = ColorUtils.get_contrast_ratio(foreground, background)
    except Exception as e:
        return Response(
            {'error': f'Invalid color value: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Determine if large text
    is_large = font_size >= 18 or (font_size >= 14 and font_weight >= 700)
    
    # Check WCAG levels
    passes_aa = ratio >= (3.0 if is_large else 4.5)
    passes_aaa = ratio >= (4.5 if is_large else 7.0)
    
    # Get suggestion if failing
    suggestion = None
    if not passes_aa:
        suggestion = ColorUtils.adjust_for_contrast(
            foreground, background, 3.0 if is_large else 4.5
        )
    
    return Response({
        'foreground': foreground,
        'background': background,
        'contrast_ratio': round(ratio, 2),
        'is_large_text': is_large,
        'passes_wcag_aa': passes_aa,
        'passes_wcag_aaa': passes_aaa,
        'suggested_color': suggestion,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_palette(request):
    """
    Analyze a color palette for accessibility.
    
    POST /api/v1/ai/accessibility/analyze-palette/
    Body: {"colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"], "background": "#FFFFFF"}
    """
    from .accessibility_service import ColorUtils
    
    colors = request.data.get('colors', [])
    background = request.data.get('background', '#FFFFFF')
    
    if not colors:
        return Response(
            {'error': 'No colors provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check each color against background
    color_analysis = []
    for color in colors:
        try:
            ratio = ColorUtils.get_contrast_ratio(color, background)
            passes_aa_text = ratio >= 4.5
            passes_aa_large = ratio >= 3.0
            passes_aa_ui = ratio >= 3.0
            
            color_analysis.append({
                'color': color,
                'contrast_ratio': round(ratio, 2),
                'usable_for_text': passes_aa_text,
                'usable_for_large_text': passes_aa_large,
                'usable_for_ui': passes_aa_ui,
            })
        except Exception:
            color_analysis.append({
                'color': color,
                'error': 'Invalid color',
            })
    
    # Check for color blindness safety
    is_safe, problem_pairs = ColorUtils.is_color_blind_safe(colors)
    
    return Response({
        'background': background,
        'colors': color_analysis,
        'color_blind_safe': is_safe,
        'problem_pairs': problem_pairs,
        'recommendations': _get_palette_recommendations(color_analysis, is_safe),
    })


def _get_palette_recommendations(color_analysis, is_color_blind_safe):
    """Generate recommendations for palette."""
    recs = []
    
    usable_for_text = [c for c in color_analysis if c.get('usable_for_text')]
    
    if len(usable_for_text) < 2:
        recs.append({
            'type': 'warning',
            'message': 'Limited colors suitable for body text. Consider adding darker colors.',
        })
    
    if not is_color_blind_safe:
        recs.append({
            'type': 'warning',
            'message': 'Some colors may be confused by color blind users. '
                      'Consider adding patterns or labels.',
        })
    
    if not recs:
        recs.append({
            'type': 'success',
            'message': 'Palette has good accessibility characteristics.',
        })
    
    return recs

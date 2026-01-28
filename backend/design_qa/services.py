"""
Services for Design QA app.
"""
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone
import time

from .models import (
    LintRuleSet, LintRule, DesignLintReport, LintIssue,
    AccessibilityCheck, AccessibilityReport, AccessibilityIssue,
    StyleUsageReport, LintIgnoreRule
)


class DesignLinter:
    """
    Service for running design lint checks.
    """
    
    def __init__(self, project):
        self.project = project
    
    def run(
        self,
        triggered_by,
        rule_set_id: Optional[str] = None,
        node_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
    ) -> DesignLintReport:
        """Run lint check on the project."""
        start_time = time.time()
        
        # Get or create rule set
        if rule_set_id:
            rule_set = LintRuleSet.objects.get(id=rule_set_id)
        else:
            rule_set = LintRuleSet.objects.filter(is_default=True).first()
        
        with transaction.atomic():
            # Create report
            report = DesignLintReport.objects.create(
                project=self.project,
                rule_set=rule_set,
                status='running',
                triggered_by=triggered_by,
                trigger_type='manual',
            )
            
            # Get nodes to check
            nodes = self._get_nodes(node_ids)
            
            # Get enabled rules
            rules = rule_set.rules.filter(is_enabled=True)
            if categories:
                rules = rules.filter(category__in=categories)
            
            errors = 0
            warnings = 0
            info = 0
            
            # Run each rule
            for rule in rules:
                issues = self._run_rule(rule, nodes)
                
                for issue_data in issues:
                    # Check ignore rules
                    if self._is_ignored(rule, issue_data['node_id']):
                        continue
                    
                    issue = LintIssue.objects.create(
                        report=report,
                        rule=rule,
                        node_id=issue_data['node_id'],
                        node_type=issue_data.get('node_type', 'unknown'),
                        node_name=issue_data.get('node_name', 'Unknown'),
                        node_path=issue_data.get('node_path', ''),
                        severity=rule.severity,
                        message=issue_data.get('message', rule.error_message),
                        suggestion=issue_data.get('suggestion', rule.suggestion),
                        current_value=issue_data.get('current_value'),
                        expected_value=issue_data.get('expected_value'),
                        auto_fix_available=rule.is_auto_fixable,
                        auto_fix_data=issue_data.get('auto_fix_data'),
                    )
                    
                    if rule.severity == 'error':
                        errors += 1
                    elif rule.severity == 'warning':
                        warnings += 1
                    else:
                        info += 1
            
            # Update report
            duration = int((time.time() - start_time) * 1000)
            report.status = 'completed'
            report.total_issues = errors + warnings + info
            report.errors = errors
            report.warnings = warnings
            report.info = info
            report.nodes_checked = len(nodes)
            report.duration_ms = duration
            report.completed_at = timezone.now()
            report.save()
        
        return report
    
    def _get_nodes(self, node_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get nodes to check from project."""
        # In production, this would fetch from project's node data
        # For now, return empty list - implement based on project structure
        return []
    
    def _run_rule(self, rule: LintRule, nodes: List[Dict]) -> List[Dict]:
        """Run a single lint rule against nodes."""
        issues = []
        
        rule_type = rule.rule_type
        config = rule.configuration or {}
        
        for node in nodes:
            issue = None
            
            if rule_type == 'spacing':
                issue = self._check_spacing(node, config)
            elif rule_type == 'alignment':
                issue = self._check_alignment(node, config)
            elif rule_type == 'color':
                issue = self._check_color(node, config)
            elif rule_type == 'typography':
                issue = self._check_typography(node, config)
            elif rule_type == 'naming':
                issue = self._check_naming(node, config)
            elif rule_type == 'custom':
                issue = self._check_custom(node, config)
            
            if issue:
                issue['node_id'] = node.get('id')
                issue['node_type'] = node.get('type')
                issue['node_name'] = node.get('name')
                issues.append(issue)
        
        return issues
    
    def _check_spacing(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Check spacing rules."""
        allowed_values = config.get('allowed_values', [4, 8, 12, 16, 24, 32, 48, 64])
        
        for prop in ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'gap']:
            value = node.get(prop)
            if value and value not in allowed_values:
                return {
                    'message': f'Spacing value {value} is not in the design system',
                    'suggestion': f'Use one of: {allowed_values}',
                    'current_value': value,
                    'expected_value': self._find_closest(value, allowed_values),
                    'auto_fix_data': {
                        'property': prop,
                        'new_value': self._find_closest(value, allowed_values),
                    }
                }
        return None
    
    def _check_alignment(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Check alignment rules."""
        # Check if children are aligned
        return None
    
    def _check_color(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Check color rules."""
        allowed_colors = config.get('allowed_colors', [])
        
        for prop in ['fill', 'stroke', 'backgroundColor']:
            value = node.get(prop)
            if value and allowed_colors and value not in allowed_colors:
                return {
                    'message': f'Color {value} is not in the design system',
                    'suggestion': 'Use a color from the design system palette',
                    'current_value': value,
                }
        return None
    
    def _check_typography(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Check typography rules."""
        allowed_fonts = config.get('allowed_fonts', [])
        allowed_sizes = config.get('allowed_sizes', [])
        
        font = node.get('fontFamily')
        size = node.get('fontSize')
        
        if font and allowed_fonts and font not in allowed_fonts:
            return {
                'message': f'Font {font} is not in the design system',
                'current_value': font,
            }
        
        if size and allowed_sizes and size not in allowed_sizes:
            return {
                'message': f'Font size {size} is not in the type scale',
                'current_value': size,
                'expected_value': self._find_closest(size, allowed_sizes),
            }
        
        return None
    
    def _check_naming(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Check naming convention rules."""
        pattern = config.get('pattern')
        name = node.get('name', '')
        
        if pattern:
            import re
            if not re.match(pattern, name):
                return {
                    'message': f'Name "{name}" does not match pattern {pattern}',
                    'current_value': name,
                }
        return None
    
    def _check_custom(self, node: Dict, config: Dict) -> Optional[Dict]:
        """Run custom check logic."""
        # Custom check implementation
        return None
    
    def _find_closest(self, value: float, allowed: List[float]) -> float:
        """Find closest allowed value."""
        if not allowed:
            return value
        return min(allowed, key=lambda x: abs(x - value))
    
    def _is_ignored(self, rule: LintRule, node_id: str) -> bool:
        """Check if issue should be ignored."""
        return LintIgnoreRule.objects.filter(
            project=self.project,
            rule=rule,
            node_id=node_id,
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=timezone.now())
        ).exists()
    
    def auto_fix(
        self,
        issue_ids: List[str],
        preview: bool = True,
        user=None,
    ) -> Dict[str, Any]:
        """Auto-fix lint issues."""
        issues = LintIssue.objects.filter(
            id__in=issue_ids,
            auto_fix_available=True,
            is_resolved=False,
        )
        
        fixes = []
        for issue in issues:
            if issue.auto_fix_data:
                fixes.append({
                    'issue_id': str(issue.id),
                    'node_id': issue.node_id,
                    'fix': issue.auto_fix_data,
                })
        
        if not preview:
            # Apply fixes
            for issue in issues:
                issue.is_resolved = True
                issue.resolved_by = user
                issue.resolved_at = timezone.now()
                issue.save()
        
        return {
            'preview': preview,
            'fixes': fixes,
            'count': len(fixes),
        }


class AccessibilityChecker:
    """
    Service for running accessibility checks.
    """
    
    def __init__(self, project):
        self.project = project
    
    def run(
        self,
        triggered_by,
        wcag_version: str = '2.1',
        target_level: str = 'AA',
        node_ids: Optional[List[str]] = None,
    ) -> AccessibilityReport:
        """Run accessibility check."""
        start_time = time.time()
        
        with transaction.atomic():
            report = AccessibilityReport.objects.create(
                project=self.project,
                wcag_version=wcag_version,
                target_level=target_level,
                status='running',
                triggered_by=triggered_by,
            )
            
            # Get nodes
            nodes = self._get_nodes(node_ids)
            
            # Get enabled checks for target level
            levels = self._get_levels_to_check(target_level)
            checks = AccessibilityCheck.objects.filter(
                is_enabled=True,
                wcag_level__in=levels,
            )
            
            critical = 0
            serious = 0
            moderate = 0
            minor = 0
            
            # Run checks
            for check in checks:
                issues = self._run_check(check, nodes)
                
                for issue_data in issues:
                    issue = AccessibilityIssue.objects.create(
                        report=report,
                        check=check,
                        node_id=issue_data['node_id'],
                        node_type=issue_data.get('node_type', 'unknown'),
                        node_name=issue_data.get('node_name', 'Unknown'),
                        severity=check.severity,
                        message=issue_data.get('message', ''),
                        impact=issue_data.get('impact', 'unknown'),
                        affected_users=issue_data.get('affected_users', ''),
                        remediation=issue_data.get('remediation', ''),
                    )
                    
                    if check.severity == 'critical':
                        critical += 1
                    elif check.severity == 'serious':
                        serious += 1
                    elif check.severity == 'moderate':
                        moderate += 1
                    else:
                        minor += 1
            
            # Calculate scores
            total = critical + serious + moderate + minor
            overall_score = self._calculate_score(nodes, total, critical, serious)
            
            duration = int((time.time() - start_time) * 1000)
            
            report.status = 'completed'
            report.overall_score = overall_score
            report.level_a_score = overall_score  # Simplified
            report.level_aa_score = overall_score if target_level in ['AA', 'AAA'] else 0
            report.level_aaa_score = overall_score if target_level == 'AAA' else 0
            report.total_issues = total
            report.critical_issues = critical
            report.serious_issues = serious
            report.moderate_issues = moderate
            report.minor_issues = minor
            report.nodes_checked = len(nodes)
            report.duration_ms = duration
            report.completed_at = timezone.now()
            report.save()
        
        return report
    
    def _get_nodes(self, node_ids: Optional[List[str]] = None) -> List[Dict]:
        """Get nodes to check."""
        return []
    
    def _get_levels_to_check(self, target_level: str) -> List[str]:
        """Get WCAG levels to check based on target."""
        if target_level == 'A':
            return ['A']
        elif target_level == 'AA':
            return ['A', 'AA']
        else:
            return ['A', 'AA', 'AAA']
    
    def _run_check(self, check: AccessibilityCheck, nodes: List[Dict]) -> List[Dict]:
        """Run an accessibility check."""
        issues = []
        
        check_type = check.check_type
        
        for node in nodes:
            issue = None
            
            if check_type == 'color_contrast':
                issue = self._check_color_contrast(node, check)
            elif check_type == 'text_size':
                issue = self._check_text_size(node, check)
            elif check_type == 'touch_target':
                issue = self._check_touch_target(node, check)
            elif check_type == 'alt_text':
                issue = self._check_alt_text(node, check)
            
            if issue:
                issue['node_id'] = node.get('id')
                issue['node_type'] = node.get('type')
                issue['node_name'] = node.get('name')
                issues.append(issue)
        
        return issues
    
    def _check_color_contrast(self, node: Dict, check: AccessibilityCheck) -> Optional[Dict]:
        """Check color contrast ratio."""
        # Would implement actual contrast calculation
        return None
    
    def _check_text_size(self, node: Dict, check: AccessibilityCheck) -> Optional[Dict]:
        """Check minimum text size."""
        min_size = check.configuration.get('min_size', 12)
        size = node.get('fontSize')
        
        if size and size < min_size:
            return {
                'message': f'Text size {size}px is below minimum {min_size}px',
                'impact': 'Users with vision impairment may have difficulty reading',
                'affected_users': 'Low vision users',
                'remediation': f'Increase font size to at least {min_size}px',
            }
        return None
    
    def _check_touch_target(self, node: Dict, check: AccessibilityCheck) -> Optional[Dict]:
        """Check touch target size."""
        min_size = check.configuration.get('min_size', 44)
        width = node.get('width', 0)
        height = node.get('height', 0)
        
        if (width < min_size or height < min_size) and node.get('isInteractive'):
            return {
                'message': f'Touch target {width}x{height}px is below minimum {min_size}x{min_size}px',
                'impact': 'Users with motor impairment may have difficulty tapping',
                'affected_users': 'Motor-impaired users, mobile users',
                'remediation': f'Increase size to at least {min_size}x{min_size}px',
            }
        return None
    
    def _check_alt_text(self, node: Dict, check: AccessibilityCheck) -> Optional[Dict]:
        """Check for alt text on images."""
        if node.get('type') == 'image' and not node.get('altText'):
            return {
                'message': 'Image missing alternative text',
                'impact': 'Screen reader users cannot understand the image',
                'affected_users': 'Blind and low vision users',
                'remediation': 'Add descriptive alt text to the image',
            }
        return None
    
    def _calculate_score(self, nodes: List, total: int, critical: int, serious: int) -> float:
        """Calculate accessibility score."""
        if not nodes:
            return 100.0
        
        # Penalize based on issues
        penalty = (critical * 10 + serious * 5 + (total - critical - serious) * 2)
        score = max(0, 100 - penalty)
        return round(score, 1)


class StyleAnalyzer:
    """
    Service for analyzing style usage.
    """
    
    def __init__(self, project):
        self.project = project
    
    def run(
        self,
        triggered_by,
        design_system_id: Optional[str] = None,
    ) -> StyleUsageReport:
        """Run style usage analysis."""
        from design_systems.models import DesignSystem
        
        design_system = None
        if design_system_id:
            design_system = DesignSystem.objects.get(id=design_system_id)
        
        with transaction.atomic():
            report = StyleUsageReport.objects.create(
                project=self.project,
                design_system=design_system,
                status='running',
                triggered_by=triggered_by,
            )
            
            # Analyze styles
            color_usage = self._analyze_colors()
            typography_usage = self._analyze_typography()
            spacing_usage = self._analyze_spacing()
            component_usage = self._analyze_components()
            
            detached = self._find_detached_styles()
            unused = self._find_unused_styles(design_system)
            overrides = self._count_overrides()
            
            consistency_score = self._calculate_consistency(
                color_usage, typography_usage, spacing_usage,
                len(detached), overrides
            )
            
            report.status = 'completed'
            report.color_usage = color_usage
            report.typography_usage = typography_usage
            report.spacing_usage = spacing_usage
            report.component_usage = component_usage
            report.detached_styles = detached
            report.unused_styles = unused
            report.override_count = overrides
            report.consistency_score = consistency_score
            report.completed_at = timezone.now()
            report.save()
        
        return report
    
    def _analyze_colors(self) -> Dict:
        """Analyze color usage in project."""
        return {
            'from_system': 0,
            'custom': 0,
            'colors': []
        }
    
    def _analyze_typography(self) -> Dict:
        """Analyze typography usage."""
        return {
            'from_system': 0,
            'custom': 0,
            'styles': []
        }
    
    def _analyze_spacing(self) -> Dict:
        """Analyze spacing usage."""
        return {
            'from_system': 0,
            'custom': 0,
            'values': []
        }
    
    def _analyze_components(self) -> Dict:
        """Analyze component usage."""
        return {
            'total_instances': 0,
            'unique_components': 0,
            'components': []
        }
    
    def _find_detached_styles(self) -> List[str]:
        """Find detached styles."""
        return []
    
    def _find_unused_styles(self, design_system) -> List[str]:
        """Find unused styles in design system."""
        return []
    
    def _count_overrides(self) -> int:
        """Count style overrides."""
        return 0
    
    def _calculate_consistency(
        self,
        colors: Dict,
        typography: Dict,
        spacing: Dict,
        detached: int,
        overrides: int
    ) -> float:
        """Calculate design consistency score."""
        # Simple scoring based on system usage vs custom
        total_from_system = (
            colors.get('from_system', 0) +
            typography.get('from_system', 0) +
            spacing.get('from_system', 0)
        )
        total_custom = (
            colors.get('custom', 0) +
            typography.get('custom', 0) +
            spacing.get('custom', 0)
        )
        
        if total_from_system + total_custom == 0:
            return 100.0
        
        base_score = (total_from_system / (total_from_system + total_custom)) * 100
        penalty = min(20, detached * 2 + overrides * 0.5)
        
        return round(max(0, base_score - penalty), 1)

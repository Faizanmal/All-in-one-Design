"""
Accessibility Audit Service

Provides comprehensive accessibility checking for designs,
including WCAG compliance, color contrast analysis, and auto-fix suggestions.
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


class IssueSeverity(Enum):
    """Accessibility issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during audit."""
    id: str
    severity: IssueSeverity
    category: str
    title: str
    description: str
    wcag_criterion: str
    wcag_level: WCAGLevel
    component_id: Optional[str]
    component_type: Optional[str]
    current_value: Optional[Any]
    suggested_fix: Optional[Dict[str, Any]]
    auto_fixable: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'wcag_criterion': self.wcag_criterion,
            'wcag_level': self.wcag_level.value,
            'component_id': self.component_id,
            'component_type': self.component_type,
            'current_value': self.current_value,
            'suggested_fix': self.suggested_fix,
            'auto_fixable': self.auto_fixable,
        }


class ColorUtils:
    """Utilities for color analysis."""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """Convert RGB to hex color."""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def get_relative_luminance(r: int, g: int, b: int) -> float:
        """
        Calculate relative luminance according to WCAG 2.1.
        https://www.w3.org/WAI/GL/wiki/Relative_luminance
        """
        def adjust(c):
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    @staticmethod
    def get_contrast_ratio(color1: str, color2: str) -> float:
        """
        Calculate contrast ratio between two colors.
        https://www.w3.org/WAI/GL/wiki/Contrast_ratio
        """
        r1, g1, b1 = ColorUtils.hex_to_rgb(color1)
        r2, g2, b2 = ColorUtils.hex_to_rgb(color2)
        
        l1 = ColorUtils.get_relative_luminance(r1, g1, b1)
        l2 = ColorUtils.get_relative_luminance(r2, g2, b2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def adjust_for_contrast(
        foreground: str,
        background: str,
        target_ratio: float = 4.5
    ) -> str:
        """
        Adjust foreground color to meet target contrast ratio.
        """
        current_ratio = ColorUtils.get_contrast_ratio(foreground, background)
        
        if current_ratio >= target_ratio:
            return foreground
        
        fg_r, fg_g, fg_b = ColorUtils.hex_to_rgb(foreground)
        bg_r, bg_g, bg_b = ColorUtils.hex_to_rgb(background)
        
        bg_luminance = ColorUtils.get_relative_luminance(bg_r, bg_g, bg_b)
        
        # Determine if we should go lighter or darker
        should_lighten = bg_luminance < 0.5
        
        # Binary search for the right adjustment
        for _ in range(20):  # Max iterations
            if should_lighten:
                fg_r = min(255, fg_r + 10)
                fg_g = min(255, fg_g + 10)
                fg_b = min(255, fg_b + 10)
            else:
                fg_r = max(0, fg_r - 10)
                fg_g = max(0, fg_g - 10)
                fg_b = max(0, fg_b - 10)
            
            new_color = ColorUtils.rgb_to_hex(fg_r, fg_g, fg_b)
            new_ratio = ColorUtils.get_contrast_ratio(new_color, background)
            
            if new_ratio >= target_ratio:
                return new_color
        
        # Fallback to black or white
        return "#FFFFFF" if should_lighten else "#000000"
    
    @staticmethod
    def is_color_blind_safe(colors: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if color palette is distinguishable for color blind users.
        Returns (is_safe, list_of_problem_pairs)
        """
        # Simplified check - in production, use proper simulation
        problem_pairs = []
        
        for i, color1 in enumerate(colors):
            for color2 in colors[i+1:]:
                r1, g1, b1 = ColorUtils.hex_to_rgb(color1)
                r2, g2, b2 = ColorUtils.hex_to_rgb(color2)
                
                # Check for red-green confusion (protanopia/deuteranopia)
                if abs(r1 - r2) < 30 and abs(g1 - g2) < 30:
                    problem_pairs.append(f"{color1} and {color2}")
        
        return len(problem_pairs) == 0, problem_pairs


class AccessibilityAuditor:
    """
    Main accessibility auditor class.
    Checks designs for WCAG compliance.
    """
    
    # Minimum font sizes (in pixels)
    MIN_FONT_SIZE_BODY = 16
    MIN_FONT_SIZE_CAPTION = 12
    
    # Touch target minimum size (in pixels)
    MIN_TOUCH_TARGET = 44
    
    # Contrast requirements
    CONTRAST_NORMAL_TEXT_AA = 4.5
    CONTRAST_LARGE_TEXT_AA = 3.0
    CONTRAST_NORMAL_TEXT_AAA = 7.0
    CONTRAST_LARGE_TEXT_AAA = 4.5
    CONTRAST_UI_COMPONENTS = 3.0
    
    # Large text threshold
    LARGE_TEXT_SIZE = 18
    LARGE_TEXT_BOLD_SIZE = 14
    
    def __init__(self, target_level: WCAGLevel = WCAGLevel.AA):
        self.target_level = target_level
        self.issues: List[AccessibilityIssue] = []
        self.issue_counter = 0
    
    def check_color_contrast(self, foreground: str, background: str) -> Dict[str, Any]:
        """
        Check color contrast between foreground and background colors.
        
        Args:
            foreground: Hex color for text
            background: Hex color for background
            
        Returns:
            Dict with ratio and compliance
        """
        ratio = ColorUtils.get_contrast_ratio(foreground, background)
        compliant = ratio >= self.CONTRAST_NORMAL_TEXT
        
        return {
            'ratio': ratio,
            'compliant': compliant,
            'required_ratio': self.CONTRAST_NORMAL_TEXT,
        }

    def audit_design(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform full accessibility audit on a design.
        
        Args:
            design_data: Design data including components and settings
            
        Returns:
            Audit results with issues and score
        """
        self.issues = []
        self.issue_counter = 0
        
        components = design_data.get('components', [])
        canvas_background = design_data.get('canvas_background', '#FFFFFF')
        color_palette = design_data.get('color_palette', [])
        
        # Run all checks
        self._check_color_contrast(components, canvas_background)
        self._check_text_sizing(components)
        self._check_touch_targets(components)
        self._check_color_palette(color_palette)
        self._check_text_content(components)
        self._check_images(components)
        self._check_interactive_elements(components)
        self._check_layout(components)
        
        # Calculate score
        score = self._calculate_score()
        
        return {
            'score': score,
            'level_achieved': self._get_achieved_level(),
            'target_level': self.target_level.value,
            'total_issues': len(self.issues),
            'issues_by_severity': {
                'error': len([i for i in self.issues if i.severity == IssueSeverity.ERROR]),
                'warning': len([i for i in self.issues if i.severity == IssueSeverity.WARNING]),
                'suggestion': len([i for i in self.issues if i.severity == IssueSeverity.SUGGESTION]),
            },
            'issues_by_category': self._group_by_category(),
            'issues': [issue.to_dict() for issue in self.issues],
            'auto_fixable_count': len([i for i in self.issues if i.auto_fixable]),
            'recommendations': self._generate_recommendations(),
        }
    
    def apply_auto_fixes(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply auto-fixes to design data.
        
        Returns updated design data with fixes applied.
        """
        # First, audit to find issues
        self.audit_design(design_data)
        
        # Apply fixes
        fixes_applied = []
        components = design_data.get('components', [])
        
        for issue in self.issues:
            if not issue.auto_fixable or not issue.suggested_fix:
                continue
            
            if issue.component_id:
                # Find and update component
                for comp in components:
                    if comp.get('id') == issue.component_id:
                        fix = issue.suggested_fix
                        if 'properties' in fix:
                            comp['properties'].update(fix['properties'])
                        fixes_applied.append({
                            'issue_id': issue.id,
                            'component_id': issue.component_id,
                            'fix_applied': fix,
                        })
                        break
        
        return {
            'design_data': design_data,
            'fixes_applied': fixes_applied,
            'fixes_count': len(fixes_applied),
        }
    
    def _add_issue(
        self,
        severity: IssueSeverity,
        category: str,
        title: str,
        description: str,
        wcag_criterion: str,
        wcag_level: WCAGLevel,
        component_id: str = None,
        component_type: str = None,
        current_value: Any = None,
        suggested_fix: Dict[str, Any] = None,
        auto_fixable: bool = False
    ):
        """Add an accessibility issue to the list."""
        self.issue_counter += 1
        
        issue = AccessibilityIssue(
            id=f"A11Y-{self.issue_counter:04d}",
            severity=severity,
            category=category,
            title=title,
            description=description,
            wcag_criterion=wcag_criterion,
            wcag_level=wcag_level,
            component_id=component_id,
            component_type=component_type,
            current_value=current_value,
            suggested_fix=suggested_fix,
            auto_fixable=auto_fixable,
        )
        
        self.issues.append(issue)
    
    def _check_color_contrast(
        self,
        components: List[Dict[str, Any]],
        canvas_background: str
    ):
        """Check color contrast for text and UI elements."""
        for comp in components:
            props = comp.get('properties', {})
            comp_type = comp.get('type', '')
            comp_id = comp.get('id')
            
            if comp_type == 'text':
                text_color = props.get('color', props.get('fill', '#000000'))
                bg_color = props.get('backgroundColor', canvas_background)
                font_size = props.get('fontSize', 16)
                font_weight = props.get('fontWeight', 400)
                
                # Determine if large text
                is_large = (
                    font_size >= self.LARGE_TEXT_SIZE or
                    (font_size >= self.LARGE_TEXT_BOLD_SIZE and font_weight >= 700)
                )
                
                # Get required contrast
                if self.target_level == WCAGLevel.AAA:
                    required_ratio = self.CONTRAST_LARGE_TEXT_AAA if is_large else self.CONTRAST_NORMAL_TEXT_AAA
                else:
                    required_ratio = self.CONTRAST_LARGE_TEXT_AA if is_large else self.CONTRAST_NORMAL_TEXT_AA
                
                try:
                    contrast_ratio = ColorUtils.get_contrast_ratio(text_color, bg_color)
                    
                    if contrast_ratio < required_ratio:
                        adjusted_color = ColorUtils.adjust_for_contrast(
                            text_color, bg_color, required_ratio
                        )
                        
                        self._add_issue(
                            severity=IssueSeverity.ERROR,
                            category='color_contrast',
                            title='Insufficient Text Contrast',
                            description=f"Text has contrast ratio of {contrast_ratio:.2f}:1, "
                                       f"but requires {required_ratio}:1 for WCAG {self.target_level.value}.",
                            wcag_criterion='1.4.3 Contrast (Minimum)',
                            wcag_level=WCAGLevel.AA,
                            component_id=comp_id,
                            component_type=comp_type,
                            current_value={'color': text_color, 'background': bg_color, 'ratio': contrast_ratio},
                            suggested_fix={'properties': {'color': adjusted_color}},
                            auto_fixable=True,
                        )
                except Exception:
                    pass
            
            elif comp_type in ['button', 'icon', 'shape']:
                # Check UI component contrast
                fill_color = props.get('fill', props.get('backgroundColor', '#FFFFFF'))
                # border_color not used
                _ = props.get('borderColor', props.get('stroke'))
                
                if fill_color:
                    try:
                        ratio = ColorUtils.get_contrast_ratio(fill_color, canvas_background)
                        
                        if ratio < self.CONTRAST_UI_COMPONENTS:
                            self._add_issue(
                                severity=IssueSeverity.WARNING,
                                category='color_contrast',
                                title='Low UI Component Contrast',
                                description=f"UI component has contrast ratio of {ratio:.2f}:1, "
                                           f"but requires {self.CONTRAST_UI_COMPONENTS}:1.",
                                wcag_criterion='1.4.11 Non-text Contrast',
                                wcag_level=WCAGLevel.AA,
                                component_id=comp_id,
                                component_type=comp_type,
                                current_value={'fill': fill_color, 'ratio': ratio},
                                suggested_fix=None,
                                auto_fixable=False,
                            )
                    except Exception:
                        pass
    
    def _check_text_sizing(self, components: List[Dict[str, Any]]):
        """Check text sizing for readability."""
        for comp in components:
            if comp.get('type') != 'text':
                continue
            
            props = comp.get('properties', {})
            comp_id = comp.get('id')
            font_size = props.get('fontSize', 16)
            
            if font_size < self.MIN_FONT_SIZE_CAPTION:
                self._add_issue(
                    severity=IssueSeverity.ERROR,
                    category='text_sizing',
                    title='Text Too Small',
                    description=f"Text is {font_size}px, which may be difficult to read. "
                               f"Minimum recommended size is {self.MIN_FONT_SIZE_CAPTION}px.",
                    wcag_criterion='1.4.4 Resize Text',
                    wcag_level=WCAGLevel.AA,
                    component_id=comp_id,
                    component_type='text',
                    current_value={'fontSize': font_size},
                    suggested_fix={'properties': {'fontSize': self.MIN_FONT_SIZE_BODY}},
                    auto_fixable=True,
                )
            elif font_size < self.MIN_FONT_SIZE_BODY:
                self._add_issue(
                    severity=IssueSeverity.WARNING,
                    category='text_sizing',
                    title='Small Body Text',
                    description=f"Body text at {font_size}px may be hard to read. "
                               f"Consider using {self.MIN_FONT_SIZE_BODY}px or larger.",
                    wcag_criterion='1.4.4 Resize Text',
                    wcag_level=WCAGLevel.AA,
                    component_id=comp_id,
                    component_type='text',
                    current_value={'fontSize': font_size},
                    suggested_fix={'properties': {'fontSize': self.MIN_FONT_SIZE_BODY}},
                    auto_fixable=True,
                )
    
    def _check_touch_targets(self, components: List[Dict[str, Any]]):
        """Check interactive element sizes for touch accessibility."""
        interactive_types = ['button', 'link', 'input', 'checkbox', 'radio', 'toggle']
        
        for comp in components:
            if comp.get('type') not in interactive_types:
                continue
            
            props = comp.get('properties', {})
            comp_id = comp.get('id')
            
            width = props.get('width', 0)
            height = props.get('height', 0)
            
            if width < self.MIN_TOUCH_TARGET or height < self.MIN_TOUCH_TARGET:
                self._add_issue(
                    severity=IssueSeverity.WARNING,
                    category='touch_targets',
                    title='Touch Target Too Small',
                    description=f"Interactive element is {width}x{height}px. "
                               f"Minimum touch target should be {self.MIN_TOUCH_TARGET}x{self.MIN_TOUCH_TARGET}px.",
                    wcag_criterion='2.5.5 Target Size',
                    wcag_level=WCAGLevel.AAA,
                    component_id=comp_id,
                    component_type=comp.get('type'),
                    current_value={'width': width, 'height': height},
                    suggested_fix={
                        'properties': {
                            'width': max(width, self.MIN_TOUCH_TARGET),
                            'height': max(height, self.MIN_TOUCH_TARGET),
                        }
                    },
                    auto_fixable=True,
                )
    
    def _check_color_palette(self, color_palette: List[str]):
        """Check color palette for color blindness safety."""
        if len(color_palette) < 2:
            return
        
        is_safe, problem_pairs = ColorUtils.is_color_blind_safe(color_palette)
        
        if not is_safe:
            self._add_issue(
                severity=IssueSeverity.WARNING,
                category='color_blindness',
                title='Color Palette May Confuse Color Blind Users',
                description=f"Some color pairs may be difficult to distinguish: {', '.join(problem_pairs[:3])}",
                wcag_criterion='1.4.1 Use of Color',
                wcag_level=WCAGLevel.A,
                component_id=None,
                component_type=None,
                current_value={'palette': color_palette, 'problem_pairs': problem_pairs},
                suggested_fix=None,
                auto_fixable=False,
            )
    
    def _check_text_content(self, components: List[Dict[str, Any]]):
        """Check text content for accessibility issues."""
        for comp in components:
            if comp.get('type') != 'text':
                continue
            
            props = comp.get('properties', {})
            comp_id = comp.get('id')
            text = props.get('text', '')
            
            # Check for ALL CAPS text (harder to read)
            if text and text.isupper() and len(text) > 10:
                self._add_issue(
                    severity=IssueSeverity.SUGGESTION,
                    category='readability',
                    title='All Caps Text May Be Hard to Read',
                    description="Long text in all capitals is harder to read. "
                               "Consider using sentence case.",
                    wcag_criterion='3.1.5 Reading Level',
                    wcag_level=WCAGLevel.AAA,
                    component_id=comp_id,
                    component_type='text',
                    current_value={'text': text[:50] + '...' if len(text) > 50 else text},
                    suggested_fix=None,
                    auto_fixable=False,
                )
            
            # Check line height for readability
            line_height = props.get('lineHeight', 1.2)
            if line_height < 1.5:
                self._add_issue(
                    severity=IssueSeverity.SUGGESTION,
                    category='readability',
                    title='Low Line Height',
                    description=f"Line height of {line_height} may reduce readability. "
                               f"Consider using 1.5 or higher.",
                    wcag_criterion='1.4.12 Text Spacing',
                    wcag_level=WCAGLevel.AA,
                    component_id=comp_id,
                    component_type='text',
                    current_value={'lineHeight': line_height},
                    suggested_fix={'properties': {'lineHeight': 1.5}},
                    auto_fixable=True,
                )
    
    def _check_images(self, components: List[Dict[str, Any]]):
        """Check images for accessibility requirements."""
        for comp in components:
            if comp.get('type') != 'image':
                continue
            
            props = comp.get('properties', {})
            comp_id = comp.get('id')
            alt_text = props.get('alt', props.get('altText', ''))
            
            if not alt_text:
                self._add_issue(
                    severity=IssueSeverity.ERROR,
                    category='images',
                    title='Missing Alt Text',
                    description="Image is missing alternative text. "
                               "Screen reader users won't know what the image shows.",
                    wcag_criterion='1.1.1 Non-text Content',
                    wcag_level=WCAGLevel.A,
                    component_id=comp_id,
                    component_type='image',
                    current_value=None,
                    suggested_fix=None,
                    auto_fixable=False,
                )
            elif len(alt_text) < 5:
                self._add_issue(
                    severity=IssueSeverity.WARNING,
                    category='images',
                    title='Alt Text Too Short',
                    description=f"Alt text '{alt_text}' may not adequately describe the image.",
                    wcag_criterion='1.1.1 Non-text Content',
                    wcag_level=WCAGLevel.A,
                    component_id=comp_id,
                    component_type='image',
                    current_value={'alt': alt_text},
                    suggested_fix=None,
                    auto_fixable=False,
                )
    
    def _check_interactive_elements(self, components: List[Dict[str, Any]]):
        """Check interactive elements for proper labeling."""
        interactive_types = ['button', 'input', 'link']
        
        for comp in components:
            if comp.get('type') not in interactive_types:
                continue
            
            props = comp.get('properties', {})
            comp_id = comp.get('id')
            comp_type = comp.get('type')
            
            # Check for accessible name
            label = props.get('label', props.get('text', props.get('ariaLabel', '')))
            
            if not label:
                self._add_issue(
                    severity=IssueSeverity.ERROR,
                    category='interactive',
                    title=f'{comp_type.title()} Missing Accessible Name',
                    description=f"Interactive {comp_type} has no accessible label. "
                               f"Add a label or aria-label attribute.",
                    wcag_criterion='4.1.2 Name, Role, Value',
                    wcag_level=WCAGLevel.A,
                    component_id=comp_id,
                    component_type=comp_type,
                    current_value=None,
                    suggested_fix=None,
                    auto_fixable=False,
                )
    
    def _check_layout(self, components: List[Dict[str, Any]]):
        """Check layout for logical reading order."""
        # Check for overlapping elements that might confuse reading order
        for i, comp1 in enumerate(components):
            props1 = comp1.get('properties', {})
            x1 = props1.get('x', props1.get('left', 0))
            y1 = props1.get('y', props1.get('top', 0))
            w1 = props1.get('width', 0)
            h1 = props1.get('height', 0)
            
            for comp2 in components[i+1:]:
                props2 = comp2.get('properties', {})
                x2 = props2.get('x', props2.get('left', 0))
                y2 = props2.get('y', props2.get('top', 0))
                w2 = props2.get('width', 0)
                h2 = props2.get('height', 0)
                
                # Check for significant overlap
                overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = overlap_x * overlap_y
                
                min_area = min(w1 * h1, w2 * h2) if w1 * h1 > 0 and w2 * h2 > 0 else 1
                
                if overlap_area / min_area > 0.5:
                    self._add_issue(
                        severity=IssueSeverity.WARNING,
                        category='layout',
                        title='Overlapping Elements',
                        description="Significantly overlapping elements may confuse screen readers.",
                        wcag_criterion='1.3.2 Meaningful Sequence',
                        wcag_level=WCAGLevel.A,
                        component_id=comp1.get('id'),
                        component_type=comp1.get('type'),
                        current_value={
                            'element1': comp1.get('id'),
                            'element2': comp2.get('id'),
                            'overlap_percent': int(overlap_area / min_area * 100)
                        },
                        suggested_fix=None,
                        auto_fixable=False,
                    )
                    break  # Only report once per component
    
    def _calculate_score(self) -> int:
        """Calculate accessibility score (0-100)."""
        if not self.issues:
            return 100
        
        # Weight issues by severity
        error_weight = 10
        warning_weight = 5
        suggestion_weight = 1
        
        total_deduction = sum(
            error_weight if i.severity == IssueSeverity.ERROR
            else warning_weight if i.severity == IssueSeverity.WARNING
            else suggestion_weight
            for i in self.issues
        )
        
        return max(0, 100 - total_deduction)
    
    def _get_achieved_level(self) -> Optional[str]:
        """Determine which WCAG level is achieved."""
        level_a_errors = any(
            i.wcag_level == WCAGLevel.A and i.severity == IssueSeverity.ERROR
            for i in self.issues
        )
        
        level_aa_errors = any(
            i.wcag_level == WCAGLevel.AA and i.severity == IssueSeverity.ERROR
            for i in self.issues
        )
        
        if level_a_errors:
            return None
        elif level_aa_errors:
            return WCAGLevel.A.value
        else:
            return WCAGLevel.AA.value
    
    def _group_by_category(self) -> Dict[str, int]:
        """Group issues by category."""
        categories = {}
        for issue in self.issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1
        return categories
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Prioritize by severity and count
        category_counts = self._group_by_category()
        
        if category_counts.get('color_contrast', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'title': 'Fix Color Contrast Issues',
                'description': 'Low contrast text is the most common accessibility barrier. '
                              'Ensure all text meets WCAG contrast requirements.',
            })
        
        if category_counts.get('images', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'title': 'Add Alt Text to Images',
                'description': 'Screen reader users rely on alt text to understand images. '
                              'Add descriptive text to all meaningful images.',
            })
        
        if category_counts.get('interactive', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'title': 'Label Interactive Elements',
                'description': 'Buttons and form elements need accessible names for '
                              'screen reader users to understand their purpose.',
            })
        
        if category_counts.get('touch_targets', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'title': 'Increase Touch Target Sizes',
                'description': 'Small touch targets are difficult for users with motor '
                              'impairments. Minimum size should be 44x44 pixels.',
            })
        
        return recommendations

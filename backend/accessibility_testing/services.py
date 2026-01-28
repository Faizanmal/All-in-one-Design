"""
Enhanced Accessibility Testing Services

Color blindness simulation, screen reader content analysis, focus order testing.
"""

from typing import Dict, List, Any, Tuple
import math


class ColorBlindnessSimulator:
    """Simulate different types of color blindness."""
    
    # Color transformation matrices for different types
    MATRICES = {
        'protanopia': [
            [0.567, 0.433, 0.0],
            [0.558, 0.442, 0.0],
            [0.0, 0.242, 0.758]
        ],
        'deuteranopia': [
            [0.625, 0.375, 0.0],
            [0.7, 0.3, 0.0],
            [0.0, 0.3, 0.7]
        ],
        'tritanopia': [
            [0.95, 0.05, 0.0],
            [0.0, 0.433, 0.567],
            [0.0, 0.475, 0.525]
        ],
        'achromatopsia': [
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114]
        ],
    }
    
    @classmethod
    def simulate_color(cls, color: str, blindness_type: str) -> str:
        """Simulate how a color appears with specific color blindness."""
        r, g, b = cls._hex_to_rgb(color)
        
        matrix = cls.MATRICES.get(blindness_type)
        if not matrix:
            return color
        
        new_r = int(matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b)
        new_g = int(matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b)
        new_b = int(matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b)
        
        # Clamp values
        new_r = max(0, min(255, new_r))
        new_g = max(0, min(255, new_g))
        new_b = max(0, min(255, new_b))
        
        return f"#{new_r:02x}{new_g:02x}{new_b:02x}"
    
    @classmethod
    def find_confusing_colors(cls, colors: List[str], blindness_type: str, threshold: float = 20) -> List[Dict]:
        """Find colors that become indistinguishable."""
        confusing = []
        simulated = [(c, cls.simulate_color(c, blindness_type)) for c in colors]
        
        for i, (orig1, sim1) in enumerate(simulated):
            for j, (orig2, sim2) in enumerate(simulated[i+1:], i+1):
                if orig1 != orig2:
                    distance = cls._color_distance(sim1, sim2)
                    if distance < threshold:
                        confusing.append({
                            'color1': orig1,
                            'color2': orig2,
                            'simulated1': sim1,
                            'simulated2': sim2,
                            'distance': distance
                        })
        
        return confusing
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def _color_distance(color1: str, color2: str) -> float:
        r1, g1, b1 = ColorBlindnessSimulator._hex_to_rgb(color1)
        r2, g2, b2 = ColorBlindnessSimulator._hex_to_rgb(color2)
        return math.sqrt((r2-r1)**2 + (g2-g1)**2 + (b2-b1)**2)


class ScreenReaderAnalyzer:
    """Analyze content for screen reader accessibility."""
    
    @staticmethod
    def extract_reading_order(elements: List[Dict]) -> List[Dict]:
        """Extract reading order from design elements."""
        reading_order = []
        
        # Sort by visual position (top to bottom, left to right)
        sorted_elements = sorted(elements, key=lambda e: (e.get('y', 0), e.get('x', 0)))
        
        for elem in sorted_elements:
            item = {
                'element_id': elem.get('id'),
                'type': ScreenReaderAnalyzer._get_semantic_type(elem),
                'text': ScreenReaderAnalyzer._get_accessible_text(elem),
                'role': elem.get('aria_role', ''),
                'level': elem.get('heading_level'),
            }
            reading_order.append(item)
        
        return reading_order
    
    @staticmethod
    def _get_semantic_type(element: Dict) -> str:
        """Determine semantic type of element."""
        elem_type = element.get('type', '').lower()
        role = element.get('aria_role', '')
        
        if role:
            return role
        
        type_mapping = {
            'text': 'text',
            'heading': 'heading',
            'button': 'button',
            'link': 'link',
            'image': 'image',
            'input': 'textbox',
            'checkbox': 'checkbox',
            'radio': 'radio',
            'list': 'list',
            'listitem': 'listitem',
        }
        
        return type_mapping.get(elem_type, 'group')
    
    @staticmethod
    def _get_accessible_text(element: Dict) -> str:
        """Get accessible text for element."""
        # Priority: aria-label > aria-labelledby > alt > title > visible text
        if element.get('aria_label'):
            return element['aria_label']
        if element.get('alt'):
            return element['alt']
        if element.get('title'):
            return element['title']
        if element.get('text'):
            return element['text']
        return ''
    
    @staticmethod
    def generate_speech_text(reading_order: List[Dict]) -> str:
        """Generate text as a screen reader would announce it."""
        announcements = []
        
        for item in reading_order:
            item_type = item['type']
            text = item['text']
            
            if item_type == 'heading':
                level = item.get('level', 1)
                announcements.append(f"Heading level {level}: {text}")
            elif item_type == 'button':
                announcements.append(f"{text}, button")
            elif item_type == 'link':
                announcements.append(f"{text}, link")
            elif item_type == 'image':
                if text:
                    announcements.append(f"Image: {text}")
                else:
                    announcements.append("Image (no description)")
            elif item_type == 'textbox':
                label = text or 'unlabeled'
                announcements.append(f"{label}, edit text")
            elif item_type == 'checkbox':
                state = 'checked' if item.get('checked') else 'not checked'
                announcements.append(f"{text}, checkbox, {state}")
            else:
                if text:
                    announcements.append(text)
        
        return '\n'.join(announcements)
    
    @staticmethod
    def find_issues(elements: List[Dict]) -> List[Dict]:
        """Find screen reader accessibility issues."""
        issues = []
        
        for elem in elements:
            elem_type = elem.get('type', '').lower()
            elem_id = elem.get('id')
            
            # Check for missing alt text on images
            if elem_type == 'image':
                if not elem.get('alt') and not elem.get('aria_label'):
                    issues.append({
                        'type': 'missing_alt_text',
                        'element_id': elem_id,
                        'severity': 'error',
                        'description': 'Image is missing alternative text'
                    })
            
            # Check for missing labels on form elements
            if elem_type in ['input', 'textbox', 'checkbox', 'radio', 'select']:
                if not elem.get('aria_label') and not elem.get('label'):
                    issues.append({
                        'type': 'missing_label',
                        'element_id': elem_id,
                        'severity': 'error',
                        'description': 'Form element is missing a label'
                    })
            
            # Check for empty buttons/links
            if elem_type in ['button', 'link']:
                if not elem.get('text') and not elem.get('aria_label'):
                    issues.append({
                        'type': 'empty_interactive',
                        'element_id': elem_id,
                        'severity': 'error',
                        'description': f'{elem_type.title()} has no accessible name'
                    })
        
        return issues


class FocusOrderAnalyzer:
    """Analyze and validate focus order."""
    
    @staticmethod
    def extract_focusable_elements(elements: List[Dict]) -> List[Dict]:
        """Extract focusable elements in tab order."""
        focusable = []
        
        focusable_types = ['button', 'link', 'input', 'textbox', 'checkbox', 
                          'radio', 'select', 'textarea', 'a']
        
        for elem in elements:
            elem_type = elem.get('type', '').lower()
            tab_index = elem.get('tabindex')
            
            # Check if naturally focusable or has tabindex
            is_focusable = (
                elem_type in focusable_types or
                tab_index is not None and tab_index >= 0 or
                elem.get('role') in ['button', 'link', 'checkbox', 'radio', 'textbox']
            )
            
            if is_focusable and tab_index != -1:
                focusable.append({
                    'element_id': elem.get('id'),
                    'type': elem_type,
                    'name': elem.get('text') or elem.get('aria_label') or 'Unnamed',
                    'tabindex': tab_index,
                    'x': elem.get('x', 0),
                    'y': elem.get('y', 0)
                })
        
        # Sort by tabindex (positive values first), then by position
        focusable.sort(key=lambda e: (
            0 if e['tabindex'] and e['tabindex'] > 0 else 1,
            e['tabindex'] or 0,
            e['y'],
            e['x']
        ))
        
        # Add order numbers
        for i, elem in enumerate(focusable, 1):
            elem['order'] = i
        
        return focusable
    
    @staticmethod
    def validate_focus_order(focusable: List[Dict]) -> List[Dict]:
        """Validate focus order for accessibility issues."""
        issues = []
        
        if not focusable:
            return issues
        
        # Check for positive tabindex (generally bad practice)
        positive_tabindex = [e for e in focusable if e.get('tabindex') and e['tabindex'] > 0]
        if positive_tabindex:
            issues.append({
                'type': 'positive_tabindex',
                'elements': [e['element_id'] for e in positive_tabindex],
                'severity': 'warning',
                'description': 'Positive tabindex values can disrupt expected focus order'
            })
        
        # Check for visual order vs tab order mismatch
        visual_order = sorted(focusable, key=lambda e: (e['y'], e['x']))
        for i, (visual, tab) in enumerate(zip(visual_order, focusable)):
            if visual['element_id'] != tab['element_id']:
                issues.append({
                    'type': 'order_mismatch',
                    'position': i + 1,
                    'visual_element': visual['element_id'],
                    'tab_element': tab['element_id'],
                    'severity': 'warning',
                    'description': 'Tab order does not match visual order'
                })
                break  # Report first mismatch
        
        return issues
    
    @staticmethod
    def check_focus_indicators(elements: List[Dict]) -> List[Dict]:
        """Check for visible focus indicators."""
        issues = []
        
        for elem in elements:
            if not elem.get('has_focus_style', True):  # Assume has focus unless marked otherwise
                issues.append({
                    'type': 'missing_focus_indicator',
                    'element_id': elem.get('id'),
                    'severity': 'error',
                    'description': 'Element has no visible focus indicator'
                })
        
        return issues


class ContrastChecker:
    """Check color contrast ratios."""
    
    @staticmethod
    def check_contrast(foreground: str, background: str, font_size: float = 16, is_bold: bool = False) -> Dict:
        """Check contrast ratio between two colors."""
        ratio = ContrastChecker._calculate_contrast_ratio(foreground, background)
        
        # Large text: 18pt+ or 14pt+ bold (approx 24px or 18.5px)
        is_large = font_size >= 24 or (font_size >= 18.5 and is_bold)
        
        # WCAG thresholds
        if is_large:
            passes_aa = ratio >= 3.0
            passes_aaa = ratio >= 4.5
        else:
            passes_aa = ratio >= 4.5
            passes_aaa = ratio >= 7.0
        
        return {
            'contrast_ratio': round(ratio, 2),
            'is_large_text': is_large,
            'passes_aa': passes_aa,
            'passes_aaa': passes_aaa,
            'required_for_aa': 3.0 if is_large else 4.5,
            'required_for_aaa': 4.5 if is_large else 7.0
        }
    
    @staticmethod
    def suggest_better_colors(foreground: str, background: str, target_ratio: float = 4.5) -> Dict:
        """Suggest colors that meet contrast requirements."""
        current_ratio = ContrastChecker._calculate_contrast_ratio(foreground, background)
        
        if current_ratio >= target_ratio:
            return {'foreground': foreground, 'background': background}
        
        # Try darkening foreground
        dark_fg = ContrastChecker._adjust_lightness(foreground, -0.3)
        if ContrastChecker._calculate_contrast_ratio(dark_fg, background) >= target_ratio:
            return {'foreground': dark_fg, 'background': background}
        
        # Try lightening background
        light_bg = ContrastChecker._adjust_lightness(background, 0.3)
        if ContrastChecker._calculate_contrast_ratio(foreground, light_bg) >= target_ratio:
            return {'foreground': foreground, 'background': light_bg}
        
        # Return black/white as fallback
        return {
            'foreground': '#000000',
            'background': '#ffffff'
        }
    
    @staticmethod
    def _calculate_contrast_ratio(color1: str, color2: str) -> float:
        l1 = ContrastChecker._get_luminance(color1)
        l2 = ContrastChecker._get_luminance(color2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def _get_luminance(hex_color: str) -> float:
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        
        def adjust(c):
            c = c / 255
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        
        return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)
    
    @staticmethod
    def _adjust_lightness(hex_color: str, amount: float) -> str:
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        
        # Simple lightness adjustment
        if amount > 0:
            r = int(r + (255 - r) * amount)
            g = int(g + (255 - g) * amount)
            b = int(b + (255 - b) * amount)
        else:
            r = int(r * (1 + amount))
            g = int(g * (1 + amount))
            b = int(b * (1 + amount))
        
        return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"

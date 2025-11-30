"""
Design System Service
Generate and manage design systems from projects
"""
import json
from typing import Dict, List, Optional
from collections import Counter


class DesignSystemService:
    """Service for creating and exporting design systems"""
    
    def extract_design_system(self, design_data: Dict, 
                              name: str = 'Design System') -> Dict:
        """
        Extract design system tokens from design data
        
        Args:
            design_data: Design structure
            name: Name for the design system
            
        Returns:
            Design system token structure
        """
        elements = design_data.get('elements', [])
        
        # Extract colors
        colors = self._extract_colors(elements)
        
        # Extract typography
        typography = self._extract_typography(elements)
        
        # Extract spacing
        spacing = self._extract_spacing(elements)
        
        # Extract radii
        radii = self._extract_radii(elements)
        
        # Extract shadows
        shadows = self._extract_shadows(elements)
        
        return {
            'name': name,
            'version': '1.0.0',
            'colors': colors,
            'typography': typography,
            'spacing': spacing,
            'radii': radii,
            'shadows': shadows,
            'breakpoints': {
                'sm': '640px',
                'md': '768px',
                'lg': '1024px',
                'xl': '1280px',
                '2xl': '1536px'
            }
        }
    
    def _extract_colors(self, elements: List[Dict]) -> Dict:
        """Extract color palette from elements"""
        colors = []
        
        def collect_colors(elems):
            for elem in elems:
                fills = elem.get('fills', [])
                for fill in fills:
                    if fill.get('color'):
                        colors.append(fill['color'])
                
                strokes = elem.get('strokes', [])
                for stroke in strokes:
                    if stroke.get('color'):
                        colors.append(stroke['color'])
                
                children = elem.get('children', [])
                if children:
                    collect_colors(children)
        
        collect_colors(elements)
        
        # Count and sort by frequency
        color_counts = Counter(colors)
        sorted_colors = [c for c, _ in color_counts.most_common()]
        
        # Categorize colors
        categorized = {
            'primary': sorted_colors[0] if sorted_colors else '#2196F3',
            'secondary': sorted_colors[1] if len(sorted_colors) > 1 else '#9C27B0',
            'palette': sorted_colors[:10],
            'semantic': {
                'success': '#4CAF50',
                'warning': '#FF9800',
                'error': '#F44336',
                'info': '#2196F3'
            }
        }
        
        return categorized
    
    def _extract_typography(self, elements: List[Dict]) -> Dict:
        """Extract typography tokens from elements"""
        fonts = []
        sizes = []
        weights = []
        line_heights = []
        
        def collect_typography(elems):
            for elem in elems:
                if elem.get('type') == 'text':
                    style = elem.get('textStyle', {})
                    if style.get('fontFamily'):
                        fonts.append(style['fontFamily'])
                    if style.get('fontSize'):
                        sizes.append(style['fontSize'])
                    if style.get('fontWeight'):
                        weights.append(style['fontWeight'])
                    if style.get('lineHeight'):
                        line_heights.append(style['lineHeight'])
                
                children = elem.get('children', [])
                if children:
                    collect_typography(children)
        
        collect_typography(elements)
        
        # Get most common values
        font_counts = Counter(fonts)
        size_counts = Counter(sizes)
        
        sorted_fonts = [f for f, _ in font_counts.most_common()]
        sorted_sizes = sorted(set(sizes))
        
        return {
            'fontFamilies': {
                'heading': sorted_fonts[0] if sorted_fonts else 'Inter',
                'body': sorted_fonts[1] if len(sorted_fonts) > 1 else sorted_fonts[0] if sorted_fonts else 'Inter',
                'mono': 'JetBrains Mono'
            },
            'fontSizes': {
                'xs': f'{sorted_sizes[0]}px' if sorted_sizes else '12px',
                'sm': f'{sorted_sizes[1] if len(sorted_sizes) > 1 else 14}px',
                'base': f'{sorted_sizes[2] if len(sorted_sizes) > 2 else 16}px',
                'lg': f'{sorted_sizes[3] if len(sorted_sizes) > 3 else 18}px',
                'xl': f'{sorted_sizes[4] if len(sorted_sizes) > 4 else 20}px',
                '2xl': f'{sorted_sizes[5] if len(sorted_sizes) > 5 else 24}px',
                '3xl': f'{sorted_sizes[6] if len(sorted_sizes) > 6 else 30}px',
            },
            'fontWeights': {
                'light': 300,
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            },
            'lineHeights': {
                'tight': 1.25,
                'normal': 1.5,
                'relaxed': 1.75
            }
        }
    
    def _extract_spacing(self, elements: List[Dict]) -> Dict:
        """Extract spacing tokens from elements"""
        # Generate standard spacing scale
        return {
            '0': '0px',
            '1': '4px',
            '2': '8px',
            '3': '12px',
            '4': '16px',
            '5': '20px',
            '6': '24px',
            '8': '32px',
            '10': '40px',
            '12': '48px',
            '16': '64px',
            '20': '80px',
            '24': '96px'
        }
    
    def _extract_radii(self, elements: List[Dict]) -> Dict:
        """Extract border radius tokens from elements"""
        radii = []
        
        def collect_radii(elems):
            for elem in elems:
                radius = elem.get('borderRadius', 0)
                if radius:
                    radii.append(radius)
                children = elem.get('children', [])
                if children:
                    collect_radii(children)
        
        collect_radii(elements)
        sorted_radii = sorted(set(radii))
        
        return {
            'none': '0px',
            'sm': f'{sorted_radii[0] if sorted_radii else 4}px',
            'md': f'{sorted_radii[1] if len(sorted_radii) > 1 else 8}px',
            'lg': f'{sorted_radii[2] if len(sorted_radii) > 2 else 16}px',
            'xl': f'{sorted_radii[3] if len(sorted_radii) > 3 else 24}px',
            'full': '9999px'
        }
    
    def _extract_shadows(self, elements: List[Dict]) -> Dict:
        """Extract shadow tokens from elements"""
        return {
            'none': 'none',
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
            '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)'
        }
    
    def export_to_css_variables(self, design_system: Dict) -> str:
        """Export design system as CSS custom properties"""
        lines = [':root {']
        
        # Colors
        colors = design_system.get('colors', {})
        if colors.get('primary'):
            lines.append(f"  --color-primary: {colors['primary']};")
        if colors.get('secondary'):
            lines.append(f"  --color-secondary: {colors['secondary']};")
        for i, color in enumerate(colors.get('palette', [])):
            lines.append(f"  --color-palette-{i}: {color};")
        for name, color in colors.get('semantic', {}).items():
            lines.append(f"  --color-{name}: {color};")
        
        lines.append('')
        
        # Typography
        typography = design_system.get('typography', {})
        for name, font in typography.get('fontFamilies', {}).items():
            lines.append(f"  --font-{name}: '{font}', sans-serif;")
        for name, size in typography.get('fontSizes', {}).items():
            lines.append(f"  --font-size-{name}: {size};")
        for name, weight in typography.get('fontWeights', {}).items():
            lines.append(f"  --font-weight-{name}: {weight};")
        
        lines.append('')
        
        # Spacing
        for name, value in design_system.get('spacing', {}).items():
            lines.append(f"  --spacing-{name}: {value};")
        
        lines.append('')
        
        # Border radius
        for name, value in design_system.get('radii', {}).items():
            lines.append(f"  --radius-{name}: {value};")
        
        lines.append('')
        
        # Shadows
        for name, value in design_system.get('shadows', {}).items():
            lines.append(f"  --shadow-{name}: {value};")
        
        lines.append('')
        
        # Breakpoints
        for name, value in design_system.get('breakpoints', {}).items():
            lines.append(f"  --breakpoint-{name}: {value};")
        
        lines.append('}')
        
        return '\n'.join(lines)
    
    def export_to_scss_variables(self, design_system: Dict) -> str:
        """Export design system as SCSS variables"""
        lines = ['// Design System Variables', '// Generated automatically', '']
        
        # Colors
        lines.append('// Colors')
        colors = design_system.get('colors', {})
        if colors.get('primary'):
            lines.append(f"$color-primary: {colors['primary']};")
        if colors.get('secondary'):
            lines.append(f"$color-secondary: {colors['secondary']};")
        for i, color in enumerate(colors.get('palette', [])):
            lines.append(f"$color-palette-{i}: {color};")
        for name, color in colors.get('semantic', {}).items():
            lines.append(f"$color-{name}: {color};")
        
        lines.append('')
        
        # Typography
        lines.append('// Typography')
        typography = design_system.get('typography', {})
        for name, font in typography.get('fontFamilies', {}).items():
            lines.append(f"$font-{name}: '{font}', sans-serif;")
        for name, size in typography.get('fontSizes', {}).items():
            lines.append(f"$font-size-{name}: {size};")
        for name, weight in typography.get('fontWeights', {}).items():
            lines.append(f"$font-weight-{name}: {weight};")
        
        lines.append('')
        
        # Spacing
        lines.append('// Spacing')
        for name, value in design_system.get('spacing', {}).items():
            lines.append(f"$spacing-{name}: {value};")
        
        lines.append('')
        
        # Border radius
        lines.append('// Border Radius')
        for name, value in design_system.get('radii', {}).items():
            lines.append(f"$radius-{name}: {value};")
        
        lines.append('')
        
        # Shadows
        lines.append('// Shadows')
        for name, value in design_system.get('shadows', {}).items():
            lines.append(f"$shadow-{name}: {value};")
        
        lines.append('')
        
        # Breakpoints
        lines.append('// Breakpoints')
        for name, value in design_system.get('breakpoints', {}).items():
            lines.append(f"$breakpoint-{name}: {value};")
        
        return '\n'.join(lines)
    
    def export_to_tailwind_config(self, design_system: Dict) -> str:
        """Export design system as Tailwind config"""
        config = {
            'theme': {
                'extend': {
                    'colors': {},
                    'fontFamily': {},
                    'fontSize': {},
                    'spacing': {},
                    'borderRadius': {},
                    'boxShadow': {}
                }
            }
        }
        
        # Colors
        colors = design_system.get('colors', {})
        config['theme']['extend']['colors']['primary'] = colors.get('primary', '#2196F3')
        config['theme']['extend']['colors']['secondary'] = colors.get('secondary', '#9C27B0')
        for name, color in colors.get('semantic', {}).items():
            config['theme']['extend']['colors'][name] = color
        
        # Typography
        typography = design_system.get('typography', {})
        for name, font in typography.get('fontFamilies', {}).items():
            config['theme']['extend']['fontFamily'][name] = [font, 'sans-serif']
        config['theme']['extend']['fontSize'] = typography.get('fontSizes', {})
        
        # Spacing
        config['theme']['extend']['spacing'] = design_system.get('spacing', {})
        
        # Border radius
        config['theme']['extend']['borderRadius'] = design_system.get('radii', {})
        
        # Shadows
        config['theme']['extend']['boxShadow'] = design_system.get('shadows', {})
        
        return f"""module.exports = {json.dumps(config, indent=2)}
"""
    
    def export_to_json_tokens(self, design_system: Dict) -> str:
        """Export design system as JSON tokens"""
        return json.dumps(design_system, indent=2)
    
    def export_to_figma_tokens(self, design_system: Dict) -> str:
        """Export design system as Figma Tokens format"""
        tokens = {
            'global': {
                'colors': {},
                'typography': {},
                'spacing': {},
                'radii': {},
                'shadows': {}
            }
        }
        
        # Colors
        colors = design_system.get('colors', {})
        tokens['global']['colors']['primary'] = {
            'value': colors.get('primary', '#2196F3'),
            'type': 'color'
        }
        tokens['global']['colors']['secondary'] = {
            'value': colors.get('secondary', '#9C27B0'),
            'type': 'color'
        }
        for name, color in colors.get('semantic', {}).items():
            tokens['global']['colors'][name] = {
                'value': color,
                'type': 'color'
            }
        
        # Typography
        typography = design_system.get('typography', {})
        for name, font in typography.get('fontFamilies', {}).items():
            tokens['global']['typography'][f'fontFamily-{name}'] = {
                'value': font,
                'type': 'fontFamilies'
            }
        for name, size in typography.get('fontSizes', {}).items():
            tokens['global']['typography'][f'fontSize-{name}'] = {
                'value': size,
                'type': 'fontSizes'
            }
        
        # Spacing
        for name, value in design_system.get('spacing', {}).items():
            tokens['global']['spacing'][name] = {
                'value': value,
                'type': 'spacing'
            }
        
        # Border radius
        for name, value in design_system.get('radii', {}).items():
            tokens['global']['radii'][name] = {
                'value': value,
                'type': 'borderRadius'
            }
        
        # Shadows
        for name, value in design_system.get('shadows', {}).items():
            tokens['global']['shadows'][name] = {
                'value': value,
                'type': 'boxShadow'
            }
        
        return json.dumps(tokens, indent=2)
    
    def export_to_style_dictionary(self, design_system: Dict) -> str:
        """Export design system as Style Dictionary format"""
        tokens = {
            'color': {},
            'font': {},
            'size': {},
            'space': {},
            'radii': {},
            'shadow': {}
        }
        
        # Colors
        colors = design_system.get('colors', {})
        tokens['color']['primary'] = {'value': colors.get('primary', '#2196F3')}
        tokens['color']['secondary'] = {'value': colors.get('secondary', '#9C27B0')}
        for name, color in colors.get('semantic', {}).items():
            tokens['color'][name] = {'value': color}
        
        # Typography
        typography = design_system.get('typography', {})
        for name, font in typography.get('fontFamilies', {}).items():
            tokens['font'][f'family-{name}'] = {'value': font}
        for name, size in typography.get('fontSizes', {}).items():
            tokens['size'][f'font-{name}'] = {'value': size}
        
        # Spacing
        for name, value in design_system.get('spacing', {}).items():
            tokens['space'][name] = {'value': value}
        
        # Border radius
        for name, value in design_system.get('radii', {}).items():
            tokens['radii'][name] = {'value': value}
        
        # Shadows
        for name, value in design_system.get('shadows', {}).items():
            tokens['shadow'][name] = {'value': value}
        
        return json.dumps(tokens, indent=2)

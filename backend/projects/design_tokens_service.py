"""
Design Tokens Service

Service for managing design tokens, exports, and synchronization.
"""
from typing import Dict, Any, List
from django.utils import timezone
import json
import re


class DesignTokensService:
    """
    Service for design token operations.
    """
    
    # CSS value patterns
    COLOR_PATTERN = re.compile(r'^(#[0-9a-fA-F]{3,8}|rgba?\(.+\)|hsla?\(.+\)|[a-z]+)$')
    SIZE_PATTERN = re.compile(r'^-?\d+(\.\d+)?(px|rem|em|%|vw|vh)?$')
    
    def __init__(self, library):
        self.library = library
    
    def get_all_tokens(self, theme=None) -> Dict[str, Any]:
        """
        Get all tokens with optional theme overrides applied.
        """
        tokens = {}
        
        for token in self.library.tokens.all():
            value = token.get_resolved_value()
            
            # Apply theme override if exists
            if theme:
                try:
                    override = token.theme_overrides.get(theme=theme)
                    value = override.value
                except Exception:
                    pass
            
            tokens[token.name] = {
                'value': value,
                'type': token.token_type,
                'category': token.category,
                'css_variable': token.css_variable,
                'deprecated': token.deprecated,
            }
        
        return tokens
    
    def export_to_css(self, theme=None, include_comments=True) -> str:
        """
        Export tokens as CSS custom properties.
        """
        tokens = self.get_all_tokens(theme)
        
        lines = []
        if include_comments:
            lines.append(f"/* {self.library.name} v{self.library.version} */")
            lines.append(f"/* Generated: {timezone.now().isoformat()} */")
            lines.append("")
        
        selector = ":root"
        if theme and theme.css_selector:
            selector = theme.css_selector
        
        lines.append(f"{selector} {{")
        
        # Group by category
        by_category = {}
        for name, data in tokens.items():
            cat = data.get('category', 'other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((name, data))
        
        for category, items in sorted(by_category.items()):
            if include_comments:
                lines.append(f"  /* {category} */")
            for name, data in sorted(items, key=lambda x: x[0]):
                if data['deprecated']:
                    lines.append(f"  /* DEPRECATED: {name} */")
                lines.append(f"  {data['css_variable']}: {data['value']};")
            lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def export_to_scss(self, theme=None) -> str:
        """
        Export tokens as SCSS variables.
        """
        tokens = self.get_all_tokens(theme)
        
        lines = [
            f"// {self.library.name} v{self.library.version}",
            f"// Generated: {timezone.now().isoformat()}",
            "",
        ]
        
        by_category = {}
        for name, data in tokens.items():
            cat = data.get('category', 'other')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((name, data))
        
        for category, items in sorted(by_category.items()):
            lines.append(f"// {category}")
            for name, data in sorted(items, key=lambda x: x[0]):
                scss_var = name.replace('-', '_')
                lines.append(f"${scss_var}: {data['value']};")
            lines.append("")
        
        return "\n".join(lines)
    
    def export_to_json(self, theme=None, nested=True) -> str:
        """
        Export tokens as JSON.
        """
        tokens = self.get_all_tokens(theme)
        
        if not nested:
            return json.dumps(tokens, indent=2)
        
        # Create nested structure
        nested_tokens = {}
        for name, data in tokens.items():
            parts = name.split('-')
            current = nested_tokens
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = data['value']
        
        return json.dumps({
            'name': self.library.name,
            'version': self.library.version,
            'tokens': nested_tokens
        }, indent=2)
    
    def export_to_js(self, theme=None, typescript=False) -> str:
        """
        Export tokens as JavaScript/TypeScript module.
        """
        tokens = self.get_all_tokens(theme)
        
        lines = [
            f"// {self.library.name} v{self.library.version}",
            f"// Generated: {timezone.now().isoformat()}",
            "",
        ]
        
        if typescript:
            lines.append("export interface DesignTokens {")
            for name, data in sorted(tokens.items()):
                prop_name = self._to_camel_case(name)
                lines.append(f"  {prop_name}: string;")
            lines.append("}")
            lines.append("")
        
        lines.append("export const tokens = {")
        for name, data in sorted(tokens.items()):
            prop_name = self._to_camel_case(name)
            lines.append(f"  {prop_name}: '{data['value']}',")
        lines.append("}")
        
        # Also export as CSS variables map
        lines.append("")
        lines.append("export const cssVariables = {")
        for name, data in sorted(tokens.items()):
            prop_name = self._to_camel_case(name)
            lines.append(f"  {prop_name}: '{data['css_variable']}',")
        lines.append("}")
        
        return "\n".join(lines)
    
    def export_to_tailwind(self, theme=None) -> str:
        """
        Export tokens as Tailwind CSS config.
        """
        tokens = self.get_all_tokens(theme)
        
        # Organize tokens by Tailwind categories
        colors = {}
        spacing = {}
        font_sizes = {}
        font_families = {}
        border_radius = {}
        shadows = {}
        
        for name, data in tokens.items():
            value = data['value']
            token_type = data['type']
            
            if token_type == 'color':
                colors[name] = value
            elif token_type in ['spacing', 'sizing']:
                spacing[name] = value
            elif token_type == 'font-size':
                font_sizes[name] = value
            elif token_type == 'font-family':
                font_families[name] = value
            elif token_type == 'border-radius':
                border_radius[name] = value
            elif token_type == 'shadow':
                shadows[name] = value
        
        config = {
            'theme': {
                'extend': {
                    'colors': colors,
                    'spacing': spacing,
                    'fontSize': font_sizes,
                    'fontFamily': font_families,
                    'borderRadius': border_radius,
                    'boxShadow': shadows,
                }
            }
        }
        
        lines = [
            f"// {self.library.name} v{self.library.version}",
            f"// Generated: {timezone.now().isoformat()}",
            "",
            "module.exports = " + json.dumps(config, indent=2),
        ]
        
        return "\n".join(lines)
    
    def export_to_figma(self, theme=None) -> str:
        """
        Export tokens in Figma Tokens format.
        """
        tokens = self.get_all_tokens(theme)
        
        figma_tokens = {}
        
        for name, data in tokens.items():
            parts = name.split('-')
            current = figma_tokens
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = {
                'value': data['value'],
                'type': data['type'],
                'description': '',
            }
        
        return json.dumps({
            'global': figma_tokens,
            '$themes': [],
            '$metadata': {
                'tokenSetOrder': ['global']
            }
        }, indent=2)
    
    def validate_token_value(self, token_type: str, value: str) -> tuple[bool, str]:
        """
        Validate a token value based on its type.
        """
        if token_type == 'color':
            if not self.COLOR_PATTERN.match(value):
                return False, "Invalid color format"
        
        elif token_type in ['spacing', 'sizing', 'font-size', 'border-radius', 'border-width']:
            if not self.SIZE_PATTERN.match(value):
                return False, "Invalid size format"
        
        elif token_type == 'font-weight':
            try:
                weight = int(value)
                if weight < 100 or weight > 900 or weight % 100 != 0:
                    return False, "Font weight must be 100-900 in increments of 100"
            except ValueError:
                if value not in ['normal', 'bold', 'lighter', 'bolder']:
                    return False, "Invalid font weight"
        
        elif token_type == 'opacity':
            try:
                opacity = float(value)
                if opacity < 0 or opacity > 1:
                    return False, "Opacity must be between 0 and 1"
            except ValueError:
                return False, "Invalid opacity value"
        
        elif token_type == 'z-index':
            try:
                int(value)
            except ValueError:
                return False, "Z-index must be an integer"
        
        return True, ""
    
    def sync_to_project(self, project, theme=None) -> Dict[str, Any]:
        """
        Sync tokens to a project, updating component styles.
        """
        from projects.models import DesignComponent
        from .design_tokens_models import ProjectTokenBinding
        
        tokens = self.get_all_tokens(theme)
        
        # Get or create binding
        binding, created = ProjectTokenBinding.objects.get_or_create(
            project=project,
            library=self.library,
            defaults={'theme': theme}
        )
        
        # Find components using tokens
        updated_count = 0
        errors = []
        
        components = DesignComponent.objects.filter(project=project)
        
        for component in components:
            props = component.properties
            changed = False
            
            # Check for token references in properties
            for key, value in props.items():
                if isinstance(value, str) and value.startswith('$'):
                    token_name = value[1:]  # Remove $ prefix
                    if token_name in tokens:
                        # We don't replace the reference, just validate it exists
                        pass
                    else:
                        errors.append(f"Component {component.id}: Unknown token '{token_name}'")
            
            if changed:
                component.save()
                updated_count += 1
        
        # Update binding
        binding.is_synced = len(errors) == 0
        binding.last_synced = timezone.now()
        binding.sync_errors = errors
        binding.save()
        
        return {
            'success': len(errors) == 0,
            'updated_count': updated_count,
            'errors': errors,
            'synced_at': binding.last_synced.isoformat(),
        }
    
    def _to_camel_case(self, name: str) -> str:
        """
        Convert kebab-case to camelCase.
        """
        parts = name.split('-')
        return parts[0] + ''.join(p.title() for p in parts[1:])
    
    def generate_color_palette(
        self,
        base_color: str,
        steps: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate a color palette from a base color.
        """
        # Simple lightness-based palette generation
        # In production, use a proper color library
        palette = []
        
        for i in range(steps):
            step = (i + 1) * 100
            # This is a simplified version
            # Real implementation would calculate proper tints/shades
            palette.append({
                'name': f"color-{step}",
                'value': base_color,  # Would be calculated
            })
        
        return palette
    
    def analyze_token_usage(self, project) -> Dict[str, Any]:
        """
        Analyze how tokens are used in a project.
        """
        from projects.models import DesignComponent
        
        tokens = self.get_all_tokens()
        usage = {name: 0 for name in tokens.keys()}
        unused = []
        
        components = DesignComponent.objects.filter(project=project)
        
        for component in components:
            props_str = json.dumps(component.properties)
            for name in tokens.keys():
                if f"${name}" in props_str or f"var({tokens[name]['css_variable']})" in props_str:
                    usage[name] += 1
        
        for name, count in usage.items():
            if count == 0:
                unused.append(name)
        
        return {
            'total_tokens': len(tokens),
            'used_tokens': len(tokens) - len(unused),
            'unused_tokens': unused,
            'usage_by_token': usage,
        }

"""
Code Export Service
Generate production-ready code from designs
"""
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CodeFile:
    """Represents a generated code file"""
    filename: str
    content: str
    language: str


class CodeExportService:
    """Service for exporting designs to various code formats"""
    
    def export_to_react(self, design_data: Dict, options: Dict = None) -> Dict[str, str]:
        """
        Export design to React components
        
        Args:
            design_data: Design structure
            options: Export options
            
        Returns:
            Dict mapping filename to content
        """
        options = options or {}
        use_typescript = options.get('typescript', False)
        use_styled_components = options.get('styled_components', False)
        
        files = {}
        elements = design_data.get('elements', [])
        
        # Generate main component
        component_name = options.get('component_name', 'Design')
        ext = '.tsx' if use_typescript else '.jsx'
        
        imports = self._generate_react_imports(use_styled_components, use_typescript)
        styles = self._generate_react_styles(elements, use_styled_components)
        jsx = self._generate_react_jsx(elements)
        
        component_code = f"""{imports}

{styles if not use_styled_components else ''}

{'interface Props {}' if use_typescript else ''}

const {component_name}{'= (): JSX.Element' if use_typescript else ' = ()'} => {{
  return (
    <div className="design-container" style={{{self._get_container_style(design_data)}}}>
      {jsx}
    </div>
  );
}};

export default {component_name};
"""
        
        files[f'{component_name}{ext}'] = component_code
        
        # Generate CSS file if not using styled-components
        if not use_styled_components:
            css_content = self._generate_css(elements, design_data)
            files[f'{component_name}.css'] = css_content
        
        # Generate styled-components file
        if use_styled_components:
            styled_content = self._generate_styled_components(elements, design_data)
            files[f'{component_name}.styles{ext}'] = styled_content
        
        return files
    
    def export_to_html_css(self, design_data: Dict, options: Dict = None) -> Dict[str, str]:
        """
        Export design to HTML and CSS
        
        Args:
            design_data: Design structure
            options: Export options
            
        Returns:
            Dict mapping filename to content
        """
        options = options or {}
        elements = design_data.get('elements', [])
        
        # Generate HTML
        html_content = self._generate_html(elements, design_data, options)
        
        # Generate CSS
        css_content = self._generate_css(elements, design_data, options)
        
        return {
            'index.html': html_content,
            'styles.css': css_content
        }
    
    def export_to_tailwind(self, design_data: Dict, options: Dict = None) -> Dict[str, str]:
        """
        Export design to Tailwind CSS
        
        Args:
            design_data: Design structure
            options: Export options
            
        Returns:
            Dict mapping filename to content
        """
        options = options or {}
        elements = design_data.get('elements', [])
        
        # Generate HTML with Tailwind classes
        html_content = self._generate_tailwind_html(elements, design_data)
        
        # Generate tailwind config if custom colors are used
        config_content = self._generate_tailwind_config(design_data)
        
        files = {
            'index.html': html_content,
        }
        
        if config_content:
            files['tailwind.config.js'] = config_content
        
        return files
    
    def export_to_vue(self, design_data: Dict, options: Dict = None) -> Dict[str, str]:
        """
        Export design to Vue.js components
        
        Args:
            design_data: Design structure
            options: Export options
            
        Returns:
            Dict mapping filename to content
        """
        options = options or {}
        elements = design_data.get('elements', [])
        component_name = options.get('component_name', 'Design')
        
        template = self._generate_vue_template(elements)
        styles = self._generate_css(elements, design_data)
        
        vue_content = f"""<template>
  <div class="design-container" :style="containerStyle">
    {template}
  </div>
</template>

<script>
export default {{
  name: '{component_name}',
  data() {{
    return {{
      containerStyle: {self._get_container_style(design_data)}
    }}
  }}
}}
</script>

<style scoped>
{styles}
</style>
"""
        
        return {f'{component_name}.vue': vue_content}
    
    def export_to_scss(self, design_data: Dict, options: Dict = None) -> Dict[str, str]:
        """
        Export design to SCSS
        
        Args:
            design_data: Design structure
            options: Export options
            
        Returns:
            Dict mapping filename to content
        """
        options = options or {}
        elements = design_data.get('elements', [])
        
        # Generate variables
        variables = self._generate_scss_variables(design_data)
        
        # Generate mixins
        mixins = self._generate_scss_mixins()
        
        # Generate styles
        styles = self._generate_scss_styles(elements)
        
        files = {
            '_variables.scss': variables,
            '_mixins.scss': mixins,
            'styles.scss': f"@import 'variables';\n@import 'mixins';\n\n{styles}"
        }
        
        return files
    
    def _generate_react_imports(self, use_styled: bool, use_ts: bool) -> str:
        """Generate React import statements"""
        imports = ["import React from 'react';"]
        if not use_styled:
            imports.append("import './Design.css';")
        if use_styled:
            imports.append("import styled from 'styled-components';")
        return '\n'.join(imports)
    
    def _generate_react_styles(self, elements: List[Dict], use_styled: bool) -> str:
        """Generate inline styles object for React"""
        if use_styled:
            return ""
        return ""
    
    def _generate_react_jsx(self, elements: List[Dict], indent: int = 6) -> str:
        """Generate JSX for elements"""
        lines = []
        spaces = ' ' * indent
        
        for elem in elements:
            elem_type = elem.get('type', 'div')
            elem_id = elem.get('id', '')
            
            # Map element types to JSX
            jsx_tag = self._get_jsx_tag(elem_type)
            style = self._element_to_inline_style(elem)
            
            if elem_type == 'text':
                text = elem.get('text', '')
                lines.append(f'{spaces}<{jsx_tag} style={{{style}}}>{text}</{jsx_tag}>')
            elif elem_type == 'image':
                src = elem.get('src', '')
                alt = elem.get('alt', 'Image')
                lines.append(f'{spaces}<img src="{src}" alt="{alt}" style={{{style}}} />')
            else:
                children = elem.get('children', [])
                if children:
                    lines.append(f'{spaces}<{jsx_tag} style={{{style}}}>')
                    lines.append(self._generate_react_jsx(children, indent + 2))
                    lines.append(f'{spaces}</{jsx_tag}>')
                else:
                    lines.append(f'{spaces}<{jsx_tag} style={{{style}}} />')
        
        return '\n'.join(lines)
    
    def _generate_html(self, elements: List[Dict], design_data: Dict, options: Dict) -> str:
        """Generate HTML document"""
        body_content = self._generate_html_elements(elements)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{options.get('title', 'Design Export')}</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <div class="design-container">
{body_content}
  </div>
</body>
</html>
"""
    
    def _generate_html_elements(self, elements: List[Dict], indent: int = 4) -> str:
        """Generate HTML for elements"""
        lines = []
        spaces = ' ' * indent
        
        for elem in elements:
            elem_type = elem.get('type', 'div')
            elem_id = elem.get('id', '')
            classes = elem.get('classes', [])
            class_str = ' '.join(classes) if classes else elem_type
            
            tag = self._get_html_tag(elem_type)
            
            if elem_type == 'text':
                text = elem.get('text', '')
                lines.append(f'{spaces}<{tag} class="{class_str}" id="{elem_id}">{text}</{tag}>')
            elif elem_type == 'image':
                src = elem.get('src', '')
                alt = elem.get('alt', 'Image')
                lines.append(f'{spaces}<img src="{src}" alt="{alt}" class="{class_str}" id="{elem_id}" />')
            else:
                children = elem.get('children', [])
                if children:
                    lines.append(f'{spaces}<{tag} class="{class_str}" id="{elem_id}">')
                    lines.append(self._generate_html_elements(children, indent + 2))
                    lines.append(f'{spaces}</{tag}>')
                else:
                    lines.append(f'{spaces}<{tag} class="{class_str}" id="{elem_id}"></{tag}>')
        
        return '\n'.join(lines)
    
    def _generate_css(self, elements: List[Dict], design_data: Dict, options: Dict = None) -> str:
        """Generate CSS styles"""
        lines = [
            "/* Generated CSS */",
            "",
            ".design-container {",
            f"  width: {design_data.get('layout', {}).get('width', 1920)}px;",
            f"  height: {design_data.get('layout', {}).get('height', 1080)}px;",
            f"  background-color: {design_data.get('layout', {}).get('backgroundColor', '#FFFFFF')};",
            "  position: relative;",
            "}",
            ""
        ]
        
        for elem in elements:
            elem_css = self._element_to_css(elem)
            lines.append(elem_css)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _element_to_css(self, elem: Dict) -> str:
        """Convert element to CSS rule"""
        elem_id = elem.get('id', 'element')
        elem_type = elem.get('type', 'div')
        
        position = elem.get('position', {})
        size = elem.get('size', {})
        
        rules = [
            f".{elem_type}#{elem_id}, #{elem_id} {{",
            f"  position: absolute;",
            f"  left: {position.get('x', 0)}px;",
            f"  top: {position.get('y', 0)}px;",
            f"  width: {size.get('width', 100)}px;",
            f"  height: {size.get('height', 100)}px;",
        ]
        
        # Add fills as background
        fills = elem.get('fills', [])
        if fills:
            fill = fills[0]
            if fill.get('type') == 'solid':
                rules.append(f"  background-color: {fill.get('color', '#FFFFFF')};")
            elif fill.get('type') in ['gradient_linear', 'linear']:
                stops = fill.get('gradientStops', [])
                if stops:
                    gradient_str = ', '.join([f"{s['color']} {s['position']*100}%" for s in stops])
                    rules.append(f"  background: linear-gradient(to right, {gradient_str});")
        
        # Add strokes as border
        strokes = elem.get('strokes', [])
        if strokes:
            stroke = strokes[0]
            rules.append(f"  border: {stroke.get('width', 1)}px solid {stroke.get('color', '#000000')};")
        
        # Add border radius
        radius = elem.get('borderRadius', 0)
        if radius:
            rules.append(f"  border-radius: {radius}px;")
        
        # Add opacity
        opacity = elem.get('opacity', 1)
        if opacity != 1:
            rules.append(f"  opacity: {opacity};")
        
        # Add rotation
        rotation = elem.get('rotation', 0)
        if rotation:
            rules.append(f"  transform: rotate({rotation}deg);")
        
        # Add text styles
        if elem_type == 'text':
            text_style = elem.get('textStyle', {})
            rules.append(f"  font-family: '{text_style.get('fontFamily', 'Inter')}', sans-serif;")
            rules.append(f"  font-size: {text_style.get('fontSize', 16)}px;")
            rules.append(f"  font-weight: {text_style.get('fontWeight', 400)};")
            rules.append(f"  line-height: {text_style.get('lineHeight', 1.5)};")
            rules.append(f"  text-align: {text_style.get('textAlign', 'left')};")
            if fills:
                rules.append(f"  color: {fills[0].get('color', '#000000')};")
        
        # Add effects
        effects = elem.get('effects', [])
        shadows = []
        for effect in effects:
            if effect.get('type') in ['drop-shadow', 'drop_shadow']:
                x = effect.get('offsetX', 0)
                y = effect.get('offsetY', 0)
                blur = effect.get('blur', 0)
                color = effect.get('color', 'rgba(0,0,0,0.25)')
                shadows.append(f"{x}px {y}px {blur}px {color}")
        if shadows:
            rules.append(f"  box-shadow: {', '.join(shadows)};")
        
        rules.append("}")
        
        return '\n'.join(rules)
    
    def _element_to_inline_style(self, elem: Dict) -> str:
        """Convert element to React inline style object"""
        position = elem.get('position', {})
        size = elem.get('size', {})
        fills = elem.get('fills', [])
        
        style_parts = [
            f"position: 'absolute'",
            f"left: {position.get('x', 0)}",
            f"top: {position.get('y', 0)}",
            f"width: {size.get('width', 100)}",
            f"height: {size.get('height', 100)}",
        ]
        
        if fills:
            fill = fills[0]
            if fill.get('color'):
                if elem.get('type') == 'text':
                    style_parts.append(f"color: '{fill.get('color')}'")
                else:
                    style_parts.append(f"backgroundColor: '{fill.get('color')}'")
        
        return '{' + ', '.join(style_parts) + '}'
    
    def _generate_tailwind_html(self, elements: List[Dict], design_data: Dict) -> str:
        """Generate HTML with Tailwind classes"""
        body = self._generate_tailwind_elements(elements)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Design Export</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
  <div class="relative w-full max-w-screen-xl mx-auto">
{body}
  </div>
</body>
</html>
"""
    
    def _generate_tailwind_elements(self, elements: List[Dict], indent: int = 4) -> str:
        """Generate HTML with Tailwind classes"""
        lines = []
        spaces = ' ' * indent
        
        for elem in elements:
            classes = self._element_to_tailwind_classes(elem)
            tag = self._get_html_tag(elem.get('type', 'div'))
            
            if elem.get('type') == 'text':
                text = elem.get('text', '')
                lines.append(f'{spaces}<{tag} class="{classes}">{text}</{tag}>')
            else:
                children = elem.get('children', [])
                if children:
                    lines.append(f'{spaces}<{tag} class="{classes}">')
                    lines.append(self._generate_tailwind_elements(children, indent + 2))
                    lines.append(f'{spaces}</{tag}>')
                else:
                    lines.append(f'{spaces}<{tag} class="{classes}"></{tag}>')
        
        return '\n'.join(lines)
    
    def _element_to_tailwind_classes(self, elem: Dict) -> str:
        """Convert element to Tailwind classes"""
        classes = ['absolute']
        
        position = elem.get('position', {})
        size = elem.get('size', {})
        
        # Position (using arbitrary values)
        x = position.get('x', 0)
        y = position.get('y', 0)
        classes.append(f'left-[{x}px]')
        classes.append(f'top-[{y}px]')
        
        # Size
        w = size.get('width', 100)
        h = size.get('height', 100)
        classes.append(f'w-[{w}px]')
        classes.append(f'h-[{h}px]')
        
        # Background
        fills = elem.get('fills', [])
        if fills:
            color = fills[0].get('color', '#FFFFFF')
            classes.append(f'bg-[{color}]')
        
        # Border radius
        radius = elem.get('borderRadius', 0)
        if radius:
            if radius >= 9999:
                classes.append('rounded-full')
            else:
                classes.append(f'rounded-[{radius}px]')
        
        # Text styles
        if elem.get('type') == 'text':
            text_style = elem.get('textStyle', {})
            fs = text_style.get('fontSize', 16)
            classes.append(f'text-[{fs}px]')
            
            if fills:
                classes.append(f'text-[{fills[0].get("color", "#000000")}]')
        
        return ' '.join(classes)
    
    def _generate_tailwind_config(self, design_data: Dict) -> str:
        """Generate Tailwind config for custom colors"""
        colors = design_data.get('colorPalette', [])
        if not colors:
            return ""
        
        color_config = {}
        for i, color in enumerate(colors):
            color_config[f'custom-{i}'] = color
        
        return f"""module.exports = {{
  content: ['./**/*.html'],
  theme: {{
    extend: {{
      colors: {json.dumps(color_config, indent=8)}
    }}
  }},
  plugins: []
}}
"""
    
    def _generate_vue_template(self, elements: List[Dict], indent: int = 4) -> str:
        """Generate Vue template"""
        return self._generate_html_elements(elements, indent)
    
    def _generate_scss_variables(self, design_data: Dict) -> str:
        """Generate SCSS variables"""
        lines = ["// Color variables"]
        colors = design_data.get('colorPalette', [])
        for i, color in enumerate(colors):
            lines.append(f"$color-{i}: {color};")
        
        lines.append("\n// Typography variables")
        typography = design_data.get('typography', {})
        lines.append(f"$font-primary: '{typography.get('primaryFont', 'Inter')}', sans-serif;")
        lines.append(f"$font-secondary: '{typography.get('secondaryFont', 'Roboto')}', sans-serif;")
        lines.append(f"$font-size-base: {typography.get('baseFontSize', 16)}px;")
        
        lines.append("\n// Layout variables")
        layout = design_data.get('layout', {})
        lines.append(f"$container-width: {layout.get('width', 1920)}px;")
        lines.append(f"$container-height: {layout.get('height', 1080)}px;")
        
        return '\n'.join(lines)
    
    def _generate_scss_mixins(self) -> str:
        """Generate common SCSS mixins"""
        return """// Responsive breakpoints
@mixin mobile {
  @media (max-width: 767px) {
    @content;
  }
}

@mixin tablet {
  @media (min-width: 768px) and (max-width: 1023px) {
    @content;
  }
}

@mixin desktop {
  @media (min-width: 1024px) {
    @content;
  }
}

// Flexbox utilities
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// Shadow utilities
@mixin shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

@mixin shadow-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

@mixin shadow-lg {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
"""
    
    def _generate_scss_styles(self, elements: List[Dict]) -> str:
        """Generate SCSS styles"""
        lines = [".design-container {", "  position: relative;", "  width: $container-width;", "  height: $container-height;", "}", ""]
        
        for elem in elements:
            lines.append(self._element_to_scss(elem))
            lines.append("")
        
        return '\n'.join(lines)
    
    def _element_to_scss(self, elem: Dict) -> str:
        """Convert element to SCSS"""
        # Similar to CSS but with variables
        return self._element_to_css(elem)
    
    def _generate_styled_components(self, elements: List[Dict], design_data: Dict) -> str:
        """Generate styled-components"""
        lines = ["import styled from 'styled-components';", ""]
        
        lines.append(f"""export const Container = styled.div`
  position: relative;
  width: {design_data.get('layout', {}).get('width', 1920)}px;
  height: {design_data.get('layout', {}).get('height', 1080)}px;
  background-color: {design_data.get('layout', {}).get('backgroundColor', '#FFFFFF')};
`;
""")
        
        for elem in elements:
            styled = self._element_to_styled_component(elem)
            lines.append(styled)
            lines.append("")
        
        return '\n'.join(lines)
    
    def _element_to_styled_component(self, elem: Dict) -> str:
        """Convert element to styled-component"""
        elem_id = elem.get('id', 'Element').replace('-', '_').title()
        position = elem.get('position', {})
        size = elem.get('size', {})
        fills = elem.get('fills', [])
        
        bg_color = fills[0].get('color', '#FFFFFF') if fills else '#FFFFFF'
        
        return f"""export const {elem_id} = styled.div`
  position: absolute;
  left: {position.get('x', 0)}px;
  top: {position.get('y', 0)}px;
  width: {size.get('width', 100)}px;
  height: {size.get('height', 100)}px;
  background-color: {bg_color};
`;"""
    
    def _get_jsx_tag(self, elem_type: str) -> str:
        """Get JSX tag for element type"""
        tag_map = {
            'text': 'p',
            'heading': 'h2',
            'button': 'button',
            'image': 'img',
            'frame': 'div',
            'group': 'div',
            'rectangle': 'div',
            'ellipse': 'div',
            'line': 'hr',
        }
        return tag_map.get(elem_type, 'div')
    
    def _get_html_tag(self, elem_type: str) -> str:
        """Get HTML tag for element type"""
        return self._get_jsx_tag(elem_type)
    
    def _get_container_style(self, design_data: Dict) -> str:
        """Get container style object"""
        layout = design_data.get('layout', {})
        return json.dumps({
            'width': layout.get('width', 1920),
            'height': layout.get('height', 1080),
            'backgroundColor': layout.get('backgroundColor', '#FFFFFF'),
            'position': 'relative'
        })

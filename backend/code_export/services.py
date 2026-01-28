"""
Code Export Services - Generate production-ready code from designs
"""
import json
import re
import zipfile
import io
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from django.core.files.base import ContentFile
from django.utils import timezone


@dataclass
class GeneratedFile:
    """Represents a generated code file"""
    filename: str
    content: str
    language: str
    size: int


class CodeGenerator:
    """Base class for code generation"""
    
    def __init__(self, components: List[Dict], config: Dict):
        self.components = components
        self.config = config
        self.typescript = config.get('typescript_enabled', True)
        self.styling = config.get('styling', 'tailwind')
    
    def generate(self) -> List[GeneratedFile]:
        """Generate code files - override in subclasses"""
        raise NotImplementedError
    
    def sanitize_name(self, name: str, style: str = 'PascalCase') -> str:
        """Convert name to appropriate casing"""
        # Remove special characters
        name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        words = name.split()
        
        if style == 'PascalCase':
            return ''.join(word.capitalize() for word in words)
        elif style == 'camelCase':
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        elif style == 'kebab-case':
            return '-'.join(word.lower() for word in words)
        elif style == 'snake_case':
            return '_'.join(word.lower() for word in words)
        return name
    
    def get_color_value(self, color: str) -> str:
        """Normalize color value"""
        if not color:
            return 'transparent'
        return color
    
    def get_tailwind_color(self, hex_color: str) -> str:
        """Map hex color to Tailwind class (approximate)"""
        color_map = {
            '#000000': 'black',
            '#FFFFFF': 'white',
            '#EF4444': 'red-500',
            '#F97316': 'orange-500',
            '#EAB308': 'yellow-500',
            '#22C55E': 'green-500',
            '#3B82F6': 'blue-500',
            '#6366F1': 'indigo-500',
            '#8B5CF6': 'violet-500',
            '#EC4899': 'pink-500',
            '#6B7280': 'gray-500',
        }
        return color_map.get(hex_color.upper(), f'[{hex_color}]')


class ReactGenerator(CodeGenerator):
    """Generate React components with various styling options"""
    
    def generate(self) -> List[GeneratedFile]:
        files = []
        component_imports = []
        
        for component in self.components:
            generated = self.generate_component(component)
            if generated:
                files.append(generated)
                component_imports.append(generated.filename.replace('.tsx', '').replace('.jsx', ''))
        
        # Generate index file
        files.append(self.generate_index(component_imports))
        
        return files
    
    def generate_component(self, component: Dict) -> Optional[GeneratedFile]:
        """Generate a single React component"""
        props = component.get('properties', {})
        comp_type = component.get('component_type', 'div')
        name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'))
        
        ext = '.tsx' if self.typescript else '.jsx'
        
        if self.styling == 'tailwind':
            content = self._generate_tailwind_component(name, comp_type, props)
        elif self.styling == 'styled_components':
            content = self._generate_styled_component(name, comp_type, props)
        elif self.styling == 'css_modules':
            content = self._generate_css_module_component(name, comp_type, props)
        else:
            content = self._generate_inline_style_component(name, comp_type, props)
        
        return GeneratedFile(
            filename=f"{name}{ext}",
            content=content,
            language='typescript' if self.typescript else 'javascript',
            size=len(content.encode('utf-8'))
        )
    
    def _generate_tailwind_component(self, name: str, comp_type: str, props: Dict) -> str:
        """Generate React component with Tailwind CSS"""
        classes = self._props_to_tailwind(props)
        type_annotation = ": React.FC" if self.typescript else ""
        
        if comp_type == 'text':
            element = 'p'
            content = f'>{props.get("text", "Text")}<'
        elif comp_type == 'button':
            element = 'button'
            content = f'>{props.get("text", "Button")}<'
        elif comp_type == 'image':
            element = 'img'
            content = f' src="{props.get("src", "/placeholder.png")}" alt="{props.get("alt", name)}" /'
        elif comp_type == 'frame':
            element = 'div'
            content = '>{children}<'
        else:
            element = 'div'
            content = '>{children}<'
        
        children_prop = "children?: React.ReactNode;" if 'children' in content else ""
        
        return f'''import React from 'react';

interface {name}Props {{
  className?: string;
  {children_prop}
}}

export const {name}{type_annotation}<{name}Props> = ({{ className = '', {"children" if "children" in content else ""} }}) => {{
  return (
    <{element}
      className={{`{classes} ${{className}}`}}
    {content.replace('{children}', '{{children}}')}
    {element}>
  );
}};

export default {name};
'''
    
    def _generate_styled_component(self, name: str, comp_type: str, props: Dict) -> str:
        """Generate React component with styled-components"""
        styles = self._props_to_css(props)
        
        return f'''import React from 'react';
import styled from 'styled-components';

const Styled{name} = styled.div`
{styles}
`;

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{ className, children }}) => {{
  return (
    <Styled{name} className={{className}}>
      {{children}}
    </Styled{name}>
  );
}};

export default {name};
'''
    
    def _generate_css_module_component(self, name: str, comp_type: str, props: Dict) -> str:
        """Generate React component with CSS Modules"""
        return f'''import React from 'react';
import styles from './{name}.module.css';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{ className, children }}) => {{
  return (
    <div className={{`${{styles.container}} ${{className || ''}}`}}>
      {{children}}
    </div>
  );
}};

export default {name};
'''
    
    def _generate_inline_style_component(self, name: str, comp_type: str, props: Dict) -> str:
        """Generate React component with inline styles"""
        styles = self._props_to_react_style(props)
        
        return f'''import React from 'react';

interface {name}Props {{
  style?: React.CSSProperties;
  children?: React.ReactNode;
}}

export const {name}: React.FC<{name}Props> = ({{ style, children }}) => {{
  const defaultStyle: React.CSSProperties = {styles};
  
  return (
    <div style={{{{ ...defaultStyle, ...style }}}}>
      {{children}}
    </div>
  );
}};

export default {name};
'''
    
    def _props_to_tailwind(self, props: Dict) -> str:
        """Convert component properties to Tailwind classes"""
        classes = []
        
        # Size
        size = props.get('size', {})
        if size.get('width'):
            classes.append(f"w-[{size['width']}px]")
        if size.get('height'):
            classes.append(f"h-[{size['height']}px]")
        
        # Position/Layout
        position = props.get('position', {})
        if props.get('layout') == 'flex':
            classes.extend(['flex', 'items-center', 'justify-center'])
        
        # Colors
        if props.get('backgroundColor'):
            color = self.get_tailwind_color(props['backgroundColor'])
            classes.append(f"bg-{color}")
        if props.get('color'):
            color = self.get_tailwind_color(props['color'])
            classes.append(f"text-{color}")
        
        # Typography
        if props.get('fontSize'):
            classes.append(f"text-[{props['fontSize']}px]")
        if props.get('fontWeight'):
            weight_map = {'normal': 'font-normal', 'bold': 'font-bold', '500': 'font-medium', '600': 'font-semibold'}
            classes.append(weight_map.get(str(props['fontWeight']), 'font-normal'))
        
        # Spacing
        padding = props.get('padding', {})
        if isinstance(padding, dict):
            if padding.get('all'):
                classes.append(f"p-[{padding['all']}px]")
            else:
                if padding.get('top'):
                    classes.append(f"pt-[{padding['top']}px]")
                if padding.get('right'):
                    classes.append(f"pr-[{padding['right']}px]")
                if padding.get('bottom'):
                    classes.append(f"pb-[{padding['bottom']}px]")
                if padding.get('left'):
                    classes.append(f"pl-[{padding['left']}px]")
        elif padding:
            classes.append(f"p-[{padding}px]")
        
        # Border
        if props.get('borderRadius'):
            classes.append(f"rounded-[{props['borderRadius']}px]")
        if props.get('borderWidth'):
            classes.append(f"border-[{props['borderWidth']}px]")
        if props.get('borderColor'):
            color = self.get_tailwind_color(props['borderColor'])
            classes.append(f"border-{color}")
        
        # Effects
        if props.get('opacity') is not None and props['opacity'] < 1:
            classes.append(f"opacity-[{props['opacity']}]")
        if props.get('shadow'):
            classes.append('shadow-lg')
        
        return ' '.join(classes)
    
    def _props_to_css(self, props: Dict) -> str:
        """Convert component properties to CSS"""
        css_rules = []
        
        size = props.get('size', {})
        if size.get('width'):
            css_rules.append(f"  width: {size['width']}px;")
        if size.get('height'):
            css_rules.append(f"  height: {size['height']}px;")
        
        if props.get('backgroundColor'):
            css_rules.append(f"  background-color: {props['backgroundColor']};")
        if props.get('color'):
            css_rules.append(f"  color: {props['color']};")
        
        if props.get('fontSize'):
            css_rules.append(f"  font-size: {props['fontSize']}px;")
        if props.get('fontFamily'):
            css_rules.append(f"  font-family: {props['fontFamily']};")
        
        if props.get('borderRadius'):
            css_rules.append(f"  border-radius: {props['borderRadius']}px;")
        
        padding = props.get('padding', {})
        if isinstance(padding, dict) and padding.get('all'):
            css_rules.append(f"  padding: {padding['all']}px;")
        elif padding:
            css_rules.append(f"  padding: {padding}px;")
        
        return '\n'.join(css_rules)
    
    def _props_to_react_style(self, props: Dict) -> str:
        """Convert properties to React inline style object"""
        styles = {}
        
        size = props.get('size', {})
        if size.get('width'):
            styles['width'] = size['width']
        if size.get('height'):
            styles['height'] = size['height']
        
        if props.get('backgroundColor'):
            styles['backgroundColor'] = props['backgroundColor']
        if props.get('color'):
            styles['color'] = props['color']
        
        if props.get('fontSize'):
            styles['fontSize'] = props['fontSize']
        if props.get('fontFamily'):
            styles['fontFamily'] = props['fontFamily']
        
        if props.get('borderRadius'):
            styles['borderRadius'] = props['borderRadius']
        
        return json.dumps(styles, indent=2)
    
    def generate_index(self, components: List[str]) -> GeneratedFile:
        """Generate index.ts with all exports"""
        exports = [f"export {{ default as {c}, {c} }} from './{c}';" for c in components]
        content = '\n'.join(exports)
        
        ext = '.ts' if self.typescript else '.js'
        return GeneratedFile(
            filename=f"index{ext}",
            content=content,
            language='typescript' if self.typescript else 'javascript',
            size=len(content.encode('utf-8'))
        )


class VueGenerator(CodeGenerator):
    """Generate Vue.js components"""
    
    def generate(self) -> List[GeneratedFile]:
        files = []
        
        for component in self.components:
            generated = self.generate_component(component)
            if generated:
                files.append(generated)
        
        return files
    
    def generate_component(self, component: Dict) -> Optional[GeneratedFile]:
        """Generate a single Vue component"""
        props = component.get('properties', {})
        name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'))
        
        styles = self._props_to_css(props)
        
        content = f'''<template>
  <div :class="['component-{name.lower()}', className]" :style="customStyle">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {{
  className?: string;
  customStyle?: Record<string, string>;
}}

withDefaults(defineProps<Props>(), {{
  className: '',
  customStyle: () => ({{}}),
}});
</script>

<style scoped>
.component-{name.lower()} {{
{styles}
}}
</style>
'''
        
        return GeneratedFile(
            filename=f"{name}.vue",
            content=content,
            language='vue',
            size=len(content.encode('utf-8'))
        )
    
    def _props_to_css(self, props: Dict) -> str:
        """Convert properties to CSS"""
        css_rules = []
        
        size = props.get('size', {})
        if size.get('width'):
            css_rules.append(f"  width: {size['width']}px;")
        if size.get('height'):
            css_rules.append(f"  height: {size['height']}px;")
        
        if props.get('backgroundColor'):
            css_rules.append(f"  background-color: {props['backgroundColor']};")
        if props.get('color'):
            css_rules.append(f"  color: {props['color']};")
        
        if props.get('borderRadius'):
            css_rules.append(f"  border-radius: {props['borderRadius']}px;")
        
        return '\n'.join(css_rules)


class AngularGenerator(CodeGenerator):
    """Generate Angular components"""
    
    def generate(self) -> List[GeneratedFile]:
        files = []
        
        for component in self.components:
            generated_files = self.generate_component(component)
            files.extend(generated_files)
        
        # Generate module file
        files.append(self.generate_module())
        
        return files
    
    def generate_component(self, component: Dict) -> List[GeneratedFile]:
        """Generate Angular component files (ts, html, scss)"""
        props = component.get('properties', {})
        name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'))
        kebab_name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'), 'kebab-case')
        
        # TypeScript file
        ts_content = f'''import {{ Component, Input }} from '@angular/core';

@Component({{
  selector: 'app-{kebab_name}',
  templateUrl: './{kebab_name}.component.html',
  styleUrls: ['./{kebab_name}.component.scss']
}})
export class {name}Component {{
  @Input() customClass = '';
  @Input() customStyle: Record<string, string> = {{}};
}}
'''
        
        # HTML template
        html_content = f'''<div
  class="{kebab_name}-container"
  [ngClass]="customClass"
  [ngStyle]="customStyle"
>
  <ng-content></ng-content>
</div>
'''
        
        # SCSS file
        scss_content = self._props_to_scss(props, kebab_name)
        
        return [
            GeneratedFile(f"{kebab_name}.component.ts", ts_content, 'typescript', len(ts_content.encode('utf-8'))),
            GeneratedFile(f"{kebab_name}.component.html", html_content, 'html', len(html_content.encode('utf-8'))),
            GeneratedFile(f"{kebab_name}.component.scss", scss_content, 'scss', len(scss_content.encode('utf-8'))),
        ]
    
    def _props_to_scss(self, props: Dict, class_name: str) -> str:
        """Convert properties to SCSS"""
        rules = []
        
        size = props.get('size', {})
        if size.get('width'):
            rules.append(f"  width: {size['width']}px;")
        if size.get('height'):
            rules.append(f"  height: {size['height']}px;")
        
        if props.get('backgroundColor'):
            rules.append(f"  background-color: {props['backgroundColor']};")
        if props.get('color'):
            rules.append(f"  color: {props['color']};")
        
        if props.get('borderRadius'):
            rules.append(f"  border-radius: {props['borderRadius']}px;")
        
        return f".{class_name}-container {{\n" + '\n'.join(rules) + "\n}"
    
    def generate_module(self) -> GeneratedFile:
        """Generate Angular module file"""
        content = '''import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

// Import all generated components here

@NgModule({
  declarations: [
    // Add all component classes here
  ],
  imports: [
    CommonModule
  ],
  exports: [
    // Export all components
  ]
})
export class GeneratedComponentsModule { }
'''
        return GeneratedFile('generated-components.module.ts', content, 'typescript', len(content.encode('utf-8')))


class SwiftUIGenerator(CodeGenerator):
    """Generate SwiftUI views for iOS"""
    
    def generate(self) -> List[GeneratedFile]:
        files = []
        
        for component in self.components:
            generated = self.generate_component(component)
            if generated:
                files.append(generated)
        
        return files
    
    def generate_component(self, component: Dict) -> Optional[GeneratedFile]:
        """Generate SwiftUI view"""
        props = component.get('properties', {})
        comp_type = component.get('component_type', 'div')
        name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'))
        
        view_content = self._generate_view_body(comp_type, props)
        
        content = f'''import SwiftUI

struct {name}View: View {{
    // MARK: - Properties
    var text: String = "{props.get('text', '')}"
    
    // MARK: - Body
    var body: some View {{
{view_content}
    }}
}}

// MARK: - Preview
struct {name}View_Previews: PreviewProvider {{
    static var previews: some View {{
        {name}View()
    }}
}}
'''
        
        return GeneratedFile(
            filename=f"{name}View.swift",
            content=content,
            language='swift',
            size=len(content.encode('utf-8'))
        )
    
    def _generate_view_body(self, comp_type: str, props: Dict) -> str:
        """Generate SwiftUI view body"""
        size = props.get('size', {})
        modifiers = []
        
        if comp_type == 'text':
            base = f'        Text("{props.get("text", "Hello")}")'
            if props.get('fontSize'):
                modifiers.append(f'            .font(.system(size: {props["fontSize"]}))')
            if props.get('fontWeight') == 'bold':
                modifiers.append('            .fontWeight(.bold)')
        elif comp_type == 'button':
            base = f'''        Button(action: {{}}) {{
            Text("{props.get("text", "Button")}")
        }}'''
        elif comp_type == 'image':
            base = f'        Image("{props.get("src", "placeholder")}")'
            modifiers.append('            .resizable()')
            modifiers.append('            .aspectRatio(contentMode: .fit)')
        else:
            base = '        VStack {'
            modifiers.append('            // Add content here')
            modifiers.append('        }')
        
        # Common modifiers
        if size.get('width') or size.get('height'):
            w = size.get('width', 0)
            h = size.get('height', 0)
            modifiers.append(f'            .frame(width: {w}, height: {h})')
        
        if props.get('backgroundColor'):
            color = self._hex_to_swift_color(props['backgroundColor'])
            modifiers.append(f'            .background({color})')
        
        if props.get('borderRadius'):
            modifiers.append(f'            .cornerRadius({props["borderRadius"]})')
        
        if props.get('padding'):
            modifiers.append(f'            .padding({props["padding"]})')
        
        return base + '\n' + '\n'.join(modifiers) if modifiers else base
    
    def _hex_to_swift_color(self, hex_color: str) -> str:
        """Convert hex color to SwiftUI Color"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return f'Color(red: {r:.3f}, green: {g:.3f}, blue: {b:.3f})'


class JetpackComposeGenerator(CodeGenerator):
    """Generate Jetpack Compose composables for Android"""
    
    def generate(self) -> List[GeneratedFile]:
        files = []
        
        for component in self.components:
            generated = self.generate_component(component)
            if generated:
                files.append(generated)
        
        return files
    
    def generate_component(self, component: Dict) -> Optional[GeneratedFile]:
        """Generate Jetpack Compose composable"""
        props = component.get('properties', {})
        comp_type = component.get('component_type', 'div')
        name = self.sanitize_name(props.get('name', f'Component{component.get("id", "")}'))
        
        compose_content = self._generate_composable_body(comp_type, props)
        
        content = f'''package com.example.generated.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun {name}(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit = {{}}
) {{
{compose_content}
}}

@Preview(showBackground = true)
@Composable
fun {name}Preview() {{
    {name}()
}}
'''
        
        return GeneratedFile(
            filename=f"{name}.kt",
            content=content,
            language='kotlin',
            size=len(content.encode('utf-8'))
        )
    
    def _generate_composable_body(self, comp_type: str, props: Dict) -> str:
        """Generate Jetpack Compose composable body"""
        size = props.get('size', {})
        modifiers = ['modifier']
        
        if size.get('width') and size.get('height'):
            modifiers.append(f'.size({size["width"]}.dp, {size["height"]}.dp)')
        elif size.get('width'):
            modifiers.append(f'.width({size["width"]}.dp)')
        elif size.get('height'):
            modifiers.append(f'.height({size["height"]}.dp)')
        
        if props.get('backgroundColor'):
            color = self._hex_to_compose_color(props['backgroundColor'])
            modifiers.append(f'.background({color})')
        
        if props.get('borderRadius'):
            modifiers.append(f'.clip(RoundedCornerShape({props["borderRadius"]}.dp))')
        
        if props.get('padding'):
            modifiers.append(f'.padding({props["padding"]}.dp)')
        
        modifier_chain = '\n            '.join(modifiers)
        
        if comp_type == 'text':
            return f'''    Text(
        text = "{props.get('text', 'Hello')}",
        fontSize = {props.get('fontSize', 16)}.sp,
        modifier = {modifier_chain}
    )'''
        elif comp_type == 'button':
            return f'''    Button(
        onClick = {{ }},
        modifier = {modifier_chain}
    ) {{
        Text("{props.get('text', 'Button')}")
    }}'''
        else:
            return f'''    Box(
        modifier = {modifier_chain},
        contentAlignment = Alignment.Center
    ) {{
        content()
    }}'''
    
    def _hex_to_compose_color(self, hex_color: str) -> str:
        """Convert hex color to Compose Color"""
        return f'Color(0xFF{hex_color.lstrip("#")})'


class CodeExportService:
    """Main service for handling code exports"""
    
    GENERATORS = {
        'react': ReactGenerator,
        'vue': VueGenerator,
        'angular': AngularGenerator,
        'swiftui': SwiftUIGenerator,
        'jetpack_compose': JetpackComposeGenerator,
    }
    
    def __init__(self, project, config: Dict):
        self.project = project
        self.config = config
    
    def generate_code(self) -> Dict[str, Any]:
        """Generate code for all components in the project"""
        framework = self.config.get('framework', 'react')
        components = list(self.project.components.all().values('id', 'component_type', 'properties'))
        
        generator_class = self.GENERATORS.get(framework, ReactGenerator)
        generator = generator_class(components, self.config)
        
        files = generator.generate()
        
        result = {
            'files': {f.filename: f.content for f in files},
            'file_count': len(files),
            'total_lines': sum(f.content.count('\n') + 1 for f in files),
            'total_size': sum(f.size for f in files),
        }
        
        return result
    
    def create_zip(self, files: Dict[str, str]) -> bytes:
        """Create a ZIP file from generated code"""
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
        
        buffer.seek(0)
        return buffer.read()
    
    def generate_design_specs(self) -> List[Dict]:
        """Generate design specifications for developer handoff"""
        specs = []
        
        for component in self.project.components.all():
            props = component.properties
            
            spec = {
                'id': component.id,
                'name': props.get('name', f'{component.component_type}_{component.id}'),
                'type': component.component_type,
                'dimensions': {
                    'width': props.get('size', {}).get('width'),
                    'height': props.get('size', {}).get('height'),
                },
                'position': props.get('position', {}),
                'colors': {
                    'background': props.get('backgroundColor'),
                    'text': props.get('color'),
                    'border': props.get('borderColor'),
                },
                'typography': {
                    'fontFamily': props.get('fontFamily'),
                    'fontSize': props.get('fontSize'),
                    'fontWeight': props.get('fontWeight'),
                    'lineHeight': props.get('lineHeight'),
                    'letterSpacing': props.get('letterSpacing'),
                },
                'spacing': {
                    'padding': props.get('padding'),
                    'margin': props.get('margin'),
                },
                'effects': {
                    'opacity': props.get('opacity'),
                    'borderRadius': props.get('borderRadius'),
                    'shadow': props.get('shadow'),
                    'blur': props.get('blur'),
                },
                'css': self._generate_css_for_component(props),
            }
            
            specs.append(spec)
        
        return specs
    
    def _generate_css_for_component(self, props: Dict) -> str:
        """Generate CSS for a component"""
        css_rules = []
        
        size = props.get('size', {})
        if size.get('width'):
            css_rules.append(f"width: {size['width']}px;")
        if size.get('height'):
            css_rules.append(f"height: {size['height']}px;")
        
        if props.get('backgroundColor'):
            css_rules.append(f"background-color: {props['backgroundColor']};")
        if props.get('color'):
            css_rules.append(f"color: {props['color']};")
        
        if props.get('fontSize'):
            css_rules.append(f"font-size: {props['fontSize']}px;")
        if props.get('fontFamily'):
            css_rules.append(f"font-family: {props['fontFamily']};")
        if props.get('fontWeight'):
            css_rules.append(f"font-weight: {props['fontWeight']};")
        if props.get('lineHeight'):
            css_rules.append(f"line-height: {props['lineHeight']};")
        
        if props.get('borderRadius'):
            css_rules.append(f"border-radius: {props['borderRadius']}px;")
        
        padding = props.get('padding')
        if isinstance(padding, dict):
            p = padding
            css_rules.append(f"padding: {p.get('top', 0)}px {p.get('right', 0)}px {p.get('bottom', 0)}px {p.get('left', 0)}px;")
        elif padding:
            css_rules.append(f"padding: {padding}px;")
        
        if props.get('opacity') is not None:
            css_rules.append(f"opacity: {props['opacity']};")
        
        shadow = props.get('shadow')
        if shadow:
            css_rules.append(f"box-shadow: {shadow.get('x', 0)}px {shadow.get('y', 2)}px {shadow.get('blur', 4)}px {shadow.get('color', 'rgba(0,0,0,0.1)')};")
        
        return '\n'.join(css_rules)

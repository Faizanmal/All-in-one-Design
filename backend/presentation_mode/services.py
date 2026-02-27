"""
Services for Presentation Mode app.
"""
from typing import Dict, Any, List, Optional
from django.db import transaction
import uuid

from .models import (
    Presentation, PresentationSlide, SlideAnnotation,
    DevModeProject, DevModeInspection, CodeExportConfig, CodeExportHistory,
    AssetExportQueue
)


class PresentationService:
    """
    Service for presentation operations.
    """
    
    def __init__(self, presentation: Presentation):
        self.presentation = presentation
    
    def duplicate(self, user) -> Presentation:
        """Duplicate the presentation."""
        with transaction.atomic():
            new_presentation = Presentation.objects.create(
                project=self.presentation.project,
                name=f"{self.presentation.name} (copy)",
                description=self.presentation.description,
                default_transition=self.presentation.default_transition,
                default_transition_duration=self.presentation.default_transition_duration,
                show_navigation=self.presentation.show_navigation,
                show_progress=self.presentation.show_progress,
                loop=self.presentation.loop,
                auto_play=self.presentation.auto_play,
                auto_play_interval=self.presentation.auto_play_interval,
                background_color=self.presentation.background_color,
                cursor_style=self.presentation.cursor_style,
                hotspot_style=self.presentation.hotspot_style,
                share_link=str(uuid.uuid4())[:8],
                created_by=user,
            )
            
            # Duplicate slides
            for slide in self.presentation.slides.order_by('order'):
                new_slide = PresentationSlide.objects.create(
                    presentation=new_presentation,
                    frame_id=slide.frame_id,
                    title=slide.title,
                    notes=slide.notes,
                    transition=slide.transition,
                    transition_duration=slide.transition_duration,
                    auto_advance=slide.auto_advance,
                    advance_delay=slide.advance_delay,
                    order=slide.order,
                )
                
                # Duplicate annotations
                for annotation in slide.annotations.all():
                    SlideAnnotation.objects.create(
                        slide=new_slide,
                        annotation_type=annotation.annotation_type,
                        content=annotation.content,
                        position_x=annotation.position_x,
                        position_y=annotation.position_y,
                        width=annotation.width,
                        height=annotation.height,
                        style=annotation.style,
                        is_visible=annotation.is_visible,
                        order=annotation.order,
                        created_by=user,
                    )
            
            return new_presentation


class CodeGenerator:
    """
    Service for generating code from design nodes.
    """
    
    def __init__(self, dev_mode_project: DevModeProject):
        self.dev_mode = dev_mode_project
    
    def inspect_node(
        self,
        node_id: str,
        formats: List[str],
        user,
    ) -> DevModeInspection:
        """Inspect a node and generate code in multiple formats."""
        # Get node data from project
        node = self._get_node(node_id)
        
        inspection = DevModeInspection.objects.create(
            dev_mode_project=self.dev_mode,
            node_id=node_id,
            node_type=node.get('type', 'unknown'),
            node_name=node.get('name', 'Unknown'),
            properties=self._extract_properties(node),
            computed_styles=self._compute_styles(node),
            inspected_by=user,
        )
        
        # Generate code for each format
        if 'css' in formats:
            inspection.css_code = self._generate_css(node)
        if 'tailwind' in formats:
            inspection.tailwind_code = self._generate_tailwind(node)
        if 'react' in formats:
            inspection.react_code = self._generate_react(node)
        if 'vue' in formats:
            inspection.vue_code = self._generate_vue(node)
        if 'flutter' in formats:
            inspection.flutter_code = self._generate_flutter(node)
        if 'swift' in formats:
            inspection.swift_code = self._generate_swift(node)
        
        inspection.save()
        return inspection
    
    def export_code(
        self,
        node_ids: List[str],
        format: str,
        config_id: Optional[str],
        user,
    ) -> CodeExportHistory:
        """Export code for multiple nodes."""
        # Get config
        if config_id:
            config = CodeExportConfig.objects.get(id=config_id)
        else:
            config = self.dev_mode.configs.filter(is_default=True).first()
            if not config:
                config = self.dev_mode.configs.first()
        
        if not config:
            # Create default config
            config = CodeExportConfig.objects.create(
                dev_mode_project=self.dev_mode,
                name='Default',
                format='css',
                is_default=True,
            )
        
        # Generate code
        generated_code = self._generate_code_batch(node_ids, format, config)
        
        export = CodeExportHistory.objects.create(
            config=config,
            node_ids=node_ids,
            export_format=format,
            generated_code=generated_code,
            exported_by=user,
        )
        
        return export
    
    def _get_node(self, node_id: str) -> Dict:
        """Get node data from project."""
        # In production, fetch from project data
        return {
            'id': node_id,
            'type': 'frame',
            'name': 'Component',
            'width': 100,
            'height': 100,
        }
    
    def _extract_properties(self, node: Dict) -> Dict:
        """Extract design properties from node."""
        return {
            'width': node.get('width'),
            'height': node.get('height'),
            'x': node.get('x'),
            'y': node.get('y'),
            'fills': node.get('fills', []),
            'strokes': node.get('strokes', []),
            'effects': node.get('effects', []),
            'cornerRadius': node.get('cornerRadius'),
        }
    
    def _compute_styles(self, node: Dict) -> Dict:
        """Compute CSS-like styles from node."""
        styles = {}
        
        if node.get('width'):
            styles['width'] = f"{node['width']}px"
        if node.get('height'):
            styles['height'] = f"{node['height']}px"
        
        fills = node.get('fills', [])
        if fills:
            first_fill = fills[0]
            if first_fill.get('type') == 'SOLID':
                color = first_fill.get('color', {})
                styles['background-color'] = self._color_to_css(color)
        
        if node.get('cornerRadius'):
            styles['border-radius'] = f"{node['cornerRadius']}px"
        
        return styles
    
    def _color_to_css(self, color: Dict) -> str:
        """Convert color object to CSS."""
        r = int(color.get('r', 0) * 255)
        g = int(color.get('g', 0) * 255)
        b = int(color.get('b', 0) * 255)
        a = color.get('a', 1)
        
        if a < 1:
            return f"rgba({r}, {g}, {b}, {a})"
        return f"rgb({r}, {g}, {b})"
    
    def _generate_css(self, node: Dict) -> str:
        """Generate CSS code."""
        styles = self._compute_styles(node)
        name = node.get('name', 'element').lower().replace(' ', '-')
        
        css_rules = '\n'.join(f"  {prop}: {value};" for prop, value in styles.items())
        return f".{name} {{\n{css_rules}\n}}"
    
    def _generate_tailwind(self, node: Dict) -> str:
        """Generate Tailwind CSS classes."""
        classes = []
        
        width = node.get('width')
        if width:
            if width % 4 == 0:
                classes.append(f"w-{width // 4}")
            else:
                classes.append(f"w-[{width}px]")
        
        height = node.get('height')
        if height:
            if height % 4 == 0:
                classes.append(f"h-{height // 4}")
            else:
                classes.append(f"h-[{height}px]")
        
        radius = node.get('cornerRadius')
        if radius:
            if radius == 9999:
                classes.append('rounded-full')
            elif radius <= 4:
                classes.append('rounded-sm')
            elif radius <= 8:
                classes.append('rounded')
            else:
                classes.append(f'rounded-[{radius}px]')
        
        return ' '.join(classes)
    
    def _generate_react(self, node: Dict) -> str:
        """Generate React component code."""
        name = ''.join(word.capitalize() for word in node.get('name', 'Component').split())
        tailwind = self._generate_tailwind(node)
        
        return f'''import React from 'react';

const {name}: React.FC = () => {{
  return (
    <div className="{tailwind}">
      {{/* Content */}}
    </div>
  );
}};

export default {name};'''
    
    def _generate_vue(self, node: Dict) -> str:
        """Generate Vue component code."""
        name = ''.join(word.capitalize() for word in node.get('name', 'Component').split())
        tailwind = self._generate_tailwind(node)
        
        return f'''<template>
  <div class="{tailwind}">
    <!-- Content -->
  </div>
</template>

<script setup lang="ts">
// {name} component
</script>'''
    
    def _generate_flutter(self, node: Dict) -> str:
        """Generate Flutter widget code."""
        name = ''.join(word.capitalize() for word in node.get('name', 'Component').split())
        width = node.get('width', 100)
        height = node.get('height', 100)
        radius = node.get('cornerRadius', 0)
        
        return f'''class {name} extends StatelessWidget {{
  const {name}({{super.key}});

  @override
  Widget build(BuildContext context) {{
    return Container(
      width: {width},
      height: {height},
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular({radius}),
      ),
      child: const Placeholder(),
    );
  }}
}}'''
    
    def _generate_swift(self, node: Dict) -> str:
        """Generate SwiftUI code."""
        name = ''.join(word.capitalize() for word in node.get('name', 'Component').split())
        width = node.get('width', 100)
        height = node.get('height', 100)
        radius = node.get('cornerRadius', 0)
        
        return f'''struct {name}: View {{
    var body: some View {{
        RoundedRectangle(cornerRadius: {radius})
            .frame(width: {width}, height: {height})
    }}
}}'''
    
    def _generate_code_batch(
        self,
        node_ids: List[str],
        format: str,
        config: CodeExportConfig
    ) -> str:
        """Generate code for multiple nodes."""
        code_parts = []
        
        for node_id in node_ids:
            node = self._get_node(node_id)
            
            if format == 'css':
                code_parts.append(self._generate_css(node))
            elif format == 'tailwind':
                code_parts.append(f"/* {node.get('name', node_id)} */\n{self._generate_tailwind(node)}")
            elif format == 'react':
                code_parts.append(self._generate_react(node))
            elif format == 'vue':
                code_parts.append(self._generate_vue(node))
            elif format == 'flutter':
                code_parts.append(self._generate_flutter(node))
            elif format == 'swift':
                code_parts.append(self._generate_swift(node))
        
        return '\n\n'.join(code_parts)


class AssetExporter:
    """
    Service for exporting design assets.
    """
    
    def __init__(self, dev_mode_project: DevModeProject):
        self.dev_mode = dev_mode_project
    
    def queue_exports(
        self,
        node_ids: List[str],
        format: str,
        scales: List[float],
        user,
    ) -> List[AssetExportQueue]:
        """Queue asset exports for processing."""
        exports = []
        
        for node_id in node_ids:
            node_name = self._get_node_name(node_id)
            
            for scale in scales:
                suffix = f"@{scale}x" if scale != 1.0 else ""
                
                export = AssetExportQueue.objects.create(
                    dev_mode_project=self.dev_mode,
                    node_id=node_id,
                    node_name=node_name,
                    format=format,
                    scale=scale,
                    suffix=suffix,
                    status='pending',
                    requested_by=user,
                )
                exports.append(export)
                
                # Queue async task
                from .tasks import export_asset_task
                export_asset_task.delay(str(export.id))
        
        return exports
    
    def _get_node_name(self, node_id: str) -> str:
        """Get node name for export."""
        # In production, fetch from project
        return f"asset_{node_id[:8]}"


class AssetExportService:
    """Service for exporting presentation assets"""
    
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'svg', 'pdf']
    
    def export_presentation_assets(
        self, 
        presentation_id: str, 
        export_format: str = 'png',
        scale: float = 1.0,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export presentation assets
        
        Args:
            presentation_id: ID of the presentation
            export_format: Export format (png, jpg, svg, pdf)
            scale: Scale factor for export
            options: Additional export options
        
        Returns:
            Dict containing export results
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # Validate format
            if export_format.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {export_format}")
            
            # Get presentation data
            presentation_data = self._get_presentation_data(presentation_id)
            
            # Export based on format
            if export_format.lower() in ['png', 'jpg', 'jpeg']:
                return self._export_raster(presentation_data, export_format, scale, options or {})
            elif export_format.lower() == 'svg':
                return self._export_svg(presentation_data, options or {})
            elif export_format.lower() == 'pdf':
                return self._export_pdf(presentation_data, options or {})
            
        except Exception as e:
            logger.error(f"Asset export failed: {e}")
            raise
    
    def _get_presentation_data(self, presentation_id: str) -> Dict[str, Any]:
        """Get presentation data from database"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            presentation = Presentation.objects.get(id=presentation_id)
            return {
                'id': presentation.id,
                'title': presentation.title,
                'slides': presentation.slides or [],
                'settings': presentation.settings or {},
                'width': 1920,
                'height': 1080,
            }
        except Exception as e:
            logger.error(f"Failed to get presentation data: {e}")
            # Return dummy data for now
            return {
                'id': presentation_id,
                'title': 'Untitled Presentation',
                'slides': [],
                'settings': {},
                'width': 1920,
                'height': 1080,
            }
    
    def _export_raster(
        self, 
        presentation_data: Dict[str, Any], 
        format: str, 
        scale: float,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Export as raster image (PNG/JPG)"""
        from PIL import Image, ImageDraw, ImageFont
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import io
        import uuid
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            width = int(1920 * scale)
            height = int(1080 * scale)
            
            # Create image
            if format.lower() == 'png':
                img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            else:
                img = Image.new('RGB', (width, height), (255, 255, 255))
            
            draw = ImageDraw.Draw(img)
            
            # Add presentation title as placeholder
            try:
                font = ImageFont.load_default()
                title = presentation_data.get('title', 'Untitled')
                text_bbox = draw.textbbox((0, 0), title, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                draw.text((x, y), title, fill=(0, 0, 0), font=font)
            except Exception as e:
                logger.warning(f"Failed to add text: {e}")
            
            # Save to storage
            img_io = io.BytesIO()
            img.save(img_io, format=format.upper(), quality=95 if format.lower() == 'jpg' else None)
            img_io.seek(0)
            
            # Generate filename and save
            filename = f"presentations/{uuid.uuid4()}.{format.lower()}"
            file_path = default_storage.save(filename, ContentFile(img_io.getvalue()))
            file_url = default_storage.url(file_path)
            
            return {
                'file_url': file_url,
                'file_path': file_path,
                'format': format,
                'width': width,
                'height': height,
                'size_bytes': len(img_io.getvalue())
            }
            
        except Exception as e:
            logger.error(f"Raster export failed: {e}")
            raise
    
    def _export_svg(self, presentation_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export as SVG"""
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import uuid
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            width = presentation_data.get('width', 1920)
            height = presentation_data.get('height', 1080)
            title = presentation_data.get('title', 'Untitled')
            
            # Generate SVG content
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width//2}" y="{height//2}" text-anchor="middle" font-family="Arial" font-size="24" fill="black">
    {title}
  </text>
</svg>'''
            
            # Save to storage
            filename = f"presentations/{uuid.uuid4()}.svg"
            file_path = default_storage.save(filename, ContentFile(svg_content.encode('utf-8')))
            file_url = default_storage.url(file_path)
            
            return {
                'file_url': file_url,
                'file_path': file_path,
                'format': 'svg',
                'width': width,
                'height': height,
                'size_bytes': len(svg_content.encode('utf-8'))
            }
            
        except Exception as e:
            logger.error(f"SVG export failed: {e}")
            raise
    
    def _export_pdf(self, presentation_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """Export as PDF"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            import io
            import uuid
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Create PDF in memory
            pdf_io = io.BytesIO()
            c = canvas.Canvas(pdf_io, pagesize=letter)
            
            # Add content
            title = presentation_data.get('title', 'Untitled Presentation')
            c.drawString(100, 750, title)
            c.drawString(100, 700, "Exported from AI Design Tool")
            
            # Save PDF
            c.save()
            pdf_io.seek(0)
            
            # Save to storage
            filename = f"presentations/{uuid.uuid4()}.pdf"
            file_path = default_storage.save(filename, ContentFile(pdf_io.getvalue()))
            file_url = default_storage.url(file_path)
            
            return {
                'file_url': file_url,
                'file_path': file_path,
                'format': 'pdf',
                'size_bytes': len(pdf_io.getvalue())
            }
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise

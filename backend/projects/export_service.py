"""
Export service for generating different file formats from design data
"""
import io
import json
import zipfile
from typing import Dict
from PIL import Image
from reportlab.pdfgen import canvas as pdf_canvas
from xml.etree import ElementTree as ET
import re


class ExportService:
    """Service for exporting designs to various formats"""
    
    @staticmethod
    def export_to_png(design_data: Dict, width: int, height: int) -> bytes:
        """
        Export design to PNG format
        
        Args:
            design_data: Design JSON data
            width: Canvas width
            height: Canvas height
            
        Returns:
            PNG image bytes
        """
        # Create blank image
        img = Image.new('RGB', (width, height), color='white')
        
        # TODO: Render design components to image
        # This would typically be done on the frontend with Fabric.js
        # Backend can receive base64 image data from frontend
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=100)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def export_to_svg(design_data: Dict) -> str:
        """
        Export design to SVG format
        
        Args:
            design_data: Design JSON data
            
        Returns:
            SVG string
        """
        components = design_data.get('components', [])
        canvas_width = design_data.get('canvasWidth', 1920)
        canvas_height = design_data.get('canvasHeight', 1080)
        
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg width="{canvas_width}" height="{canvas_height}" xmlns="http://www.w3.org/2000/svg">',
        ]
        
        for component in components:
            comp_type = component.get('type')
            
            if comp_type == 'text':
                svg_parts.append(ExportService._text_to_svg(component))
            elif comp_type == 'rectangle':
                svg_parts.append(ExportService._rect_to_svg(component))
            elif comp_type == 'circle':
                svg_parts.append(ExportService._circle_to_svg(component))
            elif comp_type == 'image':
                svg_parts.append(ExportService._image_to_svg(component))
        
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    
    @staticmethod
    def _text_to_svg(component: Dict) -> str:
        """Convert text component to SVG"""
        text = component.get('text', '')
        position = component.get('position', {'x': 0, 'y': 0})
        style = component.get('style', {})
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        font_size = style.get('fontSize', '16px').replace('px', '')
        color = style.get('color', '#000000')
        font_family = style.get('fontFamily', 'Arial')
        
        return f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{color}" font-family="{font_family}">{text}</text>'
    
    @staticmethod
    def _rect_to_svg(component: Dict) -> str:
        """Convert rectangle component to SVG"""
        position = component.get('position', {'x': 0, 'y': 0})
        size = component.get('size', {'width': 100, 'height': 100})
        style = component.get('style', {})
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        width = size.get('width', 100)
        height = size.get('height', 100)
        fill = style.get('backgroundColor', '#CCCCCC')
        stroke = style.get('borderColor', 'none')
        stroke_width = style.get('borderWidth', 0)
        
        return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    
    @staticmethod
    def _circle_to_svg(component: Dict) -> str:
        """Convert circle component to SVG"""
        position = component.get('position', {'x': 0, 'y': 0})
        style = component.get('style', {})
        radius = component.get('radius', 50)
        
        cx = position.get('x', 0) + radius
        cy = position.get('y', 0) + radius
        fill = style.get('backgroundColor', '#CCCCCC')
        
        return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}"/>'
    
    @staticmethod
    def _image_to_svg(component: Dict) -> str:
        """Convert image component to SVG"""
        position = component.get('position', {'x': 0, 'y': 0})
        size = component.get('size', {'width': 100, 'height': 100})
        image_url = component.get('url', '')
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        width = size.get('width', 100)
        height = size.get('height', 100)
        
        return f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="{image_url}"/>'
    
    @staticmethod
    def export_to_pdf(design_data: Dict, width: int, height: int) -> bytes:
        """
        Export design to PDF format
        
        Args:
            design_data: Design JSON data
            width: Canvas width
            height: Canvas height
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF canvas
        pdf = pdf_canvas.Canvas(buffer, pagesize=(width, height))
        
        components = design_data.get('components', [])
        
        for component in components:
            comp_type = component.get('type')
            
            if comp_type == 'text':
                ExportService._add_text_to_pdf(pdf, component)
            elif comp_type == 'rectangle':
                ExportService._add_rect_to_pdf(pdf, component)
            elif comp_type == 'circle':
                ExportService._add_circle_to_pdf(pdf, component)
        
        pdf.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def _add_text_to_pdf(pdf, component: Dict):
        """Add text to PDF"""
        text = component.get('text', '')
        position = component.get('position', {'x': 0, 'y': 0})
        style = component.get('style', {})
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        font_size = int(style.get('fontSize', '16px').replace('px', ''))
        
        pdf.setFont("Helvetica", font_size)
        pdf.drawString(x, y, text)
    
    @staticmethod
    def _add_rect_to_pdf(pdf, component: Dict):
        """Add rectangle to PDF"""
        position = component.get('position', {'x': 0, 'y': 0})
        size = component.get('size', {'width': 100, 'height': 100})
        style = component.get('style', {})
        
        x = position.get('x', 0)
        y = position.get('y', 0)
        width = size.get('width', 100)
        height = size.get('height', 100)
        
        pdf.rect(x, y, width, height, fill=1)
    
    @staticmethod
    def _add_circle_to_pdf(pdf, component: Dict):
        """Add circle to PDF"""
        position = component.get('position', {'x': 0, 'y': 0})
        radius = component.get('radius', 50)
        
        x = position.get('x', 0) + radius
        y = position.get('y', 0) + radius
        
        pdf.circle(x, y, radius, fill=1)
    
    @staticmethod
    def export_to_figma_json(design_data: Dict) -> Dict:
        """
        Export design to Figma-compatible JSON format
        
        Args:
            design_data: Design JSON data
            
        Returns:
            Figma JSON structure
        """
        components = design_data.get('components', [])
        canvas_width = design_data.get('canvasWidth', 1920)
        canvas_height = design_data.get('canvasHeight', 1080)
        
        figma_json = {
            "name": "Exported Design",
            "type": "FRAME",
            "width": canvas_width,
            "height": canvas_height,
            "children": []
        }
        
        for component in components:
            figma_node = ExportService._component_to_figma(component)
            if figma_node:
                figma_json['children'].append(figma_node)
        
        return figma_json
    
    @staticmethod
    def _component_to_figma(component: Dict) -> Dict:
        """Convert component to Figma node format"""
        comp_type = component.get('type')
        position = component.get('position', {'x': 0, 'y': 0})
        size = component.get('size', {'width': 100, 'height': 100})
        style = component.get('style', {})
        
        base_node = {
            "x": position.get('x', 0),
            "y": position.get('y', 0),
            "width": size.get('width', 100),
            "height": size.get('height', 100),
        }
        
        if comp_type == 'text':
            return {
                **base_node,
                "type": "TEXT",
                "name": "Text",
                "characters": component.get('text', ''),
                "fontSize": int(style.get('fontSize', '16px').replace('px', '')),
                "fontFamily": style.get('fontFamily', 'Inter'),
                "fills": [{
                    "type": "SOLID",
                    "color": ExportService._hex_to_rgb(style.get('color', '#000000'))
                }]
            }
        
        elif comp_type == 'rectangle':
            return {
                **base_node,
                "type": "RECTANGLE",
                "name": "Rectangle",
                "fills": [{
                    "type": "SOLID",
                    "color": ExportService._hex_to_rgb(style.get('backgroundColor', '#CCCCCC'))
                }],
                "cornerRadius": int(style.get('borderRadius', '0px').replace('px', ''))
            }
        
        elif comp_type == 'circle':
            radius = component.get('radius', 50)
            return {
                "type": "ELLIPSE",
                "name": "Circle",
                "x": position.get('x', 0),
                "y": position.get('y', 0),
                "width": radius * 2,
                "height": radius * 2,
                "fills": [{
                    "type": "SOLID",
                    "color": ExportService._hex_to_rgb(style.get('backgroundColor', '#CCCCCC'))
                }]
            }
        
        return base_node
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Dict:
        """Convert hex color to Figma RGB format"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            return {"r": r, "g": g, "b": b}
        
        return {"r": 0, "g": 0, "b": 0}
    
    @staticmethod
    def optimize_svg(svg_content: str) -> str:
        """
        Optimize SVG by removing unnecessary attributes and formatting
        
        Args:
            svg_content: SVG string
            
        Returns:
            Optimized SVG string
        """
        
        try:
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Remove comments
            for element in root.iter():
                if element.tag == ET.Comment:
                    element.getparent().remove(element)
            
            # Remove unnecessary attributes
            unnecessary_attrs = ['id', 'data-name', 'class']
            for element in root.iter():
                for attr in unnecessary_attrs:
                    if attr in element.attrib:
                        del element.attrib[attr]
            
            # Round coordinates to 2 decimal places
            for element in root.iter():
                for attr in ['x', 'y', 'cx', 'cy', 'r', 'width', 'height']:
                    if attr in element.attrib:
                        try:
                            value = float(element.attrib[attr])
                            element.attrib[attr] = f"{value:.2f}"
                        except ValueError:
                            pass
            
            # Convert back to string
            optimized = ET.tostring(root, encoding='unicode')
            
            # Remove extra whitespace
            optimized = re.sub(r'\s+', ' ', optimized)
            optimized = re.sub(r'>\s+<', '><', optimized)
            
            return optimized
            
        except Exception:
            # If optimization fails, return original
            return svg_content
    
    @staticmethod
    def export_batch(projects: list, format: str = 'svg') -> bytes:
        """
        Export multiple projects in a single ZIP file
        
        Args:
            projects: List of Project objects
            format: Export format (svg, pdf, png, figma)
            
        Returns:
            ZIP file bytes
        """
        import json
        
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for idx, project in enumerate(projects):
                design_data = project.design_data
                filename = f"{project.name.replace(' ', '_')}_{idx+1}"
                
                try:
                    if format == 'svg':
                        content = ExportService.export_to_svg(design_data)
                        zip_file.writestr(f"{filename}.svg", content)
                        
                    elif format == 'pdf':
                        content = ExportService.export_to_pdf(
                            design_data,
                            project.canvas_width,
                            project.canvas_height
                        )
                        zip_file.writestr(f"{filename}.pdf", content)
                        
                    elif format == 'png':
                        content = ExportService.export_to_png(
                            design_data,
                            project.canvas_width,
                            project.canvas_height
                        )
                        zip_file.writestr(f"{filename}.png", content)
                        
                    elif format == 'figma':
                        content = ExportService.export_to_figma_json(design_data)
                        zip_file.writestr(
                            f"{filename}.figma.json",
                            json.dumps(content, indent=2)
                        )
                        
                except Exception as e:
                    # Log error but continue with other exports
                    error_msg = f"Error exporting {project.name}: {str(e)}"
                    zip_file.writestr(f"{filename}_error.txt", error_msg)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def create_export_template(name: str, template_data: Dict) -> Dict:
        """
        Create an export template for reusable export configurations
        
        Args:
            name: Template name
            template_data: Template configuration
            
        Returns:
            Template object
        """
        return {
            'name': name,
            'format': template_data.get('format', 'svg'),
            'quality': template_data.get('quality', 'high'),
            'optimize': template_data.get('optimize', True),
            'include_metadata': template_data.get('include_metadata', False),
            'compression': template_data.get('compression', 'medium'),
            'dimensions': template_data.get('dimensions', {
                'width': None,  # Original size
                'height': None,
                'scale': 1.0
            }),
            'options': template_data.get('options', {
                'svg': {
                    'pretty_print': False,
                    'embed_fonts': True,
                    'convert_text_to_paths': False
                },
                'pdf': {
                    'page_size': 'A4',
                    'orientation': 'portrait',
                    'compress': True,
                    'embed_images': True
                },
                'png': {
                    'quality': 95,
                    'optimize': True,
                    'progressive': True
                },
                'figma': {
                    'include_constraints': True,
                    'flatten_groups': False,
                    'convert_effects': True
                }
            })
        }
    
    @staticmethod
    def export_with_template(design_data: Dict, template: Dict) -> bytes:
        """
        Export design using a predefined template
        
        Args:
            design_data: Design JSON data
            template: Export template configuration
            
        Returns:
            Exported file bytes
        """
        
        format = template.get('format', 'svg')
        optimize = template.get('optimize', True)
        dimensions = template.get('dimensions', {})
        
        # Get original dimensions
        width = dimensions.get('width') or design_data.get('canvasWidth', 1920)
        height = dimensions.get('height') or design_data.get('canvasHeight', 1080)
        scale = dimensions.get('scale', 1.0)
        
        # Apply scaling
        width = int(width * scale)
        height = int(height * scale)
        
        # Export based on format
        if format == 'svg':
            content = ExportService.export_to_svg(design_data)
            if optimize:
                content = ExportService.optimize_svg(content)
            return content.encode('utf-8')
            
        elif format == 'pdf':
            return ExportService.export_to_pdf(design_data, width, height)
            
        elif format == 'png':
            return ExportService.export_to_png(design_data, width, height)
            
        elif format == 'figma':
            content = ExportService.export_to_figma_json(design_data)
            return json.dumps(content, indent=2).encode('utf-8')
        
        raise ValueError(f"Unsupported format: {format}")

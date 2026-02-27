"""
Enhanced export service with support for PNG, SVG, PDF, and Figma JSON
"""
import io
import base64
from typing import Dict, Optional
from xml.etree import ElementTree as ET
from reportlab.pdfgen import canvas as pdf_canvas


class EnhancedExportService:
    """
    Enhanced export service for multiple file formats
    """
    
    @staticmethod
    def export_to_svg(design_data: Dict, width: int, height: int) -> str:
        """
        Export design to SVG format
        
        Args:
            design_data: Design JSON data with elements
            width: Canvas width
            height: Canvas height
            
        Returns:
            SVG string
        """
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': str(width),
            'height': str(height),
            'viewBox': f'0 0 {width} {height}'
        })
        
        # Add background
        background = design_data.get('background', '#FFFFFF')
        ET.SubElement(svg, 'rect', {
            'width': str(width),
            'height': str(height),
            'fill': background
        })
        
        # Add elements
        elements = design_data.get('elements', [])
        for element in elements:
            element_type = element.get('type')
            
            if element_type == 'text':
                EnhancedExportService._add_svg_text(svg, element)
            elif element_type == 'shape':
                EnhancedExportService._add_svg_shape(svg, element)
            elif element_type == 'image':
                EnhancedExportService._add_svg_image(svg, element)
            elif element_type == 'rect':
                EnhancedExportService._add_svg_rect(svg, element)
            elif element_type == 'circle':
                EnhancedExportService._add_svg_circle(svg, element)
        
        return ET.tostring(svg, encoding='unicode', method='xml')
    
    @staticmethod
    def _add_svg_text(parent: ET.Element, element: Dict):
        """Add text element to SVG"""
        pos = element.get('position', {})
        style = element.get('style', {})
        
        text_elem = ET.SubElement(parent, 'text', {
            'x': str(pos.get('x', 0)),
            'y': str(pos.get('y', 0)),
            'font-family': style.get('fontFamily', 'Arial'),
            'font-size': str(style.get('fontSize', 16)),
            'fill': style.get('color', '#000000'),
            'font-weight': style.get('fontWeight', 'normal')
        })
        text_elem.text = element.get('content', '')
    
    @staticmethod
    def _add_svg_rect(parent: ET.Element, element: Dict):
        """Add rectangle to SVG"""
        pos = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        
        ET.SubElement(parent, 'rect', {
            'x': str(pos.get('x', 0)),
            'y': str(pos.get('y', 0)),
            'width': str(size.get('width', 100)),
            'height': str(size.get('height', 100)),
            'fill': style.get('backgroundColor', '#CCCCCC'),
            'stroke': style.get('borderColor', 'none'),
            'stroke-width': str(style.get('borderWidth', 0)),
            'rx': str(style.get('borderRadius', 0))
        })
    
    @staticmethod
    def _add_svg_circle(parent: ET.Element, element: Dict):
        """Add circle to SVG"""
        pos = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        
        radius = size.get('width', 100) / 2
        
        ET.SubElement(parent, 'circle', {
            'cx': str(pos.get('x', 0) + radius),
            'cy': str(pos.get('y', 0) + radius),
            'r': str(radius),
            'fill': style.get('backgroundColor', '#CCCCCC'),
            'stroke': style.get('borderColor', 'none'),
            'stroke-width': str(style.get('borderWidth', 0))
        })
    
    @staticmethod
    def _add_svg_shape(parent: ET.Element, element: Dict):
        """Add generic shape to SVG"""
        # Implementation for various shapes
        pass
    
    @staticmethod
    def _add_svg_image(parent: ET.Element, element: Dict):
        """Add image to SVG"""
        pos = element.get('position', {})
        size = element.get('size', {})
        
        ET.SubElement(parent, 'image', {
            'x': str(pos.get('x', 0)),
            'y': str(pos.get('y', 0)),
            'width': str(size.get('width', 100)),
            'height': str(size.get('height', 100)),
            'href': element.get('src', '')
        })
    
    @staticmethod
    def export_to_pdf(design_data: Dict, width: int, height: int) -> bytes:
        """
        Export design to PDF format
        
        Args:
            design_data: Design JSON data
            width: Canvas width in pixels
            height: Canvas height in pixels
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        
        # Create PDF canvas
        c = pdf_canvas.Canvas(buffer, pagesize=(width, height))
        
        # Add background
        background = design_data.get('background', '#FFFFFF')
        if background != 'transparent':
            c.setFillColor(background)
            c.rect(0, 0, width, height, fill=1)
        
        # Add elements
        elements = design_data.get('elements', [])
        for element in elements:
            element_type = element.get('type')
            
            if element_type == 'text':
                EnhancedExportService._add_pdf_text(c, element, height)
            elif element_type == 'rect':
                EnhancedExportService._add_pdf_rect(c, element, height)
            elif element_type == 'circle':
                EnhancedExportService._add_pdf_circle(c, element, height)
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def _add_pdf_text(canvas, element: Dict, page_height: int):
        """Add text to PDF"""
        pos = element.get('position', {})
        style = element.get('style', {})
        
        # PDF coordinates are bottom-left, need to flip Y
        x = pos.get('x', 0)
        y = page_height - pos.get('y', 0)
        
        canvas.setFont(style.get('fontFamily', 'Helvetica'), style.get('fontSize', 16))
        canvas.setFillColor(style.get('color', '#000000'))
        canvas.drawString(x, y, element.get('content', ''))
    
    @staticmethod
    def _add_pdf_rect(canvas, element: Dict, page_height: int):
        """Add rectangle to PDF"""
        pos = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        
        x = pos.get('x', 0)
        y = page_height - pos.get('y', 0) - size.get('height', 100)
        
        canvas.setFillColor(style.get('backgroundColor', '#CCCCCC'))
        canvas.rect(x, y, size.get('width', 100), size.get('height', 100), fill=1)
    
    @staticmethod
    def _add_pdf_circle(canvas, element: Dict, page_height: int):
        """Add circle to PDF"""
        pos = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        
        radius = size.get('width', 100) / 2
        x = pos.get('x', 0) + radius
        y = page_height - pos.get('y', 0) - radius
        
        canvas.setFillColor(style.get('backgroundColor', '#CCCCCC'))
        canvas.circle(x, y, radius, fill=1)
    
    @staticmethod
    def export_to_figma_json(design_data: Dict, width: int, height: int) -> Dict:
        """
        Export design to Figma-compatible JSON format
        
        Args:
            design_data: Design JSON data
            width: Canvas width
            height: Canvas height
            
        Returns:
            Figma JSON dictionary
        """
        figma_doc = {
            "name": design_data.get('name', 'Untitled'),
            "type": "CANVAS",
            "children": []
        }
        
        # Create frame for canvas
        frame = {
            "id": "0:1",
            "name": "Frame 1",
            "type": "FRAME",
            "backgroundColor": EnhancedExportService._hex_to_rgba(
                design_data.get('background', '#FFFFFF')
            ),
            "absoluteBoundingBox": {
                "x": 0,
                "y": 0,
                "width": width,
                "height": height
            },
            "constraints": {
                "vertical": "TOP",
                "horizontal": "LEFT"
            },
            "children": []
        }
        
        # Convert elements to Figma nodes
        elements = design_data.get('elements', [])
        for idx, element in enumerate(elements):
            figma_node = EnhancedExportService._element_to_figma_node(element, idx + 2)
            if figma_node:
                frame['children'].append(figma_node)
        
        figma_doc['children'].append(frame)
        
        return figma_doc
    
    @staticmethod
    def _element_to_figma_node(element: Dict, node_id: int) -> Optional[Dict]:
        """Convert design element to Figma node"""
        element_type = element.get('type')
        pos = element.get('position', {})
        size = element.get('size', {})
        style = element.get('style', {})
        
        base_node = {
            "id": f"0:{node_id}",
            "name": element.get('name', f"Element {node_id}"),
            "absoluteBoundingBox": {
                "x": pos.get('x', 0),
                "y": pos.get('y', 0),
                "width": size.get('width', 100),
                "height": size.get('height', 100)
            },
            "constraints": {
                "vertical": "TOP",
                "horizontal": "LEFT"
            }
        }
        
        if element_type == 'text':
            base_node.update({
                "type": "TEXT",
                "characters": element.get('content', ''),
                "style": {
                    "fontFamily": style.get('fontFamily', 'Inter'),
                    "fontSize": style.get('fontSize', 16),
                    "fontWeight": style.get('fontWeight', 400),
                    "textAlignHorizontal": "LEFT",
                    "textAlignVertical": "TOP"
                },
                "fills": [{
                    "type": "SOLID",
                    "color": EnhancedExportService._hex_to_rgba(style.get('color', '#000000'))
                }]
            })
        elif element_type in ['rect', 'rectangle']:
            base_node.update({
                "type": "RECTANGLE",
                "fills": [{
                    "type": "SOLID",
                    "color": EnhancedExportService._hex_to_rgba(style.get('backgroundColor', '#CCCCCC'))
                }],
                "cornerRadius": style.get('borderRadius', 0)
            })
        elif element_type == 'circle':
            base_node.update({
                "type": "ELLIPSE",
                "fills": [{
                    "type": "SOLID",
                    "color": EnhancedExportService._hex_to_rgba(style.get('backgroundColor', '#CCCCCC'))
                }]
            })
        else:
            return None
        
        return base_node
    
    @staticmethod
    def _hex_to_rgba(hex_color: str) -> Dict:
        """Convert hex color to RGBA dict for Figma"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return {"r": r / 255, "g": g / 255, "b": b / 255, "a": 1}
        
        return {"r": 0, "g": 0, "b": 0, "a": 1}
    
    @staticmethod
    def export_to_png(base64_image: str) -> bytes:
        """
        Export canvas as PNG (expects base64 image from frontend)
        
        Args:
            base64_image: Base64 encoded image data
            
        Returns:
            PNG bytes
        """
        # Remove data URL prefix if present
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_image)
        
        return image_data

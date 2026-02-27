"""
Figma Integration Service
Import and export designs to/from Figma
"""
import os
import httpx
from typing import Dict, List


class FigmaService:
    """Service for Figma API integration"""
    
    BASE_URL = "https://api.figma.com/v1"
    
    def __init__(self, access_token: str = None):
        self.access_token = access_token or os.getenv('FIGMA_ACCESS_TOKEN', '')
    
    def _get_headers(self) -> Dict:
        return {
            'X-Figma-Token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def get_file(self, file_key: str, node_ids: List[str] = None) -> Dict:
        """
        Get Figma file data
        
        Args:
            file_key: The Figma file key (from URL)
            node_ids: Optional list of specific nodes to fetch
        """
        url = f"{self.BASE_URL}/files/{file_key}"
        params = {}
        
        if node_ids:
            params['ids'] = ','.join(node_ids)
        
        response = httpx.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_file_nodes(self, file_key: str, node_ids: List[str]) -> Dict:
        """Get specific nodes from a Figma file"""
        url = f"{self.BASE_URL}/files/{file_key}/nodes"
        params = {'ids': ','.join(node_ids)}
        
        response = httpx.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_file_images(self, file_key: str, node_ids: List[str],
                        format: str = 'png', scale: float = 1.0) -> Dict:
        """
        Export nodes as images
        
        Args:
            file_key: Figma file key
            node_ids: List of node IDs to export
            format: Export format (png, jpg, svg, pdf)
            scale: Scale factor (1-4)
        """
        url = f"{self.BASE_URL}/images/{file_key}"
        params = {
            'ids': ','.join(node_ids),
            'format': format,
            'scale': scale
        }
        
        response = httpx.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_file_styles(self, file_key: str) -> Dict:
        """Get styles from a Figma file"""
        url = f"{self.BASE_URL}/files/{file_key}/styles"
        
        response = httpx.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_file_components(self, file_key: str) -> Dict:
        """Get components from a Figma file"""
        url = f"{self.BASE_URL}/files/{file_key}/components"
        
        response = httpx.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_team_projects(self, team_id: str) -> Dict:
        """Get all projects in a team"""
        url = f"{self.BASE_URL}/teams/{team_id}/projects"
        
        response = httpx.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def get_project_files(self, project_id: str) -> Dict:
        """Get all files in a project"""
        url = f"{self.BASE_URL}/projects/{project_id}/files"
        
        response = httpx.get(url, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def convert_figma_to_design_data(self, figma_data: Dict) -> Dict:
        """
        Convert Figma file structure to our design_data format
        
        Args:
            figma_data: Raw Figma API response
            
        Returns:
            Dict compatible with our Project.design_data
        """
        document = figma_data.get('document', {})
        
        design_data = {
            'name': figma_data.get('name', 'Imported Design'),
            'lastModified': figma_data.get('lastModified'),
            'version': figma_data.get('version'),
            'elements': [],
            'styles': {},
            'components': []
        }
        
        # Extract styles
        if 'styles' in figma_data:
            design_data['styles'] = self._extract_styles(figma_data['styles'])
        
        # Convert canvas/pages
        for child in document.get('children', []):
            if child.get('type') == 'CANVAS':
                page_elements = self._convert_node(child)
                design_data['elements'].extend(page_elements.get('children', []))
        
        return design_data
    
    def _convert_node(self, node: Dict, parent_x: float = 0, parent_y: float = 0) -> Dict:
        """Convert a Figma node to our element format"""
        node_type = node.get('type', '')
        
        # Get absolute position
        abs_bounds = node.get('absoluteBoundingBox', {})
        x = abs_bounds.get('x', 0)
        y = abs_bounds.get('y', 0)
        width = abs_bounds.get('width', 100)
        height = abs_bounds.get('height', 100)
        
        element = {
            'id': node.get('id', ''),
            'name': node.get('name', ''),
            'type': self._map_figma_type(node_type),
            'position': {'x': x, 'y': y},
            'size': {'width': width, 'height': height},
            'rotation': node.get('rotation', 0),
            'opacity': node.get('opacity', 1),
            'visible': node.get('visible', True),
            'locked': node.get('locked', False),
        }
        
        # Handle fills
        fills = node.get('fills', [])
        if fills:
            element['fills'] = self._convert_fills(fills)
        
        # Handle strokes
        strokes = node.get('strokes', [])
        if strokes:
            element['strokes'] = self._convert_strokes(strokes, node)
        
        # Handle effects (shadows, blur)
        effects = node.get('effects', [])
        if effects:
            element['effects'] = self._convert_effects(effects)
        
        # Handle text-specific properties
        if node_type == 'TEXT':
            element['text'] = node.get('characters', '')
            element['textStyle'] = {
                'fontFamily': node.get('style', {}).get('fontFamily', 'Inter'),
                'fontSize': node.get('style', {}).get('fontSize', 14),
                'fontWeight': node.get('style', {}).get('fontWeight', 400),
                'letterSpacing': node.get('style', {}).get('letterSpacing', 0),
                'lineHeight': node.get('style', {}).get('lineHeightPx', 20),
                'textAlign': node.get('style', {}).get('textAlignHorizontal', 'LEFT').lower(),
            }
        
        # Handle children recursively
        children = node.get('children', [])
        if children:
            element['children'] = [
                self._convert_node(child, x, y) for child in children
            ]
        
        return element
    
    def _map_figma_type(self, figma_type: str) -> str:
        """Map Figma node type to our element type"""
        type_map = {
            'FRAME': 'frame',
            'GROUP': 'group',
            'RECTANGLE': 'rectangle',
            'ELLIPSE': 'ellipse',
            'LINE': 'line',
            'TEXT': 'text',
            'VECTOR': 'vector',
            'BOOLEAN_OPERATION': 'vector',
            'COMPONENT': 'component',
            'INSTANCE': 'instance',
            'SLICE': 'slice',
            'STAR': 'star',
            'POLYGON': 'polygon',
        }
        return type_map.get(figma_type, 'shape')
    
    def _convert_fills(self, fills: List[Dict]) -> List[Dict]:
        """Convert Figma fills to our format"""
        converted = []
        for fill in fills:
            if not fill.get('visible', True):
                continue
            
            fill_data = {
                'type': fill.get('type', 'SOLID').lower(),
                'opacity': fill.get('opacity', 1),
            }
            
            if fill.get('type') == 'SOLID':
                color = fill.get('color', {})
                fill_data['color'] = self._rgba_to_hex(
                    color.get('r', 0),
                    color.get('g', 0),
                    color.get('b', 0),
                    color.get('a', 1)
                )
            elif fill.get('type') in ['GRADIENT_LINEAR', 'GRADIENT_RADIAL']:
                fill_data['gradientStops'] = [
                    {
                        'position': stop.get('position', 0),
                        'color': self._rgba_to_hex(
                            stop['color'].get('r', 0),
                            stop['color'].get('g', 0),
                            stop['color'].get('b', 0),
                            stop['color'].get('a', 1)
                        )
                    }
                    for stop in fill.get('gradientStops', [])
                ]
            
            converted.append(fill_data)
        
        return converted
    
    def _convert_strokes(self, strokes: List[Dict], node: Dict) -> List[Dict]:
        """Convert Figma strokes to our format"""
        converted = []
        for stroke in strokes:
            if not stroke.get('visible', True):
                continue
            
            color = stroke.get('color', {})
            converted.append({
                'color': self._rgba_to_hex(
                    color.get('r', 0),
                    color.get('g', 0),
                    color.get('b', 0),
                    color.get('a', 1)
                ),
                'width': node.get('strokeWeight', 1),
                'alignment': node.get('strokeAlign', 'CENTER').lower(),
            })
        
        return converted
    
    def _convert_effects(self, effects: List[Dict]) -> List[Dict]:
        """Convert Figma effects to our format"""
        converted = []
        for effect in effects:
            if not effect.get('visible', True):
                continue
            
            effect_type = effect.get('type', '')
            effect_data = {
                'type': effect_type.lower().replace('_', '-'),
            }
            
            if effect_type in ['DROP_SHADOW', 'INNER_SHADOW']:
                color = effect.get('color', {})
                effect_data.update({
                    'color': self._rgba_to_hex(
                        color.get('r', 0),
                        color.get('g', 0),
                        color.get('b', 0),
                        color.get('a', 1)
                    ),
                    'offsetX': effect.get('offset', {}).get('x', 0),
                    'offsetY': effect.get('offset', {}).get('y', 0),
                    'blur': effect.get('radius', 0),
                    'spread': effect.get('spread', 0),
                })
            elif effect_type in ['LAYER_BLUR', 'BACKGROUND_BLUR']:
                effect_data['blur'] = effect.get('radius', 0)
            
            converted.append(effect_data)
        
        return converted
    
    def _extract_styles(self, styles: Dict) -> Dict:
        """Extract and convert Figma styles"""
        return {
            'colors': [],
            'textStyles': [],
            'effects': [],
        }
    
    def _rgba_to_hex(self, r: float, g: float, b: float, a: float = 1) -> str:
        """Convert RGBA (0-1 range) to hex color"""
        r_int = int(r * 255)
        g_int = int(g * 255)
        b_int = int(b * 255)
        
        if a < 1:
            a_int = int(a * 255)
            return f"#{r_int:02x}{g_int:02x}{b_int:02x}{a_int:02x}"
        return f"#{r_int:02x}{g_int:02x}{b_int:02x}"
    
    def export_to_figma_json(self, design_data: Dict, project_name: str = 'Exported Design') -> Dict:
        """
        Convert our design_data to Figma-compatible JSON
        
        Args:
            design_data: Our Project.design_data
            project_name: Name for the exported file
            
        Returns:
            Figma-compatible JSON structure
        """
        figma_json = {
            'name': project_name,
            'schemaVersion': 0,
            'document': {
                'id': '0:0',
                'name': 'Document',
                'type': 'DOCUMENT',
                'children': [
                    {
                        'id': '0:1',
                        'name': 'Page 1',
                        'type': 'CANVAS',
                        'children': [],
                        'backgroundColor': {'r': 1, 'g': 1, 'b': 1, 'a': 1}
                    }
                ]
            }
        }
        
        # Convert elements
        elements = design_data.get('elements', [])
        for i, element in enumerate(elements):
            figma_node = self._convert_element_to_figma(element, f"1:{i}")
            figma_json['document']['children'][0]['children'].append(figma_node)
        
        return figma_json
    
    def _convert_element_to_figma(self, element: Dict, node_id: str) -> Dict:
        """Convert our element to Figma node format"""
        element_type = element.get('type', 'rectangle')
        
        figma_node = {
            'id': node_id,
            'name': element.get('name', element_type),
            'type': self._map_type_to_figma(element_type),
            'visible': element.get('visible', True),
            'locked': element.get('locked', False),
            'opacity': element.get('opacity', 1),
            'rotation': element.get('rotation', 0),
        }
        
        # Set bounds
        position = element.get('position', {})
        size = element.get('size', {})
        figma_node['absoluteBoundingBox'] = {
            'x': position.get('x', 0),
            'y': position.get('y', 0),
            'width': size.get('width', 100),
            'height': size.get('height', 100),
        }
        
        # Convert fills
        fills = element.get('fills', [])
        if fills:
            figma_node['fills'] = self._convert_fills_to_figma(fills)
        elif element.get('backgroundColor'):
            figma_node['fills'] = [{
                'type': 'SOLID',
                'visible': True,
                'color': self._hex_to_rgba(element['backgroundColor']),
            }]
        
        # Convert strokes
        strokes = element.get('strokes', [])
        if strokes:
            figma_node['strokes'] = self._convert_strokes_to_figma(strokes)
            figma_node['strokeWeight'] = strokes[0].get('width', 1)
        
        # Handle text
        if element_type == 'text':
            figma_node['characters'] = element.get('text', '')
            text_style = element.get('textStyle', {})
            figma_node['style'] = {
                'fontFamily': text_style.get('fontFamily', 'Inter'),
                'fontSize': text_style.get('fontSize', 14),
                'fontWeight': text_style.get('fontWeight', 400),
                'letterSpacing': text_style.get('letterSpacing', 0),
                'textAlignHorizontal': text_style.get('textAlign', 'left').upper(),
            }
        
        # Convert children
        children = element.get('children', [])
        if children:
            figma_node['children'] = [
                self._convert_element_to_figma(child, f"{node_id}:{i}")
                for i, child in enumerate(children)
            ]
        
        return figma_node
    
    def _map_type_to_figma(self, element_type: str) -> str:
        """Map our element type to Figma node type"""
        type_map = {
            'frame': 'FRAME',
            'group': 'GROUP',
            'rectangle': 'RECTANGLE',
            'ellipse': 'ELLIPSE',
            'line': 'LINE',
            'text': 'TEXT',
            'vector': 'VECTOR',
            'component': 'COMPONENT',
            'instance': 'INSTANCE',
            'star': 'STAR',
            'polygon': 'POLYGON',
            'shape': 'RECTANGLE',
        }
        return type_map.get(element_type, 'RECTANGLE')
    
    def _convert_fills_to_figma(self, fills: List[Dict]) -> List[Dict]:
        """Convert our fills to Figma format"""
        figma_fills = []
        for fill in fills:
            figma_fill = {
                'type': fill.get('type', 'solid').upper(),
                'visible': True,
                'opacity': fill.get('opacity', 1),
            }
            
            if fill.get('color'):
                figma_fill['color'] = self._hex_to_rgba(fill['color'])
            
            figma_fills.append(figma_fill)
        
        return figma_fills
    
    def _convert_strokes_to_figma(self, strokes: List[Dict]) -> List[Dict]:
        """Convert our strokes to Figma format"""
        figma_strokes = []
        for stroke in strokes:
            figma_stroke = {
                'type': 'SOLID',
                'visible': True,
                'color': self._hex_to_rgba(stroke.get('color', '#000000')),
            }
            figma_strokes.append(figma_stroke)
        
        return figma_strokes
    
    def _hex_to_rgba(self, hex_color: str) -> Dict:
        """Convert hex color to RGBA (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            a = 255
        elif len(hex_color) == 8:
            r, g, b, a = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16), int(hex_color[6:8], 16)
        else:
            r, g, b, a = 0, 0, 0, 255
        
        return {
            'r': r / 255,
            'g': g / 255,
            'b': b / 255,
            'a': a / 255,
        }

"""
Smart Auto-Layout Engine

AI-powered automatic layout suggestions based on content analysis,
design principles, and user preferences.
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import math
from django.conf import settings


class LayoutType(Enum):
    GRID = "grid"
    FLEXBOX = "flexbox"
    MASONRY = "masonry"
    HERO = "hero"
    CARD_GRID = "card_grid"
    SPLIT = "split"
    CENTERED = "centered"
    SIDEBAR = "sidebar"
    FULL_BLEED = "full_bleed"


class AlignmentType(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass
class LayoutConstraint:
    min_width: int = 0
    max_width: int = 9999
    min_height: int = 0
    max_height: int = 9999
    aspect_ratio: Optional[float] = None
    padding: int = 16
    gap: int = 16


@dataclass
class LayoutSuggestion:
    layout_type: LayoutType
    confidence: float
    properties: Dict[str, Any]
    reasoning: str
    preview_data: Dict[str, Any]


class AutoLayoutEngine:
    """
    Intelligent layout engine that analyzes components and suggests
    optimal layouts based on content, hierarchy, and design principles.
    """
    
    # Golden ratio for aesthetically pleasing proportions
    GOLDEN_RATIO = 1.618
    
    # Common spacing scale (8-point grid)
    SPACING_SCALE = [0, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128]
    
    # Layout patterns for different content types
    CONTENT_PATTERNS = {
        'hero': ['image', 'text', 'button'],
        'card': ['image', 'text', 'text', 'button'],
        'feature': ['icon', 'text', 'text'],
        'testimonial': ['image', 'text', 'text'],
        'pricing': ['text', 'text', 'text', 'button'],
        'gallery': ['image', 'image', 'image'],
        'form': ['text', 'shape', 'shape', 'button'],
    }
    
    def __init__(self, canvas_width: int, canvas_height: int):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid_columns = 12  # 12-column grid system
        self.base_spacing = 8  # 8-point grid
    
    def analyze_components(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze components to understand content structure and relationships.
        """
        analysis = {
            'total_count': len(components),
            'by_type': {},
            'size_distribution': [],
            'positions': [],
            'text_hierarchy': [],
            'image_count': 0,
            'interactive_count': 0,
            'content_pattern': None,
            'visual_weight_center': {'x': 0, 'y': 0},
            'bounding_box': {'min_x': float('inf'), 'min_y': float('inf'), 
                           'max_x': 0, 'max_y': 0},
        }
        
        total_weight = 0
        weighted_x = 0
        weighted_y = 0
        
        for comp in components:
            comp_type = comp.get('component_type', 'unknown')
            props = comp.get('properties', {})
            
            # Count by type
            analysis['by_type'][comp_type] = analysis['by_type'].get(comp_type, 0) + 1
            
            # Track positions and sizes
            pos = props.get('position', {'x': 0, 'y': 0})
            size = props.get('size', {'width': 100, 'height': 100})
            
            analysis['positions'].append({
                'id': comp.get('id'),
                'type': comp_type,
                'x': pos.get('x', 0),
                'y': pos.get('y', 0),
                'width': size.get('width', 100),
                'height': size.get('height', 100),
            })
            
            # Update bounding box
            x, y = pos.get('x', 0), pos.get('y', 0)
            w, h = size.get('width', 100), size.get('height', 100)
            analysis['bounding_box']['min_x'] = min(analysis['bounding_box']['min_x'], x)
            analysis['bounding_box']['min_y'] = min(analysis['bounding_box']['min_y'], y)
            analysis['bounding_box']['max_x'] = max(analysis['bounding_box']['max_x'], x + w)
            analysis['bounding_box']['max_y'] = max(analysis['bounding_box']['max_y'], y + h)
            
            # Calculate visual weight (larger elements have more weight)
            weight = w * h
            weighted_x += (x + w/2) * weight
            weighted_y += (y + h/2) * weight
            total_weight += weight
            
            # Track text hierarchy
            if comp_type == 'text':
                font_size = props.get('fontSize', 16)
                analysis['text_hierarchy'].append({
                    'id': comp.get('id'),
                    'font_size': font_size,
                    'text_preview': props.get('text', '')[:50],
                })
            
            # Count special types
            if comp_type == 'image':
                analysis['image_count'] += 1
            if comp_type in ['button', 'icon']:
                analysis['interactive_count'] += 1
        
        # Calculate visual weight center
        if total_weight > 0:
            analysis['visual_weight_center'] = {
                'x': weighted_x / total_weight,
                'y': weighted_y / total_weight,
            }
        
        # Sort text by size for hierarchy
        analysis['text_hierarchy'].sort(key=lambda x: x['font_size'], reverse=True)
        
        # Detect content pattern
        analysis['content_pattern'] = self._detect_content_pattern(analysis)
        
        return analysis
    
    def _detect_content_pattern(self, analysis: Dict[str, Any]) -> Optional[str]:
        """
        Detect the content pattern based on component types.
        """
        type_sequence = list(analysis['by_type'].keys())
        
        # Check against known patterns
        for pattern_name, pattern in self.CONTENT_PATTERNS.items():
            if self._matches_pattern(type_sequence, pattern):
                return pattern_name
        
        # Heuristic detection
        if analysis['image_count'] >= 3:
            return 'gallery'
        if analysis['image_count'] == 1 and 'button' in analysis['by_type']:
            return 'hero'
        if 'icon' in analysis['by_type'] and len(analysis['text_hierarchy']) >= 2:
            return 'feature'
        
        return None
    
    def _matches_pattern(self, sequence: List[str], pattern: List[str]) -> bool:
        """
        Check if a sequence roughly matches a pattern.
        """
        pattern_set = set(pattern)
        sequence_set = set(sequence)
        # Check if at least 70% of pattern elements are present
        match_count = len(pattern_set & sequence_set)
        return match_count >= len(pattern_set) * 0.7
    
    def suggest_layouts(
        self,
        components: List[Dict[str, Any]],
        constraints: Optional[LayoutConstraint] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[LayoutSuggestion]:
        """
        Generate layout suggestions based on component analysis.
        """
        if constraints is None:
            constraints = LayoutConstraint()
        
        preferences = preferences or {}
        analysis = self.analyze_components(components)
        suggestions = []
        
        # Generate suggestions based on content pattern
        if analysis['content_pattern'] == 'hero':
            suggestions.append(self._create_hero_layout(analysis, constraints))
        
        if analysis['content_pattern'] == 'gallery':
            suggestions.append(self._create_masonry_layout(analysis, constraints))
            suggestions.append(self._create_grid_layout(analysis, constraints, columns=3))
        
        if analysis['content_pattern'] == 'feature':
            suggestions.append(self._create_card_grid_layout(analysis, constraints))
        
        # Always suggest grid and flexbox as alternatives
        if not any(s.layout_type == LayoutType.GRID for s in suggestions):
            suggestions.append(self._create_grid_layout(analysis, constraints))
        
        if not any(s.layout_type == LayoutType.FLEXBOX for s in suggestions):
            suggestions.append(self._create_flexbox_layout(analysis, constraints))
        
        # Suggest centered layout for small number of elements
        if analysis['total_count'] <= 5:
            suggestions.append(self._create_centered_layout(analysis, constraints))
        
        # Suggest split layout if there's a clear image/content divide
        if analysis['image_count'] == 1 and analysis['total_count'] - analysis['image_count'] >= 2:
            suggestions.append(self._create_split_layout(analysis, constraints))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _create_grid_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint,
        columns: int = None
    ) -> LayoutSuggestion:
        """
        Create a grid-based layout suggestion.
        """
        count = analysis['total_count']
        
        # Auto-calculate optimal columns
        if columns is None:
            if count <= 2:
                columns = count
            elif count <= 4:
                columns = 2
            elif count <= 9:
                columns = 3
            else:
                columns = 4
        
        rows = math.ceil(count / columns)
        cell_width = (self.canvas_width - constraints.padding * 2 - constraints.gap * (columns - 1)) / columns
        cell_height = cell_width / self.GOLDEN_RATIO
        
        positions = []
        for i, pos in enumerate(analysis['positions']):
            row = i // columns
            col = i % columns
            positions.append({
                'id': pos['id'],
                'x': constraints.padding + col * (cell_width + constraints.gap),
                'y': constraints.padding + row * (cell_height + constraints.gap),
                'width': cell_width,
                'height': cell_height,
            })
        
        return LayoutSuggestion(
            layout_type=LayoutType.GRID,
            confidence=0.85,
            properties={
                'columns': columns,
                'rows': rows,
                'gap': constraints.gap,
                'padding': constraints.padding,
                'cell_width': cell_width,
                'cell_height': cell_height,
            },
            reasoning=f"Grid layout with {columns} columns provides balanced visual distribution for {count} elements.",
            preview_data={'positions': positions}
        )
    
    def _create_flexbox_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a flexbox-based layout suggestion.
        """
        positions = []
        current_x = constraints.padding
        current_y = constraints.padding
        row_height = 0
        
        for pos in analysis['positions']:
            # Check if we need to wrap to next row
            if current_x + pos['width'] > self.canvas_width - constraints.padding:
                current_x = constraints.padding
                current_y += row_height + constraints.gap
                row_height = 0
            
            positions.append({
                'id': pos['id'],
                'x': current_x,
                'y': current_y,
                'width': pos['width'],
                'height': pos['height'],
            })
            
            current_x += pos['width'] + constraints.gap
            row_height = max(row_height, pos['height'])
        
        return LayoutSuggestion(
            layout_type=LayoutType.FLEXBOX,
            confidence=0.80,
            properties={
                'direction': 'row',
                'wrap': True,
                'gap': constraints.gap,
                'align_items': 'flex-start',
                'justify_content': 'flex-start',
            },
            reasoning="Flexbox layout allows natural content flow with responsive wrapping.",
            preview_data={'positions': positions}
        )
    
    def _create_hero_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a hero section layout.
        """
        hero_height = self.canvas_height * 0.6
        
        # Find the main image
        images = [p for p in analysis['positions'] if p['type'] == 'image']
        texts = sorted(
            [p for p in analysis['positions'] if p['type'] == 'text'],
            key=lambda x: x.get('font_size', 16) if 'font_size' in x else 16,
            reverse=True
        )
        buttons = [p for p in analysis['positions'] if p['type'] == 'button']
        
        positions = []
        
        # Hero image (full width background)
        if images:
            positions.append({
                'id': images[0]['id'],
                'x': 0,
                'y': 0,
                'width': self.canvas_width,
                'height': hero_height,
            })
        
        # Center text content
        content_y = hero_height * 0.3
        for i, text in enumerate(texts[:3]):
            positions.append({
                'id': text['id'],
                'x': self.canvas_width * 0.1,
                'y': content_y + i * 60,
                'width': self.canvas_width * 0.8,
                'height': 50,
            })
        
        # Center button below text
        if buttons:
            positions.append({
                'id': buttons[0]['id'],
                'x': (self.canvas_width - 200) / 2,
                'y': content_y + len(texts[:3]) * 60 + 40,
                'width': 200,
                'height': 50,
            })
        
        return LayoutSuggestion(
            layout_type=LayoutType.HERO,
            confidence=0.92,
            properties={
                'hero_height': hero_height,
                'overlay': True,
                'text_alignment': 'center',
                'vertical_position': 'center',
            },
            reasoning="Hero layout maximizes visual impact with prominent imagery and centered call-to-action.",
            preview_data={'positions': positions}
        )
    
    def _create_masonry_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a masonry/Pinterest-style layout.
        """
        columns = 3
        column_width = (self.canvas_width - constraints.padding * 2 - constraints.gap * (columns - 1)) / columns
        column_heights = [constraints.padding] * columns
        
        positions = []
        for pos in analysis['positions']:
            # Find shortest column
            min_col = column_heights.index(min(column_heights))
            
            # Calculate aspect ratio-aware height
            aspect = pos['height'] / pos['width'] if pos['width'] > 0 else 1
            new_height = column_width * aspect
            
            positions.append({
                'id': pos['id'],
                'x': constraints.padding + min_col * (column_width + constraints.gap),
                'y': column_heights[min_col],
                'width': column_width,
                'height': new_height,
            })
            
            column_heights[min_col] += new_height + constraints.gap
        
        return LayoutSuggestion(
            layout_type=LayoutType.MASONRY,
            confidence=0.88,
            properties={
                'columns': columns,
                'gap': constraints.gap,
                'preserve_aspect_ratio': True,
            },
            reasoning="Masonry layout optimally uses vertical space while preserving image proportions.",
            preview_data={'positions': positions}
        )
    
    def _create_card_grid_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a card-based grid layout.
        """
        count = analysis['total_count']
        columns = min(4, max(1, count))
        
        card_width = (self.canvas_width - constraints.padding * 2 - constraints.gap * (columns - 1)) / columns
        card_height = card_width * 1.2  # Slightly taller cards
        
        positions = []
        for i, pos in enumerate(analysis['positions']):
            row = i // columns
            col = i % columns
            positions.append({
                'id': pos['id'],
                'x': constraints.padding + col * (card_width + constraints.gap),
                'y': constraints.padding + row * (card_height + constraints.gap),
                'width': card_width,
                'height': card_height,
            })
        
        return LayoutSuggestion(
            layout_type=LayoutType.CARD_GRID,
            confidence=0.86,
            properties={
                'columns': columns,
                'gap': constraints.gap,
                'card_padding': 16,
                'card_radius': 8,
                'card_shadow': True,
            },
            reasoning="Card grid provides consistent, organized presentation for feature-like content.",
            preview_data={'positions': positions}
        )
    
    def _create_split_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a split layout (image on one side, content on other).
        """
        split_ratio = 0.5  # 50/50 split
        left_width = (self.canvas_width - constraints.gap) * split_ratio
        right_width = self.canvas_width - left_width - constraints.gap
        
        images = [p for p in analysis['positions'] if p['type'] == 'image']
        others = [p for p in analysis['positions'] if p['type'] != 'image']
        
        positions = []
        
        # Image on left
        if images:
            positions.append({
                'id': images[0]['id'],
                'x': 0,
                'y': 0,
                'width': left_width,
                'height': self.canvas_height,
            })
        
        # Content on right
        content_y = constraints.padding
        for item in others:
            positions.append({
                'id': item['id'],
                'x': left_width + constraints.gap + constraints.padding,
                'y': content_y,
                'width': right_width - constraints.padding * 2,
                'height': item['height'],
            })
            content_y += item['height'] + constraints.gap
        
        return LayoutSuggestion(
            layout_type=LayoutType.SPLIT,
            confidence=0.84,
            properties={
                'split_ratio': split_ratio,
                'image_side': 'left',
                'gap': constraints.gap,
                'vertical_align': 'center',
            },
            reasoning="Split layout creates visual balance between imagery and content.",
            preview_data={'positions': positions}
        )
    
    def _create_centered_layout(
        self,
        analysis: Dict[str, Any],
        constraints: LayoutConstraint
    ) -> LayoutSuggestion:
        """
        Create a centered, vertically stacked layout.
        """
        max_content_width = min(self.canvas_width * 0.6, 800)
        start_x = (self.canvas_width - max_content_width) / 2
        
        # Calculate total height needed
        total_height = sum(p['height'] for p in analysis['positions'])
        total_height += constraints.gap * (len(analysis['positions']) - 1)
        
        start_y = (self.canvas_height - total_height) / 2
        
        positions = []
        current_y = start_y
        
        for pos in analysis['positions']:
            positions.append({
                'id': pos['id'],
                'x': start_x + (max_content_width - pos['width']) / 2,
                'y': current_y,
                'width': min(pos['width'], max_content_width),
                'height': pos['height'],
            })
            current_y += pos['height'] + constraints.gap
        
        return LayoutSuggestion(
            layout_type=LayoutType.CENTERED,
            confidence=0.82,
            properties={
                'max_width': max_content_width,
                'vertical_align': 'center',
                'gap': constraints.gap,
            },
            reasoning="Centered layout focuses attention and works well for minimal content.",
            preview_data={'positions': positions}
        )
    
    def apply_layout(
        self,
        components: List[Dict[str, Any]],
        layout: LayoutSuggestion
    ) -> List[Dict[str, Any]]:
        """
        Apply a layout suggestion to components.
        """
        position_map = {p['id']: p for p in layout.preview_data.get('positions', [])}
        
        updated_components = []
        for comp in components:
            comp_id = comp.get('id')
            if comp_id in position_map:
                new_pos = position_map[comp_id]
                comp_copy = comp.copy()
                comp_copy['properties'] = comp.get('properties', {}).copy()
                comp_copy['properties']['position'] = {
                    'x': new_pos['x'],
                    'y': new_pos['y']
                }
                comp_copy['properties']['size'] = {
                    'width': new_pos['width'],
                    'height': new_pos['height']
                }
                updated_components.append(comp_copy)
            else:
                updated_components.append(comp)
        
        return updated_components
    
    def auto_align(
        self,
        components: List[Dict[str, Any]],
        alignment: AlignmentType = AlignmentType.LEFT,
        distribute: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Auto-align selected components.
        """
        if not components:
            return components
        
        # Calculate bounding box
        min_x = min(c.get('properties', {}).get('position', {}).get('x', 0) for c in components)
        max_x = max(
            c.get('properties', {}).get('position', {}).get('x', 0) + 
            c.get('properties', {}).get('size', {}).get('width', 0) 
            for c in components
        )
        center_x = (min_x + max_x) / 2
        
        updated = []
        for comp in components:
            comp_copy = comp.copy()
            comp_copy['properties'] = comp.get('properties', {}).copy()
            pos = comp_copy['properties'].get('position', {'x': 0, 'y': 0}).copy()
            size = comp_copy['properties'].get('size', {'width': 100, 'height': 100})
            
            if alignment == AlignmentType.LEFT:
                pos['x'] = min_x
            elif alignment == AlignmentType.CENTER:
                pos['x'] = center_x - size['width'] / 2
            elif alignment == AlignmentType.RIGHT:
                pos['x'] = max_x - size['width']
            
            comp_copy['properties']['position'] = pos
            updated.append(comp_copy)
        
        if distribute and len(updated) > 1:
            updated = self._distribute_components(updated)
        
        return updated
    
    def _distribute_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evenly distribute components vertically.
        """
        if len(components) < 2:
            return components
        
        # Sort by Y position
        sorted_comps = sorted(
            components,
            key=lambda c: c.get('properties', {}).get('position', {}).get('y', 0)
        )
        
        # Calculate distribution
        first_y = sorted_comps[0]['properties']['position']['y']
        last_y = sorted_comps[-1]['properties']['position']['y']
        total_gap = last_y - first_y
        gap_per_item = total_gap / (len(sorted_comps) - 1)
        
        for i, comp in enumerate(sorted_comps):
            comp['properties']['position']['y'] = first_y + i * gap_per_item
        
        return sorted_comps
    
    def snap_to_grid(
        self,
        components: List[Dict[str, Any]],
        grid_size: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Snap component positions to a grid.
        """
        updated = []
        for comp in components:
            comp_copy = comp.copy()
            comp_copy['properties'] = comp.get('properties', {}).copy()
            pos = comp_copy['properties'].get('position', {'x': 0, 'y': 0}).copy()
            
            pos['x'] = round(pos['x'] / grid_size) * grid_size
            pos['y'] = round(pos['y'] / grid_size) * grid_size
            
            comp_copy['properties']['position'] = pos
            updated.append(comp_copy)
        
        return updated

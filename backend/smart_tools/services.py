"""
Smart Tools Services

Core logic for smart selection, batch operations, and magic tools.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class SelectionCriteria:
    """Represents selection criteria for smart selection."""
    layer_types: Optional[List[str]] = None
    name_pattern: Optional[str] = None
    color: Optional[str] = None
    color_tolerance: int = 0
    font_family: Optional[str] = None
    has_text: Optional[bool] = None
    is_visible: Optional[bool] = None
    is_locked: Optional[bool] = None
    min_width: Optional[float] = None
    max_width: Optional[float] = None
    min_height: Optional[float] = None
    max_height: Optional[float] = None
    parent_name: Optional[str] = None
    has_effects: Optional[bool] = None
    custom_properties: Optional[Dict[str, Any]] = None


class SmartSelectionService:
    """
    Service for intelligent component selection.
    """
    
    @staticmethod
    def parse_query(query: Dict[str, Any]) -> SelectionCriteria:
        """Parse a JSON query into SelectionCriteria."""
        return SelectionCriteria(
            layer_types=query.get('layer_types'),
            name_pattern=query.get('name_pattern'),
            color=query.get('color'),
            color_tolerance=query.get('color_tolerance', 0),
            font_family=query.get('font_family'),
            has_text=query.get('has_text'),
            is_visible=query.get('is_visible'),
            is_locked=query.get('is_locked'),
            min_width=query.get('min_width'),
            max_width=query.get('max_width'),
            min_height=query.get('min_height'),
            max_height=query.get('max_height'),
            parent_name=query.get('parent_name'),
            has_effects=query.get('has_effects'),
            custom_properties=query.get('custom_properties'),
        )
    
    @staticmethod
    def matches_criteria(component: Dict[str, Any], criteria: SelectionCriteria) -> bool:
        """Check if a component matches the selection criteria."""
        
        # Layer type check
        if criteria.layer_types:
            if component.get('component_type') not in criteria.layer_types:
                return False
        
        # Name pattern check (supports wildcards)
        if criteria.name_pattern:
            pattern = criteria.name_pattern.replace('*', '.*').replace('?', '.')
            name = component.get('name', '')
            if not re.match(pattern, name, re.IGNORECASE):
                return False
        
        # Color check
        if criteria.color:
            component_color = component.get('properties', {}).get('fill_color', '')
            if not SmartSelectionService._colors_match(
                criteria.color, component_color, criteria.color_tolerance
            ):
                return False
        
        # Font family check
        if criteria.font_family:
            component_font = component.get('properties', {}).get('font_family', '')
            if criteria.font_family.lower() != component_font.lower():
                return False
        
        # Visibility check
        if criteria.is_visible is not None:
            if component.get('is_visible', True) != criteria.is_visible:
                return False
        
        # Locked check
        if criteria.is_locked is not None:
            if component.get('is_locked', False) != criteria.is_locked:
                return False
        
        # Size checks
        props = component.get('properties', {})
        size = props.get('size', {})
        width = size.get('width', 0)
        height = size.get('height', 0)
        
        if criteria.min_width is not None and width < criteria.min_width:
            return False
        if criteria.max_width is not None and width > criteria.max_width:
            return False
        if criteria.min_height is not None and height < criteria.min_height:
            return False
        if criteria.max_height is not None and height > criteria.max_height:
            return False
        
        # Text check
        if criteria.has_text is not None:
            has_text = bool(props.get('text'))
            if has_text != criteria.has_text:
                return False
        
        # Effects check
        if criteria.has_effects is not None:
            has_effects = bool(props.get('effects', []))
            if has_effects != criteria.has_effects:
                return False
        
        # Custom properties
        if criteria.custom_properties:
            for key, value in criteria.custom_properties.items():
                if props.get(key) != value:
                    return False
        
        return True
    
    @staticmethod
    def _colors_match(color1: str, color2: str, tolerance: int) -> bool:
        """Check if two colors match within tolerance."""
        if tolerance == 0:
            return color1.lower() == color2.lower()
        
        try:
            r1, g1, b1 = SmartSelectionService._hex_to_rgb(color1)
            r2, g2, b2 = SmartSelectionService._hex_to_rgb(color2)
            
            return (
                abs(r1 - r2) <= tolerance and
                abs(g1 - g2) <= tolerance and
                abs(b1 - b2) <= tolerance
            )
        except:
            return False
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def select_by_type(components: List[Dict], layer_type: str) -> List[Dict]:
        """Select all components of a specific type."""
        return [c for c in components if c.get('component_type') == layer_type]
    
    @staticmethod
    def select_by_color(components: List[Dict], color: str, tolerance: int = 0) -> List[Dict]:
        """Select all components with a specific fill color."""
        result = []
        for component in components:
            fill_color = component.get('properties', {}).get('fill_color', '')
            if SmartSelectionService._colors_match(color, fill_color, tolerance):
                result.append(component)
        return result
    
    @staticmethod
    def select_by_font(components: List[Dict], font_family: str) -> List[Dict]:
        """Select all text components with a specific font."""
        result = []
        for component in components:
            if component.get('component_type') == 'text':
                comp_font = component.get('properties', {}).get('font_family', '')
                if font_family.lower() in comp_font.lower():
                    result.append(component)
        return result
    
    @staticmethod
    def select_similar(target: Dict, components: List[Dict], match_options: Dict) -> List[Dict]:
        """Select components similar to the target component."""
        result = []
        target_props = target.get('properties', {})
        
        for component in components:
            if component.get('id') == target.get('id'):
                continue
            
            comp_props = component.get('properties', {})
            is_similar = True
            
            # Match layer type
            if match_options.get('match_type', True):
                if component.get('component_type') != target.get('component_type'):
                    is_similar = False
                    continue
            
            # Match fill color
            if match_options.get('match_fill', True) and is_similar:
                target_fill = target_props.get('fill_color', '')
                comp_fill = comp_props.get('fill_color', '')
                tolerance = match_options.get('color_tolerance', 0)
                if not SmartSelectionService._colors_match(target_fill, comp_fill, tolerance):
                    is_similar = False
            
            # Match stroke
            if match_options.get('match_stroke', False) and is_similar:
                target_stroke = target_props.get('stroke_color', '')
                comp_stroke = comp_props.get('stroke_color', '')
                if target_stroke != comp_stroke:
                    is_similar = False
            
            # Match font
            if match_options.get('match_font', False) and is_similar:
                target_font = target_props.get('font_family', '')
                comp_font = comp_props.get('font_family', '')
                if target_font != comp_font:
                    is_similar = False
            
            # Match size
            if match_options.get('match_size', False) and is_similar:
                tolerance = match_options.get('size_tolerance', 5)
                target_size = target_props.get('size', {})
                comp_size = comp_props.get('size', {})
                
                tw, th = target_size.get('width', 0), target_size.get('height', 0)
                cw, ch = comp_size.get('width', 0), comp_size.get('height', 0)
                
                if abs(tw - cw) > tolerance or abs(th - ch) > tolerance:
                    is_similar = False
            
            if is_similar:
                result.append(component)
        
        return result


class BatchRenameService:
    """
    Service for batch renaming layers.
    """
    
    @staticmethod
    def generate_names(
        components: List[Dict],
        pattern: str,
        start_number: int = 1,
        number_step: int = 1,
        case_transform: str = 'none'
    ) -> List[Tuple[str, str]]:
        """
        Generate new names for components based on pattern.
        
        Returns list of (component_id, new_name) tuples.
        """
        results = []
        
        for i, component in enumerate(components):
            original_name = component.get('name', '')
            number = start_number + (i * number_step)
            
            new_name = BatchRenameService._apply_pattern(
                pattern, original_name, number, component
            )
            
            new_name = BatchRenameService._apply_case_transform(new_name, case_transform)
            
            results.append((component.get('id'), new_name))
        
        return results
    
    @staticmethod
    def _apply_pattern(pattern: str, original_name: str, number: int, component: Dict) -> str:
        """Apply rename pattern to generate new name."""
        result = pattern
        
        # Basic replacements
        result = result.replace('{name}', original_name)
        result = result.replace('{n}', str(number))
        result = result.replace('{type}', component.get('component_type', ''))
        
        # Size info
        props = component.get('properties', {})
        size = props.get('size', {})
        result = result.replace('{width}', str(int(size.get('width', 0))))
        result = result.replace('{height}', str(int(size.get('height', 0))))
        
        # Padded numbers
        for match in re.finditer(r'\{n:(\d+)\}', result):
            padding = int(match.group(1))
            padded = str(number).zfill(padding)
            result = result.replace(match.group(0), padded)
        
        # Date/time
        now = datetime.now()
        result = result.replace('{date}', now.strftime('%Y-%m-%d'))
        result = result.replace('{time}', now.strftime('%H-%M-%S'))
        
        return result
    
    @staticmethod
    def _apply_case_transform(text: str, transform: str) -> str:
        """Apply case transformation."""
        if transform == 'lower':
            return text.lower()
        elif transform == 'upper':
            return text.upper()
        elif transform == 'title':
            return text.title()
        elif transform == 'sentence':
            return text.capitalize()
        elif transform == 'camel':
            words = re.split(r'[\s_-]+', text)
            return words[0].lower() + ''.join(w.title() for w in words[1:])
        elif transform == 'pascal':
            words = re.split(r'[\s_-]+', text)
            return ''.join(w.title() for w in words)
        elif transform == 'snake':
            return re.sub(r'[\s-]+', '_', text).lower()
        elif transform == 'kebab':
            return re.sub(r'[\s_]+', '-', text).lower()
        return text
    
    @staticmethod
    def find_duplicates(components: List[Dict], new_names: List[Tuple[str, str]]) -> List[str]:
        """Find duplicate names in the result."""
        name_counts = {}
        for _, name in new_names:
            name_counts[name] = name_counts.get(name, 0) + 1
        
        return [name for name, count in name_counts.items() if count > 1]


class FindReplaceService:
    """
    Service for find and replace operations.
    """
    
    @staticmethod
    def find_text(
        components: List[Dict],
        search_text: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False
    ) -> List[Dict]:
        """Find components containing the search text."""
        results = []
        
        for component in components:
            props = component.get('properties', {})
            text = props.get('text', '')
            name = component.get('name', '')
            
            if FindReplaceService._text_matches(
                text, search_text, case_sensitive, whole_word, use_regex
            ) or FindReplaceService._text_matches(
                name, search_text, case_sensitive, whole_word, use_regex
            ):
                # Find positions of matches
                matches = FindReplaceService._find_match_positions(
                    text, search_text, case_sensitive, use_regex
                )
                results.append({
                    'component': component,
                    'matches': matches,
                    'match_count': len(matches)
                })
        
        return results
    
    @staticmethod
    def _text_matches(
        text: str,
        search: str,
        case_sensitive: bool,
        whole_word: bool,
        use_regex: bool
    ) -> bool:
        """Check if text contains the search string."""
        if not text or not search:
            return False
        
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                return bool(re.search(search, text, flags))
            except re.error:
                return False
        
        if not case_sensitive:
            text = text.lower()
            search = search.lower()
        
        if whole_word:
            pattern = r'\b' + re.escape(search) + r'\b'
            return bool(re.search(pattern, text))
        
        return search in text
    
    @staticmethod
    def _find_match_positions(
        text: str,
        search: str,
        case_sensitive: bool,
        use_regex: bool
    ) -> List[Dict]:
        """Find all positions of matches in text."""
        matches = []
        
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                for match in re.finditer(search, text, flags):
                    matches.append({
                        'start': match.start(),
                        'end': match.end(),
                        'text': match.group()
                    })
            except re.error:
                pass
        else:
            search_text = text if case_sensitive else text.lower()
            search_term = search if case_sensitive else search.lower()
            
            start = 0
            while True:
                pos = search_text.find(search_term, start)
                if pos == -1:
                    break
                matches.append({
                    'start': pos,
                    'end': pos + len(search),
                    'text': text[pos:pos + len(search)]
                })
                start = pos + 1
        
        return matches
    
    @staticmethod
    def replace_text(
        text: str,
        search: str,
        replacement: str,
        case_sensitive: bool = False,
        whole_word: bool = False,
        use_regex: bool = False
    ) -> Tuple[str, int]:
        """
        Replace text and return new text with replacement count.
        """
        if not text or not search:
            return text, 0
        
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                new_text, count = re.subn(search, replacement, text, flags=flags)
                return new_text, count
            except re.error:
                return text, 0
        
        if whole_word:
            pattern = r'\b' + re.escape(search) + r'\b'
            flags = 0 if case_sensitive else re.IGNORECASE
            new_text, count = re.subn(pattern, replacement, text, flags=flags)
            return new_text, count
        
        if case_sensitive:
            count = text.count(search)
            return text.replace(search, replacement), count
        else:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(search), re.IGNORECASE)
            new_text, count = re.subn(pattern, replacement, text)
            return new_text, count
    
    @staticmethod
    def find_colors(
        components: List[Dict],
        target_color: str,
        tolerance: int = 0
    ) -> List[Dict]:
        """Find components with a specific color."""
        results = []
        
        for component in components:
            props = component.get('properties', {})
            matches = []
            
            # Check fill color
            fill = props.get('fill_color', '')
            if fill and SmartSelectionService._colors_match(target_color, fill, tolerance):
                matches.append({'property': 'fill_color', 'value': fill})
            
            # Check stroke color
            stroke = props.get('stroke_color', '')
            if stroke and SmartSelectionService._colors_match(target_color, stroke, tolerance):
                matches.append({'property': 'stroke_color', 'value': stroke})
            
            # Check text color
            text_color = props.get('color', '')
            if text_color and SmartSelectionService._colors_match(target_color, text_color, tolerance):
                matches.append({'property': 'color', 'value': text_color})
            
            if matches:
                results.append({
                    'component': component,
                    'matches': matches
                })
        
        return results
    
    @staticmethod
    def replace_colors(
        components: List[Dict],
        find_color: str,
        replace_color: str,
        tolerance: int = 0
    ) -> List[Dict]:
        """Replace colors in components."""
        updated = []
        
        for component in components:
            props = component.get('properties', {})
            changed = False
            
            # Replace fill color
            fill = props.get('fill_color', '')
            if fill and SmartSelectionService._colors_match(find_color, fill, tolerance):
                props['fill_color'] = replace_color
                changed = True
            
            # Replace stroke color
            stroke = props.get('stroke_color', '')
            if stroke and SmartSelectionService._colors_match(find_color, stroke, tolerance):
                props['stroke_color'] = replace_color
                changed = True
            
            # Replace text color
            text_color = props.get('color', '')
            if text_color and SmartSelectionService._colors_match(find_color, text_color, tolerance):
                props['color'] = replace_color
                changed = True
            
            if changed:
                component['properties'] = props
                updated.append(component)
        
        return updated


class BatchResizeService:
    """
    Service for batch resizing operations.
    """
    
    @staticmethod
    def calculate_new_size(
        current_width: float,
        current_height: float,
        mode: str,
        target_width: Optional[float] = None,
        target_height: Optional[float] = None,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        maintain_aspect_ratio: bool = True,
        constraints: Optional[Dict] = None
    ) -> Tuple[float, float]:
        """Calculate new dimensions based on resize mode."""
        
        new_width = current_width
        new_height = current_height
        aspect_ratio = current_width / current_height if current_height > 0 else 1
        
        if mode == 'absolute':
            new_width = target_width if target_width else current_width
            new_height = target_height if target_height else current_height
            
            if maintain_aspect_ratio:
                # Fit within the target size
                if new_width / new_height > aspect_ratio:
                    new_width = new_height * aspect_ratio
                else:
                    new_height = new_width / aspect_ratio
        
        elif mode == 'scale':
            new_width = current_width * scale_x
            new_height = current_height * scale_y
        
        elif mode == 'fit':
            # Fit inside the target size maintaining aspect ratio
            if target_width and target_height:
                width_ratio = target_width / current_width
                height_ratio = target_height / current_height
                scale = min(width_ratio, height_ratio)
                new_width = current_width * scale
                new_height = current_height * scale
        
        elif mode == 'fill':
            # Fill the target size maintaining aspect ratio (may crop)
            if target_width and target_height:
                width_ratio = target_width / current_width
                height_ratio = target_height / current_height
                scale = max(width_ratio, height_ratio)
                new_width = current_width * scale
                new_height = current_height * scale
        
        elif mode == 'width':
            # Set width, calculate height proportionally
            if target_width:
                scale = target_width / current_width
                new_width = target_width
                new_height = current_height * scale
        
        elif mode == 'height':
            # Set height, calculate width proportionally
            if target_height:
                scale = target_height / current_height
                new_height = target_height
                new_width = current_width * scale
        
        # Apply constraints
        if constraints:
            if constraints.get('min_width') and new_width < constraints['min_width']:
                new_width = constraints['min_width']
            if constraints.get('max_width') and new_width > constraints['max_width']:
                new_width = constraints['max_width']
            if constraints.get('min_height') and new_height < constraints['min_height']:
                new_height = constraints['min_height']
            if constraints.get('max_height') and new_height > constraints['max_height']:
                new_height = constraints['max_height']
        
        return new_width, new_height
    
    @staticmethod
    def calculate_position_after_resize(
        x: float, y: float,
        old_width: float, old_height: float,
        new_width: float, new_height: float,
        anchor: str = 'center'
    ) -> Tuple[float, float]:
        """Calculate new position based on anchor point."""
        
        width_diff = new_width - old_width
        height_diff = new_height - old_height
        
        # Calculate anchor offsets
        if 'left' in anchor:
            x_offset = 0
        elif 'right' in anchor:
            x_offset = -width_diff
        else:  # center
            x_offset = -width_diff / 2
        
        if 'top' in anchor:
            y_offset = 0
        elif 'bottom' in anchor:
            y_offset = -height_diff
        else:  # center
            y_offset = -height_diff / 2
        
        return x + x_offset, y + y_offset
    
    @staticmethod
    def batch_resize(
        components: List[Dict],
        mode: str,
        target_width: Optional[float] = None,
        target_height: Optional[float] = None,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        maintain_aspect_ratio: bool = True,
        anchor: str = 'center',
        round_to_pixels: bool = True,
        constraints: Optional[Dict] = None
    ) -> List[Dict]:
        """Resize multiple components."""
        
        results = []
        
        for component in components:
            props = component.get('properties', {})
            size = props.get('size', {})
            position = props.get('position', {})
            
            current_width = size.get('width', 0)
            current_height = size.get('height', 0)
            x = position.get('x', 0)
            y = position.get('y', 0)
            
            # Calculate new size
            new_width, new_height = BatchResizeService.calculate_new_size(
                current_width, current_height,
                mode, target_width, target_height,
                scale_x, scale_y,
                maintain_aspect_ratio, constraints
            )
            
            # Calculate new position
            new_x, new_y = BatchResizeService.calculate_position_after_resize(
                x, y, current_width, current_height,
                new_width, new_height, anchor
            )
            
            # Round if needed
            if round_to_pixels:
                new_width = round(new_width)
                new_height = round(new_height)
                new_x = round(new_x)
                new_y = round(new_y)
            
            results.append({
                'id': component.get('id'),
                'old_size': {'width': current_width, 'height': current_height},
                'new_size': {'width': new_width, 'height': new_height},
                'old_position': {'x': x, 'y': y},
                'new_position': {'x': new_x, 'y': new_y}
            })
        
        return results

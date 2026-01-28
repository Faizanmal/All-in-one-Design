"""
Auto-Layout Engine Service

Core engine for computing auto-layout positions and sizes.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .models import AutoLayoutFrame, AutoLayoutChild


@dataclass
class ComputedBox:
    """Computed box dimensions and position."""
    x: float
    y: float
    width: float
    height: float


class AutoLayoutEngine:
    """
    Engine for computing auto-layout positions and sizes.
    Implements Figma-like auto-layout algorithm.
    """
    
    def __init__(self, frame: AutoLayoutFrame, viewport_width: int = 1920, viewport_height: int = 1080):
        self.frame = frame
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
    
    def compute(self) -> Dict[str, Any]:
        """Compute all child positions and return the results."""
        children = list(self.frame.children.filter(visible=True).order_by('order'))
        
        if not children:
            return self._compute_empty_frame()
        
        # Separate absolute and flow children
        flow_children = [c for c in children if not c.is_absolute]
        absolute_children = [c for c in children if c.is_absolute]
        
        # Compute frame dimensions based on sizing mode
        frame_width, frame_height = self._compute_frame_dimensions(flow_children)
        
        # Compute flow children positions
        flow_positions = self._compute_flow_layout(flow_children, frame_width, frame_height)
        
        # Compute absolute children positions
        absolute_positions = self._compute_absolute_layout(
            absolute_children, frame_width, frame_height
        )
        
        # Merge results
        all_positions = {**flow_positions, **absolute_positions}
        
        # Update computed values in database
        self._update_computed_values(all_positions)
        
        return {
            'frame': {
                'width': frame_width,
                'height': frame_height,
                'x': self.frame.position_x,
                'y': self.frame.position_y,
            },
            'children': all_positions
        }
    
    def _compute_empty_frame(self) -> Dict[str, Any]:
        """Compute dimensions for empty frame."""
        width = self.frame.width or 100
        height = self.frame.height or 100
        
        # Apply padding
        width += self.frame.padding_left + self.frame.padding_right
        height += self.frame.padding_top + self.frame.padding_bottom
        
        return {
            'frame': {
                'width': width,
                'height': height,
                'x': self.frame.position_x,
                'y': self.frame.position_y,
            },
            'children': {}
        }
    
    def _compute_frame_dimensions(self, children: List[AutoLayoutChild]) -> tuple:
        """Compute frame width and height based on sizing mode."""
        padding_h = self.frame.padding_left + self.frame.padding_right
        padding_v = self.frame.padding_top + self.frame.padding_bottom
        
        if self.frame.horizontal_sizing == 'fixed':
            width = self.frame.width or 100
        elif self.frame.horizontal_sizing == 'fill':
            # Fill parent or viewport
            width = self.viewport_width
        else:  # hug
            width = self._compute_content_width(children) + padding_h
        
        if self.frame.vertical_sizing == 'fixed':
            height = self.frame.height or 100
        elif self.frame.vertical_sizing == 'fill':
            height = self.viewport_height
        else:  # hug
            height = self._compute_content_height(children) + padding_v
        
        # Apply constraints
        if self.frame.min_width:
            width = max(width, self.frame.min_width)
        if self.frame.max_width:
            width = min(width, self.frame.max_width)
        if self.frame.min_height:
            height = max(height, self.frame.min_height)
        if self.frame.max_height:
            height = min(height, self.frame.max_height)
        
        return width, height
    
    def _compute_content_width(self, children: List[AutoLayoutChild]) -> float:
        """Compute content width based on children."""
        if not children:
            return 0
        
        if self.frame.direction == 'horizontal':
            # Sum of widths + gaps
            total = sum(self._get_child_width(c) for c in children)
            total += self.frame.item_spacing * (len(children) - 1)
            return total
        else:
            # Max width
            return max(self._get_child_width(c) for c in children)
    
    def _compute_content_height(self, children: List[AutoLayoutChild]) -> float:
        """Compute content height based on children."""
        if not children:
            return 0
        
        if self.frame.direction == 'vertical':
            # Sum of heights + gaps
            total = sum(self._get_child_height(c) for c in children)
            total += self.frame.item_spacing * (len(children) - 1)
            return total
        else:
            # Max height
            return max(self._get_child_height(c) for c in children)
    
    def _get_child_width(self, child: AutoLayoutChild) -> float:
        """Get child width based on sizing mode."""
        if child.horizontal_sizing == 'fixed':
            return child.fixed_width or 100
        elif child.horizontal_sizing == 'fill':
            # Will be calculated during layout
            return 0
        else:  # hug
            return child.computed_width or child.fixed_width or 100
    
    def _get_child_height(self, child: AutoLayoutChild) -> float:
        """Get child height based on sizing mode."""
        if child.vertical_sizing == 'fixed':
            return child.fixed_height or 100
        elif child.vertical_sizing == 'fill':
            return 0
        else:  # hug
            return child.computed_height or child.fixed_height or 100
    
    def _compute_flow_layout(
        self, 
        children: List[AutoLayoutChild],
        frame_width: float,
        frame_height: float
    ) -> Dict[str, Dict]:
        """Compute positions for flow children."""
        positions = {}
        
        if not children:
            return positions
        
        # Available space
        content_width = frame_width - self.frame.padding_left - self.frame.padding_right
        content_height = frame_height - self.frame.padding_top - self.frame.padding_bottom
        
        # Calculate fill children sizes
        fill_children = self._compute_fill_sizes(children, content_width, content_height)
        
        # Starting position
        if self.frame.direction == 'horizontal':
            cursor = self._get_start_position_horizontal(
                children, fill_children, content_width
            )
        else:
            cursor = self._get_start_position_vertical(
                children, fill_children, content_height
            )
        
        # Position each child
        for child in children:
            child_width = fill_children.get(str(child.id), {}).get('width') or self._get_child_width(child)
            child_height = fill_children.get(str(child.id), {}).get('height') or self._get_child_height(child)
            
            if self.frame.direction == 'horizontal':
                x = self.frame.padding_left + cursor
                y = self._get_cross_axis_position(
                    child, child_height, content_height, self.frame.padding_top
                )
                cursor += child_width + self.frame.item_spacing
            else:
                x = self._get_cross_axis_position(
                    child, child_width, content_width, self.frame.padding_left
                )
                y = self.frame.padding_top + cursor
                cursor += child_height + self.frame.item_spacing
            
            positions[str(child.id)] = {
                'x': x,
                'y': y,
                'width': child_width,
                'height': child_height,
            }
        
        return positions
    
    def _compute_fill_sizes(
        self,
        children: List[AutoLayoutChild],
        content_width: float,
        content_height: float
    ) -> Dict[str, Dict]:
        """Calculate sizes for fill children."""
        fill_children = {}
        
        if self.frame.direction == 'horizontal':
            # Calculate remaining width after fixed children
            fixed_width = sum(
                self._get_child_width(c) for c in children 
                if c.horizontal_sizing != 'fill'
            )
            gap_width = self.frame.item_spacing * (len(children) - 1)
            remaining = content_width - fixed_width - gap_width
            
            # Distribute among fill children by ratio
            fill_items = [c for c in children if c.horizontal_sizing == 'fill']
            total_ratio = sum(c.fill_ratio for c in fill_items) or 1
            
            for child in fill_items:
                fill_children[str(child.id)] = {
                    'width': (remaining * child.fill_ratio) / total_ratio,
                    'height': self._get_child_height(child),
                }
        else:
            # Vertical layout - fill height
            fixed_height = sum(
                self._get_child_height(c) for c in children
                if c.vertical_sizing != 'fill'
            )
            gap_height = self.frame.item_spacing * (len(children) - 1)
            remaining = content_height - fixed_height - gap_height
            
            fill_items = [c for c in children if c.vertical_sizing == 'fill']
            total_ratio = sum(c.fill_ratio for c in fill_items) or 1
            
            for child in fill_items:
                fill_children[str(child.id)] = {
                    'width': self._get_child_width(child),
                    'height': (remaining * child.fill_ratio) / total_ratio,
                }
        
        return fill_children
    
    def _get_start_position_horizontal(
        self,
        children: List[AutoLayoutChild],
        fill_children: Dict,
        content_width: float
    ) -> float:
        """Get starting X position based on alignment."""
        total_width = sum(
            fill_children.get(str(c.id), {}).get('width') or self._get_child_width(c)
            for c in children
        )
        total_width += self.frame.item_spacing * (len(children) - 1)
        
        if self.frame.primary_axis_alignment == 'center':
            return (content_width - total_width) / 2
        elif self.frame.primary_axis_alignment == 'end':
            return content_width - total_width
        else:
            return 0
    
    def _get_start_position_vertical(
        self,
        children: List[AutoLayoutChild],
        fill_children: Dict,
        content_height: float
    ) -> float:
        """Get starting Y position based on alignment."""
        total_height = sum(
            fill_children.get(str(c.id), {}).get('height') or self._get_child_height(c)
            for c in children
        )
        total_height += self.frame.item_spacing * (len(children) - 1)
        
        if self.frame.primary_axis_alignment == 'center':
            return (content_height - total_height) / 2
        elif self.frame.primary_axis_alignment == 'end':
            return content_height - total_height
        else:
            return 0
    
    def _get_cross_axis_position(
        self,
        child: AutoLayoutChild,
        child_size: float,
        content_size: float,
        padding: float
    ) -> float:
        """Get cross-axis position based on alignment."""
        # Check child's self-alignment first
        alignment = child.align_self
        if alignment == 'auto':
            alignment = self.frame.cross_axis_alignment
        
        if alignment == 'center':
            return padding + (content_size - child_size) / 2
        elif alignment == 'end':
            return padding + content_size - child_size
        elif alignment == 'stretch':
            return padding
        else:  # start
            return padding
    
    def _compute_absolute_layout(
        self,
        children: List[AutoLayoutChild],
        frame_width: float,
        frame_height: float
    ) -> Dict[str, Dict]:
        """Compute positions for absolute positioned children."""
        positions = {}
        
        for child in children:
            width = child.fixed_width or 100
            height = child.fixed_height or 100
            
            x, y = self._compute_absolute_position(
                child, width, height, frame_width, frame_height
            )
            
            positions[str(child.id)] = {
                'x': x,
                'y': y,
                'width': width,
                'height': height,
            }
        
        return positions
    
    def _compute_absolute_position(
        self,
        child: AutoLayoutChild,
        width: float,
        height: float,
        frame_width: float,
        frame_height: float
    ) -> tuple:
        """Compute absolute position based on anchor."""
        anchor = child.absolute_anchor
        offset_x = child.absolute_x or 0
        offset_y = child.absolute_y or 0
        
        # X position
        if 'left' in anchor:
            x = offset_x
        elif 'right' in anchor:
            x = frame_width - width - offset_x
        else:  # center
            x = (frame_width - width) / 2 + offset_x
        
        # Y position
        if 'top' in anchor:
            y = offset_y
        elif 'bottom' in anchor:
            y = frame_height - height - offset_y
        else:  # center
            y = (frame_height - height) / 2 + offset_y
        
        return x, y
    
    def _update_computed_values(self, positions: Dict[str, Dict]):
        """Update computed values in the database."""
        for child_id, pos in positions.items():
            AutoLayoutChild.objects.filter(id=child_id).update(
                computed_x=pos['x'],
                computed_y=pos['y'],
                computed_width=pos['width'],
                computed_height=pos['height']
            )

"""
Advanced Vector Editing Services

Provides core vector operations including:
- Bezier curve calculations
- Boolean operations (clipper library)
- Path simplification
- Path offset/outline stroke
- SVG path parsing and generation
"""

import math
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import re
import json


@dataclass
class Point:
    """2D point with optional bezier handles."""
    x: float
    y: float
    handle_in: Optional[Tuple[float, float]] = None
    handle_out: Optional[Tuple[float, float]] = None
    corner_radius: float = 0
    point_type: str = 'corner'


@dataclass
class BezierSegment:
    """Cubic bezier curve segment."""
    p0: Point
    p1: Point  # Control point 1
    p2: Point  # Control point 2
    p3: Point


class VectorMath:
    """Mathematical utilities for vector operations."""
    
    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate distance between two points."""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """Linear interpolation."""
        return a + (b - a) * t
    
    @staticmethod
    def lerp_point(p1: Tuple[float, float], p2: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Linear interpolation between two points."""
        return (
            VectorMath.lerp(p1[0], p2[0], t),
            VectorMath.lerp(p1[1], p2[1], t)
        )
    
    @staticmethod
    def bezier_point(p0: Tuple[float, float], p1: Tuple[float, float], 
                     p2: Tuple[float, float], p3: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Calculate point on cubic bezier curve at parameter t."""
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        t2 = t * t
        t3 = t2 * t
        
        return (
            mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0],
            mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
        )
    
    @staticmethod
    def bezier_derivative(p0: Tuple[float, float], p1: Tuple[float, float],
                          p2: Tuple[float, float], p3: Tuple[float, float], t: float) -> Tuple[float, float]:
        """Calculate derivative of cubic bezier curve at parameter t."""
        mt = 1 - t
        
        return (
            3 * mt * mt * (p1[0] - p0[0]) + 6 * mt * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
            3 * mt * mt * (p1[1] - p0[1]) + 6 * mt * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1])
        )
    
    @staticmethod
    def split_bezier(p0: Tuple[float, float], p1: Tuple[float, float],
                     p2: Tuple[float, float], p3: Tuple[float, float], 
                     t: float) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """Split cubic bezier curve at parameter t using de Casteljau's algorithm."""
        # First level
        p01 = VectorMath.lerp_point(p0, p1, t)
        p12 = VectorMath.lerp_point(p1, p2, t)
        p23 = VectorMath.lerp_point(p2, p3, t)
        
        # Second level
        p012 = VectorMath.lerp_point(p01, p12, t)
        p123 = VectorMath.lerp_point(p12, p23, t)
        
        # Third level (the split point)
        p0123 = VectorMath.lerp_point(p012, p123, t)
        
        # Left segment: p0, p01, p012, p0123
        # Right segment: p0123, p123, p23, p3
        return (
            [p0, p01, p012, p0123],
            [p0123, p123, p23, p3]
        )
    
    @staticmethod
    def arc_to_bezier(cx: float, cy: float, rx: float, ry: float,
                      start_angle: float, end_angle: float) -> List[List[Tuple[float, float]]]:
        """
        Convert an arc to cubic bezier curves.
        Returns list of bezier segments (each with 4 points).
        """
        segments = []
        angle_diff = end_angle - start_angle
        
        # Split into 90-degree segments for better approximation
        num_segments = max(1, int(abs(angle_diff) / (math.pi / 2)) + 1)
        angle_per_segment = angle_diff / num_segments
        
        for i in range(num_segments):
            seg_start = start_angle + i * angle_per_segment
            seg_end = start_angle + (i + 1) * angle_per_segment
            
            # Bezier approximation of arc segment
            alpha = math.sin(angle_per_segment) * (math.sqrt(4 + 3 * math.tan(angle_per_segment / 2)**2) - 1) / 3
            
            cos_start = math.cos(seg_start)
            sin_start = math.sin(seg_start)
            cos_end = math.cos(seg_end)
            sin_end = math.sin(seg_end)
            
            p0 = (cx + rx * cos_start, cy + ry * sin_start)
            p3 = (cx + rx * cos_end, cy + ry * sin_end)
            
            p1 = (p0[0] - alpha * rx * sin_start, p0[1] + alpha * ry * cos_start)
            p2 = (p3[0] + alpha * rx * sin_end, p3[1] - alpha * ry * cos_end)
            
            segments.append([p0, p1, p2, p3])
        
        return segments
    
    @staticmethod
    def rotate_point(point: Tuple[float, float], angle: float, 
                     center: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
        """Rotate a point around a center."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        dx = point[0] - center[0]
        dy = point[1] - center[1]
        
        return (
            center[0] + dx * cos_a - dy * sin_a,
            center[1] + dx * sin_a + dy * cos_a
        )
    
    @staticmethod
    def normalize(vector: Tuple[float, float]) -> Tuple[float, float]:
        """Normalize a 2D vector."""
        length = math.sqrt(vector[0]**2 + vector[1]**2)
        if length == 0:
            return (0, 0)
        return (vector[0] / length, vector[1] / length)
    
    @staticmethod
    def perpendicular(vector: Tuple[float, float]) -> Tuple[float, float]:
        """Get perpendicular vector (90 degrees counterclockwise)."""
        return (-vector[1], vector[0])


class SVGPathParser:
    """Parse and generate SVG path data."""
    
    COMMANDS = 'MmZzLlHhVvCcSsQqTtAa'
    
    @staticmethod
    def parse(path_data: str) -> List[Dict[str, Any]]:
        """
        Parse SVG path data string into command list.
        
        Returns list of dicts with 'command' and 'params' keys.
        """
        commands = []
        
        # Split into command + parameters
        pattern = f'([{SVGPathParser.COMMANDS}])([^{SVGPathParser.COMMANDS}]*)'
        matches = re.findall(pattern, path_data)
        
        for command, params_str in matches:
            # Parse parameters
            params = [float(p) for p in re.findall(r'-?\d*\.?\d+(?:e[+-]?\d+)?', params_str)]
            commands.append({
                'command': command,
                'params': params
            })
        
        return commands
    
    @staticmethod
    def to_absolute(commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert relative path commands to absolute."""
        result = []
        current_x, current_y = 0, 0
        start_x, start_y = 0, 0
        
        for cmd in commands:
            command = cmd['command']
            params = cmd['params'].copy()
            is_relative = command.islower()
            command_upper = command.upper()
            
            if command_upper == 'M':
                if is_relative:
                    params[0] += current_x
                    params[1] += current_y
                current_x, current_y = params[0], params[1]
                start_x, start_y = current_x, current_y
                
            elif command_upper == 'L':
                if is_relative:
                    params[0] += current_x
                    params[1] += current_y
                current_x, current_y = params[0], params[1]
                
            elif command_upper == 'H':
                if is_relative:
                    params[0] += current_x
                current_x = params[0]
                params = [current_x, current_y]
                command_upper = 'L'
                
            elif command_upper == 'V':
                if is_relative:
                    params[0] += current_y
                current_y = params[0]
                params = [current_x, current_y]
                command_upper = 'L'
                
            elif command_upper == 'C':
                if is_relative:
                    for i in range(0, len(params), 2):
                        params[i] += current_x
                        params[i + 1] += current_y
                current_x, current_y = params[-2], params[-1]
                
            elif command_upper == 'S':
                if is_relative:
                    for i in range(0, len(params), 2):
                        params[i] += current_x
                        params[i + 1] += current_y
                current_x, current_y = params[-2], params[-1]
                
            elif command_upper == 'Q':
                if is_relative:
                    for i in range(0, len(params), 2):
                        params[i] += current_x
                        params[i + 1] += current_y
                current_x, current_y = params[-2], params[-1]
                
            elif command_upper == 'T':
                if is_relative:
                    params[0] += current_x
                    params[1] += current_y
                current_x, current_y = params[0], params[1]
                
            elif command_upper == 'A':
                if is_relative:
                    params[5] += current_x
                    params[6] += current_y
                current_x, current_y = params[5], params[6]
                
            elif command_upper == 'Z':
                current_x, current_y = start_x, start_y
            
            result.append({
                'command': command_upper,
                'params': params
            })
        
        return result
    
    @staticmethod
    def generate(commands: List[Dict[str, Any]], precision: int = 3) -> str:
        """Generate SVG path data string from commands."""
        parts = []
        
        for cmd in commands:
            command = cmd['command']
            params = cmd.get('params', [])
            
            if params:
                formatted_params = ' '.join(f'{p:.{precision}f}'.rstrip('0').rstrip('.') for p in params)
                parts.append(f'{command}{formatted_params}')
            else:
                parts.append(command)
        
        return ''.join(parts)
    
    @staticmethod
    def to_points(commands: List[Dict[str, Any]]) -> List[Point]:
        """Convert path commands to list of Points with bezier handles."""
        points = []
        current_x, current_y = 0, 0
        last_control = None
        
        for cmd in commands:
            command = cmd['command'].upper()
            params = cmd['params']
            
            if command == 'M':
                current_x, current_y = params[0], params[1]
                points.append(Point(x=current_x, y=current_y, point_type='corner'))
                
            elif command == 'L':
                current_x, current_y = params[0], params[1]
                points.append(Point(x=current_x, y=current_y, point_type='corner'))
                
            elif command == 'C':
                # Cubic bezier: cp1x, cp1y, cp2x, cp2y, x, y
                if points:
                    points[-1].handle_out = (params[0] - points[-1].x, params[1] - points[-1].y)
                
                new_point = Point(
                    x=params[4], y=params[5],
                    handle_in=(params[2] - params[4], params[3] - params[5]),
                    point_type='smooth'
                )
                points.append(new_point)
                current_x, current_y = params[4], params[5]
                last_control = (params[2], params[3])
                
            elif command == 'S':
                # Smooth cubic bezier
                if last_control and points:
                    reflected = (
                        2 * current_x - last_control[0],
                        2 * current_y - last_control[1]
                    )
                    points[-1].handle_out = (reflected[0] - points[-1].x, reflected[1] - points[-1].y)
                
                new_point = Point(
                    x=params[2], y=params[3],
                    handle_in=(params[0] - params[2], params[1] - params[3]),
                    point_type='smooth'
                )
                points.append(new_point)
                current_x, current_y = params[2], params[3]
                last_control = (params[0], params[1])
                
            elif command == 'Q':
                # Quadratic bezier (convert to cubic approximation for handles)
                cp_x, cp_y = params[0], params[1]
                end_x, end_y = params[2], params[3]
                
                if points:
                    cp1 = (
                        current_x + 2/3 * (cp_x - current_x),
                        current_y + 2/3 * (cp_y - current_y)
                    )
                    points[-1].handle_out = (cp1[0] - points[-1].x, cp1[1] - points[-1].y)
                
                cp2 = (
                    end_x + 2/3 * (cp_x - end_x),
                    end_y + 2/3 * (cp_y - end_y)
                )
                new_point = Point(
                    x=end_x, y=end_y,
                    handle_in=(cp2[0] - end_x, cp2[1] - end_y),
                    point_type='smooth'
                )
                points.append(new_point)
                current_x, current_y = end_x, end_y
                
            elif command == 'Z':
                # Close path - no new point needed
                pass
        
        return points


class BooleanOperations:
    """
    Boolean operations on vector paths.
    
    Implements:
    - Union: Combine shapes
    - Subtract: Cut one shape from another
    - Intersect: Keep only overlapping areas
    - Exclude: XOR operation (remove overlapping areas)
    """
    
    SCALE = 100  # Scale factor for integer coordinates
    
    @staticmethod
    def path_to_polygon(path_data: str) -> List[Tuple[int, int]]:
        """Convert SVG path to polygon (list of integer points)."""
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        # Flatten bezier curves to line segments
        polygon = []
        for point in points:
            polygon.append((
                int(point.x * BooleanOperations.SCALE),
                int(point.y * BooleanOperations.SCALE)
            ))
        
        return polygon
    
    @staticmethod
    def polygon_to_path(polygon: List[Tuple[int, int]]) -> str:
        """Convert polygon back to SVG path data."""
        if not polygon:
            return ''
        
        commands = []
        scale = BooleanOperations.SCALE
        
        commands.append({
            'command': 'M',
            'params': [polygon[0][0] / scale, polygon[0][1] / scale]
        })
        
        for point in polygon[1:]:
            commands.append({
                'command': 'L',
                'params': [point[0] / scale, point[1] / scale]
            })
        
        commands.append({'command': 'Z', 'params': []})
        
        return SVGPathParser.generate(commands)
    
    @staticmethod
    def union(paths: List[str]) -> str:
        """
        Combine multiple paths into one.
        
        This is a simplified implementation. In production,
        use a proper polygon clipping library like pyclipper.
        """
        # For production, integrate with pyclipper library
        # This is a placeholder that concatenates paths
        combined_commands = []
        
        for path in paths:
            commands = SVGPathParser.parse(path)
            combined_commands.extend(commands)
        
        return SVGPathParser.generate(combined_commands)
    
    @staticmethod
    def subtract(path1: str, path2: str) -> str:
        """
        Subtract path2 from path1.
        
        Returns the area of path1 that doesn't overlap with path2.
        """
        # Placeholder - use pyclipper in production
        return path1
    
    @staticmethod
    def intersect(path1: str, path2: str) -> str:
        """
        Return only the overlapping area of two paths.
        """
        # Placeholder - use pyclipper in production
        return path1
    
    @staticmethod
    def exclude(path1: str, path2: str) -> str:
        """
        XOR operation - return areas that don't overlap.
        """
        # Placeholder - use pyclipper in production
        return path1


class PathOffset:
    """
    Path offset and outline stroke operations.
    """
    
    @staticmethod
    def offset_path(path_data: str, offset: float, join_type: str = 'miter',
                    miter_limit: float = 4.0) -> str:
        """
        Create an offset path (expand or contract).
        
        Args:
            path_data: SVG path data string
            offset: Positive for expand, negative for contract
            join_type: 'miter', 'round', or 'bevel'
            miter_limit: Maximum miter ratio for miter joins
        
        Returns:
            New SVG path data string
        """
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        if len(points) < 2:
            return path_data
        
        # Calculate offset points
        offset_points = []
        
        for i, point in enumerate(points):
            prev_idx = (i - 1) % len(points)
            next_idx = (i + 1) % len(points)
            
            prev_point = points[prev_idx]
            next_point = points[next_idx]
            
            # Calculate vectors to adjacent points
            v1 = VectorMath.normalize((point.x - prev_point.x, point.y - prev_point.y))
            v2 = VectorMath.normalize((next_point.x - point.x, next_point.y - point.y))
            
            # Get perpendicular vectors (pointing outward)
            n1 = VectorMath.perpendicular(v1)
            n2 = VectorMath.perpendicular(v2)
            
            # Average normal for corner
            avg_n = VectorMath.normalize((n1[0] + n2[0], n1[1] + n2[1]))
            
            # Calculate miter length
            cos_half = n1[0] * avg_n[0] + n1[1] * avg_n[1]
            if abs(cos_half) < 0.001:
                miter_length = offset
            else:
                miter_length = offset / cos_half
            
            # Apply miter limit
            if join_type == 'miter':
                if abs(miter_length) > miter_limit * abs(offset):
                    miter_length = offset * (1 if miter_length > 0 else -1)
            elif join_type == 'bevel':
                miter_length = offset
            # For round, we'd need to add arc segments (simplified here)
            
            offset_points.append(Point(
                x=point.x + avg_n[0] * miter_length,
                y=point.y + avg_n[1] * miter_length,
                point_type=point.point_type
            ))
        
        # Generate new path
        new_commands = []
        if offset_points:
            new_commands.append({
                'command': 'M',
                'params': [offset_points[0].x, offset_points[0].y]
            })
            
            for point in offset_points[1:]:
                new_commands.append({
                    'command': 'L',
                    'params': [point.x, point.y]
                })
            
            new_commands.append({'command': 'Z', 'params': []})
        
        return SVGPathParser.generate(new_commands)
    
    @staticmethod
    def outline_stroke(path_data: str, stroke_width: float, 
                       cap: str = 'round', join: str = 'round') -> str:
        """
        Convert a stroked path to a filled outline.
        
        Args:
            path_data: SVG path data string
            stroke_width: Stroke width to convert
            cap: 'butt', 'round', or 'square'
            join: 'miter', 'round', or 'bevel'
        
        Returns:
            SVG path data for the outline shape
        """
        half_width = stroke_width / 2
        
        # Create two offset paths
        outer = PathOffset.offset_path(path_data, half_width, join)
        inner = PathOffset.offset_path(path_data, -half_width, join)
        
        # Reverse inner path
        inner_commands = SVGPathParser.parse(inner)
        inner_commands = SVGPathParser.to_absolute(inner_commands)
        
        # Combine into compound path
        # In production, properly handle caps and joins
        combined = outer + ' ' + inner
        
        return combined


class CornerRounding:
    """
    Per-point corner rounding operations.
    """
    
    @staticmethod
    def round_corner(p1: Point, corner: Point, p2: Point, radius: float) -> List[Dict[str, Any]]:
        """
        Generate bezier commands for a rounded corner.
        
        Args:
            p1: Point before corner
            corner: The corner point
            p2: Point after corner
            radius: Corner radius
        
        Returns:
            List of SVG path commands for the rounded corner
        """
        if radius <= 0:
            return [{'command': 'L', 'params': [corner.x, corner.y]}]
        
        # Vectors from corner to adjacent points
        v1 = VectorMath.normalize((p1.x - corner.x, p1.y - corner.y))
        v2 = VectorMath.normalize((p2.x - corner.x, p2.y - corner.y))
        
        # Angle between vectors
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        angle = math.acos(max(-1, min(1, dot)))
        
        if angle < 0.01:  # Nearly straight, no rounding needed
            return [{'command': 'L', 'params': [corner.x, corner.y]}]
        
        # Distance from corner to arc start/end
        tan_half = math.tan(angle / 2)
        if tan_half == 0:
            return [{'command': 'L', 'params': [corner.x, corner.y]}]
        
        d = radius / tan_half
        
        # Limit distance to half the segment length
        dist_to_p1 = VectorMath.distance((corner.x, corner.y), (p1.x, p1.y))
        dist_to_p2 = VectorMath.distance((corner.x, corner.y), (p2.x, p2.y))
        max_d = min(dist_to_p1, dist_to_p2) / 2
        d = min(d, max_d)
        actual_radius = d * tan_half
        
        # Arc start and end points
        arc_start = (corner.x + v1[0] * d, corner.y + v1[1] * d)
        arc_end = (corner.x + v2[0] * d, corner.y + v2[1] * d)
        
        # Bezier approximation of arc
        # For 90-degree arc, control point distance is ~0.5523 * radius
        k = 4 / 3 * math.tan(angle / 4) * actual_radius
        
        cp1 = (
            arc_start[0] - v1[0] * k * (1 if v1[1] >= 0 else -1),
            arc_start[1] - v1[1] * k * (1 if v1[0] <= 0 else -1)
        )
        cp2 = (
            arc_end[0] - v2[0] * k * (1 if v2[1] >= 0 else -1),
            arc_end[1] - v2[1] * k * (1 if v2[0] <= 0 else -1)
        )
        
        # Simplified: use arc_start as cp1, arc_end as cp2 reference
        commands = [
            {'command': 'L', 'params': [arc_start[0], arc_start[1]]},
            {'command': 'C', 'params': [
                arc_start[0] + (corner.x - arc_start[0]) * 0.55,
                arc_start[1] + (corner.y - arc_start[1]) * 0.55,
                arc_end[0] + (corner.x - arc_end[0]) * 0.55,
                arc_end[1] + (corner.y - arc_end[1]) * 0.55,
                arc_end[0], arc_end[1]
            ]}
        ]
        
        return commands
    
    @staticmethod
    def apply_corner_rounding(path_data: str, radii: List[float]) -> str:
        """
        Apply corner rounding to a path.
        
        Args:
            path_data: SVG path data string
            radii: List of radius values for each point
        
        Returns:
            New path data with rounded corners
        """
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        if len(points) < 3:
            return path_data
        
        # Pad radii list to match points
        while len(radii) < len(points):
            radii.append(0)
        
        new_commands = []
        
        for i, point in enumerate(points):
            radius = radii[i]
            
            if i == 0:
                new_commands.append({
                    'command': 'M',
                    'params': [point.x, point.y]
                })
            elif radius > 0:
                prev_point = points[i - 1]
                next_point = points[(i + 1) % len(points)]
                
                corner_commands = CornerRounding.round_corner(
                    prev_point, point, next_point, radius
                )
                new_commands.extend(corner_commands)
            else:
                new_commands.append({
                    'command': 'L',
                    'params': [point.x, point.y]
                })
        
        new_commands.append({'command': 'Z', 'params': []})
        
        return SVGPathParser.generate(new_commands)


class VectorService:
    """Main service class for vector editing operations."""
    
    @staticmethod
    def shape_to_path(shape) -> str:
        """Convert a VectorShape model to SVG path data."""
        shape_type = shape.shape_type
        params = shape.parameters
        x, y = shape.x, shape.y
        
        if shape_type == 'rectangle':
            w = params.get('width', 100)
            h = params.get('height', 50)
            r = params.get('cornerRadius', [0, 0, 0, 0])
            
            if isinstance(r, (int, float)):
                r = [r, r, r, r]
            
            if all(radius == 0 for radius in r):
                return f'M{x} {y}L{x+w} {y}L{x+w} {y+h}L{x} {y+h}Z'
            else:
                # Rectangle with rounded corners
                r_tl, r_tr, r_br, r_bl = r
                path = f'M{x + r_tl} {y}'
                path += f'L{x + w - r_tr} {y}'
                if r_tr > 0:
                    path += f'Q{x + w} {y} {x + w} {y + r_tr}'
                path += f'L{x + w} {y + h - r_br}'
                if r_br > 0:
                    path += f'Q{x + w} {y + h} {x + w - r_br} {y + h}'
                path += f'L{x + r_bl} {y + h}'
                if r_bl > 0:
                    path += f'Q{x} {y + h} {x} {y + h - r_bl}'
                path += f'L{x} {y + r_tl}'
                if r_tl > 0:
                    path += f'Q{x} {y} {x + r_tl} {y}'
                path += 'Z'
                return path
        
        elif shape_type == 'ellipse':
            rx = params.get('radiusX', 50)
            ry = params.get('radiusY', 50)
            cx = x + rx
            cy = y + ry
            
            # Approximate ellipse with bezier curves
            k = 0.5523  # Magic number for circle approximation
            
            return (
                f'M{cx} {cy - ry}'
                f'C{cx + rx * k} {cy - ry} {cx + rx} {cy - ry * k} {cx + rx} {cy}'
                f'C{cx + rx} {cy + ry * k} {cx + rx * k} {cy + ry} {cx} {cy + ry}'
                f'C{cx - rx * k} {cy + ry} {cx - rx} {cy + ry * k} {cx - rx} {cy}'
                f'C{cx - rx} {cy - ry * k} {cx - rx * k} {cy - ry} {cx} {cy - ry}'
                'Z'
            )
        
        elif shape_type == 'polygon':
            sides = params.get('sides', 6)
            radius = params.get('radius', 50)
            cx = x + radius
            cy = y + radius
            
            points = []
            for i in range(sides):
                angle = (2 * math.pi * i / sides) - math.pi / 2
                px = cx + radius * math.cos(angle)
                py = cy + radius * math.sin(angle)
                points.append((px, py))
            
            path = f'M{points[0][0]} {points[0][1]}'
            for point in points[1:]:
                path += f'L{point[0]} {point[1]}'
            path += 'Z'
            return path
        
        elif shape_type == 'star':
            num_points = params.get('points', 5)
            outer_radius = params.get('outerRadius', 50)
            inner_radius = params.get('innerRadius', 25)
            cx = x + outer_radius
            cy = y + outer_radius
            
            points = []
            for i in range(num_points * 2):
                angle = (math.pi * i / num_points) - math.pi / 2
                r = outer_radius if i % 2 == 0 else inner_radius
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                points.append((px, py))
            
            path = f'M{points[0][0]} {points[0][1]}'
            for point in points[1:]:
                path += f'L{point[0]} {point[1]}'
            path += 'Z'
            return path
        
        elif shape_type == 'line':
            x2 = params.get('x2', x + 100)
            y2 = params.get('y2', y)
            return f'M{x} {y}L{x2} {y2}'
        
        elif shape_type == 'arrow':
            length = params.get('length', 100)
            head_length = params.get('headLength', 15)
            head_width = params.get('headWidth', 10)
            
            # Arrow body
            path = f'M{x} {y}'
            path += f'L{x + length - head_length} {y}'
            # Arrow head
            path += f'L{x + length - head_length} {y - head_width / 2}'
            path += f'L{x + length} {y}'
            path += f'L{x + length - head_length} {y + head_width / 2}'
            path += f'L{x + length - head_length} {y}'
            return path
        
        elif shape_type == 'arc':
            radius = params.get('radius', 50)
            start_angle = params.get('startAngle', 0)
            end_angle = params.get('endAngle', 180)
            cx = x + radius
            cy = y + radius
            
            # Convert degrees to radians
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            start_x = cx + radius * math.cos(start_rad)
            start_y = cy + radius * math.sin(start_rad)
            end_x = cx + radius * math.cos(end_rad)
            end_y = cy + radius * math.sin(end_rad)
            
            large_arc = 1 if (end_angle - start_angle) > 180 else 0
            sweep = 1
            
            return f'M{start_x} {start_y}A{radius} {radius} 0 {large_arc} {sweep} {end_x} {end_y}'
        
        elif shape_type == 'spiral':
            turns = params.get('turns', 3)
            start_radius = params.get('startRadius', 10)
            end_radius = params.get('endRadius', 50)
            cx = x + end_radius
            cy = y + end_radius
            
            points = []
            num_points = turns * 36  # 36 points per turn
            
            for i in range(num_points):
                angle = (2 * math.pi * i * turns) / num_points
                t = i / (num_points - 1)
                r = start_radius + (end_radius - start_radius) * t
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                points.append((px, py))
            
            path = f'M{points[0][0]} {points[0][1]}'
            for point in points[1:]:
                path += f'L{point[0]} {point[1]}'
            return path
        
        return ''
    
    @staticmethod
    def simplify_path(path_data: str, tolerance: float = 1.0) -> str:
        """
        Simplify a path by removing unnecessary points.
        Uses Ramer-Douglas-Peucker algorithm.
        """
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        if len(points) < 3:
            return path_data
        
        # Flatten to simple points for simplification
        simple_points = [(p.x, p.y) for p in points]
        simplified = VectorService._rdp_simplify(simple_points, tolerance)
        
        # Rebuild path
        new_commands = [{'command': 'M', 'params': [simplified[0][0], simplified[0][1]]}]
        for point in simplified[1:]:
            new_commands.append({'command': 'L', 'params': [point[0], point[1]]})
        new_commands.append({'command': 'Z', 'params': []})
        
        return SVGPathParser.generate(new_commands)
    
    @staticmethod
    def _rdp_simplify(points: List[Tuple[float, float]], tolerance: float) -> List[Tuple[float, float]]:
        """Ramer-Douglas-Peucker line simplification algorithm."""
        if len(points) < 3:
            return points
        
        # Find the point with the maximum distance from the line
        start, end = points[0], points[-1]
        max_dist = 0
        max_idx = 0
        
        for i in range(1, len(points) - 1):
            dist = VectorService._point_to_line_distance(points[i], start, end)
            if dist > max_dist:
                max_dist = dist
                max_idx = i
        
        # If max distance is greater than tolerance, recursively simplify
        if max_dist > tolerance:
            left = VectorService._rdp_simplify(points[:max_idx + 1], tolerance)
            right = VectorService._rdp_simplify(points[max_idx:], tolerance)
            return left[:-1] + right
        else:
            return [start, end]
    
    @staticmethod
    def _point_to_line_distance(point: Tuple[float, float], 
                                 line_start: Tuple[float, float],
                                 line_end: Tuple[float, float]) -> float:
        """Calculate perpendicular distance from point to line."""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return VectorMath.distance(point, line_start)
        
        t = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)))
        
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return VectorMath.distance(point, (closest_x, closest_y))
    
    @staticmethod
    def flatten_beziers(path_data: str, segments_per_curve: int = 10) -> str:
        """
        Convert all bezier curves to line segments.
        Useful for boolean operations and exports.
        """
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        
        new_commands = []
        current_x, current_y = 0, 0
        
        for cmd in commands:
            command = cmd['command']
            params = cmd['params']
            
            if command == 'M':
                new_commands.append(cmd)
                current_x, current_y = params[0], params[1]
                
            elif command == 'L':
                new_commands.append(cmd)
                current_x, current_y = params[0], params[1]
                
            elif command == 'C':
                # Flatten cubic bezier
                p0 = (current_x, current_y)
                p1 = (params[0], params[1])
                p2 = (params[2], params[3])
                p3 = (params[4], params[5])
                
                for i in range(1, segments_per_curve + 1):
                    t = i / segments_per_curve
                    point = VectorMath.bezier_point(p0, p1, p2, p3, t)
                    new_commands.append({
                        'command': 'L',
                        'params': [point[0], point[1]]
                    })
                
                current_x, current_y = params[4], params[5]
                
            elif command == 'Q':
                # Flatten quadratic bezier
                p0 = (current_x, current_y)
                p1 = (params[0], params[1])
                p2 = (params[2], params[3])
                
                for i in range(1, segments_per_curve + 1):
                    t = i / segments_per_curve
                    mt = 1 - t
                    point = (
                        mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                        mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
                    )
                    new_commands.append({
                        'command': 'L',
                        'params': [point[0], point[1]]
                    })
                
                current_x, current_y = params[2], params[3]
                
            elif command == 'Z':
                new_commands.append(cmd)
        
        return SVGPathParser.generate(new_commands)
    
    @staticmethod
    def get_path_bounds(path_data: str) -> Dict[str, float]:
        """Calculate bounding box of a path."""
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        if not points:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        
        min_x = min(p.x for p in points)
        min_y = min(p.y for p in points)
        max_x = max(p.x for p in points)
        max_y = max(p.y for p in points)
        
        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
    
    @staticmethod
    def get_path_length(path_data: str) -> float:
        """Calculate total length of a path."""
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        
        total_length = 0
        current_x, current_y = 0, 0
        start_x, start_y = 0, 0
        
        for cmd in commands:
            command = cmd['command']
            params = cmd['params']
            
            if command == 'M':
                current_x, current_y = params[0], params[1]
                start_x, start_y = current_x, current_y
                
            elif command == 'L':
                length = VectorMath.distance(
                    (current_x, current_y),
                    (params[0], params[1])
                )
                total_length += length
                current_x, current_y = params[0], params[1]
                
            elif command == 'C':
                # Approximate bezier length
                p0 = (current_x, current_y)
                p1 = (params[0], params[1])
                p2 = (params[2], params[3])
                p3 = (params[4], params[5])
                
                # Sample points along curve
                prev = p0
                for i in range(1, 21):
                    t = i / 20
                    point = VectorMath.bezier_point(p0, p1, p2, p3, t)
                    total_length += VectorMath.distance(prev, point)
                    prev = point
                
                current_x, current_y = params[4], params[5]
                
            elif command == 'Z':
                length = VectorMath.distance(
                    (current_x, current_y),
                    (start_x, start_y)
                )
                total_length += length
                current_x, current_y = start_x, start_y
        
        return total_length
    
    @staticmethod
    def reverse_path(path_data: str) -> str:
        """Reverse the direction of a path."""
        commands = SVGPathParser.parse(path_data)
        commands = SVGPathParser.to_absolute(commands)
        points = SVGPathParser.to_points(commands)
        
        if not points:
            return path_data
        
        points.reverse()
        
        # Also reverse bezier handles
        for point in points:
            if point.handle_in or point.handle_out:
                point.handle_in, point.handle_out = point.handle_out, point.handle_in
        
        new_commands = [{'command': 'M', 'params': [points[0].x, points[0].y]}]
        
        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            
            if prev.handle_out and curr.handle_in:
                new_commands.append({
                    'command': 'C',
                    'params': [
                        prev.x + prev.handle_out[0], prev.y + prev.handle_out[1],
                        curr.x + curr.handle_in[0], curr.y + curr.handle_in[1],
                        curr.x, curr.y
                    ]
                })
            else:
                new_commands.append({
                    'command': 'L',
                    'params': [curr.x, curr.y]
                })
        
        new_commands.append({'command': 'Z', 'params': []})
        
        return SVGPathParser.generate(new_commands)

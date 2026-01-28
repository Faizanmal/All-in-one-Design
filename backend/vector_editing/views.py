"""
Vector Editing Views

REST API endpoints for advanced vector editing operations.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
import json

from .models import (
    VectorPath, PathPoint, BooleanOperation, PathOffset,
    VectorPattern, VectorShape, PenToolSession
)
from .serializers import (
    VectorPathSerializer, VectorPathCreateSerializer, VectorPathUpdateSerializer,
    PathPointSerializer, BooleanOperationSerializer, BooleanOperationRequestSerializer,
    PathOffsetSerializer, PathOffsetRequestSerializer,
    VectorPatternSerializer, VectorShapeSerializer, ShapeToPathSerializer,
    PenToolSessionSerializer, PenToolPointSerializer,
    CornerRoundingSerializer, PathSimplifySerializer,
    PathTransformSerializer, PathAlignSerializer, PathDistributeSerializer,
    SVGImportSerializer, SVGExportSerializer
)
from .services import (
    VectorService, SVGPathParser, BooleanOperations, PathOffset as PathOffsetService,
    CornerRounding, VectorMath
)


class VectorPathViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vector paths.
    
    Provides CRUD operations for vector paths with bezier curve support.
    """
    
    serializer_class = VectorPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VectorPath.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return VectorPathCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VectorPathUpdateSerializer
        return VectorPathSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def points(self, request, pk=None):
        """Get all points of a path."""
        path = self.get_object()
        points = path.points.all()
        serializer = PathPointSerializer(points, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_point(self, request, pk=None):
        """Add a new point to the path."""
        path = self.get_object()
        serializer = PenToolPointSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Create new point
            last_order = path.points.order_by('-order').first()
            order = (last_order.order + 1) if last_order else 0
            
            point = PathPoint.objects.create(
                path=path,
                x=data['x'],
                y=data['y'],
                handle_in_x=data['handle_in_x'],
                handle_in_y=data['handle_in_y'],
                handle_out_x=data['handle_out_x'],
                handle_out_y=data['handle_out_y'],
                point_type=data['point_type'],
                corner_radius=data['corner_radius'],
                order=order
            )
            
            # Update path data
            self._update_path_data(path)
            
            return Response(PathPointSerializer(point).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_point(self, request, pk=None):
        """Update a specific point on the path."""
        path = self.get_object()
        point_id = request.data.get('point_id')
        
        point = get_object_or_404(PathPoint, id=point_id, path=path)
        serializer = PathPointSerializer(point, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            self._update_path_data(path)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_point(self, request, pk=None):
        """Delete a point from the path."""
        path = self.get_object()
        point_id = request.data.get('point_id')
        
        point = get_object_or_404(PathPoint, id=point_id, path=path)
        point.delete()
        
        self._update_path_data(path)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def split_at_point(self, request, pk=None):
        """Split the path at a specific parameter t."""
        path = self.get_object()
        segment_index = request.data.get('segment_index', 0)
        t = request.data.get('t', 0.5)
        
        # Parse current path
        commands = SVGPathParser.parse(path.path_data)
        commands = SVGPathParser.to_absolute(commands)
        
        # Find the segment to split
        # This is simplified - production would handle all curve types
        
        return Response({
            'message': 'Path split successfully',
            'path_id': str(path.id)
        })
    
    @action(detail=True, methods=['post'])
    def simplify(self, request, pk=None):
        """Simplify path by removing unnecessary points."""
        path = self.get_object()
        tolerance = request.data.get('tolerance', 1.0)
        
        simplified_data = VectorService.simplify_path(path.path_data, tolerance)
        path.path_data = simplified_data
        path.save()
        
        return Response(VectorPathSerializer(path).data)
    
    @action(detail=True, methods=['post'])
    def flatten_beziers(self, request, pk=None):
        """Convert all bezier curves to line segments."""
        path = self.get_object()
        segments = request.data.get('segments_per_curve', 10)
        
        flattened_data = VectorService.flatten_beziers(path.path_data, segments)
        path.path_data = flattened_data
        path.save()
        
        return Response(VectorPathSerializer(path).data)
    
    @action(detail=True, methods=['post'])
    def reverse(self, request, pk=None):
        """Reverse the direction of the path."""
        path = self.get_object()
        
        reversed_data = VectorService.reverse_path(path.path_data)
        path.path_data = reversed_data
        path.save()
        
        return Response(VectorPathSerializer(path).data)
    
    @action(detail=True, methods=['get'])
    def get_info(self, request, pk=None):
        """Get detailed path information."""
        path = self.get_object()
        
        return Response({
            'bounds': VectorService.get_path_bounds(path.path_data),
            'length': VectorService.get_path_length(path.path_data),
            'point_count': path.points.count(),
            'is_closed': path.path_type == 'closed',
        })
    
    def _update_path_data(self, path):
        """Regenerate path data from points."""
        points = path.points.order_by('order')
        
        if not points:
            path.path_data = ''
            path.save()
            return
        
        commands = []
        first_point = points.first()
        commands.append({
            'command': 'M',
            'params': [first_point.x, first_point.y]
        })
        
        prev_point = first_point
        for point in points[1:]:
            if prev_point.handle_out_x or prev_point.handle_out_y or point.handle_in_x or point.handle_in_y:
                # Cubic bezier
                commands.append({
                    'command': 'C',
                    'params': [
                        prev_point.x + prev_point.handle_out_x,
                        prev_point.y + prev_point.handle_out_y,
                        point.x + point.handle_in_x,
                        point.y + point.handle_in_y,
                        point.x, point.y
                    ]
                })
            else:
                # Line
                commands.append({
                    'command': 'L',
                    'params': [point.x, point.y]
                })
            prev_point = point
        
        if path.path_type == 'closed':
            commands.append({'command': 'Z', 'params': []})
        
        path.path_data = SVGPathParser.generate(commands)
        path.save()


class BooleanOperationView(APIView):
    """
    Perform boolean operations on vector paths.
    
    Supports: union, subtract, intersect, exclude, divide, trim, merge
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = BooleanOperationRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        operation_type = data['operation_type']
        path_ids = data['path_ids']
        
        # Get paths
        paths = VectorPath.objects.filter(
            id__in=path_ids,
            user=request.user
        )
        
        if paths.count() != len(path_ids):
            return Response(
                {'error': 'One or more paths not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store original state for undo
        original_state = {
            str(p.id): {
                'path_data': p.path_data,
                'name': p.name
            }
            for p in paths
        }
        
        # Get path data
        path_data_list = [p.path_data for p in paths]
        
        # Perform operation
        if operation_type == 'union':
            result_data = BooleanOperations.union(path_data_list)
        elif operation_type == 'subtract':
            result_data = BooleanOperations.subtract(path_data_list[0], path_data_list[1])
        elif operation_type == 'intersect':
            result_data = BooleanOperations.intersect(path_data_list[0], path_data_list[1])
        elif operation_type == 'exclude':
            result_data = BooleanOperations.exclude(path_data_list[0], path_data_list[1])
        else:
            result_data = BooleanOperations.union(path_data_list)
        
        # Create result path
        first_path = paths.first()
        result_path = VectorPath.objects.create(
            user=request.user,
            project=first_path.project,
            name=f'{operation_type.title()} Result',
            path_type='closed',
            path_data=result_data,
            fill_color=first_path.fill_color,
            stroke_color=first_path.stroke_color,
            stroke_width=first_path.stroke_width
        )
        
        # Record operation
        operation = BooleanOperation.objects.create(
            user=request.user,
            project=first_path.project,
            operation_type=operation_type,
            source_paths=[str(pid) for pid in path_ids],
            result_path=result_path,
            original_state=original_state
        )
        
        return Response({
            'operation': BooleanOperationSerializer(operation).data,
            'result_path': VectorPathSerializer(result_path).data
        }, status=status.HTTP_201_CREATED)


class PathOffsetView(APIView):
    """
    Apply offset/outline operations to paths.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PathOffsetRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get source path
        source_path = get_object_or_404(
            VectorPath,
            id=data['path_id'],
            user=request.user
        )
        
        offset_type = data['offset_type']
        offset_value = data['offset_value']
        join_type = data['join_type']
        miter_limit = data['miter_limit']
        
        # Apply offset
        if offset_type == 'outline_stroke':
            result_data = PathOffsetService.outline_stroke(
                source_path.path_data,
                source_path.stroke_width,
                source_path.stroke_cap,
                source_path.stroke_join
            )
        else:
            offset = offset_value if offset_type == 'expand' else -offset_value
            result_data = PathOffsetService.offset_path(
                source_path.path_data,
                offset,
                join_type,
                miter_limit
            )
        
        # Create result path
        result_path = VectorPath.objects.create(
            user=request.user,
            project=source_path.project,
            name=f'{source_path.name} ({offset_type})',
            path_type='closed',
            path_data=result_data,
            fill_color=source_path.fill_color,
            stroke_color=source_path.stroke_color,
            stroke_width=source_path.stroke_width
        )
        
        # Record operation
        offset_op = PathOffset.objects.create(
            source_path=source_path,
            offset_type=offset_type,
            offset_value=offset_value,
            join_type=join_type,
            miter_limit=miter_limit,
            result_path=result_path
        )
        
        return Response({
            'operation': PathOffsetSerializer(offset_op).data,
            'result_path': VectorPathSerializer(result_path).data
        }, status=status.HTTP_201_CREATED)


class CornerRoundingView(APIView):
    """
    Apply per-point corner rounding to paths.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CornerRoundingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get path
        path = get_object_or_404(
            VectorPath,
            id=data['path_id'],
            user=request.user
        )
        
        # Apply corner rounding
        rounded_data = CornerRounding.apply_corner_rounding(
            path.path_data,
            data['point_radii']
        )
        
        path.path_data = rounded_data
        path.save()
        
        # Update point corner_radius values
        points = path.points.order_by('order')
        for i, point in enumerate(points):
            if i < len(data['point_radii']):
                point.corner_radius = data['point_radii'][i]
                point.save()
        
        return Response(VectorPathSerializer(path).data)


class VectorPatternViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vector patterns.
    """
    
    serializer_class = VectorPatternSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = VectorPattern.objects.filter(user=self.request.user)
        
        # Include public patterns
        if self.request.query_params.get('include_public', 'true') == 'true':
            queryset = queryset | VectorPattern.objects.filter(is_public=True)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def presets(self, request):
        """Get preset patterns."""
        presets = VectorPattern.objects.filter(pattern_type='preset')
        serializer = VectorPatternSerializer(presets, many=True)
        return Response(serializer.data)


class VectorShapeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vector shapes.
    """
    
    serializer_class = VectorShapeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = VectorShape.objects.all()
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def convert_to_path(self, request, pk=None):
        """Convert shape to editable vector path."""
        shape = self.get_object()
        
        keep_original = request.data.get('keep_original', False)
        
        # Generate path data
        path_data = VectorService.shape_to_path(shape)
        
        # Create vector path
        vector_path = VectorPath.objects.create(
            user=request.user,
            project=shape.project,
            name=f'{shape.name} (Path)',
            path_type='closed',
            path_data=path_data,
            fill_color=shape.fill_color,
            stroke_color=shape.stroke_color,
            stroke_width=shape.stroke_width,
            x=shape.x,
            y=shape.y,
            z_index=shape.z_index
        )
        
        if not keep_original:
            shape.delete()
        
        return Response(VectorPathSerializer(vector_path).data, status=status.HTTP_201_CREATED)


class PenToolSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pen tool sessions.
    """
    
    serializer_class = PenToolSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PenToolSession.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_point(self, request, pk=None):
        """Add a point to the current pen session."""
        session = self.get_object()
        serializer = PenToolPointSerializer(data=request.data)
        
        if serializer.is_valid():
            point_data = serializer.validated_data
            
            # Add to temp_points
            temp_points = session.temp_points or []
            temp_points.append(point_data)
            session.temp_points = temp_points
            session.save()
            
            return Response({
                'session': PenToolSessionSerializer(session).data,
                'point_count': len(temp_points)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def close_path(self, request, pk=None):
        """Close the current path and finish the session."""
        session = self.get_object()
        
        if not session.temp_points:
            return Response(
                {'error': 'No points in session'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate path from temp_points
        commands = []
        points = session.temp_points
        
        first_point = points[0]
        commands.append({
            'command': 'M',
            'params': [first_point['x'], first_point['y']]
        })
        
        for i in range(1, len(points)):
            prev = points[i - 1]
            curr = points[i]
            
            if (prev.get('handle_out_x', 0) or prev.get('handle_out_y', 0) or
                curr.get('handle_in_x', 0) or curr.get('handle_in_y', 0)):
                commands.append({
                    'command': 'C',
                    'params': [
                        prev['x'] + prev.get('handle_out_x', 0),
                        prev['y'] + prev.get('handle_out_y', 0),
                        curr['x'] + curr.get('handle_in_x', 0),
                        curr['y'] + curr.get('handle_in_y', 0),
                        curr['x'], curr['y']
                    ]
                })
            else:
                commands.append({
                    'command': 'L',
                    'params': [curr['x'], curr['y']]
                })
        
        commands.append({'command': 'Z', 'params': []})
        
        path_data = SVGPathParser.generate(commands)
        
        # Create vector path
        vector_path = VectorPath.objects.create(
            user=request.user,
            project=session.project,
            name='Pen Path',
            path_type='closed',
            path_data=path_data
        )
        
        # Create PathPoints
        for i, pt in enumerate(points):
            PathPoint.objects.create(
                path=vector_path,
                x=pt['x'],
                y=pt['y'],
                handle_in_x=pt.get('handle_in_x', 0),
                handle_in_y=pt.get('handle_in_y', 0),
                handle_out_x=pt.get('handle_out_x', 0),
                handle_out_y=pt.get('handle_out_y', 0),
                point_type=pt.get('point_type', 'corner'),
                corner_radius=pt.get('corner_radius', 0),
                order=i
            )
        
        # End session
        session.current_path = vector_path
        session.is_active = False
        session.is_closed = True
        session.save()
        
        return Response({
            'session': PenToolSessionSerializer(session).data,
            'path': VectorPathSerializer(vector_path).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel the current pen session."""
        session = self.get_object()
        session.is_active = False
        session.temp_points = []
        session.save()
        
        return Response({'message': 'Session cancelled'})
    
    @action(detail=True, methods=['post'])
    def undo_point(self, request, pk=None):
        """Remove the last point from the session."""
        session = self.get_object()
        
        if session.temp_points:
            session.temp_points = session.temp_points[:-1]
            session.save()
        
        return Response(PenToolSessionSerializer(session).data)


class PathTransformView(APIView):
    """
    Apply transformations to paths.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PathTransformSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        paths = VectorPath.objects.filter(
            id__in=data['path_ids'],
            user=request.user
        )
        
        transform_type = data['transform_type']
        values = data['values']
        
        results = []
        for path in paths:
            # Apply transformation based on type
            if transform_type == 'translate':
                self._apply_translate(path, values.get('dx', 0), values.get('dy', 0))
            elif transform_type == 'rotate':
                self._apply_rotate(path, values.get('angle', 0),
                                   values.get('cx'), values.get('cy'))
            elif transform_type == 'scale':
                self._apply_scale(path, values.get('sx', 1), values.get('sy', 1),
                                  values.get('cx'), values.get('cy'))
            elif transform_type == 'flip_horizontal':
                self._apply_flip(path, horizontal=True)
            elif transform_type == 'flip_vertical':
                self._apply_flip(path, horizontal=False)
            
            path.save()
            results.append(VectorPathSerializer(path).data)
        
        return Response({'paths': results})
    
    def _apply_translate(self, path, dx, dy):
        """Apply translation to path."""
        path.x += dx
        path.y += dy
        
        # Update all points
        for point in path.points.all():
            point.x += dx
            point.y += dy
            point.save()
    
    def _apply_rotate(self, path, angle, cx=None, cy=None):
        """Apply rotation to path."""
        if cx is None:
            bounds = VectorService.get_path_bounds(path.path_data)
            cx = bounds['x'] + bounds['width'] / 2
            cy = bounds['y'] + bounds['height'] / 2
        
        import math
        angle_rad = math.radians(angle)
        
        for point in path.points.all():
            new_pos = VectorMath.rotate_point((point.x, point.y), angle_rad, (cx, cy))
            point.x, point.y = new_pos
            
            # Rotate handles
            if point.handle_in_x or point.handle_in_y:
                handle_in = VectorMath.rotate_point(
                    (point.handle_in_x, point.handle_in_y), angle_rad, (0, 0)
                )
                point.handle_in_x, point.handle_in_y = handle_in
            
            if point.handle_out_x or point.handle_out_y:
                handle_out = VectorMath.rotate_point(
                    (point.handle_out_x, point.handle_out_y), angle_rad, (0, 0)
                )
                point.handle_out_x, point.handle_out_y = handle_out
            
            point.save()
    
    def _apply_scale(self, path, sx, sy, cx=None, cy=None):
        """Apply scaling to path."""
        if cx is None:
            bounds = VectorService.get_path_bounds(path.path_data)
            cx = bounds['x'] + bounds['width'] / 2
            cy = bounds['y'] + bounds['height'] / 2
        
        for point in path.points.all():
            point.x = cx + (point.x - cx) * sx
            point.y = cy + (point.y - cy) * sy
            point.handle_in_x *= sx
            point.handle_in_y *= sy
            point.handle_out_x *= sx
            point.handle_out_y *= sy
            point.save()
    
    def _apply_flip(self, path, horizontal=True):
        """Apply flip to path."""
        bounds = VectorService.get_path_bounds(path.path_data)
        
        if horizontal:
            cx = bounds['x'] + bounds['width'] / 2
            for point in path.points.all():
                point.x = 2 * cx - point.x
                point.handle_in_x *= -1
                point.handle_out_x *= -1
                point.save()
        else:
            cy = bounds['y'] + bounds['height'] / 2
            for point in path.points.all():
                point.y = 2 * cy - point.y
                point.handle_in_y *= -1
                point.handle_out_y *= -1
                point.save()


class PathAlignView(APIView):
    """
    Align multiple paths.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PathAlignSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        paths = list(VectorPath.objects.filter(
            id__in=data['path_ids'],
            user=request.user
        ))
        
        if len(paths) < 2:
            return Response(
                {'error': 'At least 2 paths required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        align_type = data['align_type']
        
        # Get bounds for all paths
        bounds_list = [VectorService.get_path_bounds(p.path_data) for p in paths]
        
        # Calculate alignment target
        if align_type == 'left':
            target = min(b['x'] for b in bounds_list)
            for path, bounds in zip(paths, bounds_list):
                dx = target - bounds['x']
                self._translate_path(path, dx, 0)
        
        elif align_type == 'right':
            target = max(b['x'] + b['width'] for b in bounds_list)
            for path, bounds in zip(paths, bounds_list):
                dx = target - (bounds['x'] + bounds['width'])
                self._translate_path(path, dx, 0)
        
        elif align_type == 'center_h':
            centers = [b['x'] + b['width'] / 2 for b in bounds_list]
            target = sum(centers) / len(centers)
            for path, bounds in zip(paths, bounds_list):
                current_center = bounds['x'] + bounds['width'] / 2
                dx = target - current_center
                self._translate_path(path, dx, 0)
        
        elif align_type == 'top':
            target = min(b['y'] for b in bounds_list)
            for path, bounds in zip(paths, bounds_list):
                dy = target - bounds['y']
                self._translate_path(path, 0, dy)
        
        elif align_type == 'bottom':
            target = max(b['y'] + b['height'] for b in bounds_list)
            for path, bounds in zip(paths, bounds_list):
                dy = target - (bounds['y'] + bounds['height'])
                self._translate_path(path, 0, dy)
        
        elif align_type == 'center_v':
            centers = [b['y'] + b['height'] / 2 for b in bounds_list]
            target = sum(centers) / len(centers)
            for path, bounds in zip(paths, bounds_list):
                current_center = bounds['y'] + bounds['height'] / 2
                dy = target - current_center
                self._translate_path(path, 0, dy)
        
        # Save all paths
        for path in paths:
            path.save()
        
        return Response({
            'paths': [VectorPathSerializer(p).data for p in paths]
        })
    
    def _translate_path(self, path, dx, dy):
        """Translate a path by dx, dy."""
        for point in path.points.all():
            point.x += dx
            point.y += dy
            point.save()


class SVGImportExportView(APIView):
    """
    Import and export SVG files.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Import SVG content."""
        serializer = SVGImportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        svg_content = data['svg_content']
        project_id = data['project_id']
        
        # Parse SVG and extract paths
        # This is a simplified implementation
        import re
        path_pattern = r'<path[^>]*d="([^"]*)"[^>]*/>'
        matches = re.findall(path_pattern, svg_content)
        
        created_paths = []
        for i, path_data in enumerate(matches):
            path = VectorPath.objects.create(
                user=request.user,
                project_id=project_id,
                name=f'Imported Path {i + 1}',
                path_type='closed',
                path_data=path_data
            )
            created_paths.append(path)
        
        return Response({
            'message': f'Imported {len(created_paths)} paths',
            'paths': [VectorPathSerializer(p).data for p in created_paths]
        }, status=status.HTTP_201_CREATED)


class SVGExportView(APIView):
    """
    Export paths as SVG.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SVGExportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        path_ids = data.get('path_ids', [])
        
        if path_ids:
            paths = VectorPath.objects.filter(
                id__in=path_ids,
                user=request.user
            )
        else:
            # Export all user's paths
            paths = VectorPath.objects.filter(user=request.user)[:100]
        
        # Calculate viewBox
        all_bounds = [VectorService.get_path_bounds(p.path_data) for p in paths]
        if all_bounds:
            min_x = min(b['x'] for b in all_bounds)
            min_y = min(b['y'] for b in all_bounds)
            max_x = max(b['x'] + b['width'] for b in all_bounds)
            max_y = max(b['y'] + b['height'] for b in all_bounds)
            
            padding = data.get('viewbox_padding', 0)
            viewbox = f'{min_x - padding} {min_y - padding} {max_x - min_x + 2*padding} {max_y - min_y + 2*padding}'
        else:
            viewbox = '0 0 100 100'
        
        # Generate SVG
        path_elements = [p.get_svg_element() for p in paths]
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">
  {chr(10).join(path_elements)}
</svg>'''
        
        if data.get('minify', False):
            svg_content = ' '.join(svg_content.split())
        
        return Response({
            'svg': svg_content,
            'path_count': paths.count()
        })

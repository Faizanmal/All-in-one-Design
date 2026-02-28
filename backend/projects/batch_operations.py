"""
Batch Operations Models and Service

Multi-select and bulk editing operations for design components.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from typing import Dict, Any, List, Optional
import copy


class BatchOperation(models.Model):
    """
    Track batch operations for undo/redo and history.
    """
    OPERATION_TYPES = [
        ('move', 'Move'),
        ('resize', 'Resize'),
        ('style', 'Style Change'),
        ('delete', 'Delete'),
        ('duplicate', 'Duplicate'),
        ('group', 'Group'),
        ('ungroup', 'Ungroup'),
        ('align', 'Align'),
        ('distribute', 'Distribute'),
        ('lock', 'Lock/Unlock'),
        ('visibility', 'Show/Hide'),
        ('order', 'Change Order'),
        ('transform', 'Transform'),
        ('replace', 'Find & Replace'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('undone', 'Undone'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='batch_operations_projects'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='batch_operations_projects'
    )
    
    operation_type = models.CharField(max_length=20, choices=OPERATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Affected components
    component_ids = models.JSONField(
        default=list,
        help_text="IDs of components affected by this operation"
    )
    component_count = models.IntegerField(default=0)
    
    # Operation parameters
    parameters = models.JSONField(
        default=dict,
        help_text="Operation-specific parameters"
    )
    
    # Before/after state for undo
    before_state = models.JSONField(
        default=dict,
        help_text="State before operation for undo"
    )
    after_state = models.JSONField(
        default=dict,
        help_text="State after operation"
    )
    
    # Results
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_operation_type_display()} on {self.component_count} components"


class BatchOperationService:
    """
    Service for executing batch operations on components.
    """
    
    def __init__(self, project, user):
        self.project = project
        self.user = user
    
    def _save_state(self, components) -> Dict[str, Any]:
        """
        Save current state of components for undo.
        """
        return {
            str(c.id): {
                'properties': copy.deepcopy(c.properties),
                'z_index': c.z_index,
                'component_type': c.component_type,
            }
            for c in components
        }
    
    def _create_operation(
        self,
        operation_type: str,
        component_ids: List[int],
        parameters: Dict[str, Any],
        before_state: Dict[str, Any]
    ) -> BatchOperation:
        """
        Create a batch operation record.
        """
        return BatchOperation.objects.create(
            user=self.user,
            project=self.project,
            operation_type=operation_type,
            component_ids=component_ids,
            component_count=len(component_ids),
            parameters=parameters,
            before_state=before_state,
        )
    
    def bulk_move(
        self,
        component_ids: List[int],
        delta_x: float,
        delta_y: float
    ) -> BatchOperation:
        """
        Move multiple components by a delta.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'move',
            component_ids,
            {'delta_x': delta_x, 'delta_y': delta_y},
            before_state
        )
        
        try:
            with transaction.atomic():
                for comp in components:
                    pos = comp.properties.get('position', {'x': 0, 'y': 0})
                    comp.properties['position'] = {
                        'x': pos.get('x', 0) + delta_x,
                        'y': pos.get('y', 0) + delta_y,
                    }
                    comp.save()
                    operation.success_count += 1
                
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_resize(
        self,
        component_ids: List[int],
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        anchor: str = 'center'
    ) -> BatchOperation:
        """
        Resize multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'resize',
            component_ids,
            {'scale_x': scale_x, 'scale_y': scale_y, 'anchor': anchor},
            before_state
        )
        
        try:
            with transaction.atomic():
                # Calculate group center for anchor
                all_positions = []
                for comp in components:
                    pos = comp.properties.get('position', {'x': 0, 'y': 0})
                    size = comp.properties.get('size', {'width': 100, 'height': 100})
                    all_positions.append({
                        'x': pos.get('x', 0),
                        'y': pos.get('y', 0),
                        'width': size.get('width', 100),
                        'height': size.get('height', 100),
                    })
                
                if all_positions:
                    center_x = sum(p['x'] + p['width']/2 for p in all_positions) / len(all_positions)
                    center_y = sum(p['y'] + p['height']/2 for p in all_positions) / len(all_positions)
                else:
                    center_x, center_y = 0, 0
                
                for comp in components:
                    pos = comp.properties.get('position', {'x': 0, 'y': 0})
                    size = comp.properties.get('size', {'width': 100, 'height': 100})
                    
                    old_width = size.get('width', 100)
                    old_height = size.get('height', 100)
                    
                    new_width = old_width * scale_x
                    new_height = old_height * scale_y
                    
                    # Adjust position based on anchor
                    if anchor == 'center':
                        old_center_x = pos.get('x', 0) + old_width / 2
                        old_center_y = pos.get('y', 0) + old_height / 2
                        
                        # Scale position relative to group center
                        new_center_x = center_x + (old_center_x - center_x) * scale_x
                        new_center_y = center_y + (old_center_y - center_y) * scale_y
                        
                        comp.properties['position'] = {
                            'x': new_center_x - new_width / 2,
                            'y': new_center_y - new_height / 2,
                        }
                    
                    comp.properties['size'] = {
                        'width': new_width,
                        'height': new_height,
                    }
                    comp.save()
                    operation.success_count += 1
                
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_style(
        self,
        component_ids: List[int],
        style_updates: Dict[str, Any]
    ) -> BatchOperation:
        """
        Apply style changes to multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'style',
            component_ids,
            {'style_updates': style_updates},
            before_state
        )
        
        try:
            with transaction.atomic():
                for comp in components:
                    for key, value in style_updates.items():
                        # Handle nested properties
                        if '.' in key:
                            parts = key.split('.')
                            target = comp.properties
                            for part in parts[:-1]:
                                if part not in target:
                                    target[part] = {}
                                target = target[part]
                            target[parts[-1]] = value
                        else:
                            comp.properties[key] = value
                    
                    comp.save()
                    operation.success_count += 1
                
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_delete(
        self,
        component_ids: List[int]
    ) -> BatchOperation:
        """
        Delete multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'delete',
            component_ids,
            {},
            before_state
        )
        
        try:
            with transaction.atomic():
                deleted_count = DesignComponent.objects.filter(
                    project=self.project,
                    id__in=component_ids
                ).delete()[0]
                
                operation.success_count = deleted_count
                operation.status = 'completed'
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_duplicate(
        self,
        component_ids: List[int],
        offset_x: float = 20,
        offset_y: float = 20
    ) -> BatchOperation:
        """
        Duplicate multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'duplicate',
            component_ids,
            {'offset_x': offset_x, 'offset_y': offset_y},
            before_state
        )
        
        new_component_ids = []
        
        try:
            with transaction.atomic():
                # Get max z_index
                max_z = DesignComponent.objects.filter(
                    project=self.project
                ).order_by('-z_index').values_list('z_index', flat=True).first() or 0
                
                for i, comp in enumerate(components):
                    new_props = copy.deepcopy(comp.properties)
                    
                    # Offset position
                    pos = new_props.get('position', {'x': 0, 'y': 0})
                    new_props['position'] = {
                        'x': pos.get('x', 0) + offset_x,
                        'y': pos.get('y', 0) + offset_y,
                    }
                    
                    new_comp = DesignComponent.objects.create(
                        project=self.project,
                        component_type=comp.component_type,
                        properties=new_props,
                        z_index=max_z + i + 1,
                        ai_generated=comp.ai_generated,
                    )
                    
                    new_component_ids.append(new_comp.id)
                    operation.success_count += 1
                
                operation.status = 'completed'
                operation.after_state = {'new_component_ids': new_component_ids}
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_align(
        self,
        component_ids: List[int],
        alignment: str,  # left, center, right, top, middle, bottom
    ) -> BatchOperation:
        """
        Align multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        if len(components) < 2:
            operation = self._create_operation('align', component_ids, {'alignment': alignment}, {})
            operation.status = 'failed'
            operation.errors = ['Need at least 2 components to align']
            operation.save()
            return operation
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'align',
            component_ids,
            {'alignment': alignment},
            before_state
        )
        
        try:
            with transaction.atomic():
                # Calculate bounds
                positions = []
                for comp in components:
                    pos = comp.properties.get('position', {'x': 0, 'y': 0})
                    size = comp.properties.get('size', {'width': 100, 'height': 100})
                    positions.append({
                        'comp': comp,
                        'x': pos.get('x', 0),
                        'y': pos.get('y', 0),
                        'width': size.get('width', 100),
                        'height': size.get('height', 100),
                    })
                
                min_x = min(p['x'] for p in positions)
                max_x = max(p['x'] + p['width'] for p in positions)
                min_y = min(p['y'] for p in positions)
                max_y = max(p['y'] + p['height'] for p in positions)
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                for p in positions:
                    comp = p['comp']
                    new_pos = comp.properties.get('position', {'x': 0, 'y': 0}).copy()
                    
                    if alignment == 'left':
                        new_pos['x'] = min_x
                    elif alignment == 'center':
                        new_pos['x'] = center_x - p['width'] / 2
                    elif alignment == 'right':
                        new_pos['x'] = max_x - p['width']
                    elif alignment == 'top':
                        new_pos['y'] = min_y
                    elif alignment == 'middle':
                        new_pos['y'] = center_y - p['height'] / 2
                    elif alignment == 'bottom':
                        new_pos['y'] = max_y - p['height']
                    
                    comp.properties['position'] = new_pos
                    comp.save()
                    operation.success_count += 1
                
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_distribute(
        self,
        component_ids: List[int],
        direction: str,  # horizontal, vertical
        spacing: Optional[float] = None  # None = equal spacing
    ) -> BatchOperation:
        """
        Distribute components evenly.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        if len(components) < 3:
            operation = self._create_operation('distribute', component_ids, {'direction': direction}, {})
            operation.status = 'failed'
            operation.errors = ['Need at least 3 components to distribute']
            operation.save()
            return operation
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'distribute',
            component_ids,
            {'direction': direction, 'spacing': spacing},
            before_state
        )
        
        try:
            with transaction.atomic():
                # Sort by position
                if direction == 'horizontal':
                    components.sort(key=lambda c: c.properties.get('position', {}).get('x', 0))
                else:
                    components.sort(key=lambda c: c.properties.get('position', {}).get('y', 0))
                
                # Calculate positions
                first_pos = components[0].properties.get('position', {'x': 0, 'y': 0})
                first_size = components[0].properties.get('size', {'width': 100, 'height': 100})
                last_pos = components[-1].properties.get('position', {'x': 0, 'y': 0})
                
                if direction == 'horizontal':
                    start = first_pos.get('x', 0) + first_size.get('width', 100)
                    end = last_pos.get('x', 0)
                    total_width = sum(
                        c.properties.get('size', {}).get('width', 100)
                        for c in components[1:-1]
                    )
                    available_space = end - start - total_width
                    gap = available_space / (len(components) - 1) if spacing is None else spacing
                    
                    current_x = start + gap
                    for comp in components[1:-1]:
                        size = comp.properties.get('size', {'width': 100, 'height': 100})
                        comp.properties['position']['x'] = current_x
                        current_x += size.get('width', 100) + gap
                        comp.save()
                        operation.success_count += 1
                else:
                    start = first_pos.get('y', 0) + first_size.get('height', 100)
                    end = last_pos.get('y', 0)
                    total_height = sum(
                        c.properties.get('size', {}).get('height', 100)
                        for c in components[1:-1]
                    )
                    available_space = end - start - total_height
                    gap = available_space / (len(components) - 1) if spacing is None else spacing
                    
                    current_y = start + gap
                    for comp in components[1:-1]:
                        size = comp.properties.get('size', {'width': 100, 'height': 100})
                        comp.properties['position']['y'] = current_y
                        current_y += size.get('height', 100) + gap
                        comp.save()
                        operation.success_count += 1
                
                operation.success_count += 2  # First and last don't move but count as success
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def bulk_change_order(
        self,
        component_ids: List[int],
        action: str  # bring_front, send_back, bring_forward, send_backward
    ) -> BatchOperation:
        """
        Change z-order of multiple components.
        """
        from projects.models import DesignComponent
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'order',
            component_ids,
            {'action': action},
            before_state
        )
        
        try:
            with transaction.atomic():
                all_components = list(DesignComponent.objects.filter(
                    project=self.project
                ).order_by('z_index'))
                
                # selected_ids unused
                _ = set(component_ids)
                
                if action == 'bring_front':
                    max_z = len(all_components) - 1
                    for i, comp in enumerate(components):
                        comp.z_index = max_z - len(components) + i + 1
                        comp.save()
                        
                elif action == 'send_back':
                    for i, comp in enumerate(components):
                        comp.z_index = i
                        comp.save()
                        
                elif action in ['bring_forward', 'send_backward']:
                    delta = 1 if action == 'bring_forward' else -1
                    for comp in components:
                        comp.z_index = max(0, comp.z_index + delta)
                        comp.save()
                
                operation.success_count = len(components)
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def find_and_replace(
        self,
        component_ids: List[int],
        property_path: str,
        find_value: Any,
        replace_value: Any,
        use_regex: bool = False
    ) -> BatchOperation:
        """
        Find and replace property values.
        """
        from projects.models import DesignComponent
        import re
        
        components = list(DesignComponent.objects.filter(
            project=self.project,
            id__in=component_ids
        ))
        
        before_state = self._save_state(components)
        operation = self._create_operation(
            'replace',
            component_ids,
            {
                'property_path': property_path,
                'find_value': find_value,
                'replace_value': replace_value,
                'use_regex': use_regex,
            },
            before_state
        )
        
        try:
            with transaction.atomic():
                for comp in components:
                    # Navigate to property
                    parts = property_path.split('.')
                    target = comp.properties
                    
                    for part in parts[:-1]:
                        if part in target:
                            target = target[part]
                        else:
                            continue
                    
                    if parts[-1] in target:
                        current_value = target[parts[-1]]
                        
                        if use_regex and isinstance(current_value, str):
                            new_value = re.sub(find_value, replace_value, current_value)
                            target[parts[-1]] = new_value
                            operation.success_count += 1
                        elif current_value == find_value:
                            target[parts[-1]] = replace_value
                            operation.success_count += 1
                        
                        comp.save()
                
                operation.status = 'completed'
                operation.after_state = self._save_state(components)
                operation.completed_at = timezone.now()
                operation.save()
                
        except Exception as e:
            operation.status = 'failed'
            operation.errors = [str(e)]
            operation.error_count = len(component_ids)
            operation.save()
        
        return operation
    
    def undo(self, operation: BatchOperation) -> bool:
        """
        Undo a batch operation.
        """
        from projects.models import DesignComponent
        
        if operation.status != 'completed':
            return False
        
        try:
            with transaction.atomic():
                if operation.operation_type == 'delete':
                    # Restore deleted components
                    for comp_id, state in operation.before_state.items():
                        DesignComponent.objects.create(
                            id=int(comp_id),
                            project=self.project,
                            component_type=state['component_type'],
                            properties=state['properties'],
                            z_index=state['z_index'],
                        )
                        
                elif operation.operation_type == 'duplicate':
                    # Delete duplicated components
                    new_ids = operation.after_state.get('new_component_ids', [])
                    DesignComponent.objects.filter(
                        project=self.project,
                        id__in=new_ids
                    ).delete()
                    
                else:
                    # Restore previous state
                    for comp_id, state in operation.before_state.items():
                        try:
                            comp = DesignComponent.objects.get(
                                id=int(comp_id),
                                project=self.project
                            )
                            comp.properties = state['properties']
                            comp.z_index = state['z_index']
                            comp.save()
                        except DesignComponent.DoesNotExist:
                            pass
                
                operation.status = 'undone'
                operation.save()
                return True
                
        except Exception:
            return False
    
    def get_operation_history(self, limit: int = 50) -> List[BatchOperation]:
        """
        Get operation history for undo.
        """
        return list(BatchOperation.objects.filter(
            project=self.project,
            user=self.user
        ).order_by('-created_at')[:limit])

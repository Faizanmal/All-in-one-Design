"""
Enhanced Version Control for Projects

Provides visual versioning with thumbnails, diffing capabilities,
branching, and restore functionality.
"""
from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.base import ContentFile
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
import difflib


class ProjectSnapshot(models.Model):
    """
    Complete project snapshot for version history.
    Stores full design data with optional thumbnail.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    
    # Version identification
    version_number = models.IntegerField()
    version_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional label like 'v1.0', 'Final', 'Before refactor'"
    )
    
    # Snapshot data
    design_data = models.JSONField(
        help_text="Complete design state at this version"
    )
    canvas_settings = models.JSONField(
        default=dict,
        help_text="Canvas width, height, background at this version"
    )
    components_count = models.IntegerField(default=0)
    
    # Hash for quick comparison
    content_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash of design_data for quick comparison"
    )
    
    # Thumbnail
    thumbnail = models.ImageField(
        upload_to='version_thumbnails/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Size tracking
    data_size_bytes = models.IntegerField(
        default=0,
        help_text="Size of design_data in bytes"
    )
    
    # Change metadata
    change_summary = models.TextField(
        blank=True,
        help_text="AI-generated or user-provided summary of changes"
    )
    change_type = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Save'),
            ('auto', 'Auto Save'),
            ('restore', 'Restored Version'),
            ('branch', 'Branched Version'),
            ('merge', 'Merged Version'),
            ('ai_generated', 'AI Generated'),
            ('import', 'Imported'),
        ],
        default='manual'
    )
    
    # Author
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_snapshots'
    )
    
    # Branch support
    parent_snapshot = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_snapshots'
    )
    branch_name = models.CharField(
        max_length=100,
        default='main',
        help_text="Branch name for this version"
    )
    is_branch_head = models.BooleanField(
        default=False,
        help_text="Is this the latest version in its branch?"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
        unique_together = ['project', 'version_number']
        indexes = [
            models.Index(fields=['project', 'branch_name', '-version_number']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['created_by', '-created_at']),
        ]
    
    def __str__(self):
        label = f" ({self.version_label})" if self.version_label else ""
        return f"{self.project.name} v{self.version_number}{label}"
    
    def save(self, *args, **kwargs):
        # Calculate content hash
        if self.design_data:
            data_str = json.dumps(self.design_data, sort_keys=True)
            self.content_hash = hashlib.sha256(data_str.encode()).hexdigest()
            self.data_size_bytes = len(data_str.encode())
        
        super().save(*args, **kwargs)
    
    def is_identical_to(self, other: 'ProjectSnapshot') -> bool:
        """Check if this snapshot is identical to another."""
        return self.content_hash == other.content_hash


class VersionDiff(models.Model):
    """
    Cached diff between two versions for quick retrieval.
    """
    from_snapshot = models.ForeignKey(
        ProjectSnapshot,
        on_delete=models.CASCADE,
        related_name='diffs_from'
    )
    to_snapshot = models.ForeignKey(
        ProjectSnapshot,
        on_delete=models.CASCADE,
        related_name='diffs_to'
    )
    
    # Diff data
    diff_data = models.JSONField(
        help_text="Structured diff information"
    )
    
    # Summary stats
    components_added = models.IntegerField(default=0)
    components_removed = models.IntegerField(default=0)
    components_modified = models.IntegerField(default=0)
    properties_changed = models.IntegerField(default=0)
    
    # Computed at
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_snapshot', 'to_snapshot']
    
    def __str__(self):
        return f"Diff: v{self.from_snapshot.version_number} → v{self.to_snapshot.version_number}"


class VersionComment(models.Model):
    """
    Comments on specific versions for collaboration.
    """
    snapshot = models.ForeignKey(
        ProjectSnapshot,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='version_comments'
    )
    
    content = models.TextField()
    
    # Optional reference to specific component
    component_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="ID of component being commented on"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on v{self.snapshot.version_number}"


class VersionService:
    """
    Service for managing project versions and computing diffs.
    """
    
    def __init__(self, project):
        self.project = project
    
    def create_snapshot(
        self,
        user: User,
        label: str = '',
        change_summary: str = '',
        change_type: str = 'manual',
        branch_name: str = 'main',
        parent_snapshot: Optional[ProjectSnapshot] = None,
    ) -> ProjectSnapshot:
        """
        Create a new snapshot of the current project state.
        """
        from projects.models import DesignComponent
        
        # Get next version number
        last_snapshot = self.project.snapshots.order_by('-version_number').first()
        next_version = (last_snapshot.version_number + 1) if last_snapshot else 1
        
        # Mark previous head as not head
        self.project.snapshots.filter(
            branch_name=branch_name,
            is_branch_head=True
        ).update(is_branch_head=False)
        
        # Get current design data
        components = DesignComponent.objects.filter(project=self.project)
        components_data = [
            {
                'id': str(c.id),
                'type': c.component_type,
                'properties': c.properties,
                'z_index': c.z_index,
                'ai_generated': c.ai_generated,
            }
            for c in components
        ]
        
        design_data = {
            'components': components_data,
            'project_settings': {
                'name': self.project.name,
                'description': self.project.description,
                'project_type': self.project.project_type,
            },
            'ai_metadata': {
                'prompt': self.project.ai_prompt,
                'color_palette': self.project.color_palette,
                'suggested_fonts': self.project.suggested_fonts,
            }
        }
        
        canvas_settings = {
            'width': self.project.canvas_width,
            'height': self.project.canvas_height,
            'background': self.project.canvas_background,
        }
        
        # Auto-generate change summary if not provided
        if not change_summary and last_snapshot:
            change_summary = self._generate_change_summary(
                last_snapshot.design_data,
                design_data
            )
        
        snapshot = ProjectSnapshot.objects.create(
            project=self.project,
            version_number=next_version,
            version_label=label,
            design_data=design_data,
            canvas_settings=canvas_settings,
            components_count=len(components_data),
            change_summary=change_summary,
            change_type=change_type,
            created_by=user,
            parent_snapshot=parent_snapshot or last_snapshot,
            branch_name=branch_name,
            is_branch_head=True,
        )
        
        return snapshot
    
    def restore_snapshot(
        self,
        snapshot: ProjectSnapshot,
        user: User,
        create_backup: bool = True
    ) -> ProjectSnapshot:
        """
        Restore project to a previous snapshot state.
        Returns the new snapshot created after restore.
        """
        from projects.models import DesignComponent
        
        with transaction.atomic():
            # Optionally create backup of current state
            if create_backup:
                self.create_snapshot(
                    user=user,
                    label=f"Before restore to v{snapshot.version_number}",
                    change_type='auto',
                    change_summary=f"Auto-backup before restoring to version {snapshot.version_number}"
                )
            
            # Clear current components
            DesignComponent.objects.filter(project=self.project).delete()
            
            # Restore components from snapshot
            components_data = snapshot.design_data.get('components', [])
            for comp_data in components_data:
                DesignComponent.objects.create(
                    project=self.project,
                    component_type=comp_data['type'],
                    properties=comp_data['properties'],
                    z_index=comp_data.get('z_index', 0),
                    ai_generated=comp_data.get('ai_generated', False),
                )
            
            # Restore canvas settings
            canvas = snapshot.canvas_settings
            self.project.canvas_width = canvas.get('width', self.project.canvas_width)
            self.project.canvas_height = canvas.get('height', self.project.canvas_height)
            self.project.canvas_background = canvas.get('background', self.project.canvas_background)
            
            # Restore AI metadata
            ai_meta = snapshot.design_data.get('ai_metadata', {})
            self.project.ai_prompt = ai_meta.get('prompt', '')
            self.project.color_palette = ai_meta.get('color_palette', [])
            self.project.suggested_fonts = ai_meta.get('suggested_fonts', [])
            
            self.project.save()
            
            # Create restore snapshot
            restore_snapshot = self.create_snapshot(
                user=user,
                label=f"Restored from v{snapshot.version_number}",
                change_type='restore',
                change_summary=f"Restored project to version {snapshot.version_number}"
            )
            
            return restore_snapshot
    
    def create_branch(
        self,
        from_snapshot: ProjectSnapshot,
        branch_name: str,
        user: User
    ) -> ProjectSnapshot:
        """
        Create a new branch from an existing snapshot.
        """
        # Check if branch already exists
        if self.project.snapshots.filter(branch_name=branch_name).exists():
            raise ValueError(f"Branch '{branch_name}' already exists")
        
        # Create new snapshot as branch head
        return self.create_snapshot(
            user=user,
            label=f"Branch: {branch_name}",
            change_type='branch',
            change_summary=f"Created branch '{branch_name}' from v{from_snapshot.version_number}",
            branch_name=branch_name,
            parent_snapshot=from_snapshot,
        )
    
    def get_diff(
        self,
        from_snapshot: ProjectSnapshot,
        to_snapshot: ProjectSnapshot,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get diff between two snapshots.
        """
        # Try to get cached diff
        if use_cache:
            try:
                cached = VersionDiff.objects.get(
                    from_snapshot=from_snapshot,
                    to_snapshot=to_snapshot
                )
                return cached.diff_data
            except VersionDiff.DoesNotExist:
                pass
        
        # Compute diff
        diff_data = self._compute_diff(
            from_snapshot.design_data,
            to_snapshot.design_data
        )
        
        # Cache the diff
        if use_cache:
            VersionDiff.objects.create(
                from_snapshot=from_snapshot,
                to_snapshot=to_snapshot,
                diff_data=diff_data,
                components_added=len(diff_data.get('added', [])),
                components_removed=len(diff_data.get('removed', [])),
                components_modified=len(diff_data.get('modified', [])),
                properties_changed=diff_data.get('total_property_changes', 0),
            )
        
        return diff_data
    
    def _compute_diff(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute detailed diff between two design data objects.
        """
        old_components = {c['id']: c for c in old_data.get('components', [])}
        new_components = {c['id']: c for c in new_data.get('components', [])}
        
        old_ids = set(old_components.keys())
        new_ids = set(new_components.keys())
        
        added_ids = new_ids - old_ids
        removed_ids = old_ids - new_ids
        common_ids = old_ids & new_ids
        
        added = [new_components[id] for id in added_ids]
        removed = [old_components[id] for id in removed_ids]
        
        modified = []
        total_property_changes = 0
        
        for comp_id in common_ids:
            old_comp = old_components[comp_id]
            new_comp = new_components[comp_id]
            
            if old_comp != new_comp:
                changes = self._diff_component(old_comp, new_comp)
                if changes:
                    modified.append({
                        'id': comp_id,
                        'type': new_comp['type'],
                        'changes': changes
                    })
                    total_property_changes += len(changes)
        
        # Diff canvas settings
        old_settings = old_data.get('project_settings', {})
        new_settings = new_data.get('project_settings', {})
        settings_changes = self._diff_dict(old_settings, new_settings)
        
        return {
            'added': added,
            'removed': removed,
            'modified': modified,
            'settings_changes': settings_changes,
            'total_property_changes': total_property_changes,
            'summary': {
                'added_count': len(added),
                'removed_count': len(removed),
                'modified_count': len(modified),
            }
        }
    
    def _diff_component(
        self,
        old_comp: Dict[str, Any],
        new_comp: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get property-level differences between two components.
        """
        changes = []
        
        old_props = old_comp.get('properties', {})
        new_props = new_comp.get('properties', {})
        
        all_keys = set(old_props.keys()) | set(new_props.keys())
        
        for key in all_keys:
            old_val = old_props.get(key)
            new_val = new_props.get(key)
            
            if old_val != new_val:
                changes.append({
                    'property': key,
                    'old_value': old_val,
                    'new_value': new_val,
                    'type': 'modified' if key in old_props and key in new_props
                           else 'added' if key not in old_props
                           else 'removed'
                })
        
        # Check z_index
        if old_comp.get('z_index') != new_comp.get('z_index'):
            changes.append({
                'property': 'z_index',
                'old_value': old_comp.get('z_index'),
                'new_value': new_comp.get('z_index'),
                'type': 'modified'
            })
        
        return changes
    
    def _diff_dict(
        self,
        old_dict: Dict[str, Any],
        new_dict: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Get differences between two dictionaries.
        """
        changes = []
        all_keys = set(old_dict.keys()) | set(new_dict.keys())
        
        for key in all_keys:
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            
            if old_val != new_val:
                changes.append({
                    'key': key,
                    'old_value': old_val,
                    'new_value': new_val,
                })
        
        return changes
    
    def _generate_change_summary(
        self,
        old_data: Dict[str, Any],
        new_data: Dict[str, Any]
    ) -> str:
        """
        Auto-generate a human-readable change summary.
        """
        diff = self._compute_diff(old_data, new_data)
        
        parts = []
        
        if diff['summary']['added_count'] > 0:
            parts.append(f"Added {diff['summary']['added_count']} component(s)")
        
        if diff['summary']['removed_count'] > 0:
            parts.append(f"Removed {diff['summary']['removed_count']} component(s)")
        
        if diff['summary']['modified_count'] > 0:
            parts.append(f"Modified {diff['summary']['modified_count']} component(s)")
        
        if diff['settings_changes']:
            parts.append(f"Updated {len(diff['settings_changes'])} setting(s)")
        
        if not parts:
            return "No changes detected"
        
        return "; ".join(parts)
    
    def get_branches(self) -> List[Dict[str, Any]]:
        """
        Get all branches for this project.
        """
        branches = self.project.snapshots.values('branch_name').distinct()
        
        result = []
        for branch in branches:
            branch_name = branch['branch_name']
            head = self.project.snapshots.filter(
                branch_name=branch_name,
                is_branch_head=True
            ).first()
            
            snapshot_count = self.project.snapshots.filter(
                branch_name=branch_name
            ).count()
            
            result.append({
                'name': branch_name,
                'head_version': head.version_number if head else None,
                'head_label': head.version_label if head else None,
                'snapshot_count': snapshot_count,
                'last_updated': head.created_at.isoformat() if head else None,
            })
        
        return result
    
    def get_history(
        self,
        branch_name: str = None,
        limit: int = 50,
        include_diff: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get version history for the project.
        """
        queryset = self.project.snapshots.select_related('created_by')
        
        if branch_name:
            queryset = queryset.filter(branch_name=branch_name)
        
        snapshots = queryset.order_by('-version_number')[:limit]
        
        history = []
        prev_snapshot = None
        
        for snapshot in snapshots:
            entry = {
                'version': snapshot.version_number,
                'label': snapshot.version_label,
                'change_type': snapshot.change_type,
                'change_summary': snapshot.change_summary,
                'components_count': snapshot.components_count,
                'branch': snapshot.branch_name,
                'created_by': snapshot.created_by.username if snapshot.created_by else None,
                'created_at': snapshot.created_at.isoformat(),
                'thumbnail_url': snapshot.thumbnail.url if snapshot.thumbnail else None,
            }
            
            if include_diff and prev_snapshot:
                entry['diff_summary'] = self.get_diff(snapshot, prev_snapshot).get('summary')
            
            history.append(entry)
            prev_snapshot = snapshot
        
        return history

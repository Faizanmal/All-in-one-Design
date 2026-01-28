"""
Services for Design Branches app.

Core engine for branching operations and version control.
"""
import hashlib
import json
from typing import Optional, Dict, Any
from django.utils import timezone
from django.db import transaction

from .models import (
    DesignBranch, DesignCommit, BranchMerge, MergeConflict, BranchComparison
)


class BranchingService:
    """
    Service for handling branching operations.
    Implements Git-like version control for design files.
    """
    
    def __init__(self, branch: DesignBranch):
        self.branch = branch
    
    def create_commit(
        self,
        author,
        message: str,
        description: str = '',
        snapshot_data: Dict[str, Any] = None,
    ) -> DesignCommit:
        """Create a new commit on the branch."""
        snapshot_data = snapshot_data or {}
        
        # Get parent commit (current head)
        parent = self.branch.head_commit
        
        # Calculate diff if parent exists
        diff_data = {}
        files_changed = 0
        insertions = 0
        deletions = 0
        
        if parent and parent.snapshot_data:
            diff_data, files_changed, insertions, deletions = self._calculate_diff(
                parent.snapshot_data, snapshot_data
            )
        else:
            files_changed = len(snapshot_data.get('nodes', []))
            insertions = files_changed
        
        # Generate commit SHA
        commit_sha = self._generate_sha(snapshot_data, message, parent)
        
        # Create commit
        with transaction.atomic():
            commit = DesignCommit.objects.create(
                branch=self.branch,
                commit_sha=commit_sha,
                parent=parent,
                message=message,
                description=description,
                snapshot_data=snapshot_data,
                diff_data=diff_data,
                author=author,
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
            )
            
            # Update branch head
            self.branch.head_commit = commit
            self.branch.updated_at = timezone.now()
            self.branch.save()
        
        return commit
    
    def _generate_sha(
        self,
        snapshot_data: Dict,
        message: str,
        parent: Optional[DesignCommit]
    ) -> str:
        """Generate SHA hash for commit."""
        data = {
            'snapshot': json.dumps(snapshot_data, sort_keys=True),
            'message': message,
            'parent': str(parent.commit_sha) if parent else '',
            'timestamp': timezone.now().isoformat(),
        }
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:40]
    
    def _calculate_diff(
        self,
        old_snapshot: Dict,
        new_snapshot: Dict
    ) -> tuple:
        """Calculate diff between two snapshots."""
        diff_data = {
            'added': [],
            'modified': [],
            'deleted': [],
        }
        
        old_nodes = {n.get('id'): n for n in old_snapshot.get('nodes', [])}
        new_nodes = {n.get('id'): n for n in new_snapshot.get('nodes', [])}
        
        # Find added and modified
        for node_id, node in new_nodes.items():
            if node_id not in old_nodes:
                diff_data['added'].append({
                    'id': node_id,
                    'type': node.get('type'),
                    'name': node.get('name'),
                })
            elif node != old_nodes[node_id]:
                diff_data['modified'].append({
                    'id': node_id,
                    'type': node.get('type'),
                    'name': node.get('name'),
                    'changes': self._get_changes(old_nodes[node_id], node),
                })
        
        # Find deleted
        for node_id, node in old_nodes.items():
            if node_id not in new_nodes:
                diff_data['deleted'].append({
                    'id': node_id,
                    'type': node.get('type'),
                    'name': node.get('name'),
                })
        
        files_changed = (
            len(diff_data['added']) +
            len(diff_data['modified']) +
            len(diff_data['deleted'])
        )
        insertions = len(diff_data['added'])
        deletions = len(diff_data['deleted'])
        
        return diff_data, files_changed, insertions, deletions
    
    def _get_changes(self, old_node: Dict, new_node: Dict) -> list:
        """Get list of changed properties between nodes."""
        changes = []
        all_keys = set(old_node.keys()) | set(new_node.keys())
        
        for key in all_keys:
            if key in ['id', 'children']:
                continue
            if old_node.get(key) != new_node.get(key):
                changes.append({
                    'property': key,
                    'old_value': old_node.get(key),
                    'new_value': new_node.get(key),
                })
        
        return changes
    
    def create_child_branch(
        self,
        name: str,
        description: str,
        branch_type: str,
        created_by,
        from_commit_id: Optional[str] = None,
    ) -> DesignBranch:
        """Create a new branch from this branch."""
        # Determine base commit
        if from_commit_id:
            base_commit = DesignCommit.objects.get(id=from_commit_id, branch=self.branch)
        else:
            base_commit = self.branch.head_commit
        
        with transaction.atomic():
            new_branch = DesignBranch.objects.create(
                project=self.branch.project,
                name=name,
                description=description,
                branch_type=branch_type,
                parent_branch=self.branch,
                base_commit=base_commit,
                head_commit=base_commit,
                created_by=created_by,
            )
        
        return new_branch
    
    def merge_into(
        self,
        target_branch: DesignBranch,
        merged_by,
        strategy: str = 'merge',
        squash_message: str = '',
        auto_resolve: bool = False,
    ) -> BranchMerge:
        """Merge this branch into target branch."""
        with transaction.atomic():
            # Create merge record
            merge = BranchMerge.objects.create(
                source_branch=self.branch,
                target_branch=target_branch,
                merge_strategy=strategy,
                status='in_progress',
                squash_message=squash_message,
                auto_resolve_conflicts=auto_resolve,
            )
            
            # Detect conflicts
            conflicts = self._detect_conflicts(target_branch)
            
            if conflicts:
                merge.status = 'conflicts'
                merge.save()
                
                for conflict in conflicts:
                    MergeConflict.objects.create(
                        merge=merge,
                        node_id=conflict['node_id'],
                        node_type=conflict['node_type'],
                        node_name=conflict['node_name'],
                        source_value=conflict['source_value'],
                        target_value=conflict['target_value'],
                        conflict_type=conflict['conflict_type'],
                    )
            else:
                # No conflicts, complete merge
                self.complete_merge(merge, merged_by)
        
        return merge
    
    def _detect_conflicts(self, target_branch: DesignBranch) -> list:
        """Detect merge conflicts between branches."""
        conflicts = []
        
        source_snapshot = self.branch.head_commit.snapshot_data if self.branch.head_commit else {}
        target_snapshot = target_branch.head_commit.snapshot_data if target_branch.head_commit else {}
        
        source_nodes = {n.get('id'): n for n in source_snapshot.get('nodes', [])}
        target_nodes = {n.get('id'): n for n in target_snapshot.get('nodes', [])}
        
        # Check for nodes modified in both branches
        for node_id in set(source_nodes.keys()) & set(target_nodes.keys()):
            source_node = source_nodes[node_id]
            target_node = target_nodes[node_id]
            
            if source_node != target_node:
                # Check if same properties were modified
                for key in set(source_node.keys()) & set(target_node.keys()):
                    if key in ['id', 'children']:
                        continue
                    if source_node.get(key) != target_node.get(key):
                        conflicts.append({
                            'node_id': node_id,
                            'node_type': source_node.get('type'),
                            'node_name': source_node.get('name'),
                            'source_value': {key: source_node.get(key)},
                            'target_value': {key: target_node.get(key)},
                            'conflict_type': 'property',
                        })
        
        return conflicts
    
    def complete_merge(self, merge: BranchMerge, merged_by) -> None:
        """Complete a merge after conflicts are resolved."""
        with transaction.atomic():
            # Build merged snapshot
            merged_snapshot = self._build_merged_snapshot(merge)
            
            # Create merge commit on target branch
            target_service = BranchingService(merge.target_branch)
            
            if merge.merge_strategy == 'squash':
                message = merge.squash_message or f"Merge branch '{self.branch.name}'"
            else:
                message = f"Merge branch '{self.branch.name}' into {merge.target_branch.name}"
            
            commit = target_service.create_commit(
                author=merged_by,
                message=message,
                snapshot_data=merged_snapshot,
            )
            
            # Update merge record
            merge.merge_commit = commit
            merge.merged_by = merged_by
            merge.merged_at = timezone.now()
            merge.status = 'completed'
            merge.save()
            
            # Update source branch status
            self.branch.status = 'merged'
            self.branch.merged_at = timezone.now()
            self.branch.save()
    
    def _build_merged_snapshot(self, merge: BranchMerge) -> Dict:
        """Build merged snapshot from resolved conflicts."""
        source_snapshot = self.branch.head_commit.snapshot_data if self.branch.head_commit else {}
        target_snapshot = merge.target_branch.head_commit.snapshot_data if merge.target_branch.head_commit else {}
        
        # Start with target snapshot
        merged = dict(target_snapshot)
        merged_nodes = {n.get('id'): n for n in merged.get('nodes', [])}
        
        # Apply source changes
        source_nodes = {n.get('id'): n for n in source_snapshot.get('nodes', [])}
        
        for node_id, node in source_nodes.items():
            if node_id not in merged_nodes:
                # Add new nodes from source
                merged_nodes[node_id] = node
        
        # Apply conflict resolutions
        for conflict in merge.conflicts.exclude(resolution='pending'):
            if conflict.resolved_value:
                node = merged_nodes.get(conflict.node_id, {})
                node.update(conflict.resolved_value)
                merged_nodes[conflict.node_id] = node
        
        merged['nodes'] = list(merged_nodes.values())
        return merged
    
    def compare_with(self, other_branch: DesignBranch) -> BranchComparison:
        """Compare this branch with another."""
        # Check for existing recent comparison
        existing = BranchComparison.objects.filter(
            base_branch=self.branch,
            compare_branch=other_branch,
            expires_at__gt=timezone.now(),
        ).first()
        
        if existing:
            return existing
        
        # Generate comparison
        base_snapshot = self.branch.head_commit.snapshot_data if self.branch.head_commit else {}
        compare_snapshot = other_branch.head_commit.snapshot_data if other_branch.head_commit else {}
        
        base_nodes = {n.get('id'): n for n in base_snapshot.get('nodes', [])}
        compare_nodes = {n.get('id'): n for n in compare_snapshot.get('nodes', [])}
        
        nodes_added = []
        nodes_modified = []
        nodes_deleted = []
        conflict_nodes = []
        
        # Find added and modified
        for node_id, node in compare_nodes.items():
            if node_id not in base_nodes:
                nodes_added.append(node_id)
            elif node != base_nodes[node_id]:
                nodes_modified.append(node_id)
                # Check for potential conflicts
                for key in set(node.keys()) & set(base_nodes[node_id].keys()):
                    if key not in ['id', 'children'] and node.get(key) != base_nodes[node_id].get(key):
                        conflict_nodes.append(node_id)
                        break
        
        # Find deleted
        for node_id in base_nodes:
            if node_id not in compare_nodes:
                nodes_deleted.append(node_id)
        
        comparison = BranchComparison.objects.create(
            base_branch=self.branch,
            compare_branch=other_branch,
            diff_summary={
                'added': nodes_added,
                'modified': nodes_modified,
                'deleted': nodes_deleted,
            },
            nodes_added=len(nodes_added),
            nodes_modified=len(nodes_modified),
            nodes_deleted=len(nodes_deleted),
            has_conflicts=len(conflict_nodes) > 0,
            conflict_nodes=conflict_nodes,
        )
        
        return comparison
    
    def cherry_pick(self, commit: DesignCommit, author) -> DesignCommit:
        """Cherry-pick a commit to this branch."""
        return self.create_commit(
            author=author,
            message=f"Cherry-pick: {commit.message}",
            description=f"Cherry-picked from {commit.branch.name} ({commit.commit_sha[:8]})",
            snapshot_data=commit.snapshot_data,
        )

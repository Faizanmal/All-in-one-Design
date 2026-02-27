"""
Version control service with branching, merging, and diff capabilities
"""
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
from django.contrib.auth.models import User
from .version_control_models import (
    VersionBranch,
    VersionCommit,
    MergeRequest,
    VersionTag,
    VersionDiff
)
from .models import Project


class VersionControlService:
    """
    Service for version control operations
    """
    
    @staticmethod
    def create_branch(
        project: Project,
        name: str,
        user: User,
        parent_branch: Optional[VersionBranch] = None,
        description: str = ""
    ) -> VersionBranch:
        """Create a new branch"""
        branch = VersionBranch.objects.create(
            project=project,
            name=name,
            description=description,
            parent_branch=parent_branch,
            created_by=user,
            is_main=(name == 'main' and not parent_branch)
        )
        
        # Create initial commit if parent branch exists
        if parent_branch:
            latest_commit = parent_branch.commits.first()
            if latest_commit:
                VersionControlService.create_commit(
                    branch=branch,
                    project=project,
                    user=user,
                    message=f"Branch created from {parent_branch.name}",
                    design_data=latest_commit.design_data,
                    canvas_config=latest_commit.canvas_config,
                    parent_commit=latest_commit
                )
        
        return branch
    
    @staticmethod
    def create_commit(
        branch: VersionBranch,
        project: Project,
        user: User,
        message: str,
        design_data: Dict,
        canvas_config: Optional[Dict] = None,
        parent_commit: Optional[VersionCommit] = None,
        tags: Optional[List[str]] = None
    ) -> VersionCommit:
        """Create a new commit"""
        # Generate commit hash
        commit_content = json.dumps({
            'branch': branch.id,
            'user': user.id,
            'timestamp': datetime.now().isoformat(),
            'design_data': design_data
        }, sort_keys=True)
        commit_hash = hashlib.sha1(commit_content.encode()).hexdigest()
        
        # Calculate changes
        changes_summary = {}
        if parent_commit:
            changes_summary = VersionControlService._calculate_changes(
                parent_commit.design_data,
                design_data
            )
        
        # Create commit
        commit = VersionCommit.objects.create(
            branch=branch,
            project=project,
            commit_hash=commit_hash,
            message=message,
            author=user,
            design_data=design_data,
            canvas_config=canvas_config or {},
            parent_commit=parent_commit,
            changes_summary=changes_summary,
            tags=tags or []
        )
        
        # Update project's current design_data if this is the main branch
        if branch.is_main:
            project.design_data = design_data
            if canvas_config:
                project.canvas_width = canvas_config.get('width', project.canvas_width)
                project.canvas_height = canvas_config.get('height', project.canvas_height)
                project.canvas_background = canvas_config.get('background', project.canvas_background)
            project.save()
        
        return commit
    
    @staticmethod
    def _calculate_changes(old_data: Dict, new_data: Dict) -> Dict:
        """Calculate changes between two design data versions"""
        old_elements = {e.get('id'): e for e in old_data.get('elements', [])}
        new_elements = {e.get('id'): e for e in new_data.get('elements', [])}
        
        old_ids = set(old_elements.keys())
        new_ids = set(new_elements.keys())
        
        added = len(new_ids - old_ids)
        deleted = len(old_ids - new_ids)
        
        # Check for modifications
        modified = 0
        properties_changed = set()
        for elem_id in old_ids & new_ids:
            old_elem = old_elements[elem_id]
            new_elem = new_elements[elem_id]
            if old_elem != new_elem:
                modified += 1
                # Track which properties changed
                for key in set(old_elem.keys()) | set(new_elem.keys()):
                    if old_elem.get(key) != new_elem.get(key):
                        properties_changed.add(key)
        
        return {
            'elements_added': added,
            'elements_modified': modified,
            'elements_deleted': deleted,
            'properties_changed': list(properties_changed)
        }
    
    @staticmethod
    def get_commit_history(
        branch: VersionBranch,
        limit: Optional[int] = None
    ) -> List[VersionCommit]:
        """Get commit history for a branch"""
        commits = branch.commits.select_related('author').order_by('-created_at')
        if limit:
            commits = commits[:limit]
        return list(commits)
    
    @staticmethod
    def restore_commit(
        commit: VersionCommit,
        user: User,
        create_new_commit: bool = True
    ) -> Optional[VersionCommit]:
        """Restore a project to a specific commit"""
        project = commit.project
        
        if create_new_commit:
            # Create a new commit with the restored data
            return VersionControlService.create_commit(
                branch=commit.branch,
                project=project,
                user=user,
                message=f"Restored from commit {commit.commit_hash[:8]}",
                design_data=commit.design_data,
                canvas_config=commit.canvas_config,
                parent_commit=commit.branch.commits.first()
            )
        else:
            # Directly update project
            project.design_data = commit.design_data
            project.canvas_width = commit.canvas_config.get('width', project.canvas_width)
            project.canvas_height = commit.canvas_config.get('height', project.canvas_height)
            project.canvas_background = commit.canvas_config.get('background', project.canvas_background)
            project.save()
            return None
    
    @staticmethod
    def create_merge_request(
        project: Project,
        source_branch: VersionBranch,
        target_branch: VersionBranch,
        user: User,
        title: str,
        description: str = ""
    ) -> MergeRequest:
        """Create a merge request"""
        # Check for conflicts
        source_commit = source_branch.commits.first()
        target_commit = target_branch.commits.first()
        
        has_conflicts, conflicts_data = VersionControlService._check_conflicts(
            source_commit,
            target_commit
        )
        
        merge_request = MergeRequest.objects.create(
            project=project,
            source_branch=source_branch,
            target_branch=target_branch,
            title=title,
            description=description,
            created_by=user,
            has_conflicts=has_conflicts,
            conflicts_data=conflicts_data
        )
        
        return merge_request
    
    @staticmethod
    def _check_conflicts(
        source_commit: Optional[VersionCommit],
        target_commit: Optional[VersionCommit]
    ) -> tuple[bool, Dict]:
        """Check for merge conflicts between commits"""
        if not source_commit or not target_commit:
            return False, {}
        
        source_elements = {e.get('id'): e for e in source_commit.design_data.get('elements', [])}
        target_elements = {e.get('id'): e for e in target_commit.design_data.get('elements', [])}
        
        conflicts = []
        common_ids = set(source_elements.keys()) & set(target_elements.keys())
        
        for elem_id in common_ids:
            source_elem = source_elements[elem_id]
            target_elem = target_elements[elem_id]
            
            # Check if element was modified in both branches
            if source_elem != target_elem:
                conflicts.append({
                    'element_id': elem_id,
                    'source_version': source_elem,
                    'target_version': target_elem,
                    'conflict_type': 'modification'
                })
        
        has_conflicts = len(conflicts) > 0
        conflicts_data = {
            'conflicts': conflicts,
            'count': len(conflicts)
        }
        
        return has_conflicts, conflicts_data
    
    @staticmethod
    def merge_branches(
        merge_request: MergeRequest,
        user: User,
        resolution_data: Optional[Dict] = None
    ) -> VersionCommit:
        """Merge source branch into target branch"""
        source_commit = merge_request.source_branch.commits.first()
        target_commit = merge_request.target_branch.commits.first()
        
        if merge_request.has_conflicts and not resolution_data:
            raise ValueError("Conflicts must be resolved before merging")
        
        # Merge design data
        merged_data = VersionControlService._merge_design_data(
            source_commit.design_data,
            target_commit.design_data,
            resolution_data
        )
        
        # Create merge commit
        merge_commit = VersionControlService.create_commit(
            branch=merge_request.target_branch,
            project=merge_request.project,
            user=user,
            message=f"Merge {merge_request.source_branch.name} into {merge_request.target_branch.name}",
            design_data=merged_data,
            canvas_config=target_commit.canvas_config,
            parent_commit=target_commit,
            tags=['merge']
        )
        
        # Update merge request
        merge_request.status = 'merged'
        merge_request.merged_by = user
        merge_request.merged_at = datetime.now()
        merge_request.merge_commit = merge_commit
        merge_request.resolution_data = resolution_data or {}
        merge_request.save()
        
        return merge_commit
    
    @staticmethod
    def _merge_design_data(
        source_data: Dict,
        target_data: Dict,
        resolution_data: Optional[Dict] = None
    ) -> Dict:
        """Merge two design data dictionaries"""
        merged = target_data.copy()
        
        source_elements = {e.get('id'): e for e in source_data.get('elements', [])}
        target_elements = {e.get('id'): e for e in target_data.get('elements', [])}
        
        # Start with target elements
        merged_elements = list(target_elements.values())
        
        # Add new elements from source
        for elem_id, elem in source_elements.items():
            if elem_id not in target_elements:
                merged_elements.append(elem)
            elif resolution_data and elem_id in resolution_data.get('resolutions', {}):
                # Apply conflict resolution
                resolution = resolution_data['resolutions'][elem_id]
                if resolution == 'source':
                    # Replace with source version
                    merged_elements = [e if e.get('id') != elem_id else elem for e in merged_elements]
        
        merged['elements'] = merged_elements
        return merged
    
    @staticmethod
    def create_tag(
        commit: VersionCommit,
        user: User,
        name: str,
        tag_type: str = 'milestone',
        description: str = ""
    ) -> VersionTag:
        """Create a named tag for a commit"""
        tag = VersionTag.objects.create(
            project=commit.project,
            commit=commit,
            name=name,
            description=description,
            tag_type=tag_type,
            created_by=user
        )
        return tag
    
    @staticmethod
    def compute_diff(
        from_commit: VersionCommit,
        to_commit: VersionCommit
    ) -> VersionDiff:
        """Compute and store diff between two commits"""
        # Check if diff already exists
        existing_diff = VersionDiff.objects.filter(
            from_commit=from_commit,
            to_commit=to_commit
        ).first()
        
        if existing_diff:
            return existing_diff
        
        # Compute diff
        from_elements = {e.get('id'): e for e in from_commit.design_data.get('elements', [])}
        to_elements = {e.get('id'): e for e in to_commit.design_data.get('elements', [])}
        
        from_ids = set(from_elements.keys())
        to_ids = set(to_elements.keys())
        
        added = [to_elements[eid] for eid in (to_ids - from_ids)]
        deleted = [from_elements[eid] for eid in (from_ids - to_ids)]
        
        modified = []
        for elem_id in from_ids & to_ids:
            if from_elements[elem_id] != to_elements[elem_id]:
                modified.append({
                    'element_id': elem_id,
                    'from': from_elements[elem_id],
                    'to': to_elements[elem_id]
                })
        
        diff_data = {
            'added': added,
            'modified': modified,
            'deleted': deleted,
            'summary': f"{len(added)} added, {len(modified)} modified, {len(deleted)} deleted"
        }
        
        # Store diff
        diff = VersionDiff.objects.create(
            project=from_commit.project,
            from_commit=from_commit,
            to_commit=to_commit,
            diff_data=diff_data
        )
        
        return diff

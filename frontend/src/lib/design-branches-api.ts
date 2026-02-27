/**
 * Design Branches API Client
 * Production-ready API for Branching & Feature Branches feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/branches`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type BranchStatus = 'active' | 'merged' | 'closed' | 'archived';
export type ReviewStatus = 'pending' | 'approved' | 'changes_requested' | 'dismissed';
export type MergeStrategy = 'merge' | 'squash' | 'rebase';
export type ConflictResolution = 'keep_source' | 'keep_target' | 'manual' | 'merge_styles';

export interface DesignCommit {
  id: string;
  branch: string;
  author: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  message: string;
  description: string;
  snapshot_data: Record<string, unknown>;
  file_changes: Array<{
    path: string;
    change_type: 'added' | 'modified' | 'deleted';
    diff_summary?: string;
  }>;
  parent_commit: string | null;
  commit_hash: string;
  is_merge_commit: boolean;
  merge_source_branch: string | null;
  stats: {
    additions: number;
    deletions: number;
    modifications: number;
  };
  created_at: string;
}

export interface DesignBranch {
  id: string;
  project: number;
  name: string;
  description: string;
  created_by: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  parent_branch: string | null;
  branch_point: string | null;
  head_commit: string | null;
  status: BranchStatus;
  is_default: boolean;
  is_protected: boolean;
  protection_rules: Record<string, unknown>;
  commits_ahead: number;
  commits_behind: number;
  last_activity: string;
  collaborators: Array<{
    user_id: number;
    username: string;
    role: 'viewer' | 'editor' | 'admin';
  }>;
  created_at: string;
  updated_at: string;
}

export interface BranchReview {
  id: string;
  branch: string;
  reviewer: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  status: ReviewStatus;
  summary: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface ReviewComment {
  id: string;
  review: string;
  author: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  content: string;
  node_id: string | null;
  position_x: number | null;
  position_y: number | null;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  replies: ReviewComment[];
  created_at: string;
  updated_at: string;
}

export interface MergeConflict {
  id: string;
  comparison: string;
  node_id: string;
  node_type: string;
  node_name: string;
  conflict_type: 'content' | 'property' | 'structure' | 'style' | 'delete';
  source_value: Record<string, unknown>;
  target_value: Record<string, unknown>;
  resolution: ConflictResolution | null;
  resolved_value: Record<string, unknown> | null;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
}

export interface BranchComparison {
  id: string;
  source_branch: string;
  target_branch: string;
  source_commit: string;
  target_commit: string;
  common_ancestor: string | null;
  added_nodes: string[];
  modified_nodes: string[];
  deleted_nodes: string[];
  style_changes: Record<string, unknown>;
  can_auto_merge: boolean;
  conflict_count: number;
  conflicts: MergeConflict[];
  stats: {
    files_changed: number;
    additions: number;
    deletions: number;
  };
  created_at: string;
}

export interface BranchMerge {
  id: string;
  source_branch: string;
  target_branch: string;
  merged_by: {
    id: number;
    username: string;
  };
  strategy: MergeStrategy;
  merge_commit: string;
  source_commit: string;
  target_commit: string;
  conflicts_resolved: Record<string, unknown>;
  merge_message: string;
  is_squashed: boolean;
  is_reverted: boolean;
  reverted_at: string | null;
  reverted_by: number | null;
  created_at: string;
}

export interface DesignTag {
  id: string;
  project: number;
  name: string;
  commit: string;
  message: string;
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
}

export interface BranchDiff {
  nodes: Array<{
    id: string;
    name: string;
    type: string;
    change_type: 'added' | 'modified' | 'deleted';
    before?: Record<string, unknown>;
    after?: Record<string, unknown>;
    property_changes?: Array<{
      property: string;
      before: unknown;
      after: unknown;
    }>;
  }>;
  stats: {
    added: number;
    modified: number;
    deleted: number;
  };
}

// API Functions
export const designBranchesApi = {
  // Branch operations
  async getBranches(projectId: number, options?: {
    status?: BranchStatus;
    search?: string;
  }): Promise<DesignBranch[]> {
    const params = new URLSearchParams();
    params.append('project', String(projectId));
    if (options?.status) params.append('status', options.status);
    if (options?.search) params.append('search', options.search);
    const { data } = await apiClient.get(`/branches/?${params}`);
    return data.results || data;
  },

  async getBranch(branchId: string): Promise<DesignBranch> {
    const { data } = await apiClient.get(`/branches/${branchId}/`);
    return data;
  },

  async createBranch(branch: {
    project: number;
    name: string;
    description?: string;
    parent_branch?: string;
    from_commit?: string;
  }): Promise<DesignBranch> {
    const { data } = await apiClient.post('/branches/', branch);
    return data;
  },

  async updateBranch(branchId: string, updates: Partial<DesignBranch>): Promise<DesignBranch> {
    const { data } = await apiClient.patch(`/branches/${branchId}/`, updates);
    return data;
  },

  async deleteBranch(branchId: string, force?: boolean): Promise<void> {
    await apiClient.delete(`/branches/${branchId}/?force=${force || false}`);
  },

  async getCommitHistory(branchId: string, options?: {
    limit?: number;
    offset?: number;
    author?: number;
  }): Promise<DesignCommit[]> {
    const params = new URLSearchParams();
    if (options?.limit) params.append('limit', String(options.limit));
    if (options?.offset) params.append('offset', String(options.offset));
    if (options?.author) params.append('author', String(options.author));
    const { data } = await apiClient.get(`/branches/${branchId}/commits/?${params}`);
    return data.results || data;
  },

  async checkout(branchId: string): Promise<{ success: boolean; snapshot: Record<string, unknown> }> {
    const { data } = await apiClient.post(`/branches/${branchId}/checkout/`);
    return data;
  },

  async setDefault(branchId: string): Promise<DesignBranch> {
    const { data } = await apiClient.post(`/branches/${branchId}/set_default/`);
    return data;
  },

  async protect(branchId: string, rules?: Record<string, unknown>): Promise<DesignBranch> {
    const { data } = await apiClient.post(`/branches/${branchId}/protect/`, { rules });
    return data;
  },

  async unprotect(branchId: string): Promise<DesignBranch> {
    const { data } = await apiClient.post(`/branches/${branchId}/unprotect/`);
    return data;
  },

  async archive(branchId: string): Promise<DesignBranch> {
    const { data } = await apiClient.post(`/branches/${branchId}/archive/`);
    return data;
  },

  async unarchive(branchId: string): Promise<DesignBranch> {
    const { data } = await apiClient.post(`/branches/${branchId}/unarchive/`);
    return data;
  },

  async getDiff(branchId: string, targetBranchId?: string): Promise<BranchDiff> {
    const params = targetBranchId ? `?target=${targetBranchId}` : '';
    const { data } = await apiClient.get(`/branches/${branchId}/diff/${params}`);
    return data;
  },

  // Commit operations
  async getCommit(commitId: string): Promise<DesignCommit> {
    const { data } = await apiClient.get(`/commits/${commitId}/`);
    return data;
  },

  async createCommit(commit: {
    branch: string;
    message: string;
    description?: string;
    snapshot_data: Record<string, unknown>;
    file_changes?: Array<{
      path: string;
      change_type: 'added' | 'modified' | 'deleted';
    }>;
  }): Promise<DesignCommit> {
    const { data } = await apiClient.post('/commits/', commit);
    return data;
  },

  async revertCommit(commitId: string): Promise<DesignCommit> {
    const { data } = await apiClient.post(`/commits/${commitId}/revert/`);
    return data;
  },

  async cherryPick(commitId: string, targetBranchId: string): Promise<DesignCommit> {
    const { data } = await apiClient.post(`/commits/${commitId}/cherry_pick/`, {
      target_branch: targetBranchId,
    });
    return data;
  },

  async getCommitDiff(commitId: string): Promise<{
    changes: Array<{
      node_id: string;
      before: Record<string, unknown>;
      after: Record<string, unknown>;
    }>;
  }> {
    const { data } = await apiClient.get(`/commits/${commitId}/diff/`);
    return data;
  },

  // Comparison operations
  async createComparison(sourceBranch: string, targetBranch: string): Promise<BranchComparison> {
    const { data } = await apiClient.post('/comparisons/', {
      source_branch: sourceBranch,
      target_branch: targetBranch,
    });
    return data;
  },

  async getComparison(comparisonId: string): Promise<BranchComparison> {
    const { data } = await apiClient.get(`/comparisons/${comparisonId}/`);
    return data;
  },

  async refreshComparison(comparisonId: string): Promise<BranchComparison> {
    const { data } = await apiClient.post(`/comparisons/${comparisonId}/refresh/`);
    return data;
  },

  // Conflict operations
  async getConflicts(comparisonId: string): Promise<MergeConflict[]> {
    const { data } = await apiClient.get(`/conflicts/?comparison=${comparisonId}`);
    return data.results || data;
  },

  async resolveConflict(conflictId: string, resolution: ConflictResolution, resolvedValue?: Record<string, unknown>): Promise<MergeConflict> {
    const { data } = await apiClient.post(`/conflicts/${conflictId}/resolve/`, {
      resolution,
      resolved_value: resolvedValue,
    });
    return data;
  },

  async autoResolveConflicts(comparisonId: string, strategy: 'keep_source' | 'keep_target'): Promise<{
    resolved_count: number;
    remaining_count: number;
  }> {
    const { data } = await apiClient.post(`/comparisons/${comparisonId}/auto_resolve/`, { strategy });
    return data;
  },

  // Merge operations
  async merge(sourceBranch: string, targetBranch: string, options: {
    strategy?: MergeStrategy;
    message?: string;
    squash?: boolean;
  }): Promise<BranchMerge> {
    const { data } = await apiClient.post('/merges/', {
      source_branch: sourceBranch,
      target_branch: targetBranch,
      ...options,
    });
    return data;
  },

  async getMerge(mergeId: string): Promise<BranchMerge> {
    const { data } = await apiClient.get(`/merges/${mergeId}/`);
    return data;
  },

  async revertMerge(mergeId: string): Promise<DesignCommit> {
    const { data } = await apiClient.post(`/merges/${mergeId}/revert/`);
    return data;
  },

  async getMergeHistory(branchId: string): Promise<BranchMerge[]> {
    const { data } = await apiClient.get(`/merges/?target_branch=${branchId}`);
    return data.results || data;
  },

  // Review operations
  async getReviews(branchId: string): Promise<BranchReview[]> {
    const { data } = await apiClient.get(`/reviews/?branch=${branchId}`);
    return data.results || data;
  },

  async createReview(review: {
    branch: string;
    summary?: string;
  }): Promise<BranchReview> {
    const { data } = await apiClient.post('/reviews/', review);
    return data;
  },

  async submitReview(reviewId: string, status: 'approved' | 'changes_requested', summary?: string): Promise<BranchReview> {
    const { data } = await apiClient.post(`/reviews/${reviewId}/submit/`, { status, summary });
    return data;
  },

  async dismissReview(reviewId: string, reason?: string): Promise<BranchReview> {
    const { data } = await apiClient.post(`/reviews/${reviewId}/dismiss/`, { reason });
    return data;
  },

  async requestReview(branchId: string, reviewerIds: number[]): Promise<BranchReview[]> {
    const { data } = await apiClient.post(`/branches/${branchId}/request_review/`, {
      reviewer_ids: reviewerIds,
    });
    return data;
  },

  // Review comment operations
  async getReviewComments(reviewId: string): Promise<ReviewComment[]> {
    const { data } = await apiClient.get(`/comments/?review=${reviewId}`);
    return data.results || data;
  },

  async createComment(comment: {
    review: string;
    content: string;
    node_id?: string;
    position_x?: number;
    position_y?: number;
    parent?: string;
  }): Promise<ReviewComment> {
    const { data } = await apiClient.post('/comments/', comment);
    return data;
  },

  async updateComment(commentId: string, content: string): Promise<ReviewComment> {
    const { data } = await apiClient.patch(`/comments/${commentId}/`, { content });
    return data;
  },

  async deleteComment(commentId: string): Promise<void> {
    await apiClient.delete(`/comments/${commentId}/`);
  },

  async resolveComment(commentId: string): Promise<ReviewComment> {
    const { data } = await apiClient.post(`/comments/${commentId}/resolve/`);
    return data;
  },

  async unresolveComment(commentId: string): Promise<ReviewComment> {
    const { data } = await apiClient.post(`/comments/${commentId}/unresolve/`);
    return data;
  },

  // Tag operations
  async getTags(projectId: number): Promise<DesignTag[]> {
    const { data } = await apiClient.get(`/tags/?project=${projectId}`);
    return data.results || data;
  },

  async createTag(tag: {
    project: number;
    name: string;
    commit: string;
    message?: string;
  }): Promise<DesignTag> {
    const { data } = await apiClient.post('/tags/', tag);
    return data;
  },

  async deleteTag(tagId: string): Promise<void> {
    await apiClient.delete(`/tags/${tagId}/`);
  },

  async getTagCommit(tagId: string): Promise<DesignCommit> {
    const { data } = await apiClient.get(`/tags/${tagId}/commit/`);
    return data;
  },

  // Utility functions
  async syncWithRemote(branchId: string): Promise<{
    synced: boolean;
    commits_pulled: number;
    commits_pushed: number;
    conflicts: boolean;
  }> {
    const { data } = await apiClient.post(`/branches/${branchId}/sync/`);
    return data;
  },

  async getActivityFeed(projectId: number, options?: {
    limit?: number;
    branch?: string;
  }): Promise<Array<{
    type: 'commit' | 'merge' | 'review' | 'branch_created' | 'branch_deleted';
    actor: { id: number; username: string };
    data: Record<string, unknown>;
    created_at: string;
  }>> {
    const params = new URLSearchParams();
    params.append('project', String(projectId));
    if (options?.limit) params.append('limit', String(options.limit));
    if (options?.branch) params.append('branch', options.branch);
    const { data } = await apiClient.get(`/activity/?${params}`);
    return data.results || data;
  },
};

export default designBranchesApi;

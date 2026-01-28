'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  GitBranch,
  GitCommit,
  GitMerge,
  GitPullRequest,
  Plus,
  Search,
  ChevronDown,
  ChevronRight,
  Check,
  X,
  Clock,
  User,
  Lock,
  Archive,
  Star,
  MoreHorizontal,
  Eye,
  Trash2,
  Copy,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  MessageSquare,
  Tag,
  Filter,
  ArrowUpRight,
  ArrowDownLeft,
  Diff,
} from 'lucide-react';

// Types
interface Author {
  id: string;
  name: string;
  avatar?: string;
  email?: string;
}

interface Branch {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  author: Author;
  isProtected: boolean;
  isArchived: boolean;
  isCurrent: boolean;
  isDefault: boolean;
  aheadCount: number;
  behindCount: number;
  commitCount: number;
  status: 'active' | 'merging' | 'conflict' | 'merged' | 'archived';
  parentBranch?: string;
  reviewStatus?: 'pending' | 'approved' | 'changes_requested' | 'none';
}

interface Commit {
  id: string;
  hash: string;
  message: string;
  description?: string;
  author: Author;
  createdAt: string;
  branchId: string;
  changes: {
    added: number;
    modified: number;
    deleted: number;
  };
  tags?: string[];
}

interface MergeConflict {
  id: string;
  elementId: string;
  elementName: string;
  elementType: string;
  sourceBranch: string;
  targetBranch: string;
  sourceValue: unknown;
  targetValue: unknown;
  resolution?: 'source' | 'target' | 'manual';
}

interface Review {
  id: string;
  branchId: string;
  reviewer: Author;
  status: 'pending' | 'approved' | 'changes_requested';
  comments: number;
  createdAt: string;
}

// Mock data
const mockBranches: Branch[] = [
  {
    id: 'main',
    name: 'main',
    description: 'Main production branch',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-15T12:00:00Z',
    author: { id: '1', name: 'John Doe', avatar: '' },
    isProtected: true,
    isArchived: false,
    isCurrent: false,
    isDefault: true,
    aheadCount: 0,
    behindCount: 0,
    commitCount: 156,
    status: 'active',
  },
  {
    id: 'feature/homepage-redesign',
    name: 'feature/homepage-redesign',
    description: 'Redesigning the homepage hero section',
    createdAt: '2024-01-10T09:00:00Z',
    updatedAt: '2024-01-15T14:30:00Z',
    author: { id: '2', name: 'Jane Smith', avatar: '' },
    isProtected: false,
    isArchived: false,
    isCurrent: true,
    isDefault: false,
    aheadCount: 12,
    behindCount: 3,
    commitCount: 24,
    status: 'active',
    parentBranch: 'main',
    reviewStatus: 'pending',
  },
  {
    id: 'feature/dark-mode',
    name: 'feature/dark-mode',
    description: 'Adding dark mode support',
    createdAt: '2024-01-08T14:00:00Z',
    updatedAt: '2024-01-14T10:00:00Z',
    author: { id: '1', name: 'John Doe', avatar: '' },
    isProtected: false,
    isArchived: false,
    isCurrent: false,
    isDefault: false,
    aheadCount: 8,
    behindCount: 5,
    commitCount: 15,
    status: 'conflict',
    parentBranch: 'main',
    reviewStatus: 'changes_requested',
  },
  {
    id: 'bugfix/button-states',
    name: 'bugfix/button-states',
    description: 'Fixing button hover states',
    createdAt: '2024-01-12T11:00:00Z',
    updatedAt: '2024-01-13T16:00:00Z',
    author: { id: '3', name: 'Mike Wilson', avatar: '' },
    isProtected: false,
    isArchived: true,
    isCurrent: false,
    isDefault: false,
    aheadCount: 0,
    behindCount: 0,
    commitCount: 5,
    status: 'merged',
    parentBranch: 'main',
    reviewStatus: 'approved',
  },
];

const mockCommits: Commit[] = [
  {
    id: 'c1',
    hash: 'a1b2c3d',
    message: 'Update hero section layout',
    description: 'Changed grid to flexbox for better responsiveness',
    author: { id: '2', name: 'Jane Smith' },
    createdAt: '2024-01-15T14:30:00Z',
    branchId: 'feature/homepage-redesign',
    changes: { added: 5, modified: 12, deleted: 2 },
    tags: ['v1.2.0'],
  },
  {
    id: 'c2',
    hash: 'e4f5g6h',
    message: 'Add new CTA button variant',
    author: { id: '2', name: 'Jane Smith' },
    createdAt: '2024-01-15T12:00:00Z',
    branchId: 'feature/homepage-redesign',
    changes: { added: 3, modified: 1, deleted: 0 },
  },
  {
    id: 'c3',
    hash: 'i7j8k9l',
    message: 'Refactor navigation component',
    author: { id: '2', name: 'Jane Smith' },
    createdAt: '2024-01-14T16:45:00Z',
    branchId: 'feature/homepage-redesign',
    changes: { added: 2, modified: 8, deleted: 3 },
  },
];

const mockConflicts: MergeConflict[] = [
  {
    id: 'conf1',
    elementId: 'btn-primary',
    elementName: 'Primary Button',
    elementType: 'Component',
    sourceBranch: 'feature/dark-mode',
    targetBranch: 'main',
    sourceValue: { background: '#1a1a1a', color: '#ffffff' },
    targetValue: { background: '#0066ff', color: '#ffffff' },
  },
  {
    id: 'conf2',
    elementId: 'header-nav',
    elementName: 'Header Navigation',
    elementType: 'Frame',
    sourceBranch: 'feature/dark-mode',
    targetBranch: 'main',
    sourceValue: { height: 64 },
    targetValue: { height: 72 },
  },
];

// Helper components
const Avatar: React.FC<{ author: Author; size?: 'sm' | 'md' }> = ({ author, size = 'sm' }) => {
  const sizeClasses = size === 'sm' ? 'w-5 h-5 text-[10px]' : 'w-7 h-7 text-xs';
  
  if (author.avatar) {
    return (
      <img
        src={author.avatar}
        alt={author.name}
        className={`${sizeClasses} rounded-full`}
      />
    );
  }
  
  return (
    <div className={`${sizeClasses} rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium`}>
      {author.name.charAt(0).toUpperCase()}
    </div>
  );
};

const StatusBadge: React.FC<{ status: Branch['status'] }> = ({ status }) => {
  const config = {
    active: { bg: 'bg-green-500/20', text: 'text-green-400', label: 'Active' },
    merging: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', label: 'Merging' },
    conflict: { bg: 'bg-red-500/20', text: 'text-red-400', label: 'Conflict' },
    merged: { bg: 'bg-purple-500/20', text: 'text-purple-400', label: 'Merged' },
    archived: { bg: 'bg-gray-500/20', text: 'text-gray-400', label: 'Archived' },
  };

  const { bg, text, label } = config[status];

  return (
    <span className={`px-1.5 py-0.5 text-[10px] font-medium rounded ${bg} ${text}`}>
      {label}
    </span>
  );
};

const ReviewBadge: React.FC<{ status: Branch['reviewStatus'] }> = ({ status }) => {
  if (!status || status === 'none') return null;

  const config = {
    pending: { icon: Clock, text: 'text-yellow-400', label: 'Review pending' },
    approved: { icon: CheckCircle, text: 'text-green-400', label: 'Approved' },
    changes_requested: { icon: XCircle, text: 'text-red-400', label: 'Changes requested' },
  };

  const { icon: Icon, text, label } = config[status];

  return (
    <span className={`flex items-center gap-1 text-[10px] ${text}`} title={label}>
      <Icon size={12} />
    </span>
  );
};

// Branch Item Component
interface BranchItemProps {
  branch: Branch;
  isExpanded: boolean;
  onToggleExpand: (id: string) => void;
  onCheckout: (id: string) => void;
  onMerge: (id: string) => void;
  onDelete: (id: string) => void;
  onViewDiff: (id: string) => void;
  commits: Commit[];
}

const BranchItem: React.FC<BranchItemProps> = ({
  branch,
  isExpanded,
  onToggleExpand,
  onCheckout,
  onMerge,
  onDelete,
  onViewDiff,
  commits,
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const branchCommits = commits.filter((c) => c.branchId === branch.id);

  return (
    <div className={`border-b border-gray-700/50 ${branch.isCurrent ? 'bg-blue-900/20' : ''}`}>
      {/* Branch Header */}
      <div className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800/50 transition-colors">
        <button
          onClick={() => onToggleExpand(branch.id)}
          className="p-0.5 hover:bg-gray-700 rounded"
        >
          {isExpanded ? (
            <ChevronDown size={14} className="text-gray-400" />
          ) : (
            <ChevronRight size={14} className="text-gray-400" />
          )}
        </button>

        <GitBranch
          size={14}
          className={branch.isCurrent ? 'text-blue-400' : 'text-gray-500'}
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className={`text-sm font-medium truncate ${
                branch.isCurrent ? 'text-blue-300' : 'text-gray-200'
              }`}
            >
              {branch.name}
            </span>
            {branch.isDefault && (
              <span className="px-1 py-0.5 text-[9px] bg-gray-700 text-gray-300 rounded">
                DEFAULT
              </span>
            )}
            {branch.isProtected && (
              <span aria-label="Protected">
                <Lock size={10} className="text-yellow-500" />
              </span>
            )}
            <StatusBadge status={branch.status} />
            <ReviewBadge status={branch.reviewStatus} />
          </div>
          <div className="flex items-center gap-3 mt-0.5">
            <span className="text-[10px] text-gray-500 flex items-center gap-1">
              <Avatar author={branch.author} size="sm" />
              {branch.author.name}
            </span>
            <span className="text-[10px] text-gray-500">
              {new Date(branch.updatedAt).toLocaleDateString()}
            </span>
            {branch.aheadCount > 0 && (
              <span className="text-[10px] text-green-400 flex items-center gap-0.5">
                <ArrowUpRight size={10} />
                {branch.aheadCount}
              </span>
            )}
            {branch.behindCount > 0 && (
              <span className="text-[10px] text-red-400 flex items-center gap-0.5">
                <ArrowDownLeft size={10} />
                {branch.behindCount}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {!branch.isCurrent && !branch.isArchived && (
            <button
              onClick={() => onCheckout(branch.id)}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded text-xs"
              title="Checkout"
            >
              <Check size={14} />
            </button>
          )}
          <button
            onClick={() => onViewDiff(branch.id)}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="View diff"
          >
            <Diff size={14} />
          </button>
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            >
              <MoreHorizontal size={14} />
            </button>
            {showMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 mt-1 w-40 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20 py-1">
                  <button
                    onClick={() => {
                      onMerge(branch.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-3 py-1.5 text-left text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                    disabled={branch.isDefault}
                  >
                    <GitMerge size={12} />
                    Merge to main
                  </button>
                  <button
                    onClick={() => setShowMenu(false)}
                    className="w-full px-3 py-1.5 text-left text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                  >
                    <Copy size={12} />
                    Duplicate
                  </button>
                  <button
                    onClick={() => setShowMenu(false)}
                    className="w-full px-3 py-1.5 text-left text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                  >
                    <Archive size={12} />
                    Archive
                  </button>
                  <div className="border-t border-gray-700 my-1" />
                  <button
                    onClick={() => {
                      onDelete(branch.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-3 py-1.5 text-left text-xs text-red-400 hover:bg-red-900/20 flex items-center gap-2"
                    disabled={branch.isProtected}
                  >
                    <Trash2 size={12} />
                    Delete
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Commits (when expanded) */}
      {isExpanded && (
        <div className="pl-8 pr-3 pb-2">
          {branchCommits.length > 0 ? (
            <div className="space-y-1">
              {branchCommits.map((commit, index) => (
                <div
                  key={commit.id}
                  className="flex items-start gap-2 py-1.5 px-2 bg-gray-800/30 rounded"
                >
                  <div className="flex flex-col items-center mt-1">
                    <GitCommit size={12} className="text-gray-500" />
                    {index < branchCommits.length - 1 && (
                      <div className="w-px h-6 bg-gray-700 mt-1" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-blue-400">
                        {commit.hash}
                      </span>
                      {commit.tags?.map((tag) => (
                        <span
                          key={tag}
                          className="flex items-center gap-0.5 px-1 py-0.5 text-[9px] bg-yellow-500/20 text-yellow-400 rounded"
                        >
                          <Tag size={8} />
                          {tag}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-gray-200 truncate mt-0.5">
                      {commit.message}
                    </p>
                    <div className="flex items-center gap-3 mt-1 text-[10px] text-gray-500">
                      <span className="flex items-center gap-1">
                        <Avatar author={commit.author} size="sm" />
                        {commit.author.name}
                      </span>
                      <span>
                        {new Date(commit.createdAt).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-2">
                        <span className="text-green-400">+{commit.changes.added}</span>
                        <span className="text-yellow-400">~{commit.changes.modified}</span>
                        <span className="text-red-400">-{commit.changes.deleted}</span>
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-500 py-2">No commits in this view</p>
          )}
        </div>
      )}
    </div>
  );
};

// Conflict Resolution Component
interface ConflictResolutionProps {
  conflicts: MergeConflict[];
  onResolve: (id: string, resolution: 'source' | 'target' | 'manual') => void;
  onResolveAll: (resolution: 'source' | 'target') => void;
  onCancel: () => void;
}

const ConflictResolution: React.FC<ConflictResolutionProps> = ({
  conflicts,
  onResolve,
  onResolveAll,
  onCancel,
}) => {
  return (
    <div className="bg-red-900/10 border border-red-800/50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <AlertCircle size={16} className="text-red-400" />
          <h4 className="text-sm font-medium text-red-300">
            {conflicts.length} Merge Conflicts
          </h4>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onResolveAll('target')}
            className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
          >
            Keep All Incoming
          </button>
          <button
            onClick={() => onResolveAll('source')}
            className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Keep All Current
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {conflicts.map((conflict) => (
          <div
            key={conflict.id}
            className="bg-gray-800/50 rounded-lg p-3 border border-gray-700"
          >
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-sm font-medium text-gray-200">
                  {conflict.elementName}
                </span>
                <span className="ml-2 text-xs text-gray-500">
                  ({conflict.elementType})
                </span>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => onResolve(conflict.id, 'source')}
                  className={`px-2 py-1 text-xs rounded ${
                    conflict.resolution === 'source'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Keep Current
                </button>
                <button
                  onClick={() => onResolve(conflict.id, 'target')}
                  className={`px-2 py-1 text-xs rounded ${
                    conflict.resolution === 'target'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Keep Incoming
                </button>
                <button
                  onClick={() => onResolve(conflict.id, 'manual')}
                  className={`px-2 py-1 text-xs rounded ${
                    conflict.resolution === 'manual'
                      ? 'bg-yellow-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Manual
                </button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-blue-900/20 p-2 rounded border border-blue-800/50">
                <div className="text-blue-400 mb-1">Current ({conflict.sourceBranch})</div>
                <pre className="text-gray-300 overflow-auto">
                  {JSON.stringify(conflict.sourceValue, null, 2)}
                </pre>
              </div>
              <div className="bg-purple-900/20 p-2 rounded border border-purple-800/50">
                <div className="text-purple-400 mb-1">Incoming ({conflict.targetBranch})</div>
                <pre className="text-gray-300 overflow-auto">
                  {JSON.stringify(conflict.targetValue, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-end gap-2 mt-4">
        <button
          onClick={onCancel}
          className="px-3 py-1.5 text-sm text-gray-300 hover:text-white"
        >
          Cancel Merge
        </button>
        <button
          disabled={conflicts.some((c) => !c.resolution)}
          className="px-3 py-1.5 text-sm bg-green-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-700"
        >
          Complete Merge
        </button>
      </div>
    </div>
  );
};

// Main Component
interface DesignBranchPanelProps {
  projectId?: string;
  onBranchChange?: (branchId: string) => void;
  onCreateBranch?: (name: string, description?: string) => void;
}

export const DesignBranchPanel: React.FC<DesignBranchPanelProps> = ({
  projectId,
  onBranchChange,
  onCreateBranch,
}) => {
  const [branches, setBranches] = useState<Branch[]>(mockBranches);
  const [commits] = useState<Commit[]>(mockCommits);
  const [conflicts, setConflicts] = useState<MergeConflict[]>(mockConflicts);
  const [expandedBranches, setExpandedBranches] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'archived' | 'mine'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showConflicts, setShowConflicts] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');
  const [newBranchDescription, setNewBranchDescription] = useState('');

  // Filter branches
  const filteredBranches = useMemo(() => {
    let result = branches;

    if (searchQuery) {
      result = result.filter(
        (b) =>
          b.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          b.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    switch (filter) {
      case 'active':
        result = result.filter((b) => !b.isArchived && b.status !== 'merged');
        break;
      case 'archived':
        result = result.filter((b) => b.isArchived || b.status === 'merged');
        break;
      case 'mine':
        result = result.filter((b) => b.author.id === '1'); // Current user
        break;
    }

    return result;
  }, [branches, searchQuery, filter]);

  // Handlers
  const handleToggleExpand = useCallback((id: string) => {
    setExpandedBranches((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleCheckout = useCallback((id: string) => {
    setBranches((prev) =>
      prev.map((b) => ({ ...b, isCurrent: b.id === id }))
    );
    onBranchChange?.(id);
  }, [onBranchChange]);

  const handleMerge = useCallback((id: string) => {
    const branch = branches.find((b) => b.id === id);
    if (branch?.status === 'conflict') {
      setShowConflicts(true);
    } else {
      // Simulate merge
      setBranches((prev) =>
        prev.map((b) =>
          b.id === id ? { ...b, status: 'merged', isArchived: true } : b
        )
      );
    }
  }, [branches]);

  const handleDelete = useCallback((id: string) => {
    setBranches((prev) => prev.filter((b) => b.id !== id));
  }, []);

  const handleViewDiff = useCallback((id: string) => {
    console.log('View diff for branch:', id);
  }, []);

  const handleCreateBranch = useCallback(() => {
    if (!newBranchName.trim()) return;

    const newBranch: Branch = {
      id: newBranchName.toLowerCase().replace(/\s+/g, '-'),
      name: newBranchName,
      description: newBranchDescription,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      author: { id: '1', name: 'John Doe' },
      isProtected: false,
      isArchived: false,
      isCurrent: false,
      isDefault: false,
      aheadCount: 0,
      behindCount: 0,
      commitCount: 0,
      status: 'active',
      parentBranch: 'main',
    };

    setBranches((prev) => [...prev, newBranch]);
    setShowCreateModal(false);
    setNewBranchName('');
    setNewBranchDescription('');
    onCreateBranch?.(newBranch.name, newBranch.description);
  }, [newBranchName, newBranchDescription, onCreateBranch]);

  const handleResolveConflict = useCallback((id: string, resolution: 'source' | 'target' | 'manual') => {
    setConflicts((prev) =>
      prev.map((c) => (c.id === id ? { ...c, resolution } : c))
    );
  }, []);

  const handleResolveAllConflicts = useCallback((resolution: 'source' | 'target') => {
    setConflicts((prev) =>
      prev.map((c) => ({ ...c, resolution }))
    );
  }, []);

  const currentBranch = branches.find((b) => b.isCurrent);

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <GitBranch size={18} className="text-blue-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">Branches</h3>
            <p className="text-xs text-gray-500">
              {currentBranch ? `Current: ${currentBranch.name}` : 'No branch selected'}
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus size={14} />
          New Branch
        </button>
      </div>

      {/* Search and Filters */}
      <div className="px-4 py-2 border-b border-gray-700 space-y-2">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search branches..."
            className="w-full pl-9 pr-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="flex items-center gap-2">
          {(['all', 'active', 'archived', 'mine'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-1 text-xs rounded-lg transition-colors ${
                filter === f
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Conflict Alert */}
      {showConflicts && conflicts.length > 0 && (
        <div className="p-4 border-b border-gray-700">
          <ConflictResolution
            conflicts={conflicts}
            onResolve={handleResolveConflict}
            onResolveAll={handleResolveAllConflicts}
            onCancel={() => setShowConflicts(false)}
          />
        </div>
      )}

      {/* Branch List */}
      <div className="flex-1 overflow-y-auto">
        {filteredBranches.length > 0 ? (
          filteredBranches.map((branch) => (
            <BranchItem
              key={branch.id}
              branch={branch}
              isExpanded={expandedBranches.has(branch.id)}
              onToggleExpand={handleToggleExpand}
              onCheckout={handleCheckout}
              onMerge={handleMerge}
              onDelete={handleDelete}
              onViewDiff={handleViewDiff}
              commits={commits}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <GitBranch size={32} className="mb-2 opacity-50" />
            <p className="text-sm">No branches found</p>
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="px-4 py-2 bg-gray-850 border-t border-gray-700 text-xs text-gray-500 flex items-center justify-between">
        <span>{filteredBranches.length} branches</span>
        <span>
          {filteredBranches.reduce((t, b) => t + b.commitCount, 0)} total commits
        </span>
      </div>

      {/* Create Branch Modal */}
      {showCreateModal && (
        <>
          <div
            className="fixed inset-0 bg-black/50 z-40"
            onClick={() => setShowCreateModal(false)}
          />
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 bg-gray-800 border border-gray-700 rounded-xl shadow-2xl z-50 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Create New Branch</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Branch Name</label>
                <input
                  type="text"
                  value={newBranchName}
                  onChange={(e) => setNewBranchName(e.target.value)}
                  placeholder="feature/my-feature"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description (optional)</label>
                <textarea
                  value={newBranchDescription}
                  onChange={(e) => setNewBranchDescription(e.target.value)}
                  placeholder="What are you working on?"
                  rows={3}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <GitBranch size={12} />
                <span>Branching from: {currentBranch?.name || 'main'}</span>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-sm text-gray-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateBranch}
                disabled={!newBranchName.trim()}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700"
              >
                Create Branch
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DesignBranchPanel;

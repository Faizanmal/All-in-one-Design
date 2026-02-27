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
  Shield,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

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

// Real data should be fetched from /api/design-branches/ endpoints

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
    <div className={`${sizeClasses} rounded-full bg-linear-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium`}>
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
  onDuplicate: (id: string) => void;
  onArchive: (id: string) => void;
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
  onDuplicate,
  onArchive,
  commits,
}) => {
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
              <Badge className="text-[9px] h-3.5 px-1 bg-gray-700 text-gray-300">DEFAULT</Badge>
            )}
            {branch.isProtected && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <span aria-label="Protected">
                    <Lock size={10} className="text-yellow-500" />
                  </span>
                </TooltipTrigger>
                <TooltipContent>Protected branch</TooltipContent>
              </Tooltip>
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
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="text-[10px] text-green-400 flex items-center gap-0.5 cursor-default">
                    <ArrowUpRight size={10} />
                    {branch.aheadCount} ahead
                  </span>
                </TooltipTrigger>
                <TooltipContent>{branch.aheadCount} commits ahead of base</TooltipContent>
              </Tooltip>
            )}
            {branch.behindCount > 0 && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="text-[10px] text-red-400 flex items-center gap-0.5 cursor-default">
                    <ArrowDownLeft size={10} />
                    {branch.behindCount} behind
                  </span>
                </TooltipTrigger>
                <TooltipContent>{branch.behindCount} commits behind base</TooltipContent>
              </Tooltip>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          {!branch.isCurrent && !branch.isArchived && (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={() => onCheckout(branch.id)}
                  className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded text-xs"
                >
                  <Check size={14} />
                </button>
              </TooltipTrigger>
              <TooltipContent>Switch to this branch</TooltipContent>
            </Tooltip>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => onViewDiff(branch.id)}
                className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
              >
                <Diff size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent>View diff vs base</TooltipContent>
          </Tooltip>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                <MoreHorizontal size={14} />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-800 border-gray-700 text-white min-w-[150px]">
              <DropdownMenuItem
                className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer gap-2"
                onClick={() => onMerge(branch.id)}
                disabled={branch.isDefault}
              >
                <GitMerge size={12} /> Merge to main
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer gap-2"
                onClick={() => onDuplicate(branch.id)}
              >
                <Copy size={12} /> Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem
                className="text-xs text-gray-300 hover:bg-gray-700 cursor-pointer gap-2"
                onClick={() => onArchive(branch.id)}
              >
                <Archive size={12} /> Archive
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700" />
              <DropdownMenuItem
                className="text-xs text-red-400 hover:bg-red-900/20 cursor-pointer gap-2"
                onClick={() => onDelete(branch.id)}
                disabled={branch.isProtected}
              >
                <Trash2 size={12} /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
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
  const [branches, setBranches] = useState<Branch[]>([]);
  const [commits] = useState<Commit[]>([]);
  const [conflicts, setConflicts] = useState<MergeConflict[]>([]);
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

  const handleDuplicate = useCallback((id: string) => {
    const branch = branches.find((b) => b.id === id);
    if (!branch) return;
    const copy: Branch = {
      ...branch,
      id: `${branch.id}-copy-${Date.now()}`,
      name: `${branch.name}-copy`,
      isCurrent: false,
      isDefault: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      aheadCount: 0,
      behindCount: 0,
      commitCount: 0,
      status: 'active',
    };
    setBranches((prev) => [...prev, copy]);
  }, [branches]);

  const handleArchive = useCallback((id: string) => {
    setBranches((prev) =>
      prev.map((b) => b.id === id ? { ...b, isArchived: !b.isArchived, status: b.isArchived ? 'active' : 'archived' } : b)
    );
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
    <TooltipProvider>
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <GitBranch size={18} className="text-blue-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">Branches</h3>
            <p className="text-xs text-gray-500">
              {currentBranch ? (
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
                  {currentBranch.name}
                </span>
              ) : 'No branch selected'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {conflicts.length > 0 && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge className="bg-red-500/20 text-red-400 text-[10px] cursor-default">
                  <AlertCircle size={10} className="mr-1" />{conflicts.length} conflict{conflicts.length !== 1 ? 's' : ''}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>Merge conflicts need resolution</TooltipContent>
            </Tooltip>
          )}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                className="flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <GitPullRequest size={13} />
                PR
              </button>
            </TooltipTrigger>
            <TooltipContent>Create pull request</TooltipContent>
          </Tooltip>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={14} />
            New Branch
          </button>
        </div>
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
              onDuplicate={handleDuplicate}
              onArchive={handleArchive}
              commits={commits}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center h-full py-16 text-gray-500">
            <GitBranch size={40} className="mb-3 opacity-30" />
            <p className="text-sm font-medium text-gray-400">
              {searchQuery || filter !== 'all' ? 'No matching branches' : 'No branches yet'}
            </p>
            <p className="text-xs mt-1">
              {searchQuery || filter !== 'all' ? 'Try changing your filters' : 'Create a branch to start working'}
            </p>
            {!searchQuery && filter === 'all' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-600/20 text-blue-400 border border-blue-600/30 rounded-lg hover:bg-blue-600/30"
              >
                <Plus size={12} /> Create First Branch
              </button>
            )}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div className="px-4 py-2 bg-gray-850 border-t border-gray-700 text-xs text-gray-500 flex items-center justify-between">
        <span>{filteredBranches.length} branch{filteredBranches.length !== 1 ? 'es' : ''}</span>
        <div className="flex items-center gap-3">
          <span className="text-green-400">{branches.filter(b => b.status === 'active').length} active</span>
          <span>
            {filteredBranches.reduce((t, b) => t + b.commitCount, 0)} total commits
          </span>
        </div>
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
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateBranch()}
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
              <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-900/50 rounded-lg px-3 py-2">
                <GitBranch size={12} />
                <span>Forking from: <span className="text-gray-300">{currentBranch?.name || 'main'}</span></span>
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
    </TooltipProvider>
  );
};

export default DesignBranchPanel;

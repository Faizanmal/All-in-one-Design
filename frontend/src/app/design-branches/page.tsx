"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  GitBranch,
  GitMerge,
  GitPullRequest,
  GitCommit,
  Plus,
  Search,
  MoreVertical,
  Trash2,
  Copy,
  Eye,
  ArrowLeftRight,
  User,
  Lock,
  ChevronRight,
  History,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface User {
  id: number;
  username: string;
  full_name: string;
  avatar?: string;
}

interface Commit {
  id: string;
  message: string;
  author: User;
  created_at: string;
  changes_count: number;
}

interface Branch {
  id: number;
  name: string;
  description: string;
  design_id: number;
  design_name: string;
  design_thumbnail: string;
  is_default: boolean;
  is_protected: boolean;
  status: 'active' | 'merged' | 'closed';
  created_by: User;
  created_at: string;
  updated_at: string;
  commits_count: number;
  commits: Commit[];
  ahead_count: number;
  behind_count: number;
}

interface MergeRequest {
  id: number;
  title: string;
  description: string;
  source_branch: Branch;
  target_branch: Branch;
  status: 'open' | 'merged' | 'closed' | 'conflict';
  author: User;
  reviewers: User[];
  created_at: string;
  comments_count: number;
}

// Mock Data
const mockUsers: User[] = [
  { id: 1, username: 'john_doe', full_name: 'John Doe', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=john' },
  { id: 2, username: 'jane_smith', full_name: 'Jane Smith', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=jane' },
  { id: 3, username: 'mike_wilson', full_name: 'Mike Wilson', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=mike' },
];

const mockBranches: Branch[] = [
  {
    id: 1, name: 'main', description: 'Production-ready designs', design_id: 1, design_name: 'Homepage Redesign',
    design_thumbnail: 'https://picsum.photos/seed/d1/200/150', is_default: true, is_protected: true,
    status: 'active', created_by: mockUsers[0], created_at: '2024-01-15T10:00:00Z', updated_at: '2024-02-20T14:00:00Z',
    commits_count: 45, ahead_count: 0, behind_count: 0,
    commits: [
      { id: 'c1', message: 'Update hero section spacing', author: mockUsers[0], created_at: '2024-02-20T14:00:00Z', changes_count: 3 },
      { id: 'c2', message: 'Fix mobile navigation', author: mockUsers[1], created_at: '2024-02-19T16:30:00Z', changes_count: 5 },
      { id: 'c3', message: 'Add footer redesign', author: mockUsers[0], created_at: '2024-02-18T11:00:00Z', changes_count: 8 },
    ],
  },
  {
    id: 2, name: 'feature/dark-mode', description: 'Dark mode variant exploration', design_id: 1, design_name: 'Homepage Redesign',
    design_thumbnail: 'https://picsum.photos/seed/d1/200/150', is_default: false, is_protected: false,
    status: 'active', created_by: mockUsers[1], created_at: '2024-02-10T09:00:00Z', updated_at: '2024-02-20T10:00:00Z',
    commits_count: 12, ahead_count: 8, behind_count: 2,
    commits: [
      { id: 'c4', message: 'Dark mode color tokens', author: mockUsers[1], created_at: '2024-02-20T10:00:00Z', changes_count: 15 },
      { id: 'c5', message: 'Update button styles for dark mode', author: mockUsers[1], created_at: '2024-02-19T14:00:00Z', changes_count: 4 },
    ],
  },
  {
    id: 3, name: 'experiment/animations', description: 'Testing micro-interactions', design_id: 1, design_name: 'Homepage Redesign',
    design_thumbnail: 'https://picsum.photos/seed/d1/200/150', is_default: false, is_protected: false,
    status: 'active', created_by: mockUsers[2], created_at: '2024-02-15T14:00:00Z', updated_at: '2024-02-18T16:00:00Z',
    commits_count: 6, ahead_count: 4, behind_count: 5,
    commits: [
      { id: 'c6', message: 'Add hover animations', author: mockUsers[2], created_at: '2024-02-18T16:00:00Z', changes_count: 7 },
    ],
  },
  {
    id: 4, name: 'feature/mobile-redesign', description: 'Mobile-first redesign', design_id: 2, design_name: 'Product Page',
    design_thumbnail: 'https://picsum.photos/seed/d2/200/150', is_default: false, is_protected: false,
    status: 'merged', created_by: mockUsers[0], created_at: '2024-02-01T10:00:00Z', updated_at: '2024-02-15T12:00:00Z',
    commits_count: 23, ahead_count: 0, behind_count: 0,
    commits: [],
  },
];

const mockMergeRequests: MergeRequest[] = [
  {
    id: 1, title: 'Merge dark mode into main', description: 'Ready for review - dark mode implementation complete',
    source_branch: mockBranches[1], target_branch: mockBranches[0],
    status: 'open', author: mockUsers[1], reviewers: [mockUsers[0], mockUsers[2]],
    created_at: '2024-02-20T11:00:00Z', comments_count: 5,
  },
  {
    id: 2, title: 'Add animation experiments', description: 'Testing micro-interactions for hero section',
    source_branch: mockBranches[2], target_branch: mockBranches[0],
    status: 'conflict', author: mockUsers[2], reviewers: [mockUsers[0]],
    created_at: '2024-02-19T09:00:00Z', comments_count: 3,
  },
];

const timeAgo = (date: string) => {
  const now = new Date();
  const then = new Date(date);
  const diff = (now.getTime() - then.getTime()) / 1000;
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'open': return 'bg-blue-100 text-blue-700';
    case 'merged': return 'bg-purple-100 text-purple-700';
    case 'closed': return 'bg-gray-100 text-gray-700';
    case 'conflict': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

// Branch Card Component
function BranchCard({ branch, onSelect, isSelected }: { branch: Branch; onSelect: () => void; isSelected: boolean }) {
  return (
    <div onClick={onSelect}
      className={`p-4 border rounded-lg cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300 hover:shadow-sm bg-white'
      }`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <GitBranch className={`h-4 w-4 ${branch.is_default ? 'text-purple-600' : 'text-gray-400'}`} />
          <span className="font-medium text-gray-900">{branch.name}</span>
          {branch.is_default && <Badge className="bg-purple-100 text-purple-700 text-xs">default</Badge>}
          {branch.is_protected && <Lock className="h-3.5 w-3.5 text-amber-500" />}
          {branch.status === 'merged' && <Badge className="bg-green-100 text-green-700 text-xs">merged</Badge>}
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={(e) => e.stopPropagation()}>
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem><Eye className="h-4 w-4 mr-2" />View Changes</DropdownMenuItem>
            <DropdownMenuItem><ArrowLeftRight className="h-4 w-4 mr-2" />Compare</DropdownMenuItem>
            <DropdownMenuItem><Copy className="h-4 w-4 mr-2" />Duplicate</DropdownMenuItem>
            <DropdownMenuSeparator />
            {!branch.is_protected && (
              <DropdownMenuItem className="text-red-600"><Trash2 className="h-4 w-4 mr-2" />Delete</DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <p className="text-sm text-gray-500 mb-3">{branch.description}</p>
      <div className="flex items-center gap-4 text-xs text-gray-400">
        <span className="flex items-center gap-1"><GitCommit className="h-3.5 w-3.5" />{branch.commits_count} commits</span>
        {branch.ahead_count > 0 && <span className="text-green-600">↑ {branch.ahead_count} ahead</span>}
        {branch.behind_count > 0 && <span className="text-orange-600">↓ {branch.behind_count} behind</span>}
      </div>
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
        <Avatar className="h-5 w-5">
          <AvatarImage src={branch.created_by.avatar} />
          <AvatarFallback className="text-xs">{branch.created_by.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
        </Avatar>
        <span className="text-xs text-gray-500">Updated {timeAgo(branch.updated_at)}</span>
      </div>
    </div>
  );
}

// Merge Request Card Component
function MergeRequestCard({ mr }: { mr: MergeRequest }) {
  return (
    <div className="p-4 border border-gray-200 rounded-lg bg-white hover:shadow-sm transition-shadow">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <GitPullRequest className={`h-5 w-5 ${mr.status === 'open' ? 'text-blue-600' : mr.status === 'merged' ? 'text-purple-600' : 'text-red-600'}`} />
          <span className="font-medium text-gray-900">{mr.title}</span>
          <Badge className={getStatusColor(mr.status)}>{mr.status}</Badge>
        </div>
      </div>
      <p className="text-sm text-gray-500 mb-3">{mr.description}</p>
      <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
        <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded">{mr.source_branch.name}</span>
        <ChevronRight className="h-3 w-3" />
        <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded">{mr.target_branch.name}</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Avatar className="h-5 w-5">
            <AvatarImage src={mr.author.avatar} />
            <AvatarFallback className="text-xs">{mr.author.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
          </Avatar>
          <span className="text-xs text-gray-500">{mr.author.full_name} • {timeAgo(mr.created_at)}</span>
        </div>
        <div className="flex items-center gap-2">
          {mr.reviewers.map(r => (
            <Avatar key={r.id} className="h-5 w-5 border border-white">
              <AvatarImage src={r.avatar} />
              <AvatarFallback className="text-xs">{r.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
            </Avatar>
          ))}
        </div>
      </div>
    </div>
  );
}

// Commit Item Component
function CommitItem({ commit }: { commit: Commit }) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 hover:bg-gray-50 rounded">
      <div className="w-2 h-2 rounded-full bg-blue-500" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900 truncate">{commit.message}</p>
        <p className="text-xs text-gray-500">{commit.author.full_name} • {timeAgo(commit.created_at)}</p>
      </div>
      <Badge variant="outline" className="text-xs">{commit.changes_count} changes</Badge>
    </div>
  );
}

export default function DesignBranchesPage() {
  const { toast } = useToast();
  const [branches] = useState<Branch[]>(mockBranches);
  const [mergeRequests] = useState<MergeRequest[]>(mockMergeRequests);
  const [selectedBranch, setSelectedBranch] = useState<Branch | null>(mockBranches[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewBranchDialog, setShowNewBranchDialog] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');

  const activeBranches = branches.filter(b => b.status === 'active');
  const mergedBranches = branches.filter(b => b.status === 'merged');

  const filteredBranches = branches.filter(b =>
    b.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    b.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreateBranch = () => {
    if (!newBranchName.trim()) return;
    toast({ title: 'Branch Created', description: `Branch "${newBranchName}" created successfully` });
    setShowNewBranchDialog(false);
    setNewBranchName('');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <GitBranch className="h-7 w-7 text-blue-600" />Design Branches
                </h1>
                <p className="text-gray-500">Version control for your designs</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><GitMerge className="h-4 w-4 mr-2" />New Merge Request</Button>
                <Button onClick={() => setShowNewBranchDialog(true)}><Plus className="h-4 w-4 mr-2" />New Branch</Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg"><GitBranch className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Active Branches</p>
                    <p className="text-2xl font-bold text-gray-900">{activeBranches.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg"><GitMerge className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Merged</p>
                    <p className="text-2xl font-bold text-gray-900">{mergedBranches.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg"><GitPullRequest className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Open MRs</p>
                    <p className="text-2xl font-bold text-gray-900">{mergeRequests.filter(m => m.status === 'open').length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-amber-100 rounded-lg"><GitCommit className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Total Commits</p>
                    <p className="text-2xl font-bold text-gray-900">{branches.reduce((a, b) => a + b.commits_count, 0)}</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
              {/* Branches List */}
              <div className="col-span-2 flex flex-col overflow-hidden bg-white rounded-lg border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold text-gray-900">Branches</h2>
                    <div className="relative w-64">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input placeholder="Search branches..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-9" />
                    </div>
                  </div>
                </div>
                <ScrollArea className="flex-1 p-4">
                  <div className="grid grid-cols-2 gap-4">
                    {filteredBranches.map(branch => (
                      <BranchCard key={branch.id} branch={branch} onSelect={() => setSelectedBranch(branch)} isSelected={selectedBranch?.id === branch.id} />
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Branch Details / Merge Requests */}
              <div className="flex flex-col gap-6 overflow-hidden">
                {/* Branch Detail */}
                {selectedBranch && (
                  <Card className="flex-1 overflow-hidden flex flex-col">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-base flex items-center gap-2">
                        <GitBranch className="h-4 w-4" />{selectedBranch.name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-hidden flex flex-col p-0">
                      <div className="px-6 py-3 border-b border-gray-100">
                        <p className="text-sm text-gray-500 mb-2">{selectedBranch.description}</p>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-6 w-6">
                            <AvatarImage src={selectedBranch.created_by.avatar} />
                            <AvatarFallback className="text-xs">{selectedBranch.created_by.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                          </Avatar>
                          <span className="text-sm text-gray-500">by {selectedBranch.created_by.full_name}</span>
                        </div>
                      </div>
                      <div className="px-6 py-2 border-b border-gray-100 flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Recent Commits</span>
                        <Button variant="ghost" size="sm" className="text-xs"><History className="h-3.5 w-3.5 mr-1" />View All</Button>
                      </div>
                      <ScrollArea className="flex-1 px-3">
                        {selectedBranch.commits.map(commit => (
                          <CommitItem key={commit.id} commit={commit} />
                        ))}
                      </ScrollArea>
                    </CardContent>
                  </Card>
                )}

                {/* Merge Requests */}
                <Card className="overflow-hidden">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <GitPullRequest className="h-4 w-4" />Merge Requests
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 max-h-64 overflow-auto">
                    {mergeRequests.map(mr => (
                      <MergeRequestCard key={mr.id} mr={mr} />
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* New Branch Dialog */}
      <Dialog open={showNewBranchDialog} onOpenChange={setShowNewBranchDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Branch</DialogTitle>
            <DialogDescription>Create a new branch from the current design state</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Branch Name</label>
              <Input placeholder="feature/my-branch" value={newBranchName} onChange={(e) => setNewBranchName(e.target.value)} className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Source Branch</label>
              <Input value="main" disabled className="mt-1 bg-gray-50" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewBranchDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateBranch}><Plus className="h-4 w-4 mr-2" />Create Branch</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

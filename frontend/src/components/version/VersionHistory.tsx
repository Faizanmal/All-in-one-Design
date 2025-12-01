'use client';

import React, { useState } from 'react';
import { 
  useProjectVersions, 
  useCreateSnapshot, 
  useRestoreVersion, 
  useVersionDiff,
  useProjectBranches,
  useCreateBranch,
  ProjectSnapshot,
  VersionDiff,
  Branch 
} from '@/hooks/use-new-features';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  History, 
  GitBranch, 
  RotateCcw, 
  Plus, 
  Diff,
  Save,
  User,
  Clock,
  ChevronRight,
  Layers
} from 'lucide-react';

interface VersionHistoryProps {
  projectId: string;
}

export function VersionHistory({ projectId }: VersionHistoryProps) {
  const [selectedBranch, setSelectedBranch] = useState<string>('main');
  const [compareFrom, setCompareFrom] = useState<number | null>(null);
  const [compareTo, setCompareTo] = useState<number | null>(null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showBranchDialog, setShowBranchDialog] = useState(false);
  const [snapshotLabel, setSnapshotLabel] = useState('');
  const [changeSummary, setChangeSummary] = useState('');
  const [newBranchName, setNewBranchName] = useState('');

  const { data: versionsData, isLoading } = useProjectVersions(projectId, { 
    branch: selectedBranch,
    limit: 50 
  });
  const { data: branches } = useProjectBranches(projectId);
  const createSnapshot = useCreateSnapshot();
  const restoreVersion = useRestoreVersion();
  const versionDiff = useVersionDiff();
  const createBranch = useCreateBranch();

  const versions: ProjectSnapshot[] = versionsData?.versions || [];

  const handleSaveSnapshot = async () => {
    await createSnapshot.mutateAsync({
      projectId,
      label: snapshotLabel,
      changeSummary,
      branchName: selectedBranch,
    });
    setShowSaveDialog(false);
    setSnapshotLabel('');
    setChangeSummary('');
  };

  const handleRestore = async (versionNumber: number) => {
    if (confirm(`Restore to version ${versionNumber}? A backup will be created.`)) {
      await restoreVersion.mutateAsync({
        projectId,
        versionNumber,
        createBackup: true,
      });
    }
  };

  const handleCompare = async () => {
    if (compareFrom && compareTo) {
      await versionDiff.mutateAsync({
        projectId,
        fromVersion: compareFrom,
        toVersion: compareTo,
      });
    }
  };

  const handleCreateBranch = async () => {
    await createBranch.mutateAsync({
      projectId,
      branchName: newBranchName,
    });
    setShowBranchDialog(false);
    setNewBranchName('');
    setSelectedBranch(newBranchName);
  };

  const getChangeTypeBadge = (type: string) => {
    const variants: Record<string, { label: string; variant: 'default' | 'secondary' | 'outline' }> = {
      manual: { label: 'Manual', variant: 'default' },
      auto: { label: 'Auto', variant: 'secondary' },
      restore: { label: 'Restored', variant: 'outline' },
      branch: { label: 'Branch', variant: 'outline' },
      ai_generated: { label: 'AI', variant: 'secondary' },
    };
    const config = variants[type] || { label: type, variant: 'outline' };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-10 bg-gray-200 rounded w-1/3"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Version History</h2>
        </div>
        <div className="flex items-center gap-2">
          {/* Branch Selector */}
          <Select value={selectedBranch} onValueChange={setSelectedBranch}>
            <SelectTrigger className="w-40">
              <GitBranch className="h-4 w-4 mr-2" />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {branches?.map((branch: Branch) => (
                <SelectItem key={branch.name} value={branch.name}>
                  {branch.name} ({branch.snapshot_count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* New Branch Button */}
          <Dialog open={showBranchDialog} onOpenChange={setShowBranchDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <GitBranch className="h-4 w-4 mr-2" />
                New Branch
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Branch</DialogTitle>
                <DialogDescription>
                  Create a new branch from the current version.
                </DialogDescription>
              </DialogHeader>
              <Input
                placeholder="Branch name"
                value={newBranchName}
                onChange={(e) => setNewBranchName(e.target.value)}
              />
              <DialogFooter>
                <Button onClick={handleCreateBranch} disabled={!newBranchName}>
                  Create Branch
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Save Version Button */}
          <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Save className="h-4 w-4 mr-2" />
                Save Version
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Save Version</DialogTitle>
                <DialogDescription>
                  Create a snapshot of the current design state.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  placeholder="Version label (optional)"
                  value={snapshotLabel}
                  onChange={(e) => setSnapshotLabel(e.target.value)}
                />
                <Textarea
                  placeholder="What changed? (optional)"
                  value={changeSummary}
                  onChange={(e) => setChangeSummary(e.target.value)}
                  rows={3}
                />
              </div>
              <DialogFooter>
                <Button onClick={handleSaveSnapshot} disabled={createSnapshot.isPending}>
                  {createSnapshot.isPending ? 'Saving...' : 'Save'}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Compare Versions */}
      <Card>
        <CardHeader className="py-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Diff className="h-4 w-4" />
            Compare Versions
          </CardTitle>
        </CardHeader>
        <CardContent className="py-3">
          <div className="flex items-center gap-2">
            <Select 
              value={compareFrom?.toString() || ''} 
              onValueChange={(v) => setCompareFrom(parseInt(v))}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="From v..." />
              </SelectTrigger>
              <SelectContent>
                {versions.map((v) => (
                  <SelectItem key={v.version_number} value={v.version_number.toString()}>
                    v{v.version_number}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <ChevronRight className="h-4 w-4" />
            <Select 
              value={compareTo?.toString() || ''} 
              onValueChange={(v) => setCompareTo(parseInt(v))}
            >
              <SelectTrigger className="w-32">
                <SelectValue placeholder="To v..." />
              </SelectTrigger>
              <SelectContent>
                {versions.map((v) => (
                  <SelectItem key={v.version_number} value={v.version_number.toString()}>
                    v{v.version_number}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button 
              size="sm" 
              onClick={handleCompare}
              disabled={!compareFrom || !compareTo || versionDiff.isPending}
            >
              Compare
            </Button>
          </div>

          {/* Diff Results */}
          {versionDiff.data && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">
                Changes: v{versionDiff.data.from_version} → v{versionDiff.data.to_version}
              </h4>
              <div className="flex gap-4 text-sm">
                <span className="text-green-600">
                  +{versionDiff.data.diff.summary.added_count} added
                </span>
                <span className="text-red-600">
                  -{versionDiff.data.diff.summary.removed_count} removed
                </span>
                <span className="text-yellow-600">
                  ~{versionDiff.data.diff.summary.modified_count} modified
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Version List */}
      <Card>
        <CardContent className="py-4">
          {versions.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No versions saved yet. Click "Save Version" to create one.
            </p>
          ) : (
            <div className="space-y-4">
              {versions.map((version) => (
                <div 
                  key={version.id}
                  className="flex items-start gap-4 p-3 border rounded-lg hover:bg-gray-50"
                >
                  {/* Thumbnail */}
                  <div className="w-16 h-12 bg-gray-100 rounded flex items-center justify-center flex-shrink-0">
                    {version.thumbnail_url ? (
                      <img 
                        src={version.thumbnail_url} 
                        alt={`Version ${version.version_number}`}
                        className="w-full h-full object-cover rounded"
                      />
                    ) : (
                      <Layers className="h-6 w-6 text-gray-400" />
                    )}
                  </div>

                  {/* Version Info */}
                  <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">v{version.version_number}</span>
                      {version.version_label && (
                        <Badge variant="outline">{version.version_label}</Badge>
                      )}
                      {version.is_branch_head && (
                        <Badge variant="secondary">HEAD</Badge>
                      )}
                      {getChangeTypeBadge(version.change_type)}
                    </div>
                    <p className="text-sm text-muted-foreground truncate">
                      {version.change_summary || 'No description'}
                    </p>
                    <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {version.created_by_username}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(version.created_at).toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Layers className="h-3 w-3" />
                        {version.components_count} components
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRestore(version.version_number)}
                      disabled={restoreVersion.isPending}
                    >
                      <RotateCcw className="h-4 w-4 mr-1" />
                      Restore
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default VersionHistory;

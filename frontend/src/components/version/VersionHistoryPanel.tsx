/**
 * Version History Panel Component
 * Display and manage project version history
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { GitBranch, GitCommit, GitMerge, Clock, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Commit {
  id: number;
  commit_hash: string;
  message: string;
  author: {
    id: number;
    username: string;
  };
  changes_summary: {
    elements_added: number;
    elements_modified: number;
    elements_deleted: number;
  };
  created_at: string;
}

interface Branch {
  id: number;
  name: string;
  is_main: boolean;
  is_active: boolean;
  created_at: string;
}

export function VersionHistoryPanel({ projectId }: { projectId: number }) {
  const [commits, setCommits] = useState<Commit[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [selectedBranch, setSelectedBranch] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchBranches = useCallback(async () => {
    try {
      // Note: This endpoint needs to be implemented in the backend
      const res = await fetch(`/api/projects/version/branches/?project_id=${projectId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setBranches(data);
        
        // Select main branch by default
        const mainBranch = data.find((b: Branch) => b.is_main);
        if (mainBranch) {
          setSelectedBranch(mainBranch.id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch branches:', error);
    }
  }, [projectId]);

  useEffect(() => {
     
    fetchBranches();
  }, [fetchBranches]);

  const fetchCommits = useCallback(async (branchId: number) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/projects/version/commits/?branch_id=${branchId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setCommits(data);
      }
    } catch (error) {
      console.error('Failed to fetch commits:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedBranch) {
      fetchCommits(selectedBranch);
    }
  }, [selectedBranch, fetchCommits]);

  const handleRestoreCommit = async (commit: Commit) => {
    if (!confirm(`Restore to commit "${commit.message}"?`)) return;

    try {
      const res = await fetch(`/api/projects/version/commits/${commit.id}/restore/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (res.ok) {
        alert('Commit restored successfully!');
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to restore commit:', error);
      alert('Failed to restore commit');
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Version History
        </h2>

        {/* Branch Selector */}
        {branches.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Branch</label>
            <select
              className="w-full border rounded-md p-2 text-sm"
              value={selectedBranch || ''}
              onChange={(e) => setSelectedBranch(parseInt(e.target.value))}
            >
              {branches.map((branch) => (
                <option key={branch.id} value={branch.id}>
                  {branch.name} {branch.is_main && '(main)'}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Commits List */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : commits.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <GitCommit className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No commits yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {commits.map((commit, index) => (
              <Card key={commit.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  {/* Commit Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <GitCommit className="w-4 h-4 text-gray-500" />
                        <span className="font-mono text-xs text-gray-600">
                          {commit.commit_hash.substring(0, 7)}
                        </span>
                        {index === 0 && (
                          <Badge variant="secondary" className="text-xs">
                            Latest
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-sm font-medium mb-1">
                        {commit.message}
                      </p>
                    </div>
                  </div>

                  {/* Author and Time */}
                  <div className="flex items-center gap-4 text-xs text-gray-600 mb-3">
                    <div className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      <span>{commit.author.username}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>
                        {formatDistanceToNow(new Date(commit.created_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>

                  {/* Changes Summary */}
                  {commit.changes_summary && (
                    <div className="flex items-center gap-3 text-xs mb-3">
                      {commit.changes_summary.elements_added > 0 && (
                        <span className="text-green-600">
                          +{commit.changes_summary.elements_added} added
                        </span>
                      )}
                      {commit.changes_summary.elements_modified > 0 && (
                        <span className="text-blue-600">
                          ~{commit.changes_summary.elements_modified} modified
                        </span>
                      )}
                      {commit.changes_summary.elements_deleted > 0 && (
                        <span className="text-red-600">
                          -{commit.changes_summary.elements_deleted} deleted
                        </span>
                      )}
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRestoreCommit(commit)}
                      className="text-xs"
                    >
                      Restore
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs"
                    >
                      View Diff
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t space-y-2">
        <Button variant="outline" className="w-full" size="sm">
          <GitBranch className="w-4 h-4 mr-2" />
          Create Branch
        </Button>
        <Button variant="outline" className="w-full" size="sm">
          <GitMerge className="w-4 h-4 mr-2" />
          Merge Requests
        </Button>
      </div>
    </div>
  );
}

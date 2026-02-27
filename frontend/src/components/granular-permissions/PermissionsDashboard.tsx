'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  Shield, Users, Lock, Eye, EyeOff, Key, UserPlus,
  Settings, Trash2, Edit, Check, X, ChevronDown,
  ChevronRight, Search, Copy, Link2, Clock, AlertTriangle,
  FileText, GitBranch, Layers, MoreVertical, Filter
} from 'lucide-react';

// Types
interface Role {
  id: string;
  name: string;
  description: string;
  level: number;
  isSystemRole: boolean;
  permissions: string[];
  color: string;
}

interface Permission {
  id: string;
  codename: string;
  name: string;
  description: string;
  category: string;
}

interface UserRole {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  userAvatar: string;
  roleId: string;
  roleName: string;
  grantedAt: string;
  grantedBy: string;
}

interface PagePermission {
  id: string;
  pageId: string;
  pageName: string;
  userId: string | null;
  roleId: string | null;
  canView: boolean;
  canEdit: boolean;
  canComment: boolean;
}

interface BranchProtection {
  id: string;
  branchPattern: string;
  requiresReview: boolean;
  requiredApprovers: number;
  restrictPushToRoles: string[];
  allowForcePush: boolean;
  isActive: boolean;
}

interface ShareLink {
  id: string;
  token: string;
  projectId: string;
  permission: 'view' | 'comment' | 'edit';
  password: string | null;
  expiresAt: string | null;
  maxUses: number | null;
  currentUses: number;
  createdAt: string;
  createdBy: string;
  isActive: boolean;
}

interface AccessLog {
  id: string;
  userId: string;
  userName: string;
  action: string;
  resourceType: string;
  resourceId: string;
  resourceName: string;
  timestamp: string;
  ipAddress: string;
}

// Role Badge Component
export function RoleBadge({ role }: { role: Role }) {
  return (
    <span
      className="px-2 py-1 rounded text-xs font-medium"
      style={{ backgroundColor: `${role.color}30`, color: role.color }}
    >
      {role.name}
    </span>
  );
}

// Role Manager Component
export function RoleManager({
  projectId,
  onRoleSelect,
}: {
  projectId: string;
  onRoleSelect?: (role: Role) => void;
}) {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newRole, setNewRole] = useState({ name: '', description: '', color: '#3B82F6' });

  const loadRoles = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/permissions/roles/?project=${projectId}`);
      const data = await response.json();
      setRoles(data.results || data);
    } catch (error) {
      console.error('Failed to load roles:', error);
    }
  }, [projectId]);

  const createRole = async () => {
    try {
      const response = await fetch('/api/v1/permissions/roles/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newRole, project_id: projectId }),
      });
      const data = await response.json();
      setRoles([...roles, data]);
      setIsCreating(false);
      setNewRole({ name: '', description: '', color: '#3B82F6' });
    } catch (error) {
      console.error('Failed to create role', error);
    }
  };

  useEffect(() => {
    const loadRolesAsync = async () => {
      await loadRoles();
    };
    loadRolesAsync();
  }, [projectId, loadRoles]);

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Shield className="w-5 h-5 text-blue-400" />
          Roles
        </h3>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
        >
          <UserPlus className="w-4 h-4" />
          Add Role
        </button>
      </div>

      <div className="space-y-2">
        {roles.map((role) => (
          <div
            key={role.id}
            onClick={() => {
              setSelectedRole(role);
              onRoleSelect?.(role);
            }}
            className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors ${
              selectedRole?.id === role.id
                ? 'bg-blue-600/20 border border-blue-500'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: role.color }}
              />
              <div>
                <div className="font-medium">{role.name}</div>
                <div className="text-xs text-gray-400">{role.description}</div>
              </div>
            </div>
            {role.isSystemRole && (
              <Lock className="w-4 h-4 text-gray-500" />
            )}
          </div>
        ))}
      </div>

      {/* Create Role Modal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md">
            <h3 className="font-semibold text-lg mb-4">Create Custom Role</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Role Name
                </label>
                <input
                  type="text"
                  value={newRole.name}
                  onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                  placeholder="e.g., Developer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={newRole.description}
                  onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                  placeholder="What can this role do?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Color
                </label>
                <div className="flex gap-2">
                  {['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'].map((color) => (
                    <button
                      key={color}
                      onClick={() => setNewRole({ ...newRole, color })}
                      className={`w-8 h-8 rounded-full ${
                        newRole.color === color ? 'ring-2 ring-white ring-offset-2 ring-offset-gray-900' : ''
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setIsCreating(false)}
                className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createRole}
                disabled={!newRole.name}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Permission Matrix Component
export function PermissionMatrix({
  roleId,
  permissions,
  grantedPermissions,
  onToggle,
}: {
  roleId: string;
  permissions: Permission[];
  grantedPermissions: string[];
  onToggle: (permissionId: string, granted: boolean) => void;
}) {
  const groupedPermissions = permissions.reduce((acc, perm) => {
    if (!acc[perm.category]) acc[perm.category] = [];
    acc[perm.category].push(perm);
    return acc;
  }, {} as Record<string, Permission[]>);

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Key className="w-5 h-5 text-amber-400" />
        Permissions
      </h3>

      <div className="space-y-6">
        {Object.entries(groupedPermissions).map(([category, perms]) => (
          <div key={category}>
            <h4 className="text-sm font-medium text-gray-400 mb-2 uppercase">
              {category}
            </h4>
            <div className="space-y-2">
              {perms.map((perm) => {
                const isGranted = grantedPermissions.includes(perm.id);
                return (
                  <label
                    key={perm.id}
                    className="flex items-center justify-between p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-650"
                  >
                    <div>
                      <div className="font-medium text-sm">{perm.name}</div>
                      <div className="text-xs text-gray-400">{perm.description}</div>
                    </div>
                    <input
                      type="checkbox"
                      checked={isGranted}
                      onChange={(e) => onToggle(perm.id, e.target.checked)}
                      className="w-5 h-5 rounded bg-gray-600 border-gray-500"
                    />
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Share Link Manager Component
export function ShareLinkManager({ projectId }: { projectId: string }) {
  const [links, setLinks] = useState<ShareLink[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [newLink, setNewLink] = useState({
    permission: 'view' as 'view' | 'comment' | 'edit',
    password: '',
    expiresIn: '',
    maxUses: '',
  });

  const loadLinks = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/permissions/share-links/?project=${projectId}`);
      const data = await response.json();
      setLinks(data.results || data);
    } catch (error) {
      setLinks([
        {
          id: '1',
          token: 'abc123xyz',
          projectId,
          permission: 'view',
          password: null,
          expiresAt: null,
          maxUses: null,
          currentUses: 45,
          createdAt: new Date().toISOString(),
          createdBy: 'John Doe',
          isActive: true,
        },
      ]);
    }
  }, [projectId]);

  const createLink = async () => {
    try {
      const response = await fetch('/api/v1/permissions/share-links/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          permission: newLink.permission,
          password: newLink.password || null,
          expires_in_days: newLink.expiresIn ? parseInt(newLink.expiresIn) : null,
          max_uses: newLink.maxUses ? parseInt(newLink.maxUses) : null,
        }),
      });
      const data = await response.json();
      setLinks([data, ...links]);
      setIsCreating(false);
      setNewLink({ permission: 'view', password: '', expiresIn: '', maxUses: '' });
    } catch (error) {
      console.error('Failed to create link', error);
    }
  };

  const copyLink = (link: ShareLink) => {
    const url = `${window.location.origin}/share/${link.token}`;
    navigator.clipboard.writeText(url);
  };

  const toggleLink = async (linkId: string, isActive: boolean) => {
    setLinks(links.map(l => l.id === linkId ? { ...l, isActive } : l));
    try {
      await fetch(`/api/v1/permissions/share-links/${linkId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: isActive }),
      });
    } catch (error) {
      console.error('Failed to toggle link', error);
    }
  };

  useEffect(() => {
    const loadLinksAsync = async () => {
      await loadLinks();
    };
    loadLinksAsync();
  }, [projectId, loadLinks]);

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Link2 className="w-5 h-5 text-green-400" />
          Share Links
        </h3>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-1 px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded-lg text-sm"
        >
          <Link2 className="w-4 h-4" />
          Create Link
        </button>
      </div>

      <div className="space-y-3">
        {links.map((link) => (
          <div
            key={link.id}
            className={`p-3 rounded-lg ${
              link.isActive ? 'bg-gray-700' : 'bg-gray-700/50'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 rounded text-xs ${
                    link.permission === 'edit'
                      ? 'bg-blue-600'
                      : link.permission === 'comment'
                      ? 'bg-purple-600'
                      : 'bg-gray-600'
                  }`}
                >
                  {link.permission}
                </span>
                {link.password && <Lock className="w-3 h-3 text-amber-400" />}
                {link.expiresAt && <Clock className="w-3 h-3 text-gray-400" />}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => copyLink(link)}
                  className="p-1.5 hover:bg-gray-600 rounded"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={link.isActive}
                    onChange={(e) => toggleLink(link.id, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-gray-600 peer-checked:bg-green-600 rounded-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4" />
                </label>
              </div>
            </div>
            <div className="text-xs text-gray-400">
              Used {link.currentUses}{link.maxUses ? ` of ${link.maxUses}` : ''} times
              {' • '}Created by {link.createdBy}
            </div>
          </div>
        ))}
      </div>

      {/* Create Link Modal */}
      {isCreating && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 rounded-xl p-6 w-full max-w-md">
            <h3 className="font-semibold text-lg mb-4">Create Share Link</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Permission Level
                </label>
                <select
                  value={newLink.permission}
                  onChange={(e) => setNewLink({ ...newLink, permission: e.target.value as 'view' | 'comment' | 'edit' })}
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                >
                  <option value="view">View Only</option>
                  <option value="comment">Can Comment</option>
                  <option value="edit">Can Edit</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Password (optional)
                </label>
                <input
                  type="password"
                  value={newLink.password}
                  onChange={(e) => setNewLink({ ...newLink, password: e.target.value })}
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                  placeholder="Leave empty for no password"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Expires in (days)
                  </label>
                  <input
                    type="number"
                    value={newLink.expiresIn}
                    onChange={(e) => setNewLink({ ...newLink, expiresIn: e.target.value })}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                    placeholder="Never"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">
                    Max uses
                  </label>
                  <input
                    type="number"
                    value={newLink.maxUses}
                    onChange={(e) => setNewLink({ ...newLink, maxUses: e.target.value })}
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
                    placeholder="Unlimited"
                  />
                </div>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setIsCreating(false)}
                className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={createLink}
                className="flex-1 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
              >
                Create Link
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Branch Protection Component
export function BranchProtectionSettings({ projectId }: { projectId: string }) {
  const [rules, setRules] = useState<BranchProtection[]>([]);
  const [isCreating, setIsCreating] = useState(false);

  const loadRules = async () => {
    try {
      const response = await fetch(`/api/v1/permissions/branch-protection/?project=${projectId}`);
      const data = await response.json();
      setRules(data.results || data);
    } catch (error) {
      setRules([
        {
          id: '1',
          branchPattern: 'main',
          requiresReview: true,
          requiredApprovers: 2,
          restrictPushToRoles: ['admin', 'owner'],
          allowForcePush: false,
          isActive: true,
        },
        {
          id: '2',
          branchPattern: 'release/*',
          requiresReview: true,
          requiredApprovers: 1,
          restrictPushToRoles: ['admin', 'owner', 'editor'],
          allowForcePush: false,
          isActive: true,
        },
      ]);
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-purple-400" />
          Branch Protection
        </h3>
        <button
          onClick={() => setIsCreating(true)}
          className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm"
        >
          <Shield className="w-4 h-4" />
          Add Rule
        </button>
      </div>

      <div className="space-y-3">
        {rules.map((rule) => (
          <div
            key={rule.id}
            className={`p-4 rounded-lg ${
              rule.isActive ? 'bg-gray-700' : 'bg-gray-700/50'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-purple-400" />
                <span className="font-mono font-medium">{rule.branchPattern}</span>
              </div>
              <div className="flex items-center gap-2">
                {!rule.allowForcePush && (
                  <span className="px-2 py-0.5 bg-red-600/30 text-red-400 rounded text-xs">
                    No Force Push
                  </span>
                )}
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rule.isActive}
                    onChange={(e) => {
                      setRules(rules.map(r => r.id === rule.id ? { ...r, isActive: e.target.checked } : r));
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-gray-600 peer-checked:bg-purple-600 rounded-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4" />
                </label>
              </div>
            </div>
            <div className="text-sm text-gray-400 space-y-1">
              {rule.requiresReview && (
                <div className="flex items-center gap-1">
                  <Check className="w-3 h-3 text-green-400" />
                  Requires {rule.requiredApprovers} approver{rule.requiredApprovers > 1 ? 's' : ''}
                </div>
              )}
              <div className="flex items-center gap-1">
                <Lock className="w-3 h-3 text-amber-400" />
                Push restricted to: {rule.restrictPushToRoles.join(', ')}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Access Logs Component
export function AccessLogs({ projectId }: { projectId: string }) {
  const [logs, setLogs] = useState<AccessLog[]>([]);
  const [filter, setFilter] = useState('');

  const loadLogs = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/permissions/access-logs/?project=${projectId}`);
      const data = await response.json();
      setLogs(data.results || data);
    } catch (error) {
      setLogs([
        { id: '1', userId: '1', userName: 'John Doe', action: 'view', resourceType: 'page', resourceId: '1', resourceName: 'Homepage', timestamp: new Date().toISOString(), ipAddress: '192.168.1.1' },
        { id: '2', userId: '2', userName: 'Jane Smith', action: 'edit', resourceType: 'component', resourceId: '2', resourceName: 'Button', timestamp: new Date().toISOString(), ipAddress: '192.168.1.2' },
        { id: '3', userId: '1', userName: 'John Doe', action: 'share', resourceType: 'project', resourceId: projectId, resourceName: 'My Project', timestamp: new Date().toISOString(), ipAddress: '192.168.1.1' },
      ]);
    }
  }, [projectId]);

  useEffect(() => {
    const loadLogsAsync = async () => {
      await loadLogs();
    };
    loadLogsAsync();
  }, [projectId, loadLogs]);

  const getActionColor = (action: string) => {
    switch (action) {
      case 'view': return 'text-gray-400';
      case 'edit': return 'text-blue-400';
      case 'delete': return 'text-red-400';
      case 'share': return 'text-green-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-400" />
          Access Logs
        </h3>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter logs..."
            className="pl-9 pr-4 py-1.5 bg-gray-700 border border-gray-600 rounded-lg text-sm"
          />
        </div>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {logs.map((log) => (
          <div key={log.id} className="flex items-center gap-3 p-2 bg-gray-700/50 rounded-lg text-sm">
            <div className="flex-1">
              <span className="font-medium">{log.userName}</span>
              <span className={`mx-2 ${getActionColor(log.action)}`}>{log.action}</span>
              <span className="text-gray-400">{log.resourceName}</span>
            </div>
            <div className="text-xs text-gray-500">
              {new Date(log.timestamp).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Main Permissions Dashboard
export function PermissionsDashboard({ projectId }: { projectId: string }) {
  const [activeTab, setActiveTab] = useState<'roles' | 'sharing' | 'branches' | 'logs'>('roles');
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [permissions, setPermissions] = useState<Permission[]>([
    { id: '1', codename: 'view', name: 'View', description: 'View designs and pages', category: 'Basic' },
    { id: '2', codename: 'comment', name: 'Comment', description: 'Add comments and feedback', category: 'Basic' },
    { id: '3', codename: 'edit', name: 'Edit', description: 'Edit designs and components', category: 'Design' },
    { id: '4', codename: 'export', name: 'Export', description: 'Export designs and assets', category: 'Design' },
    { id: '5', codename: 'manage_team', name: 'Manage Team', description: 'Add and remove team members', category: 'Admin' },
    { id: '6', codename: 'manage_settings', name: 'Manage Settings', description: 'Change project settings', category: 'Admin' },
  ]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-400" />
          Permissions & Access
        </h1>

        {/* Tabs */}
        <div className="flex border-b border-gray-700 mb-6">
          {[
            { id: 'roles', label: 'Roles', icon: Users },
            { id: 'sharing', label: 'Sharing', icon: Link2 },
            { id: 'branches', label: 'Branch Protection', icon: GitBranch },
            { id: 'logs', label: 'Access Logs', icon: FileText },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as 'branches' | 'roles' | 'logs' | 'sharing')}
              className={`flex items-center gap-2 px-6 py-3 font-medium transition-colors ${
                activeTab === id
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'roles' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RoleManager
              projectId={projectId}
              onRoleSelect={setSelectedRole}
            />
            {selectedRole && (
              <PermissionMatrix
                roleId={selectedRole.id}
                permissions={permissions}
                grantedPermissions={selectedRole.permissions}
                onToggle={(permId, granted) => {
                  console.log('Toggle permission', permId, granted);
                }}
              />
            )}
          </div>
        )}

        {activeTab === 'sharing' && (
          <ShareLinkManager projectId={projectId} />
        )}

        {activeTab === 'branches' && (
          <BranchProtectionSettings projectId={projectId} />
        )}

        {activeTab === 'logs' && (
          <AccessLogs projectId={projectId} />
        )}
      </div>
    </div>
  );
}

export default PermissionsDashboard;

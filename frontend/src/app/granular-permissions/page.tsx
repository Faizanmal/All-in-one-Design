"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Lock,
  Plus,
  Search,
  Users,
  Shield,
  Edit2,
  Trash2,
  ChevronRight,
  Check,
  X,
  Crown,
  UserPlus,
  Key,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// Types
interface TeamMember {
  id: number;
  name: string;
  email: string;
  avatar?: string;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  lastActive: string;
}

interface Permission {
  id: string;
  name: string;
  description: string;
  category: string;
}

interface Role {
  id: string;
  name: string;
  color: string;
  permissions: string[];
  memberCount: number;
}

// Mock Data
const mockMembers: TeamMember[] = [
  { id: 1, name: 'Sarah Chen', email: 'sarah@company.com', role: 'owner', lastActive: 'Now', avatar: '' },
  { id: 2, name: 'Alex Rivera', email: 'alex@company.com', role: 'admin', lastActive: '5 min ago', avatar: '' },
  { id: 3, name: 'Jordan Kim', email: 'jordan@company.com', role: 'editor', lastActive: '1 hour ago', avatar: '' },
  { id: 4, name: 'Casey Morgan', email: 'casey@company.com', role: 'editor', lastActive: '2 hours ago', avatar: '' },
  { id: 5, name: 'Taylor Swift', email: 'taylor@company.com', role: 'viewer', lastActive: '1 day ago', avatar: '' },
];

const permissions: Permission[] = [
  { id: 'view_projects', name: 'View Projects', description: 'Can view all projects in workspace', category: 'Projects' },
  { id: 'create_projects', name: 'Create Projects', description: 'Can create new projects', category: 'Projects' },
  { id: 'edit_projects', name: 'Edit Projects', description: 'Can edit existing projects', category: 'Projects' },
  { id: 'delete_projects', name: 'Delete Projects', description: 'Can delete projects', category: 'Projects' },
  { id: 'view_assets', name: 'View Assets', description: 'Can view shared assets', category: 'Assets' },
  { id: 'upload_assets', name: 'Upload Assets', description: 'Can upload new assets', category: 'Assets' },
  { id: 'delete_assets', name: 'Delete Assets', description: 'Can delete assets', category: 'Assets' },
  { id: 'manage_members', name: 'Manage Members', description: 'Can invite and remove members', category: 'Team' },
  { id: 'manage_roles', name: 'Manage Roles', description: 'Can create and edit roles', category: 'Team' },
  { id: 'export_designs', name: 'Export Designs', description: 'Can export designs', category: 'Export' },
  { id: 'share_links', name: 'Share Links', description: 'Can create share links', category: 'Export' },
];

const roles: Role[] = [
  { id: 'owner', name: 'Owner', color: 'bg-purple-100 text-purple-700', permissions: permissions.map(p => p.id), memberCount: 1 },
  { id: 'admin', name: 'Admin', color: 'bg-blue-100 text-blue-700', permissions: permissions.filter(p => p.id !== 'delete_projects' && p.id !== 'manage_roles').map(p => p.id), memberCount: 1 },
  { id: 'editor', name: 'Editor', color: 'bg-green-100 text-green-700', permissions: ['view_projects', 'edit_projects', 'view_assets', 'upload_assets', 'export_designs'], memberCount: 2 },
  { id: 'viewer', name: 'Viewer', color: 'bg-gray-100 text-gray-700', permissions: ['view_projects', 'view_assets'], memberCount: 1 },
];

const getRoleColor = (role: string) => {
  switch (role) {
    case 'owner': return 'bg-purple-100 text-purple-700';
    case 'admin': return 'bg-blue-100 text-blue-700';
    case 'editor': return 'bg-green-100 text-green-700';
    case 'viewer': return 'bg-gray-100 text-gray-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

// Member Row Component
function MemberRow({ member, onEdit, onRemove }: { member: TeamMember; onEdit: () => void; onRemove: () => void }) {
  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded-lg border border-gray-200 hover:shadow-sm transition-shadow group">
      <Avatar className="h-10 w-10">
        <AvatarImage src={member.avatar} />
        <AvatarFallback className="bg-blue-100 text-blue-700">{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
      </Avatar>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="font-medium text-gray-900">{member.name}</p>
          {member.role === 'owner' && <Crown className="h-4 w-4 text-amber-500" />}
        </div>
        <p className="text-sm text-gray-500 truncate">{member.email}</p>
      </div>
      <Badge className={getRoleColor(member.role)}>{member.role}</Badge>
      <span className="text-sm text-gray-400 w-24">{member.lastActive}</span>
      <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
        <Button size="sm" variant="ghost" onClick={onEdit}><Edit2 className="h-4 w-4" /></Button>
        {member.role !== 'owner' && (
          <Button size="sm" variant="ghost" className="text-red-600" onClick={onRemove}><Trash2 className="h-4 w-4" /></Button>
        )}
      </div>
    </div>
  );
}

// Role Card Component
function RoleCard({ role, onEdit }: { role: Role; onEdit: () => void }) {
  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={onEdit}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div>
            <Badge className={role.color}>{role.name}</Badge>
            <p className="text-sm text-gray-500 mt-2">{role.memberCount} members</p>
          </div>
          <Shield className="h-5 w-5 text-gray-400" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">{role.permissions.length} permissions</span>
          <ChevronRight className="h-4 w-4 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function GranularPermissionsPage() {
  const { toast } = useToast();
  const [members] = useState<TeamMember[]>(mockMembers);
  const [searchQuery, setSearchQuery] = useState('');
  const [showInvite, setShowInvite] = useState(false);
  const [showRoleEditor, setShowRoleEditor] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  const filteredMembers = members.filter(m => 
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleInvite = () => {
    setShowInvite(false);
    toast({ title: 'Invitation Sent', description: 'Team member has been invited' });
  };

  const handleEditRole = (role: Role) => {
    setSelectedRole(role);
    setShowRoleEditor(true);
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
                  <Lock className="h-7 w-7 text-blue-600" />Granular Permissions
                </h1>
                <p className="text-gray-500">Manage team access and role-based permissions</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Key className="h-4 w-4 mr-2" />Create Role</Button>
                <Button onClick={() => setShowInvite(true)}><UserPlus className="h-4 w-4 mr-2" />Invite Member</Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg"><Users className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Team Members</p>
                    <p className="text-2xl font-bold text-gray-900">{members.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg"><Shield className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Roles</p>
                    <p className="text-2xl font-bold text-gray-900">{roles.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg"><Check className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Permissions</p>
                    <p className="text-2xl font-bold text-gray-900">{permissions.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-amber-100 rounded-lg"><Crown className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Admins</p>
                    <p className="text-2xl font-bold text-gray-900">{members.filter(m => m.role === 'owner' || m.role === 'admin').length}</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <Tabs defaultValue="members" className="flex-1 flex flex-col overflow-hidden">
              <TabsList className="w-fit mb-4">
                <TabsTrigger value="members">Team Members</TabsTrigger>
                <TabsTrigger value="roles">Roles & Permissions</TabsTrigger>
              </TabsList>

              <TabsContent value="members" className="flex-1 overflow-hidden mt-0">
                <div className="mb-4">
                  <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input placeholder="Search members..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-10" />
                  </div>
                </div>
                <ScrollArea className="flex-1">
                  <div className="space-y-3 pr-4">
                    {filteredMembers.map(member => (
                      <MemberRow key={member.id} member={member} onEdit={() => {}} onRemove={() => toast({ title: 'Member Removed' })} />
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>

              <TabsContent value="roles" className="flex-1 overflow-hidden mt-0">
                <div className="grid grid-cols-3 gap-6 h-full">
                  {/* Roles List */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Roles</h3>
                    {roles.map(role => (
                      <RoleCard key={role.id} role={role} onEdit={() => handleEditRole(role)} />
                    ))}
                    <Button variant="outline" className="w-full"><Plus className="h-4 w-4 mr-2" />Create Role</Button>
                  </div>

                  {/* Permissions Matrix */}
                  <div className="col-span-2 bg-white rounded-xl border border-gray-200 p-4 overflow-auto">
                    <h3 className="font-semibold text-gray-900 mb-4">Permission Matrix</h3>
                    <table className="w-full">
                      <thead>
                        <tr>
                          <th className="text-left text-sm font-medium text-gray-500 pb-3">Permission</th>
                          {roles.map(role => (
                            <th key={role.id} className="text-center text-sm font-medium text-gray-500 pb-3 w-24">
                              <Badge className={role.color}>{role.name}</Badge>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {permissions.map(perm => (
                          <tr key={perm.id} className="border-t border-gray-100">
                            <td className="py-3">
                              <p className="text-sm font-medium text-gray-900">{perm.name}</p>
                              <p className="text-xs text-gray-500">{perm.description}</p>
                            </td>
                            {roles.map(role => (
                              <td key={role.id} className="text-center py-3">
                                {role.permissions.includes(perm.id) ? (
                                  <Check className="h-5 w-5 text-green-500 mx-auto" />
                                ) : (
                                  <X className="h-5 w-5 text-gray-300 mx-auto" />
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>

      {/* Invite Member Dialog */}
      <Dialog open={showInvite} onOpenChange={setShowInvite}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Invite Team Member</DialogTitle>
            <DialogDescription>Send an invitation to join your workspace</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Email Address</Label>
              <Input type="email" placeholder="colleague@company.com" className="mt-1" />
            </div>
            <div>
              <Label>Role</Label>
              <Select defaultValue="editor">
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  {roles.filter(r => r.id !== 'owner').map(role => (
                    <SelectItem key={role.id} value={role.id}>{role.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Personal Message (optional)</Label>
              <Input placeholder="Welcome to the team!" className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowInvite(false)}>Cancel</Button>
            <Button onClick={handleInvite}>Send Invitation</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Role Editor Dialog */}
      <Dialog open={showRoleEditor} onOpenChange={setShowRoleEditor}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Role: {selectedRole?.name}</DialogTitle>
            <DialogDescription>Configure permissions for this role</DialogDescription>
          </DialogHeader>
          {selectedRole && (
            <div className="space-y-4 py-4 max-h-96 overflow-auto">
              {['Projects', 'Assets', 'Team', 'Export'].map(category => (
                <div key={category}>
                  <h4 className="font-medium text-gray-900 mb-2">{category}</h4>
                  <div className="space-y-2">
                    {permissions.filter(p => p.category === category).map(perm => (
                      <div key={perm.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                        <div>
                          <p className="text-sm font-medium text-gray-700">{perm.name}</p>
                          <p className="text-xs text-gray-500">{perm.description}</p>
                        </div>
                        <Switch checked={selectedRole.permissions.includes(perm.id)} />
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRoleEditor(false)}>Cancel</Button>
            <Button onClick={() => { setShowRoleEditor(false); toast({ title: 'Role Updated' }); }}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

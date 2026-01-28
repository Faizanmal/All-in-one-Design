"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Shield, Users, Link, Eye, Clock, UserCheck, Lock } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  avatar: string;
}

interface Role {
  id: number;
  name: string;
  color: string;
  users: number;
  permissions: string[];
}

export const PermissionsDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-6 w-6" />
            Permissions & Access Control
          </CardTitle>
          <CardDescription>Manage team roles, permissions, and access levels</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="roles">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="roles">Roles</TabsTrigger>
              <TabsTrigger value="permissions">Permissions</TabsTrigger>
              <TabsTrigger value="links">Share Links</TabsTrigger>
              <TabsTrigger value="logs">Activity Logs</TabsTrigger>
            </TabsList>
            <TabsContent value="roles">
              <RoleManager />
            </TabsContent>
            <TabsContent value="permissions">
              <PermissionMatrix />
            </TabsContent>
            <TabsContent value="links">
              <ShareLinkManager />
            </TabsContent>
            <TabsContent value="logs">
              <AccessLogs />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export const RoleManager: React.FC = () => {
  const roles: Role[] = [
    { id: 1, name: 'Owner', color: 'purple', users: 1, permissions: ['all'] },
    { id: 2, name: 'Admin', color: 'blue', users: 3, permissions: ['edit', 'comment', 'share'] },
    { id: 3, name: 'Editor', color: 'green', users: 8, permissions: ['edit', 'comment'] },
    { id: 4, name: 'Viewer', color: 'gray', users: 15, permissions: ['view', 'comment'] },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">Manage team roles and their permissions</p>
        <Button size="sm">Create Role</Button>
      </div>

      <div className="grid gap-4">
        {roles.map((role) => (
          <Card key={role.id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <RoleBadge role={role.name} color={role.color} />
                  <div>
                    <p className="font-medium">{role.name}</p>
                    <p className="text-sm text-muted-foreground">{role.users} users</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Edit</Button>
                  <Button variant="ghost" size="sm">Delete</Button>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                {role.permissions.map((perm) => (
                  <Badge key={perm} variant="secondary">{perm}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const RoleBadge: React.FC<{ role: string; color?: string }> = ({ role, color = 'blue' }) => {
  const colorMap: Record<string, string> = {
    purple: 'bg-purple-500',
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    gray: 'bg-gray-500',
  };

  return (
    <div className="flex items-center gap-2">
      <div className={`h-8 w-8 rounded-full ${colorMap[color] || 'bg-blue-500'} flex items-center justify-center`}>
        <Shield className="h-4 w-4 text-white" />
      </div>
      <Badge variant="outline">{role}</Badge>
    </div>
  );
};

export const PermissionMatrix: React.FC = () => {
  const permissions = [
    { name: 'View Project', owner: true, admin: true, editor: true, viewer: true },
    { name: 'Edit Design', owner: true, admin: true, editor: true, viewer: false },
    { name: 'Delete Elements', owner: true, admin: true, editor: false, viewer: false },
    { name: 'Manage Team', owner: true, admin: true, editor: false, viewer: false },
    { name: 'Export Assets', owner: true, admin: true, editor: true, viewer: false },
    { name: 'Add Comments', owner: true, admin: true, editor: true, viewer: true },
    { name: 'Share Project', owner: true, admin: true, editor: false, viewer: false },
    { name: 'Billing Access', owner: true, admin: false, editor: false, viewer: false },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">Permission matrix for all roles</p>
        <Button variant="outline" size="sm">Export</Button>
      </div>

      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Permission</TableHead>
              <TableHead className="text-center">Owner</TableHead>
              <TableHead className="text-center">Admin</TableHead>
              <TableHead className="text-center">Editor</TableHead>
              <TableHead className="text-center">Viewer</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {permissions.map((perm, index) => (
              <TableRow key={index}>
                <TableCell className="font-medium">{perm.name}</TableCell>
                <TableCell className="text-center">
                  {perm.owner ? <UserCheck className="h-4 w-4 text-green-500 mx-auto" /> : <div className="h-4 w-4 mx-auto" />}
                </TableCell>
                <TableCell className="text-center">
                  {perm.admin ? <UserCheck className="h-4 w-4 text-green-500 mx-auto" /> : <div className="h-4 w-4 mx-auto" />}
                </TableCell>
                <TableCell className="text-center">
                  {perm.editor ? <UserCheck className="h-4 w-4 text-green-500 mx-auto" /> : <div className="h-4 w-4 mx-auto" />}
                </TableCell>
                <TableCell className="text-center">
                  {perm.viewer ? <UserCheck className="h-4 w-4 text-green-500 mx-auto" /> : <div className="h-4 w-4 mx-auto" />}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export const ShareLinkManager: React.FC = () => {
  const { toast } = useToast();
  const [links, setLinks] = useState([
    { id: 1, name: 'Design Review Link', access: 'View', expires: '7 days', views: 45 },
    { id: 2, name: 'Client Feedback', access: 'Comment', expires: '30 days', views: 12 },
  ]);

  const copyLink = (linkId: number) => {
    navigator.clipboard.writeText(`https://app.example.com/share/${linkId}`);
    toast({ title: "Link copied", description: "Share link copied to clipboard" });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">Create and manage shareable links</p>
        <Dialog>
          <DialogTrigger asChild>
            <Button size="sm">
              <Link className="h-4 w-4 mr-2" />
              Create Link
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Share Link</DialogTitle>
              <DialogDescription>Generate a shareable link with custom permissions</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Link Name</Label>
                <Input placeholder="e.g., Client Review" />
              </div>
              <div className="space-y-2">
                <Label>Access Level</Label>
                <Select defaultValue="view">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="view">View Only</SelectItem>
                    <SelectItem value="comment">View & Comment</SelectItem>
                    <SelectItem value="edit">Edit Access</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Expiration</Label>
                <Select defaultValue="7">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 day</SelectItem>
                    <SelectItem value="7">7 days</SelectItem>
                    <SelectItem value="30">30 days</SelectItem>
                    <SelectItem value="never">Never</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between">
                <Label>Require password</Label>
                <Switch />
              </div>
              <Button className="w-full" onClick={() => {
                toast({ title: "Link created", description: "Share link has been generated" });
              }}>
                Generate Link
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="space-y-3">
        {links.map((link) => (
          <Card key={link.id}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="font-medium">{link.name}</p>
                    <Badge variant="outline">{link.access}</Badge>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Expires in {link.expires}
                    </div>
                    <div className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      {link.views} views
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => copyLink(link.id)}>
                    Copy
                  </Button>
                  <Button variant="ghost" size="sm">Revoke</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const BranchProtectionSettings: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lock className="h-5 w-5" />
          Branch Protection
        </CardTitle>
        <CardDescription>Protect important branches from unwanted changes</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Label>Require review before merge</Label>
            <p className="text-sm text-muted-foreground">At least one approval required</p>
          </div>
          <Switch defaultChecked />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <Label>Lock main branch</Label>
            <p className="text-sm text-muted-foreground">Prevent direct commits to main</p>
          </div>
          <Switch defaultChecked />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <Label>Auto-merge on approval</Label>
            <p className="text-sm text-muted-foreground">Automatically merge approved branches</p>
          </div>
          <Switch />
        </div>
      </CardContent>
    </Card>
  );
};

export const AccessLogs: React.FC = () => {
  const logs = [
    { id: 1, user: 'John Doe', action: 'Edited design', resource: 'Homepage', time: '2 mins ago' },
    { id: 2, user: 'Jane Smith', action: 'Added comment', resource: 'Mobile App', time: '15 mins ago' },
    { id: 3, user: 'Mike Johnson', action: 'Exported assets', resource: 'Brand Kit', time: '1 hour ago' },
    { id: 4, user: 'Sarah Williams', action: 'Shared project', resource: 'Dashboard', time: '2 hours ago' },
    { id: 5, user: 'Tom Brown', action: 'Changed permissions', resource: 'Team Settings', time: '3 hours ago' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-sm text-muted-foreground">Recent team activity and access logs</p>
        <Button variant="outline" size="sm">Export Logs</Button>
      </div>

      <ScrollArea className="h-[400px]">
        <div className="space-y-2">
          {logs.map((log) => (
            <Card key={log.id}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                      {log.user.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <p className="font-medium">{log.user}</p>
                      <p className="text-sm text-muted-foreground">
                        {log.action} • {log.resource}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {log.time}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};
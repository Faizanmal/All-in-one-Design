"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { MessageSquare, Bell, Share2, Check, X } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export const SlackIntegration: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [workspace, setWorkspace] = useState('');
  const { toast } = useToast();

  const handleConnect = () => {
    setIsConnected(true);
    toast({ title: "Connected to Slack", description: "Successfully connected to workspace" });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Slack Integration
            </CardTitle>
            <CardDescription>Connect your Slack workspace for team collaboration</CardDescription>
          </div>
          <Badge variant={isConnected ? "default" : "secondary"}>
            {isConnected ? "Connected" : "Not Connected"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {!isConnected ? (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="workspace">Workspace URL</Label>
              <Input
                id="workspace"
                placeholder="your-workspace.slack.com"
                value={workspace}
                onChange={(e) => setWorkspace(e.target.value)}
              />
            </div>
            <Button onClick={handleConnect} className="w-full">
              Connect to Slack
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <p className="font-medium">Workspace: Design Team</p>
                <p className="text-sm text-muted-foreground">Connected as @johndoe</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setIsConnected(false)}>
                Disconnect
              </Button>
            </div>
            <Separator />
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Send notifications to #design</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Daily design summaries</Label>
                <Switch />
              </div>
              <div className="flex items-center justify-between">
                <Label>Comment notifications</Label>
                <Switch defaultChecked />
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const TeamsIntegration: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const { toast } = useToast();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Microsoft Teams Integration
            </CardTitle>
            <CardDescription>Connect Teams for seamless collaboration</CardDescription>
          </div>
          <Badge variant={isConnected ? "default" : "secondary"}>
            {isConnected ? "Connected" : "Not Connected"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {!isConnected ? (
          <Button onClick={() => { setIsConnected(true); toast({ title: "Connected to Teams" }); }} className="w-full">
            Connect to Microsoft Teams
          </Button>
        ) : (
          <div className="space-y-4">
            <div className="p-4 border rounded-lg">
              <p className="font-medium">Team: Product Design</p>
              <p className="text-sm text-muted-foreground">Channel: General</p>
            </div>
            <Button variant="outline" onClick={() => setIsConnected(false)}>
              Disconnect
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export const NotificationPreferences: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notification Preferences
        </CardTitle>
        <CardDescription>Customize how and when you receive notifications</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Design comments</Label>
              <p className="text-sm text-muted-foreground">Get notified when someone comments</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>Mentions</Label>
              <p className="text-sm text-muted-foreground">When you are mentioned in a comment</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>Project updates</Label>
              <p className="text-sm text-muted-foreground">Updates to projects you follow</p>
            </div>
            <Switch />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>Weekly digest</Label>
              <p className="text-sm text-muted-foreground">Summary of activity every Monday</p>
            </div>
            <Switch defaultChecked />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const ShareToChannelDialog: React.FC = () => {
  const [selectedChannel, setSelectedChannel] = useState('');
  const { toast } = useToast();

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Share2 className="h-4 w-4 mr-2" />
          Share to Channel
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Share to Channel</DialogTitle>
          <DialogDescription>Choose a channel to share your design</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Select Channel</Label>
            <Select value={selectedChannel} onValueChange={setSelectedChannel}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a channel" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="general">#general</SelectItem>
                <SelectItem value="design">#design</SelectItem>
                <SelectItem value="product">#product</SelectItem>
                <SelectItem value="feedback">#feedback</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Message (optional)</Label>
            <Input placeholder="Add a message..." />
          </div>
          <Button
            className="w-full"
            onClick={() => {
              toast({ title: "Shared successfully", description: `Design shared to ${selectedChannel}` });
            }}
          >
            Share
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const IntegrationSettings: React.FC = () => {
  return (
    <div className="space-y-6">
      <SlackIntegration />
      <TeamsIntegration />
      <NotificationPreferences />
    </div>
  );
};
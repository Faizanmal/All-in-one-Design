"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { WifiOff, Wifi, Download, Upload, HardDrive, RefreshCw, Clock, Check } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export const OfflineStatusBadge: React.FC = () => {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <Badge variant={isOnline ? "default" : "destructive"} className="gap-2">
      {isOnline ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
      {isOnline ? 'Online' : 'Offline'}
    </Badge>
  );
};

export const OfflineProjectsManager: React.FC = () => {
  const [projects, setProjects] = useState([
    { id: 1, name: 'Mobile App Design', size: '45 MB', synced: true, lastSync: '2 mins ago' },
    { id: 2, name: 'Website Redesign', size: '128 MB', synced: false, lastSync: '1 hour ago' },
    { id: 3, name: 'Brand Guidelines', size: '89 MB', synced: true, lastSync: '5 mins ago' },
  ]);
  const { toast } = useToast();

  const handleDownload = (projectId: number) => {
    toast({ title: "Downloading", description: "Project is being downloaded for offline use" });
    setTimeout(() => {
      setProjects(projects.map(p => p.id === projectId ? { ...p, synced: true } : p));
      toast({ title: "Downloaded", description: "Project is now available offline" });
    }, 2000);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <HardDrive className="h-5 w-5" />
          Offline Projects
        </CardTitle>
        <CardDescription>Manage projects available offline</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] pr-4">
          <div className="space-y-3">
            {projects.map((project) => (
              <div key={project.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <p className="font-medium">{project.name}</p>
                    {project.synced && <Check className="h-4 w-4 text-green-500" />}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                    <span>{project.size}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {project.lastSync}
                    </span>
                  </div>
                </div>
                <Button
                  variant={project.synced ? "outline" : "default"}
                  size="sm"
                  onClick={() => handleDownload(project.id)}
                >
                  {project.synced ? (
                    <RefreshCw className="h-4 w-4" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export const SyncQueue: React.FC = () => {
  const [syncItems, setSyncItems] = useState([
    { id: 1, name: 'Design updates', status: 'syncing', progress: 65 },
    { id: 2, name: 'New comments', status: 'pending', progress: 0 },
    { id: 3, name: 'Asset uploads', status: 'pending', progress: 0 },
  ]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Sync Queue
        </CardTitle>
        <CardDescription>Pending changes waiting to sync</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {syncItems.map((item) => (
            <div key={item.id} className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{item.name}</span>
                <Badge variant={item.status === 'syncing' ? 'default' : 'secondary'}>
                  {item.status}
                </Badge>
              </div>
              {item.status === 'syncing' && (
                <Progress value={item.progress} className="h-2" />
              )}
            </div>
          ))}
          <Separator />
          <Button variant="outline" className="w-full">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync All Now
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const PWAInstallPrompt: React.FC = () => {
  const [showPrompt, setShowPrompt] = useState(true);
  const { toast } = useToast();

  if (!showPrompt) return null;

  return (
    <Card className="border-blue-500">
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <div className="flex-1">
            <h3 className="font-semibold mb-1">Install App</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Install this app for offline access and a better experience
            </p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => {
                toast({ title: "Installing...", description: "App will be added to your home screen" });
                setShowPrompt(false);
              }}>
                Install
              </Button>
              <Button size="sm" variant="outline" onClick={() => setShowPrompt(false)}>
                Not now
              </Button>
            </div>
          </div>
          <Download className="h-8 w-8 text-blue-500" />
        </div>
      </CardContent>
    </Card>
  );
};

export const OfflineSettings: React.FC = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Offline Mode Settings</CardTitle>
        <CardDescription>Configure offline behavior and storage</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Enable offline mode</p>
              <p className="text-sm text-muted-foreground">Allow working without internet</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto-sync when online</p>
              <p className="text-sm text-muted-foreground">Automatically sync changes</p>
            </div>
            <Switch defaultChecked />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Download assets automatically</p>
              <p className="text-sm text-muted-foreground">Cache images and fonts</p>
            </div>
            <Switch />
          </div>
          <Separator />
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="font-medium">Storage usage</p>
              <span className="text-sm text-muted-foreground">2.4 GB / 5 GB</span>
            </div>
            <Progress value={48} />
            <Button variant="outline" size="sm" className="w-full mt-2">
              Clear Cache
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
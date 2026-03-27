"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Switch } from '@/components/ui/switch';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  WifiOff,
  Wifi,
  Download,
  Upload,
  HardDrive,
  Cloud,
  RefreshCw,
  Check,
  Clock,
  AlertCircle,
  Smartphone,
  Settings2,
  Trash2,
  FolderSync,
  FileText,
  Image as ImageIcon,
  Layers,
  Zap,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface CachedProject {
  id: number;
  name: string;
  size: string;
  lastSync: string;
  status: 'synced' | 'pending' | 'error';
  type: 'design' | 'template' | 'asset';
}

interface SyncAction {
  id: number;
  action: string;
  target: string;
  time: string;
  status: 'completed' | 'pending' | 'failed';
}

// Mock Data
const cachedProjects: CachedProject[] = [
  { id: 1, name: 'Mobile App Redesign', size: '24.5 MB', lastSync: '2 min ago', status: 'synced', type: 'design' },
  { id: 2, name: 'Marketing Landing Page', size: '18.2 MB', lastSync: '15 min ago', status: 'synced', type: 'design' },
  { id: 3, name: 'Brand Guidelines', size: '45.8 MB', lastSync: '1 hour ago', status: 'pending', type: 'design' },
  { id: 4, name: 'UI Component Library', size: '12.4 MB', lastSync: '3 hours ago', status: 'synced', type: 'template' },
  { id: 5, name: 'Icon Pack v2', size: '8.6 MB', lastSync: '5 hours ago', status: 'error', type: 'asset' },
];

const syncHistory: SyncAction[] = [
  { id: 1, action: 'Uploaded', target: 'Homepage Hero Section', time: '2 min ago', status: 'completed' },
  { id: 2, action: 'Downloaded', target: 'New Brand Colors', time: '5 min ago', status: 'completed' },
  { id: 3, action: 'Synced', target: 'Team Comments', time: '10 min ago', status: 'completed' },
  { id: 4, action: 'Uploading', target: 'Mobile Screens', time: 'Now', status: 'pending' },
  { id: 5, action: 'Failed', target: 'Large Asset Pack', time: '15 min ago', status: 'failed' },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'synced': return 'bg-green-100 text-green-700';
    case 'completed': return 'bg-green-100 text-green-700';
    case 'pending': return 'bg-amber-100 text-amber-700';
    case 'error': return 'bg-red-100 text-red-700';
    case 'failed': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'synced': return <Check className="h-4 w-4 text-green-500" />;
    case 'completed': return <Check className="h-4 w-4 text-green-500" />;
    case 'pending': return <Clock className="h-4 w-4 text-amber-500" />;
    case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
    case 'failed': return <AlertCircle className="h-4 w-4 text-red-500" />;
    default: return <Clock className="h-4 w-4 text-gray-500" />;
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'design': return <FileText className="h-4 w-4" />;
    case 'template': return <Layers className="h-4 w-4" />;
    case 'asset': return <ImageIcon className="h-4 w-4" />;
    default: return <FileText className="h-4 w-4" />;
  }
};

export default function OfflinePwaPage() {
  const { toast } = useToast();
  const [isOnline, setIsOnline] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  const [projects] = useState<CachedProject[]>(cachedProjects);
  const [isSyncing, setIsSyncing] = useState(false);

  const totalCacheSize = '109.5 MB';
  const syncedCount = projects.filter(p => p.status === 'synced').length;
  const pendingCount = projects.filter(p => p.status === 'pending').length;

  const handleSync = () => {
    setIsSyncing(true);
    setTimeout(() => {
      setIsSyncing(false);
      toast({ title: 'Sync Complete', description: 'All changes have been synchronized' });
    }, 2000);
  };

  const handleInstallPWA = () => {
    toast({ title: 'Installing PWA', description: 'Adding app to your device...' });
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
                  <WifiOff className="h-7 w-7 text-blue-600" />Offline PWA
                </h1>
                <p className="text-gray-500">Work offline with Progressive Web App</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  {isOnline ? (
                    <Badge className="bg-green-100 text-green-700"><Wifi className="h-3 w-3 mr-1" />Online</Badge>
                  ) : (
                    <Badge className="bg-amber-100 text-amber-700"><WifiOff className="h-3 w-3 mr-1" />Offline</Badge>
                  )}
                </div>
                <Button variant="outline" onClick={handleSync} disabled={isSyncing}>
                  {isSyncing ? <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Syncing...</> : <><FolderSync className="h-4 w-4 mr-2" />Sync Now</>}
                </Button>
                <Button onClick={handleInstallPWA}><Download className="h-4 w-4 mr-2" />Install App</Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-5 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg"><HardDrive className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Cache Size</p>
                    <p className="text-xl font-bold text-gray-900">{totalCacheSize}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg"><Check className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Synced</p>
                    <p className="text-xl font-bold text-green-600">{syncedCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-amber-100 rounded-lg"><Clock className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Pending</p>
                    <p className="text-xl font-bold text-amber-600">{pendingCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg"><Cloud className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Cloud Storage</p>
                    <p className="text-xl font-bold text-gray-900">2.4 GB</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-cyan-100 rounded-lg"><Zap className="h-5 w-5 text-cyan-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Last Sync</p>
                    <p className="text-xl font-bold text-gray-900">2 min</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
              {/* Cached Projects */}
              <div className="col-span-2 flex flex-col overflow-hidden bg-white rounded-xl border border-gray-200">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">Cached Projects</h3>
                  <Button size="sm" variant="outline"><Settings2 className="h-4 w-4 mr-1" />Manage</Button>
                </div>
                <ScrollArea className="flex-1">
                  <div className="p-4 space-y-3">
                    {projects.map(project => (
                      <div key={project.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group">
                        <div className={`p-2 rounded-lg ${project.type === 'design' ? 'bg-blue-100' : project.type === 'template' ? 'bg-purple-100' : 'bg-green-100'}`}>
                          {getTypeIcon(project.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium text-gray-900 truncate">{project.name}</h4>
                            {getStatusIcon(project.status)}
                          </div>
                          <p className="text-sm text-gray-500">{project.size} • Last sync {project.lastSync}</p>
                        </div>
                        <Badge className={getStatusColor(project.status)}>{project.status}</Badge>
                        <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
                          <Button size="sm" variant="ghost"><RefreshCw className="h-4 w-4" /></Button>
                          <Button size="sm" variant="ghost" className="text-red-600"><Trash2 className="h-4 w-4" /></Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* Settings & Sync History */}
              <div className="flex flex-col gap-6 overflow-hidden">
                {/* Settings Card */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Offline Settings</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Auto Sync</p>
                        <p className="text-sm text-gray-500">Sync when online</p>
                      </div>
                      <Switch checked={autoSync} onCheckedChange={setAutoSync} />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Offline Mode</p>
                        <p className="text-sm text-gray-500">Simulate offline</p>
                      </div>
                      <Switch checked={!isOnline} onCheckedChange={(v) => setIsOnline(!v)} />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">Cache Limit</p>
                        <p className="text-sm text-gray-500">500 MB maximum</p>
                      </div>
                      <Button size="sm" variant="outline">Change</Button>
                    </div>
                    <div className="pt-2">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">Storage Used</span>
                        <span className="text-sm font-medium">22%</span>
                      </div>
                      <Progress value={22} />
                    </div>
                  </CardContent>
                </Card>

                {/* Sync History */}
                <Card className="flex-1 flex flex-col overflow-hidden">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">Sync Activity</CardTitle>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-hidden p-0">
                    <ScrollArea className="h-full">
                      <div className="px-4 pb-4 space-y-2">
                        {syncHistory.map(action => (
                          <div key={action.id} className="flex items-center gap-3 py-2">
                            {action.status === 'completed' ? (
                              <Upload className="h-4 w-4 text-green-500" />
                            ) : action.status === 'pending' ? (
                              <RefreshCw className="h-4 w-4 text-amber-500 animate-spin" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-red-500" />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-gray-900 truncate">{action.action} {action.target}</p>
                              <p className="text-xs text-gray-400">{action.time}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>

                {/* Install PWA Card */}
                <Card className="bg-linear-to-r from-blue-600 to-purple-600 text-white">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-white/20 rounded-xl">
                        <Smartphone className="h-6 w-6" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold">Install as App</h4>
                        <p className="text-sm text-white/80">Get the full offline experience</p>
                      </div>
                    </div>
                    <Button className="w-full mt-4 bg-white text-blue-600 hover:bg-white/90" onClick={handleInstallPWA}>
                      <Download className="h-4 w-4 mr-2" />Install Now
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

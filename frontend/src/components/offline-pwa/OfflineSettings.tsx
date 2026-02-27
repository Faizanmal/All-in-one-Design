'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  Wifi, WifiOff, Cloud, CloudOff, RefreshCw,
  Download, Upload, AlertTriangle, Check, X,
  HardDrive, Trash2, Settings, Database
} from 'lucide-react';

// Types
interface OfflineProject {
  id: string;
  projectId: string;
  projectName: string;
  lastSyncedAt: string;
  localChanges: number;
  size: number;
  status: 'synced' | 'pending' | 'conflict';
}

interface SyncQueueItem {
  id: string;
  projectId: string;
  operationType: 'create' | 'update' | 'delete';
  data: unknown;
  createdAt: string;
  status: 'pending' | 'processing' | 'failed';
  retryCount: number;
}

interface StorageInfo {
  used: number;
  total: number;
  projects: number;
  assets: number;
}

// Offline Status Badge Component
export function OfflineStatusBadge() {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const [pendingChanges, setPendingChanges] = useState(0);

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
    <div
      className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm ${
        isOnline
          ? 'bg-green-900/30 text-green-400'
          : 'bg-amber-900/30 text-amber-400'
      }`}
    >
      {isOnline ? (
        <>
          <Wifi className="w-4 h-4" />
          <span>Online</span>
        </>
      ) : (
        <>
          <WifiOff className="w-4 h-4" />
          <span>Offline</span>
          {pendingChanges > 0 && (
            <span className="px-1.5 py-0.5 bg-amber-600 text-white rounded text-xs">
              {pendingChanges}
            </span>
          )}
        </>
      )}
    </div>
  );
}

// Offline Projects Manager Component
export function OfflineProjectsManager() {
  const [projects, setProjects] = useState<OfflineProject[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [storageInfo, setStorageInfo] = useState<StorageInfo>({
    used: 0,
    total: 0,
    projects: 0,
    assets: 0,
  });

  useEffect(() => {
    loadOfflineProjects();
    loadStorageInfo();
  }, []);

  const loadOfflineProjects = async () => {
    // Load from IndexedDB
    try {
      const response = await fetch('/api/v1/offline/projects/');
      const data = await response.json();
      setProjects(data);
    } catch (error) {
      // Load from local cache
      const cached = localStorage.getItem('offline_projects');
      if (cached) {
        setProjects(JSON.parse(cached));
      }
    }
  };

  const loadStorageInfo = async () => {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      const estimate = await navigator.storage.estimate();
      setStorageInfo({
        used: estimate.usage || 0,
        total: estimate.quota || 0,
        projects: projects.length,
        assets: 0,
      });
    }
  };

  const syncAll = async () => {
    setIsSyncing(true);
    try {
      await fetch('/api/v1/offline/sync/process/', {
        method: 'POST',
      });
      await loadOfflineProjects();
    } catch (error) {
      console.error('Sync failed', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const makeAvailableOffline = async (projectId: string) => {
    try {
      await fetch('/api/v1/offline/projects/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId }),
      });
      await loadOfflineProjects();
    } catch (error) {
      console.error('Failed to make available offline', error);
    }
  };

  const removeOffline = async (projectId: string) => {
    try {
      await fetch(`/api/v1/offline/projects/${projectId}/`, {
        method: 'DELETE',
      });
      setProjects(prev => prev.filter(p => p.projectId !== projectId));
    } catch (error) {
      console.error('Failed to remove', error);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="bg-gray-900 rounded-xl p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Database className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-lg">Offline Projects</h3>
        </div>
        <button
          onClick={syncAll}
          disabled={isSyncing}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          Sync All
        </button>
      </div>

      {/* Storage Usage */}
      <div className="mb-6 p-4 bg-gray-800 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Storage Used</span>
          <span className="text-sm">
            {formatBytes(storageInfo.used)} / {formatBytes(storageInfo.total)}
          </span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all"
            style={{
              width: `${(storageInfo.used / storageInfo.total) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Project List */}
      <div className="space-y-3">
        {projects.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <CloudOff className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No projects available offline</p>
            <p className="text-sm">Make projects available offline to work without internet</p>
          </div>
        ) : (
          projects.map((project) => (
            <div
              key={project.id}
              className="flex items-center justify-between p-4 bg-gray-800 rounded-lg"
            >
              <div className="flex items-center gap-4">
                <div className="relative">
                  <HardDrive className="w-8 h-8 text-gray-400" />
                  {project.status === 'synced' && (
                    <Check className="absolute -bottom-1 -right-1 w-4 h-4 text-green-400 bg-gray-800 rounded-full" />
                  )}
                  {project.status === 'pending' && (
                    <Upload className="absolute -bottom-1 -right-1 w-4 h-4 text-amber-400 bg-gray-800 rounded-full" />
                  )}
                  {project.status === 'conflict' && (
                    <AlertTriangle className="absolute -bottom-1 -right-1 w-4 h-4 text-red-400 bg-gray-800 rounded-full" />
                  )}
                </div>
                <div>
                  <div className="font-medium">{project.projectName}</div>
                  <div className="text-sm text-gray-400">
                    Last synced: {new Date(project.lastSyncedAt).toLocaleString()}
                    {project.localChanges > 0 && (
                      <span className="ml-2 text-amber-400">
                        • {project.localChanges} pending changes
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">
                  {formatBytes(project.size)}
                </span>
                <button
                  onClick={() => removeOffline(project.projectId)}
                  className="p-2 hover:bg-gray-700 rounded"
                >
                  <Trash2 className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// Sync Queue Component
export function SyncQueue() {
  const [queue, setQueue] = useState<SyncQueueItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    try {
      const response = await fetch('/api/v1/offline/sync/');
      const data = await response.json();
      setQueue(data);
    } catch (error) {
      console.error('Failed to load queue', error);
    }
  };

  const processQueue = async () => {
    setIsProcessing(true);
    try {
      await fetch('/api/v1/offline/sync/process/', {
        method: 'POST',
      });
      await loadQueue();
    } catch (error) {
      console.error('Failed to process queue', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const retryItem = async (itemId: string) => {
    try {
      await fetch(`/api/v1/offline/sync/${itemId}/retry/`, {
        method: 'POST',
      });
      await loadQueue();
    } catch (error) {
      console.error('Failed to retry', error);
    }
  };

  const discardItem = async (itemId: string) => {
    try {
      await fetch(`/api/v1/offline/sync/${itemId}/`, {
        method: 'DELETE',
      });
      setQueue(prev => prev.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Failed to discard', error);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Upload className="w-5 h-5 text-amber-400" />
          <h3 className="font-semibold text-lg">Sync Queue</h3>
          {queue.length > 0 && (
            <span className="px-2 py-0.5 bg-amber-600 text-white rounded text-sm">
              {queue.length}
            </span>
          )}
        </div>
        <button
          onClick={processQueue}
          disabled={isProcessing || queue.length === 0}
          className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded-lg disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
          Process All
        </button>
      </div>

      <div className="space-y-3">
        {queue.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Check className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>All changes synced</p>
          </div>
        ) : (
          queue.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 bg-gray-800 rounded-lg"
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-2 h-2 rounded-full ${
                    item.status === 'pending'
                      ? 'bg-amber-400'
                      : item.status === 'processing'
                      ? 'bg-blue-400 animate-pulse'
                      : 'bg-red-400'
                  }`}
                />
                <div>
                  <div className="font-medium capitalize">
                    {item.operationType} Operation
                  </div>
                  <div className="text-sm text-gray-400">
                    {new Date(item.createdAt).toLocaleString()}
                    {item.retryCount > 0 && (
                      <span className="ml-2 text-red-400">
                        • {item.retryCount} retries
                      </span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {item.status === 'failed' && (
                  <button
                    onClick={() => retryItem(item.id)}
                    className="p-2 hover:bg-gray-700 rounded"
                  >
                    <RefreshCw className="w-4 h-4 text-amber-400" />
                  </button>
                )}
                <button
                  onClick={() => discardItem(item.id)}
                  className="p-2 hover:bg-gray-700 rounded"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// PWA Install Prompt Component
export function PWAInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<any | null>(null); // eslint-disable-line @typescript-eslint/no-explicit-any
  const [isInstalled, setIsInstalled] = useState(() => window.matchMedia('(display-mode: standalone)').matches);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return;
    }

    const handleBeforeInstallPrompt = (e: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
      e.preventDefault();
      setDeferredPrompt(e);
      setShowPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      setIsInstalled(true);
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  if (isInstalled || !showPrompt) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 rounded-xl p-4 text-white shadow-2xl border border-gray-700 max-w-sm">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
          <Download className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h4 className="font-semibold mb-1">Install App</h4>
          <p className="text-sm text-gray-400 mb-3">
            Install our app for offline access and a better experience
          </p>
          <div className="flex gap-2">
            <button
              onClick={handleInstall}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
            >
              Install
            </button>
            <button
              onClick={() => setShowPrompt(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
            >
              Not now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Offline Settings Page
export function OfflineSettings() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-white">Offline & Sync</h1>
        <OfflineStatusBadge />
      </div>
      
      <OfflineProjectsManager />
      <SyncQueue />
    </div>
  );
}

export default OfflineSettings;

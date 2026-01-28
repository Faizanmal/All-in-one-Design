'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Smartphone,
  Tablet,
  Wifi,
  WifiOff,
  Battery,
  BatteryCharging,
  Cloud,
  CloudOff,
  RefreshCw,
  Download,
  Upload,
  Bell,
  BellOff,
  Settings,
  User,
  LogOut,
  ChevronRight,
  Check,
  X,
  AlertCircle,
  AlertTriangle,
  Shield,
  Fingerprint,
  Eye,
  EyeOff,
  Trash2,
  HardDrive,
  Zap,
  Moon,
  Sun,
  Monitor,
  MessageSquare,
  Star,
  Clock,
  FileText,
  Folder,
  Image,
  MoreVertical,
} from 'lucide-react';

// Types
interface MobileDevice {
  id: string;
  name: string;
  type: 'phone' | 'tablet';
  platform: 'ios' | 'android';
  model: string;
  osVersion: string;
  appVersion: string;
  lastSeen: string;
  isOnline: boolean;
  isCurrent: boolean;
  pushEnabled: boolean;
  biometricsEnabled: boolean;
}

interface SyncStatus {
  isOnline: boolean;
  lastSyncTime: string;
  pendingChanges: number;
  syncInProgress: boolean;
  conflicts: number;
  cacheSize: number;
  maxCacheSize: number;
}

interface OfflineProject {
  id: string;
  name: string;
  lastModified: string;
  size: number;
  syncStatus: 'synced' | 'pending' | 'conflict' | 'downloading';
  thumbnail?: string;
}

interface MobileNotification {
  id: string;
  type: 'comment' | 'mention' | 'update' | 'share';
  title: string;
  message: string;
  projectId?: string;
  createdAt: string;
  read: boolean;
}

// Mock data
const mockDevice: MobileDevice = {
  id: 'device-1',
  name: 'iPhone 15 Pro',
  type: 'phone',
  platform: 'ios',
  model: 'iPhone 15 Pro',
  osVersion: 'iOS 17.2',
  appVersion: '3.5.2',
  lastSeen: '2024-01-15T14:30:00Z',
  isOnline: true,
  isCurrent: true,
  pushEnabled: true,
  biometricsEnabled: true,
};

const mockDevices: MobileDevice[] = [
  mockDevice,
  {
    id: 'device-2',
    name: 'iPad Pro',
    type: 'tablet',
    platform: 'ios',
    model: 'iPad Pro 12.9"',
    osVersion: 'iPadOS 17.2',
    appVersion: '3.5.2',
    lastSeen: '2024-01-14T10:00:00Z',
    isOnline: false,
    isCurrent: false,
    pushEnabled: true,
    biometricsEnabled: false,
  },
  {
    id: 'device-3',
    name: 'Galaxy S24',
    type: 'phone',
    platform: 'android',
    model: 'Samsung Galaxy S24 Ultra',
    osVersion: 'Android 14',
    appVersion: '3.5.1',
    lastSeen: '2024-01-10T16:45:00Z',
    isOnline: false,
    isCurrent: false,
    pushEnabled: false,
    biometricsEnabled: true,
  },
];

const mockSyncStatus: SyncStatus = {
  isOnline: true,
  lastSyncTime: '2024-01-15T14:28:00Z',
  pendingChanges: 3,
  syncInProgress: false,
  conflicts: 1,
  cacheSize: 256 * 1024 * 1024, // 256 MB
  maxCacheSize: 1024 * 1024 * 1024, // 1 GB
};

const mockOfflineProjects: OfflineProject[] = [
  {
    id: 'proj-1',
    name: 'Mobile App Redesign',
    lastModified: '2024-01-15T12:00:00Z',
    size: 45 * 1024 * 1024,
    syncStatus: 'synced',
  },
  {
    id: 'proj-2',
    name: 'Dashboard Components',
    lastModified: '2024-01-15T10:30:00Z',
    size: 28 * 1024 * 1024,
    syncStatus: 'pending',
  },
  {
    id: 'proj-3',
    name: 'Icon Library',
    lastModified: '2024-01-14T16:00:00Z',
    size: 12 * 1024 * 1024,
    syncStatus: 'conflict',
  },
  {
    id: 'proj-4',
    name: 'Marketing Site',
    lastModified: '2024-01-13T09:00:00Z',
    size: 0,
    syncStatus: 'downloading',
  },
];

const mockNotifications: MobileNotification[] = [
  {
    id: 'notif-1',
    type: 'comment',
    title: 'New Comment',
    message: 'Jane Smith commented on your design',
    projectId: 'proj-1',
    createdAt: '2024-01-15T14:25:00Z',
    read: false,
  },
  {
    id: 'notif-2',
    type: 'mention',
    title: 'You were mentioned',
    message: 'John Doe mentioned you in Mobile App Redesign',
    projectId: 'proj-1',
    createdAt: '2024-01-15T12:00:00Z',
    read: false,
  },
  {
    id: 'notif-3',
    type: 'update',
    title: 'Project Updated',
    message: 'Dashboard Components has new changes',
    projectId: 'proj-2',
    createdAt: '2024-01-15T10:30:00Z',
    read: true,
  },
];

// Helper functions
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
};

// Helper Components
const StatusBadge: React.FC<{ status: OfflineProject['syncStatus'] }> = ({ status }) => {
  const config = {
    synced: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Check, label: 'Synced' },
    pending: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', icon: Upload, label: 'Pending' },
    conflict: { bg: 'bg-red-500/20', text: 'text-red-400', icon: AlertTriangle, label: 'Conflict' },
    downloading: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: Download, label: 'Downloading' },
  };

  const { bg, text, icon: Icon, label } = config[status];

  return (
    <span className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] ${bg} ${text}`}>
      <Icon size={10} className={status === 'downloading' ? 'animate-bounce' : ''} />
      {label}
    </span>
  );
};

const NotificationIcon: React.FC<{ type: MobileNotification['type'] }> = ({ type }) => {
  const icons = {
    comment: MessageSquare,
    mention: User,
    update: RefreshCw,
    share: User,
  };
  const Icon = icons[type];
  return <Icon size={14} />;
};

// Device Card Component
interface DeviceCardProps {
  device: MobileDevice;
  onRemove: (id: string) => void;
  onTogglePush: (id: string) => void;
  onToggleBiometrics: (id: string) => void;
}

const DeviceCard: React.FC<DeviceCardProps> = ({
  device,
  onRemove,
  onTogglePush,
  onToggleBiometrics,
}) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className={`bg-gray-800/50 rounded-lg p-4 border ${
      device.isCurrent ? 'border-blue-500/50' : 'border-gray-700/50'
    }`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${device.isOnline ? 'bg-green-500/20' : 'bg-gray-700'}`}>
          {device.type === 'phone' ? (
            <Smartphone size={20} className={device.isOnline ? 'text-green-400' : 'text-gray-500'} />
          ) : (
            <Tablet size={20} className={device.isOnline ? 'text-green-400' : 'text-gray-500'} />
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-medium text-white truncate">{device.name}</h4>
            {device.isCurrent && (
              <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/20 text-blue-400 rounded">
                Current
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-0.5">{device.model}</p>
          <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
            <span>{device.osVersion}</span>
            <span>•</span>
            <span>v{device.appVersion}</span>
          </div>
          <div className="flex items-center gap-1 mt-2">
            <span className={`w-2 h-2 rounded-full ${device.isOnline ? 'bg-green-500' : 'bg-gray-600'}`} />
            <span className="text-xs text-gray-500">
              {device.isOnline ? 'Online' : `Last seen ${formatRelativeTime(device.lastSeen)}`}
            </span>
          </div>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          >
            <MoreVertical size={14} />
          </button>
          
          {showMenu && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
              <div className="absolute right-0 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20 py-1">
                <button
                  onClick={() => {
                    onTogglePush(device.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                >
                  {device.pushEnabled ? <BellOff size={12} /> : <Bell size={12} />}
                  {device.pushEnabled ? 'Disable Notifications' : 'Enable Notifications'}
                </button>
                <button
                  onClick={() => {
                    onToggleBiometrics(device.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                >
                  <Fingerprint size={12} />
                  {device.biometricsEnabled ? 'Disable Biometrics' : 'Enable Biometrics'}
                </button>
                {!device.isCurrent && (
                  <>
                    <div className="border-t border-gray-700 my-1" />
                    <button
                      onClick={() => {
                        onRemove(device.id);
                        setShowMenu(false);
                      }}
                      className="w-full px-3 py-2 text-left text-xs text-red-400 hover:bg-red-900/20 flex items-center gap-2"
                    >
                      <LogOut size={12} />
                      Remove Device
                    </button>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Device settings badges */}
      <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-700/50">
        <span className={`flex items-center gap-1 text-[10px] ${device.pushEnabled ? 'text-green-400' : 'text-gray-500'}`}>
          {device.pushEnabled ? <Bell size={10} /> : <BellOff size={10} />}
          Push
        </span>
        <span className={`flex items-center gap-1 text-[10px] ${device.biometricsEnabled ? 'text-green-400' : 'text-gray-500'}`}>
          <Fingerprint size={10} />
          Biometrics
        </span>
      </div>
    </div>
  );
};

// Main Component
interface MobileAppPanelProps {
  currentDevice?: MobileDevice;
  devices?: MobileDevice[];
  syncStatus?: SyncStatus;
  offlineProjects?: OfflineProject[];
  notifications?: MobileNotification[];
  onSync?: () => void;
  onClearCache?: () => void;
  onDownloadProject?: (projectId: string) => void;
  onRemoveProject?: (projectId: string) => void;
  onResolveConflict?: (projectId: string) => void;
}

export const MobileAppPanel: React.FC<MobileAppPanelProps> = ({
  currentDevice = mockDevice,
  devices = mockDevices,
  syncStatus = mockSyncStatus,
  offlineProjects = mockOfflineProjects,
  notifications = mockNotifications,
  onSync,
  onClearCache,
  onDownloadProject,
  onRemoveProject,
  onResolveConflict,
}) => {
  const [activeTab, setActiveTab] = useState<'sync' | 'offline' | 'devices' | 'settings'>('sync');
  const [isSyncing, setIsSyncing] = useState(false);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [theme, setTheme] = useState<'system' | 'light' | 'dark'>('system');

  const unreadNotifications = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  );

  const handleSync = useCallback(async () => {
    setIsSyncing(true);
    await onSync?.();
    setTimeout(() => setIsSyncing(false), 2000);
  }, [onSync]);

  const cachePercentage = (syncStatus.cacheSize / syncStatus.maxCacheSize) * 100;

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Smartphone size={18} className="text-cyan-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">Mobile App</h3>
            <div className="flex items-center gap-2 mt-0.5">
              <span className={`w-2 h-2 rounded-full ${syncStatus.isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-xs text-gray-500">
                {syncStatus.isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={handleSync}
          disabled={isSyncing || !syncStatus.isOnline}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
            syncStatus.isOnline
              ? 'bg-cyan-600 text-white hover:bg-cyan-700'
              : 'bg-gray-700 text-gray-500 cursor-not-allowed'
          }`}
        >
          <RefreshCw size={14} className={isSyncing ? 'animate-spin' : ''} />
          {isSyncing ? 'Syncing...' : 'Sync Now'}
        </button>
      </div>

      {/* Sync Status Bar */}
      <div className="px-4 py-2 bg-gray-850/50 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Clock size={10} />
            Last sync: {formatRelativeTime(syncStatus.lastSyncTime)}
          </span>
          {syncStatus.pendingChanges > 0 && (
            <span className="flex items-center gap-1 text-yellow-400">
              <Upload size={10} />
              {syncStatus.pendingChanges} pending
            </span>
          )}
          {syncStatus.conflicts > 0 && (
            <span className="flex items-center gap-1 text-red-400">
              <AlertTriangle size={10} />
              {syncStatus.conflicts} conflicts
            </span>
          )}
        </div>
        {unreadNotifications > 0 && (
          <span className="flex items-center gap-1 text-xs text-cyan-400">
            <Bell size={10} />
            {unreadNotifications} new
          </span>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {(['sync', 'offline', 'devices', 'settings'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'text-cyan-400 border-b-2 border-cyan-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'sync' && (
          <div className="p-4 space-y-4">
            {/* Cache usage */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-300">Cache Storage</span>
                <span className="text-xs text-gray-500">
                  {formatBytes(syncStatus.cacheSize)} / {formatBytes(syncStatus.maxCacheSize)}
                </span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    cachePercentage > 90
                      ? 'bg-red-500'
                      : cachePercentage > 70
                      ? 'bg-yellow-500'
                      : 'bg-cyan-500'
                  }`}
                  style={{ width: `${cachePercentage}%` }}
                />
              </div>
              {cachePercentage > 70 && (
                <button
                  onClick={onClearCache}
                  className="mt-2 text-xs text-cyan-400 hover:underline"
                >
                  Clear cache to free up space
                </button>
              )}
            </div>

            {/* Notifications */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-2">
                Recent Notifications
              </h4>
              {notifications.length > 0 ? (
                <div className="space-y-2">
                  {notifications.slice(0, 5).map((notification) => (
                    <div
                      key={notification.id}
                      className={`flex items-start gap-3 p-3 rounded-lg ${
                        notification.read ? 'bg-gray-800/30' : 'bg-gray-800/50 border border-cyan-500/20'
                      }`}
                    >
                      <div className={`p-1.5 rounded ${notification.read ? 'bg-gray-700' : 'bg-cyan-500/20'}`}>
                        <NotificationIcon type={notification.type} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-200">{notification.title}</p>
                        <p className="text-xs text-gray-500 truncate">{notification.message}</p>
                      </div>
                      <span className="text-[10px] text-gray-500 whitespace-nowrap">
                        {formatRelativeTime(notification.createdAt)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Bell size={24} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No notifications</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'offline' && (
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{offlineProjects.length} projects available offline</span>
              <button className="text-xs text-cyan-400 hover:underline">
                Manage
              </button>
            </div>

            <div className="space-y-2">
              {offlineProjects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg"
                >
                  <div className="w-12 h-12 bg-gray-700 rounded-lg flex items-center justify-center">
                    <Folder size={20} className="text-gray-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-200 truncate">{project.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-gray-500">
                        {project.size > 0 ? formatBytes(project.size) : 'Downloading...'}
                      </span>
                      <StatusBadge status={project.syncStatus} />
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    {project.syncStatus === 'conflict' && (
                      <button
                        onClick={() => onResolveConflict?.(project.id)}
                        className="p-1.5 text-red-400 hover:bg-red-900/20 rounded"
                        title="Resolve conflict"
                      >
                        <AlertTriangle size={14} />
                      </button>
                    )}
                    {project.syncStatus === 'synced' && (
                      <button
                        onClick={() => onRemoveProject?.(project.id)}
                        className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-900/20 rounded"
                        title="Remove from offline"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                    <ChevronRight size={14} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'devices' && (
          <div className="p-4 space-y-4">
            <p className="text-xs text-gray-500">
              {devices.length} device{devices.length !== 1 ? 's' : ''} connected to your account
            </p>
            <div className="space-y-3">
              {devices.map((device) => (
                <DeviceCard
                  key={device.id}
                  device={device}
                  onRemove={() => {}}
                  onTogglePush={() => {}}
                  onToggleBiometrics={() => {}}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="p-4 space-y-4">
            {/* Sync settings */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Sync</h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <RefreshCw size={14} className="text-gray-400" />
                    <span className="text-sm text-gray-300">Auto-sync</span>
                  </div>
                  <button
                    onClick={() => setAutoSync(!autoSync)}
                    className={`relative w-10 h-5 rounded-full transition-colors ${
                      autoSync ? 'bg-cyan-500' : 'bg-gray-600'
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                        autoSync ? 'translate-x-5' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CloudOff size={14} className="text-gray-400" />
                    <span className="text-sm text-gray-300">Offline Mode</span>
                  </div>
                  <button
                    onClick={() => setOfflineMode(!offlineMode)}
                    className={`relative w-10 h-5 rounded-full transition-colors ${
                      offlineMode ? 'bg-yellow-500' : 'bg-gray-600'
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                        offlineMode ? 'translate-x-5' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Notifications</h4>
              <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Bell size={14} className="text-gray-400" />
                  <span className="text-sm text-gray-300">Push Notifications</span>
                </div>
                <button
                  onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                  className={`relative w-10 h-5 rounded-full transition-colors ${
                    notificationsEnabled ? 'bg-cyan-500' : 'bg-gray-600'
                  }`}
                >
                  <span
                    className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                      notificationsEnabled ? 'translate-x-5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Appearance */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Appearance</h4>
              <div className="flex gap-2">
                {(['system', 'light', 'dark'] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`flex-1 flex flex-col items-center gap-2 p-3 rounded-lg border transition-colors ${
                      theme === t
                        ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                        : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-600'
                    }`}
                  >
                    {t === 'system' && <Monitor size={16} />}
                    {t === 'light' && <Sun size={16} />}
                    {t === 'dark' && <Moon size={16} />}
                    <span className="text-xs capitalize">{t}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Storage */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">Storage</h4>
              <button
                onClick={onClearCache}
                className="w-full p-3 bg-gray-800/50 rounded-lg text-left hover:bg-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <HardDrive size={14} className="text-gray-400" />
                    <span className="text-sm text-gray-300">Clear Cache</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatBytes(syncStatus.cacheSize)}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Free up storage by removing cached files
                </p>
              </button>
            </div>

            {/* About */}
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wider mb-3">About</h4>
              <div className="bg-gray-800/50 rounded-lg p-3 space-y-2 text-xs text-gray-500">
                <div className="flex justify-between">
                  <span>App Version</span>
                  <span className="text-gray-300">v{currentDevice.appVersion}</span>
                </div>
                <div className="flex justify-between">
                  <span>Device</span>
                  <span className="text-gray-300">{currentDevice.model}</span>
                </div>
                <div className="flex justify-between">
                  <span>OS</span>
                  <span className="text-gray-300">{currentDevice.osVersion}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-850 border-t border-gray-700 text-xs text-gray-500 flex items-center justify-between">
        <span>{currentDevice.name}</span>
        <span className="flex items-center gap-1">
          {syncStatus.isOnline ? (
            <>
              <Wifi size={10} className="text-green-400" />
              Connected
            </>
          ) : (
            <>
              <WifiOff size={10} className="text-red-400" />
              Offline
            </>
          )}
        </span>
      </div>
    </div>
  );
};

export default MobileAppPanel;

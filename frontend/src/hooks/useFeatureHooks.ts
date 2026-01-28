// API hooks for all new features (18-25)

import { useState, useEffect, useCallback } from 'react';

// Base API configuration
const API_BASE = '/api/v1';

// Generic fetch helper
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

// ============ Code Export Hooks ============

interface ExportConfiguration {
  framework: string;
  stylingApproach: string;
  useTypeScript: boolean;
  responsive: boolean;
  includeAssets: boolean;
}

interface CodeExportResult {
  id: string;
  code: Record<string, string>;
  designSpec: Record<string, unknown>;
}

export function useCodeExport(projectId: string) {
  const [isExporting, setIsExporting] = useState(false);
  const [exportResult, setExportResult] = useState<CodeExportResult | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const generateCode = useCallback(
    async (layers: string[], config: ExportConfiguration) => {
      setIsExporting(true);
      setError(null);

      try {
        const result = await apiFetch<CodeExportResult>('/code-export/generate/', {
          method: 'POST',
          body: JSON.stringify({
            project_id: projectId,
            layers,
            config,
          }),
        });
        setExportResult(result);
        return result;
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setIsExporting(false);
      }
    },
    [projectId]
  );

  const downloadExport = useCallback(async (exportId: string) => {
    const blob = await fetch(`${API_BASE}/code-export/exports/${exportId}/download/`).then(
      (r) => r.blob()
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'code-export.zip';
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  return {
    isExporting,
    exportResult,
    error,
    generateCode,
    downloadExport,
  };
}

// ============ Slack/Teams Hooks ============

interface SlackWorkspace {
  id: string;
  teamId: string;
  teamName: string;
  isConnected: boolean;
}

interface IntegrationChannel {
  id: string;
  name: string;
  platform: 'slack' | 'teams';
}

export function useSlackIntegration() {
  const [workspace, setWorkspace] = useState<SlackWorkspace | null>(null);
  const [channels, setChannels] = useState<IntegrationChannel[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadWorkspace();
  }, []);

  const loadWorkspace = async () => {
    setIsLoading(true);
    try {
      const workspaces = await apiFetch<SlackWorkspace[]>('/slack-teams/slack/workspaces/');
      if (workspaces.length > 0) {
        setWorkspace(workspaces[0]);
        const chData = await apiFetch<IntegrationChannel[]>('/slack-teams/slack/channels/');
        setChannels(chData);
      }
    } catch (error) {
      console.error('Failed to load Slack workspace', error);
    } finally {
      setIsLoading(false);
    }
  };

  const connect = useCallback(() => {
    const clientId = process.env.NEXT_PUBLIC_SLACK_CLIENT_ID;
    const redirectUri = `${window.location.origin}/api/integrations/slack/callback`;
    window.location.href = `https://slack.com/oauth/v2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=channels:read,chat:write,commands`;
  }, []);

  const disconnect = useCallback(async () => {
    await apiFetch('/slack-teams/slack/disconnect/', { method: 'POST' });
    setWorkspace(null);
    setChannels([]);
  }, []);

  const sendMessage = useCallback(
    async (channelId: string, message: string, projectId?: string) => {
      await apiFetch('/slack-teams/slack/send-message/', {
        method: 'POST',
        body: JSON.stringify({
          channel_id: channelId,
          message,
          project_id: projectId,
        }),
      });
    },
    []
  );

  return {
    workspace,
    channels,
    isLoading,
    connect,
    disconnect,
    sendMessage,
    refresh: loadWorkspace,
  };
}

export function useTeamsIntegration() {
  const [isConnected, setIsConnected] = useState(false);
  
  const connect = useCallback(() => {
    const clientId = process.env.NEXT_PUBLIC_TEAMS_CLIENT_ID;
    const redirectUri = `${window.location.origin}/api/integrations/teams/callback`;
    window.location.href = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=ChannelMessage.Send&response_type=code`;
  }, []);

  return { isConnected, connect };
}

// ============ Offline/PWA Hooks ============

interface OfflineProject {
  id: string;
  projectId: string;
  projectName: string;
  lastSyncedAt: string;
  localChanges: number;
  status: 'synced' | 'pending' | 'conflict';
}

export function useOfflineMode() {
  const [isOnline, setIsOnline] = useState(() => navigator.onLine);
  const [offlineProjects, setOfflineProjects] = useState<OfflineProject[]>([]);
  const [syncQueue, setSyncQueue] = useState<any[]>([]);

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

  const loadOfflineData = useCallback(async () => {
    try {
      const projects = await apiFetch<OfflineProject[]>('/offline/projects/');
      setOfflineProjects(projects);
      const queue = await apiFetch<unknown[]>('/offline/sync/');
      setSyncQueue(queue);
    } catch (error) {
      // Load from localStorage as fallback
      const cached = localStorage.getItem('offline_projects');
      if (cached) setOfflineProjects(JSON.parse(cached));
    }
  }, []);

  useEffect(() => {
    // loadOfflineData is called when dependencies change
  }, [loadOfflineData]);

  const makeAvailableOffline = useCallback(async (projectId: string) => {
    const result = await apiFetch<OfflineProject>('/offline/projects/', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId }),
    });
    setOfflineProjects((prev) => [...prev, result]);
  }, []);

  const removeOffline = useCallback(async (projectId: string) => {
    await apiFetch(`/offline/projects/${projectId}/`, { method: 'DELETE' });
    setOfflineProjects((prev) => prev.filter((p) => p.projectId !== projectId));
  }, []);

  const syncAll = useCallback(async () => {
    await apiFetch('/offline/sync/process/', { method: 'POST' });
    await loadOfflineData();
  }, []);

  return {
    isOnline,
    offlineProjects,
    syncQueue,
    makeAvailableOffline,
    removeOffline,
    syncAll,
    refresh: loadOfflineData,
  };
}

// ============ Asset Management Hooks ============

interface Asset {
  id: string;
  name: string;
  type: string;
  url: string;
  thumbnailUrl: string;
  size: number;
  tags: string[];
  isFavorite: boolean;
}

interface AssetFolder {
  id: string;
  name: string;
  isSmartFolder: boolean;
  assetCount: number;
}

export function useAssetManagement(projectId?: string) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [folders, setFolders] = useState<AssetFolder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentFolder, setCurrentFolder] = useState<string | null>(null);

  useEffect(() => {
    loadAssets();
    loadFolders();
  }, [projectId, currentFolder]);

  const loadAssets = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (currentFolder) params.set('folder', currentFolder);
      if (projectId) params.set('project', projectId);
      const data = await apiFetch<Asset[]>(`/asset-management/assets/?${params}`);
      setAssets(data);
    } catch (error) {
      console.error('Failed to load assets', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const data = await apiFetch<AssetFolder[]>('/asset-management/folders/');
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders', error);
    }
  };

  const uploadAssets = useCallback(async (files: FileList) => {
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('files', file));
    if (currentFolder) formData.append('folder_id', currentFolder);

    const response = await fetch(`${API_BASE}/asset-management/assets/bulk-upload/`, {
      method: 'POST',
      body: formData,
    });
    const newAssets = await response.json();
    setAssets((prev) => [...newAssets, ...prev]);
    return newAssets;
  }, [currentFolder]);

  const searchAssets = useCallback(async (query: string, type: 'text' | 'semantic') => {
    const results = await apiFetch<Asset[]>('/asset-management/assets/search/', {
      method: 'POST',
      body: JSON.stringify({ query, search_type: type }),
    });
    setAssets(results);
    return results;
  }, []);

  const toggleFavorite = useCallback(async (assetId: string) => {
    await apiFetch(`/asset-management/assets/${assetId}/toggle-favorite/`, { method: 'POST' });
    setAssets((prev) =>
      prev.map((a) => (a.id === assetId ? { ...a, isFavorite: !a.isFavorite } : a))
    );
  }, []);

  const deleteAsset = useCallback(async (assetId: string) => {
    await apiFetch(`/asset-management/assets/${assetId}/`, { method: 'DELETE' });
    setAssets((prev) => prev.filter((a) => a.id !== assetId));
  }, []);

  return {
    assets,
    folders,
    isLoading,
    currentFolder,
    setCurrentFolder,
    uploadAssets,
    searchAssets,
    toggleFavorite,
    deleteAsset,
    refresh: loadAssets,
  };
}

// ============ Template Marketplace Hooks ============

interface Template {
  id: string;
  name: string;
  description: string;
  thumbnailUrl: string;
  category: string;
  price: number;
  isFree: boolean;
  rating: number;
  downloadCount: number;
  isFavorite: boolean;
  isPurchased: boolean;
}

export function useTemplateMarketplace() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<Array<{ id: string; name: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: null as string | null,
    priceFilter: 'all' as 'all' | 'free' | 'paid',
    sortBy: 'popular' as string,
  });

  useEffect(() => {
    loadTemplates();
    loadCategories();
  }, [filters]);

  const loadTemplates = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.category) params.set('category', filters.category);
      if (filters.priceFilter === 'free') params.set('is_free', 'true');
      if (filters.priceFilter === 'paid') params.set('is_free', 'false');
      params.set('ordering', filters.sortBy);

      const data = await apiFetch<{ results: Template[] }>(`/marketplace/templates/?${params}`);
      setTemplates(data.results || (Array.isArray(data) ? data : []));
    } catch (error) {
      console.error('Failed to load templates', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await apiFetch<Array<{ id: string; name: string }>>('/marketplace/categories/');
      setCategories(data);
    } catch (error) {
      console.error('Failed to load categories', error);
    }
  };

  const toggleFavorite = useCallback(async (templateId: string) => {
    await apiFetch(`/marketplace/templates/${templateId}/favorite/`, { method: 'POST' });
    setTemplates((prev) =>
      prev.map((t) => (t.id === templateId ? { ...t, isFavorite: !t.isFavorite } : t))
    );
  }, []);

  const purchaseTemplate = useCallback(async (templateId: string) => {
    await apiFetch(`/marketplace/templates/${templateId}/purchase/`, { method: 'POST' });
    setTemplates((prev) =>
      prev.map((t) => (t.id === templateId ? { ...t, isPurchased: true } : t))
    );
  }, []);

  return {
    templates,
    categories,
    isLoading,
    filters,
    setFilters,
    toggleFavorite,
    purchaseTemplate,
    refresh: loadTemplates,
  };
}

// ============ Time Tracking Hooks ============

interface TimeEntry {
  id: string;
  projectId: string;
  projectName: string;
  description: string;
  duration: number;
  isBillable: boolean;
}

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
}

export function useTimeTracking(projectId?: string) {
  const [entries, setEntries] = useState<TimeEntry[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isTracking, setIsTracking] = useState(false);
  const [weeklyGoal, setWeeklyGoal] = useState<Record<string, unknown> | null>(null);

  const loadData = useCallback(async () => {
    try {
      const params = projectId ? `?project=${projectId}` : '';
      const [entriesData, tasksData, goalData] = await Promise.all([
        apiFetch<TimeEntry[]>(`/time-tracking/entries/${params}`),
        apiFetch<Task[]>(`/time-tracking/tasks/${params}`),
        apiFetch<Record<string, unknown>>('/time-tracking/goals/current/'),
      ]);
      setEntries(entriesData);
      setTasks(tasksData);
      setWeeklyGoal(goalData);
    } catch (error) {
      console.error('Failed to load time tracking data', error);
    }
  }, [projectId]);

  useEffect(() => {
    // loadData is called when dependencies change
  }, [loadData]);

  const startTimer = useCallback(
    async (data: { description: string; taskId?: string; isBillable: boolean }) => {
      await apiFetch('/time-tracking/tracker/start/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          ...data,
        }),
      });
      setIsTracking(true);
    },
    [projectId]
  );

  const stopTimer = useCallback(async () => {
    const entry = await apiFetch<TimeEntry>('/time-tracking/tracker/stop/', {
      method: 'POST',
    });
    setIsTracking(false);
    setEntries((prev) => [entry, ...prev]);
    return entry;
  }, []);

  const updateTask = useCallback(async (taskId: string, updates: Partial<Task>) => {
    await apiFetch(`/time-tracking/tasks/${taskId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, ...updates } : t))
    );
  }, []);

  return {
    entries,
    tasks,
    isTracking,
    weeklyGoal,
    startTimer,
    stopTimer,
    updateTask,
    refresh: loadData,
  };
}

// ============ PDF Export Hooks ============

interface PDFExportPreset {
  pageSize: string;
  orientation: string;
  bleedMargin: number;
  colorMode: string;
  pdfStandard: string;
}

interface PreflightResult {
  status: 'pass' | 'warning' | 'error';
  checks: unknown[];
  summary: { passed: number; warnings: number; errors: number };
}

export function usePDFExport(projectId: string) {
  const [isExporting, setIsExporting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [preflightResult, setPreflightResult] = useState<PreflightResult | null>(null);

  const runPreflightCheck = useCallback(
    async (settings: PDFExportPreset) => {
      const result = await apiFetch<PreflightResult>('/pdf-export/preflight/', {
        method: 'POST',
        body: JSON.stringify({ project_id: projectId, settings }),
      });
      setPreflightResult(result);
      return result;
    },
    [projectId]
  );

  const exportPDF = useCallback(
    async (preset: PDFExportPreset, pages: number[], printMarks: unknown) => {
      setIsExporting(true);
      setProgress(0);

      try {
        const result = await apiFetch<{ id: string; file_url: string }>('/pdf-export/exports/', {
          method: 'POST',
          body: JSON.stringify({
            project_id: projectId,
            preset,
            pages,
            print_marks: printMarks,
          }),
        });

        // Poll for progress
        const pollProgress = async () => {
          const status = await apiFetch<{ progress: number; status: string }>(
            `/pdf-export/exports/${result.id}/`
          );
          setProgress(status.progress);
          if (status.status === 'completed') {
            setIsExporting(false);
            return status;
          } else if (status.status === 'failed') {
            setIsExporting(false);
            throw new Error('Export failed');
          }
          await new Promise((r) => setTimeout(r, 1000));
          return pollProgress();
        };

        return await pollProgress();
      } catch (error) {
        setIsExporting(false);
        throw error;
      }
    },
    [projectId]
  );

  return {
    isExporting,
    progress,
    preflightResult,
    runPreflightCheck,
    exportPDF,
  };
}

// ============ Permissions Hooks ============

interface Role {
  id: string;
  name: string;
  permissions: string[];
  color: string;
}

interface ShareLink {
  id: string;
  token: string;
  permission: string;
  isActive: boolean;
}

export function usePermissions(projectId: string) {
  const [roles, setRoles] = useState<Role[]>([]);
  const [shareLinks, setShareLinks] = useState<ShareLink[]>([]);
  const [branchProtection, setBranchProtection] = useState<unknown[]>([]);
  const [accessLogs, setAccessLogs] = useState<unknown[]>([]);

  const loadPermissions = useCallback(async () => {
    try {
      const [rolesData, linksData, protectionData, logsData] = await Promise.all([
        apiFetch<Role[]>(`/permissions/roles/?project=${projectId}`),
        apiFetch<ShareLink[]>(`/permissions/share-links/?project=${projectId}`),
        apiFetch<unknown[]>(`/permissions/branch-protection/?project=${projectId}`),
        apiFetch<unknown[]>(`/permissions/access-logs/?project=${projectId}`),
      ]);
      setRoles(rolesData);
      setShareLinks(linksData);
      setBranchProtection(protectionData);
      setAccessLogs(logsData);
    } catch (error) {
      console.error('Failed to load permissions', error);
    }
  }, [projectId]);

  useEffect(() => {
    // loadPermissions is called when dependencies change
  }, [loadPermissions]);

  const createRole = useCallback(
    async (data: { name: string; description: string; permissions: string[]; color: string }) => {
      const role = await apiFetch<Role>('/permissions/roles/', {
        method: 'POST',
        body: JSON.stringify({ ...data, project_id: projectId }),
      });
      setRoles((prev) => [...prev, role]);
      return role;
    },
    [projectId]
  );

  const createShareLink = useCallback(
    async (data: { permission: string; password?: string; expiresInDays?: number; maxUses?: number }) => {
      const link = await apiFetch<ShareLink>('/permissions/share-links/', {
        method: 'POST',
        body: JSON.stringify({ ...data, project_id: projectId }),
      });
      setShareLinks((prev) => [link, ...prev]);
      return link;
    },
    [projectId]
  );

  const toggleShareLink = useCallback(async (linkId: string, isActive: boolean) => {
    await apiFetch(`/permissions/share-links/${linkId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active: isActive }),
    });
    setShareLinks((prev) =>
      prev.map((l) => (l.id === linkId ? { ...l, isActive } : l))
    );
  }, []);

  const assignRole = useCallback(async (userId: string, roleId: string) => {
    await apiFetch('/permissions/user-roles/', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, role_id: roleId, project_id: projectId }),
    });
  }, [projectId]);

  return {
    roles,
    shareLinks,
    branchProtection,
    accessLogs,
    createRole,
    createShareLink,
    toggleShareLink,
    assignRole,
    refresh: loadPermissions,
  };
}

export default {
  useCodeExport,
  useSlackIntegration,
  useTeamsIntegration,
  useOfflineMode,
  useAssetManagement,
  useTemplateMarketplace,
  useTimeTracking,
  usePDFExport,
  usePermissions,
};

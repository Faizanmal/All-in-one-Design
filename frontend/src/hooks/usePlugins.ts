'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }));
    throw new Error(error.message || `API Error: ${response.statusText}`);
  }

  return response.json();
}

// ============================================
// PLUGINS - Plugin Development Platform
// ============================================

export interface PluginCategory {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  plugins_count: number;
  created_at: string;
}

export interface Plugin {
  id: string;
  name: string;
  slug: string;
  description: string;
  author: string;
  developer_profile: string;
  category: string;
  version: string;
  icon?: string;
  screenshots: string[];
  manifest_url: string;
  is_published: boolean;
  is_verified: boolean;
  is_featured: boolean;
  downloads_count: number;
  rating: number;
  reviews_count: number;
  price: number;
  is_free: boolean;
  permissions: string[];
  min_app_version: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PluginVersion {
  id: string;
  plugin: string;
  version: string;
  release_notes: string;
  manifest_url: string;
  file_size_kb: number;
  is_stable: boolean;
  min_app_version: string;
  downloads_count: number;
  created_at: string;
}

export interface PluginInstallation {
  id: string;
  user: string;
  plugin: string;
  version: string;
  status: 'active' | 'inactive' | 'error';
  settings: Record<string, unknown>;
  installed_at: string;
  last_used_at?: string;
  error_message?: string;
}

export interface PluginReview {
  id: string;
  plugin: string;
  user: string;
  rating: number;
  title: string;
  content: string;
  is_verified_purchase: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

export interface DeveloperProfile {
  id: string;
  user: string;
  company_name?: string;
  website?: string;
  bio: string;
  avatar?: string;
  verified: boolean;
  plugins_count: number;
  total_downloads: number;
  average_rating: number;
  created_at: string;
}

export interface APIEndpoint {
  id: string;
  plugin: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  description: string;
  parameters: Array<{
    name: string;
    type: string;
    required: boolean;
    description: string;
  }>;
  response_schema: Record<string, unknown>;
  rate_limit: number;
  requires_auth: boolean;
  created_at: string;
}

export interface WebhookSubscription {
  id: string;
  plugin: string;
  event_type: string;
  callback_url: string;
  secret: string;
  is_active: boolean;
  failure_count: number;
  last_triggered_at?: string;
  created_at: string;
}

export interface PluginSandbox {
  id: string;
  plugin: string;
  environment: 'development' | 'staging' | 'production';
  api_key: string;
  status: 'active' | 'suspended';
  requests_count: number;
  requests_limit: number;
  created_at: string;
}

export interface PluginLog {
  id: string;
  plugin: string;
  installation?: string;
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PluginCapabilities {
  canvas_access: boolean;
  network_access: boolean;
  storage_access: boolean;
  notification_access: boolean;
  ai_access: boolean;
  file_system_access: boolean;
}

export interface PluginExecutionResult {
  success: boolean;
  result?: unknown;
  error?: string;
  logs?: string[];
}

// Hooks for Plugin Categories
export function usePluginCategories() {
  return useQuery({
    queryKey: ['plugin-categories'],
    queryFn: () => apiRequest<PluginCategory[]>('/plugins/categories/'),
  });
}

export function usePluginCategory(categoryId: string) {
  return useQuery({
    queryKey: ['plugin-category', categoryId],
    queryFn: () => apiRequest<PluginCategory>(`/plugins/categories/${categoryId}/`),
    enabled: !!categoryId,
  });
}

// Hooks for Plugins
export function usePlugins(params?: {
  category?: string;
  search?: string;
  is_free?: boolean;
  is_verified?: boolean;
  sort?: string;
}) {
  return useQuery({
    queryKey: ['plugins', params],
    queryFn: () => {
      const queryParams = new URLSearchParams();
      if (params?.category) queryParams.append('category', params.category);
      if (params?.search) queryParams.append('search', params.search);
      if (params?.is_free !== undefined)
        queryParams.append('is_free', params.is_free.toString());
      if (params?.is_verified !== undefined)
        queryParams.append('is_verified', params.is_verified.toString());
      if (params?.sort) queryParams.append('sort', params.sort);

      const queryString = queryParams.toString();
      return apiRequest<Plugin[]>(`/plugins/plugins/${queryString ? `?${queryString}` : ''}`);
    },
  });
}

export function usePlugin(pluginId: string) {
  return useQuery({
    queryKey: ['plugin', pluginId],
    queryFn: () => apiRequest<Plugin>(`/plugins/plugins/${pluginId}/`),
    enabled: !!pluginId,
  });
}

export function useCreatePlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Plugin>) =>
      apiRequest<Plugin>('/plugins/plugins/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins'] });
    },
  });
}

export function useUpdatePlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      data,
    }: {
      pluginId: string;
      data: Partial<Plugin>;
    }) =>
      apiRequest<Plugin>(`/plugins/plugins/${pluginId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['plugin', variables.pluginId] });
      queryClient.invalidateQueries({ queryKey: ['plugins'] });
    },
  });
}

export function usePublishPlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) =>
      apiRequest(`/plugins/plugins/${pluginId}/publish/`, {
        method: 'POST',
      }),
    onSuccess: (_, pluginId) => {
      queryClient.invalidateQueries({ queryKey: ['plugin', pluginId] });
    },
  });
}

// Hooks for Plugin Versions
export function usePluginVersions(pluginId: string) {
  return useQuery({
    queryKey: ['plugin-versions', pluginId],
    queryFn: () => apiRequest<PluginVersion[]>(`/plugins/plugins/${pluginId}/versions/`),
    enabled: !!pluginId,
  });
}

export function useCreatePluginVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      data,
    }: {
      pluginId: string;
      data: Partial<PluginVersion>;
    }) =>
      apiRequest<PluginVersion>(`/plugins/plugins/${pluginId}/versions/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['plugin-versions', variables.pluginId] });
    },
  });
}

// Hooks for Plugin Installations
export function usePluginInstallations(userId?: string) {
  return useQuery({
    queryKey: ['plugin-installations', userId],
    queryFn: () =>
      apiRequest<PluginInstallation[]>(
        `/plugins/installations/${userId ? `?user=${userId}` : ''}`
      ),
  });
}

export function usePluginInstallation(installationId: string) {
  return useQuery({
    queryKey: ['plugin-installation', installationId],
    queryFn: () =>
      apiRequest<PluginInstallation>(`/plugins/installations/${installationId}/`),
    enabled: !!installationId,
  });
}

export function useInstallPlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) =>
      apiRequest<PluginInstallation>('/plugins/installations/', {
        method: 'POST',
        body: JSON.stringify({ plugin: pluginId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugin-installations'] });
    },
  });
}

export function useUninstallPlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (installationId: string) =>
      apiRequest(`/plugins/installations/${installationId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugin-installations'] });
    },
  });
}

export function useEnablePlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (installationId: string) =>
      apiRequest(`/plugins/installations/${installationId}/enable/`, {
        method: 'POST',
      }),
    onSuccess: (_, installationId) => {
      queryClient.invalidateQueries({ queryKey: ['plugin-installation', installationId] });
    },
  });
}

export function useDisablePlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (installationId: string) =>
      apiRequest(`/plugins/installations/${installationId}/disable/`, {
        method: 'POST',
      }),
    onSuccess: (_, installationId) => {
      queryClient.invalidateQueries({ queryKey: ['plugin-installation', installationId] });
    },
  });
}

export function useUpdatePluginSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      installationId,
      settings,
    }: {
      installationId: string;
      settings: Record<string, unknown>;
    }) =>
      apiRequest(`/plugins/installations/${installationId}/settings/`, {
        method: 'POST',
        body: JSON.stringify(settings),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['plugin-installation', variables.installationId],
      });
    },
  });
}

// Hooks for Plugin Reviews
export function usePluginReviews(pluginId: string) {
  return useQuery({
    queryKey: ['plugin-reviews', pluginId],
    queryFn: () => apiRequest<PluginReview[]>(`/plugins/plugins/${pluginId}/reviews/`),
    enabled: !!pluginId,
  });
}

export function useCreatePluginReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      pluginId,
      data,
    }: {
      pluginId: string;
      data: Partial<PluginReview>;
    }) =>
      apiRequest<PluginReview>(`/plugins/plugins/${pluginId}/reviews/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['plugin-reviews', variables.pluginId] });
    },
  });
}

// Hooks for Developer Profile
export function useDeveloperProfile(userId?: string) {
  return useQuery({
    queryKey: ['developer-profile', userId],
    queryFn: () =>
      apiRequest<DeveloperProfile>(
        `/plugins/developer/${userId ? `?user=${userId}` : ''}`
      ),
    enabled: !!userId,
  });
}

export function useCreateDeveloperProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<DeveloperProfile>) =>
      apiRequest<DeveloperProfile>('/plugins/developer/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['developer-profile'] });
    },
  });
}

export function useUpdateDeveloperProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      profileId,
      data,
    }: {
      profileId: string;
      data: Partial<DeveloperProfile>;
    }) =>
      apiRequest<DeveloperProfile>(`/plugins/developer/${profileId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['developer-profile', variables.profileId],
      });
    },
  });
}

// Hooks for API Documentation
export function usePluginAPIDocs(pluginId: string) {
  return useQuery({
    queryKey: ['plugin-api-docs', pluginId],
    queryFn: () =>
      apiRequest<APIEndpoint[]>(`/plugins/api-docs/?plugin=${pluginId}`),
    enabled: !!pluginId,
  });
}

// Hooks for Webhooks
export function useWebhookSubscriptions(pluginId?: string) {
  return useQuery({
    queryKey: ['webhook-subscriptions', pluginId],
    queryFn: () =>
      apiRequest<WebhookSubscription[]>(
        `/plugins/webhooks/${pluginId ? `?plugin=${pluginId}` : ''}`
      ),
    enabled: !!pluginId,
  });
}

export function useCreateWebhookSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<WebhookSubscription>) =>
      apiRequest<WebhookSubscription>('/plugins/webhooks/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhook-subscriptions'] });
    },
  });
}

export function useDeleteWebhookSubscription() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (webhookId: string) =>
      apiRequest(`/plugins/webhooks/${webhookId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['webhook-subscriptions'] });
    },
  });
}

// Hooks for Plugin Sandboxes
export function usePluginSandboxes(pluginId?: string) {
  return useQuery({
    queryKey: ['plugin-sandboxes', pluginId],
    queryFn: () =>
      apiRequest<PluginSandbox[]>(
        `/plugins/sandboxes/${pluginId ? `?plugin=${pluginId}` : ''}`
      ),
    enabled: !!pluginId,
  });
}

export function useCreatePluginSandbox() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<PluginSandbox>) =>
      apiRequest<PluginSandbox>('/plugins/sandboxes/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugin-sandboxes'] });
    },
  });
}

// Hooks for Plugin Logs
export function usePluginLogs(pluginId?: string, installationId?: string) {
  return useQuery({
    queryKey: ['plugin-logs', pluginId, installationId],
    queryFn: () => {
      const params = [];
      if (pluginId) params.push(`plugin=${pluginId}`);
      if (installationId) params.push(`installation=${installationId}`);
      const queryString = params.length ? `?${params.join('&')}` : '';
      return apiRequest<PluginLog[]>(`/plugins/logs/${queryString}`);
    },
    enabled: !!pluginId || !!installationId,
  });
}

// Hooks for Plugin Execution
export function useExecutePlugin() {
  return useMutation({
    mutationFn: async ({
      pluginId,
      method,
      params,
    }: {
      pluginId: string;
      method: string;
      params?: Record<string, unknown>;
    }) =>
      apiRequest<PluginExecutionResult>('/plugins/execute/', {
        method: 'POST',
        body: JSON.stringify({
          plugin_id: pluginId,
          method,
          params,
        }),
      }),
  });
}

export function useTriggerPluginEvent() {
  return useMutation({
    mutationFn: async ({
      eventType,
      data,
    }: {
      eventType: string;
      data?: Record<string, unknown>;
    }) =>
      apiRequest('/plugins/trigger-event/', {
        method: 'POST',
        body: JSON.stringify({
          event_type: eventType,
          data,
        }),
      }),
  });
}

// Hooks for Plugin Capabilities
export function usePluginCapabilities(pluginId: string) {
  return useQuery({
    queryKey: ['plugin-capabilities', pluginId],
    queryFn: () =>
      apiRequest<PluginCapabilities>(`/plugins/capabilities/?plugin_id=${pluginId}`),
    enabled: !!pluginId,
  });
}

// Upload Plugin Package
export function useUploadPluginPackage() {
  return useMutation({
    mutationFn: async ({
      pluginId,
      formData,
    }: {
      pluginId: string;
      formData: FormData;
    }) => {
      const response = await fetch(
        `${API_BASE}/plugins/plugins/${pluginId}/upload_package/`,
        {
          method: 'POST',
          body: formData,
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to upload plugin package');
      }

      return response.json();
    },
  });
}

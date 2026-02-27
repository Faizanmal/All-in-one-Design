'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Base API URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

// Generic API helper
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
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// ============================================
// INTEGRATIONS HOOKS
// ============================================

// Figma Integration
export function useFigmaImport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { file_key: string; access_token: string }) =>
      apiRequest('/integrations/figma/import/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useFigmaFrames(fileKey: string, accessToken: string) {
  return useQuery({
    queryKey: ['figma', 'frames', fileKey],
    queryFn: () =>
      apiRequest(`/integrations/figma/frames/?file_key=${fileKey}&access_token=${accessToken}`),
    enabled: !!fileKey && !!accessToken,
  });
}

// Stock Assets
export function useStockAssets(params: {
  provider: string;
  query: string;
  page?: number;
  per_page?: number;
}) {
  return useQuery({
    queryKey: ['stock-assets', params],
    queryFn: () => {
      const searchParams = new URLSearchParams({
        provider: params.provider,
        query: params.query,
        page: String(params.page || 1),
        per_page: String(params.per_page || 20),
      });
      return apiRequest(`/integrations/stock-assets/search/?${searchParams}`);
    },
    enabled: !!params.query,
  });
}

export function useDownloadStockAsset() {
  return useMutation({
    mutationFn: async (data: { provider: string; asset_id: string; download_url: string }) =>
      apiRequest('/integrations/stock-assets/download/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

// ============================================
// MARKETPLACE HOOKS
// ============================================

export function useMarketplaceTemplates(params?: {
  category?: string;
  search?: string;
  sort?: string;
  price_filter?: string;
  page?: number;
}) {
  return useQuery({
    queryKey: ['marketplace', 'templates', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.category) searchParams.set('category', params.category);
      if (params?.search) searchParams.set('search', params.search);
      if (params?.sort) searchParams.set('sort', params.sort);
      if (params?.price_filter) searchParams.set('price_filter', params.price_filter);
      if (params?.page) searchParams.set('page', String(params.page));
      return apiRequest(`/subscriptions/marketplace/templates/?${searchParams}`);
    },
  });
}

export function useMarketplaceTemplate(id: string) {
  return useQuery({
    queryKey: ['marketplace', 'templates', id],
    queryFn: () => apiRequest(`/subscriptions/marketplace/templates/${id}/`),
    enabled: !!id,
  });
}

export function usePurchaseTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (templateId: string) =>
      apiRequest(`/subscriptions/marketplace/templates/${templateId}/purchase/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'purchases'] });
    },
  });
}

export function useUseTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (templateId: string) =>
      apiRequest(`/subscriptions/marketplace/templates/${templateId}/use/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

// Creator Dashboard
export function useCreatorStats() {
  return useQuery({
    queryKey: ['marketplace', 'creator', 'stats'],
    queryFn: () => apiRequest('/subscriptions/marketplace/creator/stats/'),
  });
}

export function useCreatorTemplates() {
  return useQuery({
    queryKey: ['marketplace', 'creator', 'templates'],
    queryFn: () => apiRequest('/subscriptions/marketplace/creator/templates/'),
  });
}

export function useCreatorEarnings(params?: { period?: string }) {
  return useQuery({
    queryKey: ['marketplace', 'creator', 'earnings', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.period) searchParams.set('period', params.period);
      return apiRequest(`/subscriptions/marketplace/creator/earnings/?${searchParams}`);
    },
  });
}

export function useUploadTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${API_BASE}/subscriptions/marketplace/templates/upload/`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Upload failed');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['marketplace', 'creator', 'templates'] });
    },
  });
}

// ============================================
// DEVELOPER HANDOFF HOOKS
// ============================================

export function useExportCode() {
  return useMutation({
    mutationFn: async (data: {
      project_id: string;
      framework: 'react' | 'vue' | 'html' | 'tailwind';
      options?: {
        typescript?: boolean;
        css_modules?: boolean;
        responsive?: boolean;
      };
    }) =>
      apiRequest('/v1/projects/developer-handoff/export-code/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useGenerateDesignSystem() {
  return useMutation({
    mutationFn: async (data: { project_id: string; options?: Record<string, boolean> }) =>
      apiRequest('/v1/projects/developer-handoff/design-system/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useExportAssets() {
  return useMutation({
    mutationFn: async (data: {
      project_id: string;
      format: 'svg' | 'png' | 'webp';
      scale?: number;
    }) =>
      apiRequest('/v1/projects/developer-handoff/export-assets/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

// ============================================
// PRODUCTIVITY HOOKS
// ============================================

// A/B Testing
export function useABTests(params?: { project_id?: string; status?: string }) {
  return useQuery({
    queryKey: ['ab-tests', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.project_id) searchParams.set('project_id', params.project_id);
      if (params?.status) searchParams.set('status', params.status);
      return apiRequest(`/v1/projects/productivity/ab-tests/?${searchParams}`);
    },
  });
}

export function useABTest(id: string) {
  return useQuery({
    queryKey: ['ab-tests', id],
    queryFn: () => apiRequest(`/v1/projects/productivity/ab-tests/${id}/`),
    enabled: !!id,
  });
}

export function useCreateABTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      name: string;
      description?: string;
      project_id: string;
      variants: Array<{ name: string; design_id: string; traffic_percentage: number }>;
      goal_type: string;
    }) =>
      apiRequest('/v1/projects/productivity/ab-tests/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ab-tests'] });
    },
  });
}

export function useUpdateABTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      apiRequest(`/v1/projects/productivity/ab-tests/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ab-tests'] });
      queryClient.invalidateQueries({ queryKey: ['ab-tests', variables.id] });
    },
  });
}

export function useABTestResults(testId: string) {
  return useQuery({
    queryKey: ['ab-tests', testId, 'results'],
    queryFn: () => apiRequest(`/v1/projects/productivity/ab-tests/${testId}/results/`),
    enabled: !!testId,
  });
}

// Plugins
export function usePlugins(params?: { category?: string; search?: string }) {
  return useQuery({
    queryKey: ['plugins', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.category) searchParams.set('category', params.category);
      if (params?.search) searchParams.set('search', params.search);
      return apiRequest(`/v1/projects/productivity/plugins/?${searchParams}`);
    },
  });
}

export function usePlugin(id: string) {
  return useQuery({
    queryKey: ['plugins', id],
    queryFn: () => apiRequest(`/v1/projects/productivity/plugins/${id}/`),
    enabled: !!id,
  });
}

export function useInstalledPlugins() {
  return useQuery({
    queryKey: ['plugins', 'installed'],
    queryFn: () => apiRequest('/v1/projects/productivity/plugins/installed/'),
  });
}

export function useInstallPlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) =>
      apiRequest(`/v1/projects/productivity/plugins/${pluginId}/install/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins', 'installed'] });
    },
  });
}

export function useUninstallPlugin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (pluginId: string) =>
      apiRequest(`/v1/projects/productivity/plugins/${pluginId}/uninstall/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plugins', 'installed'] });
    },
  });
}

// ============================================
// ANALYTICS HOOKS
// ============================================

export function useAnalyticsOverview(params?: { time_range?: string }) {
  return useQuery({
    queryKey: ['analytics', 'overview', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.time_range) searchParams.set('time_range', params.time_range);
      return apiRequest(`/analytics/advanced/overview/?${searchParams}`);
    },
  });
}

export function useAnalyticsActivity(params?: { time_range?: string }) {
  return useQuery({
    queryKey: ['analytics', 'activity', params],
    queryFn: () => {
      const searchParams = new URLSearchParams();
      if (params?.time_range) searchParams.set('time_range', params.time_range);
      return apiRequest(`/analytics/advanced/activity/?${searchParams}`);
    },
  });
}

export function useAnalyticsInsights() {
  return useQuery({
    queryKey: ['analytics', 'insights'],
    queryFn: () => apiRequest('/analytics/advanced/insights/'),
  });
}

export function useAnalyticsTrends() {
  return useQuery({
    queryKey: ['analytics', 'trends'],
    queryFn: () => apiRequest('/analytics/advanced/trends/'),
  });
}

export function useAnalyticsRecommendations() {
  return useQuery({
    queryKey: ['analytics', 'recommendations'],
    queryFn: () => apiRequest('/analytics/advanced/recommendations/'),
  });
}

// Custom Reports
export function useCustomReports() {
  return useQuery({
    queryKey: ['analytics', 'reports'],
    queryFn: () => apiRequest('/analytics/advanced/reports/'),
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      name: string;
      description?: string;
      fields: string[];
      filters?: Array<{ field: string; operator: string; value: unknown }>;
      visualization: string;
      date_range: { start: string; end: string };
    }) =>
      apiRequest('/analytics/advanced/reports/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analytics', 'reports'] });
    },
  });
}

export function usePreviewReport() {
  return useMutation({
    mutationFn: async (config: Record<string, unknown>) =>
      apiRequest('/analytics/advanced/reports/preview/', {
        method: 'POST',
        body: JSON.stringify(config),
      }),
  });
}

export function useExportReport() {
  return useMutation({
    mutationFn: async ({ config, format }: { config: Record<string, unknown>; format: string }) => {
      const response = await fetch(
        `${API_BASE}/analytics/advanced/reports/export/?format=${format}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config),
        }
      );
      if (!response.ok) throw new Error('Export failed');
      return response.blob();
    },
  });
}

// ============================================
// ADVANCED AI HOOKS
// ============================================

export function useAIStyles() {
  return useQuery({
    queryKey: ['ai', 'styles'],
    queryFn: () => apiRequest('/ai-services/advanced/styles/'),
  });
}

export function useGenerateAIDesign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      prompt: string;
      style?: string;
      dimensions?: { width: number; height: number };
    }) =>
      apiRequest('/ai-services/advanced/generate-design/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai', 'generations'] });
    },
  });
}

export function useAIImageEdit() {
  return useMutation({
    mutationFn: async (data: {
      image_url: string;
      edit_type: 'remove_background' | 'enhance' | 'recolor' | 'resize';
      options?: Record<string, unknown>;
    }) =>
      apiRequest('/ai-services/advanced/edit-image/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useAIContentSuggestions() {
  return useMutation({
    mutationFn: async (data: { context: string; type: 'headline' | 'copy' | 'cta' }) =>
      apiRequest('/ai-services/advanced/content-suggestions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useAILayoutSuggestions() {
  return useMutation({
    mutationFn: async (data: { content_type: string; elements: string[] }) =>
      apiRequest('/ai-services/advanced/layout-suggestions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

// ============================================
// COLLABORATION HOOKS
// ============================================

export function useVideoRooms(projectId: string) {
  return useQuery({
    queryKey: ['collaboration', 'video-rooms', projectId],
    queryFn: () => apiRequest(`/v1/projects/collaboration/video-rooms/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

export function useCreateVideoRoom() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { project_id: string; name: string }) =>
      apiRequest('/v1/projects/collaboration/video-rooms/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['collaboration', 'video-rooms', variables.project_id],
      });
    },
  });
}

export function useDesignReviews(projectId: string) {
  return useQuery({
    queryKey: ['collaboration', 'reviews', projectId],
    queryFn: () => apiRequest(`/v1/projects/collaboration/reviews/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

export function useCreateDesignReview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      project_id: string;
      title: string;
      description?: string;
      reviewers: string[];
      due_date?: string;
    }) =>
      apiRequest('/v1/projects/collaboration/reviews/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['collaboration', 'reviews', variables.project_id],
      });
    },
  });
}

export function useSubmitReviewAnnotation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      review_id: string;
      annotation_type: 'comment' | 'suggestion' | 'approval' | 'rejection';
      content: string;
      position?: { x: number; y: number };
    }) =>
      apiRequest(`/v1/projects/collaboration/reviews/${data.review_id}/annotations/`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['collaboration', 'reviews', variables.review_id, 'annotations'],
      });
    },
  });
}

export function useGuestAccess(projectId: string) {
  return useQuery({
    queryKey: ['collaboration', 'guest-access', projectId],
    queryFn: () => apiRequest(`/v1/projects/collaboration/guest-access/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

export function useCreateGuestAccess() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      project_id: string;
      email: string;
      permissions: string[];
      expires_at?: string;
    }) =>
      apiRequest('/v1/projects/collaboration/guest-access/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['collaboration', 'guest-access', variables.project_id],
      });
    },
  });
}

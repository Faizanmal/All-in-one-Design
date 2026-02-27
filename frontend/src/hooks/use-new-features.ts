'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

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
// AI QUOTA & USAGE HOOKS
// ============================================

export interface QuotaInfo {
  plan_name: string;
  text_operations_used: number;
  text_operations_limit: number;
  image_generations_used: number;
  image_generations_limit: number;
  api_calls_used: number;
  api_calls_limit: number;
  budget_limit: number;
  reset_date: string;
}

export interface QuotaData {
  id: number;
  period_start: string;
  period_end: string;
  ai_requests_used: number;
  ai_requests_limit: number;
  requests_remaining: number;
  ai_tokens_used: number;
  ai_tokens_limit: number;
  tokens_remaining: number;
  image_generations_used: number;
  image_generations_limit: number;
  total_cost: string;
  budget_limit: string;
  budget_remaining: string;
  success_rate: number;
  is_request_limit_reached: boolean;
  is_budget_exceeded: boolean;
}

export interface UsageSummary {
  period: string;
  start_date: string;
  end_date: string;
  totals: {
    requests: number;
    tokens: number;
    images: number;
    cost: number;
  };
  by_type: Record<string, {
    count: number;
    tokens: number;
    images: number;
    cost: number;
    success_rate: number;
  }>;
  quota_usage: {
    requests_percent: number;
    tokens_percent: number;
    budget_percent: number;
  };
}

export interface QuotaCheck {
  allowed: boolean;
  dry_run: boolean;
  request_type: string;
  estimated_tokens: number;
  estimated_cost: number;
  current_usage: {
    requests: number;
    tokens: number;
    images: number;
    cost: number;
  };
  limits: {
    requests: number;
    tokens: number;
    images: number;
    budget: number;
  };
  remaining: {
    requests: number;
    tokens: number;
    images: number;
    budget: number;
  };
  reset_at: string;
  error?: string;
  message?: string;
}

export function useCurrentQuota() {
  return useQuery<QuotaData>({
    queryKey: ['quota', 'current'],
    queryFn: () => apiRequest('/subscriptions/quotas/current/'),
    staleTime: 60000, // 1 minute
  });
}

export function useQuotaHistory() {
  return useQuery<QuotaData[]>({
    queryKey: ['quota', 'history'],
    queryFn: () => apiRequest('/subscriptions/quotas/'),
  });
}

export function useUsageSummary(period: 'day' | 'week' | 'month' | 'year' = 'month') {
  return useQuery<UsageSummary>({
    queryKey: ['quota', 'summary', period],
    queryFn: () => apiRequest(`/subscriptions/quota/usage-summary/?period=${period}`),
  });
}

export function useQuotaDashboard() {
  return useQuery({
    queryKey: ['quota', 'dashboard'],
    queryFn: () => apiRequest('/subscriptions/quota/dashboard/'),
  });
}

export function useCheckQuota() {
  return useMutation<QuotaCheck, Error, { request_type: string; dry_run?: boolean }>({
    mutationFn: (data) =>
      apiRequest('/subscriptions/quotas/check/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  });
}

export function useCostEstimate(operations: string[]) {
  return useQuery({
    queryKey: ['quota', 'estimate', operations],
    queryFn: () => apiRequest(`/subscriptions/quota/estimate/?operations=${operations.join(',')}`),
    enabled: operations.length > 0,
  });
}

export function useDryRunCheck() {
  return useMutation<{
    allowed: boolean;
    estimated_cost: number;
    remaining_budget: number;
    remaining_quota: number;
    warnings?: string[];
  }, Error, {
    operationType: string;
    amount?: number;
  }>({
    mutationFn: ({ operationType, amount = 1 }) =>
      apiRequest('/subscriptions/quota/dry-run/', {
        method: 'POST',
        body: JSON.stringify({
          request_type: operationType,
          amount,
          dry_run: true,
        }),
      }),
  });
}

// ============================================
// VERSION CONTROL HOOKS
// ============================================

export interface ProjectSnapshot {
  id: number;
  version_number: number;
  version_label: string;
  canvas_settings: {
    width: number;
    height: number;
    background: string;
  };
  components_count: number;
  content_hash: string;
  change_summary: string;
  change_type: string;
  created_by: number;
  created_by_username: string;
  branch_name: string;
  is_branch_head: boolean;
  thumbnail_url: string | null;
  created_at: string;
}

export interface VersionDiff {
  from_version: number;
  to_version: number;
  diff: {
    added: Record<string, unknown>[];
    removed: Record<string, unknown>[];
    modified: Record<string, unknown>[];
    settings_changes: Record<string, unknown>[];
    summary: {
      added_count: number;
      removed_count: number;
      modified_count: number;
    };
  };
}

export interface Branch {
  name: string;
  head_version: number | null;
  head_label: string | null;
  snapshot_count: number;
  last_updated: string | null;
}

export function useProjectVersions(projectId: string, options?: { branch?: string; limit?: number }) {
  return useQuery({
    queryKey: ['project', projectId, 'versions', options],
    queryFn: () => {
      const params = new URLSearchParams();
      if (options?.branch) params.set('branch', options.branch);
      if (options?.limit) params.set('limit', String(options.limit));
      return apiRequest(`/v1/projects/${projectId}/versions/?${params}`);
    },
    enabled: !!projectId,
  });
}

export function useProjectVersion(projectId: string, versionNumber: number) {
  return useQuery<ProjectSnapshot>({
    queryKey: ['project', projectId, 'versions', versionNumber],
    queryFn: () => apiRequest(`/v1/projects/${projectId}/versions/${versionNumber}/`),
    enabled: !!projectId && !!versionNumber,
  });
}

export function useCreateSnapshot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ projectId, label, changeSummary, branchName }: {
      projectId: string;
      label?: string;
      changeSummary?: string;
      branchName?: string;
    }) =>
      apiRequest(`/v1/projects/${projectId}/versions/`, {
        method: 'POST',
        body: JSON.stringify({
          label,
          change_summary: changeSummary,
          branch_name: branchName,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId, 'versions'] });
    },
  });
}

export function useRestoreVersion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ projectId, versionNumber, createBackup = true }: {
      projectId: string;
      versionNumber: number;
      createBackup?: boolean;
    }) =>
      apiRequest(`/v1/projects/${projectId}/versions/${versionNumber}/restore/`, {
        method: 'POST',
        body: JSON.stringify({ create_backup: createBackup }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useCreateBranch() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ projectId, branchName, fromVersion }: {
      projectId: string;
      branchName: string;
      fromVersion?: number;
    }) =>
      apiRequest(`/v1/projects/${projectId}/versions/branch/`, {
        method: 'POST',
        body: JSON.stringify({
          branch_name: branchName,
          from_version: fromVersion,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId, 'versions'] });
    },
  });
}

export function useVersionDiff() {
  return useMutation<VersionDiff, Error, { projectId: string; fromVersion: number; toVersion: number }>({
    mutationFn: ({ projectId, fromVersion, toVersion }) =>
      apiRequest(`/v1/projects/${projectId}/versions/diff/`, {
        method: 'POST',
        body: JSON.stringify({
          from_version: fromVersion,
          to_version: toVersion,
        }),
      }),
  });
}

export function useProjectBranches(projectId: string) {
  return useQuery<Branch[]>({
    queryKey: ['project', projectId, 'branches'],
    queryFn: () => apiRequest(`/v1/projects/${projectId}/versions/branches/`),
    enabled: !!projectId,
  });
}

// ============================================
// ACCESSIBILITY AUDIT HOOKS
// ============================================

export interface AccessibilityIssue {
  id: string;
  severity: 'error' | 'warning' | 'suggestion';
  category: string;
  title: string;
  description: string;
  wcag_criterion: string;
  wcag_level: 'A' | 'AA' | 'AAA';
  component_id: string | null;
  component_type: string | null;
  current_value: Record<string, unknown>;
  suggested_fix: Record<string, unknown>;
  auto_fixable: boolean;
}

export interface AccessibilityAuditResult {
  project_id: number;
  project_name: string;
  score: number;
  level_achieved: string | null;
  target_level: string;
  total_issues: number;
  issues_by_severity: {
    error: number;
    warning: number;
    suggestion: number;
  };
  issues_by_category: Record<string, number>;
  issues: AccessibilityIssue[];
  auto_fixable_count: number;
  recommendations: Array<{
    priority: string;
    title: string;
    description: string;
  }>;
}

export interface ContrastCheckResult {
  foreground: string;
  background: string;
  contrast_ratio: number;
  is_large_text: boolean;
  passes_wcag_aa: boolean;
  passes_wcag_aaa: boolean;
  suggested_color: string | null;
}

export function useAccessibilityAudit(projectId: string, options?: { targetLevel?: 'A' | 'AA' | 'AAA' }) {
  return useQuery<AccessibilityAuditResult>({
    queryKey: ['accessibility', 'audit', projectId, options?.targetLevel],
    queryFn: () => {
      if (options?.targetLevel) {
        return apiRequest(`/ai/accessibility/projects/${projectId}/audit/`, {
          method: 'POST',
          body: JSON.stringify({ target_level: options.targetLevel }),
        });
      }
      return apiRequest(`/ai/accessibility/projects/${projectId}/audit/`);
    },
    enabled: !!projectId,
  });
}

export function useApplyAccessibilityFixes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ projectId, applyAll = false, issueIds = [] }: {
      projectId: string;
      applyAll?: boolean;
      issueIds?: string[];
    }) =>
      apiRequest(`/ai/accessibility/projects/${projectId}/fix/`, {
        method: 'POST',
        body: JSON.stringify({
          apply_all: applyAll,
          issue_ids: issueIds,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['accessibility', 'audit', variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useCheckContrast() {
  return useMutation<ContrastCheckResult, Error, {
    foreground: string;
    background: string;
    fontSize?: number;
    fontWeight?: number;
  }>({
    mutationFn: (data) =>
      apiRequest('/ai/accessibility/check-contrast/', {
        method: 'POST',
        body: JSON.stringify({
          foreground: data.foreground,
          background: data.background,
          font_size: data.fontSize,
          font_weight: data.fontWeight,
        }),
      }),
  });
}

export function useAnalyzePalette() {
  return useMutation({
    mutationFn: async ({ colors, background }: { colors: string[]; background?: string }) =>
      apiRequest('/ai/accessibility/analyze-palette/', {
        method: 'POST',
        body: JSON.stringify({ colors, background }),
      }),
  });
}

// ============================================
// REAL-TIME COLLABORATION HOOKS
// ============================================

export interface CollaborationUser {
  user_id: number;
  username: string;
  color: string;
  connected_at: string;
  last_seen: string;
}

export interface CursorPosition {
  user_id: number;
  username: string;
  x: number;
  y: number;
  component_id?: string;
  timestamp: string;
}

export interface ComponentLock {
  user_id: number;
  username: string;
  acquired_at: string;
}

export function useCollaborationConnection(projectId: string) {
  // This hook would set up the WebSocket connection
  // Implementation depends on your WebSocket library preference
  
  const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/project/${projectId}/collaborate/`;
  
  // Return connection status and methods
  return {
    wsUrl,
    // The actual WebSocket logic would be implemented here
    // using something like react-use-websocket or a custom hook
  };
}

// ============================================
// SMART AUTO-LAYOUT HOOKS
// ============================================

export interface LayoutSuggestion {
  id: string;
  name: string;
  description: string;
  preview: string;
  confidence: number;
  changes: Record<string, unknown>[];
}

export interface LayoutPreset {
  id: string;
  name: string;
  description: string;
  category: string;
  config: Record<string, unknown>;
}

export function useAutoLayoutSuggestions(projectId: string, componentIds: number[]) {
  return useMutation({
    mutationFn: () =>
      apiRequest(`/ai/auto-layout/projects/${projectId}/suggest/`, {
        method: 'POST',
        body: JSON.stringify({ component_ids: componentIds }),
      }),
  });
}

export function useApplyLayoutPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      projectId,
      presetId,
      componentIds,
      options,
    }: {
      projectId: string;
      presetId: string;
      componentIds: number[];
      options?: Record<string, unknown>;
    }) =>
      apiRequest(`/ai/auto-layout/projects/${projectId}/apply-preset/`, {
        method: 'POST',
        body: JSON.stringify({
          preset_id: presetId,
          component_ids: componentIds,
          options,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useAlignToGrid() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      projectId,
      componentIds,
      gridSize,
    }: {
      projectId: string;
      componentIds: number[];
      gridSize: number;
    }) =>
      apiRequest(`/ai/auto-layout/projects/${projectId}/align-to-grid/`, {
        method: 'POST',
        body: JSON.stringify({
          component_ids: componentIds,
          grid_size: gridSize,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useLayoutPresets() {
  return useQuery<LayoutPreset[]>({
    queryKey: ['auto-layout', 'presets'],
    queryFn: () => apiRequest('/ai/auto-layout/presets/'),
  });
}

// ============================================
// DESIGN TOKENS HOOKS
// ============================================

export interface DesignTokenLibrary {
  id: number;
  name: string;
  description: string;
  version: string;
  token_count: number;
  theme_count: number;
  is_default: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface DesignToken {
  id: number;
  name: string;
  category: string;
  token_type: string;
  value: string;
  resolved_value: string;
  css_variable: string;
  description: string;
  deprecated: boolean;
}

export interface DesignTheme {
  id: number;
  name: string;
  slug: string;
  theme_type: string;
  is_default: boolean;
  override_count: number;
}

export function useDesignTokenLibraries() {
  return useQuery<{ libraries: DesignTokenLibrary[] }>({
    queryKey: ['design-token-libraries'],
    queryFn: () => apiRequest('/v1/projects/design-token-libraries/'),
  });
}

export function useDesignTokenLibrary(libraryId: number) {
  return useQuery<DesignTokenLibrary & { tokens: DesignToken[]; themes: DesignTheme[] }>({
    queryKey: ['design-token-libraries', libraryId],
    queryFn: () => apiRequest(`/v1/projects/design-token-libraries/${libraryId}/`),
    enabled: !!libraryId,
  });
}

export function useCreateTokenLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: { name: string; description?: string; is_public?: boolean }) =>
      apiRequest('/v1/projects/design-token-libraries/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['design-token-libraries'] });
    },
  });
}

export function useCreateDesignToken() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      libraryId,
      ...data
    }: {
      libraryId: number;
      name: string;
      category: string;
      token_type: string;
      value: string;
      description?: string;
    }) =>
      apiRequest('/v1/projects/design-tokens/', {
        method: 'POST',
        body: JSON.stringify({ library_id: libraryId, ...data }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['design-token-libraries', variables.libraryId] });
    },
  });
}

export function useExportTokens(libraryId: number, format: string) {
  return useQuery({
    queryKey: ['design-tokens-export', libraryId, format],
    queryFn: () => apiRequest(`/v1/projects/design-token-libraries/${libraryId}/export/?format=${format}`),
    enabled: !!libraryId && !!format,
  });
}

// ============================================
// BATCH OPERATIONS HOOKS
// ============================================

export interface BatchOperation {
  id: number;
  operation_type: string;
  status: string;
  component_count: number;
  success_count: number;
  error_count: number;
  created_at: string;
  completed_at: string | null;
}

export function useBatchOperationHistory(projectId: string) {
  return useQuery<{ history: BatchOperation[] }>({
    queryKey: ['batch-operations-history', projectId],
    queryFn: () => apiRequest(`/v1/projects/batch-operations/history/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

export function useBatchMove() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      componentIds,
      deltaX,
      deltaY,
    }: {
      projectId: string;
      componentIds: number[];
      deltaX: number;
      deltaY: number;
    }) =>
      apiRequest('/v1/projects/batch-operations/move/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          component_ids: componentIds,
          delta_x: deltaX,
          delta_y: deltaY,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
      queryClient.invalidateQueries({ queryKey: ['batch-operations-history', variables.projectId] });
    },
  });
}

export function useBatchAlign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      componentIds,
      alignment,
    }: {
      projectId: string;
      componentIds: number[];
      alignment: 'left' | 'center' | 'right' | 'top' | 'middle' | 'bottom';
    }) =>
      apiRequest('/v1/projects/batch-operations/align/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          component_ids: componentIds,
          alignment,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useBatchDistribute() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      componentIds,
      direction,
    }: {
      projectId: string;
      componentIds: number[];
      direction: 'horizontal' | 'vertical';
    }) =>
      apiRequest('/v1/projects/batch-operations/distribute/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          component_ids: componentIds,
          direction,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useBatchDelete() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      projectId,
      componentIds,
    }: {
      projectId: string;
      componentIds: number[];
    }) =>
      apiRequest('/v1/projects/batch-operations/delete/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          component_ids: componentIds,
        }),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['project', variables.projectId] });
    },
  });
}

export function useUndoBatchOperation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: number) =>
      apiRequest(`/projects/batch-operations/${operationId}/undo/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch-operations-history'] });
    },
  });
}

// ============================================
// EXPORT PRESETS HOOKS
// ============================================

export interface ExportPreset {
  id: number;
  name: string;
  description: string;
  format: string;
  scale: string;
  quality: number;
  is_default: boolean;
  include_background: boolean;
  optimize_for_web: boolean;
  file_naming_pattern: string;
  created_at: string;
}

export interface ExportBundle {
  id: number;
  name: string;
  description: string;
  platform: string;
  preset_count: number;
}

export interface ScheduledExport {
  id: number;
  name: string;
  schedule_type: string;
  status: string;
  next_run: string | null;
  last_run: string | null;
  run_count: number;
}

export interface ExportHistoryItem {
  id: number;
  status: string;
  format: string;
  file_count: number;
  total_size: number;
  duration_ms: number;
  created_at: string;
}

export function useExportPresets() {
  return useQuery<{ presets: ExportPreset[]; default_presets: Record<string, unknown>[] }>({
    queryKey: ['export-presets'],
    queryFn: () => apiRequest('/v1/projects/export-presets/'),
  });
}

export function useCreateExportPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<ExportPreset, 'id' | 'created_at'>) =>
      apiRequest('/v1/projects/export-presets/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['export-presets'] });
    },
  });
}

export function useDeleteExportPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (presetId: number) =>
      apiRequest(`/projects/export-presets/${presetId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['export-presets'] });
    },
  });
}

export function useQuickExport() {
  return useMutation({
    mutationFn: ({
      projectId,
      format,
      scale,
      componentIds,
    }: {
      projectId: string;
      format: string;
      scale: string;
      componentIds?: number[];
    }) =>
      apiRequest('/v1/projects/export/quick/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          format,
          scale,
          component_ids: componentIds,
        }),
      }),
  });
}

export function useExportWithPreset() {
  return useMutation({
    mutationFn: ({
      projectId,
      presetId,
      componentIds,
    }: {
      projectId: string;
      presetId: number;
      componentIds?: number[];
    }) =>
      apiRequest('/v1/projects/export/with_preset/', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          preset_id: presetId,
          component_ids: componentIds,
        }),
      }),
  });
}

export function useExportBundles() {
  return useQuery<{ bundles: ExportBundle[]; platform_bundles: Record<string, unknown> }>({
    queryKey: ['export-bundles'],
    queryFn: () => apiRequest('/v1/projects/export-bundles/'),
  });
}

export function useScheduledExports(projectId: string) {
  return useQuery<{ scheduled_exports: ScheduledExport[] }>({
    queryKey: ['scheduled-exports', projectId],
    queryFn: () => apiRequest(`/projects/scheduled-exports/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

export function useExportHistory(projectId: string) {
  return useQuery<{ history: ExportHistoryItem[] }>({
    queryKey: ['export-history', projectId],
    queryFn: () => apiRequest(`/projects/export-history/?project_id=${projectId}`),
    enabled: !!projectId,
  });
}

// ============================================
// KEYBOARD SHORTCUTS HOOKS
// ============================================

export interface KeyboardShortcut {
  action_id: string;
  name: string;
  description: string;
  category: string;
  key: string;
  default_key: string;
  is_custom: boolean;
  is_enabled: boolean;
  is_customizable: boolean;
}

export interface ShortcutPreset {
  id: number;
  name: string;
  description: string;
  shortcut_count: number;
  icon?: string;
}

export interface LearningStats {
  is_learning_mode: boolean;
  daily_goal: number;
  shortcuts_used_today: number;
  current_streak: number;
  best_streak: number;
  shortcuts_learned: number;
  most_used: Array<{ shortcut__name: string; count: number }>;
  to_learn: Array<{ shortcut__name: string; shortcut__default_key: string; count: number }>;
}

export function useKeyboardShortcuts(platform?: string) {
  return useQuery<{ shortcuts: KeyboardShortcut[]; total: number }>({
    queryKey: ['keyboard-shortcuts', platform],
    queryFn: () => apiRequest(`/projects/shortcuts/${platform ? `?platform=${platform}` : ''}`),
  });
}

export function useShortcutsByCategory() {
  return useQuery<{ categories: Record<string, KeyboardShortcut[]> }>({
    queryKey: ['keyboard-shortcuts-categories'],
    queryFn: () => apiRequest('/v1/projects/shortcuts/by_category/'),
  });
}

export function useSetShortcut() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ actionId, key }: { actionId: string; key: string }) =>
      apiRequest('/v1/projects/shortcuts/set/', {
        method: 'POST',
        body: JSON.stringify({ action_id: actionId, key }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
    },
  });
}

export function useResetShortcut() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (actionId: string) =>
      apiRequest('/v1/projects/shortcuts/reset/', {
        method: 'POST',
        body: JSON.stringify({ action_id: actionId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
    },
  });
}

export function useResetAllShortcuts() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      apiRequest('/v1/projects/shortcuts/reset_all/', {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
    },
  });
}

export function useSearchShortcuts(query: string) {
  return useQuery<{ query: string; results: KeyboardShortcut[]; count: number }>({
    queryKey: ['keyboard-shortcuts-search', query],
    queryFn: () => apiRequest(`/projects/shortcuts/search/?q=${encodeURIComponent(query)}`),
    enabled: query.length > 0,
  });
}

export function useShortcutPresets() {
  return useQuery<{
    user_presets: ShortcutPreset[];
    system_presets: ShortcutPreset[];
    application_presets: Record<string, unknown>;
  }>({
    queryKey: ['shortcut-presets'],
    queryFn: () => apiRequest('/v1/projects/shortcut-presets/'),
  });
}

export function useApplyShortcutPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (presetId: number) =>
      apiRequest(`/projects/shortcut-presets/${presetId}/apply/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keyboard-shortcuts'] });
    },
  });
}

export function useLearningStats() {
  return useQuery<LearningStats>({
    queryKey: ['shortcuts-learning-stats'],
    queryFn: () => apiRequest('/v1/projects/shortcuts-learning/stats/'),
  });
}

export function useToggleLearningMode() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (enabled: boolean) =>
      apiRequest('/v1/projects/shortcuts-learning/toggle/', {
        method: 'POST',
        body: JSON.stringify({ enabled }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shortcuts-learning-stats'] });
    },
  });
}

export function useLogShortcutUsage() {
  return useMutation({
    mutationFn: ({ actionId, usedShortcut }: { actionId: string; usedShortcut: boolean }) =>
      apiRequest('/v1/projects/shortcuts-learning/log_usage/', {
        method: 'POST',
        body: JSON.stringify({ action_id: actionId, used_shortcut: usedShortcut }),
      }),
  });
}

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
// OPTIMIZATION - AI Design Optimization
// ============================================

export interface ABTest {
  id: string;
  name: string;
  project: string;
  variant_a: string;
  variant_b: string;
  metric: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  impressions_a: number;
  impressions_b: number;
  conversions_a: number;
  conversions_b: number;
  confidence_level: number;
  winning_variant?: 'A' | 'B' | 'none';
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface PerformanceAnalysis {
  id: string;
  design: string;
  load_time: number;
  first_contentful_paint: number;
  largest_contentful_paint: number;
  cumulative_layout_shift: number;
  time_to_interactive: number;
  total_blocking_time: number;
  asset_count: number;
  total_size_kb: number;
  image_optimization_score: number;
  code_optimization_score: number;
  caching_score: number;
  overall_score: number;
  recommendations: Array<{
    severity: 'critical' | 'high' | 'medium' | 'low';
    title: string;
    description: string;
    impact: string;
  }>;
  created_at: string;
}

export interface DeviceCompatibility {
  id: string;
  design: string;
  device_type: 'desktop' | 'tablet' | 'mobile';
  device_model: string;
  screen_width: number;
  screen_height: number;
  viewport_width: number;
  viewport_height: number;
  pixel_ratio: number;
  browser: string;
  browser_version: string;
  compatibility_score: number;
  layout_issues: Array<{
    severity: string;
    element: string;
    issue: string;
    suggestion: string;
  }>;
  rendering_issues: string[];
  touch_target_issues: string[];
  created_at: string;
}

export interface SmartLayoutSuggestion {
  id: string;
  design: string;
  suggestion_type: 'spacing' | 'alignment' | 'hierarchy' | 'contrast' | 'accessibility';
  title: string;
  description: string;
  confidence: number;
  before_preview?: string;
  after_preview?: string;
  changes: Array<{
    element: string;
    property: string;
    current_value: string;
    suggested_value: string;
  }>;
  is_applied: boolean;
  created_at: string;
}

export interface OptimizationReport {
  id: string;
  project: string;
  report_type: 'performance' | 'accessibility' | 'seo' | 'ux' | 'comprehensive';
  overall_score: number;
  performance_score: number;
  accessibility_score: number;
  seo_score: number;
  ux_score: number;
  key_findings: Array<{
    category: string;
    severity: string;
    finding: string;
    recommendation: string;
  }>;
  action_items: Array<{
    priority: string;
    title: string;
    description: string;
    estimated_impact: string;
  }>;
  generated_at: string;
  created_at: string;
}

export interface DesignAnalysis {
  visual_weight_score: number;
  color_harmony_score: number;
  typography_consistency: number;
  spacing_consistency: number;
  contrast_ratio: number;
  accessibility_score: number;
  suggestions: Array<{
    category: string;
    suggestion: string;
    priority: string;
  }>;
}

export interface BehaviorPrediction {
  click_heatmap: Record<string, number>;
  attention_map: Record<string, number>;
  scroll_depth_prediction: number;
  engagement_score: number;
  conversion_probability: number;
  recommendations: string[];
}

// Hooks for A/B Tests
export function useABTests(projectId?: string) {
  return useQuery({
    queryKey: ['ab-tests', projectId],
    queryFn: () =>
      apiRequest<ABTest[]>(
        `/optimization/ab-tests/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useABTest(testId: string) {
  return useQuery({
    queryKey: ['ab-test', testId],
    queryFn: () => apiRequest<ABTest>(`/optimization/ab-tests/${testId}/`),
    enabled: !!testId,
  });
}

export function useCreateABTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ABTest>) =>
      apiRequest<ABTest>('/optimization/ab-tests/', {
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
    mutationFn: async ({
      testId,
      data,
    }: {
      testId: string;
      data: Partial<ABTest>;
    }) =>
      apiRequest<ABTest>(`/optimization/ab-tests/${testId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['ab-test', variables.testId] });
      queryClient.invalidateQueries({ queryKey: ['ab-tests'] });
    },
  });
}

export function useStartABTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (testId: string) =>
      apiRequest(`/optimization/ab-tests/${testId}/start/`, {
        method: 'POST',
      }),
    onSuccess: (_, testId) => {
      queryClient.invalidateQueries({ queryKey: ['ab-test', testId] });
    },
  });
}

export function useStopABTest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (testId: string) =>
      apiRequest(`/optimization/ab-tests/${testId}/stop/`, {
        method: 'POST',
      }),
    onSuccess: (_, testId) => {
      queryClient.invalidateQueries({ queryKey: ['ab-test', testId] });
    },
  });
}

// Hooks for Performance Analysis
export function usePerformanceAnalyses(designId?: string) {
  return useQuery({
    queryKey: ['performance-analyses', designId],
    queryFn: () =>
      apiRequest<PerformanceAnalysis[]>(
        `/optimization/performance/${designId ? `?design=${designId}` : ''}`
      ),
    enabled: !!designId,
  });
}

export function usePerformanceAnalysis(analysisId: string) {
  return useQuery({
    queryKey: ['performance-analysis', analysisId],
    queryFn: () =>
      apiRequest<PerformanceAnalysis>(`/optimization/performance/${analysisId}/`),
    enabled: !!analysisId,
  });
}

export function useCreatePerformanceAnalysis() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (designId: string) =>
      apiRequest<PerformanceAnalysis>('/optimization/performance/', {
        method: 'POST',
        body: JSON.stringify({ design: designId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['performance-analyses'] });
    },
  });
}

// Hooks for Device Compatibility
export function useDeviceCompatibility(designId?: string) {
  return useQuery({
    queryKey: ['device-compatibility', designId],
    queryFn: () =>
      apiRequest<DeviceCompatibility[]>(
        `/optimization/device-compatibility/${designId ? `?design=${designId}` : ''}`
      ),
    enabled: !!designId,
  });
}

export function useTestDeviceCompatibility() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { design: string; devices: string[] }) =>
      apiRequest<DeviceCompatibility[]>('/optimization/device-compatibility/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['device-compatibility'] });
    },
  });
}

// Hooks for Smart Layout Suggestions
export function useSmartLayoutSuggestions(designId?: string) {
  return useQuery({
    queryKey: ['layout-suggestions', designId],
    queryFn: () =>
      apiRequest<SmartLayoutSuggestion[]>(
        `/optimization/layout-suggestions/${designId ? `?design=${designId}` : ''}`
      ),
    enabled: !!designId,
  });
}

export function useGenerateLayoutSuggestions() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (designId: string) =>
      apiRequest<SmartLayoutSuggestion[]>('/optimization/layout-suggestions/', {
        method: 'POST',
        body: JSON.stringify({ design: designId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layout-suggestions'] });
    },
  });
}

export function useApplyLayoutSuggestion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (suggestionId: string) =>
      apiRequest(`/optimization/layout-suggestions/${suggestionId}/apply/`, {
        method: 'POST',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layout-suggestions'] });
    },
  });
}

// Hooks for Optimization Reports
export function useOptimizationReports(projectId?: string) {
  return useQuery({
    queryKey: ['optimization-reports', projectId],
    queryFn: () =>
      apiRequest<OptimizationReport[]>(
        `/optimization/reports/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useOptimizationReport(reportId: string) {
  return useQuery({
    queryKey: ['optimization-report', reportId],
    queryFn: () =>
      apiRequest<OptimizationReport>(`/optimization/reports/${reportId}/`),
    enabled: !!reportId,
  });
}

export function useGenerateOptimizationReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: {
      project: string;
      report_type: string;
    }) =>
      apiRequest<OptimizationReport>('/optimization/reports/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['optimization-reports'] });
    },
  });
}

// Hooks for Design Analysis
export function useAnalyzeDesign() {
  return useMutation({
    mutationFn: async (designData: {
      layers: unknown[];
      canvas_data: Record<string, unknown>;
    }) =>
      apiRequest<DesignAnalysis>('/optimization/analyze/', {
        method: 'POST',
        body: JSON.stringify(designData),
      }),
  });
}

// Hooks for Behavior Prediction
export function usePredictBehavior() {
  return useMutation({
    mutationFn: async (designData: {
      layers: unknown[];
      canvas_data: Record<string, unknown>;
      target_audience?: string;
    }) =>
      apiRequest<BehaviorPrediction>('/optimization/predict-behavior/', {
        method: 'POST',
        body: JSON.stringify(designData),
      }),
  });
}

// Export Report
export function useExportOptimizationReport() {
  return useMutation({
    mutationFn: async ({
      reportId,
      format,
    }: {
      reportId: string;
      format: 'pdf' | 'xlsx' | 'json';
    }) => {
      const response = await fetch(
        `${API_BASE}/optimization/reports/${reportId}/export/?format=${format}`,
        {
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to export report');
      }

      return response.blob();
    },
  });
}

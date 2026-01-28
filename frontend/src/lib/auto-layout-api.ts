/**
 * Auto Layout API Client
 * Production-ready API for the Auto-Layout System feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/auto-layout`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export interface AutoLayoutFrame {
  id: string;
  project: number;
  node_id: string;
  name: string;
  layout_mode: 'horizontal' | 'vertical' | 'none';
  primary_axis_sizing: 'fixed' | 'hug' | 'fill';
  counter_axis_sizing: 'fixed' | 'hug' | 'fill';
  primary_axis_align: 'min' | 'center' | 'max' | 'space_between';
  counter_axis_align: 'min' | 'center' | 'max' | 'baseline';
  padding_top: number;
  padding_right: number;
  padding_bottom: number;
  padding_left: number;
  item_spacing: number;
  wrap: boolean;
  wrap_spacing: number;
  stroke_included: boolean;
  absolute_children: boolean;
  min_width: number | null;
  max_width: number | null;
  min_height: number | null;
  max_height: number | null;
  created_at: string;
  updated_at: string;
}

export interface AutoLayoutChild {
  id: string;
  parent_frame: string;
  node_id: string;
  order_index: number;
  layout_align: 'inherit' | 'stretch' | 'min' | 'center' | 'max';
  layout_grow: number;
  layout_sizing_horizontal: 'fixed' | 'hug' | 'fill';
  layout_sizing_vertical: 'fixed' | 'hug' | 'fill';
  layout_position: 'auto' | 'absolute';
  absolute_x: number | null;
  absolute_y: number | null;
}

export interface LayoutConstraint {
  id: string;
  node_id: string;
  project: number;
  horizontal_constraint: 'left' | 'right' | 'left_right' | 'center' | 'scale';
  vertical_constraint: 'top' | 'bottom' | 'top_bottom' | 'center' | 'scale';
  parent_reference_point: 'top_left' | 'top_center' | 'top_right' | 'center_left' | 'center' | 'center_right' | 'bottom_left' | 'bottom_center' | 'bottom_right';
  offset_x: number;
  offset_y: number;
  fixed_width: boolean;
  fixed_height: boolean;
}

export interface LayoutPreset {
  id: string;
  name: string;
  slug: string;
  description: string;
  category: string;
  layout_config: Record<string, unknown>;
  preview_image: string | null;
  is_system: boolean;
  is_public: boolean;
  usage_count: number;
  tags: string[];
}

export interface ResponsiveBreakpoint {
  id: string;
  project: number;
  name: string;
  min_width: number | null;
  max_width: number | null;
  order: number;
  is_default: boolean;
  icon: string;
  description: string;
}

export interface ResponsiveOverride {
  id: string;
  breakpoint: string;
  frame: string;
  layout_mode: 'horizontal' | 'vertical' | 'none' | null;
  item_spacing: number | null;
  padding_override: Record<string, number> | null;
  visibility: 'visible' | 'hidden' | 'inherit';
  width_override: number | null;
  height_override: number | null;
}

export interface AISuggestion {
  id: string;
  name: string;
  description: string;
  confidence: number;
  layout_config: Record<string, unknown>;
  changes: unknown[];
  preview_url?: string;
}

export interface LayoutAnalysis {
  consistency_score: number;
  spacing_issues: Array<{
    node_id: string;
    issue: string;
    suggestion: string;
  }>;
  alignment_issues: Array<{
    node_id: string;
    issue: string;
    suggestion: string;
  }>;
  accessibility_notes: string[];
  optimization_suggestions: string[];
}

// API Functions
export const autoLayoutApi = {
  // Frame operations
  async getFrames(projectId: number): Promise<AutoLayoutFrame[]> {
    const { data } = await apiClient.get(`/frames/?project=${projectId}`);
    return data.results || data;
  },

  async getFrame(frameId: string): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.get(`/frames/${frameId}/`);
    return data;
  },

  async createFrame(frame: Partial<AutoLayoutFrame>): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.post('/frames/', frame);
    return data;
  },

  async updateFrame(frameId: string, updates: Partial<AutoLayoutFrame>): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.patch(`/frames/${frameId}/`, updates);
    return data;
  },

  async deleteFrame(frameId: string): Promise<void> {
    await apiClient.delete(`/frames/${frameId}/`);
  },

  async toggleLayoutMode(frameId: string): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.post(`/frames/${frameId}/toggle_layout/`);
    return data;
  },

  async applyPresetToFrame(frameId: string, presetId: string): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.post(`/frames/${frameId}/apply_preset/`, { preset_id: presetId });
    return data;
  },

  async cloneFrame(frameId: string, name?: string): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.post(`/frames/${frameId}/clone/`, { name });
    return data;
  },

  async getFrameChildrenInfo(frameId: string): Promise<{ children: AutoLayoutChild[]; stats: Record<string, unknown> }> {
    const { data } = await apiClient.get(`/frames/${frameId}/children_info/`);
    return data;
  },

  // Child operations
  async getChildren(frameId: string): Promise<AutoLayoutChild[]> {
    const { data } = await apiClient.get(`/children/?parent_frame=${frameId}`);
    return data.results || data;
  },

  async updateChild(childId: string, updates: Partial<AutoLayoutChild>): Promise<AutoLayoutChild> {
    const { data } = await apiClient.patch(`/children/${childId}/`, updates);
    return data;
  },

  async reorderChildren(frameId: string, childIds: string[]): Promise<void> {
    await apiClient.post(`/children/reorder/`, {
      parent_frame: frameId,
      child_ids: childIds,
    });
  },

  // Constraint operations
  async getConstraints(projectId: number): Promise<LayoutConstraint[]> {
    const { data } = await apiClient.get(`/constraints/?project=${projectId}`);
    return data.results || data;
  },

  async updateConstraints(constraintId: string, updates: Partial<LayoutConstraint>): Promise<LayoutConstraint> {
    const { data } = await apiClient.patch(`/constraints/${constraintId}/`, updates);
    return data;
  },

  async resetConstraints(constraintId: string): Promise<LayoutConstraint> {
    const { data } = await apiClient.post(`/constraints/${constraintId}/reset/`);
    return data;
  },

  // Preset operations
  async getPresets(category?: string): Promise<LayoutPreset[]> {
    const params = category ? `?category=${category}` : '';
    const { data } = await apiClient.get(`/presets/${params}`);
    return data.results || data;
  },

  async getPreset(presetId: string): Promise<LayoutPreset> {
    const { data } = await apiClient.get(`/presets/${presetId}/`);
    return data;
  },

  async createPreset(preset: Partial<LayoutPreset>): Promise<LayoutPreset> {
    const { data } = await apiClient.post('/presets/', preset);
    return data;
  },

  async duplicatePreset(presetId: string): Promise<LayoutPreset> {
    const { data } = await apiClient.post(`/presets/${presetId}/duplicate/`);
    return data;
  },

  async getPopularPresets(): Promise<LayoutPreset[]> {
    const { data } = await apiClient.get('/presets/popular/');
    return data;
  },

  // Responsive breakpoint operations
  async getBreakpoints(projectId: number): Promise<ResponsiveBreakpoint[]> {
    const { data } = await apiClient.get(`/breakpoints/?project=${projectId}`);
    return data.results || data;
  },

  async createBreakpoint(breakpoint: Partial<ResponsiveBreakpoint>): Promise<ResponsiveBreakpoint> {
    const { data } = await apiClient.post('/breakpoints/', breakpoint);
    return data;
  },

  async updateBreakpoint(breakpointId: string, updates: Partial<ResponsiveBreakpoint>): Promise<ResponsiveBreakpoint> {
    const { data } = await apiClient.patch(`/breakpoints/${breakpointId}/`, updates);
    return data;
  },

  async deleteBreakpoint(breakpointId: string): Promise<void> {
    await apiClient.delete(`/breakpoints/${breakpointId}/`);
  },

  async setDefaultBreakpoint(breakpointId: string): Promise<ResponsiveBreakpoint> {
    const { data } = await apiClient.post(`/breakpoints/${breakpointId}/set_default/`);
    return data;
  },

  async reorderBreakpoints(projectId: number, breakpointIds: string[]): Promise<void> {
    await apiClient.post('/breakpoints/reorder/', {
      project: projectId,
      breakpoint_ids: breakpointIds,
    });
  },

  // Responsive override operations
  async getOverrides(breakpointId: string): Promise<ResponsiveOverride[]> {
    const { data } = await apiClient.get(`/overrides/?breakpoint=${breakpointId}`);
    return data.results || data;
  },

  async updateOverride(overrideId: string, updates: Partial<ResponsiveOverride>): Promise<ResponsiveOverride> {
    const { data } = await apiClient.patch(`/overrides/${overrideId}/`, updates);
    return data;
  },

  async clearOverride(overrideId: string): Promise<void> {
    await apiClient.post(`/overrides/${overrideId}/clear/`);
  },

  async copyOverridesToBreakpoint(sourceBreakpointId: string, targetBreakpointId: string): Promise<void> {
    await apiClient.post('/overrides/copy_to_breakpoint/', {
      source_breakpoint: sourceBreakpointId,
      target_breakpoint: targetBreakpointId,
    });
  },

  // AI-powered operations
  async getAISuggestions(projectId: number, nodeIds: string[]): Promise<AISuggestion[]> {
    const { data } = await apiClient.post('/ai/suggest/', {
      project_id: projectId,
      node_ids: nodeIds,
    });
    return data.suggestions || [];
  },

  async applySuggestion(suggestionId: string, nodeIds: string[]): Promise<{ applied: boolean; changes: unknown[] }> {
    const { data } = await apiClient.post('/ai/apply-suggestion/', {
      suggestion_id: suggestionId,
      node_ids: nodeIds,
    });
    return data;
  },

  async analyzeLayout(projectId: number, frameId?: string): Promise<LayoutAnalysis> {
    const { data } = await apiClient.post('/ai/analyze/', {
      project_id: projectId,
      frame_id: frameId,
    });
    return data;
  },

  async autoArrange(projectId: number, nodeIds: string[], options?: {
    spacing?: number;
    alignment?: string;
    direction?: 'horizontal' | 'vertical';
  }): Promise<{ arranged_count: number; layout: unknown }> {
    const { data } = await apiClient.post('/ai/auto-arrange/', {
      project_id: projectId,
      node_ids: nodeIds,
      ...options,
    });
    return data;
  },

  async alignToGrid(projectId: number, nodeIds: string[], gridSize: number): Promise<{ aligned_count: number }> {
    const { data } = await apiClient.post('/ai/align-to-grid/', {
      project_id: projectId,
      node_ids: nodeIds,
      grid_size: gridSize,
    });
    return data;
  },

  async smartResize(frameId: string, targetWidth: number, targetHeight: number, maintainProportions: boolean): Promise<AutoLayoutFrame> {
    const { data } = await apiClient.post(`/frames/${frameId}/smart_resize/`, {
      width: targetWidth,
      height: targetHeight,
      maintain_proportions: maintainProportions,
    });
    return data;
  },
};

export default autoLayoutApi;

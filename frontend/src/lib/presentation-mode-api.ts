/**
 * Presentation & Dev Mode API Client
 * Production-ready API for Presentation Mode and Dev Mode features
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/presentation`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type TransitionType = 'none' | 'fade' | 'slide_left' | 'slide_right' | 'slide_up' | 'slide_down' | 
                              'zoom_in' | 'zoom_out' | 'flip' | 'dissolve' | 'custom';
export type ExportFormat = 'css' | 'scss' | 'tailwind' | 'styled_components' | 'emotion' | 'swift' | 
                           'kotlin' | 'flutter' | 'react_native' | 'xml';

export interface PresentationSlide {
  id: string;
  presentation: string;
  name: string;
  node_id: string;
  order: number;
  duration: number | null;
  transition: TransitionType;
  transition_duration: number;
  notes: string;
  is_hidden: boolean;
  thumbnail_url: string | null;
  annotations: SlideAnnotation[];
  created_at: string;
  updated_at: string;
}

export interface SlideAnnotation {
  id: string;
  slide: string;
  content: string;
  position_x: number;
  position_y: number;
  annotation_type: 'text' | 'arrow' | 'highlight' | 'spotlight';
  style: Record<string, unknown>;
  is_visible: boolean;
  created_by: number;
  created_at: string;
}

export interface Presentation {
  id: string;
  project: number;
  name: string;
  description: string;
  slides: PresentationSlide[];
  theme: Record<string, unknown>;
  settings: {
    auto_advance: boolean;
    default_duration: number;
    show_slide_numbers: boolean;
    show_progress_bar: boolean;
    allow_navigation: boolean;
    loop: boolean;
  };
  is_public: boolean;
  share_link: string | null;
  password_protected: boolean;
  view_count: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface PresentationViewer {
  id: string;
  presentation: string;
  viewer_type: 'authenticated' | 'anonymous' | 'invited';
  user: number | null;
  email: string;
  session_id: string;
  current_slide: number;
  last_viewed_at: string;
  total_view_time: number;
  interactions: Array<{
    type: string;
    slide: number;
    timestamp: string;
  }>;
}

export interface DevModeProject {
  id: string;
  project: number;
  settings: {
    show_grid: boolean;
    show_guides: boolean;
    show_rulers: boolean;
    measurement_unit: 'px' | 'rem' | 'em' | 'pt' | '%';
    color_format: 'hex' | 'rgb' | 'hsl' | 'hsb';
    show_spacing: boolean;
    show_properties: boolean;
    code_syntax: ExportFormat;
  };
  selected_nodes: string[];
  pinned_nodes: string[];
  bookmarks: Array<{
    id: string;
    name: string;
    node_id: string;
    position: { x: number; y: number; zoom: number };
  }>;
  created_at: string;
  updated_at: string;
}

export interface DevModeInspection {
  id: string;
  dev_mode_project: string;
  node_id: string;
  properties: Record<string, unknown>;
  styles: Record<string, unknown>;
  spacing: {
    padding: { top: number; right: number; bottom: number; left: number };
    margin: { top: number; right: number; bottom: number; left: number };
  };
  constraints: Record<string, unknown>;
  auto_layout: Record<string, unknown> | null;
  effects: Array<Record<string, unknown>>;
  created_at: string;
}

export interface MeasurementOverlay {
  id: string;
  dev_mode_project: string;
  source_node: string;
  target_node: string | null;
  measurement_type: 'distance' | 'spacing' | 'size' | 'custom';
  value: number;
  unit: string;
  direction: 'horizontal' | 'vertical' | 'diagonal';
  is_pinned: boolean;
  label: string;
  created_at: string;
}

export interface CodeExportConfig {
  id: string;
  project: number;
  name: string;
  format: ExportFormat;
  options: {
    include_comments: boolean;
    use_variables: boolean;
    class_naming: 'bem' | 'camelCase' | 'kebab-case' | 'snake_case';
    include_responsive: boolean;
    breakpoints: Array<{ name: string; width: number }>;
    custom_properties: boolean;
    minify: boolean;
  };
  template: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface CodeExportHistory {
  id: string;
  config: string;
  node_ids: string[];
  generated_code: string;
  file_name: string;
  file_size: number;
  download_url: string | null;
  created_at: string;
}

export interface AssetExportQueue {
  id: string;
  project: number;
  node_id: string;
  node_name: string;
  format: 'png' | 'jpg' | 'svg' | 'pdf' | 'webp';
  scale: number;
  suffix: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_url: string | null;
  file_size: number | null;
  error_message: string;
  created_at: string;
  completed_at: string | null;
}

export interface NodeSpecs {
  node_id: string;
  name: string;
  type: string;
  position: { x: number; y: number };
  size: { width: number; height: number };
  rotation: number;
  opacity: number;
  styles: {
    fills: Array<{
      type: string;
      color?: string;
      gradient?: Record<string, unknown>;
      image_url?: string;
    }>;
    strokes: Array<{
      color: string;
      weight: number;
      type: string;
    }>;
    effects: Array<{
      type: string;
      visible: boolean;
      params: Record<string, unknown>;
    }>;
  };
  typography?: {
    font_family: string;
    font_weight: number;
    font_size: number;
    line_height: number | string;
    letter_spacing: number;
    text_align: string;
    text_decoration: string;
    text_transform: string;
  };
  auto_layout?: {
    mode: string;
    spacing: number;
    padding: Record<string, number>;
    alignment: string;
  };
  constraints?: {
    horizontal: string;
    vertical: string;
  };
  code_snippets: Record<ExportFormat, string>;
}

// API Functions
export const presentationModeApi = {
  // Presentation operations
  async getPresentations(projectId: number): Promise<Presentation[]> {
    const { data } = await apiClient.get(`/presentations/?project=${projectId}`);
    return data.results || data;
  },

  async getPresentation(presentationId: string): Promise<Presentation> {
    const { data } = await apiClient.get(`/presentations/${presentationId}/`);
    return data;
  },

  async createPresentation(presentation: Partial<Presentation>): Promise<Presentation> {
    const { data } = await apiClient.post('/presentations/', presentation);
    return data;
  },

  async updatePresentation(presentationId: string, updates: Partial<Presentation>): Promise<Presentation> {
    const { data } = await apiClient.patch(`/presentations/${presentationId}/`, updates);
    return data;
  },

  async deletePresentation(presentationId: string): Promise<void> {
    await apiClient.delete(`/presentations/${presentationId}/`);
  },

  async duplicatePresentation(presentationId: string, name?: string): Promise<Presentation> {
    const { data } = await apiClient.post(`/presentations/${presentationId}/duplicate/`, { name });
    return data;
  },

  async startPresentation(presentationId: string): Promise<{
    session_id: string;
    presenter_url: string;
    viewer_url: string;
  }> {
    const { data } = await apiClient.post(`/presentations/${presentationId}/start/`);
    return data;
  },

  async endPresentation(presentationId: string): Promise<void> {
    await apiClient.post(`/presentations/${presentationId}/end/`);
  },

  async generateShareLink(presentationId: string, options?: {
    password?: string;
    expires_in?: number;
  }): Promise<{ share_link: string }> {
    const { data } = await apiClient.post(`/presentations/${presentationId}/share/`, options);
    return data;
  },

  async revokeShareLink(presentationId: string): Promise<void> {
    await apiClient.post(`/presentations/${presentationId}/revoke_share/`);
  },

  async getViewerAnalytics(presentationId: string): Promise<{
    total_views: number;
    unique_viewers: number;
    avg_view_time: number;
    completion_rate: number;
    slide_analytics: Array<{
      slide_id: string;
      views: number;
      avg_time: number;
    }>;
  }> {
    const { data } = await apiClient.get(`/presentations/${presentationId}/analytics/`);
    return data;
  },

  // Slide operations
  async getSlides(presentationId: string): Promise<PresentationSlide[]> {
    const { data } = await apiClient.get(`/slides/?presentation=${presentationId}`);
    return data.results || data;
  },

  async getSlide(slideId: string): Promise<PresentationSlide> {
    const { data } = await apiClient.get(`/slides/${slideId}/`);
    return data;
  },

  async createSlide(slide: Partial<PresentationSlide>): Promise<PresentationSlide> {
    const { data } = await apiClient.post('/slides/', slide);
    return data;
  },

  async updateSlide(slideId: string, updates: Partial<PresentationSlide>): Promise<PresentationSlide> {
    const { data } = await apiClient.patch(`/slides/${slideId}/`, updates);
    return data;
  },

  async deleteSlide(slideId: string): Promise<void> {
    await apiClient.delete(`/slides/${slideId}/`);
  },

  async reorderSlides(presentationId: string, slideIds: string[]): Promise<void> {
    await apiClient.post('/slides/reorder/', {
      presentation: presentationId,
      slide_ids: slideIds,
    });
  },

  async generateThumbnails(presentationId: string): Promise<void> {
    await apiClient.post(`/presentations/${presentationId}/generate_thumbnails/`);
  },

  async toggleSlideVisibility(slideId: string): Promise<PresentationSlide> {
    const { data } = await apiClient.post(`/slides/${slideId}/toggle_visibility/`);
    return data;
  },

  // Slide Annotation operations
  async getAnnotations(slideId: string): Promise<SlideAnnotation[]> {
    const { data } = await apiClient.get(`/annotations/?slide=${slideId}`);
    return data.results || data;
  },

  async createAnnotation(annotation: Partial<SlideAnnotation>): Promise<SlideAnnotation> {
    const { data } = await apiClient.post('/annotations/', annotation);
    return data;
  },

  async updateAnnotation(annotationId: string, updates: Partial<SlideAnnotation>): Promise<SlideAnnotation> {
    const { data } = await apiClient.patch(`/annotations/${annotationId}/`, updates);
    return data;
  },

  async deleteAnnotation(annotationId: string): Promise<void> {
    await apiClient.delete(`/annotations/${annotationId}/`);
  },

  // Viewer operations
  async getViewers(presentationId: string): Promise<PresentationViewer[]> {
    const { data } = await apiClient.get(`/viewers/?presentation=${presentationId}`);
    return data.results || data;
  },

  async trackViewerActivity(viewerId: string, activity: {
    type: 'slide_view' | 'click' | 'scroll' | 'pause' | 'resume';
    slide?: number;
  }): Promise<void> {
    await apiClient.post(`/viewers/${viewerId}/track/`, activity);
  },

  // Dev Mode Project operations
  async getDevModeProject(projectId: number): Promise<DevModeProject> {
    const { data } = await apiClient.get(`/dev-mode/${projectId}/`);
    return data;
  },

  async updateDevModeSettings(projectId: number, settings: Partial<DevModeProject['settings']>): Promise<DevModeProject> {
    const { data } = await apiClient.patch(`/dev-mode/${projectId}/`, { settings });
    return data;
  },

  async selectNodes(projectId: number, nodeIds: string[]): Promise<DevModeProject> {
    const { data } = await apiClient.post(`/dev-mode/${projectId}/select/`, { node_ids: nodeIds });
    return data;
  },

  async pinNode(projectId: number, nodeId: string): Promise<DevModeProject> {
    const { data } = await apiClient.post(`/dev-mode/${projectId}/pin/`, { node_id: nodeId });
    return data;
  },

  async unpinNode(projectId: number, nodeId: string): Promise<DevModeProject> {
    const { data } = await apiClient.post(`/dev-mode/${projectId}/unpin/`, { node_id: nodeId });
    return data;
  },

  async addBookmark(projectId: number, bookmark: {
    name: string;
    node_id: string;
    position: { x: number; y: number; zoom: number };
  }): Promise<DevModeProject> {
    const { data } = await apiClient.post(`/dev-mode/${projectId}/bookmark/`, bookmark);
    return data;
  },

  async removeBookmark(projectId: number, bookmarkId: string): Promise<DevModeProject> {
    const { data } = await apiClient.delete(`/dev-mode/${projectId}/bookmark/${bookmarkId}/`);
    return data;
  },

  // Inspection operations
  async inspectNode(projectId: number, nodeId: string): Promise<DevModeInspection> {
    const { data } = await apiClient.get(`/inspections/?project=${projectId}&node_id=${nodeId}`);
    return data;
  },

  async getNodeSpecs(projectId: number, nodeId: string, format?: ExportFormat): Promise<NodeSpecs> {
    const params = format ? `?format=${format}` : '';
    const { data } = await apiClient.get(`/inspections/specs/${projectId}/${nodeId}/${params}`);
    return data;
  },

  async copySpecs(projectId: number, nodeId: string, what: 'css' | 'properties' | 'colors' | 'typography'): Promise<{
    copied: string;
    format: string;
  }> {
    const { data } = await apiClient.post(`/inspections/copy/`, {
      project_id: projectId,
      node_id: nodeId,
      what,
    });
    return data;
  },

  // Measurement operations
  async getMeasurements(projectId: number): Promise<MeasurementOverlay[]> {
    const { data } = await apiClient.get(`/measurements/?project=${projectId}`);
    return data.results || data;
  },

  async createMeasurement(measurement: Partial<MeasurementOverlay>): Promise<MeasurementOverlay> {
    const { data } = await apiClient.post('/measurements/', measurement);
    return data;
  },

  async deleteMeasurement(measurementId: string): Promise<void> {
    await apiClient.delete(`/measurements/${measurementId}/`);
  },

  async toggleMeasurementPin(measurementId: string): Promise<MeasurementOverlay> {
    const { data } = await apiClient.post(`/measurements/${measurementId}/toggle_pin/`);
    return data;
  },

  async measureBetweenNodes(projectId: number, sourceNodeId: string, targetNodeId: string): Promise<{
    horizontal_distance: number;
    vertical_distance: number;
    diagonal_distance: number;
    spacing: {
      horizontal: number;
      vertical: number;
    };
  }> {
    const { data } = await apiClient.post('/measurements/between/', {
      project_id: projectId,
      source_node: sourceNodeId,
      target_node: targetNodeId,
    });
    return data;
  },

  // Code Export Config operations
  async getCodeExportConfigs(projectId: number): Promise<CodeExportConfig[]> {
    const { data } = await apiClient.get(`/export-configs/?project=${projectId}`);
    return data.results || data;
  },

  async createCodeExportConfig(config: Partial<CodeExportConfig>): Promise<CodeExportConfig> {
    const { data } = await apiClient.post('/export-configs/', config);
    return data;
  },

  async updateCodeExportConfig(configId: string, updates: Partial<CodeExportConfig>): Promise<CodeExportConfig> {
    const { data } = await apiClient.patch(`/export-configs/${configId}/`, updates);
    return data;
  },

  async deleteCodeExportConfig(configId: string): Promise<void> {
    await apiClient.delete(`/export-configs/${configId}/`);
  },

  async setDefaultConfig(configId: string): Promise<CodeExportConfig> {
    const { data } = await apiClient.post(`/export-configs/${configId}/set_default/`);
    return data;
  },

  // Code Export operations
  async exportCode(configId: string, nodeIds: string[]): Promise<CodeExportHistory> {
    const { data } = await apiClient.post('/export-history/', {
      config: configId,
      node_ids: nodeIds,
    });
    return data;
  },

  async getExportHistory(configId: string): Promise<CodeExportHistory[]> {
    const { data } = await apiClient.get(`/export-history/?config=${configId}`);
    return data.results || data;
  },

  async previewExport(configId: string, nodeId: string): Promise<{
    code: string;
    language: string;
  }> {
    const { data } = await apiClient.post('/export-history/preview/', {
      config: configId,
      node_id: nodeId,
    });
    return data;
  },

  // Asset Export operations
  async getAssetExportQueue(projectId: number): Promise<AssetExportQueue[]> {
    const { data } = await apiClient.get(`/asset-queue/?project=${projectId}`);
    return data.results || data;
  },

  async queueAssetExport(asset: {
    project: number;
    node_id: string;
    format: AssetExportQueue['format'];
    scale?: number;
    suffix?: string;
  }): Promise<AssetExportQueue> {
    const { data } = await apiClient.post('/asset-queue/', asset);
    return data;
  },

  async bulkQueueAssets(projectId: number, assets: Array<{
    node_id: string;
    formats: Array<AssetExportQueue['format']>;
    scales?: number[];
  }>): Promise<AssetExportQueue[]> {
    const { data } = await apiClient.post('/asset-queue/bulk/', {
      project: projectId,
      assets,
    });
    return data;
  },

  async cancelAssetExport(queueId: string): Promise<void> {
    await apiClient.delete(`/asset-queue/${queueId}/`);
  },

  async downloadAsset(queueId: string): Promise<Blob> {
    const { data } = await apiClient.get(`/asset-queue/${queueId}/download/`, {
      responseType: 'blob',
    });
    return data;
  },

  async downloadAllAssets(projectId: number): Promise<Blob> {
    const { data } = await apiClient.get(`/asset-queue/download_all/?project=${projectId}`, {
      responseType: 'blob',
    });
    return data;
  },

  // Utility functions
  async getRedlines(projectId: number, nodeId: string): Promise<{
    node_id: string;
    measurements: Array<{
      type: string;
      value: number;
      label: string;
      position: { x: number; y: number };
    }>;
    spacing_guides: Array<{
      from: string;
      to: string;
      value: number;
      direction: string;
    }>;
  }> {
    const { data } = await apiClient.get(`/redlines/${projectId}/${nodeId}/`);
    return data;
  },

  async compareVersions(projectId: number, nodeId: string, version1: string, version2: string): Promise<{
    changes: Array<{
      property: string;
      before: unknown;
      after: unknown;
    }>;
    visual_diff_url: string;
  }> {
    const { data } = await apiClient.post('/compare/', {
      project_id: projectId,
      node_id: nodeId,
      version_1: version1,
      version_2: version2,
    });
    return data;
  },
};

export default presentationModeApi;

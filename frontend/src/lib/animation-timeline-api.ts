/**
 * Animation Timeline API Client
 * Production-ready API for Advanced Animation Timeline feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/timeline`,
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
export type AnimationType = 'tween' | 'spring' | 'physics' | 'path' | 'sequence' | 'stagger';
export type EffectType = 'fade' | 'scale' | 'rotate' | 'translate' | 'skew' | 'blur' | 'color' | 'opacity' | 'custom';
export type TriggerType = 'click' | 'hover' | 'scroll' | 'load' | 'custom' | 'time' | 'intersection';

export interface AnimationKeyframe {
  id: string;
  track: string;
  time: number;
  value: number | string | Record<string, unknown>;
  easing: string;
  easing_params: Record<string, number>;
  interpolation: 'linear' | 'bezier' | 'step' | 'spring';
  control_points: number[];
  label: string;
  is_hold: boolean;
  created_at: string;
  updated_at: string;
}

export interface AnimationTrack {
  id: string;
  layer: string;
  property: string;
  property_path: string;
  keyframes: AnimationKeyframe[];
  is_locked: boolean;
  is_muted: boolean;
  color: string;
  expression: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface AnimationLayer {
  id: string;
  composition: string;
  name: string;
  node_id: string;
  node_type: string;
  tracks: AnimationTrack[];
  parent_layer: string | null;
  is_visible: boolean;
  is_locked: boolean;
  is_solo: boolean;
  blend_mode: string;
  opacity: number;
  start_time: number;
  end_time: number;
  in_point: number;
  out_point: number;
  time_remap: number[];
  motion_blur: boolean;
  is_collapsed: boolean;
  color_label: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface AnimationComposition {
  id: string;
  project: string;
  name: string;
  description: string;
  width: number;
  height: number;
  frame_rate: number;
  duration: number;
  background_color: string;
  layers: AnimationLayer[];
  is_template: boolean;
  preview_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnimationProject {
  id: string;
  project: number;
  name: string;
  description: string;
  compositions: AnimationComposition[];
  global_presets: Record<string, unknown>;
  color_palette: string[];
  audio_tracks: Array<{
    id: string;
    name: string;
    url: string;
    start_time: number;
    volume: number;
  }>;
  markers: Array<{
    time: number;
    label: string;
    color: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface AnimationEffect {
  id: string;
  layer: string;
  effect_type: EffectType;
  name: string;
  is_enabled: boolean;
  parameters: Record<string, unknown>;
  keyframeable_params: string[];
  order: number;
  preset_name: string;
}

export interface AnimationSequence {
  id: string;
  composition: string;
  name: string;
  description: string;
  trigger: TriggerType;
  trigger_config: Record<string, unknown>;
  animations: Array<{
    layer_id: string;
    start_time: number;
    duration: number;
    animation_type: AnimationType;
  }>;
  loop: boolean;
  loop_count: number;
  delay: number;
  reverse_on_complete: boolean;
  order: number;
  is_enabled: boolean;
}

export interface EasingPreset {
  id: string;
  name: string;
  category: string;
  easing_function: string;
  bezier_points: number[];
  spring_config: {
    stiffness: number;
    damping: number;
    mass: number;
  } | null;
  is_system: boolean;
  preview_svg: string;
  usage_count: number;
}

export interface LottieExport {
  id: string;
  composition: string;
  file_name: string;
  file_url: string;
  file_size: number;
  export_settings: {
    optimize: boolean;
    include_hidden: boolean;
    frame_range?: [number, number];
  };
  lottie_version: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string;
  created_at: string;
}

export interface TimelinePlaybackState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  playbackRate: number;
  loop: boolean;
  frameRate: number;
}

// API Functions
export const animationTimelineApi = {
  // Animation Project operations
  async getProjects(projectId: number): Promise<AnimationProject[]> {
    const { data } = await apiClient.get(`/projects/?project=${projectId}`);
    return data.results || data;
  },

  async getProject(animationProjectId: string): Promise<AnimationProject> {
    const { data } = await apiClient.get(`/projects/${animationProjectId}/`);
    return data;
  },

  async createProject(project: Partial<AnimationProject>): Promise<AnimationProject> {
    const { data } = await apiClient.post('/projects/', project);
    return data;
  },

  async updateProject(projectId: string, updates: Partial<AnimationProject>): Promise<AnimationProject> {
    const { data } = await apiClient.patch(`/projects/${projectId}/`, updates);
    return data;
  },

  async deleteProject(projectId: string): Promise<void> {
    await apiClient.delete(`/projects/${projectId}/`);
  },

  async duplicateProject(projectId: string, name?: string): Promise<AnimationProject> {
    const { data } = await apiClient.post(`/projects/${projectId}/duplicate/`, { name });
    return data;
  },

  // Composition operations
  async getCompositions(animationProjectId: string): Promise<AnimationComposition[]> {
    const { data } = await apiClient.get(`/compositions/?animation_project=${animationProjectId}`);
    return data.results || data;
  },

  async getComposition(compositionId: string): Promise<AnimationComposition> {
    const { data } = await apiClient.get(`/compositions/${compositionId}/`);
    return data;
  },

  async createComposition(composition: Partial<AnimationComposition>): Promise<AnimationComposition> {
    const { data } = await apiClient.post('/compositions/', composition);
    return data;
  },

  async updateComposition(compositionId: string, updates: Partial<AnimationComposition>): Promise<AnimationComposition> {
    const { data } = await apiClient.patch(`/compositions/${compositionId}/`, updates);
    return data;
  },

  async deleteComposition(compositionId: string): Promise<void> {
    await apiClient.delete(`/compositions/${compositionId}/`);
  },

  async duplicateComposition(compositionId: string, name?: string): Promise<AnimationComposition> {
    const { data } = await apiClient.post(`/compositions/${compositionId}/duplicate/`, { name });
    return data;
  },

  async renderPreview(compositionId: string, options?: {
    format?: 'gif' | 'mp4' | 'webm';
    quality?: 'low' | 'medium' | 'high';
    frame_range?: [number, number];
  }): Promise<{ preview_url: string; render_id: string }> {
    const { data } = await apiClient.post(`/compositions/${compositionId}/render_preview/`, options);
    return data;
  },

  async getPlaybackState(compositionId: string): Promise<TimelinePlaybackState> {
    const { data } = await apiClient.get(`/compositions/${compositionId}/playback_state/`);
    return data;
  },

  // Layer operations
  async getLayers(compositionId: string): Promise<AnimationLayer[]> {
    const { data } = await apiClient.get(`/layers/?composition=${compositionId}`);
    return data.results || data;
  },

  async getLayer(layerId: string): Promise<AnimationLayer> {
    const { data } = await apiClient.get(`/layers/${layerId}/`);
    return data;
  },

  async createLayer(layer: Partial<AnimationLayer>): Promise<AnimationLayer> {
    const { data } = await apiClient.post('/layers/', layer);
    return data;
  },

  async updateLayer(layerId: string, updates: Partial<AnimationLayer>): Promise<AnimationLayer> {
    const { data } = await apiClient.patch(`/layers/${layerId}/`, updates);
    return data;
  },

  async deleteLayer(layerId: string): Promise<void> {
    await apiClient.delete(`/layers/${layerId}/`);
  },

  async duplicateLayer(layerId: string, name?: string): Promise<AnimationLayer> {
    const { data } = await apiClient.post(`/layers/${layerId}/duplicate/`, { name });
    return data;
  },

  async toggleVisibility(layerId: string): Promise<AnimationLayer> {
    const { data } = await apiClient.post(`/layers/${layerId}/toggle_visibility/`);
    return data;
  },

  async toggleLock(layerId: string): Promise<AnimationLayer> {
    const { data } = await apiClient.post(`/layers/${layerId}/toggle_lock/`);
    return data;
  },

  async toggleSolo(layerId: string): Promise<AnimationLayer> {
    const { data } = await apiClient.post(`/layers/${layerId}/toggle_solo/`);
    return data;
  },

  async reorderLayers(compositionId: string, layerIds: string[]): Promise<void> {
    await apiClient.post('/layers/reorder/', {
      composition: compositionId,
      layer_ids: layerIds,
    });
  },

  async trimLayer(layerId: string, inPoint: number, outPoint: number): Promise<AnimationLayer> {
    const { data } = await apiClient.post(`/layers/${layerId}/trim/`, {
      in_point: inPoint,
      out_point: outPoint,
    });
    return data;
  },

  async splitLayer(layerId: string, atTime: number): Promise<[AnimationLayer, AnimationLayer]> {
    const { data } = await apiClient.post(`/layers/${layerId}/split/`, { at_time: atTime });
    return data;
  },

  // Track operations
  async getTracks(layerId: string): Promise<AnimationTrack[]> {
    const { data } = await apiClient.get(`/tracks/?layer=${layerId}`);
    return data.results || data;
  },

  async createTrack(track: Partial<AnimationTrack>): Promise<AnimationTrack> {
    const { data } = await apiClient.post('/tracks/', track);
    return data;
  },

  async updateTrack(trackId: string, updates: Partial<AnimationTrack>): Promise<AnimationTrack> {
    const { data } = await apiClient.patch(`/tracks/${trackId}/`, updates);
    return data;
  },

  async deleteTrack(trackId: string): Promise<void> {
    await apiClient.delete(`/tracks/${trackId}/`);
  },

  async toggleMute(trackId: string): Promise<AnimationTrack> {
    const { data } = await apiClient.post(`/tracks/${trackId}/toggle_mute/`);
    return data;
  },

  async setExpression(trackId: string, expression: string): Promise<AnimationTrack> {
    const { data } = await apiClient.post(`/tracks/${trackId}/set_expression/`, { expression });
    return data;
  },

  async clearExpression(trackId: string): Promise<AnimationTrack> {
    const { data } = await apiClient.post(`/tracks/${trackId}/clear_expression/`);
    return data;
  },

  // Keyframe operations
  async getKeyframes(trackId: string): Promise<AnimationKeyframe[]> {
    const { data } = await apiClient.get(`/keyframes/?track=${trackId}`);
    return data.results || data;
  },

  async createKeyframe(keyframe: Partial<AnimationKeyframe>): Promise<AnimationKeyframe> {
    const { data } = await apiClient.post('/keyframes/', keyframe);
    return data;
  },

  async updateKeyframe(keyframeId: string, updates: Partial<AnimationKeyframe>): Promise<AnimationKeyframe> {
    const { data } = await apiClient.patch(`/keyframes/${keyframeId}/`, updates);
    return data;
  },

  async deleteKeyframe(keyframeId: string): Promise<void> {
    await apiClient.delete(`/keyframes/${keyframeId}/`);
  },

  async bulkCreateKeyframes(trackId: string, keyframes: Array<Partial<AnimationKeyframe>>): Promise<AnimationKeyframe[]> {
    const { data } = await apiClient.post('/keyframes/bulk_create/', {
      track: trackId,
      keyframes,
    });
    return data;
  },

  async bulkUpdateKeyframes(updates: Array<{ id: string; changes: Partial<AnimationKeyframe> }>): Promise<AnimationKeyframe[]> {
    const { data } = await apiClient.post('/keyframes/bulk_update/', { updates });
    return data;
  },

  async bulkDeleteKeyframes(keyframeIds: string[]): Promise<void> {
    await apiClient.post('/keyframes/bulk_delete/', { ids: keyframeIds });
  },

  async copyKeyframes(keyframeIds: string[], targetTrackId: string, timeOffset?: number): Promise<AnimationKeyframe[]> {
    const { data } = await apiClient.post('/keyframes/copy/', {
      keyframe_ids: keyframeIds,
      target_track: targetTrackId,
      time_offset: timeOffset,
    });
    return data;
  },

  async reverseKeyframes(trackId: string): Promise<AnimationKeyframe[]> {
    const { data } = await apiClient.post(`/tracks/${trackId}/reverse_keyframes/`);
    return data;
  },

  async interpolateKeyframe(keyframeId: string, time: number): Promise<{ value: unknown }> {
    const { data } = await apiClient.get(`/keyframes/${keyframeId}/interpolate/?time=${time}`);
    return data;
  },

  // Effect operations
  async getEffects(layerId: string): Promise<AnimationEffect[]> {
    const { data } = await apiClient.get(`/effects/?layer=${layerId}`);
    return data.results || data;
  },

  async createEffect(effect: Partial<AnimationEffect>): Promise<AnimationEffect> {
    const { data } = await apiClient.post('/effects/', effect);
    return data;
  },

  async updateEffect(effectId: string, updates: Partial<AnimationEffect>): Promise<AnimationEffect> {
    const { data } = await apiClient.patch(`/effects/${effectId}/`, updates);
    return data;
  },

  async deleteEffect(effectId: string): Promise<void> {
    await apiClient.delete(`/effects/${effectId}/`);
  },

  async toggleEffect(effectId: string): Promise<AnimationEffect> {
    const { data } = await apiClient.post(`/effects/${effectId}/toggle/`);
    return data;
  },

  async reorderEffects(layerId: string, effectIds: string[]): Promise<void> {
    await apiClient.post('/effects/reorder/', {
      layer: layerId,
      effect_ids: effectIds,
    });
  },

  async saveEffectAsPreset(effectId: string, name: string): Promise<{ preset_id: string }> {
    const { data } = await apiClient.post(`/effects/${effectId}/save_preset/`, { name });
    return data;
  },

  // Sequence operations
  async getSequences(compositionId: string): Promise<AnimationSequence[]> {
    const { data } = await apiClient.get(`/sequences/?composition=${compositionId}`);
    return data.results || data;
  },

  async createSequence(sequence: Partial<AnimationSequence>): Promise<AnimationSequence> {
    const { data } = await apiClient.post('/sequences/', sequence);
    return data;
  },

  async updateSequence(sequenceId: string, updates: Partial<AnimationSequence>): Promise<AnimationSequence> {
    const { data } = await apiClient.patch(`/sequences/${sequenceId}/`, updates);
    return data;
  },

  async deleteSequence(sequenceId: string): Promise<void> {
    await apiClient.delete(`/sequences/${sequenceId}/`);
  },

  async toggleSequence(sequenceId: string): Promise<AnimationSequence> {
    const { data } = await apiClient.post(`/sequences/${sequenceId}/toggle/`);
    return data;
  },

  async previewSequence(sequenceId: string): Promise<{ preview_url: string }> {
    const { data } = await apiClient.post(`/sequences/${sequenceId}/preview/`);
    return data;
  },

  // Easing preset operations
  async getEasingPresets(category?: string): Promise<EasingPreset[]> {
    const params = category ? `?category=${category}` : '';
    const { data } = await apiClient.get(`/easing-presets/${params}`);
    return data.results || data;
  },

  async createEasingPreset(preset: Partial<EasingPreset>): Promise<EasingPreset> {
    const { data } = await apiClient.post('/easing-presets/', preset);
    return data;
  },

  async deleteEasingPreset(presetId: string): Promise<void> {
    await apiClient.delete(`/easing-presets/${presetId}/`);
  },

  async visualizeEasing(bezierPoints: number[]): Promise<{ svg: string; values: number[] }> {
    const { data } = await apiClient.post('/easing-presets/visualize/', { bezier_points: bezierPoints });
    return data;
  },

  // Lottie export operations
  async getLottieExports(compositionId: string): Promise<LottieExport[]> {
    const { data } = await apiClient.get(`/lottie-exports/?composition=${compositionId}`);
    return data.results || data;
  },

  async createLottieExport(compositionId: string, options?: {
    optimize?: boolean;
    include_hidden?: boolean;
    frame_range?: [number, number];
    file_name?: string;
  }): Promise<LottieExport> {
    const { data } = await apiClient.post('/lottie-exports/', {
      composition: compositionId,
      ...options,
    });
    return data;
  },

  async getLottieExportStatus(exportId: string): Promise<LottieExport> {
    const { data } = await apiClient.get(`/lottie-exports/${exportId}/`);
    return data;
  },

  async downloadLottie(exportId: string): Promise<Blob> {
    const { data } = await apiClient.get(`/lottie-exports/${exportId}/download/`, {
      responseType: 'blob',
    });
    return data;
  },

  // Utility functions
  async importFromFigma(nodeId: string, compositionId: string): Promise<AnimationLayer[]> {
    const { data } = await apiClient.post('/import/figma/', {
      node_id: nodeId,
      composition_id: compositionId,
    });
    return data.layers;
  },

  async importFromLottie(file: File, animationProjectId: string): Promise<AnimationComposition> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('animation_project', animationProjectId);
    const { data } = await apiClient.post('/import/lottie/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async bakeExpressions(layerId: string): Promise<AnimationTrack[]> {
    const { data } = await apiClient.post(`/layers/${layerId}/bake_expressions/`);
    return data.tracks;
  },

  async getTimelineSnapshot(compositionId: string, time: number): Promise<Record<string, unknown>> {
    const { data } = await apiClient.get(`/compositions/${compositionId}/snapshot/?time=${time}`);
    return data;
  },
};

export default animationTimelineApi;

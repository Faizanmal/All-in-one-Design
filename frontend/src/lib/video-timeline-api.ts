/**
 * Video Timeline API client
 */
import apiClient from './api';

export interface TimelineSettings {
  width: number;
  height: number;
  fps: number;
  duration: number;
  background_color: string;
}

export interface TimelineClip {
  id: string;
  type: string;
  source_url: string;
  start_time: number;
  end_time: number;
  in_point: number;
  out_point: number | null;
  duration: number;
  name: string;
  volume: number;
  opacity: number;
  speed: number;
  filters: string[];
  transform: {
    x: number; y: number;
    scale_x: number; scale_y: number;
    rotation: number;
    anchor_x: number; anchor_y: number;
  };
  transition_in: TransitionInfo | null;
  transition_out: TransitionInfo | null;
  keyframes: Keyframe[];
  // Text-specific
  text?: string;
  font_family?: string;
  font_size?: number;
  color?: string;
  effect?: string;
}

export interface TransitionInfo {
  name: string;
  duration: number;
  description: string;
}

export interface Keyframe {
  id: string;
  time: number;
  property: string;
  value: unknown;
  easing: string;
}

export interface TimelineTrack {
  id: string;
  type: 'video' | 'audio' | 'text' | 'effect' | 'image';
  name: string;
  clips: TimelineClip[];
  muted: boolean;
  locked: boolean;
  visible: boolean;
  volume: number;
  opacity: number;
  order: number;
}

export interface Timeline {
  id: string;
  project_id: number;
  user_id: number;
  settings: TimelineSettings;
  tracks: TimelineTrack[];
  markers: unknown[];
  audio_tracks: unknown[];
  playhead_position: number;
}

export interface ExportPreset {
  name: string;
  width: number;
  height: number;
  fps: number;
  bitrate: string | null;
  format: string;
  codec: string | null;
}

export const videoTimelineApi = {
  createTimeline: async (projectId: number, settings?: Partial<TimelineSettings>): Promise<Timeline> => {
    const response = await apiClient.post('/v1/media/timeline/create/', {
      project_id: projectId,
      settings,
    });
    return response.data;
  },

  addTrack: async (timeline: Timeline, trackType: string, name?: string) => {
    const response = await apiClient.post('/v1/media/timeline/track/', {
      timeline, track_type: trackType, name,
    });
    return response.data;
  },

  addClip: async (track: TimelineTrack, clipData: Partial<TimelineClip>) => {
    const response = await apiClient.post('/v1/media/timeline/clip/', {
      track, clip_data: clipData,
    });
    return response.data;
  },

  splitClip: async (track: TimelineTrack, clipId: string, splitPoint: number) => {
    const response = await apiClient.post('/v1/media/timeline/clip/split/', {
      track, clip_id: clipId, split_point: splitPoint,
    });
    return response.data;
  },

  trimClip: async (clip: TimelineClip, newStart?: number, newEnd?: number) => {
    const response = await apiClient.post('/v1/media/timeline/clip/trim/', {
      clip, new_start: newStart, new_end: newEnd,
    });
    return response.data;
  },

  setTransition: async (clip: TimelineClip, position: 'in' | 'out', transitionType: string, duration?: number) => {
    const response = await apiClient.post('/v1/media/timeline/clip/transition/', {
      clip, position, transition_type: transitionType, duration,
    });
    return response.data;
  },

  addTextOverlay: async (timeline: Timeline, textData: Record<string, unknown>) => {
    const response = await apiClient.post('/v1/media/timeline/text/', {
      timeline, text_data: textData,
    });
    return response.data;
  },

  addKeyframe: async (clip: TimelineClip, time: number, property: string, value: unknown) => {
    const response = await apiClient.post('/v1/media/timeline/keyframe/', {
      clip, time, property, value,
    });
    return response.data;
  },

  validate: async (timeline: Timeline) => {
    const response = await apiClient.post('/v1/media/timeline/validate/', { timeline });
    return response.data;
  },

  getTransitions: async (): Promise<Record<string, TransitionInfo>> => {
    const response = await apiClient.get('/v1/media/timeline/transitions/');
    return response.data.transitions;
  },

  getExportPresets: async (): Promise<Record<string, ExportPreset>> => {
    const response = await apiClient.get('/v1/media/timeline/export-presets/');
    return response.data.presets;
  },

  getTextEffects: async () => {
    const response = await apiClient.get('/v1/media/timeline/text-effects/');
    return response.data.effects;
  },

  getPreviewFrames: async (timeline: Timeline, count?: number) => {
    const response = await apiClient.post('/v1/media/timeline/preview/', {
      timeline, count: count || 10,
    });
    return response.data;
  },
};

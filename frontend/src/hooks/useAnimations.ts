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
// ANIMATIONS - Animation & Motion Design
// ============================================

export interface Animation {
  id: string;
  name: string;
  project: string;
  layers: string[];
  duration: number;
  fps: number;
  easing: string;
  loop: boolean;
  auto_play: boolean;
  keyframes: Array<{
    time: number;
    property: string;
    value: unknown;
  }>;
  created_at: string;
  updated_at: string;
}

export interface LottieAnimation {
  id: string;
  name: string;
  project: string;
  lottie_json: Record<string, unknown>;
  preview_url?: string;
  file_size: number;
  frame_rate: number;
  duration: number;
  created_at: string;
  updated_at: string;
}

export interface MicroInteraction {
  id: string;
  name: string;
  trigger: 'hover' | 'click' | 'focus' | 'scroll' | 'load';
  animation_type: 'fade' | 'slide' | 'scale' | 'rotate' | 'bounce' | 'custom';
  duration: number;
  easing: string;
  delay: number;
  properties: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AnimationPreset {
  id: string;
  name: string;
  category: string;
  description: string;
  animation_data: Record<string, unknown>;
  preview_url?: string;
  is_premium: boolean;
  created_at: string;
}

export interface AnimationTimeline {
  id: string;
  name: string;
  project: string;
  tracks: Array<{
    id: string;
    name: string;
    type: string;
    keyframes: Array<{
      time: number;
      value: unknown;
      easing: string;
    }>;
  }>;
  markers: Array<{
    time: number;
    label: string;
  }>;
  total_duration: number;
  created_at: string;
  updated_at: string;
}

export interface EasingPreset {
  name: string;
  value: string;
  category: string;
  preview_curve: string;
}

// Hooks for Animations
export function useAnimations(projectId?: string) {
  return useQuery({
    queryKey: ['animations', projectId],
    queryFn: () =>
      apiRequest<Animation[]>(
        `/animations/animations/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useAnimation(animationId: string) {
  return useQuery({
    queryKey: ['animation', animationId],
    queryFn: () => apiRequest<Animation>(`/animations/animations/${animationId}/`),
    enabled: !!animationId,
  });
}

export function useCreateAnimation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Animation>) =>
      apiRequest<Animation>('/animations/animations/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animations'] });
    },
  });
}

export function useUpdateAnimation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      animationId,
      data,
    }: {
      animationId: string;
      data: Partial<Animation>;
    }) =>
      apiRequest<Animation>(`/animations/animations/${animationId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['animation', variables.animationId] });
      queryClient.invalidateQueries({ queryKey: ['animations'] });
    },
  });
}

export function useDeleteAnimation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (animationId: string) =>
      apiRequest(`/animations/animations/${animationId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animations'] });
    },
  });
}

// Hooks for Lottie Animations
export function useLottieAnimations(projectId?: string) {
  return useQuery({
    queryKey: ['lottie-animations', projectId],
    queryFn: () =>
      apiRequest<LottieAnimation[]>(
        `/animations/lottie/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useLottieAnimation(lottieId: string) {
  return useQuery({
    queryKey: ['lottie-animation', lottieId],
    queryFn: () => apiRequest<LottieAnimation>(`/animations/lottie/${lottieId}/`),
    enabled: !!lottieId,
  });
}

export function useCreateLottieAnimation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<LottieAnimation>) =>
      apiRequest<LottieAnimation>('/animations/lottie/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lottie-animations'] });
    },
  });
}

export function useExportToLottie() {
  return useMutation({
    mutationFn: async (animationId: string) =>
      apiRequest<LottieAnimation>(`/animations/animations/${animationId}/export_lottie/`, {
        method: 'POST',
      }),
  });
}

// Hooks for Micro Interactions
export function useMicroInteractions(projectId?: string) {
  return useQuery({
    queryKey: ['micro-interactions', projectId],
    queryFn: () =>
      apiRequest<MicroInteraction[]>(
        `/animations/interactions/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useMicroInteraction(interactionId: string) {
  return useQuery({
    queryKey: ['micro-interaction', interactionId],
    queryFn: () =>
      apiRequest<MicroInteraction>(`/animations/interactions/${interactionId}/`),
    enabled: !!interactionId,
  });
}

export function useCreateMicroInteraction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<MicroInteraction>) =>
      apiRequest<MicroInteraction>('/animations/interactions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['micro-interactions'] });
    },
  });
}

export function useUpdateMicroInteraction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      interactionId,
      data,
    }: {
      interactionId: string;
      data: Partial<MicroInteraction>;
    }) =>
      apiRequest<MicroInteraction>(`/animations/interactions/${interactionId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['micro-interaction', variables.interactionId],
      });
      queryClient.invalidateQueries({ queryKey: ['micro-interactions'] });
    },
  });
}

export function useDeleteMicroInteraction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (interactionId: string) =>
      apiRequest(`/animations/interactions/${interactionId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['micro-interactions'] });
    },
  });
}

// Hooks for Animation Presets
export function useAnimationPresets(category?: string) {
  return useQuery({
    queryKey: ['animation-presets', category],
    queryFn: () =>
      apiRequest<AnimationPreset[]>(
        `/animations/presets/${category ? `?category=${category}` : ''}`
      ),
  });
}

export function useApplyAnimationPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      presetId,
      layerId,
    }: {
      presetId: string;
      layerId: string;
    }) =>
      apiRequest(`/animations/presets/${presetId}/apply/`, {
        method: 'POST',
        body: JSON.stringify({ layer_id: layerId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animations'] });
    },
  });
}

// Hooks for Animation Timeline
export function useAnimationTimelines(projectId?: string) {
  return useQuery({
    queryKey: ['animation-timelines', projectId],
    queryFn: () =>
      apiRequest<AnimationTimeline[]>(
        `/animations/timelines/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function useAnimationTimeline(timelineId: string) {
  return useQuery({
    queryKey: ['animation-timeline', timelineId],
    queryFn: () =>
      apiRequest<AnimationTimeline>(`/animations/timelines/${timelineId}/`),
    enabled: !!timelineId,
  });
}

export function useCreateAnimationTimeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<AnimationTimeline>) =>
      apiRequest<AnimationTimeline>('/animations/timelines/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animation-timelines'] });
    },
  });
}

export function useUpdateAnimationTimeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      timelineId,
      data,
    }: {
      timelineId: string;
      data: Partial<AnimationTimeline>;
    }) =>
      apiRequest<AnimationTimeline>(`/animations/timelines/${timelineId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['animation-timeline', variables.timelineId],
      });
      queryClient.invalidateQueries({ queryKey: ['animation-timelines'] });
    },
  });
}

export function useDeleteAnimationTimeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (timelineId: string) =>
      apiRequest(`/animations/timelines/${timelineId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['animation-timelines'] });
    },
  });
}

// Hooks for Easing Presets
export function useEasingPresets() {
  return useQuery({
    queryKey: ['easing-presets'],
    queryFn: () => apiRequest<EasingPreset[]>('/animations/easing-presets/'),
  });
}

// Preview Animation
export function usePreviewAnimation() {
  return useMutation({
    mutationFn: async (animationId: string) => {
      const response = await fetch(
        `${API_BASE}/animations/animations/${animationId}/preview/`,
        {
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Failed to generate preview');
      }

      return response.blob();
    },
  });
}

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
// 3D STUDIO - 3D Design & Prototyping
// ============================================

export interface Model3D {
  id: string;
  name: string;
  project: string;
  file_path: string;
  thumbnail: string;
  format: '3ds' | 'obj' | 'fbx' | 'gltf' | 'usdz';
  size_mb: number;
  vertex_count: number;
  face_count: number;
  materials: string[];
  textures: string[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Scene3D {
  id: string;
  name: string;
  project: string;
  models: string[];
  camera_position: { x: number; y: number; z: number };
  camera_rotation: { x: number; y: number; z: number };
  lighting: {
    ambient: string;
    directional: Array<{
      color: string;
      intensity: number;
      position: { x: number; y: number; z: number };
    }>;
  };
  background: string;
  environment_map?: string;
  created_at: string;
  updated_at: string;
}

export interface Prototype3D {
  id: string;
  name: string;
  scene: string;
  interactions: Array<{
    trigger: string;
    action: string;
    target: string;
  }>;
  animations: Array<{
    name: string;
    duration: number;
    loop: boolean;
  }>;
  share_link?: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface ARPreview {
  id: string;
  prototype: string;
  ar_mode: 'usdz' | 'gltf' | 'reality';
  scale: number;
  placement: 'floor' | 'wall' | 'table';
  qr_code?: string;
  share_link?: string;
  created_at: string;
  updated_at: string;
}

export interface Conversion3DTo2D {
  id: string;
  model: string;
  view_angle: { x: number; y: number; z: number };
  output_format: 'png' | 'svg' | 'pdf';
  resolution: { width: number; height: number };
  result_url?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

// Hooks for 3D Models
export function use3DModels(projectId?: string) {
  return useQuery({
    queryKey: ['3d-models', projectId],
    queryFn: () =>
      apiRequest<Model3D[]>(
        `/3d-studio/models/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function use3DModel(modelId: string) {
  return useQuery({
    queryKey: ['3d-model', modelId],
    queryFn: () => apiRequest<Model3D>(`/3d-studio/models/${modelId}/`),
    enabled: !!modelId,
  });
}

export function useUpload3DModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${API_BASE}/3d-studio/models/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to upload 3D model');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-models'] });
    },
  });
}

export function useUpdate3DModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      modelId,
      data,
    }: {
      modelId: string;
      data: Partial<Model3D>;
    }) =>
      apiRequest<Model3D>(`/3d-studio/models/${modelId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['3d-model', variables.modelId] });
      queryClient.invalidateQueries({ queryKey: ['3d-models'] });
    },
  });
}

export function useDelete3DModel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (modelId: string) =>
      apiRequest(`/3d-studio/models/${modelId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-models'] });
    },
  });
}

// Hooks for 3D Scenes
export function use3DScenes(projectId?: string) {
  return useQuery({
    queryKey: ['3d-scenes', projectId],
    queryFn: () =>
      apiRequest<Scene3D[]>(
        `/3d-studio/scenes/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function use3DScene(sceneId: string) {
  return useQuery({
    queryKey: ['3d-scene', sceneId],
    queryFn: () => apiRequest<Scene3D>(`/3d-studio/scenes/${sceneId}/`),
    enabled: !!sceneId,
  });
}

export function useCreate3DScene() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Scene3D>) =>
      apiRequest<Scene3D>('/3d-studio/scenes/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-scenes'] });
    },
  });
}

export function useUpdate3DScene() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sceneId,
      data,
    }: {
      sceneId: string;
      data: Partial<Scene3D>;
    }) =>
      apiRequest<Scene3D>(`/3d-studio/scenes/${sceneId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['3d-scene', variables.sceneId] });
      queryClient.invalidateQueries({ queryKey: ['3d-scenes'] });
    },
  });
}

export function useDelete3DScene() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (sceneId: string) =>
      apiRequest(`/3d-studio/scenes/${sceneId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-scenes'] });
    },
  });
}

// Hooks for 3D Prototypes
export function use3DPrototypes(projectId?: string) {
  return useQuery({
    queryKey: ['3d-prototypes', projectId],
    queryFn: () =>
      apiRequest<Prototype3D[]>(
        `/3d-studio/prototypes/${projectId ? `?project=${projectId}` : ''}`
      ),
    enabled: !!projectId,
  });
}

export function use3DPrototype(prototypeId: string) {
  return useQuery({
    queryKey: ['3d-prototype', prototypeId],
    queryFn: () => apiRequest<Prototype3D>(`/3d-studio/prototypes/${prototypeId}/`),
    enabled: !!prototypeId,
  });
}

export function useCreate3DPrototype() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Prototype3D>) =>
      apiRequest<Prototype3D>('/3d-studio/prototypes/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-prototypes'] });
    },
  });
}

export function useUpdate3DPrototype() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      prototypeId,
      data,
    }: {
      prototypeId: string;
      data: Partial<Prototype3D>;
    }) =>
      apiRequest<Prototype3D>(`/3d-studio/prototypes/${prototypeId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['3d-prototype', variables.prototypeId],
      });
      queryClient.invalidateQueries({ queryKey: ['3d-prototypes'] });
    },
  });
}

export function useDelete3DPrototype() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (prototypeId: string) =>
      apiRequest(`/3d-studio/prototypes/${prototypeId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-prototypes'] });
    },
  });
}

// Hooks for AR Preview
export function useARPreviews(prototypeId?: string) {
  return useQuery({
    queryKey: ['ar-previews', prototypeId],
    queryFn: () =>
      apiRequest<ARPreview[]>(
        `/3d-studio/ar-previews/${prototypeId ? `?prototype=${prototypeId}` : ''}`
      ),
    enabled: !!prototypeId,
  });
}

export function useCreateARPreview() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ARPreview>) =>
      apiRequest<ARPreview>('/3d-studio/ar-previews/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ar-previews'] });
    },
  });
}

// Hooks for 3D to 2D Conversion
export function useConvert3DTo2D() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<Conversion3DTo2D>) =>
      apiRequest<Conversion3DTo2D>('/3d-studio/conversions/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['3d-conversions'] });
    },
  });
}

export function useConversionStatus(conversionId: string) {
  return useQuery({
    queryKey: ['3d-conversion', conversionId],
    queryFn: () =>
      apiRequest<Conversion3DTo2D>(`/3d-studio/conversions/${conversionId}/`),
    enabled: !!conversionId,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.status === 'pending' || data?.status === 'processing' ? 2000 : false;
    },
  });
}

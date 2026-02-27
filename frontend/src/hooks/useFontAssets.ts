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
// FONT ASSETS - Font & Asset Hub
// ============================================

export interface FontFamily {
  id: string;
  name: string;
  category: 'serif' | 'sans-serif' | 'monospace' | 'display' | 'handwriting';
  source: 'google' | 'adobe' | 'custom' | 'system';
  variants: Array<{
    weight: number;
    style: 'normal' | 'italic';
    url: string;
  }>;
  preview_text: string;
  is_premium: boolean;
  license: string;
  file_size_kb: number;
  created_at: string;
}

export interface FontCollection {
  id: string;
  name: string;
  description: string;
  user: string;
  fonts: string[];
  is_public: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface IconSet {
  id: string;
  name: string;
  description: string;
  source: 'material' | 'fontawesome' | 'feather' | 'custom';
  icons_count: number;
  format: 'svg' | 'font' | 'png';
  style: 'outline' | 'filled' | 'rounded' | 'sharp' | 'duotone';
  is_premium: boolean;
  license: string;
  created_at: string;
}

export interface Icon {
  id: string;
  icon_set: string;
  name: string;
  tags: string[];
  svg_path: string;
  unicode?: string;
  size: number;
  preview_url: string;
  created_at: string;
}

export interface AssetLibrary {
  id: string;
  name: string;
  description: string;
  organization?: string;
  asset_types: string[];
  total_assets: number;
  storage_used_mb: number;
  is_shared: boolean;
  created_at: string;
  updated_at: string;
}

export interface LibraryAsset {
  id: string;
  library: string;
  name: string;
  asset_type: 'image' | 'video' | 'audio' | 'document' | 'font' | 'icon' | 'other';
  file_path: string;
  file_size_kb: number;
  file_format: string;
  thumbnail?: string;
  dimensions?: { width: number; height: number };
  duration?: number;
  metadata: Record<string, unknown>;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface StockProvider {
  id: string;
  name: string;
  api_endpoint: string;
  asset_types: string[];
  requires_api_key: boolean;
  is_active: boolean;
  pricing_model: 'free' | 'paid' | 'subscription' | 'credits';
  created_at: string;
}

export interface StockSearchResult {
  id: string;
  provider: string;
  asset_type: string;
  title: string;
  description?: string;
  preview_url: string;
  download_url: string;
  author: string;
  license: string;
  dimensions?: { width: number; height: number };
  file_size_kb?: number;
  price?: number;
  tags: string[];
}

export interface ColorPalette {
  id: string;
  name: string;
  colors: string[];
  description?: string;
  category: string;
  is_public: boolean;
  likes_count: number;
  created_by: string;
  created_at: string;
}

export interface GradientPreset {
  id: string;
  name: string;
  gradient_type: 'linear' | 'radial' | 'conic';
  color_stops: Array<{
    color: string;
    position: number;
  }>;
  angle?: number;
  category: string;
  is_premium: boolean;
  preview_url: string;
  created_at: string;
}

// Hooks for Fonts
export function useFonts(category?: string, source?: string) {
  return useQuery({
    queryKey: ['fonts', category, source],
    queryFn: () => {
      const params = [];
      if (category) params.push(`category=${category}`);
      if (source) params.push(`source=${source}`);
      const queryString = params.length ? `?${params.join('&')}` : '';
      return apiRequest<FontFamily[]>(`/font-assets/fonts/${queryString}`);
    },
  });
}

export function useFont(fontId: string) {
  return useQuery({
    queryKey: ['font', fontId],
    queryFn: () => apiRequest<FontFamily>(`/font-assets/fonts/${fontId}/`),
    enabled: !!fontId,
  });
}

export function useUploadCustomFont() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${API_BASE}/font-assets/fonts/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to upload font');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fonts'] });
    },
  });
}

export function useSearchFonts() {
  return useMutation({
    mutationFn: async (query: string) =>
      apiRequest<FontFamily[]>(`/font-assets/fonts/search/?q=${query}`, {
        method: 'GET',
      }),
  });
}

// Hooks for Font Collections
export function useFontCollections(userId?: string) {
  return useQuery({
    queryKey: ['font-collections', userId],
    queryFn: () =>
      apiRequest<FontCollection[]>(
        `/font-assets/font-collections/${userId ? `?user=${userId}` : ''}`
      ),
  });
}

export function useFontCollection(collectionId: string) {
  return useQuery({
    queryKey: ['font-collection', collectionId],
    queryFn: () =>
      apiRequest<FontCollection>(`/font-assets/font-collections/${collectionId}/`),
    enabled: !!collectionId,
  });
}

export function useCreateFontCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<FontCollection>) =>
      apiRequest<FontCollection>('/font-assets/font-collections/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['font-collections'] });
    },
  });
}

export function useUpdateFontCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      collectionId,
      data,
    }: {
      collectionId: string;
      data: Partial<FontCollection>;
    }) =>
      apiRequest<FontCollection>(`/font-assets/font-collections/${collectionId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['font-collection', variables.collectionId],
      });
      queryClient.invalidateQueries({ queryKey: ['font-collections'] });
    },
  });
}

export function useDeleteFontCollection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (collectionId: string) =>
      apiRequest(`/font-assets/font-collections/${collectionId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['font-collections'] });
    },
  });
}

// Hooks for Icon Sets
export function useIconSets(source?: string, style?: string) {
  return useQuery({
    queryKey: ['icon-sets', source, style],
    queryFn: () => {
      const params = [];
      if (source) params.push(`source=${source}`);
      if (style) params.push(`style=${style}`);
      const queryString = params.length ? `?${params.join('&')}` : '';
      return apiRequest<IconSet[]>(`/font-assets/icon-sets/${queryString}`);
    },
  });
}

export function useIconSet(setId: string) {
  return useQuery({
    queryKey: ['icon-set', setId],
    queryFn: () => apiRequest<IconSet>(`/font-assets/icon-sets/${setId}/`),
    enabled: !!setId,
  });
}

// Hooks for Icons
export function useIcons(iconSetId?: string, search?: string) {
  return useQuery({
    queryKey: ['icons', iconSetId, search],
    queryFn: () => {
      const params = [];
      if (iconSetId) params.push(`icon_set=${iconSetId}`);
      if (search) params.push(`search=${search}`);
      const queryString = params.length ? `?${params.join('&')}` : '';
      return apiRequest<Icon[]>(`/font-assets/icons/${queryString}`);
    },
  });
}

export function useIcon(iconId: string) {
  return useQuery({
    queryKey: ['icon', iconId],
    queryFn: () => apiRequest<Icon>(`/font-assets/icons/${iconId}/`),
    enabled: !!iconId,
  });
}

export function useSearchIcons() {
  return useMutation({
    mutationFn: async (query: string) =>
      apiRequest<Icon[]>(`/font-assets/icons/search/?q=${query}`, {
        method: 'GET',
      }),
  });
}

// Hooks for Asset Libraries
export function useAssetLibraries(organizationId?: string) {
  return useQuery({
    queryKey: ['asset-libraries', organizationId],
    queryFn: () =>
      apiRequest<AssetLibrary[]>(
        `/font-assets/libraries/${organizationId ? `?organization=${organizationId}` : ''}`
      ),
  });
}

export function useAssetLibrary(libraryId: string) {
  return useQuery({
    queryKey: ['asset-library', libraryId],
    queryFn: () => apiRequest<AssetLibrary>(`/font-assets/libraries/${libraryId}/`),
    enabled: !!libraryId,
  });
}

export function useCreateAssetLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<AssetLibrary>) =>
      apiRequest<AssetLibrary>('/font-assets/libraries/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['asset-libraries'] });
    },
  });
}

export function useUpdateAssetLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      libraryId,
      data,
    }: {
      libraryId: string;
      data: Partial<AssetLibrary>;
    }) =>
      apiRequest<AssetLibrary>(`/font-assets/libraries/${libraryId}/`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['asset-library', variables.libraryId] });
      queryClient.invalidateQueries({ queryKey: ['asset-libraries'] });
    },
  });
}

export function useDeleteAssetLibrary() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (libraryId: string) =>
      apiRequest(`/font-assets/libraries/${libraryId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['asset-libraries'] });
    },
  });
}

// Hooks for Library Assets
export function useLibraryAssets(libraryId?: string, assetType?: string) {
  return useQuery({
    queryKey: ['library-assets', libraryId, assetType],
    queryFn: () => {
      const params = [];
      if (libraryId) params.push(`library=${libraryId}`);
      if (assetType) params.push(`asset_type=${assetType}`);
      const queryString = params.length ? `?${params.join('&')}` : '';
      return apiRequest<LibraryAsset[]>(`/font-assets/assets/${queryString}`);
    },
  });
}

export function useLibraryAsset(assetId: string) {
  return useQuery({
    queryKey: ['library-asset', assetId],
    queryFn: () => apiRequest<LibraryAsset>(`/font-assets/assets/${assetId}/`),
    enabled: !!assetId,
  });
}

export function useUploadLibraryAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${API_BASE}/font-assets/assets/`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to upload asset');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library-assets'] });
    },
  });
}

export function useDeleteLibraryAsset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (assetId: string) =>
      apiRequest(`/font-assets/assets/${assetId}/`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library-assets'] });
    },
  });
}

// Hooks for Stock Providers
export function useStockProviders() {
  return useQuery({
    queryKey: ['stock-providers'],
    queryFn: () => apiRequest<StockProvider[]>('/font-assets/stock-providers/'),
  });
}

// Hooks for Stock Search
export function useStockSearch() {
  return useMutation({
    mutationFn: async (params: {
      query: string;
      provider?: string;
      asset_type?: string;
      page?: number;
    }) => {
      const queryParams = new URLSearchParams();
      if (params.query) queryParams.append('q', params.query);
      if (params.provider) queryParams.append('provider', params.provider);
      if (params.asset_type) queryParams.append('asset_type', params.asset_type);
      if (params.page) queryParams.append('page', params.page.toString());

      return apiRequest<StockSearchResult[]>(
        `/font-assets/stock-search/?${queryParams.toString()}`
      );
    },
  });
}

export function useDownloadStockAsset() {
  return useMutation({
    mutationFn: async (assetId: string) =>
      apiRequest(`/font-assets/stock-search/${assetId}/download/`, {
        method: 'POST',
      }),
  });
}

// Hooks for Color Palettes
export function useColorPalettes(category?: string) {
  return useQuery({
    queryKey: ['color-palettes', category],
    queryFn: () =>
      apiRequest<ColorPalette[]>(
        `/font-assets/palettes/${category ? `?category=${category}` : ''}`
      ),
  });
}

export function useColorPalette(paletteId: string) {
  return useQuery({
    queryKey: ['color-palette', paletteId],
    queryFn: () => apiRequest<ColorPalette>(`/font-assets/palettes/${paletteId}/`),
    enabled: !!paletteId,
  });
}

export function useCreateColorPalette() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<ColorPalette>) =>
      apiRequest<ColorPalette>('/font-assets/palettes/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['color-palettes'] });
    },
  });
}

export function useGenerateColorPalette() {
  return useMutation({
    mutationFn: async (baseColor: string) =>
      apiRequest<ColorPalette>('/font-assets/palettes/generate/', {
        method: 'POST',
        body: JSON.stringify({ base_color: baseColor }),
      }),
  });
}

// Hooks for Gradient Presets
export function useGradientPresets(category?: string) {
  return useQuery({
    queryKey: ['gradient-presets', category],
    queryFn: () =>
      apiRequest<GradientPreset[]>(
        `/font-assets/gradients/${category ? `?category=${category}` : ''}`
      ),
  });
}

export function useGradientPreset(presetId: string) {
  return useQuery({
    queryKey: ['gradient-preset', presetId],
    queryFn: () => apiRequest<GradientPreset>(`/font-assets/gradients/${presetId}/`),
    enabled: !!presetId,
  });
}

export function useCreateGradientPreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<GradientPreset>) =>
      apiRequest<GradientPreset>('/font-assets/gradients/', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gradient-presets'] });
    },
  });
}

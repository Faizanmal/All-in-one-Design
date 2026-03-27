// API service for asset management (folders, tags, bulk operations)
import api from './api';

// Asset Folder Types
export interface AssetFolder {
  id: number;
  name: string;
  parent: number | null;
  path: string;
  project: number;
  children_count: number;
  assets_count: number;
  created_at: string;
  updated_at: string;
}

// Asset Tag Types
export interface AssetTag {
  id: number;
  name: string;
  color: string;
  usage_count: number;
  created_at: string;
}

// Enhanced Asset Types
export interface EnhancedAsset {
  id: number;
  name: string;
  file: string;
  file_type: 'image' | 'video' | 'audio' | 'document' | 'font' | '3d_model' | 'lottie' | 'other';
  file_size: number;
  thumbnail?: string;
  width?: number;
  height?: number;
  duration?: number;
  folder: number | null;
  tags: AssetTag[];
  ai_tags?: string[];
  ai_description?: string;
  colors?: string[];
  cdn_url?: string;
  is_favorite: boolean;
  usage_count: number;
  version_count: number;
  current_version: number;
  created_by: {
    id: number;
    username: string;
    avatar?: string;
  };
  created_at: string;
  updated_at: string;
}

// CDN Integration Types
export interface CDNIntegration {
  id: number;
  provider: 'cloudinary' | 'aws_cloudfront' | 'bunny' | 'fastly' | 'custom';
  name: string;
  is_active: boolean;
  base_url: string;
  created_at: string;
}

// Usage Log Types
export interface AssetUsageLog {
  id: number;
  asset: number;
  project: number;
  page?: string;
  element?: string;
  used_at: string;
}

// Asset Stats Types
export interface AssetStats {
  total_assets: number;
  total_size: number;
  by_type: { type: string; count: number; size: number }[];
  unused_count: number;
  favorites_count: number;
}

// Asset Folder API
export const assetFoldersApi = {
  list: (projectId?: number) =>
    api.get<AssetFolder[]>('/v1/asset-management/folders/', {
      params: projectId ? { project: projectId } : undefined
    }),

  get: (folderId: number) =>
    api.get<AssetFolder>(`/v1/asset-management/folders/${folderId}/`),

  create: (data: { name: string; parent?: number; project: number }) =>
    api.post<AssetFolder>('/v1/asset-management/folders/', data),

  update: (folderId: number, data: Partial<AssetFolder>) =>
    api.patch<AssetFolder>(`/v1/asset-management/folders/${folderId}/`, data),

  delete: (folderId: number) =>
    api.delete(`/v1/asset-management/folders/${folderId}/`),

  getTree: (projectId: number) =>
    api.get<AssetFolder[]>(`/v1/asset-management/folders/tree/`, {
      params: { project: projectId }
    }),

  move: (folderId: number, newParentId: number | null) =>
    api.post(`/v1/asset-management/folders/${folderId}/move/`, { parent: newParentId }),
};

// Asset Tags API
export const assetTagsApi = {
  list: () =>
    api.get<AssetTag[]>('/v1/asset-management/tags/'),

  create: (data: { name: string; color: string }) =>
    api.post<AssetTag>('/v1/asset-management/tags/', data),

  update: (tagId: number, data: Partial<AssetTag>) =>
    api.patch<AssetTag>(`/v1/asset-management/tags/${tagId}/`, data),

  delete: (tagId: number) =>
    api.delete(`/v1/asset-management/tags/${tagId}/`),
};

// Enhanced Assets API
export const enhancedAssetsApi = {
  list: (params?: {
    folder?: number;
    tag?: number;
    file_type?: string;
    search?: string;
    is_favorite?: boolean;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) =>
    api.get<{ results: EnhancedAsset[]; count: number; next?: string; previous?: string }>(
      '/v1/asset-management/items/',
      { params }
    ),

  get: (assetId: number) =>
    api.get<EnhancedAsset>(`/v1/asset-management/items/${assetId}/`),

  create: (data: FormData) =>
    api.post<EnhancedAsset>('/v1/asset-management/items/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  update: (assetId: number, data: Partial<EnhancedAsset>) =>
    api.patch<EnhancedAsset>(`/v1/asset-management/items/${assetId}/`, data),

  delete: (assetId: number) =>
    api.delete(`/v1/asset-management/items/${assetId}/`),

  toggleFavorite: (assetId: number) =>
    api.post<EnhancedAsset>(`/v1/asset-management/items/${assetId}/toggle-favorite/`),

  addTags: (assetId: number, tagIds: number[]) =>
    api.post<EnhancedAsset>(`/v1/asset-management/items/${assetId}/add-tags/`, { tags: tagIds }),

  removeTags: (assetId: number, tagIds: number[]) =>
    api.post<EnhancedAsset>(`/v1/asset-management/items/${assetId}/remove-tags/`, { tags: tagIds }),

  move: (assetId: number, folderId: number | null) =>
    api.post<EnhancedAsset>(`/v1/asset-management/items/${assetId}/move/`, { folder: folderId }),

  analyze: (assetId: number) =>
    api.post<{ ai_tags: string[]; ai_description: string; colors: string[] }>(
      `/v1/asset-management/items/${assetId}/analyze/`
    ),

  getUsage: (assetId: number) =>
    api.get<AssetUsageLog[]>(`/v1/asset-management/items/${assetId}/usage/`),

  aiSearch: (query: string) =>
    api.get<EnhancedAsset[]>('/v1/asset-management/items/ai-search/', { params: { q: query } }),
};

// Bulk Operations API
export const bulkOperationsApi = {
  move: (assetIds: number[], folderId: number | null) =>
    api.post('/v1/asset-management/bulk-operations/move/', {
      asset_ids: assetIds,
      folder: folderId
    }),

  delete: (assetIds: number[]) =>
    api.post('/v1/asset-management/bulk-operations/delete/', {
      asset_ids: assetIds
    }),

  addTags: (assetIds: number[], tagIds: number[]) =>
    api.post('/v1/asset-management/bulk-operations/add-tags/', {
      asset_ids: assetIds,
      tag_ids: tagIds
    }),

  removeTags: (assetIds: number[], tagIds: number[]) =>
    api.post('/v1/asset-management/bulk-operations/remove-tags/', {
      asset_ids: assetIds,
      tag_ids: tagIds
    }),

  download: (assetIds: number[]) =>
    api.post('/v1/asset-management/bulk-operations/download/', {
      asset_ids: assetIds
    }, { responseType: 'blob' }),
};

// CDN Integration API
export const cdnIntegrationApi = {
  list: () =>
    api.get<CDNIntegration[]>('/v1/asset-management/cdn/'),

  create: (data: Omit<CDNIntegration, 'id' | 'created_at'>) =>
    api.post<CDNIntegration>('/v1/asset-management/cdn/', data),

  update: (cdnId: number, data: Partial<CDNIntegration>) =>
    api.patch<CDNIntegration>(`/v1/asset-management/cdn/${cdnId}/`, data),

  delete: (cdnId: number) =>
    api.delete(`/v1/asset-management/cdn/${cdnId}/`),

  test: (cdnId: number) =>
    api.post<{ status: string; latency: number }>(`/v1/asset-management/cdn/${cdnId}/test/`),
};

// Asset Stats API
export const assetStatsApi = {
  get: (projectId?: number) =>
    api.get<AssetStats>('/v1/asset-management/stats/', {
      params: projectId ? { project: projectId } : undefined
    }),

  getUnused: () =>
    api.get<EnhancedAsset[]>('/v1/asset-management/unused/'),

  cleanupUnused: () =>
    api.post<{ deleted_count: number }>('/v1/asset-management/unused/cleanup/'),
};

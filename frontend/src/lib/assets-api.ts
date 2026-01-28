// API service for assets versioning and collections
import api from './api';

// Asset Version Types
export interface AssetVersion {
  id: number;
  asset: number;
  version_number: number;
  file: string;
  file_size: number;
  description: string;
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
  is_current: boolean;
}

export interface AssetComment {
  id: number;
  asset: number;
  user: {
    id: number;
    username: string;
  };
  content: string;
  position_x?: number;
  position_y?: number;
  parent?: number;
  replies?: AssetComment[];
  created_at: string;
  updated_at: string;
}

export interface AssetCollection {
  id: number;
  name: string;
  description: string;
  owner: {
    id: number;
    username: string;
  };
  asset_count: number;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: number;
  name: string;
  file: string;
  file_type: string;
  file_size: number;
  thumbnail?: string;
  width?: number;
  height?: number;
  project: number;
  created_at: string;
  updated_at: string;
}

// Asset Version API
export const assetVersionsApi = {
  // List versions for an asset
  list: (assetId: number) => 
    api.get<AssetVersion[]>(`/v1/assets/versions/?asset=${assetId}`),
  
  // Create new version
  create: (data: { asset: number; file: File; description?: string }) => {
    const formData = new FormData();
    formData.append('asset', data.asset.toString());
    formData.append('file', data.file);
    if (data.description) {
      formData.append('description', data.description);
    }
    return api.post<AssetVersion>('/v1/assets/versions/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // Get version details
  get: (versionId: number) => 
    api.get<AssetVersion>(`/v1/assets/versions/${versionId}/`),
  
  // Restore to a specific version
  restore: (versionId: number) => 
    api.post<Asset>(`/v1/assets/versions/${versionId}/restore/`),
  
  // Delete version
  delete: (versionId: number) => 
    api.delete(`/v1/assets/versions/${versionId}/`),
};

// Asset Comments API
export const assetCommentsApi = {
  // List comments for an asset
  list: (assetId: number) => 
    api.get<AssetComment[]>(`/v1/assets/comments/?asset=${assetId}`),
  
  // Create comment
  create: (data: {
    asset: number;
    content: string;
    position_x?: number;
    position_y?: number;
    parent?: number;
  }) => api.post<AssetComment>('/v1/assets/comments/', data),
  
  // Update comment
  update: (commentId: number, data: { content: string }) => 
    api.patch<AssetComment>(`/v1/assets/comments/${commentId}/`, data),
  
  // Delete comment
  delete: (commentId: number) => 
    api.delete(`/v1/assets/comments/${commentId}/`),
};

// Asset Collections API
export const assetCollectionsApi = {
  // List all collections
  list: () => api.get<AssetCollection[]>('/v1/assets/collections/'),
  
  // Create collection
  create: (data: { name: string; description?: string; is_public?: boolean }) => 
    api.post<AssetCollection>('/v1/assets/collections/', data),
  
  // Get collection details
  get: (collectionId: number) => 
    api.get<AssetCollection>(`/v1/assets/collections/${collectionId}/`),
  
  // Update collection
  update: (collectionId: number, data: Partial<AssetCollection>) => 
    api.patch<AssetCollection>(`/v1/assets/collections/${collectionId}/`, data),
  
  // Delete collection
  delete: (collectionId: number) => 
    api.delete(`/v1/assets/collections/${collectionId}/`),
  
  // Add asset to collection
  addAsset: (collectionId: number, assetId: number) => 
    api.post(`/v1/assets/collections/${collectionId}/add_asset/`, { asset_id: assetId }),
  
  // Remove asset from collection
  removeAsset: (collectionId: number, assetId: number) => 
    api.post(`/v1/assets/collections/${collectionId}/remove_asset/`, { asset_id: assetId }),
  
  // Get assets in collection
  getAssets: (collectionId: number) => 
    api.get<Asset[]>(`/v1/assets/collections/${collectionId}/assets/`),
};

const assetsApi = {
  versions: assetVersionsApi,
  comments: assetCommentsApi,
  collections: assetCollectionsApi,
};

export default assetsApi;

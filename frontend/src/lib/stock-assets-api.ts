/**
 * Stock Assets API - Search and import stock photos/videos
 * from Unsplash, Pexels, and Pixabay.
 */
import apiClient from './api';

export interface StockAsset {
  id: string;
  provider: 'unsplash' | 'pexels' | 'pixabay';
  type: 'photo' | 'video' | 'illustration' | 'vector';
  title: string;
  thumbnail: string;
  preview: string;
  full: string;
  download_url: string;
  width: number;
  height: number;
  author: string;
  author_url: string;
  license: string;
  tags: string[];
  color?: string;
  duration?: number;
}

export interface StockSearchParams {
  q: string;
  provider?: 'unsplash' | 'pexels' | 'pixabay' | 'all';
  type?: 'photo' | 'video' | 'illustration' | 'vector';
  page?: number;
  per_page?: number;
  orientation?: 'landscape' | 'portrait' | 'squarish';
  color?: string;
}

export interface StockSearchResponse {
  results: StockAsset[];
  total: number;
  page: number;
  per_page: number;
}

export interface StockProvider {
  id: string;
  name: string;
  types: string[];
  configured: boolean;
  license: string;
  attribution_required: boolean;
}

export const stockAssetsApi = {
  search: async (params: StockSearchParams): Promise<StockSearchResponse> => {
    const response = await apiClient.get('/v1/assets/stock/search/', { params });
    return response.data;
  },

  getDownloadUrl: async (provider: string, assetId: string): Promise<string> => {
    const response = await apiClient.get(`/v1/assets/stock/download/${provider}/${assetId}/`);
    return response.data.download_url;
  },

  getProviders: async (): Promise<StockProvider[]> => {
    const response = await apiClient.get('/v1/assets/stock/providers/');
    return response.data.providers;
  },
};

export default stockAssetsApi;

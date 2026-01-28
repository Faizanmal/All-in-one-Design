// API service for search and filtering
import api from './api';

export interface SearchFilters {
  project_type?: string;
  created_after?: string;
  created_before?: string;
  has_ai?: boolean;
}

export interface AdvancedFilters {
  project_types?: string[];
  created_after?: string;
  created_before?: string;
  updated_after?: string;
  updated_before?: string;
  min_width?: number;
  max_width?: number;
  min_height?: number;
  max_height?: number;
  has_ai_prompt?: boolean;
  has_color_palette?: boolean;
  is_public?: boolean;
  owner_username?: string;
  colors?: string[];
  sort_by?: string;
}

class SearchAPI {
  async searchProjects(query: string, filters?: SearchFilters) {
    const params = new URLSearchParams();
    params.append('q', query);
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    
    const response = await api.get(`/projects/projects/search/?${params.toString()}`);
    return response.data;
  }

  async autocomplete(query: string, limit: number = 10) {
    const response = await api.get(`/projects/projects/autocomplete/?q=${query}&limit=${limit}`);
    return response.data;
  }

  async advancedFilter(filters: AdvancedFilters) {
    const response = await api.post('/projects/projects/advanced_filter/', filters);
    return response.data;
  }

  async getSuggestions(query: string) {
    const response = await api.get(`/projects/projects/suggestions/?q=${query}`);
    return response.data;
  }

  async getPopularSearches() {
    const response = await api.get('/projects/projects/popular_searches/');
    return response.data;
  }
}

export const searchAPI = new SearchAPI();

// API service for advanced search and filtering
import api from './api';

export interface SearchFilters {
  q?: string;
  type?: string;
  date_from?: string;
  date_to?: string;
  tags?: string[];
  sort?: string;
  page?: number;
  page_size?: number;
}

export interface ProjectSearchFilters extends SearchFilters {
  has_ai?: boolean;
  status?: string;
}

export interface AssetSearchFilters extends SearchFilters {
  min_size?: number;
  max_size?: number;
  min_width?: number;
  max_width?: number;
  min_height?: number;
  max_height?: number;
  ai_generated?: boolean;
  project?: number;
  collection?: number;
}

export interface TemplateSearchFilters extends SearchFilters {
  category?: string;
  premium?: boolean;
  featured?: boolean;
  min_rating?: number;
  colors?: string[];
}

export interface TeamSearchFilters extends SearchFilters {
  is_active?: boolean;
}

export interface SearchResult<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  type: string;
  thumbnail?: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
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
  created_at: string;
}

export interface Template {
  id: number;
  name: string;
  category: string;
  description?: string;
  thumbnail?: string;
  is_premium: boolean;
  is_featured: boolean;
  average_rating?: number;
  usage_count: number;
}

export interface Team {
  id: number;
  name: string;
  slug: string;
  description?: string;
  member_count: number;
  project_count: number;
  is_active: boolean;
}

export interface GlobalSearchResult {
  projects: Project[];
  assets: Asset[];
  templates: Template[];
  teams: Team[];
  total_count: number;
}

// Advanced Search API
export const advancedSearchApi = {
  // Search projects
  projects: (filters: ProjectSearchFilters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
    return api.get<SearchResult<Project>>(`/v1/projects/advanced-search/projects/?${params.toString()}`);
  },
  
  // Search assets
  assets: (filters: AssetSearchFilters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
    return api.get<SearchResult<Asset>>(`/v1/projects/advanced-search/assets/?${params.toString()}`);
  },
  
  // Search templates
  templates: (filters: TemplateSearchFilters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v.toString()));
        } else {
          params.append(key, value.toString());
        }
      }
    });
    return api.get<SearchResult<Template>>(`/v1/projects/advanced-search/templates/?${params.toString()}`);
  },
  
  // Search teams
  teams: (filters: TeamSearchFilters) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    return api.get<SearchResult<Team>>(`/v1/projects/advanced-search/teams/?${params.toString()}`);
  },
  
  // Global search across all content types
  global: (query: string, filters?: { type?: string }) => {
    const params = new URLSearchParams({ q: query });
    if (filters?.type) params.append('type', filters.type);
    return api.get<GlobalSearchResult>(`/v1/projects/advanced-search/global/?${params.toString()}`);
  },
};

export default advancedSearchApi;

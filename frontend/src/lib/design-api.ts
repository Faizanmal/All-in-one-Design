/**
 * API Client for AI-Powered Design Tool
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for AI operations
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============= Types =============

export interface Project {
  id: number;
  name: string;
  description: string;
  project_type: 'graphic' | 'ui_ux' | 'logo';
  canvas_width: number;
  canvas_height: number;
  canvas_background: string;
  design_data: Record<string, unknown>;
  ai_prompt: string;
  color_palette: string[];
  suggested_fonts: string[];
  created_at: string;
  updated_at: string;
  is_public: boolean;
  user_name: string;
  collaborator_names: string[];
  components: DesignComponent[];
}

export interface DesignComponent {
  id: number;
  project: number;
  component_type: 'text' | 'image' | 'shape' | 'button' | 'icon' | 'group' | 'frame' | 'map' | 'chart';
  properties: Record<string, unknown>;
  z_index: number;
  ai_generated: boolean;
  ai_prompt: string;
  created_at: string;
  updated_at: string;
}

export interface AIGenerationRequest {
  id: number;
  request_type: 'layout' | 'logo' | 'color_palette' | 'text_content' | 'image' | 'refinement';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  prompt: string;
  parameters: Record<string, unknown>;
  result: Record<string, unknown> | null;
  error_message: string;
  model_used: string;
  tokens_used: number | null;
  created_at: string;
  completed_at: string | null;
}

export interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  design_data: Record<string, unknown>;
  thumbnail_url: string;
  width: number;
  height: number;
  tags: string[];
  color_palette: string[];
  is_premium: boolean;
  is_public: boolean;
  use_count: number;
  ai_generated: boolean;
}

// ============= Auth API =============

export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/auth/login/', { username, password });
    return response.data;
  },
  
  register: async (username: string, email: string, password: string) => {
    const response = await apiClient.post('/auth/register/', { username, email, password });
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('auth_token');
  },
};

// ============= Projects API =============

export const projectsAPI = {
  list: async () => {
    const response = await apiClient.get<Project[]>('/projects/projects/');
    return response.data;
  },
  
  myProjects: async () => {
    const response = await apiClient.get<Project[]>('/projects/projects/my_projects/');
    return response.data;
  },
  
  get: async (id: number) => {
    const response = await apiClient.get<Project>(`/projects/projects/${id}/`);
    return response.data;
  },
  
  create: async (data: Partial<Project>) => {
    const response = await apiClient.post<Project>('/projects/projects/', data);
    return response.data;
  },
  
  update: async (id: number, data: Partial<Project>) => {
    const response = await apiClient.patch<Project>(`/projects/projects/${id}/`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    await apiClient.delete(`/projects/projects/${id}/`);
  },
  
  saveDesign: async (id: number, design_data: Record<string, unknown>) => {
    const response = await apiClient.post<Project>(
      `/projects/projects/${id}/save_design/`,
      { design_data }
    );
    return response.data;
  },
  
  createVersion: async (id: number) => {
    const response = await apiClient.post(`/projects/projects/${id}/create_version/`);
    return response.data;
  },
  
  getVersions: async (id: number) => {
    const response = await apiClient.get(`/projects/projects/${id}/versions/`);
    return response.data;
  },
  
  restoreVersion: async (id: number, version_number: number) => {
    const response = await apiClient.post(
      `/projects/projects/${id}/restore_version/`,
      { version_number }
    );
    return response.data;
  },
  
  addCollaborator: async (id: number, username: string) => {
    const response = await apiClient.post(
      `/projects/projects/${id}/add_collaborator/`,
      { username }
    );
    return response.data;
  },
};

// ============= AI Services API =============

export const aiAPI = {
  generateLayout: async (prompt: string, design_type: 'graphic' | 'ui_ux' | 'logo' = 'ui_ux') => {
    const response = await apiClient.post('/ai/generate-layout/', {
      prompt,
      design_type,
    });
    return response.data;
  },
  
  generateLogo: async (params: {
    company_name: string;
    industry?: string;
    style?: string;
    colors?: string[];
  }) => {
    const response = await apiClient.post('/ai/generate-logo/', params);
    return response.data;
  },
  
  generateColorPalette: async (theme: string) => {
    const response = await apiClient.post('/ai/generate-color-palette/', { theme });
    return response.data;
  },
  
  suggestFonts: async (design_style: string, purpose: string = 'general') => {
    const response = await apiClient.post('/ai/suggest-fonts/', {
      design_style,
      purpose,
    });
    return response.data;
  },
  
  refineDesign: async (current_design: Record<string, unknown>, refinement_instruction: string) => {
    const response = await apiClient.post('/ai/refine-design/', {
      current_design,
      refinement_instruction,
    });
    return response.data;
  },
  
  generateImage: async (prompt: string, size: string = '1024x1024', style: string = 'vivid') => {
    const response = await apiClient.post('/ai/generate-image/', {
      prompt,
      size,
      style,
    });
    return response.data;
  },
  
  getRequests: async () => {
    const response = await apiClient.get<AIGenerationRequest[]>('/ai/requests/');
    return response.data;
  },
};

// ============= Components API =============

export const componentsAPI = {
  list: async (project_id: number) => {
    const response = await apiClient.get<DesignComponent[]>('/projects/components/', {
      params: { project_id },
    });
    return response.data;
  },
  
  create: async (data: Partial<DesignComponent>) => {
    const response = await apiClient.post<DesignComponent>('/projects/components/', data);
    return response.data;
  },
  
  update: async (id: number, data: Partial<DesignComponent>) => {
    const response = await apiClient.patch<DesignComponent>(`/projects/components/${id}/`, data);
    return response.data;
  },
  
  delete: async (id: number) => {
    await apiClient.delete(`/projects/components/${id}/`);
  },
};

export default apiClient;

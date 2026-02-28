/**
 * API Client for AI Design Tool Backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
  withCredentials: true,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Use AxiosRequestConfig and track retry flag
    const originalRequest = error.config as unknown as import('axios').AxiosRequestConfig & { _retry?: boolean };

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('access_token', access);

          // Retry original request with new token
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ==================== Types ====================

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  timezone: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface Meeting {
  id: string;
  user: User;
  title: string;
  meeting_date: string;
  duration: number | null;
  duration_formatted: string | null;
  file_name: string;
  file_type: string;
  status: 'uploading' | 'processing' | 'transcribing' | 'analyzing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  action_items_count: number;
  is_shared: boolean;
  is_favorite: boolean;
  tags: Tag[];
}

export interface MeetingDetail extends Meeting {
  file_path: string;
  file_size: number;
  processing_started_at: string | null;
  processing_completed_at: string | null;
  error_message: string | null;
  transcript: string | null;
  summary: string | null;
  key_decisions: string[];
  share_token: string | null;
  share_url: string | null;
  speakers: Speaker[];
  action_items: ActionItem[];
  notes: MeetingNote[];
  transcript_segments: TranscriptSegment[];
}

export interface Speaker {
  id: string;
  name: string;
  speaker_id: string;
  created_at: string;
}

export interface TranscriptSegment {
  id: string;
  speaker: Speaker | null;
  text: string;
  start_time: number;
  end_time: number;
  confidence: number | null;
}

export interface ActionItem {
  id: string;
  meeting: string;
  meeting_title: string;
  task: string;
  owner: string | null;
  due_date: string | null;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  context: string | null;
  timestamp: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface MeetingNote {
  id: string;
  meeting: string;
  user: User;
  content: string;
  timestamp: number | null;
  created_at: string;
  updated_at: string;
}

export interface MeetingStats {
  total_meetings: number;
  completed: number;
  processing: number;
  failed: number;
  total_action_items: number;
  pending_action_items: number;
  completion_rate: number;
}

export interface AnalyticsData {
  meeting_trends: Array<{
    date: string;
    count: number;
  }>;
  duration_stats: {
    average_minutes: number;
    total_hours: number;
    total_meetings: number;
  };
  status_distribution: Array<{
    status: string;
    count: number;
  }>;
  speaker_stats: Array<{
    name: string;
    segment_count: number;
    meeting_count: number;
  }>;
  action_item_priority: Array<{
    priority: string;
    count: number;
  }>;
  action_item_status: Array<{
    status: string;
    count: number;
  }>;
  completion_trends: Array<{
    week: string;
    completion_rate: number;
    total: number;
    completed: number;
  }>;
  tag_stats: Array<{
    name: string;
    color: string;
    meeting_count: number;
  }>;
}

// ==================== API Functions ====================

// Authentication
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/auth/token/', { username, password });
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    return response.data;
  },

  register: async (username: string, email: string, password: string, timezone?: string) => {
    const response = await apiClient.post('/users/register/', { 
      username, 
      email, 
      password,
      password_confirm: password,
      timezone: timezone || 'UTC'
    });
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  verifyToken: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) throw new Error('No token found');
    return await apiClient.post('/auth/token/verify/', { token });
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/users/profile/');
    return response.data;
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch('/users/profile/', data);
    return response.data;
  },

  changePassword: async (oldPassword: string, newPassword: string) => {
    const response = await apiClient.post('/users/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password_confirm: newPassword,
    });
    return response.data;
  },
};

// Meetings
export const meetingsAPI = {
  list: async (params?: {
    search?: string;
    status?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: Meeting[]; count: number; next: string | null; previous: string | null }> => {
    const response = await apiClient.get('/meetings/', { params });
    return response.data;
  },

  get: async (id: string): Promise<MeetingDetail> => {
    const response = await apiClient.get(`/meetings/${id}/`);
    return response.data;
  },

  create: async (data: FormData) => {
    const response = await apiClient.post('/meetings/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes for uploads
    });
    return response.data;
  },

  update: async (id: string, data: Partial<Meeting>) => {
    const response = await apiClient.patch(`/meetings/${id}/`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/meetings/${id}/`);
  },

  getTranscript: async (id: string) => {
    const response = await apiClient.get(`/meetings/${id}/transcript/`);
    return response.data;
  },

  share: async (id: string) => {
    const response = await apiClient.post(`/meetings/${id}/share/`);
    return response.data;
  },

  getShared: async (token: string): Promise<MeetingDetail> => {
    const response = await apiClient.get(`/meetings/shared/${token}/`);
    return response.data;
  },

  getStats: async (): Promise<MeetingStats> => {
    const response = await apiClient.get('/meetings/stats/');
    return response.data;
  },

  getAnalytics: async (days: number = 30): Promise<AnalyticsData> => {
    const response = await apiClient.get('/meetings/analytics/', {
      params: { days }
    });
    return response.data;
  },

  exportPDF: async (id: string) => {
    const response = await apiClient.get(`/meetings/${id}/export_pdf/`, {
      responseType: 'blob',
    });
    return response.data;
  },

  toggleFavorite: async (id: string) => {
    const response = await apiClient.post(`/meetings/${id}/toggle_favorite/`);
    return response.data;
  },

  getFavorites: async (): Promise<Meeting[]> => {
    const response = await apiClient.get('/meetings/favorites/');
    return response.data;
  },

  exportMarkdown: async (id: string) => {
    const response = await apiClient.get(`/meetings/${id}/export_markdown/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Action Items
export const actionItemsAPI = {
  list: async (params?: {
    search?: string;
    status?: string;
    priority?: string;
    meeting?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: ActionItem[]; count: number }> => {
    const response = await apiClient.get('/action-items/', { params });
    return response.data;
  },

  get: async (id: string): Promise<ActionItem> => {
    const response = await apiClient.get(`/action-items/${id}/`);
    return response.data;
  },

  create: async (data: Partial<ActionItem>) => {
    const response = await apiClient.post('/action-items/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<ActionItem>) => {
    const response = await apiClient.patch(`/action-items/${id}/`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/action-items/${id}/`);
  },

  complete: async (id: string) => {
    const response = await apiClient.post(`/action-items/${id}/complete/`);
    return response.data;
  },
};

// Meeting Notes
export const notesAPI = {
  list: async (meetingId?: string) => {
    const response = await apiClient.get('/notes/', {
      params: meetingId ? { meeting: meetingId } : undefined,
    });
    return response.data;
  },

  create: async (data: { meeting: string; content: string; timestamp?: number }) => {
    const response = await apiClient.post('/notes/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<MeetingNote>) => {
    const response = await apiClient.patch(`/notes/${id}/`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/notes/${id}/`);
  },
};

// Tags
export const tagsAPI = {
  list: async (): Promise<Tag[]> => {
    const response = await apiClient.get('/tags/');
    return response.data;
  },

  get: async (id: string): Promise<Tag> => {
    const response = await apiClient.get(`/tags/${id}/`);
    return response.data;
  },

  create: async (data: { name: string; color?: string }) => {
    const response = await apiClient.post('/tags/', data);
    return response.data;
  },

  update: async (id: string, data: Partial<Tag>) => {
    const response = await apiClient.patch(`/tags/${id}/`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await apiClient.delete(`/tags/${id}/`);
  },
};

// Default axios instance export
export default apiClient;

// Named API modules export
export const api = {
  auth: authAPI,
  meetings: meetingsAPI,
  actionItems: actionItemsAPI,
  notes: notesAPI,
  tags: tagsAPI,
};

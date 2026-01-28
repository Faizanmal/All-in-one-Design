import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance with interceptors
const authApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
authApi.interceptors.request.use(
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
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        originalRequest.headers.Authorization = `Bearer ${access}`;
        return authApi(originalRequest);
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

// Auth API functions
export const authService = {
  async login(email: string, password: string) {
    const response = await authApi.post('/token/', { email, password });
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    return response.data;
  },

  async register(name: string, email: string, password: string) {
    const response = await authApi.post('/register/', { name, email, password });
    return response.data;
  },

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  async getCurrentUser() {
    const response = await authApi.get('/users/me/');
    return response.data;
  },

  async verifyToken() {
    try {
      const token = localStorage.getItem('access_token');
      await authApi.post('/token/verify/', { token });
      return true;
    } catch {
      return false;
    }
  },
};

// Analytics API
export const analyticsService = {
  async getDashboardStats() {
    const response = await authApi.get('/v1/analytics/dashboard-stats/');
    return response.data;
  },

  async getProjectAnalytics(projectId: string) {
    const response = await authApi.get(`/v1/analytics/projects/${projectId}/`);
    return response.data;
  },

  async getAIUsage() {
    const response = await authApi.get('/v1/analytics/ai-usage/');
    return response.data;
  },

  async trackActivity(activityType: string, metadata: Record<string, unknown>) {
    const response = await authApi.post('/v1/analytics/track/', {
      activity_type: activityType,
      metadata,
    });
    return response.data;
  },
};

// Subscription API
export const subscriptionService = {
  async getCurrentSubscription() {
    const response = await authApi.get('/v1/subscriptions/current/');
    return response.data;
  },

  async getTiers() {
    const response = await authApi.get('/v1/subscriptions/tiers/');
    return response.data;
  },

  async upgradePlan(tierId: string) {
    const response = await authApi.post('/v1/subscriptions/upgrade/', {
      tier_id: tierId,
    });
    return response.data;
  },

  async getUsageStats() {
    const response = await authApi.get('/v1/subscriptions/usage/');
    return response.data;
  },

  async getInvoices() {
    const response = await authApi.get('/v1/subscriptions/invoices/');
    return response.data;
  },
};

export default authApi;

// API service for notifications and webhooks
import api from './api';

// Notification Types
export interface Notification {
  id: number;
  type: 'project_shared' | 'project_update' | 'comment_added' | 'team_invitation' | 
        'ai_generation_complete' | 'export_complete' | 'subscription_update' | 'system_alert';
  title: string;
  message: string;
  read: boolean;
  data?: Record<string, unknown>;
  created_at: string;
}

export interface UserPreference {
  id: number;
  user: number;
  email_notifications: boolean;
  push_notifications: boolean;
  notification_types: {
    project_shared: boolean;
    project_update: boolean;
    comment_added: boolean;
    team_invitation: boolean;
    ai_generation_complete: boolean;
    export_complete: boolean;
    subscription_update: boolean;
    system_alert: boolean;
  };
}

export interface Webhook {
  id: number;
  name: string;
  url: string;
  is_active: boolean;
  events: string[];
  secret?: string;
  created_at: string;
  last_triggered_at?: string;
}

export interface WebhookDelivery {
  id: number;
  webhook: number;
  event: string;
  payload: Record<string, unknown>;
  response_code?: number;
  response_body?: string;
  success: boolean;
  attempted_at: string;
}

// Notifications API
export const notificationsApi = {
  // List all notifications
  list: () => api.get<Notification[]>('/v1/notifications/notifications/'),
  
  // Get unread notifications
  unread: () => api.get<{ count: number; notifications: Notification[] }>('/v1/notifications/notifications/unread/'),
  
  // Mark notification as read
  markRead: (notificationId: number) => 
    api.post(`/v1/notifications/notifications/${notificationId}/mark_read/`),
  
  // Mark all as read
  markAllRead: () => 
    api.post('/v1/notifications/notifications/mark_all_read/'),
  
  // Clear all notifications
  clearAll: () => 
    api.delete('/v1/notifications/notifications/clear_all/'),
  
  // Delete specific notification
  delete: (notificationId: number) => 
    api.delete(`/v1/notifications/notifications/${notificationId}/`),
};

// User Preferences API
export const userPreferencesApi = {
  // Get user preferences
  get: () => api.get<UserPreference>('/v1/notifications/preferences/'),
  
  // Update preferences
  update: (data: Partial<UserPreference>) => 
    api.patch<UserPreference>('/v1/notifications/preferences/', data),
};

// Webhooks API
export const webhooksApi = {
  // List webhooks
  list: () => api.get<Webhook[]>('/v1/notifications/webhooks/'),
  
  // Create webhook
  create: (data: {
    name: string;
    url: string;
    events: string[];
    is_active?: boolean;
  }) => api.post<Webhook>('/v1/notifications/webhooks/', data),
  
  // Get webhook details
  get: (webhookId: number) => 
    api.get<Webhook>(`/v1/notifications/webhooks/${webhookId}/`),
  
  // Update webhook
  update: (webhookId: number, data: Partial<Webhook>) => 
    api.patch<Webhook>(`/v1/notifications/webhooks/${webhookId}/`, data),
  
  // Delete webhook
  delete: (webhookId: number) => 
    api.delete(`/v1/notifications/webhooks/${webhookId}/`),
  
  // Test webhook
  test: (webhookId: number) => 
    api.post(`/v1/notifications/webhooks/${webhookId}/test/`),
  
  // Get webhook deliveries
  deliveries: (webhookId: number) => 
    api.get<WebhookDelivery[]>(`/v1/notifications/webhooks/${webhookId}/deliveries/`),
};

const notificationsApiExport = {
  notifications: notificationsApi,
  preferences: userPreferencesApi,
  webhooks: webhooksApi,
};

export default notificationsApiExport;

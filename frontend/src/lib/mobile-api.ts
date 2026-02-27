/**
 * Mobile API Client
 * Production-ready API for mobile app integration
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/mobile`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type Platform = 'ios' | 'android' | 'web' | 'desktop';
export type NotificationType = 'comment' | 'mention' | 'share' | 'update' | 'review' | 'system';

export interface MobileDevice {
  id: string;
  user: number;
  device_id: string;
  device_name: string;
  platform: Platform;
  os_version: string;
  app_version: string;
  push_token: string | null;
  push_enabled: boolean;
  last_active: string;
  is_active: boolean;
  is_trusted: boolean;
  biometrics_enabled: boolean;
  device_info: {
    model: string;
    manufacturer: string;
    screen_width: number;
    screen_height: number;
    is_tablet: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface MobileSession {
  id: string;
  user: number;
  device: string;
  access_token: string;
  refresh_token: string;
  expires_at: string;
  is_active: boolean;
  ip_address: string;
  user_agent: string;
  last_activity: string;
  created_at: string;
}

export interface OfflineCache {
  id: string;
  user: number;
  device: string;
  content_type: 'project' | 'file' | 'component' | 'asset' | 'team';
  content_id: string;
  content_name: string;
  cache_size: number;
  last_synced: string;
  sync_version: number;
  is_dirty: boolean;
  pending_changes: Array<{
    id: string;
    action: 'create' | 'update' | 'delete';
    data: Record<string, unknown>;
    timestamp: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface MobileAnnotation {
  id: string;
  user: number;
  project: number;
  node_id: string;
  annotation_type: 'drawing' | 'voice' | 'text' | 'pin';
  content: string;
  drawing_data: Record<string, unknown> | null;
  voice_url: string | null;
  voice_duration: number | null;
  position_x: number;
  position_y: number;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MobileNotification {
  id: string;
  user: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  data: Record<string, unknown>;
  deep_link: string | null;
  image_url: string | null;
  is_read: boolean;
  read_at: string | null;
  is_pushed: boolean;
  pushed_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface MobilePreference {
  id: string;
  user: number;
  theme: 'light' | 'dark' | 'system';
  notifications_enabled: boolean;
  notification_settings: {
    comments: boolean;
    mentions: boolean;
    shares: boolean;
    updates: boolean;
    reviews: boolean;
    system: boolean;
    quiet_hours_enabled: boolean;
    quiet_hours_start: string;
    quiet_hours_end: string;
  };
  offline_mode_enabled: boolean;
  auto_sync: boolean;
  sync_on_wifi_only: boolean;
  max_cache_size: number;
  gesture_settings: {
    swipe_to_navigate: boolean;
    pinch_to_zoom: boolean;
    double_tap_to_select: boolean;
  };
  accessibility_settings: {
    font_size: 'small' | 'medium' | 'large' | 'xlarge';
    high_contrast: boolean;
    reduce_motion: boolean;
    voice_over_enabled: boolean;
  };
  created_at: string;
  updated_at: string;
}

export interface MobileAppVersion {
  id: string;
  platform: Platform;
  version: string;
  build_number: string;
  min_supported_version: string;
  is_mandatory: boolean;
  release_notes: string;
  download_url: string;
  file_size: number;
  released_at: string;
  is_active: boolean;
  created_at: string;
}

export interface SyncStatus {
  device_id: string;
  last_sync: string;
  pending_uploads: number;
  pending_downloads: number;
  sync_in_progress: boolean;
  sync_progress: number;
  conflicts: Array<{
    content_type: string;
    content_id: string;
    local_version: number;
    server_version: number;
  }>;
  total_cached_size: number;
  items_cached: number;
}

export interface ProjectSyncData {
  project_id: number;
  project_name: string;
  last_modified: string;
  version: number;
  files: Array<{
    id: string;
    name: string;
    size: number;
    version: number;
    download_url: string;
  }>;
  components: Array<{
    id: string;
    name: string;
    thumbnail_url: string;
  }>;
  assets: Array<{
    id: string;
    name: string;
    size: number;
    download_url: string;
  }>;
}

export interface AnalyticsEvent {
  event_type: string;
  event_data: Record<string, unknown>;
  timestamp: string;
  session_id: string;
  screen_name?: string;
}

// API Functions
export const mobileApi = {
  // Device operations
  async getDevices(): Promise<MobileDevice[]> {
    const { data } = await apiClient.get('/devices/');
    return data.results || data;
  },

  async getDevice(deviceId: string): Promise<MobileDevice> {
    const { data } = await apiClient.get(`/devices/${deviceId}/`);
    return data;
  },

  async registerDevice(device: {
    device_id: string;
    device_name: string;
    platform: Platform;
    os_version: string;
    app_version: string;
    push_token?: string;
    device_info?: MobileDevice['device_info'];
  }): Promise<MobileDevice> {
    const { data } = await apiClient.post('/devices/', device);
    return data;
  },

  async updateDevice(deviceId: string, updates: Partial<MobileDevice>): Promise<MobileDevice> {
    const { data } = await apiClient.patch(`/devices/${deviceId}/`, updates);
    return data;
  },

  async deleteDevice(deviceId: string): Promise<void> {
    await apiClient.delete(`/devices/${deviceId}/`);
  },

  async updatePushToken(deviceId: string, pushToken: string): Promise<MobileDevice> {
    const { data } = await apiClient.post(`/devices/${deviceId}/update_push_token/`, {
      push_token: pushToken,
    });
    return data;
  },

  async deactivateDevice(deviceId: string): Promise<MobileDevice> {
    const { data } = await apiClient.post(`/devices/${deviceId}/deactivate/`);
    return data;
  },

  async trustDevice(deviceId: string): Promise<MobileDevice> {
    const { data } = await apiClient.post(`/devices/${deviceId}/trust/`);
    return data;
  },

  async untrustDevice(deviceId: string): Promise<MobileDevice> {
    const { data } = await apiClient.post(`/devices/${deviceId}/untrust/`);
    return data;
  },

  async setupBiometrics(deviceId: string, enabled: boolean): Promise<MobileDevice> {
    const { data } = await apiClient.post(`/devices/${deviceId}/setup_biometrics/`, { enabled });
    return data;
  },

  // Session operations
  async getSessions(): Promise<MobileSession[]> {
    const { data } = await apiClient.get('/sessions/');
    return data.results || data;
  },

  async createSession(options: {
    device_id: string;
    ip_address?: string;
    user_agent?: string;
  }): Promise<MobileSession> {
    const { data } = await apiClient.post('/sessions/', options);
    return data;
  },

  async refreshSession(sessionId: string): Promise<MobileSession> {
    const { data } = await apiClient.post(`/sessions/${sessionId}/refresh/`);
    return data;
  },

  async endSession(sessionId: string): Promise<void> {
    await apiClient.post(`/sessions/${sessionId}/end/`);
  },

  async endAllSessions(): Promise<{ ended_count: number }> {
    const { data } = await apiClient.post('/sessions/end_all/');
    return data;
  },

  async updateSessionActivity(sessionId: string): Promise<MobileSession> {
    const { data } = await apiClient.post(`/sessions/${sessionId}/update_activity/`);
    return data;
  },

  // Offline Cache operations
  async getCachedItems(deviceId: string): Promise<OfflineCache[]> {
    const { data } = await apiClient.get(`/cache/?device=${deviceId}`);
    return data.results || data;
  },

  async cacheContent(options: {
    device: string;
    content_type: OfflineCache['content_type'];
    content_id: string;
    content_name: string;
  }): Promise<OfflineCache> {
    const { data } = await apiClient.post('/cache/', options);
    return data;
  },

  async removeCachedItem(cacheId: string): Promise<void> {
    await apiClient.delete(`/cache/${cacheId}/`);
  },

  async clearCache(deviceId: string): Promise<{ cleared_count: number; freed_bytes: number }> {
    const { data } = await apiClient.post(`/cache/clear/?device=${deviceId}`);
    return data;
  },

  async getSyncStatus(deviceId: string): Promise<SyncStatus> {
    const { data } = await apiClient.get(`/cache/sync_status/?device=${deviceId}`);
    return data;
  },

  async syncContent(deviceId: string, contentIds?: string[]): Promise<{
    synced_count: number;
    failed_count: number;
    conflicts: number;
  }> {
    const { data } = await apiClient.post('/cache/sync/', {
      device: deviceId,
      content_ids: contentIds,
    });
    return data;
  },

  async uploadPendingChanges(deviceId: string, changes: Array<{
    cache_id: string;
    action: 'create' | 'update' | 'delete';
    data: Record<string, unknown>;
  }>): Promise<{
    uploaded_count: number;
    failed_count: number;
    conflicts: Array<{
      cache_id: string;
      error: string;
    }>;
  }> {
    const { data } = await apiClient.post('/cache/upload_changes/', {
      device: deviceId,
      changes,
    });
    return data;
  },

  async resolveConflict(cacheId: string, resolution: 'keep_local' | 'keep_server' | 'merge'): Promise<OfflineCache> {
    const { data } = await apiClient.post(`/cache/${cacheId}/resolve_conflict/`, { resolution });
    return data;
  },

  // Annotation operations
  async getAnnotations(projectId: number): Promise<MobileAnnotation[]> {
    const { data } = await apiClient.get(`/annotations/?project=${projectId}`);
    return data.results || data;
  },

  async createAnnotation(annotation: Partial<MobileAnnotation>): Promise<MobileAnnotation> {
    const { data } = await apiClient.post('/annotations/', annotation);
    return data;
  },

  async updateAnnotation(annotationId: string, updates: Partial<MobileAnnotation>): Promise<MobileAnnotation> {
    const { data } = await apiClient.patch(`/annotations/${annotationId}/`, updates);
    return data;
  },

  async deleteAnnotation(annotationId: string): Promise<void> {
    await apiClient.delete(`/annotations/${annotationId}/`);
  },

  async resolveAnnotation(annotationId: string): Promise<MobileAnnotation> {
    const { data } = await apiClient.post(`/annotations/${annotationId}/resolve/`);
    return data;
  },

  async unresolveAnnotation(annotationId: string): Promise<MobileAnnotation> {
    const { data } = await apiClient.post(`/annotations/${annotationId}/unresolve/`);
    return data;
  },

  async uploadVoiceAnnotation(projectId: number, nodeId: string, audioBlob: Blob, position: { x: number; y: number }): Promise<MobileAnnotation> {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice_annotation.m4a');
    formData.append('project', String(projectId));
    formData.append('node_id', nodeId);
    formData.append('position_x', String(position.x));
    formData.append('position_y', String(position.y));
    formData.append('annotation_type', 'voice');
    const { data } = await apiClient.post('/annotations/voice/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async batchSyncAnnotations(deviceId: string, annotations: Array<Partial<MobileAnnotation>>): Promise<{
    created: MobileAnnotation[];
    updated: MobileAnnotation[];
    failed: Array<{ index: number; error: string }>;
  }> {
    const { data } = await apiClient.post('/annotations/batch_sync/', {
      device: deviceId,
      annotations,
    });
    return data;
  },

  // Notification operations
  async getNotifications(options?: {
    is_read?: boolean;
    notification_type?: NotificationType;
    limit?: number;
  }): Promise<MobileNotification[]> {
    const params = new URLSearchParams();
    if (options?.is_read !== undefined) params.append('is_read', String(options.is_read));
    if (options?.notification_type) params.append('notification_type', options.notification_type);
    if (options?.limit) params.append('limit', String(options.limit));
    const { data } = await apiClient.get(`/notifications/?${params}`);
    return data.results || data;
  },

  async getUnreadCount(): Promise<{ count: number }> {
    const { data } = await apiClient.get('/notifications/unread_count/');
    return data;
  },

  async markAsRead(notificationId: string): Promise<MobileNotification> {
    const { data } = await apiClient.post(`/notifications/${notificationId}/mark_read/`);
    return data;
  },

  async markAllAsRead(): Promise<{ marked_count: number }> {
    const { data } = await apiClient.post('/notifications/mark_all_read/');
    return data;
  },

  async deleteNotification(notificationId: string): Promise<void> {
    await apiClient.delete(`/notifications/${notificationId}/`);
  },

  async deleteAllNotifications(): Promise<{ deleted_count: number }> {
    const { data } = await apiClient.delete('/notifications/delete_all/');
    return data;
  },

  // Preference operations
  async getPreferences(): Promise<MobilePreference> {
    const { data } = await apiClient.get('/preferences/my/');
    return data;
  },

  async updatePreferences(updates: Partial<MobilePreference>): Promise<MobilePreference> {
    const { data } = await apiClient.patch('/preferences/my/', updates);
    return data;
  },

  async resetPreferences(): Promise<MobilePreference> {
    const { data } = await apiClient.post('/preferences/reset/');
    return data;
  },

  // App Version operations
  async checkVersion(platform: Platform, currentVersion: string): Promise<{
    update_available: boolean;
    latest_version: MobileAppVersion | null;
    is_mandatory: boolean;
    download_url: string | null;
  }> {
    const { data } = await apiClient.get(`/versions/check/?platform=${platform}&current_version=${currentVersion}`);
    return data;
  },

  async getVersionHistory(platform: Platform): Promise<MobileAppVersion[]> {
    const { data } = await apiClient.get(`/versions/?platform=${platform}`);
    return data.results || data;
  },

  // Project Sync operations
  async syncProject(projectId: number, deviceId: string): Promise<ProjectSyncData> {
    const { data } = await apiClient.post('/sync/projects/', {
      project_id: projectId,
      device_id: deviceId,
    });
    return data;
  },

  async getProjectSyncStatus(projectId: number, deviceId: string): Promise<{
    is_synced: boolean;
    local_version: number;
    server_version: number;
    needs_update: boolean;
    size_difference: number;
  }> {
    const { data } = await apiClient.get(`/sync/projects/status/?project=${projectId}&device=${deviceId}`);
    return data;
  },

  async downloadProjectAsset(projectId: number, assetId: string): Promise<Blob> {
    const { data } = await apiClient.get(`/sync/projects/${projectId}/assets/${assetId}/download/`, {
      responseType: 'blob',
    });
    return data;
  },

  // Analytics operations
  async trackEvent(event: AnalyticsEvent): Promise<void> {
    await apiClient.post('/analytics/events/', event);
  },

  async trackEvents(events: AnalyticsEvent[]): Promise<{ tracked_count: number }> {
    const { data } = await apiClient.post('/analytics/events/batch/', { events });
    return data;
  },

  async trackScreenView(screenName: string, sessionId: string): Promise<void> {
    await apiClient.post('/analytics/screen_view/', {
      screen_name: screenName,
      session_id: sessionId,
    });
  },

  async trackError(error: {
    message: string;
    stack?: string;
    context?: Record<string, unknown>;
    session_id: string;
  }): Promise<void> {
    await apiClient.post('/analytics/error/', error);
  },

  // Utility functions
  async testConnection(): Promise<{ status: 'ok'; latency_ms: number }> {
    const start = Date.now();
    const { data } = await apiClient.get('/health/');
    return { ...data, latency_ms: Date.now() - start };
  },

  async getServerTime(): Promise<{ server_time: string; timezone: string }> {
    const { data } = await apiClient.get('/time/');
    return data;
  },

  async reportIssue(issue: {
    title: string;
    description: string;
    device_id: string;
    logs?: string;
    screenshot?: Blob;
  }): Promise<{ issue_id: string }> {
    const formData = new FormData();
    formData.append('title', issue.title);
    formData.append('description', issue.description);
    formData.append('device_id', issue.device_id);
    if (issue.logs) formData.append('logs', issue.logs);
    if (issue.screenshot) formData.append('screenshot', issue.screenshot);
    const { data } = await apiClient.post('/support/report/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};

export default mobileApi;

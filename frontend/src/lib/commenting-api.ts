// API service for commenting system
import api from './api';

// Comment Thread Types
export interface CommentThread {
  id: number;
  project: number;
  page?: number;
  element_id?: string;
  position_x: number;
  position_y: number;
  frame_index?: number;
  title?: string;
  status: 'open' | 'resolved' | 'closed';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  assigned_to?: {
    id: number;
    username: string;
    avatar?: string;
  };
  created_by: {
    id: number;
    username: string;
    avatar?: string;
  };
  comment_count: number;
  unread_count: number;
  last_activity: string;
  created_at: string;
  updated_at: string;
}

// Comment Types
export interface Comment {
  id: number;
  thread: number;
  parent?: number;
  content: string;
  comment_type: 'text' | 'voice' | 'video' | 'annotation';
  attachment?: string;
  voice_duration?: number;
  video_duration?: number;
  annotations?: AnnotationData[];
  mentions: UserMention[];
  reactions: CommentReaction[];
  is_edited: boolean;
  created_by: {
    id: number;
    username: string;
    avatar?: string;
  };
  replies?: Comment[];
  created_at: string;
  updated_at: string;
}

// Annotation Data Types
export interface AnnotationData {
  type: 'arrow' | 'circle' | 'rectangle' | 'freehand' | 'pin';
  color: string;
  stroke_width: number;
  points: { x: number; y: number }[];
  text?: string;
}

// User Mention Types
export interface UserMention {
  id: number;
  user: {
    id: number;
    username: string;
    avatar?: string;
  };
  position_start: number;
  position_end: number;
}

// Comment Reaction Types
export interface CommentReaction {
  id: number;
  emoji: string;
  users: {
    id: number;
    username: string;
  }[];
  count: number;
}

// Review Session Types
export interface ReviewSession {
  id: number;
  project: number;
  name: string;
  description?: string;
  status: 'draft' | 'in_review' | 'approved' | 'needs_changes' | 'rejected';
  due_date?: string;
  reviewers: Reviewer[];
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
  completed_at?: string;
}

// Reviewer Types
export interface Reviewer {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
    avatar?: string;
  };
  status: 'pending' | 'approved' | 'needs_changes' | 'rejected';
  feedback?: string;
  reviewed_at?: string;
}

// Comment Notification Types
export interface CommentNotification {
  id: number;
  thread: number;
  comment?: number;
  notification_type: 'mention' | 'reply' | 'assignment' | 'resolution' | 'reaction';
  is_read: boolean;
  created_at: string;
}

// Comment Templates Types
export interface CommentTemplate {
  id: number;
  name: string;
  content: string;
  category: string;
  is_shared: boolean;
  usage_count: number;
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
}

// Comment Threads API
export const commentThreadsApi = {
  list: (params?: {
    project?: number;
    page?: number;
    status?: string;
    assigned_to?: number;
    ordering?: string;
  }) =>
    api.get<{ results: CommentThread[]; count: number }>(
      '/v1/commenting/threads/',
      { params }
    ),

  get: (threadId: number) =>
    api.get<CommentThread>(`/v1/commenting/threads/${threadId}/`),

  create: (data: {
    project: number;
    page?: number;
    element_id?: string;
    position_x: number;
    position_y: number;
    title?: string;
    priority?: string;
  }) =>
    api.post<CommentThread>('/v1/commenting/threads/', data),

  update: (threadId: number, data: Partial<CommentThread>) =>
    api.patch<CommentThread>(`/v1/commenting/threads/${threadId}/`, data),

  delete: (threadId: number) =>
    api.delete(`/v1/commenting/threads/${threadId}/`),

  resolve: (threadId: number) =>
    api.post<CommentThread>(`/v1/commenting/threads/${threadId}/resolve/`),

  reopen: (threadId: number) =>
    api.post<CommentThread>(`/v1/commenting/threads/${threadId}/reopen/`),

  assign: (threadId: number, userId: number) =>
    api.post<CommentThread>(`/v1/commenting/threads/${threadId}/assign/`, { user_id: userId }),

  unassign: (threadId: number) =>
    api.post<CommentThread>(`/v1/commenting/threads/${threadId}/unassign/`),
};

// Comments API
export const commentsApi = {
  list: (threadId: number) =>
    api.get<Comment[]>(`/v1/commenting/threads/${threadId}/comments/`),

  create: (threadId: number, data: {
    content: string;
    comment_type?: string;
    parent?: number;
    mentions?: number[];
    annotations?: AnnotationData[];
  }) =>
    api.post<Comment>(`/v1/commenting/threads/${threadId}/comments/`, data),

  createWithAttachment: (threadId: number, data: FormData) =>
    api.post<Comment>(`/v1/commenting/threads/${threadId}/comments/`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  update: (threadId: number, commentId: number, data: { content: string }) =>
    api.patch<Comment>(`/v1/commenting/threads/${threadId}/comments/${commentId}/`, data),

  delete: (threadId: number, commentId: number) =>
    api.delete(`/v1/commenting/threads/${threadId}/comments/${commentId}/`),

  addReaction: (threadId: number, commentId: number, emoji: string) =>
    api.post(`/v1/commenting/threads/${threadId}/comments/${commentId}/react/`, { emoji }),

  removeReaction: (threadId: number, commentId: number, emoji: string) =>
    api.delete(`/v1/commenting/threads/${threadId}/comments/${commentId}/react/`, {
      data: { emoji }
    }),
};

// Review Sessions API
export const reviewSessionsApi = {
  list: (params?: { project?: number; status?: string }) =>
    api.get<ReviewSession[]>('/v1/commenting/reviews/', { params }),

  get: (reviewId: number) =>
    api.get<ReviewSession>(`/v1/commenting/reviews/${reviewId}/`),

  create: (data: {
    project: number;
    name: string;
    description?: string;
    due_date?: string;
    reviewers: number[];
  }) =>
    api.post<ReviewSession>('/v1/commenting/reviews/', data),

  update: (reviewId: number, data: Partial<ReviewSession>) =>
    api.patch<ReviewSession>(`/v1/commenting/reviews/${reviewId}/`, data),

  delete: (reviewId: number) =>
    api.delete(`/v1/commenting/reviews/${reviewId}/`),

  addReviewer: (reviewId: number, userId: number) =>
    api.post(`/v1/commenting/reviews/${reviewId}/add-reviewer/`, { user_id: userId }),

  removeReviewer: (reviewId: number, userId: number) =>
    api.post(`/v1/commenting/reviews/${reviewId}/remove-reviewer/`, { user_id: userId }),

  submitFeedback: (reviewId: number, data: { status: string; feedback?: string }) =>
    api.post(`/v1/commenting/reviews/${reviewId}/submit-feedback/`, data),
};

// Comment Notifications API
export const commentNotificationsApi = {
  list: () =>
    api.get<CommentNotification[]>('/v1/commenting/notifications/'),

  markRead: (notificationId: number) =>
    api.post(`/v1/commenting/notifications/${notificationId}/read/`),

  markAllRead: () =>
    api.post('/v1/commenting/notifications/mark-all-read/'),

  getUnreadCount: () =>
    api.get<{ count: number }>('/v1/commenting/notifications/unread-count/'),
};

// Comment Templates API
export const commentTemplatesApi = {
  list: () =>
    api.get<CommentTemplate[]>('/v1/commenting/templates/'),

  create: (data: { name: string; content: string; category: string; is_shared?: boolean }) =>
    api.post<CommentTemplate>('/v1/commenting/templates/', data),

  update: (templateId: number, data: Partial<CommentTemplate>) =>
    api.patch<CommentTemplate>(`/v1/commenting/templates/${templateId}/`, data),

  delete: (templateId: number) =>
    api.delete(`/v1/commenting/templates/${templateId}/`),
};

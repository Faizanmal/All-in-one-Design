// API service for AI chat assistant
import api from './api';

// Chat Types
export interface ChatConversation {
  id: number;
  title: string;
  user: number;
  project?: number;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  conversation: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, unknown>;
  created_at: string;
}

export interface AIFeedback {
  id: number;
  message: number;
  rating: 1 | 2 | 3 | 4 | 5;
  comment?: string;
  created_at: string;
}

// Chat API
export const chatApi = {
  // List conversations
  list: (projectId?: number) => {
    const url = projectId 
      ? `/v1/ai/chat/?project=${projectId}`
      : '/v1/ai/chat/';
    return api.get<ChatConversation[]>(url);
  },
  
  // Create conversation
  create: (data: { title?: string; project?: number }) => 
    api.post<ChatConversation>('/v1/ai/chat/', data),
  
  // Get conversation details
  get: (conversationId: number) => 
    api.get<ChatConversation>(`/v1/ai/chat/${conversationId}/`),
  
  // Update conversation
  update: (conversationId: number, data: { title: string }) => 
    api.patch<ChatConversation>(`/v1/ai/chat/${conversationId}/`, data),
  
  // Delete conversation
  delete: (conversationId: number) => 
    api.delete(`/v1/ai/chat/${conversationId}/`),
  
  // Send message
  sendMessage: (conversationId: number, message: string) => 
    api.post<ChatMessage>(`/v1/ai/chat/${conversationId}/send_message/`, { message }),
  
  // Get messages
  getMessages: (conversationId: number) => 
    api.get<ChatMessage[]>(`/v1/ai/chat/${conversationId}/messages/`),
};

// Feedback API
export const feedbackApi = {
  // Submit feedback
  create: (data: { message: number; rating: number; comment?: string }) => 
    api.post<AIFeedback>('/v1/ai/feedback/', data),
  
  // Update feedback
  update: (feedbackId: number, data: Partial<AIFeedback>) => 
    api.patch<AIFeedback>(`/v1/ai/feedback/${feedbackId}/`, data),
  
  // Delete feedback
  delete: (feedbackId: number) => 
    api.delete(`/v1/ai/feedback/${feedbackId}/`),
};

const aiChatApi = {
  chat: chatApi,
  feedback: feedbackApi,
};

export default aiChatApi;

// API service for team collaboration features (tasks and chat)
import api from './api';

// Task Types
export interface Task {
  id: number;
  team: number;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'review' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigned_to?: {
    id: number;
    username: string;
    email: string;
  };
  created_by: {
    id: number;
    username: string;
  };
  due_date?: string;
  project?: number;
  created_at: string;
  updated_at: string;
}

// Team Chat Types
export interface TeamChat {
  id: number;
  team: number;
  name: string;
  description?: string;
  is_private: boolean;
  created_by: {
    id: number;
    username: string;
  };
  member_count: number;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  chat: number;
  user: {
    id: number;
    username: string;
  };
  content: string;
  parent?: number;
  reactions: {
    emoji: string;
    users: number[];
  }[];
  is_edited: boolean;
  created_at: string;
  updated_at: string;
}

// Tasks API
export const tasksApi = {
  // List tasks
  list: (teamId?: number, params?: {
    status?: string;
    priority?: string;
    assigned_to?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (teamId) queryParams.append('team', teamId.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.priority) queryParams.append('priority', params.priority);
    if (params?.assigned_to) queryParams.append('assigned_to', params.assigned_to.toString());
    
    return api.get<Task[]>(`/v1/teams/tasks/?${queryParams.toString()}`);
  },
  
  // Create task
  create: (data: {
    team: number;
    title: string;
    description?: string;
    priority?: string;
    assigned_to?: number;
    due_date?: string;
    project?: number;
  }) => api.post<Task>('/v1/teams/tasks/', data),
  
  // Get task details
  get: (taskId: number) => api.get<Task>(`/v1/teams/tasks/${taskId}/`),
  
  // Update task
  update: (taskId: number, data: Partial<Task>) => 
    api.patch<Task>(`/v1/teams/tasks/${taskId}/`, data),
  
  // Delete task
  delete: (taskId: number) => api.delete(`/v1/teams/tasks/${taskId}/`),
  
  // Assign task
  assign: (taskId: number, userId: number) => 
    api.post(`/v1/teams/tasks/${taskId}/assign/`, { user_id: userId }),
  
  // Update task status
  updateStatus: (taskId: number, status: string) => 
    api.post(`/v1/teams/tasks/${taskId}/update_status/`, { status }),
};

// Team Chat API
export const teamChatApi = {
  // List chats
  list: (teamId?: number) => {
    const url = teamId 
      ? `/v1/teams/chats/?team=${teamId}`
      : '/v1/teams/chats/';
    return api.get<TeamChat[]>(url);
  },
  
  // Create chat room
  create: (data: {
    team: number;
    name: string;
    description?: string;
    is_private?: boolean;
  }) => api.post<TeamChat>('/v1/teams/chats/', data),
  
  // Get chat details
  get: (chatId: number) => api.get<TeamChat>(`/v1/teams/chats/${chatId}/`),
  
  // Update chat
  update: (chatId: number, data: Partial<TeamChat>) => 
    api.patch<TeamChat>(`/v1/teams/chats/${chatId}/`, data),
  
  // Delete chat
  delete: (chatId: number) => api.delete(`/v1/teams/chats/${chatId}/`),
  
  // Send message
  sendMessage: (chatId: number, content: string, parentId?: number) => 
    api.post(`/v1/teams/chats/${chatId}/send_message/`, { 
      content, 
      parent: parentId 
    }),
  
  // Get messages
  getMessages: (chatId: number) => 
    api.get<ChatMessage[]>(`/v1/teams/chats/${chatId}/messages/`),
  
  // Add member to chat
  addMember: (chatId: number, userId: number) => 
    api.post(`/v1/teams/chats/${chatId}/add_member/`, { user_id: userId }),
  
  // Remove member from chat
  removeMember: (chatId: number, userId: number) => 
    api.post(`/v1/teams/chats/${chatId}/remove_member/`, { user_id: userId }),
};

// Chat Messages API
export const chatMessagesApi = {
  // Get message
  get: (messageId: number) => 
    api.get<ChatMessage>(`/v1/teams/messages/${messageId}/`),
  
  // Edit message
  edit: (messageId: number, content: string) => 
    api.patch<ChatMessage>(`/v1/teams/messages/${messageId}/`, { content }),
  
  // Delete message
  delete: (messageId: number) => 
    api.delete(`/v1/teams/messages/${messageId}/`),
  
  // Add reaction
  addReaction: (messageId: number, emoji: string) => 
    api.post(`/v1/teams/messages/${messageId}/add_reaction/`, { emoji }),
  
  // Remove reaction
  removeReaction: (messageId: number, emoji: string) => 
    api.post(`/v1/teams/messages/${messageId}/remove_reaction/`, { emoji }),
};

const collaborationApi = {
  tasks: tasksApi,
  teamChat: teamChatApi,
  messages: chatMessagesApi,
};

export default collaborationApi;

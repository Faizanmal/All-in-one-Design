/**
 * Whiteboard/FigJam API Client
 * Production-ready API for collaborative whiteboarding feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/whiteboard`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type CollaboratorRole = 'viewer' | 'editor' | 'admin';
export type ShapeType = 'rectangle' | 'ellipse' | 'triangle' | 'diamond' | 'star' | 'arrow' | 
                        'line' | 'polygon' | 'freeform';
export type ConnectorType = 'straight' | 'elbow' | 'curved';
export type ConnectorEndpoint = 'none' | 'arrow' | 'dot' | 'diamond' | 'square';

export interface WhiteboardCollaborator {
  id: string;
  whiteboard: string;
  user: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  role: CollaboratorRole;
  cursor_color: string;
  last_x: number | null;
  last_y: number | null;
  last_zoom: number | null;
  invited_by: number | null;
  joined_at: string;
  last_active: string;
  is_online: boolean;
}

export interface Whiteboard {
  id: string;
  team: number | null;
  project: number | null;
  name: string;
  description: string;
  owner: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  thumbnail_url: string | null;
  canvas_width: number;
  canvas_height: number;
  background_color: string;
  grid_enabled: boolean;
  grid_size: number;
  snap_to_grid: boolean;
  zoom_level: number;
  viewport_x: number;
  viewport_y: number;
  is_public: boolean;
  share_link: string | null;
  allow_guest_editing: boolean;
  collaborators: WhiteboardCollaborator[];
  is_archived: boolean;
  is_template: boolean;
  tags: string[];
  last_activity: string;
  created_at: string;
  updated_at: string;
}

export interface StickyNote {
  id: string;
  whiteboard: string;
  created_by: {
    id: number;
    username: string;
  };
  content: string;
  color: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  rotation: number;
  font_size: number;
  text_align: 'left' | 'center' | 'right';
  is_locked: boolean;
  vote_count: number;
  has_voted: boolean;
  group: string | null;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardShape {
  id: string;
  whiteboard: string;
  created_by: {
    id: number;
    username: string;
  };
  shape_type: ShapeType;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  rotation: number;
  fill_color: string;
  stroke_color: string;
  stroke_width: number;
  stroke_style: 'solid' | 'dashed' | 'dotted';
  corner_radius: number;
  opacity: number;
  points: Array<{ x: number; y: number }>;
  text_content: string;
  font_size: number;
  text_color: string;
  is_locked: boolean;
  group: string | null;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface Connector {
  id: string;
  whiteboard: string;
  created_by: number;
  connector_type: ConnectorType;
  start_node_id: string;
  start_node_type: string;
  end_node_id: string;
  end_node_type: string;
  start_position: 'top' | 'right' | 'bottom' | 'left' | 'center' | 'auto';
  end_position: 'top' | 'right' | 'bottom' | 'left' | 'center' | 'auto';
  start_offset_x: number;
  start_offset_y: number;
  end_offset_x: number;
  end_offset_y: number;
  control_points: Array<{ x: number; y: number }>;
  stroke_color: string;
  stroke_width: number;
  stroke_style: 'solid' | 'dashed' | 'dotted';
  start_cap: ConnectorEndpoint;
  end_cap: ConnectorEndpoint;
  label: string;
  label_position: number;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardText {
  id: string;
  whiteboard: string;
  created_by: number;
  content: string;
  position_x: number;
  position_y: number;
  width: number | null;
  height: number | null;
  font_family: string;
  font_size: number;
  font_weight: string;
  font_style: 'normal' | 'italic';
  text_color: string;
  text_align: 'left' | 'center' | 'right';
  line_height: number;
  letter_spacing: number;
  is_locked: boolean;
  group: string | null;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardImage {
  id: string;
  whiteboard: string;
  created_by: number;
  image_url: string;
  thumbnail_url: string | null;
  original_filename: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  rotation: number;
  opacity: number;
  border_radius: number;
  fit_mode: 'fill' | 'fit' | 'crop';
  is_locked: boolean;
  group: string | null;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardGroup {
  id: string;
  whiteboard: string;
  name: string;
  created_by: number;
  is_locked: boolean;
  z_index: number;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardSection {
  id: string;
  whiteboard: string;
  name: string;
  created_by: number;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  fill_color: string;
  is_collapsed: boolean;
  created_at: string;
  updated_at: string;
}

export interface Timer {
  id: string;
  whiteboard: string;
  created_by: number;
  name: string;
  duration_seconds: number;
  remaining_seconds: number;
  status: 'idle' | 'running' | 'paused' | 'completed';
  started_at: string | null;
  ended_at: string | null;
  position_x: number;
  position_y: number;
  is_visible: boolean;
  play_sound: boolean;
  created_at: string;
}

export interface WhiteboardComment {
  id: string;
  whiteboard: string;
  author: {
    id: number;
    username: string;
    avatar_url?: string;
  };
  content: string;
  position_x: number;
  position_y: number;
  target_node_id: string | null;
  target_node_type: string | null;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  replies: WhiteboardComment[];
  parent: string | null;
  created_at: string;
  updated_at: string;
}

export interface WhiteboardEmoji {
  id: string;
  whiteboard: string;
  created_by: number;
  emoji: string;
  position_x: number;
  position_y: number;
  size: number;
  created_at: string;
}

export interface WhiteboardTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnail_url: string | null;
  template_data: Record<string, unknown>;
  is_system: boolean;
  is_public: boolean;
  usage_count: number;
  created_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface CursorPosition {
  user_id: number;
  username: string;
  avatar_url?: string;
  cursor_color: string;
  x: number;
  y: number;
  last_updated: string;
}

export interface WhiteboardElements {
  sticky_notes: StickyNote[];
  shapes: WhiteboardShape[];
  connectors: Connector[];
  texts: WhiteboardText[];
  images: WhiteboardImage[];
  groups: WhiteboardGroup[];
  sections: WhiteboardSection[];
  emojis: WhiteboardEmoji[];
}

// API Functions
export const whiteboardApi = {
  // Whiteboard operations
  async getWhiteboards(options?: {
    team?: number;
    project?: number;
    search?: string;
    is_template?: boolean;
  }): Promise<Whiteboard[]> {
    const params = new URLSearchParams();
    if (options?.team) params.append('team', String(options.team));
    if (options?.project) params.append('project', String(options.project));
    if (options?.search) params.append('search', options.search);
    if (options?.is_template !== undefined) params.append('is_template', String(options.is_template));
    const { data } = await apiClient.get(`/whiteboards/?${params}`);
    return data.results || data;
  },

  async getWhiteboard(whiteboardId: string): Promise<Whiteboard> {
    const { data } = await apiClient.get(`/whiteboards/${whiteboardId}/`);
    return data;
  },

  async createWhiteboard(whiteboard: Partial<Whiteboard>): Promise<Whiteboard> {
    const { data } = await apiClient.post('/whiteboards/', whiteboard);
    return data;
  },

  async updateWhiteboard(whiteboardId: string, updates: Partial<Whiteboard>): Promise<Whiteboard> {
    const { data } = await apiClient.patch(`/whiteboards/${whiteboardId}/`, updates);
    return data;
  },

  async deleteWhiteboard(whiteboardId: string): Promise<void> {
    await apiClient.delete(`/whiteboards/${whiteboardId}/`);
  },

  async duplicateWhiteboard(whiteboardId: string, name?: string): Promise<Whiteboard> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/duplicate/`, { name });
    return data;
  },

  async getElements(whiteboardId: string): Promise<WhiteboardElements> {
    const { data } = await apiClient.get(`/whiteboards/${whiteboardId}/elements/`);
    return data;
  },

  async saveAsTemplate(whiteboardId: string, name: string, category?: string): Promise<WhiteboardTemplate> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/save_as_template/`, { name, category });
    return data;
  },

  async createFromTemplate(templateId: string, options: {
    name: string;
    team?: number;
    project?: number;
  }): Promise<Whiteboard> {
    const { data } = await apiClient.post(`/whiteboards/from_template/`, {
      template_id: templateId,
      ...options,
    });
    return data;
  },

  async archive(whiteboardId: string): Promise<Whiteboard> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/archive/`);
    return data;
  },

  async unarchive(whiteboardId: string): Promise<Whiteboard> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/unarchive/`);
    return data;
  },

  async generateShareLink(whiteboardId: string, options?: {
    allow_editing?: boolean;
    expires_in?: number;
  }): Promise<{ share_link: string }> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/share/`, options);
    return data;
  },

  async revokeShareLink(whiteboardId: string): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/revoke_share/`);
  },

  async exportAsImage(whiteboardId: string, format: 'png' | 'jpg' | 'svg' | 'pdf'): Promise<Blob> {
    const { data } = await apiClient.get(`/whiteboards/${whiteboardId}/export/?format=${format}`, {
      responseType: 'blob',
    });
    return data;
  },

  // Collaboration operations
  async joinWhiteboard(whiteboardId: string): Promise<{
    collaborator: WhiteboardCollaborator;
    cursor_color: string;
  }> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/join/`);
    return data;
  },

  async leaveWhiteboard(whiteboardId: string): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/leave/`);
  },

  async inviteCollaborator(whiteboardId: string, options: {
    user_id?: number;
    email?: string;
    role: CollaboratorRole;
  }): Promise<WhiteboardCollaborator> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/invite/`, options);
    return data;
  },

  async removeCollaborator(whiteboardId: string, collaboratorId: string): Promise<void> {
    await apiClient.delete(`/collaborators/${collaboratorId}/`);
  },

  async updateCollaboratorRole(collaboratorId: string, role: CollaboratorRole): Promise<WhiteboardCollaborator> {
    const { data } = await apiClient.patch(`/collaborators/${collaboratorId}/`, { role });
    return data;
  },

  async updateCursor(whiteboardId: string, position: { x: number; y: number; zoom?: number }): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/update_cursor/`, position);
  },

  async getActiveCursors(whiteboardId: string): Promise<CursorPosition[]> {
    const { data } = await apiClient.get(`/whiteboards/${whiteboardId}/cursors/`);
    return data;
  },

  // Sticky Note operations
  async getStickyNotes(whiteboardId: string): Promise<StickyNote[]> {
    const { data } = await apiClient.get(`/sticky-notes/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createStickyNote(stickyNote: Partial<StickyNote>): Promise<StickyNote> {
    const { data } = await apiClient.post('/sticky-notes/', stickyNote);
    return data;
  },

  async updateStickyNote(noteId: string, updates: Partial<StickyNote>): Promise<StickyNote> {
    const { data } = await apiClient.patch(`/sticky-notes/${noteId}/`, updates);
    return data;
  },

  async deleteStickyNote(noteId: string): Promise<void> {
    await apiClient.delete(`/sticky-notes/${noteId}/`);
  },

  async voteStickyNote(noteId: string): Promise<StickyNote> {
    const { data } = await apiClient.post(`/sticky-notes/${noteId}/vote/`);
    return data;
  },

  async unvoteStickyNote(noteId: string): Promise<StickyNote> {
    const { data } = await apiClient.post(`/sticky-notes/${noteId}/unvote/`);
    return data;
  },

  async toggleStickyNoteLock(noteId: string): Promise<StickyNote> {
    const { data } = await apiClient.post(`/sticky-notes/${noteId}/toggle_lock/`);
    return data;
  },

  // Shape operations
  async getShapes(whiteboardId: string): Promise<WhiteboardShape[]> {
    const { data } = await apiClient.get(`/shapes/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createShape(shape: Partial<WhiteboardShape>): Promise<WhiteboardShape> {
    const { data } = await apiClient.post('/shapes/', shape);
    return data;
  },

  async updateShape(shapeId: string, updates: Partial<WhiteboardShape>): Promise<WhiteboardShape> {
    const { data } = await apiClient.patch(`/shapes/${shapeId}/`, updates);
    return data;
  },

  async deleteShape(shapeId: string): Promise<void> {
    await apiClient.delete(`/shapes/${shapeId}/`);
  },

  async duplicateShape(shapeId: string): Promise<WhiteboardShape> {
    const { data } = await apiClient.post(`/shapes/${shapeId}/duplicate/`);
    return data;
  },

  // Connector operations
  async getConnectors(whiteboardId: string): Promise<Connector[]> {
    const { data } = await apiClient.get(`/connectors/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createConnector(connector: Partial<Connector>): Promise<Connector> {
    const { data } = await apiClient.post('/connectors/', connector);
    return data;
  },

  async updateConnector(connectorId: string, updates: Partial<Connector>): Promise<Connector> {
    const { data } = await apiClient.patch(`/connectors/${connectorId}/`, updates);
    return data;
  },

  async deleteConnector(connectorId: string): Promise<void> {
    await apiClient.delete(`/connectors/${connectorId}/`);
  },

  // Text operations
  async getTexts(whiteboardId: string): Promise<WhiteboardText[]> {
    const { data } = await apiClient.get(`/texts/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createText(text: Partial<WhiteboardText>): Promise<WhiteboardText> {
    const { data } = await apiClient.post('/texts/', text);
    return data;
  },

  async updateText(textId: string, updates: Partial<WhiteboardText>): Promise<WhiteboardText> {
    const { data } = await apiClient.patch(`/texts/${textId}/`, updates);
    return data;
  },

  async deleteText(textId: string): Promise<void> {
    await apiClient.delete(`/texts/${textId}/`);
  },

  // Image operations
  async getImages(whiteboardId: string): Promise<WhiteboardImage[]> {
    const { data } = await apiClient.get(`/images/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async uploadImage(whiteboardId: string, file: File, position?: { x: number; y: number }): Promise<WhiteboardImage> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('whiteboard', whiteboardId);
    if (position) {
      formData.append('position_x', String(position.x));
      formData.append('position_y', String(position.y));
    }
    const { data } = await apiClient.post('/images/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async updateImage(imageId: string, updates: Partial<WhiteboardImage>): Promise<WhiteboardImage> {
    const { data } = await apiClient.patch(`/images/${imageId}/`, updates);
    return data;
  },

  async deleteImage(imageId: string): Promise<void> {
    await apiClient.delete(`/images/${imageId}/`);
  },

  // Group operations
  async getGroups(whiteboardId: string): Promise<WhiteboardGroup[]> {
    const { data } = await apiClient.get(`/groups/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createGroup(group: {
    whiteboard: string;
    name: string;
    element_ids: string[];
  }): Promise<WhiteboardGroup> {
    const { data } = await apiClient.post('/groups/', group);
    return data;
  },

  async ungroupElements(groupId: string): Promise<void> {
    await apiClient.post(`/groups/${groupId}/ungroup/`);
  },

  async deleteGroup(groupId: string): Promise<void> {
    await apiClient.delete(`/groups/${groupId}/`);
  },

  // Section operations
  async getSections(whiteboardId: string): Promise<WhiteboardSection[]> {
    const { data } = await apiClient.get(`/sections/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createSection(section: Partial<WhiteboardSection>): Promise<WhiteboardSection> {
    const { data } = await apiClient.post('/sections/', section);
    return data;
  },

  async updateSection(sectionId: string, updates: Partial<WhiteboardSection>): Promise<WhiteboardSection> {
    const { data } = await apiClient.patch(`/sections/${sectionId}/`, updates);
    return data;
  },

  async deleteSection(sectionId: string): Promise<void> {
    await apiClient.delete(`/sections/${sectionId}/`);
  },

  async toggleSectionCollapse(sectionId: string): Promise<WhiteboardSection> {
    const { data } = await apiClient.post(`/sections/${sectionId}/toggle_collapse/`);
    return data;
  },

  // Timer operations
  async getTimers(whiteboardId: string): Promise<Timer[]> {
    const { data } = await apiClient.get(`/timers/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createTimer(timer: Partial<Timer>): Promise<Timer> {
    const { data } = await apiClient.post('/timers/', timer);
    return data;
  },

  async startTimer(timerId: string): Promise<Timer> {
    const { data } = await apiClient.post(`/timers/${timerId}/start/`);
    return data;
  },

  async pauseTimer(timerId: string): Promise<Timer> {
    const { data } = await apiClient.post(`/timers/${timerId}/pause/`);
    return data;
  },

  async resumeTimer(timerId: string): Promise<Timer> {
    const { data } = await apiClient.post(`/timers/${timerId}/resume/`);
    return data;
  },

  async resetTimer(timerId: string): Promise<Timer> {
    const { data } = await apiClient.post(`/timers/${timerId}/reset/`);
    return data;
  },

  async deleteTimer(timerId: string): Promise<void> {
    await apiClient.delete(`/timers/${timerId}/`);
  },

  // Comment operations
  async getComments(whiteboardId: string): Promise<WhiteboardComment[]> {
    const { data } = await apiClient.get(`/comments/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async createComment(comment: Partial<WhiteboardComment>): Promise<WhiteboardComment> {
    const { data } = await apiClient.post('/comments/', comment);
    return data;
  },

  async updateComment(commentId: string, content: string): Promise<WhiteboardComment> {
    const { data } = await apiClient.patch(`/comments/${commentId}/`, { content });
    return data;
  },

  async deleteComment(commentId: string): Promise<void> {
    await apiClient.delete(`/comments/${commentId}/`);
  },

  async resolveComment(commentId: string): Promise<WhiteboardComment> {
    const { data } = await apiClient.post(`/comments/${commentId}/resolve/`);
    return data;
  },

  async unresolveComment(commentId: string): Promise<WhiteboardComment> {
    const { data } = await apiClient.post(`/comments/${commentId}/unresolve/`);
    return data;
  },

  async replyToComment(commentId: string, content: string): Promise<WhiteboardComment> {
    const { data } = await apiClient.post(`/comments/${commentId}/reply/`, { content });
    return data;
  },

  // Emoji operations
  async getEmojis(whiteboardId: string): Promise<WhiteboardEmoji[]> {
    const { data } = await apiClient.get(`/emojis/?whiteboard=${whiteboardId}`);
    return data.results || data;
  },

  async addEmoji(emoji: Partial<WhiteboardEmoji>): Promise<WhiteboardEmoji> {
    const { data } = await apiClient.post('/emojis/', emoji);
    return data;
  },

  async deleteEmoji(emojiId: string): Promise<void> {
    await apiClient.delete(`/emojis/${emojiId}/`);
  },

  // Template operations
  async getTemplates(category?: string): Promise<WhiteboardTemplate[]> {
    const params = category ? `?category=${category}` : '';
    const { data } = await apiClient.get(`/templates/${params}`);
    return data.results || data;
  },

  async getTemplate(templateId: string): Promise<WhiteboardTemplate> {
    const { data } = await apiClient.get(`/templates/${templateId}/`);
    return data;
  },

  async deleteTemplate(templateId: string): Promise<void> {
    await apiClient.delete(`/templates/${templateId}/`);
  },

  // Bulk operations
  async bulkUpdateElements(whiteboardId: string, updates: Array<{
    element_type: 'sticky_note' | 'shape' | 'text' | 'image' | 'connector';
    element_id: string;
    changes: Record<string, unknown>;
  }>): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/bulk_update/`, { updates });
  },

  async bulkDeleteElements(whiteboardId: string, elements: Array<{
    element_type: string;
    element_id: string;
  }>): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/bulk_delete/`, { elements });
  },

  async copyElements(whiteboardId: string, elements: Array<{
    element_type: string;
    element_id: string;
  }>): Promise<{
    copied_elements: Array<{
      original_id: string;
      new_id: string;
      element_type: string;
    }>;
  }> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/copy_elements/`, { elements });
    return data;
  },

  async bringToFront(whiteboardId: string, elementType: string, elementId: string): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/bring_to_front/`, {
      element_type: elementType,
      element_id: elementId,
    });
  },

  async sendToBack(whiteboardId: string, elementType: string, elementId: string): Promise<void> {
    await apiClient.post(`/whiteboards/${whiteboardId}/send_to_back/`, {
      element_type: elementType,
      element_id: elementId,
    });
  },

  // Undo/Redo operations
  async getHistory(whiteboardId: string, limit?: number): Promise<Array<{
    id: string;
    action: string;
    element_type: string;
    element_id: string;
    before: Record<string, unknown>;
    after: Record<string, unknown>;
    user: { id: number; username: string };
    created_at: string;
  }>> {
    const params = limit ? `?limit=${limit}` : '';
    const { data } = await apiClient.get(`/whiteboards/${whiteboardId}/history/${params}`);
    return data;
  },

  async undo(whiteboardId: string): Promise<{ undone: boolean; action: string }> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/undo/`);
    return data;
  },

  async redo(whiteboardId: string): Promise<{ redone: boolean; action: string }> {
    const { data } = await apiClient.post(`/whiteboards/${whiteboardId}/redo/`);
    return data;
  },
};

export default whiteboardApi;

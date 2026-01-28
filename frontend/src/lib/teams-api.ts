// API service for teams functionality
import api from './api';

export interface Team {
  id: number;
  name: string;
  slug: string;
  description: string;
  owner: {
    id: number;
    username: string;
    email: string;
  };
  member_count: number;
  project_count: number;
  is_active: boolean;
  created_at: string;
}

export interface TeamMember {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  role: 'owner' | 'admin' | 'member' | 'viewer';
  role_display: string;
  can_create_projects: boolean;
  can_edit_projects: boolean;
  can_delete_projects: boolean;
  can_invite_members: boolean;
  can_manage_members: boolean;
  joined_at: string;
}

export interface TeamInvitation {
  id: number;
  team: number;
  team_name: string;
  email: string;
  invited_by_name: string;
  role: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  message: string;
  created_at: string;
  expires_at: string;
}

export interface Comment {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  };
  content: string;
  parent: number | null;
  position_x: number | null;
  position_y: number | null;
  is_resolved: boolean;
  resolved_by: number | null;
  resolved_at: string | null;
  reply_count: number;
  mentions: string[];
  replies: Comment[];
  created_at: string;
  updated_at: string;
  author_name?: string;
}

export interface TeamActivity {
  id: number;
  user: {
    id: number;
    username: string;
  };
  action: string;
  action_display: string;
  project_name: string | null;
  description: string;
  created_at: string;
  details?: Record<string, unknown>;
  actor_name?: string;
}

class TeamsAPI {
  // Teams
  async getTeams() {
    const response = await api.get('/teams/teams/');
    return response.data;
  }

  async createTeam(data: { name: string; slug: string; description?: string; max_members?: number }) {
    const response = await api.post('/teams/teams/', data);
    return response.data;
  }

  async getTeam(id: number) {
    const response = await api.get(`/teams/teams/${id}/`);
    return response.data;
  }

  async updateTeam(id: number, data: Partial<Team>) {
    const response = await api.patch(`/teams/teams/${id}/`, data);
    return response.data;
  }

  async deleteTeam(id: number) {
    await api.delete(`/teams/teams/${id}/`);
  }

  // Team Members
  async getTeamMembers(teamId: number) {
    const response = await api.get(`/teams/teams/${teamId}/members/`);
    return response.data;
  }

  async inviteMember(teamId: number, data: { email: string; role: string; message?: string }) {
    const response = await api.post(`/teams/teams/${teamId}/invite_member/`, data);
    return response.data;
  }

  async removeMember(teamId: number, userId: number) {
    const response = await api.post(`/teams/teams/${teamId}/remove_member/`, { user_id: userId });
    return response.data;
  }

  async updateMemberRole(teamId: number, userId: number, role: string) {
    const response = await api.post(`/teams/teams/${teamId}/update_member_role/`, {
      user_id: userId,
      role: role
    });
    return response.data;
  }

  // Team Projects
  async getTeamProjects(teamId: number) {
    const response = await api.get(`/teams/teams/${teamId}/projects/`);
    return response.data;
  }

  async addProjectToTeam(teamId: number, projectId: number) {
    const response = await api.post(`/teams/teams/${teamId}/add_project/`, { project_id: projectId });
    return response.data;
  }

  // Team Activity
  async getTeamActivity(teamId: number) {
    const response = await api.get(`/teams/teams/${teamId}/activity/`);
    return response.data;
  }

  // Invitations
  async getInvitations() {
    const response = await api.get('/teams/invitations/');
    return response.data;
  }

  async acceptInvitation(invitationId: number) {
    const response = await api.post(`/teams/invitations/${invitationId}/accept/`);
    return response.data;
  }

  async declineInvitation(invitationId: number) {
    const response = await api.post(`/teams/invitations/${invitationId}/decline/`);
    return response.data;
  }

  // Comments
  async getComments(projectId: number) {
    const response = await api.get(`/teams/comments/?project_id=${projectId}`);
    return response.data;
  }

  async createComment(projectId: number, data: {
    content: string;
    parent?: number;
    position_x?: number;
    position_y?: number;
    mention_usernames?: string[];
  }) {
    const response = await api.post('/teams/comments/', { ...data, project_id: projectId });
    return response.data;
  }

  async resolveComment(commentId: number) {
    const response = await api.post(`/teams/comments/${commentId}/resolve/`);
    return response.data;
  }

  async deleteComment(commentId: number) {
    await api.delete(`/teams/comments/${commentId}/`);
  }

  async getCommentReplies(commentId: number) {
    const response = await api.get(`/teams/comments/${commentId}/replies/`);
    return response.data;
  }
}

export const teamsAPI = new TeamsAPI();

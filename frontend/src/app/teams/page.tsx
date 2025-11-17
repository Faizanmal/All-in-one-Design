'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { teamsAPI, Team, TeamMember, TeamInvitation } from '@/lib/teams-api';
import { Users, Plus, Mail, Settings, Shield, Eye, UserPlus } from 'lucide-react';

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);

  const loadTeamMembers = async (teamId: number) => {
    try {
      const data = await teamsAPI.getTeamMembers(teamId);
      setMembers(data);
    } catch (error) {
      console.error('Failed to load team members:', error);
    }
  };

  const loadTeams = useCallback(async () => {
    try {
      const data = await teamsAPI.getTeams();
      setTeams(data.results || data);
      if (data.results?.length > 0 || data.length > 0) {
        const firstTeam = data.results?.[0] || data[0];
        setSelectedTeam(firstTeam);
        loadTeamMembers(firstTeam.id);
      }
    } catch (error) {
      console.error('Failed to load teams:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadInvitations = useCallback(async () => {
    try {
      const data = await teamsAPI.getInvitations();
      setInvitations(data.results || data);
    } catch (error) {
      console.error('Failed to load invitations:', error);
    }
  }, []);

  useEffect(() => {
    loadTeams();
    loadInvitations();
  }, [loadTeams, loadInvitations]);

  const handleCreateTeam = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      const newTeam = await teamsAPI.createTeam({
        name: formData.get('name') as string,
        slug: (formData.get('name') as string).toLowerCase().replace(/\s+/g, '-'),
        description: formData.get('description') as string,
      });
      
      setTeams([newTeam, ...teams]);
      setShowCreateModal(false);
      setSelectedTeam(newTeam);
    } catch (error) {
      console.error('Failed to create team:', error);
    }
  };

  const handleInviteMember = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!selectedTeam) return;
    
    const formData = new FormData(e.currentTarget);
    
    try {
      await teamsAPI.inviteMember(selectedTeam.id, {
        email: formData.get('email') as string,
        role: formData.get('role') as string,
        message: formData.get('message') as string,
      });
      
      setShowInviteModal(false);
      alert('Invitation sent successfully!');
    } catch (error) {
      console.error('Failed to invite member:', error);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner': return <Shield className="w-4 h-4 text-purple-500" />;
      case 'admin': return <Settings className="w-4 h-4 text-blue-500" />;
      case 'member': return <Users className="w-4 h-4 text-green-500" />;
      case 'viewer': return <Eye className="w-4 h-4 text-gray-500" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner': return 'bg-purple-100 text-purple-700';
      case 'admin': return 'bg-blue-100 text-blue-700';
      case 'member': return 'bg-green-100 text-green-700';
      case 'viewer': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading teams...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                Teams
              </h1>
              <p className="text-gray-600 mt-2">Collaborate with your team members</p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              Create Team
            </button>
          </div>
        </motion.div>

        {/* Pending Invitations */}
        {invitations.filter(inv => inv.status === 'pending').length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <Mail className="w-5 h-5 text-yellow-600" />
              <h3 className="font-semibold text-yellow-800">Pending Invitations</h3>
            </div>
            <div className="space-y-2">
              {invitations.filter(inv => inv.status === 'pending').map(inv => (
                <div key={inv.id} className="flex items-center justify-between bg-white p-3 rounded">
                  <div>
                    <p className="font-medium">{inv.team_name}</p>
                    <p className="text-sm text-gray-600">Invited by {inv.invited_by_name} as {inv.role}</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={async () => {
                        await teamsAPI.acceptInvitation(inv.id);
                        loadTeams();
                        loadInvitations();
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                    >
                      Accept
                    </button>
                    <button
                      onClick={async () => {
                        await teamsAPI.declineInvitation(inv.id);
                        loadInvitations();
                      }}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                    >
                      Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Teams List */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-1"
          >
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold mb-4">Your Teams</h2>
              <div className="space-y-3">
                {teams.map((team) => (
                  <button
                    key={team.id}
                    onClick={() => {
                      setSelectedTeam(team);
                      loadTeamMembers(team.id);
                    }}
                    className={`w-full text-left p-4 rounded-lg transition-all ${
                      selectedTeam?.id === team.id
                        ? 'bg-gradient-to-r from-purple-100 to-blue-100 border-2 border-purple-300'
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{team.name}</h3>
                        <p className="text-sm text-gray-600">
                          {team.member_count} members · {team.project_count} projects
                        </p>
                      </div>
                      <Users className="w-5 h-5 text-gray-400" />
                    </div>
                  </button>
                ))}

                {teams.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No teams yet</p>
                    <p className="text-sm">Create your first team to get started</p>
                  </div>
                )}
              </div>
            </div>
          </motion.div>

          {/* Team Details */}
          {selectedTeam && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="lg:col-span-2"
            >
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold">{selectedTeam.name}</h2>
                    <p className="text-gray-600 mt-1">{selectedTeam.description}</p>
                  </div>
                  <button
                    onClick={() => setShowInviteModal(true)}
                    className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <UserPlus className="w-4 h-4" />
                    Invite
                  </button>
                </div>

                {/* Members List */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Team Members ({members.length})</h3>
                  <div className="space-y-3">
                    {members.map((member) => (
                      <div
                        key={member.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-400 to-blue-400 flex items-center justify-center text-white font-semibold">
                            {member.user.username[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="font-medium">{member.user.username}</p>
                            <p className="text-sm text-gray-600">{member.user.email}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getRoleBadgeColor(member.role)}`}>
                            {getRoleIcon(member.role)}
                            {member.role_display}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Create Team Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 max-w-md w-full"
          >
            <h2 className="text-2xl font-bold mb-4">Create New Team</h2>
            <form onSubmit={handleCreateTeam} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Team Name</label>
                <input
                  type="text"
                  name="name"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="My Awesome Team"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  name="description"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="What's this team about?"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Create Team
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteModal && selectedTeam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-6 max-w-md w-full"
          >
            <h2 className="text-2xl font-bold mb-4">Invite Team Member</h2>
            <form onSubmit={handleInviteMember} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="colleague@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Role</label>
                <select
                  name="role"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  <option value="member">Member</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Message (Optional)</label>
                <textarea
                  name="message"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  placeholder="Join our team!"
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Send Invitation
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
}

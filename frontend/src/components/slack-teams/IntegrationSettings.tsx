'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  MessageSquare, Bell, Settings, Link2, Unlink,
  Hash, Search, Send, Check, X, RefreshCw,
  Slack, Users, AtSign, Filter
} from 'lucide-react';

// Types
interface SlackWorkspace {
  id: string;
  teamId: string;
  teamName: string;
  isConnected: boolean;
  connectedAt: string;
  botUserId: string;
}

interface TeamsWorkspace {
  id: string;
  tenantId: string;
  name: string;
  isConnected: boolean;
  connectedAt: string;
}

interface IntegrationChannel {
  id: string;
  name: string;
  platform: 'slack' | 'teams';
  projectId: string | null;
  notificationsEnabled: boolean;
}

interface NotificationPreference {
  type: string;
  label: string;
  enabled: boolean;
  channels: string[];
}

// Slack Integration Component
export function SlackIntegration() {
  const [workspace, setWorkspace] = useState<SlackWorkspace | null>(null);
  const [channels, setChannels] = useState<IntegrationChannel[]>([]);
  const [isConnecting, setIsConnecting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const connectSlack = useCallback(async () => {
    setIsConnecting(true);
    
    // Redirect to Slack OAuth
    const clientId = process.env.NEXT_PUBLIC_SLACK_CLIENT_ID;
    const redirectUri = `${window.location.origin}/api/integrations/slack/callback`;
    const scope = 'channels:read,chat:write,commands,users:read';
    
    window.location.href = `https://slack.com/oauth/v2/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  }, []);

  const disconnectSlack = useCallback(async () => {
    try {
      await fetch('/api/v1/slack-teams/slack/disconnect/', {
        method: 'POST',
      });
      setWorkspace(null);
      setChannels([]);
    } catch (error) {
      console.error('Failed to disconnect', error);
    }
  }, []);

  const toggleChannel = useCallback(async (channelId: string, enabled: boolean) => {
    setChannels(prev =>
      prev.map(ch =>
        ch.id === channelId ? { ...ch, notificationsEnabled: enabled } : ch
      )
    );
    
    try {
      await fetch(`/api/v1/slack-teams/channels/${channelId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notifications_enabled: enabled }),
      });
    } catch (error) {
      console.error('Failed to update channel', error);
    }
  }, []);

  useEffect(() => {
    // Check connection status
    const checkStatus = async () => {
      try {
        const response = await fetch('/api/v1/slack-teams/slack/workspaces/');
        const data = await response.json();
        if (data.length > 0) {
          setWorkspace(data[0]);
          // Load channels
          const chResponse = await fetch('/api/v1/slack-teams/slack/channels/');
          const chData = await chResponse.json();
          setChannels(chData);
        }
      } catch (error) {
        console.error('Failed to check status', error);
      }
    };
    checkStatus();
  }, []);

  const filteredChannels = channels.filter(ch =>
    ch.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-gray-900 rounded-xl p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-[#4A154B] rounded-xl flex items-center justify-center">
            <Slack className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Slack Integration</h3>
            <p className="text-sm text-gray-400">
              {workspace ? `Connected to ${workspace.teamName}` : 'Not connected'}
            </p>
          </div>
        </div>
        
        {workspace ? (
          <button
            onClick={disconnectSlack}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
          >
            <Unlink className="w-4 h-4" />
            Disconnect
          </button>
        ) : (
          <button
            onClick={connectSlack}
            disabled={isConnecting}
            className="flex items-center gap-2 px-4 py-2 bg-[#4A154B] hover:bg-[#611f69] rounded-lg"
          >
            {isConnecting ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Link2 className="w-4 h-4" />
            )}
            Connect Slack
          </button>
        )}
      </div>

      {workspace && (
        <>
          {/* Channel Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search channels..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg"
            />
          </div>

          {/* Channels List */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {filteredChannels.map((channel) => (
              <div
                key={channel.id}
                className="flex items-center justify-between p-3 bg-gray-800 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Hash className="w-4 h-4 text-gray-400" />
                  <span>{channel.name}</span>
                  {channel.projectId && (
                    <span className="px-2 py-0.5 text-xs bg-blue-600 rounded">
                      Linked
                    </span>
                  )}
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={channel.notificationsEnabled}
                    onChange={(e) => toggleChannel(channel.id, e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-600 peer-checked:bg-green-600 rounded-full peer-focus:ring-2 peer-focus:ring-green-300 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full" />
                </label>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// Microsoft Teams Integration Component
export function TeamsIntegration() {
  const [workspace, setWorkspace] = useState<TeamsWorkspace | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  const connectTeams = useCallback(async () => {
    setIsConnecting(true);
    
    // Redirect to Microsoft OAuth
    const clientId = process.env.NEXT_PUBLIC_TEAMS_CLIENT_ID;
    const redirectUri = `${window.location.origin}/api/integrations/teams/callback`;
    const scope = 'ChannelMessage.Send,Team.ReadBasic.All,Channel.ReadBasic.All';
    
    window.location.href = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=code`;
  }, []);

  return (
    <div className="bg-gray-900 rounded-xl p-6 text-white">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-[#6264A7] rounded-xl flex items-center justify-center">
            <Users className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">Microsoft Teams</h3>
            <p className="text-sm text-gray-400">
              {workspace ? `Connected to ${workspace.name}` : 'Not connected'}
            </p>
          </div>
        </div>
        
        <button
          onClick={connectTeams}
          disabled={isConnecting}
          className="flex items-center gap-2 px-4 py-2 bg-[#6264A7] hover:bg-[#7678B7] rounded-lg"
        >
          {isConnecting ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Link2 className="w-4 h-4" />
          )}
          Connect Teams
        </button>
      </div>

      {workspace && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <p className="text-sm text-gray-400">
            Teams integration active. Configure notification channels in Teams settings.
          </p>
        </div>
      )}
    </div>
  );
}

// Notification Preferences Component
export function NotificationPreferences() {
  const [preferences, setPreferences] = useState<NotificationPreference[]>([
    { type: 'comment', label: 'New Comments', enabled: true, channels: ['slack'] },
    { type: 'mention', label: 'Mentions', enabled: true, channels: ['slack', 'teams'] },
    { type: 'share', label: 'Design Shared', enabled: true, channels: ['slack'] },
    { type: 'export', label: 'Export Complete', enabled: false, channels: [] },
    { type: 'approval', label: 'Approval Requests', enabled: true, channels: ['teams'] },
    { type: 'update', label: 'Design Updates', enabled: false, channels: [] },
  ]);

  const togglePreference = (type: string, enabled: boolean) => {
    setPreferences(prev =>
      prev.map(p => (p.type === type ? { ...p, enabled } : p))
    );
  };

  const toggleChannel = (type: string, channel: string) => {
    setPreferences(prev =>
      prev.map(p => {
        if (p.type !== type) return p;
        const channels = p.channels.includes(channel)
          ? p.channels.filter(c => c !== channel)
          : [...p.channels, channel];
        return { ...p, channels };
      })
    );
  };

  return (
    <div className="bg-gray-900 rounded-xl p-6 text-white">
      <div className="flex items-center gap-3 mb-6">
        <Bell className="w-5 h-5 text-blue-400" />
        <h3 className="font-semibold text-lg">Notification Preferences</h3>
      </div>

      <div className="space-y-4">
        {preferences.map((pref) => (
          <div key={pref.type} className="p-4 bg-gray-800 rounded-lg">
            <div className="flex items-center justify-between mb-3">
              <span className="font-medium">{pref.label}</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={pref.enabled}
                  onChange={(e) => togglePreference(pref.type, e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-600 peer-checked:bg-blue-600 rounded-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full" />
              </label>
            </div>
            
            {pref.enabled && (
              <div className="flex gap-2">
                <button
                  onClick={() => toggleChannel(pref.type, 'slack')}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded ${
                    pref.channels.includes('slack')
                      ? 'bg-[#4A154B] text-white'
                      : 'bg-gray-700 text-gray-400'
                  }`}
                >
                  <Slack className="w-4 h-4" />
                  Slack
                </button>
                <button
                  onClick={() => toggleChannel(pref.type, 'teams')}
                  className={`flex items-center gap-1 px-3 py-1.5 rounded ${
                    pref.channels.includes('teams')
                      ? 'bg-[#6264A7] text-white'
                      : 'bg-gray-700 text-gray-400'
                  }`}
                >
                  <Users className="w-4 h-4" />
                  Teams
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Share to Slack/Teams Dialog
export function ShareToChannelDialog({
  isOpen,
  onClose,
  projectId,
  projectName,
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  projectName: string;
}) {
  const [platform, setPlatform] = useState<'slack' | 'teams'>('slack');
  const [channel, setChannel] = useState('');
  const [message, setMessage] = useState(`Check out this design: ${projectName}`);
  const [isSending, setIsSending] = useState(false);
  const [channels, setChannels] = useState<IntegrationChannel[]>([]);

  useEffect(() => {
    // Load channels
    const loadChannels = async () => {
      try {
        const response = await fetch(`/api/v1/slack-teams/${platform}/channels/`);
        const data = await response.json();
        setChannels(data);
      } catch (error) {
        console.error('Failed to load channels', error);
      }
    };
    if (isOpen) {
      loadChannels();
    }
  }, [isOpen, platform]);

  const handleSend = async () => {
    setIsSending(true);
    try {
      await fetch(`/api/v1/slack-teams/${platform}/send-message/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          channel_id: channel,
          project_id: projectId,
          message,
        }),
      });
      onClose();
    } catch (error) {
      console.error('Failed to send', error);
    } finally {
      setIsSending(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-xl w-full max-w-md p-6 text-white">
        <div className="flex items-center justify-between mb-6">
          <h3 className="font-semibold text-lg">Share to Channel</h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Platform Selection */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setPlatform('slack')}
            className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg ${
              platform === 'slack' ? 'bg-[#4A154B]' : 'bg-gray-800'
            }`}
          >
            <Slack className="w-5 h-5" />
            Slack
          </button>
          <button
            onClick={() => setPlatform('teams')}
            className={`flex-1 flex items-center justify-center gap-2 p-3 rounded-lg ${
              platform === 'teams' ? 'bg-[#6264A7]' : 'bg-gray-800'
            }`}
          >
            <Users className="w-5 h-5" />
            Teams
          </button>
        </div>

        {/* Channel Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Channel
          </label>
          <select
            value={channel}
            onChange={(e) => setChannel(e.target.value)}
            className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg"
          >
            <option value="">Select a channel</option>
            {channels.map((ch) => (
              <option key={ch.id} value={ch.id}>
                #{ch.name}
              </option>
            ))}
          </select>
        </div>

        {/* Message */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Message
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg resize-none"
            placeholder="Add a message..."
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={!channel || isSending}
            className="flex-1 flex items-center justify-center gap-2 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
          >
            {isSending ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

// Integration Settings Page
export function IntegrationSettings() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white mb-8">Integration Settings</h1>
      
      <SlackIntegration />
      <TeamsIntegration />
      <NotificationPreferences />
    </div>
  );
}

export default IntegrationSettings;

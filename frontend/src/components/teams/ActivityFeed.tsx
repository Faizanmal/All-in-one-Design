'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { teamsAPI, TeamActivity } from '@/lib/teams-api';
import {
  Activity,
  FileText,
  UserPlus,
  UserMinus,
  MessageSquare,
  Download,
  Settings,
  Clock
} from 'lucide-react';

interface ActivityFeedProps {
  teamId: number;
  limit?: number;
}

export default function ActivityFeed({ teamId, limit = 20 }: ActivityFeedProps) {
  const [activities, setActivities] = useState<TeamActivity[]>([]);
  const [loading, setLoading] = useState(true);

  const loadActivities = useCallback(async () => {
    try {
      const data = await teamsAPI.getTeamActivity(teamId);
      const activityList = data.results || data;
      setActivities(activityList.slice(0, limit));
    } catch (error) {
      console.error('Failed to load activities:', error);
    } finally {
      setLoading(false);
    }
  }, [teamId, limit]);

  useEffect(() => {
    loadActivities();
    
    // Poll for new activities every 30 seconds
    const interval = setInterval(loadActivities, 30000);
    return () => clearInterval(interval);
  }, [loadActivities]);

  const getActivityIcon = (action: string) => {
    switch (action) {
      case 'project_created':
      case 'project_updated':
        return <FileText className="w-4 h-4" />;
      case 'member_joined':
      case 'member_invited':
        return <UserPlus className="w-4 h-4" />;
      case 'member_left':
      case 'member_removed':
        return <UserMinus className="w-4 h-4" />;
      case 'comment_added':
        return <MessageSquare className="w-4 h-4" />;
      case 'project_exported':
        return <Download className="w-4 h-4" />;
      case 'settings_changed':
        return <Settings className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getActivityColor = (action: string) => {
    switch (action) {
      case 'project_created':
        return 'bg-green-100 text-green-700';
      case 'project_updated':
        return 'bg-blue-100 text-blue-700';
      case 'member_joined':
      case 'member_invited':
        return 'bg-purple-100 text-purple-700';
      case 'member_left':
      case 'member_removed':
        return 'bg-red-100 text-red-700';
      case 'comment_added':
        return 'bg-yellow-100 text-yellow-700';
      case 'project_exported':
        return 'bg-indigo-100 text-indigo-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = (now.getTime() - date.getTime()) / (1000 * 60);

    if (diffInMinutes < 1) {
      return 'Just now';
    } else if (diffInMinutes < 60) {
      return `${Math.round(diffInMinutes)} minutes ago`;
    } else if (diffInMinutes < 1440) {
      const hours = Math.round(diffInMinutes / 60);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      const days = Math.round(diffInMinutes / 1440);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    }
  };

  const formatDescription = (activity: TeamActivity) => {
    const details = activity.details;
    let description = activity.description;

    // Replace placeholders with actual values from details
    if (details) {
      Object.keys(details).forEach(key => {
        description = description.replace(`{${key}}`, String(details[key]));
      });
    }

    return description;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold">Recent Activity</h3>
      </div>

      {activities.length > 0 ? (
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-start gap-4 pb-4 border-b last:border-b-0"
            >
              {/* Icon */}
              <div className={`p-2 rounded-lg ${getActivityColor(activity.action)}`}>
                {getActivityIcon(activity.action)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <p className="text-sm">
                      <span className="font-semibold">{activity.user.username}</span>
                      {' '}
                      <span className="text-gray-600">{formatDescription(activity)}</span>
                    </p>
                    {activity.project_name && (
                      <p className="text-sm text-purple-600 mt-1">
                        Project: {activity.project_name}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-500 whitespace-nowrap">
                    <Clock className="w-3 h-3" />
                    {formatDate(activity.created_at)}
                  </div>
                </div>

                {/* Additional details */}
                {activity.details && Object.keys(activity.details).length > 0 && (
                  <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
                    {Object.entries(activity.details).map(([key, value]) => (
                      <div key={key}>
                        <span className="font-medium">{key}:</span> {String(value)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <Activity className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No recent activity</p>
          <p className="text-sm">Team activities will appear here</p>
        </div>
      )}
    </div>
  );
}

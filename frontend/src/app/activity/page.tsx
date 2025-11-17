'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, 
  FileEdit, 
  Upload, 
  Download, 
  Trash2, 
  Share2, 
  Sparkles,
  User,
  Clock,
  Filter,
  Search
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

const activityTypes = {
  project_created: { icon: FileEdit, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  project_updated: { icon: FileEdit, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  project_deleted: { icon: Trash2, color: 'text-red-500', bg: 'bg-red-500/10' },
  asset_uploaded: { icon: Upload, color: 'text-green-500', bg: 'bg-green-500/10' },
  export_created: { icon: Download, color: 'text-orange-500', bg: 'bg-orange-500/10' },
  ai_generated: { icon: Sparkles, color: 'text-pink-500', bg: 'bg-pink-500/10' },
  project_shared: { icon: Share2, color: 'text-cyan-500', bg: 'bg-cyan-500/10' },
  login: { icon: User, color: 'text-gray-500', bg: 'bg-gray-500/10' }
};

const mockActivities = [
  {
    id: 1,
    type: 'ai_generated',
    title: 'Generated logo variations',
    description: 'Created 4 AI-powered logo designs for "TechStartup Inc"',
    timestamp: '2 minutes ago',
    user: { name: 'You', avatar: null },
    metadata: { tokens: 2500, cost: 0.08 }
  },
  {
    id: 2,
    type: 'project_created',
    title: 'Created new project',
    description: 'Modern Landing Page',
    timestamp: '15 minutes ago',
    user: { name: 'You', avatar: null }
  },
  {
    id: 3,
    type: 'export_created',
    title: 'Exported project',
    description: 'Social Media Campaign (PNG, 1920x1080)',
    timestamp: '1 hour ago',
    user: { name: 'You', avatar: null }
  },
  {
    id: 4,
    type: 'asset_uploaded',
    title: 'Uploaded assets',
    description: '5 images (2.4 MB)',
    timestamp: '2 hours ago',
    user: { name: 'You', avatar: null }
  },
  {
    id: 5,
    type: 'project_shared',
    title: 'Shared project',
    description: 'Invited john@example.com to collaborate',
    timestamp: '3 hours ago',
    user: { name: 'You', avatar: null }
  },
  {
    id: 6,
    type: 'ai_generated',
    title: 'Generated color palette',
    description: 'Created harmonious colors for Brand Identity',
    timestamp: '4 hours ago',
    user: { name: 'You', avatar: null },
    metadata: { tokens: 450, cost: 0.02 }
  },
  {
    id: 7,
    type: 'project_updated',
    title: 'Updated project',
    description: 'Modified layout for E-commerce Banner',
    timestamp: '5 hours ago',
    user: { name: 'You', avatar: null }
  },
  {
    id: 8,
    type: 'login',
    title: 'Logged in',
    description: 'From 192.168.1.100 (Chrome on Windows)',
    timestamp: '6 hours ago',
    user: { name: 'You', avatar: null }
  }
];

const stats = [
  { label: 'Today', value: 12, change: '+3' },
  { label: 'This Week', value: 67, change: '+15' },
  { label: 'This Month', value: 234, change: '+42' },
  { label: 'Total', value: 1847, change: '+234' }
];

export default function ActivityPage() {
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');

  const filteredActivities = mockActivities.filter(activity => {
    const matchesFilter = filter === 'all' || activity.type === filter;
    const matchesSearch = activity.title.toLowerCase().includes(search.toLowerCase()) || 
                         activity.description.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-linear-to-br from-background via-background to-primary/5">
      <div className="container mx-auto p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-linear-to-br from-primary to-primary/60 rounded-xl shadow-lg">
              <Activity className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-linear-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
                Activity Feed
              </h1>
              <p className="text-muted-foreground">
                Track all your actions and events
              </p>
            </div>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid gap-4 md:grid-cols-4"
        >
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold">{stat.value}</span>
                  <Badge variant="secondary" className="bg-green-500/20 text-green-500 border-green-500/50">
                    {stat.change}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search activities..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Select value={filter} onValueChange={setFilter}>
                  <SelectTrigger className="w-[180px]">
                    <Filter className="h-4 w-4 mr-2" />
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Activities</SelectItem>
                    <SelectItem value="project_created">Projects</SelectItem>
                    <SelectItem value="ai_generated">AI Generated</SelectItem>
                    <SelectItem value="export_created">Exports</SelectItem>
                    <SelectItem value="asset_uploaded">Uploads</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* Activity List */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              {filteredActivities.length} activities found
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px] pr-4">
              <div className="space-y-4">
                {filteredActivities.map((activity, index) => {
                  const config = activityTypes[activity.type as keyof typeof activityTypes];
                  const Icon = config.icon;

                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-start gap-4 p-4 rounded-lg hover:bg-primary/5 transition-colors border border-transparent hover:border-primary/20"
                    >
                      {/* Icon */}
                      <div className={`p-3 rounded-lg ${config.bg}`}>
                        <Icon className={`h-5 w-5 ${config.color}`} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1">
                            <p className="font-semibold">{activity.title}</p>
                            <p className="text-sm text-muted-foreground">{activity.description}</p>
                            {activity.metadata && (
                              <div className="flex items-center gap-3 text-xs text-muted-foreground">
                                <span>Tokens: {activity.metadata.tokens.toLocaleString()}</span>
                                <span>Cost: ${activity.metadata.cost.toFixed(2)}</span>
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground whitespace-nowrap">
                            <Clock className="h-3 w-3" />
                            {activity.timestamp}
                          </div>
                        </div>
                      </div>

                      {/* User Avatar */}
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={activity.user.avatar || undefined} />
                        <AvatarFallback>{activity.user.name[0]}</AvatarFallback>
                      </Avatar>
                    </motion.div>
                  );
                })}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

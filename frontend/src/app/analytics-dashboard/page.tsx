"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  MousePointer, 
  Clock, 
  Target,
  Eye,
  Activity,
  Download,
  Calendar,
  Filter,
  ArrowUp,
  ArrowDown,
  Layers,
  Repeat,
  CheckCircle
} from 'lucide-react';

// Generate mock session data once
const generateMockSessionData = () => {
  return Array.from({ length: 5 }, (_, index) => ({
    id: index,
    userId: Math.floor(Math.random() * 10000),
    timeAgo: Math.floor(Math.random() * 10) + 1,
    duration: {
      minutes: Math.floor(Math.random() * 5) + 1,
      seconds: Math.floor(Math.random() * 60)
    }
  }));
};

const MOCK_SESSION_DATA = generateMockSessionData();

// Mock data
const mockHeatmapData = {
  totalClicks: 12456,
  avgTimeOnDesign: '2m 34s',
  topInteractions: ['Button clicks', 'Image views', 'Text selections'],
  hotZones: 3
};

const mockUserFlows = [
  { id: '1', name: 'Homepage → Product → Checkout', users: 2340, conversion: 12.4, trend: 'up' },
  { id: '2', name: 'Landing Page → Signup', users: 1890, conversion: 8.7, trend: 'up' },
  { id: '3', name: 'Blog → Product Page', users: 1245, conversion: 5.2, trend: 'down' },
  { id: '4', name: 'Search → Category → Product', users: 987, conversion: 9.1, trend: 'up' },
];

const mockMetrics = [
  { label: 'Total Views', value: '45.2K', change: '+12.3%', trend: 'up' },
  { label: 'Unique Users', value: '12.8K', change: '+8.7%', trend: 'up' },
  { label: 'Avg. Session', value: '3m 42s', change: '+15.2%', trend: 'up' },
  { label: 'Bounce Rate', value: '34.5%', change: '-4.2%', trend: 'down' },
];

const mockConversionGoals = [
  { id: '1', name: 'Sign Up Completion', target: 1000, current: 847, deadline: '2024-02-15' },
  { id: '2', name: 'Free Trial Starts', target: 500, current: 412, deadline: '2024-02-10' },
  { id: '3', name: 'Pro Upgrades', target: 100, current: 89, deadline: '2024-02-28' },
  { id: '4', name: 'Feature Adoption', target: 2000, current: 1876, deadline: '2024-02-20' },
];

const mockTeamStats = [
  { name: 'John Doe', designs: 45, views: '12.4K', engagement: 'High' },
  { name: 'Sarah Smith', designs: 38, views: '10.2K', engagement: 'Medium' },
  { name: 'Mike Johnson', designs: 52, views: '15.8K', engagement: 'High' },
  { name: 'Emily Brown', designs: 29, views: '8.1K', engagement: 'Medium' },
];

export default function AnalyticsDashboardPage() {
  const [dateRange, setDateRange] = useState('7d');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Real-Time Analytics</h1>
              <p className="text-sm text-gray-500">Track design performance and user interactions</p>
            </div>
            <div className="flex gap-2">
              <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
                {['24h', '7d', '30d', '90d'].map((range) => (
                  <Button
                    key={range}
                    variant={dateRange === range ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setDateRange(range)}
                  >
                    {range}
                  </Button>
                ))}
              </div>
              <Button variant="outline">
                <Calendar className="h-4 w-4 mr-2" />
                Custom
              </Button>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {mockMetrics.map((metric, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="text-sm text-gray-500">{metric.label}</p>
                    <p className="text-2xl font-bold mt-1">{metric.value}</p>
                  </div>
                  <Badge 
                    variant="outline" 
                    className={metric.trend === 'up' ? 'text-green-600 border-green-200 bg-green-50' : 'text-red-600 border-red-200 bg-red-50'}
                  >
                    {metric.trend === 'up' ? <ArrowUp className="h-3 w-3 mr-1" /> : <ArrowDown className="h-3 w-3 mr-1" />}
                    {metric.change}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs defaultValue="heatmaps" className="space-y-6">
          <TabsList className="grid grid-cols-5 w-full max-w-2xl">
            <TabsTrigger value="heatmaps" className="flex items-center gap-2">
              <MousePointer className="h-4 w-4" />
              Heatmaps
            </TabsTrigger>
            <TabsTrigger value="userflows" className="flex items-center gap-2">
              <Repeat className="h-4 w-4" />
              User Flows
            </TabsTrigger>
            <TabsTrigger value="sessions" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Sessions
            </TabsTrigger>
            <TabsTrigger value="conversions" className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Conversions
            </TabsTrigger>
            <TabsTrigger value="team" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Team
            </TabsTrigger>
          </TabsList>

          {/* Heatmaps Tab */}
          <TabsContent value="heatmaps" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Heatmap Visualization */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Click Heatmap</CardTitle>
                  <CardDescription>Visual representation of user interactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    {/* Simulated heatmap overlay */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <MousePointer className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500">Select a design to view heatmap</p>
                        <Button variant="outline" className="mt-4">
                          Choose Design
                        </Button>
                      </div>
                    </div>
                    {/* Heat zones simulation */}
                    <div className="absolute top-1/4 left-1/4 w-20 h-20 rounded-full bg-red-500/30 blur-xl"></div>
                    <div className="absolute top-1/2 right-1/3 w-16 h-16 rounded-full bg-orange-500/25 blur-xl"></div>
                    <div className="absolute bottom-1/4 left-1/2 w-24 h-24 rounded-full bg-yellow-500/20 blur-xl"></div>
                  </div>
                </CardContent>
              </Card>

              {/* Heatmap Stats */}
              <div className="space-y-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Interaction Summary</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">Total Clicks</span>
                      <span className="font-semibold">{mockHeatmapData.totalClicks.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">Avg. Time</span>
                      <span className="font-semibold">{mockHeatmapData.avgTimeOnDesign}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">Hot Zones</span>
                      <span className="font-semibold">{mockHeatmapData.hotZones}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Top Interactions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {mockHeatmapData.topInteractions.map((interaction, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-xs font-medium text-blue-600">
                            {index + 1}
                          </div>
                          <span className="text-sm">{interaction}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Heatmap Types</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button variant="outline" className="w-full justify-start">
                      <MousePointer className="h-4 w-4 mr-2" />
                      Click Map
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Eye className="h-4 w-4 mr-2" />
                      Scroll Map
                    </Button>
                    <Button variant="outline" className="w-full justify-start">
                      <Activity className="h-4 w-4 mr-2" />
                      Move Map
                    </Button>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* User Flows Tab */}
          <TabsContent value="userflows" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">User Journey Analysis</h3>
              <Button variant="outline">
                <Filter className="h-4 w-4 mr-2" />
                Filter Flows
              </Button>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {mockUserFlows.map((flow) => (
                <Card key={flow.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <Repeat className="h-5 w-5 text-blue-500" />
                          <span className="font-medium">{flow.name}</span>
                        </div>
                        <div className="flex gap-6 mt-2 text-sm text-gray-500">
                          <span className="flex items-center gap-1">
                            <Users className="h-4 w-4" />
                            {flow.users.toLocaleString()} users
                          </span>
                          <span className="flex items-center gap-1">
                            <Target className="h-4 w-4" />
                            {flow.conversion}% conversion
                          </span>
                        </div>
                      </div>
                      <Badge 
                        variant="outline"
                        className={flow.trend === 'up' ? 'text-green-600' : 'text-red-600'}
                      >
                        {flow.trend === 'up' ? <TrendingUp className="h-3 w-3 mr-1" /> : <ArrowDown className="h-3 w-3 mr-1" />}
                        {flow.trend === 'up' ? 'Improving' : 'Declining'}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Flow Visualization */}
            <Card>
              <CardHeader>
                <CardTitle>Flow Visualization</CardTitle>
                <CardDescription>Visual representation of user navigation paths</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center gap-4 py-8">
                  <div className="flex flex-col items-center">
                    <div className="w-24 h-24 rounded-lg bg-blue-100 flex items-center justify-center">
                      <Layers className="h-8 w-8 text-blue-600" />
                    </div>
                    <span className="mt-2 text-sm font-medium">Landing</span>
                    <span className="text-xs text-gray-500">5,234 users</span>
                  </div>
                  <ArrowDown className="h-6 w-6 text-gray-400 rotate-[-90deg]" />
                  <div className="flex flex-col items-center">
                    <div className="w-24 h-24 rounded-lg bg-green-100 flex items-center justify-center">
                      <Eye className="h-8 w-8 text-green-600" />
                    </div>
                    <span className="mt-2 text-sm font-medium">Product</span>
                    <span className="text-xs text-gray-500">3,421 users</span>
                  </div>
                  <ArrowDown className="h-6 w-6 text-gray-400 rotate-[-90deg]" />
                  <div className="flex flex-col items-center">
                    <div className="w-24 h-24 rounded-lg bg-purple-100 flex items-center justify-center">
                      <CheckCircle className="h-8 w-8 text-purple-600" />
                    </div>
                    <span className="mt-2 text-sm font-medium">Checkout</span>
                    <span className="text-xs text-gray-500">1,245 users</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sessions Tab */}
          <TabsContent value="sessions" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Active Sessions</CardTitle>
                  <CardDescription>Real-time user activity</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <div className="text-5xl font-bold text-green-600">247</div>
                    <p className="text-gray-500 mt-2">Users currently active</p>
                    <div className="flex justify-center gap-8 mt-6 text-sm">
                      <div>
                        <div className="font-semibold">12</div>
                        <div className="text-gray-500">Editing</div>
                      </div>
                      <div>
                        <div className="font-semibold">89</div>
                        <div className="text-gray-500">Viewing</div>
                      </div>
                      <div>
                        <div className="font-semibold">146</div>
                        <div className="text-gray-500">Browsing</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Session Duration</CardTitle>
                  <CardDescription>Average time spent per session</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>0-30 seconds</span>
                        <span>15%</span>
                      </div>
                      <Progress value={15} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>30s - 2 min</span>
                        <span>25%</span>
                      </div>
                      <Progress value={25} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>2 - 5 min</span>
                        <span>35%</span>
                      </div>
                      <Progress value={35} className="h-2" />
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>5+ min</span>
                        <span>25%</span>
                      </div>
                      <Progress value={25} className="h-2" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Session Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Sessions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {MOCK_SESSION_DATA.map((session) => (
                    <div key={session.id} className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50">
                      <div className="w-10 h-10 rounded-full bg-gray-200"></div>
                      <div className="flex-1">
                        <p className="font-medium">Anonymous User #{session.userId}</p>
                        <p className="text-sm text-gray-500">
                          Viewed 4 designs • {session.timeAgo}m ago
                        </p>
                      </div>
                      <Badge variant="outline">
                        <Clock className="h-3 w-3 mr-1" />
                        {session.duration.minutes}m {session.duration.seconds}s
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Conversions Tab */}
          <TabsContent value="conversions" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Conversion Goals</h3>
              <Button>
                <Target className="h-4 w-4 mr-2" />
                Create Goal
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {mockConversionGoals.map((goal) => (
                <Card key={goal.id}>
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <CardTitle className="text-base">{goal.name}</CardTitle>
                      <Badge variant={goal.current >= goal.target * 0.9 ? 'default' : 'secondary'}>
                        {Math.round((goal.current / goal.target) * 100)}%
                      </Badge>
                    </div>
                    <CardDescription>Deadline: {goal.deadline}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress value={(goal.current / goal.target) * 100} className="h-3 mb-2" />
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>{goal.current.toLocaleString()} achieved</span>
                      <span>{goal.target.toLocaleString()} target</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Conversion Funnel */}
            <Card>
              <CardHeader>
                <CardTitle>Conversion Funnel</CardTitle>
                <CardDescription>Track users through your conversion pipeline</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="w-full bg-blue-500 h-12 rounded flex items-center justify-center text-white font-medium">
                      Visitors: 10,000 (100%)
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-[75%] bg-blue-400 h-12 rounded flex items-center justify-center text-white font-medium">
                      Engaged: 7,500 (75%)
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-[45%] bg-blue-300 h-12 rounded flex items-center justify-center text-white font-medium">
                      Signed Up: 4,500 (45%)
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="w-[15%] bg-green-500 h-12 rounded flex items-center justify-center text-white font-medium">
                      Converted: 1,500 (15%)
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Team Tab */}
          <TabsContent value="team" className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Team Performance</h3>
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export Report
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Team Members</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-3 px-4 font-medium text-gray-500">Member</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-500">Designs</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-500">Total Views</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-500">Engagement</th>
                        <th className="text-left py-3 px-4 font-medium text-gray-500">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mockTeamStats.map((member, index) => (
                        <tr key={index} className="border-b hover:bg-gray-50">
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-gray-200"></div>
                              <span className="font-medium">{member.name}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4">{member.designs}</td>
                          <td className="py-3 px-4">{member.views}</td>
                          <td className="py-3 px-4">
                            <Badge variant={member.engagement === 'High' ? 'default' : 'secondary'}>
                              {member.engagement}
                            </Badge>
                          </td>
                          <td className="py-3 px-4">
                            <Button variant="ghost" size="sm">View Details</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Team Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="pt-6 text-center">
                  <BarChart3 className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">164</div>
                  <p className="text-sm text-gray-500">Total Designs This Month</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6 text-center">
                  <Eye className="h-8 w-8 text-green-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">46.5K</div>
                  <p className="text-sm text-gray-500">Total Views</p>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="pt-6 text-center">
                  <TrendingUp className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                  <div className="text-2xl font-bold">+23%</div>
                  <p className="text-sm text-gray-500">Growth vs Last Month</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

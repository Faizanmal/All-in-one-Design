'use client';

import { useEffect, useState } from 'react';
import { motion, Variants } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { 
  Activity, 
  TrendingUp, 
  Zap, 
  DollarSign, 
  BarChart3,
  Clock,
  Database,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import CountUp from 'react-countup';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { MainHeader } from '@/components/layout/MainHeader';

// Animation variants
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const cardVariants: Variants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 100
    }
  }
};

// Mock data - replace with actual API calls
const mockDashboardData = {
  projects: {
    total: 156,
    thisWeek: 12,
    thisMonth: 45,
    change: 23.5
  },
  aiUsage: {
    today: { requests: 34, tokens: 12500, cost: 0.45 },
    thisMonth: { requests: 847, tokens: 324000, cost: 12.68 }
  },
  activity: {
    today: 89,
    thisWeek: 456
  },
  assets: {
    total: 234,
    storageBytes: 524288000,
    storageMB: 500
  }
};

const chartData = [
  { date: '11/07', projects: 4, aiRequests: 23, exports: 12 },
  { date: '11/08', projects: 7, aiRequests: 31, exports: 18 },
  { date: '11/09', projects: 5, aiRequests: 28, exports: 15 },
  { date: '11/10', projects: 9, aiRequests: 42, exports: 24 },
  { date: '11/11', projects: 11, aiRequests: 38, exports: 21 },
  { date: '11/12', projects: 8, aiRequests: 45, exports: 28 },
  { date: '11/13', projects: 12, aiRequests: 51, exports: 32 }
];

const aiUsageData = [
  { name: 'Layout Generation', value: 342, color: '#8b5cf6' },
  { name: 'Logo Generation', value: 256, color: '#3b82f6' },
  { name: 'Image Generation', value: 189, color: '#10b981' },
  { name: 'Color Palettes', value: 60, color: '#f59e0b' }
];

interface StatCardProps {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  value: string | number;
  change?: number;
  prefix?: string;
  suffix?: string;
  delay?: number;
}

const StatCard = ({ icon: Icon, title, value, change, prefix = '', suffix = '', delay = 0 }: StatCardProps) => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const isPositive = change !== undefined ? change >= 0 : true;

  return (
    <motion.div
      ref={ref}
      variants={cardVariants}
      initial="hidden"
      animate={inView ? "visible" : "hidden"}
      transition={{ delay }}
    >
      <Card className="relative overflow-hidden group hover:shadow-lg transition-all duration-300 border-2 hover:border-primary/50">
        <div className="absolute inset-0 bg-linear-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {title}
          </CardTitle>
          <div className="p-2 bg-primary/10 rounded-lg group-hover:scale-110 transition-transform">
            <Icon className="h-4 w-4 text-primary" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold bg-linear-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            {inView && (
              <CountUp
                start={0}
                end={Number(value)}
                duration={2}
                separator=","
                prefix={prefix}
                suffix={suffix}
                decimals={suffix === 'MB' || prefix === '$' ? 2 : 0}
              />
            )}
          </div>
          {change !== undefined && (
            <div className="flex items-center gap-1 mt-2">
              {isPositive ? (
                <ArrowUpRight className="h-4 w-4 text-green-500" />
              ) : (
                <ArrowDownRight className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm font-medium ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                {Math.abs(change)}%
              </span>
              <span className="text-sm text-muted-foreground">vs last month</span>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default function AnalyticsPage() {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });
  const [_metrics, _setMetrics] = useState({
    totalProjects: 0,
    activeUsers: 0,
    designsCreated: 0,
    storageUsed: '0 MB',
  });

  useEffect(() => {
    // Fetch real data from API
    const fetchAnalyticsData = async () => {
      try {
        const response = await fetch('/api/analytics/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          setMetrics({
            totalProjects: data.projects_count || 0,
            activeUsers: data.active_users || 0,
            designsCreated: data.designs_created || 0,
            storageUsed: data.storage_used || '0 MB',
          });
        }
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
        // Use mock data as fallback
      }
    };
    
    fetchAnalyticsData();
  }, []);

  return (
    <div className="min-h-screen bg-linear-to-br from-background via-background to-primary/5">
      <MainHeader />

      <div className="container mx-auto p-6 space-y-8">
        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-3">
            <div className="p-3 bg-linear-to-br from-primary to-primary/60 rounded-xl shadow-lg">
              <BarChart3 className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-linear-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
                Analytics Dashboard
              </h1>
              <p className="text-muted-foreground">
                Track your projects, AI usage, and performance metrics
              </p>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
        >
          <StatCard
            icon={Activity}
            title="Total Projects"
            value={mockDashboardData.projects.total}
            change={mockDashboardData.projects.change}
            delay={0}
          />
          <StatCard
            icon={Zap}
            title="AI Requests (Month)"
            value={mockDashboardData.aiUsage.thisMonth.requests}
            change={15.3}
            delay={0.1}
          />
          <StatCard
            icon={DollarSign}
            title="AI Cost (Month)"
            value={mockDashboardData.aiUsage.thisMonth.cost}
            prefix="$"
            change={-8.2}
            delay={0.2}
          />
          <StatCard
            icon={Database}
            title="Storage Used"
            value={mockDashboardData.assets.storageMB}
            suffix="MB"
            delay={0.3}
          />
        </motion.div>

        {/* Charts Section */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="overview" className="data-[state=active]:bg-primary">
              Overview
            </TabsTrigger>
            <TabsTrigger value="ai" className="data-[state=active]:bg-primary">
              AI Usage
            </TabsTrigger>
            <TabsTrigger value="activity" className="data-[state=active]:bg-primary">
              Activity
            </TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-primary">
              Insights
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <motion.div
              ref={ref}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5 }}
              className="grid gap-6 md:grid-cols-2"
            >
              {/* Activity Chart */}
              <Card className="col-span-full lg:col-span-1 hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary" />
                    Weekly Activity
                  </CardTitle>
                  <CardDescription>Projects, AI requests, and exports</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="colorProjects" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="colorAI" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" opacity={0.1} />
                      <XAxis dataKey="date" stroke="#888" />
                      <YAxis stroke="#888" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--background))', 
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px'
                        }} 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="projects" 
                        stroke="#8b5cf6" 
                        fillOpacity={1} 
                        fill="url(#colorProjects)" 
                      />
                      <Area 
                        type="monotone" 
                        dataKey="aiRequests" 
                        stroke="#3b82f6" 
                        fillOpacity={1} 
                        fill="url(#colorAI)" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* AI Usage Distribution */}
              <Card className="hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-primary" />
                    AI Usage Distribution
                  </CardTitle>
                  <CardDescription>Breakdown by service type</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={aiUsageData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent = 0 }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {aiUsageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="mt-4 grid grid-cols-2 gap-2">
                    {aiUsageData.map((item, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-sm text-muted-foreground">{item.name}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Recent Activity */}
            <Card className="hover:shadow-xl transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-primary" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { action: 'Project Created', name: 'Modern Landing Page', time: '2 minutes ago', type: 'create' },
                    { action: 'AI Generation', name: 'Logo variations generated', time: '15 minutes ago', type: 'ai' },
                    { action: 'Project Exported', name: 'Social Media Post', time: '1 hour ago', type: 'export' },
                    { action: 'Collaboration', name: 'Invited team member', time: '3 hours ago', type: 'collab' }
                  ].map((activity, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-center justify-between p-4 rounded-lg bg-linear-to-r from-primary/5 to-transparent hover:from-primary/10 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-primary/20 rounded-lg">
                          <Activity className="h-4 w-4 text-primary" />
                        </div>
                        <div>
                          <p className="font-medium">{activity.action}</p>
                          <p className="text-sm text-muted-foreground">{activity.name}</p>
                        </div>
                      </div>
                      <span className="text-sm text-muted-foreground">{activity.time}</span>
                    </motion.div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai" className="space-y-6">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="grid gap-6 md:grid-cols-3"
            >
              <Card className="hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="text-sm">Total Tokens</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-primary">
                    <CountUp end={324000} separator="," />
                  </div>
                  <Progress value={65} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">65% of monthly quota</p>
                </CardContent>
              </Card>
              <Card className="hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="text-sm">Success Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-500">98.5%</div>
                  <Progress value={98.5} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">847 successful requests</p>
                </CardContent>
              </Card>
              <Card className="hover:shadow-xl transition-shadow">
                <CardHeader>
                  <CardTitle className="text-sm">Avg Response Time</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-blue-500">2.4s</div>
                  <Progress value={40} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">Faster than 60% of users</p>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="activity">
            <Card>
              <CardHeader>
                <CardTitle>Activity Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Activity timeline coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="insights">
            <Card>
              <CardHeader>
                <CardTitle>AI Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Insights and recommendations coming soon...</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

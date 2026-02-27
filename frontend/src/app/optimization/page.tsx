'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  BarChart3,
  Beaker,
  Brain,
  CheckCircle,
  ChevronRight,
  FlaskConical,
  Layers,
  Lightbulb,
  Monitor,
  Play,
  Plus,
  Settings,
  Smartphone,
  Tablet,
  Target,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';

interface ABTest {
  id: string;
  name: string;
  status: 'running' | 'completed' | 'draft';
  variants: number;
  traffic: number;
  winner?: string;
  improvement?: number;
  startDate: string;
}

interface PerformanceMetric {
  name: string;
  score: number;
  status: 'good' | 'needs-work' | 'poor';
  suggestions: string[];
}

interface DevicePreview {
  device: string;
  icon: React.ReactNode;
  score: number;
  issues: number;
}

export default function OptimizationPage() {
  const [activeTab, setActiveTab] = useState('ab-testing');
  const [selectedTest, setSelectedTest] = useState<string | null>(null);

  // Mock data
  const abTests: ABTest[] = [
    {
      id: '1',
      name: 'Hero Section CTA Color',
      status: 'running',
      variants: 3,
      traffic: 75,
      startDate: '2024-01-15',
    },
    {
      id: '2',
      name: 'Navigation Layout',
      status: 'completed',
      variants: 2,
      traffic: 100,
      winner: 'Variant B',
      improvement: 23,
      startDate: '2024-01-01',
    },
    {
      id: '3',
      name: 'Product Card Design',
      status: 'draft',
      variants: 4,
      traffic: 0,
      startDate: '',
    },
  ];

  const performanceMetrics: PerformanceMetric[] = [
    {
      name: 'Load Time',
      score: 85,
      status: 'good',
      suggestions: ['Optimize images', 'Enable lazy loading'],
    },
    {
      name: 'Visual Hierarchy',
      score: 72,
      status: 'needs-work',
      suggestions: ['Increase heading contrast', 'Add more whitespace'],
    },
    {
      name: 'Color Contrast',
      score: 91,
      status: 'good',
      suggestions: ['Minor text contrast issues'],
    },
    {
      name: 'Touch Targets',
      score: 65,
      status: 'poor',
      suggestions: ['Increase button sizes', 'Add more padding to links'],
    },
  ];

  const devicePreviews: DevicePreview[] = [
    { device: 'Desktop', icon: <Monitor className="h-5 w-5" />, score: 92, issues: 2 },
    { device: 'Tablet', icon: <Tablet className="h-5 w-5" />, score: 85, issues: 5 },
    { device: 'Mobile', icon: <Smartphone className="h-5 w-5" />, score: 78, issues: 8 },
  ];

  const aiSuggestions = [
    {
      type: 'layout',
      title: 'Improve Visual Flow',
      description: 'Reorder elements to guide user attention more effectively',
      impact: 'high',
    },
    {
      type: 'color',
      title: 'Enhance CTA Visibility',
      description: 'Increase contrast on primary action buttons',
      impact: 'high',
    },
    {
      type: 'typography',
      title: 'Optimize Reading Experience',
      description: 'Adjust line height and paragraph spacing',
      impact: 'medium',
    },
    {
      type: 'accessibility',
      title: 'Add ARIA Labels',
      description: 'Improve screen reader compatibility',
      impact: 'medium',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500/20 text-green-400';
      case 'completed':
        return 'bg-blue-500/20 text-blue-400';
      case 'draft':
        return 'bg-gray-500/20 text-gray-400';
      default:
        return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <header className="border-b border-white/10 bg-gray-900/50 backdrop-blur-lg">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-green-500 to-emerald-600">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">AI Design Optimization</h1>
              <p className="text-sm text-gray-400">Data-driven design improvements</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
            <Button className="bg-linear-to-r from-green-500 to-emerald-600 text-white">
              <Zap className="mr-2 h-4 w-4" />
              Run Analysis
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-6 bg-gray-800/50">
            <TabsTrigger value="ab-testing" className="data-[state=active]:bg-green-500/20">
              <Beaker className="mr-2 h-4 w-4" />
              A/B Testing
            </TabsTrigger>
            <TabsTrigger value="performance" className="data-[state=active]:bg-green-500/20">
              <BarChart3 className="mr-2 h-4 w-4" />
              Performance
            </TabsTrigger>
            <TabsTrigger value="devices" className="data-[state=active]:bg-green-500/20">
              <Monitor className="mr-2 h-4 w-4" />
              Device Preview
            </TabsTrigger>
            <TabsTrigger value="ai-suggestions" className="data-[state=active]:bg-green-500/20">
              <Lightbulb className="mr-2 h-4 w-4" />
              AI Suggestions
            </TabsTrigger>
          </TabsList>

          {/* A/B Testing Tab */}
          <TabsContent value="ab-testing">
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Tests List */}
              <div className="lg:col-span-2">
                <Card className="border-white/10 bg-gray-900/50">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                      <CardTitle className="text-white">A/B Tests</CardTitle>
                      <CardDescription>Manage your design experiments</CardDescription>
                    </div>
                    <Button className="bg-green-600 hover:bg-green-700">
                      <Plus className="mr-2 h-4 w-4" />
                      New Test
                    </Button>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {abTests.map((test) => (
                        <div
                          key={test.id}
                          className={`cursor-pointer rounded-lg border p-4 transition-all ${
                            selectedTest === test.id
                              ? 'border-green-500 bg-green-500/10'
                              : 'border-white/10 bg-gray-800/50 hover:border-white/20'
                          }`}
                          onClick={() => setSelectedTest(test.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <FlaskConical className="h-5 w-5 text-gray-400" />
                              <div>
                                <h3 className="font-medium text-white">{test.name}</h3>
                                <div className="flex items-center gap-2 text-sm text-gray-400">
                                  <span>{test.variants} variants</span>
                                  <span>•</span>
                                  <span>{test.traffic}% traffic</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge className={getStatusColor(test.status)}>
                                {test.status}
                              </Badge>
                              {test.winner && (
                                <div className="flex items-center gap-1 text-green-400">
                                  <TrendingUp className="h-4 w-4" />
                                  <span>+{test.improvement}%</span>
                                </div>
                              )}
                              <ChevronRight className="h-5 w-5 text-gray-500" />
                            </div>
                          </div>
                          {test.status === 'running' && (
                            <div className="mt-3">
                              <div className="mb-1 flex justify-between text-sm text-gray-400">
                                <span>Progress</span>
                                <span>{test.traffic}%</span>
                              </div>
                              <Progress value={test.traffic} className="h-2" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Test Details / Stats */}
              <div>
                <Card className="border-white/10 bg-gray-900/50">
                  <CardHeader>
                    <CardTitle className="text-white">Overall Statistics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20">
                        <Target className="h-6 w-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">18%</p>
                        <p className="text-sm text-gray-400">Avg. Improvement</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/20">
                        <Users className="h-6 w-6 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">24.5K</p>
                        <p className="text-sm text-gray-400">Total Participants</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-500/20">
                        <CheckCircle className="h-6 w-6 text-purple-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">12</p>
                        <p className="text-sm text-gray-400">Completed Tests</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance">
            <div className="grid gap-6 md:grid-cols-2">
              {performanceMetrics.map((metric) => (
                <Card key={metric.name} className="border-white/10 bg-gray-900/50">
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-lg text-white">{metric.name}</CardTitle>
                    <span className={`text-2xl font-bold ${getScoreColor(metric.score)}`}>
                      {metric.score}
                    </span>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-800">
                        <div
                          className={`h-full rounded-full ${getProgressColor(metric.score)}`}
                          style={{ width: `${metric.score}%` }}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-400">Suggestions:</p>
                      {metric.suggestions.map((suggestion, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-sm text-gray-300">
                          <Lightbulb className="mt-0.5 h-4 w-4 text-yellow-400" />
                          {suggestion}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Device Preview Tab */}
          <TabsContent value="devices">
            <div className="grid gap-6 md:grid-cols-3">
              {devicePreviews.map((device) => (
                <Card key={device.device} className="border-white/10 bg-gray-900/50">
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-800">
                        {device.icon}
                      </div>
                      <div>
                        <CardTitle className="text-white">{device.device}</CardTitle>
                        <CardDescription>{device.issues} issues found</CardDescription>
                      </div>
                    </div>
                    <span className={`text-2xl font-bold ${getScoreColor(device.score)}`}>
                      {device.score}
                    </span>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <Progress value={device.score} className="h-2" />
                    </div>
                    <div className="flex h-48 items-center justify-center rounded-lg border border-white/10 bg-gray-800/50">
                      <div className="text-center text-gray-500">
                        {device.icon}
                        <p className="mt-2 text-sm">Preview</p>
                      </div>
                    </div>
                    <Button className="mt-4 w-full" variant="outline">
                      <Play className="mr-2 h-4 w-4" />
                      Test on {device.device}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* AI Suggestions Tab */}
          <TabsContent value="ai-suggestions">
            <Card className="border-white/10 bg-gray-900/50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-linear-to-br from-purple-500 to-pink-500">
                    <Brain className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-white">AI-Powered Suggestions</CardTitle>
                    <CardDescription>
                      Smart recommendations to improve your design
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aiSuggestions.map((suggestion, idx) => (
                    <div
                      key={idx}
                      className="flex items-start justify-between rounded-lg border border-white/10 bg-gray-800/50 p-4"
                    >
                      <div className="flex gap-4">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-500/20">
                          <Layers className="h-5 w-5 text-purple-400" />
                        </div>
                        <div>
                          <h3 className="font-medium text-white">{suggestion.title}</h3>
                          <p className="text-sm text-gray-400">{suggestion.description}</p>
                          <Badge
                            className={`mt-2 ${
                              suggestion.impact === 'high'
                                ? 'bg-red-500/20 text-red-400'
                                : 'bg-yellow-500/20 text-yellow-400'
                            }`}
                          >
                            {suggestion.impact} impact
                          </Badge>
                        </div>
                      </div>
                      <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                        Apply
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

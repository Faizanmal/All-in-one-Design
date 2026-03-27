"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Contrast,
  Type,
  MousePointer2,
  Volume2,
  Scan,
  RefreshCw,
  Download,
  ChevronRight,
  Glasses,
  Palette,
  Target,
  Lightbulb,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface AccessibilityIssue {
  id: number;
  type: 'error' | 'warning' | 'info';
  category: 'contrast' | 'text' | 'keyboard' | 'screen_reader' | 'motion';
  wcag: string;
  title: string;
  description: string;
  element: string;
  suggestion: string;
  impact: 'critical' | 'serious' | 'moderate' | 'minor';
}

interface ColorBlindnessMode {
  id: string;
  name: string;
  description: string;
  percentage: string;
}

// Mock Data
const mockIssues: AccessibilityIssue[] = [
  {
    id: 1, type: 'error', category: 'contrast', wcag: 'WCAG 1.4.3',
    title: 'Insufficient color contrast', description: 'Text color #888888 on background #FFFFFF has a contrast ratio of 3.5:1, which is below the minimum 4.5:1 for normal text.',
    element: 'Button text on hero section', suggestion: 'Change text color to #595959 or darker for a contrast ratio of 7:1.',
    impact: 'critical',
  },
  {
    id: 2, type: 'error', category: 'text', wcag: 'WCAG 1.4.4',
    title: 'Text cannot be resized', description: 'Some text elements use fixed pixel sizes that prevent proper scaling when users zoom the page.',
    element: 'Navigation menu items', suggestion: 'Use relative units (rem, em) instead of fixed px values.',
    impact: 'serious',
  },
  {
    id: 3, type: 'warning', category: 'keyboard', wcag: 'WCAG 2.1.1',
    title: 'Missing focus indicator', description: 'Interactive elements do not have visible focus states for keyboard navigation.',
    element: 'Card hover actions', suggestion: 'Add outline or border styles to :focus and :focus-visible states.',
    impact: 'serious',
  },
  {
    id: 4, type: 'warning', category: 'screen_reader', wcag: 'WCAG 1.1.1',
    title: 'Image missing alt text', description: 'Decorative images should have empty alt text, informative images need descriptive alt text.',
    element: 'Hero background image', suggestion: 'Add alt="" for decorative images or descriptive alt text for informative images.',
    impact: 'moderate',
  },
  {
    id: 5, type: 'info', category: 'motion', wcag: 'WCAG 2.3.3',
    title: 'Animation detected', description: 'Page contains animations that may affect users with motion sensitivity.',
    element: 'Logo animation', suggestion: 'Implement prefers-reduced-motion media query to disable animations for users who prefer reduced motion.',
    impact: 'minor',
  },
];

const colorBlindnessModes: ColorBlindnessMode[] = [
  { id: 'protanopia', name: 'Protanopia', description: 'Red-blind', percentage: '1%' },
  { id: 'deuteranopia', name: 'Deuteranopia', description: 'Green-blind', percentage: '1%' },
  { id: 'tritanopia', name: 'Tritanopia', description: 'Blue-blind', percentage: '0.01%' },
  { id: 'achromatopsia', name: 'Achromatopsia', description: 'Monochromacy', percentage: '0.003%' },
];

const getImpactColor = (impact: string) => {
  switch (impact) {
    case 'critical': return 'bg-red-100 text-red-700 border-red-200';
    case 'serious': return 'bg-orange-100 text-orange-700 border-orange-200';
    case 'moderate': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
    case 'minor': return 'bg-blue-100 text-blue-700 border-blue-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'error': return <XCircle className="h-5 w-5 text-red-500" />;
    case 'warning': return <AlertTriangle className="h-5 w-5 text-amber-500" />;
    case 'info': return <Info className="h-5 w-5 text-blue-500" />;
    default: return <Info className="h-5 w-5 text-gray-500" />;
  }
};


// Issue Card Component
function IssueCard({ issue, onFix }: { issue: AccessibilityIssue; onFix: () => void }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`border rounded-lg bg-white overflow-hidden ${issue.type === 'error' ? 'border-red-200' : issue.type === 'warning' ? 'border-amber-200' : 'border-gray-200'}`}>
      <div className="p-4 cursor-pointer hover:bg-gray-50 transition-colors" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex items-start gap-3">
          {getTypeIcon(issue.type)}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-medium text-gray-900">{issue.title}</h4>
              <Badge variant="outline" className={getImpactColor(issue.impact)}>{issue.impact}</Badge>
              <Badge variant="outline" className="text-xs">{issue.wcag}</Badge>
            </div>
            <p className="text-sm text-gray-500 truncate">{issue.element}</p>
          </div>
          <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
        </div>
      </div>
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-gray-100 bg-gray-50">
          <p className="text-sm text-gray-700 mb-3">{issue.description}</p>
          <div className="flex items-start gap-2 p-3 bg-green-50 rounded-lg mb-3">
            <Lightbulb className="h-4 w-4 text-green-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-green-800">Suggestion</p>
              <p className="text-sm text-green-700">{issue.suggestion}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button size="sm" onClick={onFix}>Auto Fix</Button>
            <Button size="sm" variant="outline">Ignore</Button>
            <Button size="sm" variant="outline">Learn More</Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function AccessibilityTestingPage() {
  const { toast } = useToast();
  const [issues] = useState<AccessibilityIssue[]>(mockIssues);
  const [isScanning, setIsScanning] = useState(false);
  const [activeColorMode, setActiveColorMode] = useState<string | null>(null);

  const errorCount = issues.filter(i => i.type === 'error').length;
  const warningCount = issues.filter(i => i.type === 'warning').length;
  const infoCount = issues.filter(i => i.type === 'info').length;
  const score = Math.round(((issues.length - errorCount * 2 - warningCount) / issues.length) * 100);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      toast({ title: 'Scan Complete', description: `Found ${issues.length} accessibility issues` });
    }, 2000);
  };

  const handleFix = () => {
    toast({ title: 'Auto-fix Applied', description: 'Issue has been automatically resolved' });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                  <Eye className="h-7 w-7 text-blue-600" />Accessibility Testing
                </h1>
                <p className="text-gray-500">WCAG compliance and accessibility checks</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export Report</Button>
                <Button onClick={handleScan} disabled={isScanning}>
                  {isScanning ? <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Scanning...</> : <><Scan className="h-4 w-4 mr-2" />Run Scan</>}
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-5 gap-4 mb-6">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">Score</p>
                      <p className="text-3xl font-bold text-gray-900">{score}%</p>
                    </div>
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${score >= 80 ? 'bg-green-100' : score >= 50 ? 'bg-amber-100' : 'bg-red-100'}`}>
                      {score >= 80 ? <CheckCircle className="h-6 w-6 text-green-600" /> : <AlertTriangle className="h-6 w-6 text-amber-600" />}
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-red-100 rounded-lg"><XCircle className="h-5 w-5 text-red-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Errors</p>
                    <p className="text-2xl font-bold text-red-600">{errorCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-amber-100 rounded-lg"><AlertTriangle className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Warnings</p>
                    <p className="text-2xl font-bold text-amber-600">{warningCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg"><Info className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Info</p>
                    <p className="text-2xl font-bold text-blue-600">{infoCount}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg"><CheckCircle className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Passed</p>
                    <p className="text-2xl font-bold text-green-600">24</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
              {/* Issues List */}
              <div className="col-span-2 flex flex-col overflow-hidden">
                <Tabs defaultValue="all" className="flex-1 flex flex-col overflow-hidden">
                  <TabsList className="mb-4">
                    <TabsTrigger value="all">All Issues ({issues.length})</TabsTrigger>
                    <TabsTrigger value="errors">Errors ({errorCount})</TabsTrigger>
                    <TabsTrigger value="warnings">Warnings ({warningCount})</TabsTrigger>
                    <TabsTrigger value="info">Info ({infoCount})</TabsTrigger>
                  </TabsList>
                  <TabsContent value="all" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {issues.map(issue => <IssueCard key={issue.id} issue={issue} onFix={handleFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="errors" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {issues.filter(i => i.type === 'error').map(issue => <IssueCard key={issue.id} issue={issue} onFix={handleFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="warnings" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {issues.filter(i => i.type === 'warning').map(issue => <IssueCard key={issue.id} issue={issue} onFix={handleFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="info" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {issues.filter(i => i.type === 'info').map(issue => <IssueCard key={issue.id} issue={issue} onFix={handleFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </div>

              {/* Right Panel */}
              <div className="space-y-6 overflow-auto">
                {/* Color Blindness Simulation */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2"><Glasses className="h-4 w-4" />Color Blindness Simulation</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {colorBlindnessModes.map(mode => (
                      <button key={mode.id} onClick={() => setActiveColorMode(activeColorMode === mode.id ? null : mode.id)}
                        className={`w-full flex items-center justify-between p-3 rounded-lg border transition-colors ${
                          activeColorMode === mode.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'
                        }`}>
                        <div className="flex items-center gap-3">
                          <Palette className="h-4 w-4 text-gray-400" />
                          <div className="text-left">
                            <p className="font-medium text-gray-900 text-sm">{mode.name}</p>
                            <p className="text-xs text-gray-500">{mode.description}</p>
                          </div>
                        </div>
                        <Badge variant="outline" className="text-xs">{mode.percentage}</Badge>
                      </button>
                    ))}
                    <Button variant="outline" size="sm" className="w-full mt-2" onClick={() => setActiveColorMode(null)}>Reset View</Button>
                  </CardContent>
                </Card>

                {/* Quick Actions */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2"><Target className="h-4 w-4" />Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button variant="outline" size="sm" className="w-full justify-start"><Contrast className="h-4 w-4 mr-2" />Check Contrast</Button>
                    <Button variant="outline" size="sm" className="w-full justify-start"><Type className="h-4 w-4 mr-2" />Text Size Test</Button>
                    <Button variant="outline" size="sm" className="w-full justify-start"><MousePointer2 className="h-4 w-4 mr-2" />Keyboard Navigation</Button>
                    <Button variant="outline" size="sm" className="w-full justify-start"><Volume2 className="h-4 w-4 mr-2" />Screen Reader Preview</Button>
                  </CardContent>
                </Card>

                {/* WCAG Guidelines */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">WCAG 2.1 Compliance</CardTitle>
                    <CardDescription>Current compliance level</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Level A</span>
                      <div className="flex items-center gap-2">
                        <Progress value={85} className="w-24" />
                        <span className="text-sm font-medium">85%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Level AA</span>
                      <div className="flex items-center gap-2">
                        <Progress value={72} className="w-24" />
                        <span className="text-sm font-medium">72%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-700">Level AAA</span>
                      <div className="flex items-center gap-2">
                        <Progress value={45} className="w-24" />
                        <span className="text-sm font-medium">45%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

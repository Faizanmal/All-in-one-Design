"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  Info,
  Scan,
  RefreshCw,
  Download,
  ChevronRight,
  Layout,
  Type,
  Palette,
  Grid,
  Layers,
  Image,
  Zap,
  Shield,
  FileCheck,
  TrendingUp,
  Target,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface QACheck {
  id: number;
  category: string;
  categoryIcon: React.ElementType;
  name: string;
  status: 'pass' | 'fail' | 'warning' | 'info';
  description: string;
  details?: string;
  autoFixable: boolean;
}

interface QACategory {
  id: string;
  name: string;
  icon: React.ElementType;
  passCount: number;
  totalCount: number;
}

// Mock Data
const mockChecks: QACheck[] = [
  { id: 1, category: 'Typography', categoryIcon: Type, name: 'Consistent font families', status: 'pass', description: 'All text uses approved font families', autoFixable: false },
  { id: 2, category: 'Typography', categoryIcon: Type, name: 'Text alignment consistency', status: 'warning', description: '3 elements have inconsistent text alignment', details: 'Found mixed alignment in card components', autoFixable: true },
  { id: 3, category: 'Typography', categoryIcon: Type, name: 'Line height standards', status: 'pass', description: 'Line heights follow the 1.5x base rule', autoFixable: false },
  { id: 4, category: 'Colors', categoryIcon: Palette, name: 'Brand color compliance', status: 'pass', description: 'All colors match the brand palette', autoFixable: false },
  { id: 5, category: 'Colors', categoryIcon: Palette, name: 'Color contrast ratio', status: 'fail', description: '2 text elements have insufficient contrast', details: 'Button text on hero section: 3.5:1 (minimum 4.5:1)', autoFixable: true },
  { id: 6, category: 'Spacing', categoryIcon: Grid, name: 'Consistent spacing grid', status: 'pass', description: 'All spacing follows 8px grid system', autoFixable: false },
  { id: 7, category: 'Spacing', categoryIcon: Grid, name: 'Component padding', status: 'warning', description: '5 components have non-standard padding', details: 'Cards using 18px instead of 16px or 24px', autoFixable: true },
  { id: 8, category: 'Layout', categoryIcon: Layout, name: 'Responsive breakpoints', status: 'pass', description: 'All layouts adapt to defined breakpoints', autoFixable: false },
  { id: 9, category: 'Layout', categoryIcon: Layout, name: 'Alignment guidelines', status: 'pass', description: 'Elements properly aligned to grid', autoFixable: false },
  { id: 10, category: 'Images', categoryIcon: Image, name: 'Image optimization', status: 'warning', description: '8 images exceed recommended file size', details: 'Total oversized: 2.4MB above budget', autoFixable: false },
  { id: 11, category: 'Images', categoryIcon: Image, name: 'Alt text coverage', status: 'fail', description: '4 images missing alt text', details: 'Hero image, product thumbnails (3)', autoFixable: false },
  { id: 12, category: 'Components', categoryIcon: Layers, name: 'Component instances', status: 'pass', description: 'All components use main library instances', autoFixable: false },
  { id: 13, category: 'Components', categoryIcon: Layers, name: 'Detached components', status: 'info', description: '2 detached component instances found', details: 'Custom button variants may be intentional', autoFixable: true },
];

const categories: QACategory[] = [
  { id: 'typography', name: 'Typography', icon: Type, passCount: 2, totalCount: 3 },
  { id: 'colors', name: 'Colors', icon: Palette, passCount: 1, totalCount: 2 },
  { id: 'spacing', name: 'Spacing', icon: Grid, passCount: 1, totalCount: 2 },
  { id: 'layout', name: 'Layout', icon: Layout, passCount: 2, totalCount: 2 },
  { id: 'images', name: 'Images', icon: Image, passCount: 0, totalCount: 2 },
  { id: 'components', name: 'Components', icon: Layers, passCount: 1, totalCount: 2 },
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'pass': return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'fail': return <XCircle className="h-5 w-5 text-red-500" />;
    case 'warning': return <AlertTriangle className="h-5 w-5 text-amber-500" />;
    case 'info': return <Info className="h-5 w-5 text-blue-500" />;
    default: return <Info className="h-5 w-5 text-gray-500" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pass': return 'bg-green-100 text-green-700 border-green-200';
    case 'fail': return 'bg-red-100 text-red-700 border-red-200';
    case 'warning': return 'bg-amber-100 text-amber-700 border-amber-200';
    case 'info': return 'bg-blue-100 text-blue-700 border-blue-200';
    default: return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

// QA Check Row Component
function QACheckRow({ check, onFix }: { check: QACheck; onFix: () => void }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`border rounded-lg overflow-hidden ${check.status === 'fail' ? 'border-red-200' : check.status === 'warning' ? 'border-amber-200' : 'border-gray-200'}`}>
      <div className="flex items-center gap-3 p-4 bg-white cursor-pointer hover:bg-gray-50" onClick={() => setExpanded(!expanded)}>
        {getStatusIcon(check.status)}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-medium text-gray-900">{check.name}</span>
            <Badge variant="outline" className={getStatusColor(check.status)}>{check.status}</Badge>
          </div>
          <p className="text-sm text-gray-500">{check.description}</p>
        </div>
        {check.autoFixable && check.status !== 'pass' && (
          <Button size="sm" variant="outline" onClick={(e) => { e.stopPropagation(); onFix(); }}>
            <Zap className="h-3 w-3 mr-1" />Auto Fix
          </Button>
        )}
        {check.details && <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`} />}
      </div>
      {expanded && check.details && (
        <div className="px-4 pb-4 pt-2 bg-gray-50 border-t border-gray-100">
          <div className="flex items-start gap-2 p-3 bg-white rounded-lg border border-gray-200">
            <Info className="h-4 w-4 text-gray-400 mt-0.5 shrink-0" />
            <p className="text-sm text-gray-700">{check.details}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function DesignQAPage() {
  const { toast } = useToast();
  const [checks] = useState<QACheck[]>(mockChecks);
  const [isScanning, setIsScanning] = useState(false);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const passCount = checks.filter(c => c.status === 'pass').length;
  const failCount = checks.filter(c => c.status === 'fail').length;
  const warningCount = checks.filter(c => c.status === 'warning').length;
  const score = Math.round((passCount / checks.length) * 100);

  const filteredChecks = activeCategory ? checks.filter(c => c.category.toLowerCase() === activeCategory) : checks;

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      toast({ title: 'Scan Complete', description: `Found ${failCount} issues and ${warningCount} warnings` });
    }, 2000);
  };

  const handleAutoFix = () => {
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
                  <CheckCircle className="h-7 w-7 text-blue-600" />Design QA
                </h1>
                <p className="text-gray-500">Quality assurance and design consistency checks</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Download className="h-4 w-4 mr-2" />Export Report</Button>
                <Button onClick={handleScan} disabled={isScanning}>
                  {isScanning ? <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Scanning...</> : <><Scan className="h-4 w-4 mr-2" />Run QA Check</>}
                </Button>
              </div>
            </div>

            {/* Score & Stats */}
            <div className="grid grid-cols-5 gap-4 mb-6">
              <Card className="col-span-2">
                <CardContent className="p-6">
                  <div className="flex items-center gap-6">
                    <div className="relative w-24 h-24">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="48" cy="48" r="40" fill="none" stroke="#E5E7EB" strokeWidth="8" />
                        <circle cx="48" cy="48" r="40" fill="none" stroke={score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : '#EF4444'} strokeWidth="8" strokeDasharray={`${score * 2.51} 251`} strokeLinecap="round" />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-2xl font-bold text-gray-900">{score}%</span>
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Quality Score</h3>
                      <p className="text-sm text-gray-500 mb-2">Based on {checks.length} quality checks</p>
                      <div className="flex gap-3">
                        <span className="flex items-center gap-1 text-sm"><CheckCircle className="h-4 w-4 text-green-500" />{passCount} passed</span>
                        <span className="flex items-center gap-1 text-sm"><XCircle className="h-4 w-4 text-red-500" />{failCount} failed</span>
                        <span className="flex items-center gap-1 text-sm"><AlertTriangle className="h-4 w-4 text-amber-500" />{warningCount} warnings</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg"><Shield className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Brand Compliance</p>
                    <p className="text-xl font-bold text-gray-900">94%</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg"><Target className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Consistency</p>
                    <p className="text-xl font-bold text-gray-900">87%</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg"><TrendingUp className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">vs Last Check</p>
                    <p className="text-xl font-bold text-green-600">+8%</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-4 gap-6 overflow-hidden">
              {/* Category Sidebar */}
              <div className="space-y-2">
                <button onClick={() => setActiveCategory(null)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg border transition-colors ${
                    !activeCategory ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:bg-gray-50'
                  }`}>
                  <div className="flex items-center gap-3">
                    <FileCheck className="h-5 w-5 text-gray-600" />
                    <span className="font-medium text-gray-900">All Checks</span>
                  </div>
                  <Badge variant="outline">{checks.length}</Badge>
                </button>
                {categories.map(cat => (
                  <button key={cat.id} onClick={() => setActiveCategory(cat.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-lg border transition-colors ${
                      activeCategory === cat.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:bg-gray-50'
                    }`}>
                    <div className="flex items-center gap-3">
                      <cat.icon className="h-5 w-5 text-gray-600" />
                      <span className="font-medium text-gray-900">{cat.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-16">
                        <Progress value={(cat.passCount / cat.totalCount) * 100} className="h-1.5" />
                      </div>
                      <span className="text-xs text-gray-500">{cat.passCount}/{cat.totalCount}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Checks List */}
              <div className="col-span-3 flex flex-col overflow-hidden">
                <Tabs defaultValue="all" className="flex-1 flex flex-col overflow-hidden">
                  <TabsList className="mb-4 w-fit">
                    <TabsTrigger value="all">All</TabsTrigger>
                    <TabsTrigger value="failed">Failed ({failCount})</TabsTrigger>
                    <TabsTrigger value="warnings">Warnings ({warningCount})</TabsTrigger>
                    <TabsTrigger value="passed">Passed ({passCount})</TabsTrigger>
                  </TabsList>
                  <TabsContent value="all" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {filteredChecks.map(check => <QACheckRow key={check.id} check={check} onFix={handleAutoFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="failed" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {filteredChecks.filter(c => c.status === 'fail').map(check => <QACheckRow key={check.id} check={check} onFix={handleAutoFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="warnings" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {filteredChecks.filter(c => c.status === 'warning').map(check => <QACheckRow key={check.id} check={check} onFix={handleAutoFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="passed" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-3 pr-4">
                        {filteredChecks.filter(c => c.status === 'pass').map(check => <QACheckRow key={check.id} check={check} onFix={handleAutoFix} />)}
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

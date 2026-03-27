"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';

import { ScrollArea } from '@/components/ui/scroll-area';

import {
  Lightbulb,
  Sparkles,
  Wand2,
  Palette,
  Type,
  Layout,
  Image,
  Layers,
  Zap,
  RefreshCw,
  Check,
  ChevronRight,
  TrendingUp,
  Target,
  Brain,
  Scissors,
  Maximize,
  Grid,
  AlignCenter,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface SmartTool {
  id: number;
  name: string;
  description: string;
  icon: React.ElementType;
  category: string;
  isNew?: boolean;
  isPremium?: boolean;
}

interface AISuggestion {
  id: number;
  type: string;
  title: string;
  description: string;
  confidence: number;
  preview?: string;
}

// Mock Data
const smartTools: SmartTool[] = [
  { id: 1, name: 'Auto Layout', icon: Layout, description: 'Automatically arrange elements with smart spacing', category: 'Layout' },
  { id: 2, name: 'Smart Color', icon: Palette, description: 'Generate harmonious color palettes instantly', category: 'Colors', isNew: true },
  { id: 3, name: 'Font Pairing', icon: Type, description: 'AI-powered font combination suggestions', category: 'Typography' },
  { id: 4, name: 'Background Remover', icon: Scissors, description: 'Remove backgrounds from images with one click', category: 'Images' },
  { id: 5, name: 'Smart Resize', icon: Maximize, description: 'Intelligently resize designs for different formats', category: 'Layout', isPremium: true },
  { id: 6, name: 'Content Fill', icon: Grid, description: 'Auto-generate placeholder content and images', category: 'Content' },
  { id: 7, name: 'Style Transfer', icon: Wand2, description: 'Apply styles from one design to another', category: 'Styles', isNew: true },
  { id: 8, name: 'Smart Align', icon: AlignCenter, description: 'Perfect alignment with intelligent guides', category: 'Layout' },
  { id: 9, name: 'Image Enhance', icon: Image, description: 'AI-powered image upscaling and enhancement', category: 'Images', isPremium: true },
  { id: 10, name: 'Component Match', icon: Layers, description: 'Find similar components in your library', category: 'Components' },
];

const mockSuggestions: AISuggestion[] = [
  { id: 1, type: 'Layout', title: 'Center align hero section', description: 'Your hero text would look better centered with more breathing room', confidence: 92 },
  { id: 2, type: 'Color', title: 'Improve contrast ratio', description: 'Button text needs darker color for better accessibility', confidence: 88 },
  { id: 3, type: 'Typography', title: 'Reduce font weights', description: 'Using too many font weights - simplify to 2-3 for cleaner design', confidence: 85 },
  { id: 4, type: 'Spacing', title: 'Consistent padding', description: 'Card components have inconsistent padding - suggest 24px standard', confidence: 78 },
];

const categories = ['All', 'Layout', 'Colors', 'Typography', 'Images', 'Styles', 'Components', 'Content'];

// Smart Tool Card
function SmartToolCard({ tool, onUse }: { tool: SmartTool; onUse: () => void }) {
  return (
    <Card className="hover:shadow-md transition-all cursor-pointer group" onClick={onUse}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 rounded-xl group-hover:bg-blue-600 transition-colors">
            <tool.icon className="h-6 w-6 text-blue-600 group-hover:text-white transition-colors" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-gray-900">{tool.name}</h4>
              {tool.isNew && <Badge className="bg-green-100 text-green-700">New</Badge>}
              {tool.isPremium && <Badge className="bg-amber-100 text-amber-700">Pro</Badge>}
            </div>
            <p className="text-sm text-gray-500 mt-1">{tool.description}</p>
          </div>
          <ChevronRight className="h-5 w-5 text-gray-300 group-hover:text-gray-600 transition-colors" />
        </div>
      </CardContent>
    </Card>
  );
}

// Suggestion Card
function SuggestionCard({ suggestion, onApply, onDismiss }: { suggestion: AISuggestion; onApply: () => void; onDismiss: () => void }) {
  return (
    <div className="p-4 bg-white rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
      <div className="flex items-start gap-3">
        <div className="p-2 bg-purple-100 rounded-lg">
          <Sparkles className="h-4 w-4 text-purple-600" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Badge variant="outline">{suggestion.type}</Badge>
              <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
            </div>
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <Target className="h-3 w-3" />
              <span>{suggestion.confidence}%</span>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-3">{suggestion.description}</p>
          <div className="flex gap-2">
            <Button size="sm" onClick={onApply}><Check className="h-3 w-3 mr-1" />Apply</Button>
            <Button size="sm" variant="ghost" onClick={onDismiss}>Dismiss</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SmartToolsPage() {
  const { toast } = useToast();
  const [activeCategory, setActiveCategory] = useState('All');
  const [suggestions, setSuggestions] = useState<AISuggestion[]>(mockSuggestions);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const filteredTools = activeCategory === 'All' 
    ? smartTools 
    : smartTools.filter(t => t.category === activeCategory);

  const handleUseTool = (tool: SmartTool) => {
    toast({ title: `${tool.name} Activated`, description: tool.description });
  };

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      toast({ title: 'Analysis Complete', description: `Found ${suggestions.length} suggestions to improve your design` });
    }, 2000);
  };

  const handleApplySuggestion = (id: number) => {
    setSuggestions(suggestions.filter(s => s.id !== id));
    toast({ title: 'Suggestion Applied', description: 'Design has been updated' });
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
                  <Lightbulb className="h-7 w-7 text-blue-600" />Smart Tools
                </h1>
                <p className="text-gray-500">AI-powered design helpers and automation</p>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" onClick={handleAnalyze} disabled={isAnalyzing}>
                  {isAnalyzing ? <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Analyzing...</> : <><Brain className="h-4 w-4 mr-2" />Analyze Design</>}
                </Button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg"><Zap className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Tools Available</p>
                    <p className="text-2xl font-bold text-gray-900">{smartTools.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg"><Sparkles className="h-5 w-5 text-purple-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">AI Suggestions</p>
                    <p className="text-2xl font-bold text-gray-900">{suggestions.length}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-green-100 rounded-lg"><TrendingUp className="h-5 w-5 text-green-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Time Saved</p>
                    <p className="text-2xl font-bold text-gray-900">4.2h</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="p-3 bg-amber-100 rounded-lg"><Target className="h-5 w-5 text-amber-600" /></div>
                  <div>
                    <p className="text-sm text-gray-500">Design Score</p>
                    <p className="text-2xl font-bold text-gray-900">87%</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-3 gap-6 overflow-hidden">
              {/* Tools Grid */}
              <div className="col-span-2 flex flex-col overflow-hidden">
                <div className="flex gap-2 mb-4 flex-wrap">
                  {categories.map(cat => (
                    <Button key={cat} size="sm" variant={activeCategory === cat ? 'default' : 'outline'} onClick={() => setActiveCategory(cat)}>
                      {cat}
                    </Button>
                  ))}
                </div>
                <ScrollArea className="flex-1">
                  <div className="grid grid-cols-2 gap-4 pr-4">
                    {filteredTools.map(tool => (
                      <SmartToolCard key={tool.id} tool={tool} onUse={() => handleUseTool(tool)} />
                    ))}
                  </div>
                </ScrollArea>
              </div>

              {/* AI Suggestions Panel */}
              <div className="flex flex-col overflow-hidden bg-white rounded-xl border border-gray-200">
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                      <Sparkles className="h-4 w-4 text-purple-600" />AI Suggestions
                    </h3>
                    <Badge variant="outline">{suggestions.length} active</Badge>
                  </div>
                </div>
                <ScrollArea className="flex-1">
                  <div className="p-4 space-y-3">
                    {suggestions.length > 0 ? (
                      suggestions.map(suggestion => (
                        <SuggestionCard key={suggestion.id} suggestion={suggestion} 
                          onApply={() => handleApplySuggestion(suggestion.id)}
                          onDismiss={() => setSuggestions(suggestions.filter(s => s.id !== suggestion.id))} />
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <Check className="h-8 w-8 mx-auto mb-2 text-green-500" />
                        <p className="font-medium">All caught up!</p>
                        <p className="text-sm">No more suggestions for now</p>
                      </div>
                    )}
                  </div>
                </ScrollArea>
                {suggestions.length > 0 && (
                  <div className="p-4 border-t border-gray-200">
                    <Button className="w-full" variant="outline" onClick={() => { 
                      suggestions.forEach(s => handleApplySuggestion(s.id));
                    }}>
                      <Zap className="h-4 w-4 mr-2" />Apply All Suggestions
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

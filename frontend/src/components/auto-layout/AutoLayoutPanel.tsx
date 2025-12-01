'use client';

import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  LayoutGrid,
  Wand2,
  AlignHorizontalJustifyCenter,
  AlignVerticalJustifyCenter,
  Grid3X3,
  Layers,
  ChevronDown,
  Check,
  Loader2,
  Sparkles,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';

interface LayoutPreset {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
}

interface LayoutSuggestion {
  id: string;
  name: string;
  description: string;
  preview: string;
  confidence: number;
  changes: any[];
}

interface AutoLayoutPanelProps {
  projectId: number;
  selectedComponents?: number[];
  onApplyLayout?: (layout: any) => void;
}

const LAYOUT_PRESETS: LayoutPreset[] = [
  { id: 'grid-2x2', name: '2x2 Grid', description: 'Arrange in 2 columns, 2 rows', icon: 'grid', category: 'grid' },
  { id: 'grid-3x3', name: '3x3 Grid', description: 'Arrange in 3 columns, 3 rows', icon: 'grid', category: 'grid' },
  { id: 'flex-row', name: 'Horizontal Row', description: 'Arrange in a horizontal row', icon: 'row', category: 'flex' },
  { id: 'flex-col', name: 'Vertical Column', description: 'Arrange in a vertical column', icon: 'col', category: 'flex' },
  { id: 'masonry', name: 'Masonry', description: 'Pinterest-style layout', icon: 'masonry', category: 'grid' },
  { id: 'hero-cards', name: 'Hero + Cards', description: 'Large hero with card grid below', icon: 'hero', category: 'composition' },
  { id: 'sidebar', name: 'Sidebar Layout', description: 'Sidebar with main content', icon: 'sidebar', category: 'composition' },
  { id: 'centered', name: 'Centered Stack', description: 'Centered vertical stack', icon: 'center', category: 'flex' },
];

export function AutoLayoutPanel({ projectId, selectedComponents = [], onApplyLayout }: AutoLayoutPanelProps) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('ai');
  const [gridSpacing, setGridSpacing] = useState([16]);
  const [gridSize, setGridSize] = useState([8]);

  // Fetch AI layout suggestions
  const { data: suggestions, isLoading: loadingSuggestions, refetch } = useQuery({
    queryKey: ['auto-layout-suggestions', projectId, selectedComponents],
    queryFn: async () => {
      const response = await fetch(`/api/v1/ai/auto-layout/projects/${projectId}/suggest/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component_ids: selectedComponents }),
      });
      if (!response.ok) throw new Error('Failed to get suggestions');
      return response.json();
    },
    enabled: selectedComponents.length > 0,
  });

  // Apply layout mutation
  const applyLayoutMutation = useMutation({
    mutationFn: async ({ presetId, options }: { presetId: string; options?: any }) => {
      const response = await fetch(`/api/v1/ai/auto-layout/projects/${projectId}/apply-preset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          preset_id: presetId,
          component_ids: selectedComponents,
          options,
        }),
      });
      if (!response.ok) throw new Error('Failed to apply layout');
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: 'Layout Applied',
        description: 'The layout has been applied to selected components.',
      });
      onApplyLayout?.(data);
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'Failed to apply layout. Please try again.',
        variant: 'destructive',
      });
    },
  });

  // Align to grid mutation
  const alignToGridMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/ai/auto-layout/projects/${projectId}/align-to-grid/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          component_ids: selectedComponents,
          grid_size: gridSize[0],
        }),
      });
      if (!response.ok) throw new Error('Failed to align');
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: 'Aligned to Grid',
        description: `${data.aligned_count} components aligned to ${gridSize[0]}px grid.`,
      });
      onApplyLayout?.(data);
    },
  });

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <LayoutGrid className="h-5 w-5 text-primary" />
            <CardTitle className="text-lg">Auto Layout</CardTitle>
          </div>
          {selectedComponents.length > 0 && (
            <Badge variant="secondary">
              {selectedComponents.length} selected
            </Badge>
          )}
        </div>
        <CardDescription>
          AI-powered automatic layout suggestions and presets
        </CardDescription>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="ai" className="flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              AI Suggest
            </TabsTrigger>
            <TabsTrigger value="presets" className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              Presets
            </TabsTrigger>
            <TabsTrigger value="grid" className="flex items-center gap-1">
              <Grid3X3 className="h-3 w-3" />
              Grid
            </TabsTrigger>
          </TabsList>

          {/* AI Suggestions Tab */}
          <TabsContent value="ai" className="space-y-4 mt-4">
            {selectedComponents.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Wand2 className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>Select components to get AI layout suggestions</p>
              </div>
            ) : loadingSuggestions ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                <span className="ml-2">Analyzing layout...</span>
              </div>
            ) : suggestions?.suggestions?.length > 0 ? (
              <div className="space-y-3">
                {suggestions.suggestions.map((suggestion: LayoutSuggestion) => (
                  <div
                    key={suggestion.id}
                    className="p-3 border rounded-lg hover:border-primary cursor-pointer transition-colors"
                    onClick={() => applyLayoutMutation.mutate({ 
                      presetId: suggestion.id,
                      options: suggestion.changes 
                    })}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">{suggestion.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {suggestion.description}
                        </p>
                      </div>
                      <Badge variant="outline" className="ml-2">
                        {Math.round(suggestion.confidence * 100)}%
                      </Badge>
                    </div>
                  </div>
                ))}
                
                <Button 
                  variant="outline" 
                  className="w-full" 
                  onClick={() => refetch()}
                  disabled={loadingSuggestions}
                >
                  <Wand2 className="h-4 w-4 mr-2" />
                  Refresh Suggestions
                </Button>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p>No suggestions available for current selection</p>
                <Button 
                  variant="outline" 
                  className="mt-2"
                  onClick={() => refetch()}
                >
                  Try Again
                </Button>
              </div>
            )}
          </TabsContent>

          {/* Presets Tab */}
          <TabsContent value="presets" className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-2">
              {LAYOUT_PRESETS.map((preset) => (
                <Button
                  key={preset.id}
                  variant="outline"
                  className="h-auto py-3 flex flex-col items-start"
                  disabled={selectedComponents.length === 0 || applyLayoutMutation.isPending}
                  onClick={() => applyLayoutMutation.mutate({ 
                    presetId: preset.id,
                    options: { spacing: gridSpacing[0] }
                  })}
                >
                  <span className="font-medium">{preset.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {preset.description}
                  </span>
                </Button>
              ))}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Spacing</label>
              <Slider
                value={gridSpacing}
                onValueChange={setGridSpacing}
                min={0}
                max={64}
                step={4}
              />
              <span className="text-xs text-muted-foreground">{gridSpacing[0]}px</span>
            </div>
          </TabsContent>

          {/* Grid Alignment Tab */}
          <TabsContent value="grid" className="space-y-4 mt-4">
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Grid Size</label>
                <Slider
                  value={gridSize}
                  onValueChange={setGridSize}
                  min={4}
                  max={32}
                  step={4}
                />
                <span className="text-xs text-muted-foreground">{gridSize[0]}px grid</span>
              </div>

              <Button
                className="w-full"
                disabled={selectedComponents.length === 0 || alignToGridMutation.isPending}
                onClick={() => alignToGridMutation.mutate()}
              >
                {alignToGridMutation.isPending ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Grid3X3 className="h-4 w-4 mr-2" />
                )}
                Align to Grid
              </Button>

              <div className="grid grid-cols-3 gap-2">
                <Button variant="outline" size="sm">
                  <AlignHorizontalJustifyCenter className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <AlignVerticalJustifyCenter className="h-4 w-4" />
                </Button>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem>Distribute Horizontally</DropdownMenuItem>
                    <DropdownMenuItem>Distribute Vertically</DropdownMenuItem>
                    <DropdownMenuItem>Match Width</DropdownMenuItem>
                    <DropdownMenuItem>Match Height</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

export default AutoLayoutPanel;

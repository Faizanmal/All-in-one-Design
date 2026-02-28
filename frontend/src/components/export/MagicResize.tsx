"use client";

import React, { useState, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Share2, Megaphone, Printer, Presentation, Globe,
  Wand2, Loader2, Check, Copy, ArrowRight,
} from 'lucide-react';
import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api';
import { toast } from 'sonner';

interface MagicResizeProps {
  projectId: number;
  projectName: string;
  sourceWidth: number;
  sourceHeight: number;
  onResizeComplete?: (projects: CreatedProject[]) => void;
}

interface CreatedProject {
  id: number;
  name: string;
  format: string;
  width: number;
  height: number;
}

interface FormatPreset {
  name: string;
  width: number;
  height: number;
  category: string;
}

const categoryIcons: Record<string, React.ReactNode> = {
  social: <Share2 className="w-4 h-4" />,
  ads: <Megaphone className="w-4 h-4" />,
  print: <Printer className="w-4 h-4" />,
  presentation: <Presentation className="w-4 h-4" />,
  web: <Globe className="w-4 h-4" />,
};

const categoryNames: Record<string, string> = {
  social: 'Social Media',
  ads: 'Display Ads',
  print: 'Print',
  presentation: 'Presentations',
  web: 'Web',
};

export function MagicResize({ projectId, projectName, sourceWidth, sourceHeight, onResizeComplete }: MagicResizeProps) {
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [strategy, setStrategy] = useState('smart');
  const [activeCategory, setActiveCategory] = useState('social');

  // Fetch presets
  const { data: presetsData } = useQuery({
    queryKey: ['resize-presets'],
    queryFn: async () => {
      const response = await apiClient.get('/v1/projects/resize/presets/');
      return response.data;
    },
  });

  const presets: Record<string, FormatPreset> = presetsData?.presets || {};
  const categories: { id: string; name: string }[] = presetsData?.categories || [];

  const filteredPresets = useMemo(() => {
    return Object.entries(presets).filter(([, preset]) => preset.category === activeCategory);
  }, [presets, activeCategory]);

  const toggleFormat = (formatKey: string) => {
    setSelectedFormats(prev =>
      prev.includes(formatKey)
        ? prev.filter(f => f !== formatKey)
        : [...prev, formatKey]
    );
  };

  const selectAll = () => {
    const categoryFormats = filteredPresets.map(([key]) => key);
    const allSelected = categoryFormats.every(f => selectedFormats.includes(f));
    if (allSelected) {
      setSelectedFormats(prev => prev.filter(f => !categoryFormats.includes(f)));
    } else {
      setSelectedFormats(prev => [...new Set([...prev, ...categoryFormats])]);
    }
  };

  // Resize mutation
  const resizeMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`/v1/projects/resize/${projectId}/`, {
        formats: selectedFormats,
        strategy,
        create_copies: true,
      });
      return response.data;
    },
    onSuccess: (data) => {
      toast.success(
        `Created ${data.created_projects.length} resized designs!`
      );
      onResizeComplete?.(data.created_projects);
      setSelectedFormats([]);
    },
    onError: () => {
      toast.error('Failed to resize designs. Please try again.');
    },
  });

  const aspectRatio = (w: number, h: number) => {
    const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
    const d = gcd(w, h);
    return `${w / d}:${h / d}`;
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-2">
          <Wand2 className="w-5 h-5 text-primary" />
          <h2 className="text-lg font-semibold">Magic Resize</h2>
        </div>
        <p className="text-sm text-muted-foreground">
          Resize &ldquo;{projectName}&rdquo; ({sourceWidth}×{sourceHeight}) to multiple formats
        </p>
      </div>

      {/* Strategy selector */}
      <div className="px-4 py-3 border-b">
        <label className="text-sm font-medium mb-1.5 block">Resize Strategy</label>
        <Select value={strategy} onValueChange={setStrategy}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="smart">Smart (AI-powered repositioning)</SelectItem>
            <SelectItem value="scale">Scale (proportional)</SelectItem>
            <SelectItem value="center">Center (fit &amp; center)</SelectItem>
            <SelectItem value="fill">Fill (crop to fit)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category tabs */}
      <Tabs value={activeCategory} onValueChange={setActiveCategory} className="flex-1 flex flex-col">
        <TabsList className="mx-4 mt-3 justify-start flex-wrap h-auto gap-1">
          {(categories.length > 0 ? categories : [
            { id: 'social', name: 'Social Media' },
            { id: 'ads', name: 'Ads' },
            { id: 'print', name: 'Print' },
            { id: 'presentation', name: 'Presentations' },
            { id: 'web', name: 'Web' },
          ]).map((cat) => (
            <TabsTrigger key={cat.id} value={cat.id} className="text-xs gap-1">
              {categoryIcons[cat.id]}
              {cat.name}
            </TabsTrigger>
          ))}
        </TabsList>

        <div className="px-4 py-2 flex justify-between items-center">
          <span className="text-xs text-muted-foreground">
            {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
          </span>
          <Button variant="ghost" size="sm" onClick={selectAll} className="text-xs h-7">
            Select all in {categoryNames[activeCategory] || activeCategory}
          </Button>
        </div>

        <ScrollArea className="flex-1 px-4">
          <div className="grid grid-cols-1 gap-2 pb-4">
            {filteredPresets.map(([key, preset]) => {
              const isSelected = selectedFormats.includes(key);
              return (
                <Card
                  key={key}
                  className={`cursor-pointer transition-colors ${
                    isSelected ? 'border-primary bg-primary/5' : 'hover:border-muted-foreground/30'
                  }`}
                  onClick={() => toggleFormat(key)}
                >
                  <CardContent className="p-3 flex items-center gap-3">
                    <Checkbox checked={isSelected} className="pointer-events-none" />
                    {/* Mini preview */}
                    <div
                      className="border rounded bg-muted flex-shrink-0"
                      style={{
                        width: Math.min(40, preset.width / Math.max(preset.width, preset.height) * 40),
                        height: Math.min(40, preset.height / Math.max(preset.width, preset.height) * 40),
                      }}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">{preset.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {preset.width}×{preset.height}px &middot; {aspectRatio(preset.width, preset.height)}
                      </p>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-primary flex-shrink-0" />}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </ScrollArea>
      </Tabs>

      {/* Action bar */}
      <div className="p-4 border-t bg-background">
        {selectedFormats.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {selectedFormats.map(f => (
              <Badge key={f} variant="secondary" className="text-xs">
                {presets[f]?.name || f}
                <button
                  className="ml-1 hover:text-destructive"
                  onClick={(e) => { e.stopPropagation(); toggleFormat(f); }}
                >
                  ×
                </button>
              </Badge>
            ))}
          </div>
        )}
        <Button
          className="w-full"
          size="lg"
          disabled={selectedFormats.length === 0 || resizeMutation.isPending}
          onClick={() => resizeMutation.mutate()}
        >
          {resizeMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Resizing {selectedFormats.length} format{selectedFormats.length > 1 ? 's' : ''}...
            </>
          ) : (
            <>
              <Copy className="w-4 h-4 mr-2" />
              Resize to {selectedFormats.length} format{selectedFormats.length > 1 ? 's' : ''}
              <ArrowRight className="w-4 h-4 ml-2" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}

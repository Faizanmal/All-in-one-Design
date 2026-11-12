/**
 * AI Design Assistant Panel
 * Advanced AI features: generate designs, suggest improvements, auto-layout
 */
'use client';

import React, { useState, useCallback } from 'react';
import type { FabricCanvas, FabricObject } from '@/types/fabric';
import {
  Sparkles, Wand2, Palette, Type, Layout, Image as ImageIcon,
  Accessibility, Zap, Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { useToast } from '@/hooks/use-toast';
import apiClient from '@/lib/design-api';
import { requestDesignAssistant } from '@/lib/design-assistant-api';
import { AIResultReport } from './AIResultReport';

interface AIAssistantPanelProps {
  canvas: FabricCanvas | null;
  projectId?: number;
  onApplySuggestion?: (suggestion: Record<string, unknown>) => void;
}

export function AIAssistantPanel({ canvas, projectId: _projectId, onApplySuggestion }: AIAssistantPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<{ title: string; data: unknown } | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Array<Record<string, unknown>>>([]);
  const [designStyle, setDesignStyle] = useState('modern');
  const [designType, setDesignType] = useState('landing_page');
  const [numVariants, setNumVariants] = useState(3);
  const [accessibilityFirst, setAccessibilityFirst] = useState(true);
  const [brandColors, setBrandColors] = useState<string[]>(['#3B82F6', '#10B981']);
  const { toast } = useToast();

  // Generate design variants
  const generateDesign = useCallback(async () => {
    if (!prompt.trim()) {
      toast({ title: 'Please enter a prompt', variant: 'destructive' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post(
        '/ai/enhanced/generate_variants/',
        {
          prompt,
          design_type: designType,
          num_variants: numVariants,
          style_preferences: { mood: designStyle, colors: brandColors, accessibility_first: accessibilityFirst },
        }
      );

      setSuggestions(response.data.variants || []);
      toast({ title: 'Design variants generated!', description: `Created ${response.data.variants.length} variants` });
    } catch (error: unknown) {
      console.error('Generation failed:', error);
      const errorMessage = error && typeof error === 'object' && 'response' in error && error.response && typeof error.response === 'object' && 'data' in error.response && error.response.data && typeof error.response.data === 'object' && 'error' in error.response.data ? String(error.response.data.error) : 'Please try again';
      toast({
        title: 'Generation failed',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [prompt, designType, designStyle, numVariants, brandColors, accessibilityFirst, toast]);

  // Check accessibility
  const checkAccessibility = useCallback(async () => {
    if (!canvas || canvas.getObjects().length === 0) {
      toast({ title: 'Add elements to the canvas first', variant: 'destructive' });
      return;
    }
    setLoading(true);
    try {
      // Extract colors from canvas
      const objects = canvas?.getObjects() || [];
      const colors = new Set<string>();
      objects.forEach((obj) => {
        if (obj.fill && typeof obj.fill === 'string') colors.add(obj.fill);
        if (obj.stroke && typeof obj.stroke === 'string') colors.add(obj.stroke);
      });

      const response = await apiClient.post(
        '/ai/accessibility/analyze-palette/',
        {
          colors: Array.from(colors),
          background: typeof canvas.backgroundColor === 'string' && canvas.backgroundColor ? canvas.backgroundColor : '#FFFFFF',
        }
      );

      const results = response.data.colors || [];
      const failing = results.filter((r: { usable_for_text?: boolean; error?: string }) => !r.usable_for_text || r.error);
      setReport({ title: 'Color accessibility report', data: response.data });

      if (failing.length === 0) {
        toast({
          title: 'Accessibility passed!',
          description: 'Canvas colors meet WCAG AA text contrast against the canvas background',
          variant: 'default'
        });
      } else {
        toast({
          title: 'Accessibility issues found',
          description: `${failing.length} color combinations need improvement`,
          variant: 'destructive'
        });
      }
    } catch (error: unknown) {
      console.error('Check failed:', error);
      toast({ title: 'Check failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [canvas, toast]);

  // Generate color palette
  const generateColorPalette = useCallback(async () => {
    if (brandColors.length === 0) {
      toast({ title: 'Please add at least one base color', variant: 'destructive' });
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post(
        '/ai/generate-color-palette/',
        {
          theme: `${designStyle} design palette based on ${brandColors.join(', ')}`,
        }
      );

      const palette: string[] = response.data.colors || [];
      if (!palette.length) throw new Error('No colors returned');
      setBrandColors(palette);
      toast({
        title: 'Color palette generated!',
        description: 'Updated brand colors; applied the first color to the selected element'
      });

      // Apply colors to canvas (example)
      if (canvas) {
        const activeObj = canvas.getActiveObject();
        if (activeObj && palette[0]) {
          activeObj.set('fill', palette[0]);
          canvas.renderAll();
        }
      }
    } catch (error: unknown) {
      console.error('Generation failed:', error);
      toast({ title: 'Generation failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [brandColors, designStyle, canvas, toast]);

  const analyzeDesign = async (kind: 'layout' | 'typography') => {
    if (!canvas || canvas.getObjects().length === 0) {
      toast({ title: 'Add elements to the canvas first', variant: 'destructive' });
      return;
    }
    setLoading(true);
    setReport(null);
    try {
      const objects = canvas.getObjects();
      const fonts = [...new Set(objects.map(obj => 'fontFamily' in obj ? String(obj.fontFamily) : '').filter(Boolean))];
      const data = await requestDesignAssistant(
        kind === 'layout' ? 'critique-design' : 'suggest-typography',
        kind === 'layout' ? {
          project_type: designType, colors: brandColors, fonts,
          element_count: objects.length, width: canvas.getWidth(), height: canvas.getHeight(),
          elements: objects.slice(0, 100).map(obj => ({
            type: obj.type, left: obj.left, top: obj.top,
            width: obj.getScaledWidth(), height: obj.getScaledHeight(),
            angle: obj.angle,
          })),
        } : { design_type: designType, mood: designStyle, brand_attributes: fonts },
      );
      const result = kind === 'layout' ? data.critique : data.typography;
      if (!result) throw new Error('The AI service returned no report. Please try again.');
      setReport({ title: kind === 'layout' ? 'Layout analysis' : 'Typography recommendations', data: result });
    } catch (error) {
      toast({ title: 'Analysis failed', description: error instanceof Error ? error.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const generateImage = async () => {
    if (!prompt.trim()) {
      toast({ title: 'Describe the image you want to generate', variant: 'destructive' });
      return;
    }
    setLoading(true);
    setImageUrl(null);
    try {
      const data = await requestDesignAssistant('generate-image', { prompt: prompt.trim(), size: '1024x1024', style: 'vivid' });
      if (typeof data.image_url !== 'string' || !/^https?:\/\//.test(data.image_url)) throw new Error('The image service returned no usable image.');
      setImageUrl(data.image_url);
    } catch (error) {
      toast({ title: 'Image generation failed', description: error instanceof Error ? error.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const addImageToCanvas = async () => {
    if (!canvas || !imageUrl) return;
    setLoading(true);
    try {
      const { FabricImage } = await import('fabric');
      const image = await FabricImage.fromURL(imageUrl, { crossOrigin: 'anonymous' });
      const scale = Math.min(canvas.getWidth() / image.width, canvas.getHeight() / image.height, 1);
      image.scale(scale);
      canvas.add(image);
      canvas.centerObject(image);
      image.setCoords();
      canvas.setActiveObject(image);
      canvas.requestRenderAll();
      toast({ title: 'Image added to your canvas' });
    } catch {
      toast({ title: 'Unable to add image', description: 'The image could not be loaded. Try generating it again.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  // Auto-layout elements
  const autoLayout = useCallback(async () => {
    if (!canvas) return;

    const objects = canvas.getActiveObjects();
    if (objects.length < 2) {
      toast({ title: 'Select multiple objects to auto-layout', variant: 'destructive' });
      return;
    }

    // Simple grid layout
    const padding = 20;
    const cols = Math.ceil(Math.sqrt(objects.length));
    const maxWidth = Math.max(...objects.map((obj: FabricObject) => (obj.width || 0) * (obj.scaleX || 1)));
    const maxHeight = Math.max(...objects.map((obj: FabricObject) => (obj.height || 0) * (obj.scaleY || 1)));

    objects.forEach((obj: FabricObject, index: number) => {
      const row = Math.floor(index / cols);
      const col = index % cols;

      obj.set({
        left: col * (maxWidth + padding),
        top: row * (maxHeight + padding),
      });
      obj.setCoords();
    });

    canvas.renderAll();
    toast({ title: 'Auto-layout applied!' });
  }, [canvas, toast]);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          AI Assistant
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 p-0 overflow-hidden">
        <Tabs defaultValue="generate" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-3 mx-2">
            <TabsTrigger value="generate" className="text-xs">
              <Wand2 className="w-3 h-3 mr-1" />
              Generate
            </TabsTrigger>
            <TabsTrigger value="analyze" className="text-xs">
              <Accessibility className="w-3 h-3 mr-1" />
              Analyze
            </TabsTrigger>
            <TabsTrigger value="tools" className="text-xs">
              <Zap className="w-3 h-3 mr-1" />
              Tools
            </TabsTrigger>
          </TabsList>

          <ScrollArea className="flex-1">
            {/* Generate Tab */}
            <TabsContent value="generate" className="p-4 space-y-4 mt-0">
              <div className="space-y-2">
                <Label htmlFor="prompt">Design Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe your design... e.g., 'Modern SaaS landing page with hero section'"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={4}
                  className="resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="design-type">Type</Label>
                  <Select value={designType} onValueChange={setDesignType}>
                    <SelectTrigger id="design-type">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="landing_page">Landing Page</SelectItem>
                      <SelectItem value="social_media">Social Media</SelectItem>
                      <SelectItem value="presentation">Presentation</SelectItem>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="general">General</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="design-style">Style</Label>
                  <Select value={designStyle} onValueChange={setDesignStyle}>
                    <SelectTrigger id="design-style">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="modern">Modern</SelectItem>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="bold">Bold</SelectItem>
                      <SelectItem value="corporate">Corporate</SelectItem>
                      <SelectItem value="creative">Creative</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Number of Variants: {numVariants}</Label>
                <Slider
                  value={[numVariants]}
                  onValueChange={([value]) => setNumVariants(value)}
                  min={1}
                  max={5}
                  step={1}
                  className="w-full"
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="accessibility">Accessibility First</Label>
                <Switch
                  id="accessibility"
                  checked={accessibilityFirst}
                  onCheckedChange={setAccessibilityFirst}
                />
              </div>

              <Button
                onClick={generateDesign}
                disabled={loading}
                className="w-full"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                ) : (
                  <><Sparkles className="w-4 h-4 mr-2" /> Generate Design</>
                )}
              </Button>

              {/* Suggestions */}
              {suggestions.length > 0 && (
                <div className="space-y-2 pt-4 border-t">
                  <Label>Generated Variants</Label>
                  {suggestions.map((suggestion, index) => (
                    <Card key={index} className="p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="font-medium text-sm">Variant {index + 1}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {typeof suggestion === 'object' && suggestion !== null && 'description' in suggestion ? (suggestion as { description?: string }).description : 'AI-generated design'}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => onApplySuggestion?.(suggestion)}
                        >
                          Apply
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Analyze Tab */}
            <TabsContent value="analyze" className="p-4 space-y-4 mt-0">
              <Button
                onClick={checkAccessibility}
                disabled={loading}
                variant="outline"
                className="w-full"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Checking...</>
                ) : (
                  <><Accessibility className="w-4 h-4 mr-2" /> Check Accessibility</>
                )}
              </Button>

              <Button
                variant="outline"
                className="w-full"
                disabled={loading}
                onClick={() => void analyzeDesign('layout')}
              >
                <Layout className="w-4 h-4 mr-2" />
                Analyze Layout
              </Button>

              <Button
                variant="outline"
                className="w-full"
                disabled={loading}
                onClick={() => void analyzeDesign('typography')}
              >
                <Type className="w-4 h-4 mr-2" />
                Typography Report
              </Button>
              {report && <section aria-live="polite" className="space-y-3 text-sm"><h3 className="font-semibold">{report.title}</h3><AIResultReport value={report.data} /></section>}
            </TabsContent>

            {/* Tools Tab */}
            <TabsContent value="tools" className="p-4 space-y-4 mt-0">
              <Button
                onClick={generateColorPalette}
                disabled={loading}
                variant="outline"
                className="w-full"
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
                ) : (
                  <><Palette className="w-4 h-4 mr-2" /> Generate Palette</>
                )}
              </Button>

              <Button
                onClick={autoLayout}
                variant="outline"
                className="w-full"
              >
                <Layout className="w-4 h-4 mr-2" />
                Auto-Layout Selection
              </Button>

              <div className="space-y-2"><Label htmlFor="image-prompt">Image description</Label><Textarea id="image-prompt" value={prompt} onChange={event => setPrompt(event.target.value)} placeholder="Describe the image to generate" /></div>
              <Button
                variant="outline"
                className="w-full"
                disabled={loading}
                onClick={() => void generateImage()}
              >
                <ImageIcon className="w-4 h-4 mr-2" />
                AI Image Generation
              </Button>
              {imageUrl && <div className="space-y-2"><a href={imageUrl} target="_blank" rel="noopener noreferrer" className="text-sm underline">Open generated image</a><Button className="w-full" disabled={!canvas || loading} onClick={() => void addImageToCanvas()}>Add image to canvas</Button></div>}

              <div className="pt-4 border-t space-y-2">
                <Label>Brand Colors</Label>
                <div className="flex flex-wrap gap-2">
                  {brandColors.map((color, index) => (
                    <div
                      key={index}
                      className="w-10 h-10 rounded border-2 border-background shadow-sm cursor-pointer"
                      style={{ backgroundColor: color }}
                      onClick={() => {
                        const input = document.createElement('input');
                        input.type = 'color';
                        input.value = color;
                        input.onchange = (e) => {
                          const newColors = [...brandColors];
                          newColors[index] = (e.target as HTMLInputElement).value;
                          setBrandColors(newColors);
                        };
                        input.click();
                      }}
                    />
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-10 h-10 p-0"
                    onClick={() => setBrandColors([...brandColors, '#000000'])}
                  >
                    +
                  </Button>
                </div>
              </div>
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </CardContent>
    </Card>
  );
}

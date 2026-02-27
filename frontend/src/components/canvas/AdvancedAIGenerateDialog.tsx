"use client";

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Loader2, Palette, Layout, Wand2, Grid3x3, Layers, AlignCenter, GitBranch } from 'lucide-react';
import { aiAPI } from '@/lib/design-api';
import { useToast } from '@/hooks/use-toast';

interface AdvancedAIGenerateDialogProps {
  onGenerate: (result: Record<string, unknown>) => void;
  designType?: 'graphic' | 'ui_ux' | 'logo';
  canvasWidth?: number;
  canvasHeight?: number;
}

export const AdvancedAIGenerateDialog: React.FC<AdvancedAIGenerateDialogProps> = ({
  onGenerate,
  designType = 'ui_ux',
  canvasWidth = 1920,
  canvasHeight = 1080,
}) => {
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const [selectedDesignType, setSelectedDesignType] = useState<'graphic' | 'ui_ux' | 'logo'>(designType);
  const [style, setStyle] = useState('modern');
  const [placementStrategy, setPlacementStrategy] = useState('grid');
  const [customColors, setCustomColors] = useState<string[]>([]);
  const [colorInput, setColorInput] = useState('#3B82F6');
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);

    try {
      const requestData: Record<string, unknown> = {
        prompt,
        design_type: selectedDesignType,
        style,
        canvas_width: canvasWidth,
        canvas_height: canvasHeight,
        placement_strategy: placementStrategy,
        include_guidelines: true,
      };

      if (customColors.length > 0) {
        requestData.color_scheme = customColors;
      }

      const result = await aiAPI.generateLayout(prompt, selectedDesignType, requestData);
      onGenerate(result);
      setOpen(false);
      setPrompt('');
      
      toast({
        title: 'Success',
        description: `Professional ${selectedDesignType.replace('_', '/')} design generated!`,
      });
    } catch (error) {
      console.error('Generation error:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate design. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const addColor = () => {
    if (colorInput && !customColors.includes(colorInput)) {
      setCustomColors([...customColors, colorInput]);
    }
  };

  const removeColor = (color: string) => {
    setCustomColors(customColors.filter(c => c !== color));
  };

  const styles = [
    { value: 'modern', label: 'Modern', icon: Wand2 },
    { value: 'minimalist', label: 'Minimalist', icon: Layers },
    { value: 'corporate', label: 'Corporate', icon: Layout },
    { value: 'playful', label: 'Playful', icon: Sparkles },
    { value: 'elegant', label: 'Elegant', icon: Palette },
    { value: 'bold', label: 'Bold', icon: GitBranch },
  ];

  const placementStrategies = [
    { value: 'grid', label: 'Grid Layout', description: 'Organized grid structure', icon: Grid3x3 },
    { value: 'centered', label: 'Centered', description: 'Centered composition', icon: AlignCenter },
    { value: 'layered', label: 'Layered', description: 'Depth and layers', icon: Layers },
    { value: 'flow', label: 'Flow', description: 'Natural flow', icon: GitBranch },
    { value: 'symmetrical', label: 'Symmetrical', description: 'Perfect symmetry', icon: Layout },
  ];

  const examplePrompts = {
    ui_ux: [
      'Modern travel booking app with map integration and search filters',
      'Professional dashboard for analytics with charts, metrics, and data tables',
      'E-commerce product page with image gallery, reviews, and add to cart',
      'Social media profile with timeline, posts, and user info',
      'Landing page for SaaS product with hero section, features, and CTA',
    ],
    graphic: [
      'Summer sale social media post with vibrant colors and bold typography',
      'Music festival poster with dynamic layout and energetic design',
      'Instagram story template for fashion brand with elegant aesthetic',
      'Event invitation card with sophisticated design elements',
      'Product announcement banner with modern gradient background',
    ],
    logo: [
      'Tech startup logo with geometric shapes and blue gradient',
      'Minimalist coffee shop logo with warm earth tones',
      'Professional consulting firm logo with corporate aesthetic',
      'Eco-friendly brand logo with nature-inspired elements',
      'Luxury fashion brand logo with elegant typography',
    ],
  };

  const designTypeInfo = {
    ui_ux: {
      title: 'UI/UX Design',
      description: 'Complete interfaces with components, layouts, and interactions',
      features: ['Component hierarchy', 'Responsive layouts', '8px grid system', 'Accessibility'],
    },
    graphic: {
      title: 'Graphic Design',
      description: 'Visual communications for social media, marketing, and print',
      features: ['Visual hierarchy', 'Typography balance', 'Color harmony', 'Print-ready'],
    },
    logo: {
      title: 'Logo Design',
      description: 'Professional brand marks with symmetry and scalability',
      features: ['Perfect symmetry', 'Multiple variations', 'Scalable design', 'Brand guidelines'],
    },
  };

  const currentDesignInfo = designTypeInfo[selectedDesignType];

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default" size="lg" className="gap-2">
          <Sparkles className="h-5 w-5" />
          AI Generate Professional Design
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-6 w-6 text-primary" />
            Generate Professional Design with AI
          </DialogTitle>
          <DialogDescription>
            Create professional, structured designs with advanced AI generation
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="generate" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="generate">Generate</TabsTrigger>
            <TabsTrigger value="examples">Examples</TabsTrigger>
          </TabsList>

          <TabsContent value="generate" className="space-y-4 mt-4">
            {/* Design Type Selection */}
            <div className="space-y-2">
              <Label htmlFor="design-type" className="text-base font-semibold">Design Type</Label>
              <Select
                value={selectedDesignType}
                onValueChange={(value: 'graphic' | 'ui_ux' | 'logo') => setSelectedDesignType(value)}
              >
                <SelectTrigger className="h-12">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ui_ux">
                    <div className="flex items-center gap-2">
                      <Layout className="h-4 w-4" />
                      UI/UX Design
                    </div>
                  </SelectItem>
                  <SelectItem value="graphic">
                    <div className="flex items-center gap-2">
                      <Palette className="h-4 w-4" />
                      Graphic Design
                    </div>
                  </SelectItem>
                  <SelectItem value="logo">
                    <div className="flex items-center gap-2">
                      <Wand2 className="h-4 w-4" />
                      Logo Design
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
              
              {/* Design type info */}
              <div className="bg-muted/50 rounded-lg p-3 space-y-2">
                <p className="text-sm font-medium">{currentDesignInfo.title}</p>
                <p className="text-xs text-muted-foreground">{currentDesignInfo.description}</p>
                <div className="flex flex-wrap gap-1">
                  {currentDesignInfo.features.map((feature) => (
                    <Badge key={feature} variant="secondary" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Prompt */}
            <div className="space-y-2">
              <Label htmlFor="prompt" className="text-base font-semibold">Your Design Prompt</Label>
              <Textarea
                id="prompt"
                placeholder={`Describe your ${currentDesignInfo.title.toLowerCase()} in detail...`}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Be specific about elements, colors, style, and layout you want
              </p>
            </div>

            {/* Style Selection */}
            <div className="space-y-2">
              <Label className="text-base font-semibold">Design Style</Label>
              <div className="grid grid-cols-3 gap-2">
                {styles.map((styleOption) => {
                  const Icon = styleOption.icon;
                  return (
                    <button
                      key={styleOption.value}
                      onClick={() => setStyle(styleOption.value)}
                      className={`flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all ${
                        style === styleOption.value
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="text-sm font-medium">{styleOption.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Advanced Options */}
            <div className="space-y-2">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-sm font-medium text-primary hover:underline"
              >
                {showAdvanced ? '− Hide' : '+ Show'} Advanced Options
              </button>

              {showAdvanced && (
                <div className="space-y-4 pt-2 border-t">
                  {/* Placement Strategy */}
                  <div className="space-y-2">
                    <Label className="text-sm font-semibold">Placement Strategy</Label>
                    <Select value={placementStrategy} onValueChange={setPlacementStrategy}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {placementStrategies.map((strategy) => (
                          <SelectItem key={strategy.value} value={strategy.value}>
                            <div className="flex items-center gap-2">
                              <strategy.icon className="h-3 w-3" />
                              <span>{strategy.label}</span>
                              <span className="text-xs text-muted-foreground">
                                — {strategy.description}
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Custom Colors */}
                  <div className="space-y-2">
                    <Label className="text-sm font-semibold">Brand Colors (Optional)</Label>
                    <div className="flex gap-2">
                      <Input
                        type="color"
                        value={colorInput}
                        onChange={(e) => setColorInput(e.target.value)}
                        className="w-20 h-10"
                      />
                      <Input
                        type="text"
                        value={colorInput}
                        onChange={(e) => setColorInput(e.target.value)}
                        placeholder="#3B82F6"
                        className="flex-1"
                      />
                      <Button onClick={addColor} size="sm">Add</Button>
                    </div>
                    {customColors.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {customColors.map((color) => (
                          <div
                            key={color}
                            className="flex items-center gap-1 pl-1 pr-2 py-1 rounded-md border bg-background"
                          >
                            <div
                              className="w-4 h-4 rounded border"
                              style={{ backgroundColor: color }}
                            />
                            <span className="text-xs font-mono">{color}</span>
                            <button
                              onClick={() => removeColor(color)}
                              className="text-muted-foreground hover:text-foreground"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Canvas Size */}
                  <div className="space-y-2">
                    <Label className="text-sm font-semibold">Canvas Size</Label>
                    <div className="text-sm text-muted-foreground">
                      {canvasWidth} × {canvasHeight} px
                    </div>
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="examples" className="space-y-3 mt-4">
            <div className="space-y-2">
              <Label className="text-sm font-semibold">Example Prompts for {currentDesignInfo.title}</Label>
              <div className="space-y-1 max-h-[400px] overflow-y-auto">
                {examplePrompts[selectedDesignType].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setPrompt(example);
                      toast({ title: 'Prompt copied', description: 'Click Generate tab to continue' });
                    }}
                    className="block w-full text-left text-sm p-3 rounded-lg border hover:border-primary hover:bg-accent transition-all"
                  >
                    <span className="font-medium">Example {index + 1}:</span>
                    <p className="text-muted-foreground mt-1">{example}</p>
                  </button>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => setOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleGenerate} disabled={loading || !prompt.trim()}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Professional Design
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AdvancedAIGenerateDialog;

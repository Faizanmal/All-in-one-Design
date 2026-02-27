"use client";

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import {
  Play, Pause, SkipBack, SkipForward, RotateCcw,
  Plus, Copy, Upload, Code, FileJson,
  ChevronLeft, ChevronRight,
  Settings, Eye, EyeOff, Lock, Unlock, Maximize2, Sparkles
} from 'lucide-react';

// Types
interface Keyframe {
  id: string;
  time: number; // percentage 0-100
  properties: Record<string, number | string>;
  easing: string;
}

interface AnimationTrack {
  id: string;
  name: string;
  property: string;
  keyframes: Keyframe[];
  visible: boolean;
  locked: boolean;
}

interface Animation {
  id: string;
  name: string;
  duration: number;
  delay: number;
  easing: string;
  iterations: number;
  direction: string;
  tracks: AnimationTrack[];
}

interface MicroInteraction {
  id: string;
  name: string;
  type: string;
  preview: string;
  css: string;
}

const EASING_OPTIONS = [
  { label: 'Linear', value: 'linear' },
  { label: 'Ease', value: 'ease' },
  { label: 'Ease In', value: 'ease-in' },
  { label: 'Ease Out', value: 'ease-out' },
  { label: 'Ease In Out', value: 'ease-in-out' },
  { label: 'Ease In Quad', value: 'cubic-bezier(0.55, 0.085, 0.68, 0.53)' },
  { label: 'Ease Out Quad', value: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)' },
  { label: 'Ease In Cubic', value: 'cubic-bezier(0.55, 0.055, 0.675, 0.19)' },
  { label: 'Ease Out Cubic', value: 'cubic-bezier(0.215, 0.61, 0.355, 1)' },
  { label: 'Ease In Back', value: 'cubic-bezier(0.6, -0.28, 0.735, 0.045)' },
  { label: 'Ease Out Back', value: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' },
  { label: 'Spring', value: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' },
];

const ANIMATION_PRESETS = [
  { id: '1', name: 'Fade In', category: 'entrance', duration: 0.5 },
  { id: '2', name: 'Fade Out', category: 'exit', duration: 0.5 },
  { id: '3', name: 'Slide Up', category: 'entrance', duration: 0.6 },
  { id: '4', name: 'Slide Down', category: 'exit', duration: 0.6 },
  { id: '5', name: 'Scale In', category: 'entrance', duration: 0.4 },
  { id: '6', name: 'Scale Out', category: 'exit', duration: 0.4 },
  { id: '7', name: 'Bounce', category: 'emphasis', duration: 1.0 },
  { id: '8', name: 'Shake', category: 'emphasis', duration: 0.5 },
  { id: '9', name: 'Pulse', category: 'emphasis', duration: 1.0 },
  { id: '10', name: 'Spin', category: 'emphasis', duration: 1.0 },
  { id: '11', name: 'Flip X', category: '3d', duration: 0.6 },
  { id: '12', name: 'Flip Y', category: '3d', duration: 0.6 },
];

const MICRO_INTERACTIONS: MicroInteraction[] = [
  { id: '1', name: 'Button Hover', type: 'button', preview: '🔘', css: '.btn:hover { transform: scale(1.05); }' },
  { id: '2', name: 'Card Lift', type: 'hover', preview: '📋', css: '.card:hover { transform: translateY(-4px); box-shadow: 0 10px 40px rgba(0,0,0,0.2); }' },
  { id: '3', name: 'Loading Spinner', type: 'loading', preview: '⏳', css: '@keyframes spin { to { transform: rotate(360deg); } }' },
  { id: '4', name: 'Success Check', type: 'success', preview: '✅', css: '@keyframes checkmark { 0% { stroke-dashoffset: 100; } 100% { stroke-dashoffset: 0; } }' },
  { id: '5', name: 'Ripple Effect', type: 'button', preview: '💧', css: '@keyframes ripple { to { transform: scale(4); opacity: 0; } }' },
  { id: '6', name: 'Toggle Switch', type: 'toggle', preview: '🔀', css: '.toggle:checked + .slider { transform: translateX(20px); }' },
  { id: '7', name: 'Menu Slide', type: 'menu', preview: '☰', css: '.menu { transform: translateX(-100%); transition: transform 0.3s; }' },
  { id: '8', name: 'Toast Enter', type: 'notification', preview: '🔔', css: '@keyframes slideInRight { from { transform: translateX(100%); } }' },
];

export default function AnimationStudioPage() {
  const { toast } = useToast();
  const timelineRef = useRef<HTMLDivElement>(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [selectedKeyframeId, setSelectedKeyframeId] = useState<string | null>(null);
  
  const [animation, setAnimation] = useState<Animation>({
    id: '1',
    name: 'My Animation',
    duration: 1,
    delay: 0,
    easing: 'ease',
    iterations: 1,
    direction: 'normal',
    tracks: [
      {
        id: '1',
        name: 'Opacity',
        property: 'opacity',
        visible: true,
        locked: false,
        keyframes: [
          { id: '1', time: 0, properties: { opacity: 0 }, easing: 'ease' },
          { id: '2', time: 100, properties: { opacity: 1 }, easing: 'ease' },
        ]
      },
      {
        id: '2',
        name: 'Transform',
        property: 'transform',
        visible: true,
        locked: false,
        keyframes: [
          { id: '3', time: 0, properties: { translateY: 20, scale: 0.9 }, easing: 'ease-out' },
          { id: '4', time: 100, properties: { translateY: 0, scale: 1 }, easing: 'ease-out' },
        ]
      }
    ]
  });

  const togglePlay = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      // Start animation playback
      const startTime = Date.now();
      const duration = animation.duration * 1000;
      
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min((elapsed / duration) * 100, 100);
        setCurrentTime(progress);
        
        if (progress < 100 && isPlaying) {
          requestAnimationFrame(animate);
        } else {
          setIsPlaying(false);
        }
      };
      
      requestAnimationFrame(animate);
    }
  };

  const addTrack = (property: string) => {
    const newTrack: AnimationTrack = {
      id: Date.now().toString(),
      name: property.charAt(0).toUpperCase() + property.slice(1),
      property,
      visible: true,
      locked: false,
      keyframes: [
        { id: Date.now().toString() + '-1', time: 0, properties: {}, easing: 'ease' },
        { id: Date.now().toString() + '-2', time: 100, properties: {}, easing: 'ease' },
      ]
    };
    setAnimation(prev => ({
      ...prev,
      tracks: [...prev.tracks, newTrack]
    }));
  };

  const addKeyframe = (trackId: string, time: number) => {
    setAnimation(prev => ({
      ...prev,
      tracks: prev.tracks.map(track => {
        if (track.id === trackId) {
          return {
            ...track,
            keyframes: [...track.keyframes, {
              id: Date.now().toString(),
              time,
              properties: {},
              easing: 'ease'
            }].sort((a, b) => a.time - b.time)
          };
        }
        return track;
      })
    }));
  };

  const deleteKeyframe = (trackId: string, keyframeId: string) => {
    setAnimation(prev => ({
      ...prev,
      tracks: prev.tracks.map(track => {
        if (track.id === trackId) {
          return {
            ...track,
            keyframes: track.keyframes.filter(kf => kf.id !== keyframeId)
          };
        }
        return track;
      })
    }));
  };

  const generateCSS = () => {
    const animName = animation.name.toLowerCase().replace(/\s+/g, '-');
    let css = `/* Animation: ${animation.name} */\n`;
    css += `.${animName} {\n`;
    css += `  animation-name: ${animName};\n`;
    css += `  animation-duration: ${animation.duration}s;\n`;
    css += `  animation-delay: ${animation.delay}s;\n`;
    css += `  animation-timing-function: ${animation.easing};\n`;
    css += `  animation-iteration-count: ${animation.iterations === -1 ? 'infinite' : animation.iterations};\n`;
    css += `  animation-direction: ${animation.direction};\n`;
    css += `  animation-fill-mode: forwards;\n`;
    css += `}\n\n`;
    css += `@keyframes ${animName} {\n`;
    
    // Collect all unique time points
    const timePoints = new Set<number>();
    animation.tracks.forEach(track => {
      track.keyframes.forEach(kf => timePoints.add(kf.time));
    });
    
    Array.from(timePoints).sort((a, b) => a - b).forEach(time => {
      css += `  ${time}% {\n`;
      animation.tracks.forEach(track => {
        const kf = track.keyframes.find(k => k.time === time);
        if (kf) {
          Object.entries(kf.properties).forEach(([prop, value]) => {
            css += `    ${prop}: ${value};\n`;
          });
        }
      });
      css += `  }\n`;
    });
    
    css += `}\n`;
    
    return css;
  };

  const exportCSS = () => {
    const css = generateCSS();
    navigator.clipboard.writeText(css);
    toast({ title: 'CSS copied to clipboard!' });
  };

  const exportLottie = () => {
    toast({ title: 'Exporting as Lottie...', description: 'This feature will convert to Lottie JSON format' });
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Toolbar */}
      <div className="h-14 border-b flex items-center justify-between px-4 bg-card">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => setLeftPanelOpen(!leftPanelOpen)}>
            {leftPanelOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <Sparkles className="h-5 w-5 text-primary" />
          <span className="font-semibold text-lg">Animation Studio</span>
        </div>

        <div className="flex items-center gap-2">
          <Input
            value={animation.name}
            onChange={(e) => setAnimation(prev => ({ ...prev, name: e.target.value }))}
            className="w-48"
          />
          
          <Separator orientation="vertical" className="h-6" />
          
          <div className="flex items-center gap-2">
            <Label className="text-sm">Duration:</Label>
            <Input
              type="number"
              value={animation.duration}
              onChange={(e) => setAnimation(prev => ({ ...prev, duration: parseFloat(e.target.value) || 1 }))}
              className="w-20"
              step="0.1"
              min="0.1"
            />
            <span className="text-sm text-muted-foreground">s</span>
          </div>

          <Select value={animation.easing} onValueChange={(v) => setAnimation(prev => ({ ...prev, easing: v }))}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Easing" />
            </SelectTrigger>
            <SelectContent>
              {EASING_OPTIONS.map(opt => (
                <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Separator orientation="vertical" className="h-6" />

          <Button variant="outline" size="sm" onClick={exportCSS}>
            <Code className="h-4 w-4 mr-2" />
            Export CSS
          </Button>
          <Button variant="outline" size="sm" onClick={exportLottie}>
            <FileJson className="h-4 w-4 mr-2" />
            Export Lottie
          </Button>

          <Separator orientation="vertical" className="h-6" />

          <Button variant="ghost" size="icon" onClick={() => setRightPanelOpen(!rightPanelOpen)}>
            {rightPanelOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Presets & Library */}
        {leftPanelOpen && (
          <div className="w-72 border-r bg-card flex flex-col">
            <Tabs defaultValue="presets" className="flex-1 flex flex-col">
              <TabsList className="w-full justify-start rounded-none border-b bg-transparent px-2">
                <TabsTrigger value="presets">Presets</TabsTrigger>
                <TabsTrigger value="micro">Micro</TabsTrigger>
                <TabsTrigger value="lottie">Lottie</TabsTrigger>
              </TabsList>

              <ScrollArea className="flex-1">
                <TabsContent value="presets" className="p-3 mt-0 space-y-3">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Entrance</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {ANIMATION_PRESETS.filter(p => p.category === 'entrance').map(preset => (
                        <Button
                          key={preset.id}
                          variant="outline"
                          size="sm"
                          className="justify-start text-xs"
                          onClick={() => toast({ title: `Applied: ${preset.name}` })}
                        >
                          {preset.name}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Exit</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {ANIMATION_PRESETS.filter(p => p.category === 'exit').map(preset => (
                        <Button
                          key={preset.id}
                          variant="outline"
                          size="sm"
                          className="justify-start text-xs"
                          onClick={() => toast({ title: `Applied: ${preset.name}` })}
                        >
                          {preset.name}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Emphasis</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {ANIMATION_PRESETS.filter(p => p.category === 'emphasis').map(preset => (
                        <Button
                          key={preset.id}
                          variant="outline"
                          size="sm"
                          className="justify-start text-xs"
                          onClick={() => toast({ title: `Applied: ${preset.name}` })}
                        >
                          {preset.name}
                        </Button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-sm font-medium">3D</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {ANIMATION_PRESETS.filter(p => p.category === '3d').map(preset => (
                        <Button
                          key={preset.id}
                          variant="outline"
                          size="sm"
                          className="justify-start text-xs"
                          onClick={() => toast({ title: `Applied: ${preset.name}` })}
                        >
                          {preset.name}
                        </Button>
                      ))}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="micro" className="p-3 mt-0">
                  <div className="space-y-2">
                    {MICRO_INTERACTIONS.map(interaction => (
                      <Card key={interaction.id} className="cursor-pointer hover:bg-accent transition-colors">
                        <CardContent className="p-3 flex items-center gap-3">
                          <span className="text-2xl">{interaction.preview}</span>
                          <div className="flex-1">
                            <p className="font-medium text-sm">{interaction.name}</p>
                            <Badge variant="secondary" className="text-xs">{interaction.type}</Badge>
                          </div>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Plus className="h-4 w-4" />
                          </Button>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="lottie" className="p-3 mt-0">
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full">
                      <Upload className="h-4 w-4 mr-2" />
                      Import Lottie
                    </Button>
                    
                    <div className="text-center text-muted-foreground py-8">
                      <FileJson className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No Lottie files yet</p>
                      <p className="text-xs">Import .json files to get started</p>
                    </div>
                  </div>
                </TabsContent>
              </ScrollArea>
            </Tabs>
          </div>
        )}

        {/* Center - Preview & Timeline */}
        <div className="flex-1 flex flex-col">
          {/* Preview Area */}
          <div className="flex-1 bg-muted/30 flex items-center justify-center relative">
            <div className="relative">
              {/* Animated Element Preview */}
              <div 
                className="w-32 h-32 rounded-xl bg-linear-to-br from-primary to-purple-600 shadow-lg flex items-center justify-center text-white font-semibold"
                style={{
                  animation: isPlaying ? `preview ${animation.duration}s ${animation.easing} ${animation.iterations === -1 ? 'infinite' : animation.iterations} ${animation.direction}` : 'none',
                }}
              >
                Preview
              </div>
            </div>

            {/* Preview Controls Overlay */}
            <div className="absolute top-4 right-4 flex gap-2">
              <Button variant="secondary" size="icon">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Timeline */}
          <div className="h-64 border-t bg-card flex flex-col">
            {/* Timeline Controls */}
            <div className="h-12 border-b flex items-center justify-between px-4">
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => setCurrentTime(0)}>
                  <SkipBack className="h-4 w-4" />
                </Button>
                <Button variant="default" size="icon" onClick={togglePlay}>
                  {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setCurrentTime(100)}>
                  <SkipForward className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setCurrentTime(0)}>
                  <RotateCcw className="h-4 w-4" />
                </Button>
                <Separator orientation="vertical" className="h-6 mx-2" />
                <span className="text-sm font-mono">
                  {(currentTime * animation.duration / 100).toFixed(2)}s / {animation.duration}s
                </span>
              </div>

              <div className="flex items-center gap-2">
                <Select defaultValue="opacity" onValueChange={addTrack}>
                  <SelectTrigger className="w-[140px]">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Track
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="opacity">Opacity</SelectItem>
                    <SelectItem value="transform">Transform</SelectItem>
                    <SelectItem value="scale">Scale</SelectItem>
                    <SelectItem value="rotate">Rotate</SelectItem>
                    <SelectItem value="translateX">Translate X</SelectItem>
                    <SelectItem value="translateY">Translate Y</SelectItem>
                    <SelectItem value="color">Color</SelectItem>
                    <SelectItem value="backgroundColor">Background</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Timeline Tracks */}
            <div className="flex-1 flex overflow-hidden">
              {/* Track Labels */}
              <div className="w-48 border-r flex flex-col">
                {animation.tracks.map(track => (
                  <div
                    key={track.id}
                    className="h-10 flex items-center px-3 gap-2 border-b hover:bg-muted/50"
                  >
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      {track.visible ? <Eye className="h-3 w-3" /> : <EyeOff className="h-3 w-3" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      {track.locked ? <Lock className="h-3 w-3" /> : <Unlock className="h-3 w-3" />}
                    </Button>
                    <span className="text-sm flex-1 truncate">{track.name}</span>
                  </div>
                ))}
              </div>

              {/* Timeline Grid */}
              <div className="flex-1 overflow-x-auto" ref={timelineRef}>
                <div className="relative min-w-full h-full">
                  {/* Time Ruler */}
                  <div className="h-6 border-b flex items-end px-2 text-xs text-muted-foreground sticky top-0 bg-card">
                    {[0, 25, 50, 75, 100].map(t => (
                      <div key={t} className="absolute" style={{ left: `${t}%` }}>
                        {(t * animation.duration / 100).toFixed(1)}s
                      </div>
                    ))}
                  </div>

                  {/* Playhead */}
                  <div 
                    className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10"
                    style={{ left: `${currentTime}%` }}
                  >
                    <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rotate-45" />
                  </div>

                  {/* Track Rows */}
                  {animation.tracks.map(track => (
                    <div
                      key={track.id}
                      className="h-10 border-b relative"
                      onClick={(e) => {
                        const rect = e.currentTarget.getBoundingClientRect();
                        const time = Math.round(((e.clientX - rect.left) / rect.width) * 100);
                        addKeyframe(track.id, time);
                      }}
                    >
                      {/* Grid Lines */}
                      <div className="absolute inset-0 flex">
                        {[0, 25, 50, 75, 100].map(t => (
                          <div key={t} className="absolute h-full border-l border-dashed border-muted" style={{ left: `${t}%` }} />
                        ))}
                      </div>

                      {/* Keyframes */}
                      {track.keyframes.map(keyframe => (
                        <div
                          key={keyframe.id}
                          className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-4 h-4 rounded-sm cursor-pointer transition-all ${
                            selectedKeyframeId === keyframe.id 
                              ? 'bg-primary scale-125 shadow-lg' 
                              : 'bg-primary/70 hover:bg-primary hover:scale-110'
                          }`}
                          style={{ left: `${keyframe.time}%` }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedKeyframeId(keyframe.id);
                          }}
                          onDoubleClick={(e) => {
                            e.stopPropagation();
                            deleteKeyframe(track.id, keyframe.id);
                          }}
                        />
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Properties */}
        {rightPanelOpen && (
          <div className="w-72 border-l bg-card flex flex-col">
            <div className="p-3 border-b">
              <h3 className="font-semibold flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Properties
              </h3>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-4 space-y-4">
                <div className="space-y-2">
                  <Label>Duration</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      value={animation.duration}
                      onChange={(e) => setAnimation(prev => ({ ...prev, duration: parseFloat(e.target.value) || 1 }))}
                      step="0.1"
                      min="0.1"
                    />
                    <span className="text-sm text-muted-foreground self-center">sec</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Delay</Label>
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      value={animation.delay}
                      onChange={(e) => setAnimation(prev => ({ ...prev, delay: parseFloat(e.target.value) || 0 }))}
                      step="0.1"
                      min="0"
                    />
                    <span className="text-sm text-muted-foreground self-center">sec</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Easing</Label>
                  <Select value={animation.easing} onValueChange={(v) => setAnimation(prev => ({ ...prev, easing: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EASING_OPTIONS.map(opt => (
                        <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Iterations</Label>
                  <div className="flex gap-2 items-center">
                    <Input
                      type="number"
                      value={animation.iterations === -1 ? '' : animation.iterations}
                      onChange={(e) => setAnimation(prev => ({ ...prev, iterations: parseInt(e.target.value) || 1 }))}
                      min="1"
                      disabled={animation.iterations === -1}
                    />
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={animation.iterations === -1}
                        onCheckedChange={(checked) => setAnimation(prev => ({ ...prev, iterations: checked ? -1 : 1 }))}
                      />
                      <Label className="text-xs">Infinite</Label>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Direction</Label>
                  <Select value={animation.direction} onValueChange={(v) => setAnimation(prev => ({ ...prev, direction: v }))}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="reverse">Reverse</SelectItem>
                      <SelectItem value="alternate">Alternate</SelectItem>
                      <SelectItem value="alternate-reverse">Alternate Reverse</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Separator />

                {selectedKeyframeId && (
                  <div className="space-y-3">
                    <Label className="text-sm font-medium">Keyframe Properties</Label>
                    
                    <div className="space-y-2">
                      <Label className="text-xs text-muted-foreground">Position (%)</Label>
                      <Slider defaultValue={[50]} max={100} step={1} />
                    </div>

                    <div className="space-y-2">
                      <Label className="text-xs text-muted-foreground">Easing</Label>
                      <Select defaultValue="ease">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {EASING_OPTIONS.map(opt => (
                            <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}

                <Separator />

                <div className="space-y-2">
                  <Label className="text-sm font-medium">Generated CSS</Label>
                  <pre className="text-xs bg-muted p-3 rounded-lg overflow-x-auto max-h-48">
                    {generateCSS()}
                  </pre>
                  <Button variant="outline" size="sm" className="w-full" onClick={exportCSS}>
                    <Copy className="h-4 w-4 mr-2" />
                    Copy CSS
                  </Button>
                </div>
              </div>
            </ScrollArea>
          </div>
        )}
      </div>
    </div>
  );
}

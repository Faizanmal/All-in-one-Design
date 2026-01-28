"use client";

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import {
  Box, Layers, Move3D, RotateCcw, ZoomIn, ZoomOut, Sun,
  Upload, Download, Eye, Play, Pause, Smartphone, Monitor,
  Grid3X3, Cylinder, Cone, Circle, Square,
  Lightbulb, Share2, Maximize2,
  ChevronLeft, ChevronRight, Plus, Trash2, Copy, Lock
} from 'lucide-react';

// Types
interface Model3D {
  id: string;
  name: string;
  type: string;
  position: { x: number; y: number; z: number };
  rotation: { x: number; y: number; z: number };
  scale: { x: number; y: number; z: number };
  visible: boolean;
  locked: boolean;
  material?: {
    color: string;
    metalness: number;
    roughness: number;
    opacity: number;
  };
}

interface Scene3DState {
  models: Model3D[];
  selectedModelId: string | null;
  camera: {
    position: { x: number; y: number; z: number };
    target: { x: number; y: number; z: number };
    fov: number;
  };
  lighting: {
    ambient: { intensity: number; color: string };
    directional: { intensity: number; color: string; position: { x: number; y: number; z: number } };
  };
  environment: {
    background: string;
    showGrid: boolean;
    showAxes: boolean;
  };
}

export default function Studio3DPage() {
  const { toast } = useToast();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [viewMode, setViewMode] = useState<'perspective' | 'top' | 'front' | 'side'>('perspective');
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'mobile' | 'ar' | 'vr'>('desktop');
  const [leftPanelOpen, setLeftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);

  const [scene, setScene] = useState<Scene3DState>({
    models: [
      {
        id: '1',
        name: 'Cube 1',
        type: 'cube',
        position: { x: 0, y: 0, z: 0 },
        rotation: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        visible: true,
        locked: false,
        material: { color: '#6366f1', metalness: 0.5, roughness: 0.5, opacity: 1 }
      }
    ],
    selectedModelId: '1',
    camera: {
      position: { x: 5, y: 5, z: 5 },
      target: { x: 0, y: 0, z: 0 },
      fov: 75
    },
    lighting: {
      ambient: { intensity: 0.5, color: '#ffffff' },
      directional: { intensity: 1, color: '#ffffff', position: { x: 5, y: 10, z: 7 } }
    },
    environment: {
      background: '#1a1a2e',
      showGrid: true,
      showAxes: true
    }
  });

  const selectedModel = scene.models.find(m => m.id === scene.selectedModelId);

  const addPrimitive = (type: string) => {
    const newModel: Model3D = {
      id: Date.now().toString(),
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${scene.models.length + 1}`,
      type,
      position: { x: 0, y: 0, z: 0 },
      rotation: { x: 0, y: 0, z: 0 },
      scale: { x: 1, y: 1, z: 1 },
      visible: true,
      locked: false,
      material: { color: '#6366f1', metalness: 0.5, roughness: 0.5, opacity: 1 }
    };
    setScene(prev => ({
      ...prev,
      models: [...prev.models, newModel],
      selectedModelId: newModel.id
    }));
    toast({ title: `Added ${type}` });
  };

  const updateSelectedModel = (updates: Partial<Model3D>) => {
    if (!scene.selectedModelId) return;
    setScene(prev => ({
      ...prev,
      models: prev.models.map(m =>
        m.id === prev.selectedModelId ? { ...m, ...updates } : m
      )
    }));
  };

  const deleteSelectedModel = () => {
    if (!scene.selectedModelId) return;
    setScene(prev => ({
      ...prev,
      models: prev.models.filter(m => m.id !== prev.selectedModelId),
      selectedModelId: prev.models.length > 1 ? prev.models[0].id : null
    }));
    toast({ title: 'Model deleted' });
  };

  const duplicateSelectedModel = () => {
    if (!selectedModel) return;
    const newModel: Model3D = {
      ...selectedModel,
      id: Date.now().toString(),
      name: `${selectedModel.name} (Copy)`,
      position: {
        x: selectedModel.position.x + 1,
        y: selectedModel.position.y,
        z: selectedModel.position.z
      }
    };
    setScene(prev => ({
      ...prev,
      models: [...prev.models, newModel],
      selectedModelId: newModel.id
    }));
    toast({ title: 'Model duplicated' });
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedFormats = ['gltf', 'glb', 'obj', 'fbx', 'stl'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    
    if (!ext || !allowedFormats.includes(ext)) {
      toast({
        title: 'Unsupported format',
        description: `Allowed formats: ${allowedFormats.join(', ')}`,
        variant: 'destructive'
      });
      return;
    }

    toast({ title: 'Importing model...', description: file.name });
    // In production, upload to backend and process
  };

  const exportScene = (format: string) => {
    toast({ title: `Exporting as ${format.toUpperCase()}...` });
    // In production, call backend export API
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Toolbar */}
      <div className="h-14 border-b flex items-center justify-between px-4 bg-card">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => setLeftPanelOpen(!leftPanelOpen)}>
            {leftPanelOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
          <Separator orientation="vertical" className="h-6" />
          <span className="font-semibold text-lg">3D Studio</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Primitives */}
          <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
            <Button variant="ghost" size="icon" onClick={() => addPrimitive('cube')} title="Add Cube">
              <Box className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => addPrimitive('sphere')} title="Add Sphere">
              <Circle className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => addPrimitive('cylinder')} title="Add Cylinder">
              <Cylinder className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => addPrimitive('cone')} title="Add Cone">
              <Cone className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => addPrimitive('plane')} title="Add Plane">
              <Square className="h-4 w-4" />
            </Button>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Import/Export */}
          <div className="flex items-center gap-1">
            <input
              type="file"
              id="model-upload"
              className="hidden"
              accept=".gltf,.glb,.obj,.fbx,.stl"
              onChange={handleFileUpload}
            />
            <Button variant="outline" size="sm" onClick={() => document.getElementById('model-upload')?.click()}>
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <Select onValueChange={exportScene}>
              <SelectTrigger className="w-[100px]">
                <Download className="h-4 w-4 mr-2" />
                Export
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="gltf">GLTF</SelectItem>
                <SelectItem value="glb">GLB</SelectItem>
                <SelectItem value="obj">OBJ</SelectItem>
                <SelectItem value="usdz">USDZ (AR)</SelectItem>
                <SelectItem value="png">PNG</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* View Mode */}
          <Select value={viewMode} onValueChange={(v) => setViewMode(v as typeof viewMode)}>
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="perspective">Perspective</SelectItem>
              <SelectItem value="top">Top</SelectItem>
              <SelectItem value="front">Front</SelectItem>
              <SelectItem value="side">Side</SelectItem>
            </SelectContent>
          </Select>

          {/* Preview Device */}
          <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
            <Button
              variant={previewDevice === 'desktop' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setPreviewDevice('desktop')}
            >
              <Monitor className="h-4 w-4" />
            </Button>
            <Button
              variant={previewDevice === 'mobile' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setPreviewDevice('mobile')}
            >
              <Smartphone className="h-4 w-4" />
            </Button>
            <Button
              variant={previewDevice === 'ar' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setPreviewDevice('ar')}
            >
              <Eye className="h-4 w-4" />
            </Button>
          </div>

          <Separator orientation="vertical" className="h-6" />

          <Button variant="ghost" size="icon" onClick={() => setRightPanelOpen(!rightPanelOpen)}>
            {rightPanelOpen ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Scene Hierarchy */}
        {leftPanelOpen && (
          <div className="w-64 border-r bg-card flex flex-col">
            <div className="p-3 border-b">
              <h3 className="font-semibold flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Scene Hierarchy
              </h3>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-2 space-y-1">
                {scene.models.map(model => (
                  <div
                    key={model.id}
                    className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                      model.id === scene.selectedModelId ? 'bg-primary/10 border border-primary' : 'hover:bg-muted'
                    }`}
                    onClick={() => setScene(prev => ({ ...prev, selectedModelId: model.id }))}
                  >
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={(e) => {
                        e.stopPropagation();
                        updateSelectedModel({ visible: !model.visible });
                      }}
                    >
                      {model.visible ? <Eye className="h-3 w-3" /> : <Eye className="h-3 w-3 opacity-30" />}
                    </Button>
                    <Box className="h-4 w-4 text-muted-foreground" />
                    <span className="flex-1 truncate text-sm">{model.name}</span>
                    {model.locked && <Lock className="h-3 w-3 text-muted-foreground" />}
                  </div>
                ))}
              </div>
            </ScrollArea>
            <div className="p-2 border-t">
              <Button className="w-full" size="sm" onClick={() => addPrimitive('cube')}>
                <Plus className="h-4 w-4 mr-2" />
                Add Object
              </Button>
            </div>
          </div>
        )}

        {/* 3D Canvas */}
        <div className="flex-1 relative bg-[#1a1a2e]">
          <canvas
            ref={canvasRef}
            className="w-full h-full"
            style={{ background: scene.environment.background }}
          />
          
          {/* Canvas Overlay UI */}
          <div className="absolute top-4 left-4 flex flex-col gap-2">
            <div className="bg-card/80 backdrop-blur rounded-lg p-2 flex flex-col gap-1">
              <Button variant="ghost" size="icon" title="Zoom In">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" title="Zoom Out">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" title="Reset View">
                <RotateCcw className="h-4 w-4" />
              </Button>
              <Separator />
              <Button variant="ghost" size="icon" title="Fullscreen">
                <Maximize2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Transform Tools */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-card/80 backdrop-blur rounded-lg p-2 flex gap-1">
            <Button variant="secondary" size="sm">
              <Move3D className="h-4 w-4 mr-2" />
              Move
            </Button>
            <Button variant="ghost" size="sm">
              <RotateCcw className="h-4 w-4 mr-2" />
              Rotate
            </Button>
            <Button variant="ghost" size="sm">
              <Box className="h-4 w-4 mr-2" />
              Scale
            </Button>
          </div>

          {/* Grid/Axes Toggle */}
          <div className="absolute top-4 right-4 bg-card/80 backdrop-blur rounded-lg p-2 flex gap-2">
            <Button
              variant={scene.environment.showGrid ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setScene(prev => ({
                ...prev,
                environment: { ...prev.environment, showGrid: !prev.environment.showGrid }
              }))}
              title="Toggle Grid"
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
          </div>

          {/* Playback Controls for Animations */}
          <div className="absolute bottom-4 right-4 bg-card/80 backdrop-blur rounded-lg p-2 flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={() => setIsPlaying(!isPlaying)}>
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </Button>
            <span className="text-sm text-muted-foreground">0:00 / 0:00</span>
          </div>

          {/* 3D Canvas Placeholder */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-center text-muted-foreground">
              <Box className="h-24 w-24 mx-auto mb-4 opacity-20" />
              <p className="text-lg">WebGL 3D Canvas</p>
              <p className="text-sm">Three.js rendering area</p>
            </div>
          </div>
        </div>

        {/* Right Panel - Properties */}
        {rightPanelOpen && (
          <div className="w-80 border-l bg-card flex flex-col">
            <Tabs defaultValue="transform" className="flex-1 flex flex-col">
              <TabsList className="w-full justify-start rounded-none border-b bg-transparent px-2">
                <TabsTrigger value="transform">Transform</TabsTrigger>
                <TabsTrigger value="material">Material</TabsTrigger>
                <TabsTrigger value="lighting">Lighting</TabsTrigger>
                <TabsTrigger value="ar">AR</TabsTrigger>
              </TabsList>

              <ScrollArea className="flex-1">
                <TabsContent value="transform" className="p-4 space-y-4 mt-0">
                  {selectedModel ? (
                    <>
                      <div className="flex items-center justify-between">
                        <Input
                          value={selectedModel.name}
                          onChange={(e) => updateSelectedModel({ name: e.target.value })}
                          className="font-semibold"
                        />
                        <div className="flex gap-1">
                          <Button variant="ghost" size="icon" onClick={duplicateSelectedModel}>
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={deleteSelectedModel}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label>Position</Label>
                        <div className="grid grid-cols-3 gap-2">
                          <div>
                            <Label className="text-xs text-muted-foreground">X</Label>
                            <Input
                              type="number"
                              value={selectedModel.position.x}
                              onChange={(e) => updateSelectedModel({
                                position: { ...selectedModel.position, x: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Y</Label>
                            <Input
                              type="number"
                              value={selectedModel.position.y}
                              onChange={(e) => updateSelectedModel({
                                position: { ...selectedModel.position, y: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Z</Label>
                            <Input
                              type="number"
                              value={selectedModel.position.z}
                              onChange={(e) => updateSelectedModel({
                                position: { ...selectedModel.position, z: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label>Rotation (degrees)</Label>
                        <div className="grid grid-cols-3 gap-2">
                          <div>
                            <Label className="text-xs text-muted-foreground">X</Label>
                            <Input
                              type="number"
                              value={selectedModel.rotation.x}
                              onChange={(e) => updateSelectedModel({
                                rotation: { ...selectedModel.rotation, x: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Y</Label>
                            <Input
                              type="number"
                              value={selectedModel.rotation.y}
                              onChange={(e) => updateSelectedModel({
                                rotation: { ...selectedModel.rotation, y: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Z</Label>
                            <Input
                              type="number"
                              value={selectedModel.rotation.z}
                              onChange={(e) => updateSelectedModel({
                                rotation: { ...selectedModel.rotation, z: parseFloat(e.target.value) || 0 }
                              })}
                            />
                          </div>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label>Scale</Label>
                        <div className="grid grid-cols-3 gap-2">
                          <div>
                            <Label className="text-xs text-muted-foreground">X</Label>
                            <Input
                              type="number"
                              value={selectedModel.scale.x}
                              step="0.1"
                              onChange={(e) => updateSelectedModel({
                                scale: { ...selectedModel.scale, x: parseFloat(e.target.value) || 1 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Y</Label>
                            <Input
                              type="number"
                              value={selectedModel.scale.y}
                              step="0.1"
                              onChange={(e) => updateSelectedModel({
                                scale: { ...selectedModel.scale, y: parseFloat(e.target.value) || 1 }
                              })}
                            />
                          </div>
                          <div>
                            <Label className="text-xs text-muted-foreground">Z</Label>
                            <Input
                              type="number"
                              value={selectedModel.scale.z}
                              step="0.1"
                              onChange={(e) => updateSelectedModel({
                                scale: { ...selectedModel.scale, z: parseFloat(e.target.value) || 1 }
                              })}
                            />
                          </div>
                        </div>
                      </div>

                      <Separator />

                      <div className="flex items-center justify-between">
                        <Label>Lock Object</Label>
                        <Switch
                          checked={selectedModel.locked}
                          onCheckedChange={(checked) => updateSelectedModel({ locked: checked })}
                        />
                      </div>
                    </>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      <Box className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Select an object to edit</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="material" className="p-4 space-y-4 mt-0">
                  {selectedModel?.material && (
                    <>
                      <div className="space-y-2">
                        <Label>Color</Label>
                        <div className="flex gap-2">
                          <input
                            type="color"
                            value={selectedModel.material.color}
                            onChange={(e) => updateSelectedModel({
                              material: { ...selectedModel.material!, color: e.target.value }
                            })}
                            className="h-10 w-20 rounded cursor-pointer"
                          />
                          <Input
                            value={selectedModel.material.color}
                            onChange={(e) => updateSelectedModel({
                              material: { ...selectedModel.material!, color: e.target.value }
                            })}
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Metalness: {selectedModel.material.metalness}</Label>
                        <Slider
                          value={[selectedModel.material.metalness]}
                          min={0}
                          max={1}
                          step={0.01}
                          onValueChange={([v]) => updateSelectedModel({
                            material: { ...selectedModel.material!, metalness: v }
                          })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Roughness: {selectedModel.material.roughness}</Label>
                        <Slider
                          value={[selectedModel.material.roughness]}
                          min={0}
                          max={1}
                          step={0.01}
                          onValueChange={([v]) => updateSelectedModel({
                            material: { ...selectedModel.material!, roughness: v }
                          })}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Opacity: {selectedModel.material.opacity}</Label>
                        <Slider
                          value={[selectedModel.material.opacity]}
                          min={0}
                          max={1}
                          step={0.01}
                          onValueChange={([v]) => updateSelectedModel({
                            material: { ...selectedModel.material!, opacity: v }
                          })}
                        />
                      </div>

                      <Separator />

                      <div className="space-y-2">
                        <Label>Material Presets</Label>
                        <div className="grid grid-cols-4 gap-2">
                          {['Metal', 'Plastic', 'Glass', 'Wood', 'Rubber', 'Gold', 'Silver', 'Chrome'].map(preset => (
                            <Button key={preset} variant="outline" size="sm" className="text-xs">
                              {preset}
                            </Button>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </TabsContent>

                <TabsContent value="lighting" className="p-4 space-y-4 mt-0">
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Sun className="h-4 w-4" />
                      <Label>Ambient Light</Label>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm text-muted-foreground">Intensity: {scene.lighting.ambient.intensity}</Label>
                      <Slider
                        value={[scene.lighting.ambient.intensity]}
                        min={0}
                        max={2}
                        step={0.1}
                        onValueChange={([v]) => setScene(prev => ({
                          ...prev,
                          lighting: { ...prev.lighting, ambient: { ...prev.lighting.ambient, intensity: v } }
                        }))}
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="h-4 w-4" />
                      <Label>Directional Light</Label>
                    </div>
                    <div className="space-y-2">
                      <Label className="text-sm text-muted-foreground">Intensity: {scene.lighting.directional.intensity}</Label>
                      <Slider
                        value={[scene.lighting.directional.intensity]}
                        min={0}
                        max={3}
                        step={0.1}
                        onValueChange={([v]) => setScene(prev => ({
                          ...prev,
                          lighting: { ...prev.lighting, directional: { ...prev.lighting.directional, intensity: v } }
                        }))}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Label className="text-sm">Color</Label>
                      <input
                        type="color"
                        value={scene.lighting.directional.color}
                        onChange={(e) => setScene(prev => ({
                          ...prev,
                          lighting: { ...prev.lighting, directional: { ...prev.lighting.directional, color: e.target.value } }
                        }))}
                        className="h-6 w-12 rounded cursor-pointer"
                      />
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <Label>Environment</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {['Studio', 'Outdoor', 'Night', 'Sunset', 'Forest', 'City'].map(env => (
                        <Button key={env} variant="outline" size="sm">
                          {env}
                        </Button>
                      ))}
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="ar" className="p-4 space-y-4 mt-0">
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Smartphone className="h-4 w-4" />
                        AR Preview
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground">
                        Preview your 3D model in augmented reality on your mobile device.
                      </p>
                      <Button className="w-full">
                        <Eye className="h-4 w-4 mr-2" />
                        Generate AR Preview
                      </Button>
                      <Button variant="outline" className="w-full">
                        <Share2 className="h-4 w-4 mr-2" />
                        Share AR Link
                      </Button>
                    </CardContent>
                  </Card>

                  <div className="space-y-2">
                    <Label>AR Placement Type</Label>
                    <Select defaultValue="plane">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="plane">Plane Detection</SelectItem>
                        <SelectItem value="image">Image Tracking</SelectItem>
                        <SelectItem value="face">Face Tracking</SelectItem>
                        <SelectItem value="world">World Anchor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>AR Scale</Label>
                    <Slider defaultValue={[1]} min={0.1} max={5} step={0.1} />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label>Allow User Scaling</Label>
                    <Switch defaultChecked />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label>Allow User Rotation</Label>
                    <Switch defaultChecked />
                  </div>
                </TabsContent>
              </ScrollArea>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}

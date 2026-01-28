/**
 * Enhanced Editor Page
 * Advanced canvas editor with all pro features
 */
'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Canvas } from 'fabric';
import type { FabricCanvas, FabricObject } from '@/types/fabric';
import { 
  Save, Download, Settings, Share2, Play, Eye, Grid3x3, 
  Layers as LayersIcon, History, Sparkles, Box, Maximize2, ZoomIn, ZoomOut
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { projectsAPI, type Project } from '@/lib/design-api';

// New advanced components
import { CanvasEditor } from '@/components/canvas/CanvasEditor';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { LayersPanel } from '@/components/canvas/LayersPanel';
import { HistoryPanel } from '@/components/canvas/HistoryPanel';
import { AlignmentGuides } from '@/components/canvas/AlignmentGuides';
import { PropertiesPanel } from '@/components/canvas/PropertiesPanel';
import { AIAssistantPanel } from '@/components/ai/AIAssistantPanel';
import { ComponentLibrary } from '@/components/canvas/ComponentLibrary';
import { KeyboardShortcutsManager } from '@/components/shortcuts/KeyboardShortcutsManager';

interface EnhancedEditorPageProps {
  projectId?: number;
}

export default function EnhancedEditorPage({ projectId = 1 }: EnhancedEditorPageProps) {
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [hasSelection, setHasSelection] = useState(false);
  const [selectedElements, setSelectedElements] = useState<Record<string, unknown>[]>([]);
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [leftPanel, setLeftPanel] = useState<'components' | 'assets'>('components');
  const [rightPanel, setRightPanel] = useState<'properties' | 'layers' | 'history' | 'ai'>('properties');
  const [showGrid, setShowGrid] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);
  const canvasContainerRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Load project
  useEffect(() => {
    const loadProject = async () => {
      try {
        setLoading(true);
        const data = await projectsAPI.get(projectId);
        setProject(data);
      } catch (error) {
        console.error('Failed to load project:', error);
        toast({ title: 'Failed to load project', variant: 'destructive' });
      } finally {
        setLoading(false);
      }
    };

    if (projectId) {
      loadProject();
    }
  }, [projectId, toast]);

  // Get canvas from CanvasEditor
  const handleCanvasReady = useCallback((fabricCanvas: Canvas) => {
    setCanvas(fabricCanvas);
    
    // Setup selection listeners
    fabricCanvas.on('selection:created', (e: { selected?: object[] }) => {
      setHasSelection(true);
      setSelectedElements((e.selected || []) as Record<string, unknown>[]);
    });
    
    fabricCanvas.on('selection:updated', (e: { selected?: object[] }) => {
      setHasSelection(true);
      setSelectedElements((e.selected || []) as Record<string, unknown>[]);
    });
    
    fabricCanvas.on('selection:cleared', () => {
      setHasSelection(false);
      setSelectedElements([]);
    });
  }, []);

  // Toolbar handlers
  const handleAddText = useCallback(() => {
    if (!canvas) return;
    const text = new (window as { fabric: { IText: new (...args: unknown[]) => unknown } }).fabric.IText('New Text', {
      left: 100,
      top: 100,
      fontSize: 24,
      fill: '#000000',
    }) as FabricObject;
    canvas.add(text);
    canvas.setActiveObject(text);
    canvas.renderAll();
  }, [canvas]);

  const handleAddRectangle = useCallback(() => {
    if (!canvas) return;
    const rect = new (window as { fabric: { Rect: new (...args: unknown[]) => unknown } }).fabric.Rect({
      left: 100,
      top: 100,
      width: 200,
      height: 100,
      fill: '#3B82F6',
      stroke: '#1E40AF',
      strokeWidth: 2,
    }) as FabricObject;
    canvas.add(rect);
    canvas.setActiveObject(rect);
    canvas.renderAll();
  }, [canvas]);

  const handleAddCircle = useCallback(() => {
    if (!canvas) return;
    const circle = new (window as any).fabric.Circle({
      left: 100,
      top: 100,
      radius: 50,
      fill: '#10B981',
      stroke: '#047857',
      strokeWidth: 2,
    }) as FabricObject;
    canvas.add(circle);
    canvas.setActiveObject(circle);
    canvas.renderAll();
  }, [canvas]);

  const handleAddImage = useCallback(() => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e: Event) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file && canvas) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const imgUrl = event.target?.result as string;
          (window as any).fabric.Image.fromURL(imgUrl, (img: FabricObject) => {
            img.scaleToWidth(300);
            img.set({ left: 100, top: 100 });
            canvas.add(img);
            canvas.setActiveObject(img);
            canvas.renderAll();
          });
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  }, [canvas]);

  const handleSave = useCallback(async () => {
    if (!canvas || !projectId) {
      toast({ title: 'Cannot save', description: 'No project loaded', variant: 'destructive' });
      return;
    }

    try {
      const designData = canvas.toJSON();
      await projectsAPI.saveDesign(projectId, designData);
      toast({ title: 'Saved successfully!' });
    } catch (error) {
      console.error('Save failed:', error);
      toast({ title: 'Save failed', variant: 'destructive' });
    }
  }, [canvas, projectId, toast]);

  const handleExportPNG = useCallback(() => {
    if (!canvas) return;
    const dataURL = canvas.toDataURL({ format: 'png', quality: 1, multiplier: 2 });
    const link = document.createElement('a');
    link.download = `${project?.name || 'design'}.png`;
    link.href = dataURL;
    link.click();
    toast({ title: 'Exported as PNG!' });
  }, [canvas, project, toast]);

  const handleExportSVG = useCallback(() => {
    if (!canvas) return;
    const svg = canvas.toSVG();
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = `${project?.name || 'design'}.svg`;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
    toast({ title: 'Exported as SVG!' });
  }, [canvas, project, toast]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    if (!canvas) return;
    const newZoom = Math.min(zoomLevel + 10, 200);
    setZoomLevel(newZoom);
    canvas.setZoom(newZoom / 100);
    canvas.renderAll();
  }, [canvas, zoomLevel]);

  const handleZoomOut = useCallback(() => {
    if (!canvas) return;
    const newZoom = Math.max(zoomLevel - 10, 25);
    setZoomLevel(newZoom);
    canvas.setZoom(newZoom / 100);
    canvas.renderAll();
  }, [canvas, zoomLevel]);

  const handleZoomFit = useCallback(() => {
    setZoomLevel(100);
    if (canvas) {
      canvas.setZoom(1);
      canvas.renderAll();
    }
  }, [canvas]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading project...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Top toolbar */}
      <div className="border-b bg-card">
        <div className="flex items-center justify-between px-4 h-14">
          {/* Left section */}
          <div className="flex items-center gap-3">
            <div className="flex flex-col">
              <span className="text-sm font-semibold">
                {project?.name || 'Untitled Project'}
              </span>
              <span className="text-xs text-muted-foreground">
                Last saved {new Date().toLocaleTimeString()}
              </span>
            </div>
            <Badge variant="secondary" className="text-xs">
              Auto-saving
            </Badge>
          </div>

          {/* Center section - Main tools */}
          <CanvasToolbar
            onAddText={handleAddText}
            onAddRectangle={handleAddRectangle}
            onAddCircle={handleAddCircle}
            onAddImage={handleAddImage}
            onDelete={() => {
              if (canvas) {
                const activeObjects = canvas.getActiveObjects();
                canvas.remove(...activeObjects);
                canvas.discardActiveObject();
                canvas.renderAll();
              }
            }}
            onClone={() => {
              if (canvas) {
                const activeObject = canvas.getActiveObject();
                if (activeObject) {
                  activeObject.clone().then((cloned: FabricObject) => {
                    cloned.set({ left: (cloned.left || 0) + 20, top: (cloned.top || 0) + 20 });
                    canvas.add(cloned);
                    canvas.setActiveObject(cloned);
                    canvas.renderAll();
                  });
                }
              }
            }}
            onBringToFront={() => {
              if (canvas) {
                const activeObject = canvas.getActiveObject();
                if (activeObject) {
                  canvas.bringObjectToFront(activeObject);
                  canvas.renderAll();
                }
              }
            }}
            onSendToBack={() => {
              if (canvas) {
                const activeObject = canvas.getActiveObject();
                if (activeObject) {
                  canvas.sendObjectToBack(activeObject);
                  canvas.renderAll();
                }
              }
            }}
            onExportPNG={handleExportPNG}
            onExportSVG={handleExportSVG}
            onSave={handleSave}
            onAIGenerate={() => setRightPanel('ai')}
            hasSelection={hasSelection}
          />

          {/* Right section */}
          <div className="flex items-center gap-2">
            <KeyboardShortcutsManager canvas={canvas} />
            
            <Button variant="ghost" size="sm" onClick={() => setShowGrid(!showGrid)}>
              <Grid3x3 className="w-4 h-4" />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button variant="ghost" size="sm" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <div className="text-sm font-medium min-w-[60px] text-center">
              {zoomLevel}%
            </div>
            <Button variant="ghost" size="sm" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleZoomFit}>
              <Maximize2 className="w-4 h-4" />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button variant="default" size="sm" onClick={handleSave}>
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
          </div>
        </div>
      </div>

      {/* Main editor area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar */}
        <div className="w-64 border-r bg-card flex flex-col">
          <Tabs value={leftPanel} onValueChange={(v) => setLeftPanel(v as 'components' | 'assets')} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="components">
                <Box className="w-4 h-4 mr-2" />
                Components
              </TabsTrigger>
              <TabsTrigger value="assets">
                Assets
              </TabsTrigger>
            </TabsList>
            <TabsContent value="components" className="flex-1 m-0">
              <ComponentLibrary canvas={canvas} />
            </TabsContent>
            <TabsContent value="assets" className="flex-1 m-0 p-4">
              <div className="text-sm text-muted-foreground text-center py-12">
                Assets panel
              </div>
            </TabsContent>
          </Tabs>
        </div>

        {/* Canvas area */}
        <div 
          ref={canvasContainerRef}
          className="flex-1 bg-muted/20 p-8 overflow-auto flex items-center justify-center relative"
        >
          <div className="bg-white shadow-2xl rounded-lg overflow-hidden">
            <CanvasEditor
              width={project?.canvas_width || 1920}
              height={project?.canvas_height || 1080}
              backgroundColor={project?.canvas_background || '#FFFFFF'}
              initialData={project?.design_data}
              onSave={handleSave}
            />
          </div>
          
          {/* Alignment guides */}
          {canvas && <AlignmentGuides canvas={canvas} />}
        </div>

        {/* Right sidebar */}
        <div className="w-72 border-l bg-card flex flex-col">
          <Tabs value={rightPanel} onValueChange={(v) => setRightPanel(v as 'properties' | 'layers' | 'history' | 'ai')} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="properties" className="text-xs">
                <Settings className="w-3.5 h-3.5" />
              </TabsTrigger>
              <TabsTrigger value="layers" className="text-xs">
                <LayersIcon className="w-3.5 h-3.5" />
              </TabsTrigger>
              <TabsTrigger value="history" className="text-xs">
                <History className="w-3.5 h-3.5" />
              </TabsTrigger>
              <TabsTrigger value="ai" className="text-xs">
                <Sparkles className="w-3.5 h-3.5" />
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-hidden">
              <TabsContent value="properties" className="h-full m-0">
                <PropertiesPanel
                  selectedElements={selectedElements}
                  onPropertyChange={(updates) => {
                    if (canvas) {
                      const activeObject = canvas.getActiveObject();
                      if (activeObject) {
                        activeObject.set(updates);
                        canvas.renderAll();
                      }
                    }
                  }}
                />
              </TabsContent>
              
              <TabsContent value="layers" className="h-full m-0">
                <LayersPanel canvas={canvas} />
              </TabsContent>
              
              <TabsContent value="history" className="h-full m-0">
                <HistoryPanel canvas={canvas} />
              </TabsContent>
              
              <TabsContent value="ai" className="h-full m-0">
                <AIAssistantPanel canvas={canvas} projectId={projectId} />
              </TabsContent>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}

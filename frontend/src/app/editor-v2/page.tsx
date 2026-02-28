/**
 * Enhanced Editor Page
 * Advanced canvas editor with all pro features
 */
'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Canvas, IText, Rect, Circle, Image, Triangle, Line, Group as FabricGroup } from 'fabric';
import type { FabricObject } from '@/types/fabric';
import { 
  Save, Settings, Share2, Grid3x3, Ruler,
  Layers as LayersIcon, History, Sparkles, Box, Maximize2, Minimize2, ZoomIn, ZoomOut,
  ChevronDown, Monitor, Smartphone, Instagram, Youtube
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
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
  const [selectedElements, setSelectedElements] = useState<FabricObject[]>([]);
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [leftPanel, setLeftPanel] = useState<'components' | 'assets'>('components');
  const [rightPanel, setRightPanel] = useState<'properties' | 'layers' | 'history' | 'ai'>('properties');
  const [showGrid, setShowGrid] = useState(false);
  const [showRuler, setShowRuler] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(100);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);
  const [isLocked, setIsLocked] = useState(false);
  const historyRef = useRef<string[]>([]);
  const historyIndexRef = useRef(-1);
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
  const _handleCanvasReady = useCallback((fabricCanvas: Canvas) => {
    setCanvas(fabricCanvas);
    
    // Setup selection listeners
    fabricCanvas.on('selection:created', (e: { selected?: FabricObject[] }) => {
      setHasSelection(true);
      setSelectedElements(e.selected || []);
    });
    
    fabricCanvas.on('selection:updated', (e: { selected?: FabricObject[] }) => {
      setHasSelection(true);
      setSelectedElements(e.selected || []);
    });
    
    fabricCanvas.on('selection:cleared', () => {
      setHasSelection(false);
      setSelectedElements([]);
    });

    // History tracking
    const saveSnapshot = () => {
      const json = JSON.stringify(fabricCanvas.toJSON());
      const idx = historyIndexRef.current;
      historyRef.current = historyRef.current.slice(0, idx + 1);
      historyRef.current.push(json);
      historyIndexRef.current = historyRef.current.length - 1;
      setCanUndo(historyIndexRef.current > 0);
      setCanRedo(false);
    };
    fabricCanvas.on('object:added', saveSnapshot);
    fabricCanvas.on('object:removed', saveSnapshot);
    fabricCanvas.on('object:modified', saveSnapshot);
    // Save initial state
    saveSnapshot();
  }, []);

  // Undo
  const handleUndo = useCallback(() => {
    if (!canvas || historyIndexRef.current <= 0) return;
    historyIndexRef.current -= 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas.loadFromJSON(JSON.parse(json)).then(() => {
      canvas.renderAll();
      setCanUndo(historyIndexRef.current > 0);
      setCanRedo(true);
    });
  }, [canvas]);

  // Redo
  const handleRedo = useCallback(() => {
    if (!canvas || historyIndexRef.current >= historyRef.current.length - 1) return;
    historyIndexRef.current += 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas.loadFromJSON(JSON.parse(json)).then(() => {
      canvas.renderAll();
      setCanUndo(true);
      setCanRedo(historyIndexRef.current < historyRef.current.length - 1);
    });
  }, [canvas]);

  // Toolbar handlers
  const handleAddText = useCallback(() => {
    if (!canvas) return;
    const text = new IText('New Text', {
      left: 100,
      top: 100,
      fontSize: 24,
      fill: '#000000',
    });
    canvas.add(text);
    canvas.setActiveObject(text);
    canvas.renderAll();
  }, [canvas]);

  const handleAddRectangle = useCallback(() => {
    if (!canvas) return;
    const rect = new Rect({
      left: 100,
      top: 100,
      width: 200,
      height: 100,
      fill: '#3B82F6',
      stroke: '#1E40AF',
      strokeWidth: 2,
    });
    canvas.add(rect);
    canvas.setActiveObject(rect);
    canvas.renderAll();
  }, [canvas]);

  const handleAddCircle = useCallback(() => {
    if (!canvas) return;
    const circle = new Circle({
      left: 100,
      top: 100,
      radius: 50,
      fill: '#10B981',
      stroke: '#047857',
      strokeWidth: 2,
    });
    canvas.add(circle);
    canvas.setActiveObject(circle);
    canvas.renderAll();
  }, [canvas]);

  const handleAddTriangle = useCallback(() => {
    if (!canvas) return;
    const tri = new Triangle({
      left: 100, top: 100, width: 120, height: 100,
      fill: '#F59E0B', stroke: '#B45309', strokeWidth: 2,
    });
    canvas.add(tri);
    canvas.setActiveObject(tri);
    canvas.renderAll();
  }, [canvas]);

  const handleAddLine = useCallback(() => {
    if (!canvas) return;
    const line = new Line([50, 100, 300, 100], {
      stroke: '#6B7280', strokeWidth: 3, selectable: true,
    });
    canvas.add(line);
    canvas.setActiveObject(line);
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
          Image.fromURL(imgUrl, {
            crossOrigin: 'anonymous'
          }).then((img) => {
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

  const handleExportJSON = useCallback(() => {
    if (!canvas) return;
    const json = JSON.stringify(canvas.toJSON(), null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = `${project?.name || 'design'}.json`;
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
    toast({ title: 'Exported as JSON!' });
  }, [canvas, project, toast]);

  // Alignment helpers
  const handleAlign = useCallback((type: 'left' | 'center' | 'right' | 'top' | 'middle' | 'bottom') => {
    if (!canvas) return;
    const obj = canvas.getActiveObject();
    if (!obj) return;
    const cw = canvas.getWidth();
    const ch = canvas.getHeight();
    const ow = (obj.width || 0) * (obj.scaleX || 1);
    const oh = (obj.height || 0) * (obj.scaleY || 1);
    switch (type) {
      case 'left': obj.set({ left: 0 }); break;
      case 'center': obj.set({ left: (cw - ow) / 2 }); break;
      case 'right': obj.set({ left: cw - ow }); break;
      case 'top': obj.set({ top: 0 }); break;
      case 'middle': obj.set({ top: (ch - oh) / 2 }); break;
      case 'bottom': obj.set({ top: ch - oh }); break;
    }
    canvas.renderAll();
  }, [canvas]);

  // Flip helpers
  const handleFlipHorizontal = useCallback(() => {
    if (!canvas) return;
    const obj = canvas.getActiveObject();
    if (!obj) return;
    obj.set('flipX', !obj.flipX);
    canvas.renderAll();
  }, [canvas]);

  const handleFlipVertical = useCallback(() => {
    if (!canvas) return;
    const obj = canvas.getActiveObject();
    if (!obj) return;
    obj.set('flipY', !obj.flipY);
    canvas.renderAll();
  }, [canvas]);

  // Group / Ungroup
  const handleGroup = useCallback(() => {
    if (!canvas) return;
    const activeObjects = canvas.getActiveObjects();
    if (activeObjects.length < 2) return;
    const group = new FabricGroup(activeObjects);
    canvas.remove(...activeObjects);
    canvas.add(group);
    canvas.setActiveObject(group);
    canvas.renderAll();
    toast({ title: 'Grouped' });
  }, [canvas, toast]);

  const handleUngroup = useCallback(() => {
    if (!canvas) return;
    const activeObj = canvas.getActiveObject() as FabricObject & { getObjects?: () => FabricObject[] };
    if (!activeObj || activeObj.type !== 'group') return;
    const items = activeObj.getObjects?.() || [];
    canvas.remove(activeObj);
    items.forEach((item: FabricObject) => canvas.add(item));
    canvas.renderAll();
    toast({ title: 'Ungrouped' });
  }, [canvas, toast]);

  // Lock / unlock selected
  const handleLock = useCallback(() => {
    if (!canvas) return;
    const obj = canvas.getActiveObject();
    if (!obj) return;
    const newLocked = !isLocked;
    obj.set({ selectable: !newLocked, evented: !newLocked });
    canvas.renderAll();
    setIsLocked(newLocked);
  }, [canvas, isLocked]);

  // Fullscreen toggle
  const handleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;
      if (ctrl && e.key === 'z') { e.preventDefault(); handleUndo(); }
      if (ctrl && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) { e.preventDefault(); handleRedo(); }
      if (ctrl && e.key === 'd') { e.preventDefault(); /* clone handled in toolbar */ }
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if ((e.target as HTMLElement).tagName !== 'INPUT' && (e.target as HTMLElement).tagName !== 'TEXTAREA') {
          if (canvas) {
            const objs = canvas.getActiveObjects();
            canvas.remove(...objs);
            canvas.discardActiveObject();
            canvas.renderAll();
          }
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleUndo, handleRedo, canvas]);

  // Save current design to project
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
            onAddTriangle={handleAddTriangle}
            onAddLine={handleAddLine}
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
            onExportJSON={handleExportJSON}
            onSave={handleSave}
            onAIGenerate={() => setRightPanel('ai')}
            onUndo={handleUndo}
            onRedo={handleRedo}
            onAlignLeft={() => handleAlign('left')}
            onAlignCenter={() => handleAlign('center')}
            onAlignRight={() => handleAlign('right')}
            onAlignTop={() => handleAlign('top')}
            onAlignMiddle={() => handleAlign('middle')}
            onAlignBottom={() => handleAlign('bottom')}
            onFlipHorizontal={handleFlipHorizontal}
            onFlipVertical={handleFlipVertical}
            onGroup={handleGroup}
            onUngroup={handleUngroup}
            onLock={handleLock}
            hasSelection={hasSelection}
            isLocked={isLocked}
            canUndo={canUndo}
            canRedo={canRedo}
          />

          {/* Right section */}
          <div className="flex items-center gap-1.5">
            <KeyboardShortcutsManager canvas={canvas} />

            {/* Canvas size presets */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 gap-1 px-2 text-xs">
                  <Monitor className="w-3.5 h-3.5" />
                  <ChevronDown className="w-3 h-3 opacity-60" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-52">
                <DropdownMenuLabel className="text-xs">Canvas Presets</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-xs gap-2" onClick={() => toast({ title: 'Canvas: 1920×1080' })}>
                  <Monitor className="w-3.5 h-3.5" /> Desktop HD (1920×1080)
                </DropdownMenuItem>
                <DropdownMenuItem className="text-xs gap-2" onClick={() => toast({ title: 'Canvas: 3840×2160' })}>
                  <Monitor className="w-3.5 h-3.5" /> 4K UHD (3840×2160)
                </DropdownMenuItem>
                <DropdownMenuItem className="text-xs gap-2" onClick={() => toast({ title: 'Canvas: 1080×1920' })}>
                  <Smartphone className="w-3.5 h-3.5" /> Mobile (1080×1920)
                </DropdownMenuItem>
                <DropdownMenuItem className="text-xs gap-2" onClick={() => toast({ title: 'Canvas: 1080×1080' })}>
                  <Instagram className="w-3.5 h-3.5" /> Instagram Square (1080×1080)
                </DropdownMenuItem>
                <DropdownMenuItem className="text-xs gap-2" onClick={() => toast({ title: 'Canvas: 1280×720' })}>
                  <Youtube className="w-3.5 h-3.5" /> YouTube Thumbnail (1280×720)
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setShowGrid(!showGrid)}
              title="Toggle Grid">
              <Grid3x3 className={`w-4 h-4 ${showGrid ? 'text-primary' : ''}`} />
            </Button>

            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setShowRuler(!showRuler)}
              title="Toggle Ruler">
              <Ruler className={`w-4 h-4 ${showRuler ? 'text-primary' : ''}`} />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <div className="text-xs font-mono font-medium min-w-[46px] text-center bg-muted rounded px-1 py-0.5">
              {zoomLevel}%
            </div>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleZoomFit} title="Fit to screen">
              <Maximize2 className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleFullscreen} title="Fullscreen">
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>

            <Separator orientation="vertical" className="h-6" />

            <Button variant="default" size="sm" onClick={handleSave} className="h-8">
              <Save className="w-4 h-4 mr-1.5" />
              Save
            </Button>
            <Button variant="outline" size="sm" className="h-8">
              <Share2 className="w-4 h-4 mr-1.5" />
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

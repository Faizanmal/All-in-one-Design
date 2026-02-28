"use client";

declare global {
  interface Window {
    canvasEditor?: {
      addText?: (text: string) => void;
      addRectangle?: () => void;
      addCircle?: () => void;
      addTriangle?: () => void;
      addLine?: () => void;
      deleteSelected?: () => void;
      cloneSelected?: () => void;
      bringToFront?: () => void;
      sendToBack?: () => void;
      groupSelected?: () => void;
      ungroupSelected?: () => void;
      zoomIn?: () => void;
      zoomOut?: () => void;
      zoomToFit?: () => void;
      undo?: () => void;
      redo?: () => void;
      exportAsPNG?: () => void;
      exportAsSVG?: () => void;
      exportAsJPG?: () => void;
      exportAsPDF?: (projectId: number) => void;
      exportAsFigmaJSON?: () => void;
      handleSave?: () => void;
      renderAIDesign?: (result: Record<string, unknown>) => void;
      getCanvasData?: () => Record<string, unknown>;
    };
  }
}

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { CanvasEditor } from '@/components/canvas/CanvasEditor';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { AdvancedAIGenerateDialog } from '@/components/canvas/AdvancedAIGenerateDialog';
import { useToast } from '@/hooks/use-toast';
import { projectsAPI, type Project } from '@/lib/design-api';
import { Loader2, ZoomIn, ZoomOut, Maximize, Keyboard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';

export default function EditorPage() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project') ? parseInt(searchParams.get('project')!) : null;
  const [project, setProject] = useState<Project | null>(null);
  const [hasSelection] = useState(false);
  const [loading, setLoading] = useState(!!projectId);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autoSaveEnabled] = useState(true);
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  // Load project data
  React.useEffect(() => {
    if (projectId) {
      setLoading(true);
      projectsAPI.get(projectId)
        .then((data) => {
          setProject(data);
          setLoading(false);
        })
        .catch((err) => {
          setLoading(false);
          toast({
            title: 'Error loading project',
            description: err.message || 'Failed to load project. Please check your connection and try again.',
            variant: 'destructive',
          });
        });
    }
  }, [projectId, toast]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;
      
      if (ctrl && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        window.canvasEditor?.undo?.();
      } else if (ctrl && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault();
        window.canvasEditor?.redo?.();
      } else if (ctrl && e.key === 's') {
        e.preventDefault();
        handleSave();
      } else if (e.key === 'Delete' || e.key === 'Backspace') {
        if (document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
          window.canvasEditor?.deleteSelected?.();
        }
      } else if (ctrl && e.key === 'd') {
        e.preventDefault();
        window.canvasEditor?.cloneSelected?.();
      } else if (ctrl && e.key === 'g') {
        e.preventDefault();
        if (e.shiftKey) {
          window.canvasEditor?.ungroupSelected?.();
        } else {
          window.canvasEditor?.groupSelected?.();
        }
      } else if (!ctrl && !e.altKey) {
        if (document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
          switch (e.key.toLowerCase()) {
            case 't': window.canvasEditor?.addText?.('New Text'); break;
            case 'r': window.canvasEditor?.addRectangle?.(); break;
            case 'o': window.canvasEditor?.addCircle?.(); break;
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auto-save every 30 seconds
  useEffect(() => {
    if (autoSaveEnabled && projectId) {
      autoSaveTimerRef.current = setInterval(() => {
        const canvasData = window.canvasEditor?.getCanvasData?.();
        if (canvasData && projectId) {
          projectsAPI.saveDesign(projectId, canvasData)
            .then(() => setLastSaved(new Date()))
            .catch(() => {}); // Silent auto-save failure
        }
      }, 30000);
    }
    return () => {
      if (autoSaveTimerRef.current) {
        clearInterval(autoSaveTimerRef.current);
      }
    };
  }, [autoSaveEnabled, projectId]);

  // Canvas toolbar handlers
  const handleAddText = () => {
    window.canvasEditor?.addText?.('New Text');
    toast({ title: 'Text added' });
  };

  const handleAddRectangle = () => {
    window.canvasEditor?.addRectangle?.();
    toast({ title: 'Rectangle added' });
  };

  const handleAddCircle = () => {
    window.canvasEditor?.addCircle?.();
    toast({ title: 'Circle added' });
  };

  const handleAddImage = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e: Event) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = () => {
          toast({ title: 'Image added to canvas' });
        };
        reader.readAsDataURL(file);
      }
    };
    input.click();
  };

  const handleDelete = () => {
    window.canvasEditor?.deleteSelected?.();
    toast({ title: 'Object deleted' });
  };

  const handleClone = () => {
    window.canvasEditor?.cloneSelected?.();
    toast({ title: 'Object cloned' });
  };

  const handleBringToFront = () => {
    window.canvasEditor?.bringToFront?.();
    toast({ title: 'Brought to front' });
  };

  const handleSendToBack = () => {
    window.canvasEditor?.sendToBack?.();
    toast({ title: 'Sent to back' });
  };

  const handleExportPNG = () => {
    window.canvasEditor?.exportAsPNG?.();
    toast({ title: 'Exporting as PNG...' });
  };

  const handleExportSVG = () => {
    window.canvasEditor?.exportAsSVG?.();
    toast({ title: 'Exporting as SVG...' });
  };

  const handleExportJSON = () => {
    window.canvasEditor?.exportAsFigmaJSON?.();
    toast({ title: 'Exporting as Figma JSON...' });
  };

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      const canvasData = window.canvasEditor?.getCanvasData?.();
      
      if (!projectId) {
        toast({
          title: 'No project',
          description: 'Create or open a project first to save your work.',
          variant: 'destructive',
        });
        setSaving(false);
        return;
      }

      if (canvasData) {
        await projectsAPI.saveDesign(projectId, canvasData);
      }
      
      setLastSaved(new Date());
      toast({
        title: 'Saved',
        description: 'Project saved successfully',
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Failed to save project';
      toast({
        title: 'Save failed',
        description: message + '. Please try again or check your connection.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  }, [projectId, toast]);

  const handleAIGenerate = (result: Record<string, unknown>) => {
    console.log('AI Result received:', result);
    console.log('Window canvasEditor:', window.canvasEditor);
    
    // Check if canvasEditor is available
    const canvasEditor = (window as { canvasEditor?: { 
      renderAIDesign?: (result: Record<string, unknown>) => void;
      addText?: (text?: string, position?: { x: number; y: number }) => void; 
      addRectangle?: (position?: { x: number; y: number }) => void; 
      addCircle?: (position?: { x: number; y: number }) => void;
    } }).canvasEditor;
    
    if (!canvasEditor) {
      console.error('Canvas editor not ready - window.canvasEditor is undefined');
      toast({
        title: 'Error',
        description: 'Canvas is not ready. Please wait a moment and try again.',
        variant: 'destructive',
      });
      return;
    }
    
    // Use the new advanced rendering method if available
    if (canvasEditor.renderAIDesign) {
      console.log('Using advanced AI rendering');
      canvasEditor.renderAIDesign(result);
      
      toast({
        title: 'Success',
        description: 'Professional design generated and rendered on canvas!',
      });
    } else {
      console.warn('Advanced renderer not available, falling back to basic rendering');
      
      // Fallback to old method
      const components = result.components as Array<Record<string, unknown>>;
      
      if (!components || components.length === 0) {
        console.warn('No components in AI response');
        toast({
          title: 'Warning',
          description: 'No components in AI response',
          variant: 'destructive',
        });
        return;
      }
      
      console.log(`Processing ${components.length} components...`);
      
      // Add each component to the canvas using basic methods
      components.forEach((component, index) => {
        const type = component.type as string;
        const text = component.content as string;
        const rawPosition = component.position as unknown;
        
        let position: { x: number; y: number } | undefined;
        if (rawPosition && typeof rawPosition === 'object' && 
            'x' in rawPosition && 'y' in rawPosition &&
            typeof (rawPosition as Record<string, unknown>).x === 'number' && 
            typeof (rawPosition as Record<string, unknown>).y === 'number') {
          const pos = rawPosition as { x: number; y: number };
          position = {
            x: Math.max(50, Math.min(1820, pos.x)),
            y: Math.max(50, Math.min(980, pos.y))
          };
        }
        
        try {
          switch (type) {
            case 'text':
            case 'header':
            case 'footer':
            case 'navigation':
              canvasEditor.addText?.(text || type.charAt(0).toUpperCase() + type.slice(1), position);
              break;
              
            case 'button':
            case 'input':
            case 'container':
            case 'card':
            case 'section':
            case 'rectangle':
            case 'background':
              canvasEditor.addRectangle?.(position);
              break;
              
            case 'icon':
            case 'symbol':
              canvasEditor.addCircle?.(position);
              break;
              
            default:
              canvasEditor.addRectangle?.(position);
          }
        } catch (error) {
          console.error(`Error adding component ${index + 1}:`, error);
        }
      });
      
      toast({
        title: 'Success',
        description: `Added ${components.length} components to canvas!`,
      });
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Top Toolbar */}
      <CanvasToolbar
        onAddText={handleAddText}
        onAddRectangle={handleAddRectangle}
        onAddCircle={handleAddCircle}
        onAddTriangle={() => { window.canvasEditor?.addTriangle?.(); toast({ title: 'Triangle added' }); }}
        onAddLine={() => { window.canvasEditor?.addLine?.(); toast({ title: 'Line added' }); }}
        onAddImage={handleAddImage}
        onDelete={handleDelete}
        onClone={handleClone}
        onBringToFront={handleBringToFront}
        onSendToBack={handleSendToBack}
        onExportPNG={handleExportPNG}
        onExportSVG={handleExportSVG}
        onExportJSON={handleExportJSON}
        onSave={handleSave}
        onAIGenerate={() => {}}
        onUndo={() => window.canvasEditor?.undo?.()}
        onRedo={() => window.canvasEditor?.redo?.()}
        onGroup={() => { window.canvasEditor?.groupSelected?.(); toast({ title: 'Objects grouped' }); }}
        onUngroup={() => { window.canvasEditor?.ungroupSelected?.(); toast({ title: 'Objects ungrouped' }); }}
        hasSelection={hasSelection}
      />

      {/* Main Editor Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - AI Generation */}
        <div className="w-64 border-r bg-gray-50 dark:bg-gray-900 p-4 overflow-y-auto flex flex-col">
          <h3 className="font-semibold mb-4">AI Generation</h3>
          <div className="space-y-2 flex-1">
            <AdvancedAIGenerateDialog 
              onGenerate={handleAIGenerate}
              canvasWidth={project?.canvas_width || 1920}
              canvasHeight={project?.canvas_height || 1080}
            />
          </div>
          
          {/* Keyboard Shortcuts Hint */}
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
              <Keyboard className="h-3 w-3" /> Shortcuts
            </div>
            <div className="grid grid-cols-2 gap-1 text-xs text-muted-foreground">
              <span>T</span><span>Text</span>
              <span>R</span><span>Rectangle</span>
              <span>O</span><span>Circle</span>
              <span>Del</span><span>Delete</span>
              <span>Ctrl+Z</span><span>Undo</span>
              <span>Ctrl+S</span><span>Save</span>
              <span>Ctrl+D</span><span>Duplicate</span>
              <span>Ctrl+G</span><span>Group</span>
            </div>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-gray-100 dark:bg-gray-800 overflow-auto flex flex-col">
          {/* Zoom & Status Bar */}
          <div className="flex items-center justify-between px-4 py-1 bg-white dark:bg-gray-900 border-b text-xs">
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => window.canvasEditor?.zoomOut?.()}>
                <ZoomOut className="h-3 w-3" />
              </Button>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => window.canvasEditor?.zoomToFit?.()}>
                <Maximize className="h-3 w-3" />
              </Button>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => window.canvasEditor?.zoomIn?.()}>
                <ZoomIn className="h-3 w-3" />
              </Button>
            </div>
            <div className="flex items-center gap-3 text-muted-foreground">
              {saving && <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" /> Saving...</span>}
              {lastSaved && !saving && <span>Last saved: {lastSaved.toLocaleTimeString()}</span>}
              <span>{project?.canvas_width || 1920} × {project?.canvas_height || 1080}</span>
            </div>
          </div>
          
          {/* Canvas */}
          <div className="flex-1 p-8 overflow-auto flex items-center justify-center">
            {loading ? (
              <div className="flex flex-col items-center gap-4">
                <Skeleton className="w-[960px] h-[540px] rounded-lg" />
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Loading project...</span>
                </div>
              </div>
            ) : (
              <div className="bg-white shadow-2xl">
                <CanvasEditor
                  width={project?.canvas_width || 1920}
                  height={project?.canvas_height || 1080}
                  backgroundColor={project?.canvas_background || '#FFFFFF'}
                  initialData={project?.design_data}
                  onSave={handleSave}
                />
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar - Properties */}
        <div className="w-64 border-l bg-gray-50 dark:bg-gray-900 p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">Properties</h3>
          {hasSelection ? (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Position</label>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  <input
                    type="number"
                    placeholder="X"
                    className="px-2 py-1 border rounded text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Y"
                    className="px-2 py-1 border rounded text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Size</label>
                <div className="grid grid-cols-2 gap-2 mt-1">
                  <input
                    type="number"
                    placeholder="Width"
                    className="px-2 py-1 border rounded text-sm"
                  />
                  <input
                    type="number"
                    placeholder="Height"
                    className="px-2 py-1 border rounded text-sm"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Opacity</label>
                <input
                  type="range" min="0" max="100" defaultValue="100"
                  className="w-full mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Fill Color</label>
                <input type="color" defaultValue="#3B82F6" className="w-full h-8 mt-1 rounded border" />
              </div>
              <div>
                <label className="text-sm font-medium">Stroke</label>
                <div className="flex gap-2 mt-1">
                  <input type="color" defaultValue="#000000" className="w-8 h-8 rounded border" />
                  <input type="number" placeholder="Width" defaultValue={2} className="flex-1 px-2 py-1 border rounded text-sm" />
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-muted-foreground">Select an object to edit its properties</p>
              <p className="text-xs text-muted-foreground mt-2">Use the tools above to add elements to the canvas</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

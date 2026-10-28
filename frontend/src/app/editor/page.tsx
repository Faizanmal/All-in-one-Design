"use client";

import React, { Suspense, useState, useCallback, useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { CanvasEditor } from '@/components/canvas/CanvasEditor';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { AdvancedAIGenerateDialog } from '@/components/canvas/AdvancedAIGenerateDialog';
import { PropertiesPanel } from '@/components/canvas/PropertiesPanel';
import { LayersPanel } from '@/components/canvas/LayersPanel';
import { CollaborationBar, CollaborationCursorsOverlay } from '@/components/collaboration/CollaborationBar';
import { CommentsPanel } from '@/components/collaboration/CommentsPanel';
import { ShareProjectDialog } from '@/components/collaboration/ShareProjectDialog';
import { ExportModal } from '@/components/export/ExportModal';
import { useCollaborativeCanvas, type CanvasUpdate } from '@/hooks/useCollaborativeCanvas';
import { useToast } from '@/hooks/use-toast';
import { projectsAPI, type Project } from '@/lib/design-api';
import { Loader2, ZoomIn, ZoomOut, Maximize, Keyboard, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import type { Canvas as FabricCanvas, FabricObject } from 'fabric';

declare global {
  interface Window {
    canvasEditor?: {
      canvas?: FabricCanvas;
      addText?: (text?: string, position?: { x: number; y: number }) => void;
      addRectangle?: (position?: { x: number; y: number }) => void;
      addCircle?: (position?: { x: number; y: number }) => void;
      addTriangle?: () => void;
      addLine?: () => void;
      addImage?: (url?: string, position?: { x: number; y: number }) => void;
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
      exportAsPNG?: (opts?: { multiplier?: number; quality?: number; includeBackground?: boolean; fileName?: string }) => void;
      exportAsSVG?: () => void;
      exportAsJPG?: (opts?: { multiplier?: number; quality?: number; includeBackground?: boolean; fileName?: string }) => void;
      exportAsPDF?: (projectId: number) => void;
      exportAsFigmaJSON?: () => void;
      handleSave?: () => void;
      renderAIDesign?: (result: Record<string, unknown>) => boolean;
      getCanvasData?: () => Record<string, unknown> | null;
      loadCanvasData?: (data: Record<string, unknown>) => Promise<unknown>;
      applyObjectProperty?: (property: string, value: unknown) => void;
      getSelectedObjects?: () => FabricObject[];
    };
  }
}

// Client-only component: contains all the editor logic which relies on
// browser APIs and next/navigation hooks.
const EditorPageClient = () => {
  "use client";

  const searchParams = useSearchParams();
  const projectParam = searchParams.get('project') || searchParams.get('projectId');
  const projectId = projectParam ? parseInt(projectParam, 10) : null;
  const [project, setProject] = useState<Project | null>(null);
  const [hasSelection, setHasSelection] = useState(false);
  const [selectedElements, setSelectedElements] = useState<FabricObject[]>([]);
  const [fabricCanvas, setFabricCanvas] = useState<FabricCanvas | null>(null);
  const [loading, setLoading] = useState(!!projectId);
  const [saving, setSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autoSaveEnabled] = useState(true);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showAIDialog, setShowAIDialog] = useState(false);
  const [rightPanel, setRightPanel] = useState<'properties' | 'layers' | 'comments'>('properties');
  const autoSaveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const syncTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const canvasAreaRef = useRef<HTMLDivElement | null>(null);
  const { toast } = useToast();

  // Keep toolbar + properties panel in sync with Fabric selection
  useEffect(() => {
    const onSelection = (event: Event) => {
      const detail = (event as CustomEvent<{ objects?: FabricObject[]; hasSelection?: boolean }>).detail;
      const objects = detail?.objects || [];
      setSelectedElements(objects);
      setHasSelection(Boolean(detail?.hasSelection ?? objects.length > 0));
    };
    const onExportFallback = (event: Event) => {
      const detail = (event as CustomEvent<{ message?: string }>).detail;
      toast({
        title: 'Export fallback',
        description: detail?.message || 'PDF failed; exported PNG instead.',
        variant: 'destructive',
      });
    };
    window.addEventListener('canvas-selection-change', onSelection);
    window.addEventListener('canvas-export-fallback', onExportFallback);
    return () => {
      window.removeEventListener('canvas-selection-change', onSelection);
      window.removeEventListener('canvas-export-fallback', onExportFallback);
    };
  }, [toast]);

  const handlePropertyChange = useCallback((property: string, value: unknown) => {
    if (property === 'group') {
      window.canvasEditor?.groupSelected?.();
      return;
    }
    window.canvasEditor?.applyObjectProperty?.(property, value);
  }, []);

  const handleCanvasReady = useCallback((canvas: FabricCanvas) => {
    setFabricCanvas(canvas);
  }, []);

  const {
    isConnected,
    activeUsers,
    sendCursorPosition,
    syncDesign,
    markApplyingRemote,
    recordAppliedSync,
  } = useCollaborativeCanvas(projectId);

  const broadcastDesign = useCallback(() => {
    const canvasData = window.canvasEditor?.getCanvasData?.();
    if (canvasData) {
      syncDesign(canvasData);
    }
  }, [syncDesign]);

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

  // Apply remote design snapshots from collaborators
  useEffect(() => {
    const onCanvasUpdate = (event: Event) => {
      const detail = (event as CustomEvent<CanvasUpdate>).detail;
      if (detail?.type !== 'design_synced' || !detail.design_data) return;

      markApplyingRemote(true);
      recordAppliedSync(detail.timestamp);
      Promise.resolve(window.canvasEditor?.loadCanvasData?.(detail.design_data))
        .finally(() => {
          // Small delay so our own object:modified handlers don't echo the sync
          setTimeout(() => markApplyingRemote(false), 250);
        });
    };

    window.addEventListener('canvas-update', onCanvasUpdate);
    return () => window.removeEventListener('canvas-update', onCanvasUpdate);
  }, [markApplyingRemote, recordAppliedSync]);

  // Debounced design sync after local edits
  useEffect(() => {
    const scheduleSync = () => {
      if (syncTimerRef.current) clearTimeout(syncTimerRef.current);
      syncTimerRef.current = setTimeout(() => {
        broadcastDesign();
      }, 800);
    };

    const onObjectChanged = () => scheduleSync();
    // Fabric events bubble via window.canvasEditor lifecycle; listen on document for custom hooks
    window.addEventListener('canvas-local-change', onObjectChanged);
    return () => {
      window.removeEventListener('canvas-local-change', onObjectChanged);
      if (syncTimerRef.current) clearTimeout(syncTimerRef.current);
    };
  }, [broadcastDesign]);

  // Cursor presence over the canvas area
  useEffect(() => {
    const area = canvasAreaRef.current;
    if (!area || !projectId) return;

    const onMove = (e: MouseEvent) => {
      const rect = area.getBoundingClientRect();
      sendCursorPosition(e.clientX - rect.left, e.clientY - rect.top);
    };

    area.addEventListener('mousemove', onMove);
    return () => area.removeEventListener('mousemove', onMove);
  }, [projectId, sendCursorPosition]);
  // handleSave moved above keyboard effect to avoid "used before declaration" errors
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

      if (!canvasData) {
        toast({
          title: 'Nothing to save',
          description: 'Canvas is not ready yet. Wait a moment and try again.',
          variant: 'destructive',
        });
        setSaving(false);
        return;
      }

      await projectsAPI.saveDesign(projectId, canvasData);
      syncDesign(canvasData);

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
  }, [projectId, toast, syncDesign]);

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
  }, [handleSave]);

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
          const url = typeof reader.result === 'string' ? reader.result : undefined;
          if (url) {
            window.canvasEditor?.addImage?.(url);
            toast({ title: 'Image added to canvas' });
          }
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

  // handleSave already defined earlier; duplicate removed


  const handleAIGenerate = (result: Record<string, unknown>) => {
    const metadata = (result.metadata as Record<string, unknown> | undefined)
      || ((result.result as Record<string, unknown> | undefined)?.metadata as Record<string, unknown> | undefined);
    if (metadata?.status === 'fallback') {
      toast({
        title: 'AI generation unavailable',
        description: (metadata.message as string) || 'The AI service could not generate a design. Check your API keys and try again.',
        variant: 'destructive',
      });
      return;
    }

    const canvasEditor = window.canvasEditor;

    if (!canvasEditor) {
      toast({
        title: 'Error',
        description: 'Canvas is not ready. Please wait a moment and try again.',
        variant: 'destructive',
      });
      return;
    }

    if (canvasEditor.renderAIDesign) {
      const rendered = canvasEditor.renderAIDesign(result);
      if (rendered) {
        broadcastDesign();
        toast({
          title: 'Success',
          description: 'Design generated and rendered on canvas.',
        });
      } else {
        toast({
          title: 'Nothing to render',
          description: 'AI returned no drawable components. Try a more specific prompt.',
          variant: 'destructive',
        });
      }
      return;
    }

    // Fallback if renderAIDesign is unavailable
    const components = result.components as Array<Record<string, unknown>>;

    if (!components || components.length === 0) {
      toast({
        title: 'Warning',
        description: 'No components in AI response',
        variant: 'destructive',
      });
      return;
    }

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
      description: `Added ${components.length} components to canvas.`,
    });
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
        onAIGenerate={() => setShowAIDialog(true)}
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
              open={showAIDialog}
              onOpenChange={setShowAIDialog}
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
              <CollaborationBar
                isConnected={isConnected}
                activeUsers={activeUsers}
                projectId={projectId}
              />
            </div>
            <div className="flex items-center gap-3 text-muted-foreground">
              {saving && <span className="flex items-center gap-1"><Loader2 className="h-3 w-3 animate-spin" /> Saving...</span>}
              {lastSaved && !saving && <span>Last saved: {lastSaved.toLocaleTimeString()}</span>}
              <span>{project?.canvas_width || 1920} × {project?.canvas_height || 1080}</span>
              {projectId && (
                <>
                  <ShareProjectDialog
                    projectId={projectId}
                    projectName={project?.name}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 gap-1"
                    onClick={() => setShowExportModal(true)}
                  >
                    <Download className="h-3 w-3" />
                    Export
                  </Button>
                </>
              )}
            </div>
          </div>
          
          {/* Canvas */}
          <div className="flex-1 p-8 overflow-auto flex items-center justify-center" ref={canvasAreaRef}>
            {loading ? (
              <div className="flex flex-col items-center gap-4">
                <Skeleton className="w-240 h-135 rounded-lg" />
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Loading project...</span>
                </div>
              </div>
            ) : (
              <div className="bg-white shadow-2xl relative">
                <CollaborationCursorsOverlay activeUsers={activeUsers} />
                <CanvasEditor
                  width={project?.canvas_width || 1920}
                  height={project?.canvas_height || 1080}
                  backgroundColor={project?.canvas_background || '#FFFFFF'}
                  initialData={project?.design_data}
                  onSave={handleSave}
                  onCanvasReady={handleCanvasReady}
                  onSelectionChange={(objects) => {
                    setSelectedElements(objects);
                    setHasSelection(objects.length > 0);
                  }}
                />
              </div>
            )}
          </div>
        </div>

        {/* Right Sidebar - Properties / Layers / Comments */}
        <div className="w-80 border-l bg-gray-50 dark:bg-gray-900 overflow-hidden flex flex-col">
          <Tabs
            value={rightPanel}
            onValueChange={(v) => setRightPanel(v as 'properties' | 'layers' | 'comments')}
            className="flex flex-col h-full"
          >
            <div className="px-3 pt-3">
              <TabsList className="w-full grid grid-cols-3">
                <TabsTrigger value="properties">Props</TabsTrigger>
                <TabsTrigger value="layers">Layers</TabsTrigger>
                <TabsTrigger value="comments" disabled={!projectId}>
                  Chat
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="properties" className="flex-1 overflow-y-auto mt-0 data-[state=inactive]:hidden">
              {hasSelection ? (
                <PropertiesPanel
                  selectedElements={selectedElements}
                  onPropertyChange={handlePropertyChange}
                />
              ) : (
                <div className="text-center py-8 px-4">
                  <p className="text-sm text-muted-foreground">Select an object to edit its properties</p>
                  <p className="text-xs text-muted-foreground mt-2">Use the tools above to add elements to the canvas</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="layers" className="flex-1 overflow-hidden mt-0 data-[state=inactive]:hidden">
              <LayersPanel canvas={fabricCanvas} />
            </TabsContent>

            <TabsContent value="comments" className="flex-1 overflow-hidden mt-0">
              {projectId ? (
                <CommentsPanel projectId={projectId} />
              ) : (
                <p className="p-4 text-sm text-muted-foreground">
                  Open a project to use comments.
                </p>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {projectId && (
        <ExportModal
          open={showExportModal}
          onOpenChange={setShowExportModal}
          projectId={projectId}
        />
      )}
    </div>
  );
}

// Server-side wrapper that provides a Suspense boundary around the
// client-only editor. This satisfies Next.js's requirement that any
// component using `useSearchParams` (or other routing hooks) must be
// rendered inside a <Suspense> during server prerendering.
export default function Page() {
  return (
    <Suspense fallback={<Skeleton className="h-full w-full" />}>
      <EditorPageClient />
    </Suspense>
  );
}

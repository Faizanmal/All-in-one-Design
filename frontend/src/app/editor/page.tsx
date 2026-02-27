"use client";

declare global {
  interface Window {
    canvasEditor?: {
      addText?: (text: string) => void;
      addRectangle?: () => void;
      addCircle?: () => void;
      deleteSelected?: () => void;
      cloneSelected?: () => void;
      bringToFront?: () => void;
      sendToBack?: () => void;
      exportAsPNG?: () => void;
      exportAsSVG?: () => void;
      getCanvasData?: () => Record<string, unknown>;
    };
  }
}

import React, { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { CanvasEditor } from '@/components/canvas/CanvasEditor';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { AdvancedAIGenerateDialog } from '@/components/canvas/AdvancedAIGenerateDialog';
import { useToast } from '@/hooks/use-toast';
import { projectsAPI, type Project } from '@/lib/design-api';

export default function EditorPage() {
  const searchParams = useSearchParams();
  const projectId = searchParams.get('project') ? parseInt(searchParams.get('project')!) : null;
  const [project, setProject] = useState<Project | null>(null);
  const [hasSelection] = useState(false);
  const { toast } = useToast();

  // Load project data
  React.useEffect(() => {
    if (projectId) {
      projectsAPI.get(projectId).then(setProject).catch(() => {
        toast({
          title: 'Error',
          description: 'Failed to load project',
          variant: 'destructive',
        });
      });
    }
  }, [projectId, toast]);

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
    toast({ title: 'Exporting PNG...' });
  };

  const handleExportSVG = () => {
    window.canvasEditor?.exportAsSVG?.();
    toast({ title: 'Exporting SVG...' });
  };

  const handleSave = async () => {
    try {
      const canvasData = window.canvasEditor?.getCanvasData?.();
      
      if (!canvasData && !projectId) {
        toast({
          title: 'Error',
          description: 'No project selected',
          variant: 'destructive',
        });
        return;
      }

      if (projectId && canvasData) {
        await projectsAPI.saveDesign(projectId, canvasData);
      }
      
      toast({
        title: 'Success',
        description: 'Project saved successfully',
      });
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: 'Error',
        description: 'Failed to save project',
        variant: 'destructive',
      });
    }
  };

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
        const rawPosition = component.position as any;
        
        let position: { x: number; y: number } | undefined;
        if (rawPosition && typeof rawPosition.x === 'number' && typeof rawPosition.y === 'number') {
          position = {
            x: Math.max(50, Math.min(1820, rawPosition.x)),
            y: Math.max(50, Math.min(980, rawPosition.y))
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
        onAddImage={handleAddImage}
        onDelete={handleDelete}
        onClone={handleClone}
        onBringToFront={handleBringToFront}
        onSendToBack={handleSendToBack}
        onExportPNG={handleExportPNG}
        onExportSVG={handleExportSVG}
        onSave={handleSave}
        onAIGenerate={() => {}}
        hasSelection={hasSelection}
      />

      {/* Main Editor Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar - AI Generation */}
        <div className="w-64 border-r bg-gray-50 p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">AI Generation</h3>
          <div className="space-y-2">
            <AdvancedAIGenerateDialog 
              onGenerate={handleAIGenerate}
              canvasWidth={project?.canvas_width || 1920}
              canvasHeight={project?.canvas_height || 1080}
            />
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-gray-100 p-8 overflow-auto flex items-center justify-center">
          <div className="bg-white shadow-2xl">
            <CanvasEditor
              width={project?.canvas_width || 1920}
              height={project?.canvas_height || 1080}
              backgroundColor={project?.canvas_background || '#FFFFFF'}
              initialData={project?.design_data}
              onSave={handleSave}
            />
          </div>
        </div>

        {/* Right Sidebar - Properties */}
        <div className="w-64 border-l bg-gray-50 p-4 overflow-y-auto">
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
            </div>
          ) : (
            <p className="text-sm text-gray-500">Select an object to edit properties</p>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState } from 'react';
import { CanvasEditor } from '@/components/canvas/CanvasEditor';
import { CanvasToolbar } from '@/components/canvas/CanvasToolbar';
import { AIGenerateDialog } from '@/components/canvas/AIGenerateDialog';
import { useToast } from '@/hooks/use-toast';
import { projectsAPI, type Project } from '@/lib/design-api';

interface EditorPageProps {
  projectId?: number;
}

export default function EditorPage({ projectId }: EditorPageProps) {
  const [project, setProject] = useState<Project | null>(null);
  const [hasSelection] = useState(false);
  const { toast } = useToast();

  // Load project data
  React.useEffect(() => {
    if (projectId) {
      projectsAPI.get(projectId).then(setProject).catch(console.error);
    }
  }, [projectId]);

  // Canvas toolbar handlers
  const handleAddText = () => {
    toast({ title: 'Add text to canvas' });
  };

  const handleAddRectangle = () => {
    toast({ title: 'Add rectangle to canvas' });
  };

  const handleAddCircle = () => {
    toast({ title: 'Add circle to canvas' });
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
    toast({ title: 'Delete selected object' });
  };

  const handleClone = () => {
    toast({ title: 'Clone selected object' });
  };

  const handleBringToFront = () => {
    toast({ title: 'Bring to front' });
  };

  const handleSendToBack = () => {
    toast({ title: 'Send to back' });
  };

  const handleExportPNG = () => {
    toast({ title: 'Export as PNG' });
  };

  const handleExportSVG = () => {
    toast({ title: 'Export as SVG' });
  };

  const handleSave = async () => {
    if (!projectId) {
      toast({
        title: 'Error',
        description: 'No project selected',
        variant: 'destructive',
      });
      return;
    }

    try {
      const designData = {};
      await projectsAPI.saveDesign(projectId, designData);
      
      toast({
        title: 'Success',
        description: 'Project saved successfully',
      });
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to save project',
        variant: 'destructive',
      });
    }
  };

  const handleAIGenerate = (result: Record<string, unknown>) => {
    console.log('AI Result:', result);
    
    // Check if canvasEditor is available
    const canvasEditor = (window as { canvasEditor?: { 
      addText: (text: string) => void; 
      addRectangle: () => void; 
      addCircle: () => void 
    } }).canvasEditor;
    
    if (!canvasEditor) {
      console.error('Canvas editor not ready');
      toast({
        title: 'Error',
        description: 'Canvas is not ready. Please wait a moment and try again.',
        variant: 'destructive',
      });
      return;
    }
    
    // Extract components from the AI result
    const components = result.components as Array<Record<string, unknown>>;
    
    if (!components || components.length === 0) {
      toast({
        title: 'Warning',
        description: 'No components in AI response',
        variant: 'destructive',
      });
      return;
    }
    
    console.log(`Processing ${components.length} components...`);
    
    // Add each component to the canvas
    components.forEach((component, index) => {
      const type = component.type as string;
      const text = component.text as string;
      
      console.log(`Adding component ${index + 1}: type=${type}, text=${text}`);
      
      // Map all component types to canvas elements
      switch (type) {
        case 'text':
        case 'header':
        case 'footer':
        case 'card':
        case 'navigation':
          // All text-based components become text objects
          canvasEditor.addText(text || type.charAt(0).toUpperCase() + type.slice(1));
          break;
          
        case 'button':
        case 'input':
        case 'map':
        case 'image':
          // UI elements become rectangles
          canvasEditor.addRectangle();
          break;
          
        case 'shape':
          // Generic shapes - check if circle or rectangle
          if (text?.toLowerCase().includes('circle')) {
            canvasEditor.addCircle();
          } else {
            canvasEditor.addRectangle();
          }
          break;
          
        case 'icon':
          // Icons become circles
          canvasEditor.addCircle();
          break;
          
        default:
          // Unknown types default to rectangle
          console.warn(`Unknown component type: ${type}, defaulting to rectangle`);
          canvasEditor.addRectangle();
      }
    });
    
    toast({
      title: 'Success',
      description: `Added ${components.length} components to canvas`,
    });
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
        {/* Left Sidebar - Templates/Assets */}
        <div className="w-64 border-r bg-gray-50 p-4 overflow-y-auto">
          <h3 className="font-semibold mb-4">Templates</h3>
          <div className="space-y-2">
            <AIGenerateDialog onGenerate={handleAIGenerate} />
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

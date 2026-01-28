import type { FabricCanvas, FabricObject, FabricEvent } from '@/types/fabric';
"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Canvas, IText, Rect, Circle, Image as FabricImage, Object as FabricObjectClass } from 'fabric';
interface CanvasEditorProps {
  width?: number;
  height?: number;
  backgroundColor?: string;
  onSave?: (json: Record<string, unknown>) => void;
  initialData?: Record<string, unknown>;
}

export const CanvasEditor: React.FC<CanvasEditorProps> = ({
  width = 1920,
  height = 1080,
  backgroundColor = '#FFFFFF',
  onSave,
  initialData,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [selectedObject, setSelectedObject] = useState<FabricObject | null>(null);

  // Initialize canvas
  useEffect(() => {
    if (!canvasRef.current) return;

    const fabricCanvas = new Canvas(canvasRef.current, {
      width: width,
      height: height,
      backgroundColor: backgroundColor,
    });

    // Load initial data if provided
    if (initialData) {
      fabricCanvas.loadFromJSON(initialData as Record<string, unknown>).then(() => {
        fabricCanvas.renderAll();
      }).catch(console.error);
    }

    // Event listeners
    fabricCanvas.on('selection:created', (e: { selected?: FabricObject[] }) => {
      setSelectedObject(e.selected?.[0] || null);
    });

    fabricCanvas.on('selection:updated', (e: { selected?: FabricObject[] }) => {
      setSelectedObject(e.selected?.[0] || null);
    });

    fabricCanvas.on('selection:cleared', () => {
      setSelectedObject(null);
    });

    setCanvas(fabricCanvas);

    return () => {
      fabricCanvas.dispose();
    };
  }, [width, height, backgroundColor, initialData]);

  // Save canvas state
  const handleSave = useCallback(() => {
    if (canvas && onSave) {
      const json = canvas.toJSON();
      onSave(json);
    }
  }, [canvas, onSave]);

  // Add text
  const addText = useCallback((text: string = 'New Text') => {
    if (!canvas) return;

    const textObj = new IText(text, {
      left: 100,
      top: 100,
      fontSize: 24,
      fontFamily: 'Arial',
      fill: '#000000',
    });

    canvas.add(textObj as unknown as FabricObject);
    canvas.setActiveObject(textObj as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas]);

  // Add rectangle
  const addRectangle = useCallback(() => {
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

    canvas.add(rect as unknown as FabricObject);
    canvas.setActiveObject(rect as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas]);

  // Add circle
  const addCircle = useCallback(() => {
    if (!canvas) return;

    const circle = new Circle({
      left: 100,
      top: 100,
      radius: 50,
      fill: '#10B981',
      stroke: '#047857',
      strokeWidth: 2,
    });

    canvas.add(circle as unknown as FabricObject);
    canvas.setActiveObject(circle as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas]);

  // Add image from URL
  const addImage = useCallback((url: string) => {
    if (!canvas) return;

    FabricImage.fromURL(url).then((img: FabricImage) => {
      img.scale(0.5);
      img.set({
        left: 100,
        top: 100,
      });
      canvas.add(img as unknown as FabricObject);
      canvas.setActiveObject(img as unknown as FabricObject);
      canvas.renderAll();
    }).catch(console.error);
  }, [canvas]);

  // Delete selected object
  const deleteSelected = useCallback(() => {
    if (!canvas || !selectedObject) return;

    canvas.remove(selectedObject);
    canvas.renderAll();
  }, [canvas, selectedObject]);

  // Clone selected object
  const cloneSelected = useCallback(() => {
    if (!canvas || !selectedObject) return;

    selectedObject.clone().then((cloned: FabricObject) => {
      cloned.set({
        left: (cloned.left || 0) + 20,
        top: (cloned.top || 0) + 20,
      });
      canvas.add(cloned);
      canvas.setActiveObject(cloned);
      canvas.renderAll();
    }).catch(console.error);
  }, [canvas, selectedObject]);

  // Bring to front
  const bringToFront = useCallback(() => {
    if (!canvas || !selectedObject) return;
    canvas.bringObjectToFront(selectedObject);
    canvas.renderAll();
  }, [canvas, selectedObject]);

  // Send to back
  const sendToBack = useCallback(() => {
    if (!canvas || !selectedObject) return;
    canvas.sendObjectToBack(selectedObject);
    canvas.renderAll();
  }, [canvas, selectedObject]);

  // Export as PNG
  const exportAsPNG = useCallback(() => {
    if (!canvas) return;
    
    const dataURL = canvas.toDataURL({
      format: 'png',
      quality: 1,
      multiplier: 2,
    });

    const link = document.createElement('a');
    link.download = 'design.png';
    link.href = dataURL;
    link.click();
  }, [canvas]);

  // Export as JPG
  const exportAsJPG = useCallback(() => {
    if (!canvas) return;
    
    const dataURL = canvas.toDataURL({
      format: 'jpeg',
      quality: 0.9,
      multiplier: 2,
    });

    const link = document.createElement('a');
    link.download = 'design.jpg';
    link.href = dataURL;
    link.click();
  }, [canvas]);

  // Export as SVG
  const exportAsSVG = useCallback(() => {
    if (!canvas) return;

    const svg = canvas.toSVG();
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.download = 'design.svg';
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  }, [canvas]);

  // Export as PDF (using backend)
  const exportAsPDF = useCallback(async (projectId: number) => {
    try {
      const response = await fetch(`/api/projects/projects/${projectId}/export_pdf/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('auth_token')}`,
        },
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = 'design.pdf';
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF export failed:', error);
    }
  }, []);

  // Helper function to convert hex to RGB
  const hexToRgb = useCallback((hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16) / 255,
      g: parseInt(result[2], 16) / 255,
      b: parseInt(result[3], 16) / 255,
    } : { r: 0, g: 0, b: 0 };
  }, []);

  // Export as Figma JSON
  const exportAsFigmaJSON = useCallback(() => {
    if (!canvas) return;

    const objects = canvas.getObjects();
    
    const figmaFormat = {
      name: "Exported Design",
      type: "FRAME",
      width: canvas.width,
      height: canvas.height,
      children: objects.map((obj) => {
        const baseNode = {
          name: obj.type || 'Object',
          x: obj.left || 0,
          y: obj.top || 0,
          width: (obj.width || 0) * (obj.scaleX || 1),
          height: (obj.height || 0) * (obj.scaleY || 1),
          rotation: obj.angle || 0,
          opacity: obj.opacity || 1,
        };

        const objWithProps = obj as unknown as Record<string, unknown>;
        
        if (obj.type === 'i-text' || obj.type === 'text') {
          return {
            ...baseNode,
            type: 'TEXT',
            characters: (objWithProps.text as string) || '',
            fontSize: (objWithProps.fontSize as number) || 16,
            fontFamily: (objWithProps.fontFamily as string) || 'Inter',
            fills: [{
              type: 'SOLID',
              color: hexToRgb((objWithProps.fill as string) || '#000000'),
            }],
          };
        } else if (obj.type === 'rect') {
          return {
            ...baseNode,
            type: 'RECTANGLE',
            fills: [{
              type: 'SOLID',
              color: hexToRgb((objWithProps.fill as string) || '#CCCCCC'),
            }],
            cornerRadius: (objWithProps.rx as number) || 0,
          };
        } else if (obj.type === 'circle') {
          return {
            ...baseNode,
            type: 'ELLIPSE',
            fills: [{
              type: 'SOLID',
              color: hexToRgb((objWithProps.fill as string) || '#CCCCCC'),
            }],
          };
        }

        return baseNode;
      }),
    };

    const json = JSON.stringify(figmaFormat, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = 'design-figma.json';
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  }, [canvas, hexToRgb]);

  // Expose methods for external use
  useEffect(() => {
    if (canvas) {
      (window as { canvasEditor?: unknown }).canvasEditor = {
        addText,
        addRectangle,
        addCircle,
        addImage,
        deleteSelected,
        cloneSelected,
        bringToFront,
        sendToBack,
        exportAsPNG,
        exportAsJPG,
        exportAsSVG,
        exportAsPDF,
        exportAsFigmaJSON,
        handleSave,
      };
      console.log('CanvasEditor methods exposed to window.canvasEditor');
    }
  }, [canvas, addText, addRectangle, addCircle, addImage, deleteSelected, cloneSelected, bringToFront, sendToBack, exportAsPNG, exportAsJPG, exportAsSVG, exportAsPDF, exportAsFigmaJSON, handleSave]);

  return (
    <div className="canvas-editor">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default CanvasEditor;

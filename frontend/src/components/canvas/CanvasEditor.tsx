"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Canvas, IText, Rect, Circle, Image as FabricImage, Triangle, Line, Point, ActiveSelection } from 'fabric';
import type { FabricObject } from 'fabric';
import { AdvancedCanvasRenderer } from './AdvancedCanvasRenderer';

interface CanvasEditorProps {
  width?: number;
  height?: number;
  backgroundColor?: string;
  onSave?: (json: Record<string, unknown>) => void;
  initialData?: Record<string, unknown>;
  onCanvasReady?: (canvas: Canvas) => void;
}

export const CanvasEditor: React.FC<CanvasEditorProps> = ({
  width = 1920,
  height = 1080,
  backgroundColor = '#FFFFFF',
  onSave,
  initialData,
  onCanvasReady,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [selectedObject, setSelectedObject] = useState<FabricObject | null>(null);
  const [renderer, setRenderer] = useState<AdvancedCanvasRenderer | null>(null);
  const historyRef = useRef<string[]>([]);
  const historyIndexRef = useRef<number>(-1);
  const isUndoingRef = useRef<boolean>(false);

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

    // History tracking
    const saveHistory = () => {
      if (isUndoingRef.current) return;
      const json = JSON.stringify(fabricCanvas.toJSON());
      historyRef.current = historyRef.current.slice(0, historyIndexRef.current + 1);
      historyRef.current.push(json);
      historyIndexRef.current = historyRef.current.length - 1;
    };

    fabricCanvas.on('object:added', saveHistory);
    fabricCanvas.on('object:removed', saveHistory);
    fabricCanvas.on('object:modified', saveHistory);

    // Save initial state
    saveHistory();

    setCanvas(fabricCanvas);
    onCanvasReady?.(fabricCanvas);
    
    // Initialize advanced renderer
    const advancedRenderer = new AdvancedCanvasRenderer(fabricCanvas);
    setRenderer(advancedRenderer);
    console.log('Advanced canvas renderer initialized');

    return () => {
      fabricCanvas.dispose();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [width, height, backgroundColor, initialData, onCanvasReady]);

  // Save canvas state
  const handleSave = useCallback(() => {
    if (canvas && onSave) {
      const json = canvas.toJSON();
      onSave(json);
    }
  }, [canvas, onSave]);

  // Undo
  const undo = useCallback(() => {
    if (!canvas || historyIndexRef.current <= 0) return;
    isUndoingRef.current = true;
    historyIndexRef.current -= 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas.loadFromJSON(JSON.parse(json)).then(() => {
      canvas.renderAll();
      isUndoingRef.current = false;
    });
  }, [canvas]);

  // Redo
  const redo = useCallback(() => {
    if (!canvas || historyIndexRef.current >= historyRef.current.length - 1) return;
    isUndoingRef.current = true;
    historyIndexRef.current += 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas.loadFromJSON(JSON.parse(json)).then(() => {
      canvas.renderAll();
      isUndoingRef.current = false;
    });
  }, [canvas]);

  // Get auto-position for new objects
  const getAutoPosition = useCallback((canvasInstance: Canvas) => {
    const selectable = canvasInstance.getObjects().filter((o: FabricObject) => o.selectable !== false);
    const count = selectable.length;
    const x = 100 + (count * 50) % (width - 200);
    const y = 100 + Math.floor((count * 50) / (width - 200)) * 150;
    return { x, y };
  }, [width]);

  // Add text
  const addText = useCallback((text: string = 'New Text', position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const textObj = new IText(text, {
      left: x, top: y,
      fontSize: 24, fontFamily: 'Arial', fill: '#000000',
    });
    canvas.add(textObj as unknown as FabricObject);
    canvas.setActiveObject(textObj as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add rectangle
  const addRectangle = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const rect = new Rect({ left: x, top: y, width: 200, height: 100, fill: '#3B82F6', stroke: '#1E40AF', strokeWidth: 2 });
    canvas.add(rect as unknown as FabricObject);
    canvas.setActiveObject(rect as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add circle
  const addCircle = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const circle = new Circle({ left: x, top: y, radius: 50, fill: '#10B981', stroke: '#047857', strokeWidth: 2 });
    canvas.add(circle as unknown as FabricObject);
    canvas.setActiveObject(circle as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add triangle
  const addTriangle = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const triangle = new Triangle({ left: x, top: y, width: 150, height: 130, fill: '#F59E0B', stroke: '#D97706', strokeWidth: 2 });
    canvas.add(triangle as unknown as FabricObject);
    canvas.setActiveObject(triangle as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add line
  const addLine = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const line = new Line([x, y, x + 200, y], { stroke: '#6B7280', strokeWidth: 3, selectable: true });
    canvas.add(line as unknown as FabricObject);
    canvas.setActiveObject(line as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add image from URL
  const addImage = useCallback((url?: string, position?: { x: number; y: number }) => {
    if (!canvas) return;

    const imageUrl = url || 'https://via.placeholder.com/200x100/cccccc/000000?text=Image';
    
    let x: number, y: number;
    
    if (position) {
      // Use AI-provided position
      x = position.x;
      y = position.y;
    } else {
      // Use automatic positioning (only count selectable objects)
      const selectableObjects = canvas.getObjects().filter((obj: FabricObject) => obj.selectable !== false);
      const objectsCount = selectableObjects.length;
      x = 100 + (objectsCount * 50) % (width - 200); // Wrap horizontally
      y = 100 + Math.floor((objectsCount * 50) / (width - 200)) * 150; // Stack vertically
    }

    FabricImage.fromURL(imageUrl).then((img: FabricImage) => {
      img.scale(0.5);
      img.set({
        left: x,
        top: y,
      });
      canvas.add(img as unknown as FabricObject);
      canvas.setActiveObject(img as unknown as FabricObject);
      canvas.renderAll();
    }).catch(console.error);
  }, [canvas, width]);

  // Delete selected object
  const deleteSelected = useCallback(() => {
    if (!canvas) return;
    const active = canvas.getActiveObjects();
    if (!active.length) return;
    active.forEach((o) => canvas.remove(o));
    canvas.discardActiveObject();
    canvas.renderAll();
  }, [canvas]);

  // Clone selected object
  const cloneSelected = useCallback(() => {
    if (!canvas || !selectedObject) return;
    selectedObject.clone().then((cloned: FabricObject) => {
      cloned.set({ left: (cloned.left || 0) + 20, top: (cloned.top || 0) + 20 });
      canvas.add(cloned);
      canvas.setActiveObject(cloned);
      canvas.renderAll();
    }).catch(console.error);
  }, [canvas, selectedObject]);

  // Zoom controls
  const zoomIn = useCallback(() => {
    if (!canvas) return;
    const zoom = Math.min(canvas.getZoom() * 1.2, 5);
    canvas.setZoom(zoom);
    canvas.renderAll();
  }, [canvas]);

  const zoomOut = useCallback(() => {
    if (!canvas) return;
    const zoom = Math.max(canvas.getZoom() / 1.2, 0.1);
    canvas.setZoom(zoom);
    canvas.renderAll();
  }, [canvas]);

  const zoomToFit = useCallback(() => {
    if (!canvas) return;
    canvas.setZoom(1);
    canvas.absolutePan(new Point(0, 0));
    canvas.renderAll();
  }, [canvas]);

  // Group selected
  const groupSelected = useCallback(() => {
    if (!canvas) return;
    const active = canvas.getActiveObject();
    if (!active || active.type !== 'activeselection') return;
    (active as unknown as ActiveSelection).toGroup();
    canvas.requestRenderAll();
  }, [canvas]);

  // Ungroup selected
  const ungroupSelected = useCallback(() => {
    if (!canvas) return;
    const active = canvas.getActiveObject();
    if (!active || active.type !== 'group') return;
    (active as unknown as { toActiveSelection: () => FabricObject }).toActiveSelection();
    canvas.requestRenderAll();
  }, [canvas]);

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
  
  // Render AI-generated design
  const renderAIDesign = useCallback((aiResult: Record<string, unknown>) => {
    if (!renderer) {
      console.error('Renderer not initialized');
      return;
    }
    
    console.log('Rendering AI-generated design:', aiResult);
    renderer.renderAIResult(aiResult);
  }, [renderer]);

  // Expose methods for external use
  useEffect(() => {
    if (canvas) {
      (window as { canvasEditor?: unknown }).canvasEditor = {
        addText,
        addRectangle,
        addCircle,
        addTriangle,
        addLine,
        addImage,
        deleteSelected,
        cloneSelected,
        bringToFront,
        sendToBack,
        groupSelected,
        ungroupSelected,
        zoomIn,
        zoomOut,
        zoomToFit,
        undo,
        redo,
        exportAsPNG,
        exportAsJPG,
        exportAsSVG,
        exportAsPDF,
        exportAsFigmaJSON,
        handleSave,
        renderAIDesign,
      };
      console.log('CanvasEditor methods exposed to window.canvasEditor');
    }
  }, [canvas, addText, addRectangle, addCircle, addTriangle, addLine, addImage, deleteSelected, cloneSelected, bringToFront, sendToBack, groupSelected, ungroupSelected, zoomIn, zoomOut, zoomToFit, undo, redo, exportAsPNG, exportAsJPG, exportAsSVG, exportAsPDF, exportAsFigmaJSON, handleSave, renderAIDesign]);

  return (
    <div className="canvas-editor">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default CanvasEditor;

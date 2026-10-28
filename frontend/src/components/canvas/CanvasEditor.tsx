"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Canvas, IText, Rect, Circle, Image as FabricImage, Triangle, Line, Point } from 'fabric';
import type { FabricObject } from 'fabric';
import { AdvancedCanvasRenderer } from './AdvancedCanvasRenderer';
import { getBearerAuthHeader } from '@/lib/auth-token';

const MAX_HISTORY = 50;

// Fabric 7 defaults originX/originY to center. The placement math here assumes
// top-left anchoring, so pin it rather than inherit the default.
const TOP_LEFT = { originX: 'left', originY: 'top' } as const;

export interface CanvasExportOptions {
  format?: 'png' | 'jpeg' | 'jpg';
  multiplier?: number;
  quality?: number;
  includeBackground?: boolean;
  fileName?: string;
}

interface CanvasEditorProps {
  width?: number;
  height?: number;
  backgroundColor?: string;
  onSave?: (json: Record<string, unknown>) => void;
  initialData?: Record<string, unknown>;
  onCanvasReady?: (canvas: Canvas) => void;
  onSelectionChange?: (objects: FabricObject[]) => void;
}

interface FabricCanvasElement extends HTMLCanvasElement {
  fabric?: Canvas;
}

interface FabricCanvasState {
  disposed?: boolean;
  destroyed?: boolean;
  elements?: {
    lower?: {
      ctx?: CanvasRenderingContext2D | null;
    };
  };
}

const isCanvasDestroyed = (target?: Canvas | null): boolean => {
  if (!target) return true;
  const t = target as FabricCanvasState;
  return Boolean(t.disposed || t.destroyed);
};

export const CanvasEditor: React.FC<CanvasEditorProps> = ({

  width = 1920,
  height = 1080,
  backgroundColor = '#FFFFFF',
  onSave,
  initialData,
  onCanvasReady,
  onSelectionChange,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<Canvas | null>(null);
  const loadControllerRef = useRef<AbortController | null>(null);
  const [canvas, setCanvas] = useState<Canvas | null>(null);
  const [, setSelectedObject] = useState<FabricObject | null>(null);
  const rendererRef = useRef<AdvancedCanvasRenderer | null>(null);
  const historyRef = useRef<string[]>([]);
  const historyIndexRef = useRef<number>(-1);
  const isUndoingRef = useRef<boolean>(false);
  const displayScaleRef = useRef(1);
  const scaleOuterRef = useRef<HTMLDivElement>(null);
  const onSelectionChangeRef = useRef(onSelectionChange);
  onSelectionChangeRef.current = onSelectionChange;

  // Initialize canvas once (avoid repeated initializations)
  useEffect(() => {
    if (!canvasRef.current) return;

    let mounted = true;

    const canvasElement = canvasRef.current as FabricCanvasElement;
    if (!canvasElement || !canvasElement.getContext) return;

    // Clean up any old Fabric instance attached to this element
    const existingFabric = canvasElement.fabric;
    if (existingFabric) {
      try {
        existingFabric.dispose();
      } catch (error) {
        console.warn('Error disposing existing fabric canvas on element:', error);
      }
    }

    if (fabricCanvasRef.current) {
      try {
        fabricCanvasRef.current.dispose();
      } catch (error) {
        console.warn('Error disposing existing fabric canvas ref:', error);
      }
      fabricCanvasRef.current = null;
    }

    // Set canvas dimensions explicitly
    canvasElement.width = width;
    canvasElement.height = height;

    const fabricCanvas = new Canvas(canvasElement, {
      width: width,
      height: height,
      backgroundColor: backgroundColor,
    });

    fabricCanvasRef.current = fabricCanvas;
    canvasElement.fabric = fabricCanvas;

    // Defensive overrides (avoid clearRect crash when context is missing due dispose race)
    const originalClearContext = fabricCanvas.clearContext.bind(fabricCanvas);
    fabricCanvas.clearContext = ((ctx: CanvasRenderingContext2D | null | undefined) => {
      if (!ctx || typeof ctx.clearRect !== 'function') {
        return;
      }
      try {
        originalClearContext(ctx);
      } catch (error) {
        console.warn('Fabric clearContext error (ignored):', error);
      }
    }) as unknown as typeof fabricCanvas.clearContext;

    const originalClear = fabricCanvas.clear.bind(fabricCanvas);
    fabricCanvas.clear = (() => {
      const extCanvas = fabricCanvas as FabricCanvasState;
      if (extCanvas.disposed || extCanvas.destroyed) {
        return;
      }
      const lowerContext = extCanvas.elements?.lower?.ctx;
      if (!lowerContext || typeof lowerContext.clearRect !== 'function') {
        return;
      }
      try {
        originalClear();
      } catch (error) {
        console.warn('Fabric clear() error (ignored):', error);
      }
    }) as unknown as typeof fabricCanvas.clear;

    // Load initial data if provided
    if (initialData) {
      const controller = new AbortController();
      loadControllerRef.current = controller;

      const components = initialData.components as unknown[] | undefined;
      const hasFabricObjects = Array.isArray(initialData.objects);
      const hasAIComponents = Array.isArray(components) && components.length > 0 && !hasFabricObjects;

      if (hasAIComponents) {
        // AI logo/layout payloads use components[] — render via AdvancedCanvasRenderer
        const renderer = new AdvancedCanvasRenderer(fabricCanvas);
        rendererRef.current = renderer;
        renderer.renderAIResult(initialData as Parameters<AdvancedCanvasRenderer['renderAIResult']>[0]);
      } else {
        fabricCanvas
          .loadFromJSON(initialData as Record<string, unknown>, undefined, {
            signal: controller.signal,
          })
          .then(() => {
            if (!mounted || fabricCanvas.disposed) return;
            fabricCanvas.renderAll();
          })
          .catch((error) => {
            if (!controller.signal.aborted) {
              console.error(error);
            }
          });
      }
    }

    const notifySelection = (objects: FabricObject[]) => {
      setSelectedObject(objects[0] || null);
      onSelectionChangeRef.current?.(objects);
      window.dispatchEvent(
        new CustomEvent('canvas-selection-change', {
          detail: { objects, hasSelection: objects.length > 0 },
        })
      );
    };

    // Event listeners
    fabricCanvas.on('selection:created', (e: { selected?: FabricObject[] }) => {
      notifySelection(e.selected || []);
    });

    fabricCanvas.on('selection:updated', (e: { selected?: FabricObject[] }) => {
      notifySelection(e.selected || []);
    });

    fabricCanvas.on('selection:cleared', () => {
      notifySelection([]);
    });

    // History tracking (capped to avoid unbounded memory growth)
    const saveHistory = () => {
      if (isUndoingRef.current) return;
      const json = JSON.stringify(fabricCanvas.toJSON());
      historyRef.current = historyRef.current.slice(0, historyIndexRef.current + 1);
      historyRef.current.push(json);
      if (historyRef.current.length > MAX_HISTORY) {
        const overflow = historyRef.current.length - MAX_HISTORY;
        historyRef.current = historyRef.current.slice(overflow);
      }
      historyIndexRef.current = historyRef.current.length - 1;
      window.dispatchEvent(new CustomEvent('canvas-local-change'));
    };

    fabricCanvas.on('object:added', saveHistory);
    fabricCanvas.on('object:removed', saveHistory);
    fabricCanvas.on('object:modified', saveHistory);

    // Save initial state
    saveHistory();

    setCanvas(fabricCanvas);
    rendererRef.current = new AdvancedCanvasRenderer(fabricCanvas);
    onCanvasReady?.(fabricCanvas);

    return () => {
      mounted = false;
      loadControllerRef.current?.abort();
      loadControllerRef.current = null;
      rendererRef.current = null;

      if (fabricCanvasRef.current) {
        try {
          fabricCanvasRef.current.dispose();
        } catch (error) {
          console.warn('Error disposing canvas on unmount:', error);
        }
        fabricCanvasRef.current = null;
      }
      if (canvasElement && canvasElement.fabric) {
        delete canvasElement.fabric;
      }
      setCanvas(null);
    };
  }, [width, height, backgroundColor, initialData, onCanvasReady]);

  // Update canvas dimensions and background when props change
  useEffect(() => {
    const fabricCanvas = fabricCanvasRef.current;
    if (!fabricCanvas || fabricCanvas.disposed) return;

    let needsRender = false;

    if (fabricCanvas.getWidth() !== width || fabricCanvas.getHeight() !== height) {
      fabricCanvas.setDimensions({ width, height });
      fabricCanvas.calcOffset();
      // Re-apply display scale so CSS transform stays in sync with design size
      const outer = scaleOuterRef.current;
      const next = displayScaleRef.current;
      const fabricRoot = fabricCanvas.getElement()?.parentElement as HTMLElement | null;
      if (outer) {
        outer.style.width = `${Math.round(width * next)}px`;
        outer.style.height = `${Math.round(height * next)}px`;
      }
      if (fabricRoot) {
        fabricRoot.style.transform = `scale(${next})`;
        fabricRoot.style.transformOrigin = '0 0';
        fabricRoot.style.width = `${width}px`;
        fabricRoot.style.height = `${height}px`;
      }
      needsRender = true;
    }

    if (fabricCanvas.backgroundColor !== backgroundColor) {
      fabricCanvas.set({ backgroundColor });
      needsRender = true;
    }

    if (needsRender) {
      fabricCanvas.renderAll();
    }
  }, [width, height, backgroundColor]);

  // Reload initial data when it changes (after mount)
  useEffect(() => {
    const fabricCanvas = fabricCanvasRef.current;
    if (!fabricCanvas || !initialData) return;

    const controller = new AbortController();
    loadControllerRef.current = controller;

    let mounted = true;
    const components = initialData.components as unknown[] | undefined;
    const hasFabricObjects = Array.isArray(initialData.objects);
    const hasAIComponents = Array.isArray(components) && components.length > 0 && !hasFabricObjects;

    const apply = async () => {
      if (hasAIComponents) {
        const renderer = rendererRef.current ?? new AdvancedCanvasRenderer(fabricCanvas);
        rendererRef.current = renderer;
        renderer.renderAIResult(initialData as Parameters<AdvancedCanvasRenderer['renderAIResult']>[0]);
        return;
      }
      await fabricCanvas.loadFromJSON(initialData as Record<string, unknown>, undefined, {
        signal: controller.signal,
      });
      if (!mounted || fabricCanvas.disposed) return;
      fabricCanvas.renderAll();
    };

    apply().catch((error) => {
      if (!controller.signal.aborted) {
        console.error(error);
      }
    });

    return () => {
      mounted = false;
      controller.abort();
      loadControllerRef.current = null;
    };
  }, [initialData]);

  // Notify canvas ready callback when it or onCanvasReady changes
  useEffect(() => {
    const fabricCanvas = fabricCanvasRef.current;
    if (!fabricCanvas) return;
    onCanvasReady?.(fabricCanvas);
  }, [onCanvasReady]);

  // Save canvas state
  const handleSave = useCallback(() => {
    if (!canvas || isCanvasDestroyed(canvas) || !onSave) return;
    const json = canvas.toJSON();
    onSave(json);
  }, [canvas, onSave]);

  // Undo
  const undo = useCallback(() => {
    if (!canvas || isCanvasDestroyed(canvas) || historyIndexRef.current <= 0) return;
    isUndoingRef.current = true;
    historyIndexRef.current -= 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas
      .loadFromJSON(JSON.parse(json))
      .then(() => {
        if (isCanvasDestroyed(canvas)) {
          isUndoingRef.current = false;
          return;
        }
        canvas.renderAll();
        isUndoingRef.current = false;
      })
      .catch(console.error);
  }, [canvas]);

  // Redo
  const redo = useCallback(() => {
    if (!canvas || isCanvasDestroyed(canvas) || historyIndexRef.current >= historyRef.current.length - 1) return;
    isUndoingRef.current = true;
    historyIndexRef.current += 1;
    const json = historyRef.current[historyIndexRef.current];
    canvas
      .loadFromJSON(JSON.parse(json))
      .then(() => {
        if (isCanvasDestroyed(canvas)) {
          isUndoingRef.current = false;
          return;
        }
        canvas.renderAll();
        isUndoingRef.current = false;
      })
      .catch(console.error);
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
      ...TOP_LEFT,
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
    const rect = new Rect({ ...TOP_LEFT, left: x, top: y, width: 200, height: 100, fill: '#3B82F6', stroke: '#1E40AF', strokeWidth: 2 });
    canvas.add(rect as unknown as FabricObject);
    canvas.setActiveObject(rect as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add circle
  const addCircle = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const circle = new Circle({ ...TOP_LEFT, left: x, top: y, radius: 50, fill: '#10B981', stroke: '#047857', strokeWidth: 2 });
    canvas.add(circle as unknown as FabricObject);
    canvas.setActiveObject(circle as unknown as FabricObject);
    canvas.renderAll();
  }, [canvas, getAutoPosition]);

  // Add triangle
  const addTriangle = useCallback((position?: { x: number; y: number }) => {
    if (!canvas) return;
    const { x, y } = position ?? getAutoPosition(canvas);
    const triangle = new Triangle({ ...TOP_LEFT, left: x, top: y, width: 150, height: 130, fill: '#F59E0B', stroke: '#D97706', strokeWidth: 2 });
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

    // No URL: insert a local placeholder rect instead of a broken external image host
    if (!url) {
      const placeholder = new Rect({
        ...TOP_LEFT,
        left: x,
        top: y,
        width: 200,
        height: 100,
        fill: '#E5E7EB',
        stroke: '#9CA3AF',
        strokeWidth: 1,
        rx: 4,
        ry: 4,
      });
      canvas.add(placeholder as unknown as FabricObject);
      canvas.setActiveObject(placeholder as unknown as FabricObject);
      canvas.renderAll();
      return;
    }

    FabricImage.fromURL(url).then((img: FabricImage) => {
      img.scale(0.5);
      img.set({
        ...TOP_LEFT,
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
    if (!canvas) return;
    const selectedObject = canvas.getActiveObject();
    if (!selectedObject) return;
    selectedObject.clone().then((cloned: FabricObject) => {
      cloned.set({ left: (cloned.left || 0) + 20, top: (cloned.top || 0) + 20 });
      canvas.add(cloned);
      canvas.setActiveObject(cloned);
      canvas.renderAll();
    }).catch(console.error);
  }, [canvas]);

  // Zoom controls — CSS transform on a wrapper (never touch Fabric backstore size).
  // setDimensions({ cssOnly }) previously corrupted layout for some Fabric 7 paths.

  const applyDisplayScale = useCallback((scale: number) => {
    if (!canvas) return;
    const next = Math.min(3, Math.max(0.1, scale));
    displayScaleRef.current = next;

    canvas.setZoom(1);
    canvas.setViewportTransform([1, 0, 0, 1, 0, 0]);
    if (canvas.getWidth() !== width || canvas.getHeight() !== height) {
      canvas.setDimensions({ width, height });
    }

    const outer = scaleOuterRef.current;
    const fabricRoot =
      (canvas.getElement()?.parentElement as HTMLElement | null) || null;

    // Outer = layout box at scaled size; inner Fabric root is design-sized + CSS scaled.
    if (outer) {
      outer.style.overflow = 'hidden';
      outer.style.width = `${Math.round(width * next)}px`;
      outer.style.height = `${Math.round(height * next)}px`;
    }
    if (fabricRoot) {
      fabricRoot.style.transform = `scale(${next})`;
      fabricRoot.style.transformOrigin = '0 0';
      fabricRoot.style.margin = '0';
    }
    canvas.requestRenderAll();
  }, [canvas, width, height]);

  const zoomIn = useCallback(() => {
    applyDisplayScale(displayScaleRef.current * 1.15);
  }, [applyDisplayScale]);

  const zoomOut = useCallback(() => {
    applyDisplayScale(displayScaleRef.current / 1.15);
  }, [applyDisplayScale]);

  const zoomToFit = useCallback(() => {
    if (!canvas) return;
    const canvasEl = canvas.getElement();
    const area =
      (canvasEl?.closest('.overflow-auto') as HTMLElement | null) ||
      (scaleOuterRef.current?.parentElement as HTMLElement | null);

    if (!area) {
      applyDisplayScale(1);
      return;
    }

    const pad = 64;
    const availW = Math.max(120, area.clientWidth - pad);
    const availH = Math.max(120, area.clientHeight - pad);
    const scale = Math.min(1, availW / width, availH / height);
    applyDisplayScale(scale);
  }, [canvas, width, height, applyDisplayScale]);

  // Group selected
  const groupSelected = useCallback(() => {
    if (!canvas) return;
    const active = canvas.getActiveObject();
    if (!active || active.type !== 'activeselection') return;
    // `toGroup` is not declared in current type defs, use type assertion
    (active as unknown as { toGroup(): void }).toGroup();
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
    if (!canvas) return;
    const selectedObject = canvas.getActiveObject();
    if (!selectedObject) return;
    canvas.bringObjectToFront(selectedObject);
    canvas.renderAll();
  }, [canvas]);

  // Send to back
  const sendToBack = useCallback(() => {
    if (!canvas) return;
    const selectedObject = canvas.getActiveObject();
    if (!selectedObject) return;
    canvas.sendObjectToBack(selectedObject);
    canvas.renderAll();
  }, [canvas]);

  const exportRaster = useCallback((opts: CanvasExportOptions = {}) => {
    if (!canvas || isCanvasDestroyed(canvas)) return;

    const format = opts.format === 'jpg' || opts.format === 'jpeg' ? 'jpeg' : 'png';
    const multiplier = opts.multiplier ?? 2;
    const quality = opts.quality ?? (format === 'jpeg' ? 0.9 : 1);
    const previousBg = canvas.backgroundColor;

    if (opts.includeBackground === false) {
      canvas.backgroundColor = 'transparent';
      canvas.renderAll();
    }

    const dataURL = canvas.toDataURL({
      format,
      quality,
      multiplier,
    });

    if (opts.includeBackground === false) {
      canvas.backgroundColor = previousBg;
      canvas.renderAll();
    }

    const link = document.createElement('a');
    link.download = opts.fileName || `design.${format === 'jpeg' ? 'jpg' : 'png'}`;
    link.href = dataURL;
    link.click();
  }, [canvas]);

  // Export as PNG
  const exportAsPNG = useCallback((opts?: CanvasExportOptions) => {
    exportRaster({ ...opts, format: 'png' });
  }, [exportRaster]);

  // Export as JPG
  const exportAsJPG = useCallback((opts?: CanvasExportOptions) => {
    exportRaster({ ...opts, format: 'jpeg' });
  }, [exportRaster]);

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

  // Export as PDF (backend first; fall back to high-res PNG so the user still gets an export)
  const exportAsPDF = useCallback(async (projectId: number) => {
    try {
      const response = await fetch(`/api/v1/projects/${projectId}/export_pdf/`, {
        method: 'POST',
        headers: {
          ...getBearerAuthHeader(),
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
      window.dispatchEvent(new CustomEvent('canvas-export-success', { detail: { format: 'pdf' } }));
    } catch (error) {
      console.error('PDF export failed, falling back to PNG:', error);
      exportAsPNG({ multiplier: 2, fileName: 'design-fallback.png' });
      window.dispatchEvent(
        new CustomEvent('canvas-export-fallback', {
          detail: {
            format: 'png',
            message: 'PDF export failed. Downloaded a PNG of your canvas instead.',
          },
        })
      );
    }
  }, [exportAsPNG]);

  const applyObjectProperty = useCallback((property: string, value: unknown) => {
    if (!canvas || isCanvasDestroyed(canvas)) return;
    const active = canvas.getActiveObjects();
    if (!active.length) return;

    const propMap: Record<string, string> = {
      x: 'left',
      y: 'top',
      rotation: 'angle',
      borderRadius: 'rx',
      blendMode: 'globalCompositeOperation',
      letterSpacing: 'charSpacing',
      textColor: 'fill',
    };

    active.forEach((obj) => {
      if (property === 'opacity' && typeof value === 'number') {
        obj.set('opacity', value > 1 ? value / 100 : value);
      } else if (property === 'shadow') {
        obj.set('shadow', value as never);
      } else if (property === 'group') {
        // handled by toolbar
      } else {
        const fabricProp = propMap[property] || property;
        obj.set(fabricProp as keyof FabricObject, value as never);
        if (property === 'borderRadius') {
          obj.set('ry', value as never);
        }
      }
      obj.setCoords();
    });
    canvas.requestRenderAll();
    window.dispatchEvent(new CustomEvent('canvas-local-change'));
  }, [canvas]);

  const getSelectedObjects = useCallback(() => {
    if (!canvas || isCanvasDestroyed(canvas)) return [];
    return canvas.getActiveObjects();
  }, [canvas]);

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
  
  // Persistable canvas snapshot for save/reload
  const getCanvasData = useCallback(() => {
    if (!canvas || isCanvasDestroyed(canvas)) return null;
    return canvas.toJSON() as Record<string, unknown>;
  }, [canvas]);

  const loadCanvasData = useCallback((data: Record<string, unknown>) => {
    if (!canvas || isCanvasDestroyed(canvas) || !data) return Promise.resolve();
    return canvas
      .loadFromJSON(data)
      .then(() => {
        if (!isCanvasDestroyed(canvas)) {
          canvas.renderAll();
        }
      })
      .catch(console.error);
  }, [canvas]);

  // Render AI-generated design onto the canvas
  const renderAIDesign = useCallback((aiResult: Record<string, unknown>) => {
    if (!canvas || isCanvasDestroyed(canvas)) {
      console.warn('Cannot render AI design: canvas not ready');
      return false;
    }

    const nested = aiResult.result as Record<string, unknown> | undefined;
    const normalized: Record<string, unknown> = {
      ...aiResult,
      components:
        (aiResult.components as unknown[]) ||
        (nested?.components as unknown[]) ||
        [],
    };

    const components = (normalized.components as unknown[]) || [];
    if (components.length === 0) {
      console.warn('No components to render from AI result');
      return false;
    }

    const renderer = rendererRef.current ?? new AdvancedCanvasRenderer(canvas);
    rendererRef.current = renderer;
    renderer.renderAIResult(normalized as Parameters<AdvancedCanvasRenderer['renderAIResult']>[0]);
    // Fit full artboard into the visible editor viewport
    requestAnimationFrame(() => {
      zoomToFit();
    });
    return true;
  }, [canvas, zoomToFit]);

  // Expose methods for external use
  useEffect(() => {
    if (canvas) {
      (window as unknown as { canvasEditor?: unknown }).canvasEditor = {
        canvas,
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
        getCanvasData,
        loadCanvasData,
        renderAIDesign,
        applyObjectProperty,
        getSelectedObjects,
      };
    }

    return () => {
      type WindowCanvasAPI = { zoomToFit?: () => void };
      const current = (window as unknown as { canvasEditor?: WindowCanvasAPI }).canvasEditor;
      if (current?.zoomToFit === zoomToFit) {
        delete (window as unknown as { canvasEditor?: WindowCanvasAPI }).canvasEditor;
      }
    };
  }, [canvas, addText, addRectangle, addCircle, addTriangle, addLine, addImage, deleteSelected, cloneSelected, bringToFront, sendToBack, groupSelected, ungroupSelected, zoomIn, zoomOut, zoomToFit, undo, redo, exportAsPNG, exportAsJPG, exportAsSVG, exportAsPDF, exportAsFigmaJSON, handleSave, getCanvasData, loadCanvasData, renderAIDesign, applyObjectProperty, getSelectedObjects]);

  return (
    <div className="canvas-editor" ref={scaleOuterRef}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export default CanvasEditor;

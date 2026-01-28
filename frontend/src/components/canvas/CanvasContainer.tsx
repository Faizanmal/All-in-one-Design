/**
 * Canvas Container Component
 * Renders the main design canvas with collaborative features
 */
'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { Canvas, IText, Rect, Circle, FabricObject } from 'fabric';
import { CollaborativeUser } from '@/hooks/useCollaborativeCanvas';

interface Project {
  id?: number;
  canvas_width?: number;
  canvas_height?: number;
  canvas_background?: string;
  design_data?: {
    elements?: unknown[];
    [k: string]: unknown;
  };
  [k: string]: unknown;
}

interface CanvasContainerProps {
  projectId: number;
  project: Project;
  isConnected: boolean;
  activeUsers: CollaborativeUser[];
  onElementUpdate: (elementId: string, updates: Record<string, unknown>, previousData: Record<string, unknown>) => void;
  onElementCreate: (elementData: Record<string, unknown>) => void;
  onElementDelete: (elementId: string, elementData: Record<string, unknown>) => void;
  onCursorMove: (x: number, y: number) => void;
  onSelectionChange: (selectedElements: string[]) => void;
}

export function CanvasContainer({
  project,
  isConnected,
  activeUsers,
  onElementUpdate,
  onElementCreate,
  onElementDelete,
  onCursorMove,
  onSelectionChange
}: CanvasContainerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<Canvas | null>(null);
  const [isReady, setIsReady] = useState(false);
  const cursorUpdateThrottle = useRef<NodeJS.Timeout | null>(null);

  // --- Helper callbacks (declare before effects) ---
  const loadDesignData = useCallback((canvas: Canvas, designData: unknown) => {
    const elements = (designData as { elements?: unknown[] })?.elements || [];
    elements.forEach((elem: unknown) => {
      let obj: unknown = null;
      const type = (elem as { type?: string })?.type;
      if (type === 'text') {
        obj = new IText((elem as { content?: string })?.content || '', {
          left: (elem as { position?: { x?: number } })?.position?.x || 0,
          top: (elem as { position?: { y?: number } })?.position?.y || 0,
          fontSize: (elem as { style?: { fontSize?: number } })?.style?.fontSize || 16,
          fill: (elem as { style?: { color?: string } })?.style?.color || '#000000',
          fontFamily: (elem as { style?: { fontFamily?: string } })?.style?.fontFamily || 'Arial'
        });
      } else if (type === 'rect' || type === 'rectangle') {
        obj = new Rect({
          left: (elem as { position?: { x?: number } })?.position?.x || 0,
          top: (elem as { position?: { y?: number } })?.position?.y || 0,
          width: (elem as { size?: { width?: number } })?.size?.width || 100,
          height: (elem as { size?: { height?: number } })?.size?.height || 100,
          fill: (elem as { style?: { backgroundColor?: string } })?.style?.backgroundColor || '#CCCCCC'
        });
      } else if (type === 'circle') {
        obj = new Circle({
          left: (elem as { position?: { x?: number } })?.position?.x || 0,
          top: (elem as { position?: { y?: number } })?.position?.y || 0,
          radius: ((elem as { size?: { width?: number } })?.size?.width || 100) / 2,
          fill: (elem as { style?: { backgroundColor?: string } })?.style?.backgroundColor || '#CCCCCC'
        });
      }

      if (obj) {
        (obj as FabricObject & { id?: string }).id = (elem as { id?: string })?.id || `elem-${Date.now()}`;
        canvas.add(obj as FabricObject);
      }
    });
    canvas.renderAll();
  }, []);

  const updateRemoteElement = useCallback((canvas: Canvas, elementId: string, updates: Record<string, unknown>) => {
    const obj = canvas.getObjects().find((o: FabricObject & { id?: string }) => o.id === elementId);
    if (!obj) return;
    obj.set(updates);
    canvas.renderAll();
  }, []);

  const createRemoteElement = useCallback((canvas: Canvas, elementData: unknown) => {
    let obj: unknown = null;
    if ((elementData as { type?: string })?.type === 'text') {
      obj = new IText((elementData as { content?: string })?.content || '', {
        left: (elementData as { left?: number })?.left || 0,
        top: (elementData as { top?: number })?.top || 0
      });
    } else if ((elementData as { type?: string })?.type === 'rect') {
      obj = new Rect({
        left: (elementData as { left?: number })?.left || 0,
        top: (elementData as { top?: number })?.top || 0,
        width: (elementData as { width?: number })?.width || 100,
        height: (elementData as { height?: number })?.height || 100
      });
    }
    if (obj) {
      (obj as FabricObject & { id?: string }).id = (elementData as { id?: string })?.id;
      canvas.add(obj as FabricObject);
      canvas.renderAll();
    }
  }, []);

  const deleteRemoteElement = useCallback((canvas: Canvas, elementId: string) => {
    const obj = canvas.getObjects().find((o: FabricObject & { id?: string }) => o.id === elementId);
    if (!obj) return;
    canvas.remove(obj);
    canvas.renderAll();
  }, []);

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (!canvasRef.current || fabricCanvasRef.current) return;

    const fabricGlobal = (window as unknown as { fabric?: { Canvas: new (el: HTMLCanvasElement, options?: Record<string, unknown>) => Canvas } }).fabric;
    if (!fabricGlobal) {
      console.warn('fabric.js is not available on window');
      return;
    }
    const canvas = new fabricGlobal.Canvas(canvasRef.current as HTMLCanvasElement, {
      width: (project.canvas_width as number) || 1920,
      height: (project.canvas_height as number) || 1080,
      backgroundColor: project.canvas_background || '#FFFFFF',
      selection: true,
      preserveObjectStacking: true
    });

    fabricCanvasRef.current = canvas;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsReady(true);

    // Load existing design data
    if (project.design_data?.elements) {
      loadDesignData(canvas, project.design_data);
    }

    return () => {
      canvas.dispose?.();
      fabricCanvasRef.current = null;
    };
  }, [project, loadDesignData]);

  // Handle canvas events
  useEffect(() => {
    if (!fabricCanvasRef.current || !isReady) return;

    const canvas = fabricCanvasRef.current;

    // Object modified
    const handleObjectModified = (e: unknown) => {
      const obj = (e as { target?: Record<string, unknown> }).target;
      if (!obj || !obj.id) return;

      const updates = {
        left: obj.left,
        top: obj.top,
        scaleX: obj.scaleX,
        scaleY: obj.scaleY,
        angle: obj.angle,
        // Add more properties as needed
      };

      onElementUpdate(obj.id as string, updates, {});
    };

    // Object added
    const handleObjectAdded = (e: unknown) => {
      const obj = (e as { target?: Record<string, unknown> }).target;
      if (!obj || obj.id) return; // Skip if already has ID (loaded from data)

      const id = `elem-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      obj.id = id;

      const elementData = {
        id,
        type: obj.type,
        left: obj.left,
        top: obj.top,
        width: obj.width,
        height: obj.height,
        scaleX: obj.scaleX,
        scaleY: obj.scaleY,
        angle: obj.angle,
        fill: obj.fill,
      };

      onElementCreate(elementData);
    };

    // Object removed
    const handleObjectRemoved = (e: unknown) => {
      const obj = (e as { target?: Record<string, unknown> }).target;
      if (!obj || !obj.id) return;

      onElementDelete(obj.id as string, {
        id: obj.id,
        type: obj.type
      });
    };

    // Selection changed
    const handleSelectionCreated = () => {
      const selection = canvas.getActiveObjects();
      const selectedIds = selection.map((obj: FabricObject & { id?: string }) => obj.id as string).filter(Boolean);
      onSelectionChange(selectedIds);
    };

    const handleSelectionUpdated = handleSelectionCreated;
    const handleSelectionCleared = () => onSelectionChange([]);

    // Mouse move for cursor tracking
    const handleMouseMove = (e: unknown) => {
      const pointer = (e as { pointer?: { x: number; y: number } }).pointer;
      if (!pointer) return;

      // Throttle cursor updates
      if (cursorUpdateThrottle.current) return;

      cursorUpdateThrottle.current = setTimeout(() => {
        cursorUpdateThrottle.current = null;
      }, 100);

      onCursorMove(pointer.x, pointer.y);
    };

    // Attach event listeners
    canvas.on('object:modified', handleObjectModified);
    canvas.on('object:added', handleObjectAdded);
    canvas.on('object:removed', handleObjectRemoved);
    canvas.on('selection:created', handleSelectionCreated);
    canvas.on('selection:updated', handleSelectionUpdated);
    canvas.on('selection:cleared', handleSelectionCleared);
    canvas.on('mouse:move', handleMouseMove);

    return () => {
      canvas.off('object:modified', handleObjectModified);
      canvas.off('object:added', handleObjectAdded);
      canvas.off('object:removed', handleObjectRemoved);
      canvas.off('selection:created', handleSelectionCreated);
      canvas.off('selection:updated', handleSelectionUpdated);
      canvas.off('selection:cleared', handleSelectionCleared);
      canvas.off('mouse:move', handleMouseMove);
    };
  }, [isReady, onElementUpdate, onElementCreate, onElementDelete, onCursorMove, onSelectionChange]);

  // Listen for remote updates
  useEffect(() => {
    const handleRemoteUpdate = (event: CustomEvent) => {
      const data = event.detail;
      if (!fabricCanvasRef.current) return;

      const canvas = fabricCanvasRef.current;

      switch (data.type) {
        case 'element_updated':
          updateRemoteElement(canvas, data.element_id, data.updates);
          break;
        case 'element_created':
          createRemoteElement(canvas, data.element_data);
          break;
        case 'element_deleted':
          deleteRemoteElement(canvas, data.element_id);
          break;
      }
    };

    window.addEventListener('canvas-update', handleRemoteUpdate as EventListener);
    return () => {
      window.removeEventListener('canvas-update', handleRemoteUpdate as EventListener);
    };
  }, [updateRemoteElement, createRemoteElement, deleteRemoteElement]);

  return (
    <div className="relative w-full h-full bg-gray-100 dark:bg-gray-900 flex items-center justify-center overflow-auto">
      {/* Connection Status Indicator */}
      {!isConnected && (
        <div className="absolute top-4 right-4 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 px-3 py-2 rounded-lg shadow-lg text-sm">
          Reconnecting...
        </div>
      )}

      {/* Canvas */}
      <div className="shadow-2xl">
        <canvas ref={canvasRef} />
      </div>

      {/* Remote Cursors */}
      {activeUsers.map((user) => (
        user.cursor_position && (
          <div
            key={user.user_id}
            className="absolute pointer-events-none"
            style={{
              left: user.cursor_position.x,
              top: user.cursor_position.y,
              transform: 'translate(-50%, -50%)'
            }}
          >
            <div className="relative">
              <svg width="20" height="20" viewBox="0 0 20 20" className="drop-shadow-lg">
                <path
                  d="M0 0L0 16L5 11L8 20L10 19L7 10L13 10L0 0Z"
                  fill={`hsl(${user.user_id * 137.5 % 360}, 70%, 50%)`}
                />
              </svg>
              <div className="absolute top-5 left-5 bg-white dark:bg-gray-800 px-2 py-1 rounded text-xs whitespace-nowrap shadow-lg">
                {user.username}
              </div>
            </div>
          </div>
        )
      ))}
    </div>
  );
}

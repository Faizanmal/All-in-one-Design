/**
 * Canvas Container Component
 * Renders the main design canvas with collaborative features
 */
'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { Canvas, FabricObject, Rect, Circle, FabricText as Text } from 'fabric';
import { CollaborativeUser } from '@/hooks/useCollaborativeCanvas';

interface CanvasContainerProps {
  projectId: number;
  project: any;
  isConnected: boolean;
  activeUsers: CollaborativeUser[];
  onElementUpdate: (elementId: string, updates: any, previousData: any) => void;
  onElementCreate: (elementData: any) => void;
  onElementDelete: (elementId: string, elementData: any) => void;
  onCursorMove: (x: number, y: number) => void;
  onSelectionChange: (selectedElements: string[]) => void;
}

export function CanvasContainer({
  projectId,
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

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (!canvasRef.current || fabricCanvasRef.current) return;

    const canvas = new Canvas(canvasRef.current, {
      width: project.canvas_width || 1920,
      height: project.canvas_height || 1080,
      backgroundColor: project.canvas_background || '#FFFFFF',
      selection: true,
      preserveObjectStacking: true
    });

    fabricCanvasRef.current = canvas;
    setIsReady(true);

    // Load existing design data
    if (project.design_data?.elements) {
      loadDesignData(canvas, project.design_data);
    }

    return () => {
      canvas.dispose();
      fabricCanvasRef.current = null;
    };
  }, [project]);

  // Handle canvas events
  useEffect(() => {
    if (!fabricCanvasRef.current || !isReady) return;

    const canvas = fabricCanvasRef.current;

    // Object modified
    const handleObjectModified = (e: any) => {
      const obj = e.target as any;
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
    const handleObjectAdded = (e: any) => {
      const obj = e.target as any;
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
    const handleObjectRemoved = (e: any) => {
      const obj = e.target as any;
      if (!obj || !obj.id) return;

      onElementDelete(obj.id as string, {
        id: obj.id,
        type: obj.type
      });
    };

    // Selection changed
    const handleSelectionCreated = (e: any) => {
      const selection = canvas.getActiveObjects();
      const selectedIds = selection.map((obj: any) => obj.id as string).filter(Boolean);
      onSelectionChange(selectedIds);
    };

    const handleSelectionUpdated = handleSelectionCreated;
    const handleSelectionCleared = () => onSelectionChange([]);

    // Mouse move for cursor tracking
    const handleMouseMove = (e: any) => {
      if (!e.pointer) return;

      // Throttle cursor updates
      if (cursorUpdateThrottle.current) return;

      cursorUpdateThrottle.current = setTimeout(() => {
        cursorUpdateThrottle.current = null;
      }, 100);

      onCursorMove(e.pointer.x, e.pointer.y);
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
  }, []);

  const loadDesignData = (canvas: Canvas, designData: any) => {
    const elements = designData.elements || [];
    
    elements.forEach((elem: any) => {
      let obj: any = null;

      switch (elem.type) {
        case 'text':
          obj = new Text(elem.content || '', {
            left: elem.position?.x || 0,
            top: elem.position?.y || 0,
            fontSize: elem.style?.fontSize || 16,
            fill: elem.style?.color || '#000000',
            fontFamily: elem.style?.fontFamily || 'Arial'
          });
          break;

        case 'rect':
        case 'rectangle':
          obj = new Rect({
            left: elem.position?.x || 0,
            top: elem.position?.y || 0,
            width: elem.size?.width || 100,
            height: elem.size?.height || 100,
            fill: elem.style?.backgroundColor || '#CCCCCC'
          });
          break;

        case 'circle':
          obj = new Circle({
            left: elem.position?.x || 0,
            top: elem.position?.y || 0,
            radius: (elem.size?.width || 100) / 2,
            fill: elem.style?.backgroundColor || '#CCCCCC'
          });
          break;
      }

      if (obj) {
        obj.id = elem.id || `elem-${Date.now()}`;
        canvas.add(obj);
      }
    });

    canvas.renderAll();
  };

  const updateRemoteElement = (canvas: Canvas, elementId: string, updates: any) => {
    const obj = canvas.getObjects().find((o: any) => o.id === elementId);
    if (!obj) return;

    obj.set(updates);
    canvas.renderAll();
  };

  const createRemoteElement = (canvas: Canvas, elementData: any) => {
    // Similar to loadDesignData but for single element
    let obj: any = null;

    if (elementData.type === 'text') {
      obj = new Text(elementData.content || '', {
        left: elementData.left || 0,
        top: elementData.top || 0
      });
    } else if (elementData.type === 'rect') {
      obj = new Rect({
        left: elementData.left || 0,
        top: elementData.top || 0,
        width: elementData.width || 100,
        height: elementData.height || 100
      });
    }

    if (obj) {
      obj.id = elementData.id;
      canvas.add(obj);
      canvas.renderAll();
    }
  };

  const deleteRemoteElement = (canvas: Canvas, elementId: string) => {
    const obj = canvas.getObjects().find((o: any) => o.id === elementId);
    if (!obj) return;

    canvas.remove(obj);
    canvas.renderAll();
  };

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

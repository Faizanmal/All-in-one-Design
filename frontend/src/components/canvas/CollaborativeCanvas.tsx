/**
 * Collaborative Canvas Component with User Presence
 */
'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas, ModifiedEvent, TPointerEvent, FabricObject } from 'fabric';
import { useCollaborativeCanvas } from '@/hooks/useCollaborativeCanvas';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Users, WifiOff, Wifi } from 'lucide-react';

type FabricObjectWithId = FabricObject & { id?: string | number };

export function CollaborativeCanvas({ projectId, token }: { projectId: number; token: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fabricCanvasRef = useRef<Canvas | null>(null);
  const [cursors, setCursors] = useState<Map<number, { x: number; y: number; username: string }>>(new Map());

  const {
    isConnected,
    activeUsers,
    sendCursorPosition,
    updateElement,
    updateSelection
  } = useCollaborativeCanvas(projectId, token);

  // Initialize Fabric.js canvas
  useEffect(() => {
    if (!canvasRef.current || fabricCanvasRef.current) return;

    const canvas = new Canvas(canvasRef.current, {
      width: 1920,
      height: 1080,
      backgroundColor: '#ffffff'
    });

    fabricCanvasRef.current = canvas;

    // Handle mouse move for cursor tracking
    canvas.on('mouse:move', (e) => {
      if (e.pointer) {
        sendCursorPosition(e.pointer.x, e.pointer.y);
      }
    });

    // Handle object modifications
    canvas.on('object:modified', (e: ModifiedEvent<TPointerEvent>) => {
      const obj = e.target;
      if (obj) {
        updateElement(
          String((obj as FabricObjectWithId).id ?? obj),
          {
            left: obj.left,
            top: obj.top,
            scaleX: obj.scaleX,
            scaleY: obj.scaleY,
            angle: obj.angle
          },
          {} // Previous data would come from undo/redo stack
        );
      }
    });

    // Handle selection
    type FabricSelectionEvent = Partial<ModifiedEvent<TPointerEvent>> & { selected?: Array<FabricObject | string>; deselected?: Array<FabricObject | string> };

    canvas.on('selection:created', (e: FabricSelectionEvent) => {
      const selectedIds = (e.selected ?? []).map((obj) => String((obj as FabricObjectWithId).id ?? obj));
      updateSelection(selectedIds);
    });

    canvas.on('selection:updated', (e: FabricSelectionEvent) => {
      const selectedIds = (e.selected ?? []).map((obj) => String((obj as FabricObjectWithId).id ?? obj));
      updateSelection(selectedIds);
    });

    canvas.on('selection:cleared', () => {
      updateSelection([]);
    });

    return () => {
      canvas.dispose();
    };
  }, [sendCursorPosition, updateElement, updateSelection]);

  // Listen for remote updates
  useEffect(() => {
    const handleCanvasUpdate = (event: CustomEvent) => {
      const data = event.detail;
      const canvas = fabricCanvasRef.current;
      if (!canvas) return;

      switch (data.type) {
        case 'element_updated':
          const obj = canvas.getObjects().find((o: FabricObjectWithId) => o.id === data.element_id);
          if (obj && data.updates) {
            obj.set(data.updates);
            canvas.renderAll();
          }
          break;

        case 'element_created':
          // Add new element to canvas
          if (data.element_data) {
            // Note: You'll need to reconstruct the object based on element_data
            // For now, just trigger a re-render
            canvas.renderAll();
          }
          break;

        case 'element_deleted':
          const toDelete = canvas.getObjects().find((o: FabricObjectWithId) => o.id === data.element_id);
          if (toDelete) {
            canvas.remove(toDelete);
            canvas.renderAll();
          }
          break;

        case 'cursor_update':
          setCursors(prev => {
            const updated = new Map(prev);
            if (data.position) {
              updated.set(data.user_id, {
                x: data.position.x,
                y: data.position.y,
                username: data.username
              });
            }
            return updated;
          });
          break;
      }
    };

    window.addEventListener('canvas-update', handleCanvasUpdate as EventListener);
    return () => window.removeEventListener('canvas-update', handleCanvasUpdate as EventListener);
  }, []);

  // Update cursor positions
  useEffect(() => {
    activeUsers.forEach(user => {
      if (user.cursor_position && user.user_id) {
        setCursors(prev => {
          const updated = new Map(prev);
          updated.set(user.user_id, {
            x: user.cursor_position!.x,
            y: user.cursor_position!.y,
            username: user.username
          });
          return updated;
        });
      }
    });
  }, [activeUsers]);

  const getUserColor = (userId: number) => {
    const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];
    return colors[userId % colors.length];
  };

  return (
    <div className="relative w-full h-full bg-gray-50 dark:bg-gray-900">
      {/* Top Toolbar */}
      <div className="absolute top-0 left-0 right-0 z-10 bg-white dark:bg-gray-800 border-b shadow-sm">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <Badge variant={isConnected ? "default" : "destructive"} className="gap-1">
              {isConnected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
              {isConnected ? 'Connected' : 'Disconnected'}
            </Badge>

            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-600" />
              <span className="text-sm font-medium">{activeUsers.length} online</span>
            </div>
          </div>

          {/* Active Users */}
          <div className="flex items-center gap-2">
            {activeUsers.slice(0, 5).map((user) => (
              <div key={user.user_id} className="relative">
                <Avatar className="w-8 h-8 border-2" style={{ borderColor: getUserColor(user.user_id) }}>
                  <AvatarFallback style={{ backgroundColor: getUserColor(user.user_id), color: 'white' }}>
                    {user.username.substring(0, 2).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
              </div>
            ))}
            {activeUsers.length > 5 && (
              <Badge variant="secondary">+{activeUsers.length - 5}</Badge>
            )}
          </div>
        </div>
      </div>

      {/* Canvas Container */}
      <div className="absolute inset-0 top-[60px] overflow-auto">
        <div className="relative inline-block" style={{ minWidth: '1920px', minHeight: '1080px' }}>
          <canvas ref={canvasRef} />

          {/* Remote Cursors */}
          {Array.from(cursors.entries()).map(([userId, cursor]) => (
            <div
              key={userId}
              className="absolute pointer-events-none transition-all duration-100"
              style={{
                left: `${cursor.x}px`,
                top: `${cursor.y}px`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M5 3L19 12L12 13L9 21L5 3Z"
                  fill={getUserColor(userId)}
                  stroke="white"
                  strokeWidth="1"
                />
              </svg>
              <div
                className="absolute left-6 top-0 px-2 py-1 rounded text-xs text-white font-medium whitespace-nowrap shadow-lg"
                style={{ backgroundColor: getUserColor(userId) }}
              >
                {cursor.username}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Connection Status Overlay */}
      {!isConnected && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="p-6 max-w-md">
            <div className="flex flex-col items-center gap-4">
              <WifiOff className="w-12 h-12 text-red-500" />
              <h3 className="text-lg font-semibold">Connection Lost</h3>
              <p className="text-sm text-gray-600 text-center">
                Attempting to reconnect to collaboration server...
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

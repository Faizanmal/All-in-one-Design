/**
 * Collaboration Cursors Component
 * Show real-time cursors of other users like Figma
 */
'use client';

import React, { useEffect, useState, useCallback } from 'react';
import type { FabricCanvas } from '@/types/fabric';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { motion, AnimatePresence } from 'framer-motion';

interface CollaboratorCursor {
  userId: number;
  username: string;
  color: string;
  x: number;
  y: number;
  avatar?: string;
  lastSeen: Date;
}

interface CollaborationCursorsProps {
  canvas?: FabricCanvas;
  projectId?: number;
  websocketUrl?: string;
}

const USER_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
  '#F8B195', '#F67280', '#C06C84', '#6C5B7B',
];

export function CollaborationCursors({ canvas, projectId, websocketUrl }: CollaborationCursorsProps) {
  const [cursors, setCursors] = useState<Map<number, CollaboratorCursor>>(new Map());
  const wsRef = useRef<WebSocket | null>(null);
  const [myUserId, setMyUserId] = useState<number | null>(null);
  const [myColor] = useState(() => USER_COLORS[Math.floor(Math.random() * USER_COLORS.length)]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((data: unknown) => {
    const d = data as any;
    switch (d.type) {
      case 'user_joined':
        // Add new collaborator
        break;
        
      case 'user_left':
        setCursors(prev => {
          const newCursors = new Map(prev);
          newCursors.delete(d.user_id);
          return newCursors;
        });
        break;
        
      case 'cursor_update':
        setCursors(prev => {
          const newCursors = new Map(prev);
          newCursors.set(d.user_id, {
            userId: d.user_id,
            username: d.username || 'Anonymous',
            color: d.color || USER_COLORS[d.user_id % USER_COLORS.length],
            x: d.x,
            y: d.y,
            avatar: d.avatar,
            lastSeen: new Date(),
          });
          return newCursors;
        });
        break;
        
      case 'init':
        setMyUserId(d.your_user_id);
        break;
    }
  }, []);

  // Connect to WebSocket
  useEffect(() => {
    if (!projectId || !websocketUrl) return;

    const token = localStorage.getItem('auth_token');
    const socket = new WebSocket(`${websocketUrl}?token=${token}&project=${projectId}`);

    socket.onopen = () => {
      console.log('Collaboration WebSocket connected');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('Collaboration WebSocket disconnected');
    };

    wsRef.current = socket;

    return () => {
      socket.close();
    };
  }, [projectId, websocketUrl]);

  // Send cursor position
  const sendCursorPosition = useCallback((x: number, y: number) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'cursor_update',
        x,
        y,
        color: myColor,
      }));
    }
  }, [myColor]);

  // Track mouse movement on canvas
  useEffect(() => {
    if (!canvas) return;

    let throttleTimeout: NodeJS.Timeout | null = null;

    const handleMouseMove = (e: unknown) => {
      if (throttleTimeout) return;

      const pointer = canvas.getPointer((e as any).e);
      sendCursorPosition(pointer.x, pointer.y);

      throttleTimeout = setTimeout(() => {
        throttleTimeout = null;
      }, 50); // Throttle to 20fps
    };

    canvas.on('mouse:move', handleMouseMove);

    return () => {
      canvas.off('mouse:move', handleMouseMove);
      if (throttleTimeout) clearTimeout(throttleTimeout);
    };
  }, [canvas, sendCursorPosition]);

  // Cleanup old cursors
  useEffect(() => {
    const interval = setInterval(() => {
      setCursors(prev => {
        const now = new Date();
        const newCursors = new Map(prev);
        
        for (const [userId, cursor] of newCursors) {
          const timeSinceLastSeen = now.getTime() - cursor.lastSeen.getTime();
          if (timeSinceLastSeen > 5000) { // 5 seconds
            newCursors.delete(userId);
          }
        }
        
        return newCursors;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none z-50">
      <AnimatePresence>
        {Array.from(cursors.values()).map((cursor) => (
          <motion.div
            key={cursor.userId}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.2 }}
            style={{
              position: 'absolute',
              left: cursor.x,
              top: cursor.y,
              transform: 'translate(-50%, -50%)',
            }}
            className="pointer-events-none"
          >
            {/* Cursor pointer */}
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              style={{
                filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))',
              }}
            >
              <path
                d="M5.5 3L19 10L11.5 12.5L9 20L5.5 3Z"
                fill={cursor.color}
                stroke="white"
                strokeWidth="1.5"
              />
            </svg>

            {/* User label */}
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                backgroundColor: cursor.color,
              }}
              className="absolute left-6 top-0 px-2 py-1 rounded-md text-white text-xs font-medium whitespace-nowrap shadow-lg"
            >
              {cursor.username}
            </motion.div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Collaborators list (top-right corner) */}
      {cursors.size > 0 && (
        <div className="absolute top-4 right-4 pointer-events-auto">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border rounded-lg shadow-lg p-2"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">
                {cursors.size} {cursors.size === 1 ? 'collaborator' : 'collaborators'}
              </span>
              <div className="flex -space-x-2">
                {Array.from(cursors.values()).slice(0, 5).map((cursor) => (
                  <Avatar
                    key={cursor.userId}
                    className="w-6 h-6 border-2 border-background"
                    style={{ borderColor: cursor.color }}
                  >
                    {cursor.avatar ? (
                      <AvatarImage src={cursor.avatar} alt={cursor.username} />
                    ) : (
                      <AvatarFallback style={{ backgroundColor: cursor.color }} className="text-white text-xs">
                        {cursor.username.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    )}
                  </Avatar>
                ))}
                {cursors.size > 5 && (
                  <Badge variant="secondary" className="ml-2 text-xs">
                    +{cursors.size - 5}
                  </Badge>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

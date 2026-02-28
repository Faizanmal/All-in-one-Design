/**
 * Collaborative Canvas Hook
 * Real-time collaboration for canvas editing
 */
import { useEffect, useRef, useState, useCallback } from 'react';

export interface CollaborativeUser {
  user_id: number;
  username: string;
  cursor_position?: { x: number; y: number };
  selected_elements?: string[];
}

export interface CanvasUpdate {
  type: 'element_updated' | 'element_created' | 'element_deleted' | 'cursor_update' | 'selection_changed' | 'active_users' | 'user_joined' | 'user_left';
  user_id?: number;
  username?: string;
  element_id?: string;
  element_data?: Record<string, unknown>;
  updates?: Record<string, unknown>;
  position?: { x: number; y: number };
  selected_elements?: string[];
  users?: CollaborativeUser[];
}

export function useCollaborativeCanvas(projectId: number, token: string) {
  const ws = useRef<WebSocket | null>(null);
  const [activeUsers, setActiveUsers] = useState<CollaborativeUser[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionAttempt, setConnectionAttempt] = useState(0);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const connectRef = useRef<(() => void) | null>(null);
  const maxReconnectAttempts = 10;

  const handleMessage = useCallback((data: CanvasUpdate) => {
    switch (data.type) {
      case 'active_users':
        setActiveUsers(data.users || []);
        break;
      
      case 'user_joined':
        setActiveUsers(prev => [
          ...prev,
          {
            user_id: data.user_id!,
            username: data.username!
          }
        ]);
        break;
      
      case 'user_left':
        setActiveUsers(prev => prev.filter(u => u.user_id !== data.user_id));
        break;
      
      case 'cursor_update':
        setActiveUsers(prev => prev.map(u => 
          u.user_id === data.user_id 
            ? { ...u, cursor_position: data.position }
            : u
        ));
        break;
      
      case 'element_updated':
      case 'element_created':
      case 'element_deleted':
      case 'selection_changed':
        // Emit custom event for canvas to handle
        window.dispatchEvent(new CustomEvent('canvas-update', { detail: data }));
        break;
    }
  }, []);

  const connect = useCallback(() => {
    if (!projectId || !token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/canvas/${projectId}/`;
    
    ws.current = new WebSocket(wsUrl);
    
    ws.current.onopen = () => {
      console.log('Connected to collaborative canvas');
      setIsConnected(true);
      setConnectionAttempt(0); // Reset on successful connection
      
      // Clear any reconnect timeout
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };
    
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data) as CanvasUpdate;
      handleMessage(data);
    };
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.current.onclose = () => {
      console.log('Disconnected from collaborative canvas');
      setIsConnected(false);
      
      // Exponential backoff reconnection (1s, 2s, 4s, 8s, ..., max 30s)
      setConnectionAttempt(prev => {
        const attempt = prev + 1;
        if (attempt <= maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, prev), 30000);
          console.log(`Reconnecting in ${delay / 1000}s (attempt ${attempt}/${maxReconnectAttempts})...`);
          reconnectTimeout.current = setTimeout(() => {
            if (connectRef.current) {
              connectRef.current();
            }
          }, delay);
        } else {
          console.warn('Max reconnection attempts reached. Please refresh the page.');
        }
        return attempt;
      });
    };
  }, [projectId, token, handleMessage]);

  // Store the connect function in ref for use in callbacks
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const sendCursorPosition = useCallback((x: number, y: number) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'cursor_move',
        position: { x, y }
      }));
    }
  }, []);

  const updateElement = useCallback((elementId: string, updates: Record<string, unknown>, previousData: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'element_update',
        element_id: elementId,
        updates,
        previous_data: previousData,
        timestamp: Date.now()
      }));
    }
  }, []);

  const createElement = useCallback((elementData: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'element_create',
        element_data: elementData,
        timestamp: Date.now()
      }));
    }
  }, []);

  const deleteElement = useCallback((elementId: string, elementData: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'element_delete',
        element_id: elementId,
        element_data: elementData,
        timestamp: Date.now()
      }));
    }
  }, []);

  const updateSelection = useCallback((selectedElements: string[]) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'selection_change',
        selected_elements: selectedElements
      }));
    }
  }, []);

  const updateViewport = useCallback((viewport: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'viewport_change',
        viewport
      }));
    }
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      ws.current?.close();
    };
  }, [connect, handleMessage]);

  // Ping to keep connection alive
  useEffect(() => {
    if (!isConnected) return;
    
    const pingInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000); // Ping every 30 seconds
    
    return () => clearInterval(pingInterval);
  }, [isConnected]);

  return {
    isConnected,
    activeUsers,
    sendCursorPosition,
    updateElement,
    createElement,
    deleteElement,
    updateSelection,
    updateViewport
  };
}

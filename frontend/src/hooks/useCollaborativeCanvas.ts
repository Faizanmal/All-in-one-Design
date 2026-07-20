/**
 * Collaborative Canvas Hook
 * Real-time collaboration for canvas editing
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { getAccessToken } from '@/lib/auth-token';
import { nextSyncTimestamp, shouldApplyRemoteSync } from '@/lib/collab-sync';

export interface CollaborativeUser {
  user_id: number;
  username: string;
  cursor_position?: { x: number; y: number };
  selected_elements?: string[];
}

export interface CanvasUpdate {
  type: 'element_updated' | 'element_created' | 'element_deleted' | 'cursor_update' | 'selection_changed' | 'active_users' | 'user_joined' | 'user_left' | 'design_synced' | 'pong';
  user_id?: number;
  username?: string;
  element_id?: string;
  element_data?: Record<string, unknown>;
  updates?: Record<string, unknown>;
  position?: { x: number; y: number };
  selected_elements?: string[];
  users?: CollaborativeUser[];
  design_data?: Record<string, unknown>;
  timestamp?: number;
}

function resolveWsBaseUrl(): string {
  if (typeof window === 'undefined') return '';
  const configured = process.env.NEXT_PUBLIC_WS_URL;
  if (configured) return configured.replace(/\/$/, '');

  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (apiUrl) {
    try {
      const url = new URL(apiUrl);
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${protocol}//${url.host}`;
    } catch {
      // fall through
    }
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return `${protocol}//localhost:8000`;
  }
  return `${protocol}//${window.location.host}`;
}

export function useCollaborativeCanvas(projectId: number | null, token?: string | null) {
  const ws = useRef<WebSocket | null>(null);
  const [activeUsers, setActiveUsers] = useState<CollaborativeUser[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [, setConnectionAttempt] = useState(0);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const connectRef = useRef<(() => void) | null>(null);
  const maxReconnectAttempts = 10;
  const applyingRemoteRef = useRef(false);
  const lastSentSyncRef = useRef(0);
  const lastAppliedSyncRef = useRef(0);

  const handleMessage = useCallback((data: CanvasUpdate) => {
    switch (data.type) {
      case 'active_users':
        setActiveUsers(data.users || []);
        break;

      case 'user_joined':
        setActiveUsers(prev => {
          if (prev.some(u => u.user_id === data.user_id)) return prev;
          return [
            ...prev,
            {
              user_id: data.user_id!,
              username: data.username!,
            },
          ];
        });
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

      case 'design_synced': {
        if (
          !shouldApplyRemoteSync(
            data.timestamp,
            lastAppliedSyncRef.current,
            lastSentSyncRef.current,
          )
        ) {
          return;
        }
        if (typeof data.timestamp === 'number') {
          lastAppliedSyncRef.current = data.timestamp;
        }
        window.dispatchEvent(new CustomEvent('canvas-update', { detail: data }));
        break;
      }

      case 'element_updated':
      case 'element_created':
      case 'element_deleted':
      case 'selection_changed':
        window.dispatchEvent(new CustomEvent('canvas-update', { detail: data }));
        break;
    }
  }, []);

  const connect = useCallback(() => {
    const authToken = token || getAccessToken();
    if (!projectId || !authToken) return;

    if (ws.current && (ws.current.readyState === WebSocket.OPEN || ws.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const wsUrl = `${resolveWsBaseUrl()}/ws/canvas/${projectId}/?token=${encodeURIComponent(authToken)}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      setConnectionAttempt(0);
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as CanvasUpdate;
        handleMessage(data);
      } catch (error) {
        console.error('Failed to parse collaboration message:', error);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      setConnectionAttempt(prev => {
        const attempt = prev + 1;
        if (attempt <= maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, prev), 30000);
          reconnectTimeout.current = setTimeout(() => {
            connectRef.current?.();
          }, delay);
        }
        return attempt;
      });
    };
  }, [projectId, token, handleMessage]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  const sendCursorPosition = useCallback((x: number, y: number) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'cursor_move',
        position: { x, y },
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
        timestamp: Date.now(),
      }));
    }
  }, []);

  const createElement = useCallback((elementData: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'element_create',
        element_data: elementData,
        timestamp: Date.now(),
      }));
    }
  }, []);

  const deleteElement = useCallback((elementId: string, elementData: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'element_delete',
        element_id: elementId,
        element_data: elementData,
        timestamp: Date.now(),
      }));
    }
  }, []);

  const updateSelection = useCallback((selectedElements: string[]) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'selection_change',
        selected_elements: selectedElements,
      }));
    }
  }, []);

  const updateViewport = useCallback((viewport: Record<string, unknown>) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'viewport_change',
        viewport,
      }));
    }
  }, []);

  const syncDesign = useCallback((designData: Record<string, unknown>) => {
    if (applyingRemoteRef.current) return;
    if (ws.current?.readyState === WebSocket.OPEN) {
      const timestamp = nextSyncTimestamp(lastSentSyncRef.current);
      lastSentSyncRef.current = timestamp;
      ws.current.send(JSON.stringify({
        action: 'design_sync',
        design_data: designData,
        timestamp,
      }));
    }
  }, []);

  const markApplyingRemote = useCallback((value: boolean) => {
    applyingRemoteRef.current = value;
  }, []);

  const recordAppliedSync = useCallback((timestamp?: number) => {
    if (typeof timestamp === 'number' && timestamp > lastAppliedSyncRef.current) {
      lastAppliedSyncRef.current = timestamp;
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      ws.current?.close();
      ws.current = null;
    };
  }, [connect]);

  useEffect(() => {
    if (!isConnected) return;

    const pingInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000);

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
    updateViewport,
    syncDesign,
    markApplyingRemote,
    recordAppliedSync,
  };
}

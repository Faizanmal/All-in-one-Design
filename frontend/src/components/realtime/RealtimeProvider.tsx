'use client';

import React, { 
  createContext, 
  useContext, 
  useEffect, 
  useState, 
  useCallback, 
  useRef,
  ReactNode 
} from 'react';
import Image from 'next/image';

// --- Types ---

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

interface CursorPosition {
  x: number;
  y: number;
}

interface Collaborator extends User {
  cursor?: CursorPosition;
  selection?: string[];
  color: string;
  isActive: boolean;
  lastSeen: Date;
}

interface CanvasOperation {
  type: 'add' | 'modify' | 'delete' | 'move' | 'resize' | 'style';
  objectId: string;
  data: Record<string, unknown>;
  userId: string;
  timestamp: number;
}

interface RawCollaborator {
  id: string;
  name: string;
  avatar?: string;
}

interface RawPresenceUser {
  id: string;
  is_active: boolean;
  last_seen?: string;
  [key: string]: unknown;
}

// Unified Canvas Message Interface
interface CanvasMessage {
  type: 'user_joined' | 'user_left' | 'cursor_update' | 'selection_change' | 'element_update' 
        | 'element_create' | 'element_delete' | 'canvas_operation' | 'object_locked' 
        | 'object_unlocked' | 'lock_denied' | 'sync_state';
  user?: User;
  user_id?: string;
  position?: CursorPosition;
  selected_elements?: string[];
  object_ids?: string[]; // Handle inconsistency between selection_change formats
  element_id?: string;
  updates?: Record<string, unknown>;
  element_data?: Record<string, unknown>;
  operation?: Record<string, unknown>; // The canvas operation payload
  object_id?: string;
  locked_by?: string;
  collaborators?: RawCollaborator[]; // Raw collaborator data from sync
  locked_objects?: Record<string, string>; // Raw lock data from sync
}

// Unified Presence Message Interface
interface PresenceMessage {
  type: 'online' | 'offline' | 'cursor_update' | 'selection_change' | 'presence_update' | 'heartbeat';
  user?: User;
  user_id?: string;
  users?: RawPresenceUser[]; // Raw user list from presence_update
  position?: CursorPosition;
  selected_elements?: string[];
  object_id?: string;
  last_seen?: string;
}

interface RealtimeContextValue {
  // Connection state
  isConnected: boolean;
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  error: string | null;
  
  // Collaborators
  collaborators: Map<string, Collaborator>;
  activeUsers: Collaborator[];
  
  // Operations
  sendCanvasOperation: (operation: Omit<CanvasOperation, 'userId' | 'timestamp'>) => void;
  sendCursorUpdate: (position: CursorPosition) => void;
  sendSelectionChange: (objectIds: string[]) => void;
  
  // Lock management
  lockObject: (objectId: string) => Promise<boolean>;
  unlockObject: (objectId: string) => void;
  lockedObjects: Map<string, string>; // objectId -> userId
  
  // Reconnection
  reconnect: () => void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

// Color palette for collaborator cursors
const COLLABORATOR_COLORS = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
];

function getCollaboratorColor(userId: string): string {
  const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return COLLABORATOR_COLORS[hash % COLLABORATOR_COLORS.length];
}

interface RealtimeProviderProps {
  children: ReactNode;
  projectId: string;
  user: User;
  wsBaseUrl?: string;
}

export function RealtimeProvider({ 
  children, 
  projectId, 
  user,
  wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
}: RealtimeProviderProps) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
  const [error, setError] = useState<string | null>(null);
  const [collaborators, setCollaborators] = useState<Map<string, Collaborator>>(new Map());
  const [lockedObjects, setLockedObjects] = useState<Map<string, string>>(new Map());
  
  const canvasWsRef = useRef<WebSocket | null>(null);
  const presenceWsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const cursorThrottleRef = useRef<NodeJS.Timeout | null>(null);
  const pendingCursorRef = useRef<CursorPosition | null>(null);
  const connectRef = useRef<(() => void) | null>(null);
  const mountedRef = useRef(true);
  const connectionStateRef = useRef<string>('disconnected');

  // --- Merged Handler for Canvas Messages ---
  const handleCanvasMessage = useCallback((message: CanvasMessage) => {
    switch (message.type) {
      case 'user_joined': {
        if (message.user) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            updated.set(message.user!.id, {
              ...message.user!,
              color: getCollaboratorColor(message.user!.id),
              isActive: true,
              lastSeen: new Date(),
            });
            return updated;
          });
        }
        break;
      }

      case 'user_left': {
        if (message.user_id) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            updated.delete(message.user_id!);
            return updated;
          });
        }
        break;
      }

      case 'cursor_update': {
        if (message.user_id && message.user_id !== user.id && message.position) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            const existing = updated.get(message.user_id!);
            if (existing) {
              updated.set(message.user_id!, {
                ...existing,
                cursor: message.position,
                lastSeen: new Date(),
              });
            }
            return updated;
          });
        }
        break;
      }

      case 'selection_change': {
        // Handle both formats of selection (selected_elements or object_ids)
        const selection = message.selected_elements || message.object_ids;
        if (message.user_id && message.user_id !== user.id && selection) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            const existing = updated.get(message.user_id!);
            if (existing) {
              updated.set(message.user_id!, {
                ...existing,
                selection: selection,
                lastSeen: new Date(),
              });
            }
            return updated;
          });
        }
        break;
      }

      case 'element_update':
      case 'element_create':
      case 'element_delete': {
        // Emit custom event for canvas to handle
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('canvas-update', { detail: message }));
        }
        break;
      }

      case 'canvas_operation': {
        if (typeof window !== 'undefined' && message.operation) {
          window.dispatchEvent(new CustomEvent('realtime-canvas-operation', {
            detail: message.operation,
          }));
        }
        break;
      }

      case 'object_locked': {
        if (message.object_id && message.user_id) {
          setLockedObjects(prev => {
            const updated = new Map(prev);
            updated.set(message.object_id!, message.user_id!);
            return updated;
          });
        }
        break;
      }

      case 'object_unlocked': {
        if (message.object_id) {
          setLockedObjects(prev => {
            const updated = new Map(prev);
            updated.delete(message.object_id!);
            return updated;
          });
        }
        break;
      }

      case 'lock_denied': {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('realtime-lock-denied', {
            detail: { objectId: message.object_id, lockedBy: message.locked_by },
          }));
        }
        break;
      }

      case 'sync_state': {
        // Full state sync on reconnect
        if (message.collaborators) {
          const collabMap = new Map();
          message.collaborators.forEach((c: RawCollaborator) => {
            collabMap.set(c.id, {
              ...c,
              color: getCollaboratorColor(c.id),
              isActive: true,
              lastSeen: new Date(),
            });
          });
          setCollaborators(collabMap);
        }
        if (message.locked_objects) {
          setLockedObjects(new Map(Object.entries(message.locked_objects)));
        }
        break;
      }
    }
  }, [user.id]);

  // --- Merged Handler for Presence Messages ---
  const handlePresenceMessage = useCallback((message: PresenceMessage) => {
    switch (message.type) {
      case 'presence_update': {
        if (Array.isArray(message.users)) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            message.users!.forEach((u: RawPresenceUser) => {
              if (u.id !== user.id) {
                updated.set(u.id, {
                  id: u.id,
                  name: (u as Record<string, unknown>).name as string || `User ${u.id}`,
                  email: (u as Record<string, unknown>).email as string || '',
                  color: getCollaboratorColor(u.id),
                  isActive: !!u.is_active,
                  lastSeen: u.last_seen ? new Date(u.last_seen) : new Date(),
                });
              }
            });
            return updated;
          });
        }
        break;
      }
      
      // Note: cursor/selection often sent via canvas socket, but handling here just in case
      case 'cursor_update': {
        if (message.user_id && message.user_id !== user.id && message.position) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            const existing = updated.get(message.user_id!);
            if (existing) {
              updated.set(message.user_id!, {
                ...existing,
                cursor: message.position,
                lastSeen: new Date(),
              });
            }
            return updated;
          });
        }
        break;
      }

      case 'selection_change': {
        if (message.user_id && message.user_id !== user.id && message.selected_elements) {
          setCollaborators(prev => {
            const updated = new Map(prev);
            const existing = updated.get(message.user_id!);
            if (existing) {
              updated.set(message.user_id!, {
                ...existing,
                selection: message.selected_elements,
                lastSeen: new Date(),
              });
            }
            return updated;
          });
        }
        break;
      }

      case 'online':
      case 'offline':
        // Optional: Handle individual online/offline if not covered by general sync
        break;
    }
  }, [user.id]);

  // Schedule reconnection - Define before connect so it can be called from within
  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    reconnectTimeoutRef.current = setTimeout(() => {
      console.log('[RealtimeProvider] Attempting reconnection...');
      setConnectionState('connecting');
      setError(null);
      // Use the connectRef to avoid circular dependency
      if (connectRef.current) {
        connectRef.current();
      }
    }, 3000);
  }, []);

  // Connect to WebSocket servers
  const connect = useCallback(() => {
    if (canvasWsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    // State is set by callers or via initial state to avoid
    // setting state synchronously inside effects.
    connectionStateRef.current = 'connecting';

    // Canvas WebSocket for operations
    const canvasWs = new WebSocket(`${wsBaseUrl}/ws/canvas/${projectId}/`);
    canvasWsRef.current = canvasWs;

    canvasWs.onopen = () => {
      console.log('[RealtimeProvider] Canvas WebSocket connected');
      setIsConnected(true);
      setConnectionState('connected');
      
      // Send join message
      canvasWs.send(JSON.stringify({
        type: 'join',
        user: {
          id: user.id,
          name: user.name,
          avatar: user.avatar,
        },
      }));
    };

    canvasWs.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleCanvasMessage(message);
      } catch (err) {
        console.error('[RealtimeProvider] Failed to parse message:', err);
      }
    };

    canvasWs.onerror = (event) => {
      console.error('[RealtimeProvider] Canvas WebSocket error:', event);
      setError('Connection error occurred');
      setConnectionState('error');
    };

    canvasWs.onclose = (event) => {
      console.log('[RealtimeProvider] Canvas WebSocket closed:', event.code, event.reason);
      setIsConnected(false);
      setConnectionState('disconnected');
      
      // Attempt reconnection after delay
      if (event.code !== 1000) {
        scheduleReconnect();
      }
    };

    // Presence WebSocket for user status
    const presenceWs = new WebSocket(`${wsBaseUrl}/ws/presence/${projectId}/`);
    presenceWsRef.current = presenceWs;

    presenceWs.onopen = () => {
      console.log('[RealtimeProvider] Presence WebSocket connected');
      presenceWs.send(JSON.stringify({
        type: 'online',
        user: {
          id: user.id,
          name: user.name,
          avatar: user.avatar,
        },
      }));
    };

    presenceWs.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handlePresenceMessage(message);
      } catch (err) {
        console.error('[RealtimeProvider] Failed to parse presence message:', err);
      }
    };

    presenceWs.onerror = console.error;
    presenceWs.onclose = () => console.log('[RealtimeProvider] Presence WebSocket closed');

  }, [projectId, user, wsBaseUrl, handleCanvasMessage, handlePresenceMessage, scheduleReconnect]);

  // Store connect in ref after definition
  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  // Manual reconnect
  const reconnect = useCallback(() => {
    canvasWsRef.current?.close();
    presenceWsRef.current?.close();
    setConnectionState('connecting');
    setError(null);
    connect();
  }, [connect]);

  // Send canvas operation
  const sendCanvasOperation = useCallback((operation: Omit<CanvasOperation, 'userId' | 'timestamp'>) => {
    if (canvasWsRef.current?.readyState === WebSocket.OPEN) {
      canvasWsRef.current.send(JSON.stringify({
        type: 'canvas_operation',
        operation: {
          ...operation,
          userId: user.id,
          timestamp: Date.now(),
        },
      }));
    }
  }, [user.id]);

  // Send cursor update (throttled)
  const sendCursorUpdate = useCallback((position: CursorPosition) => {
    pendingCursorRef.current = position;
    
    if (!cursorThrottleRef.current) {
      cursorThrottleRef.current = setTimeout(() => {
        if (pendingCursorRef.current && canvasWsRef.current?.readyState === WebSocket.OPEN) {
          canvasWsRef.current.send(JSON.stringify({
            type: 'cursor_update',
            position: pendingCursorRef.current,
          }));
        }
        cursorThrottleRef.current = null;
      }, 50); // Throttle to 20fps
    }
  }, []);

  // Send selection change
  const sendSelectionChange = useCallback((objectIds: string[]) => {
    if (canvasWsRef.current?.readyState === WebSocket.OPEN) {
      canvasWsRef.current.send(JSON.stringify({
        type: 'selection_change',
        object_ids: objectIds,
      }));
    }
  }, []);

  // Lock object
  const lockObject = useCallback((objectId: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (canvasWsRef.current?.readyState !== WebSocket.OPEN) {
        resolve(false);
        return;
      }

      // If already locked by us, return true
      if (lockedObjects.get(objectId) === user.id) {
        resolve(true);
        return;
      }

      // If locked by someone else, return false
      if (lockedObjects.has(objectId)) {
        resolve(false);
        return;
      }

      // Type safe event handler
      const handleLockResponse = (event: Event) => {
        const customEvent = event as CustomEvent;
        if (customEvent.detail.objectId === objectId) {
          window.removeEventListener('realtime-lock-denied', handleLockResponse);
          resolve(false);
        }
      };

      const handleLockSuccess = () => {
        const checkLock = () => {
          if (lockedObjects.get(objectId) === user.id) {
            resolve(true);
          } else {
            setTimeout(checkLock, 50);
          }
        };
        setTimeout(checkLock, 50);
      };

      window.addEventListener('realtime-lock-denied', handleLockResponse);
      
      canvasWsRef.current.send(JSON.stringify({
        type: 'lock_object',
        object_id: objectId,
      }));

      // Timeout after 2 seconds
      setTimeout(() => {
        window.removeEventListener('realtime-lock-denied', handleLockResponse);
        if (lockedObjects.get(objectId) === user.id) {
          resolve(true);
        } else {
          resolve(false);
        }
      }, 2000);

      handleLockSuccess();
    });
  }, [lockedObjects, user.id]);

  // Unlock object
  const unlockObject = useCallback((objectId: string) => {
    if (canvasWsRef.current?.readyState === WebSocket.OPEN) {
      canvasWsRef.current.send(JSON.stringify({
        type: 'unlock_object',
        object_id: objectId,
      }));
    }
  }, []);

  // Get active users (excluding self)
  const activeUsers = Array.from(collaborators.values()).filter(
    c => c.isActive && c.id !== user.id
  );

  // Connect on mount
  useEffect(() => {
    if (mountedRef.current) {
      mountedRef.current = false;
      // Defer connection and state updates to avoid
      // synchronous setState inside the effect body.
      const timer = setTimeout(() => {
        setConnectionState('connecting');
        setError(null);
        connect();
      }, 0);
      return () => clearTimeout(timer);
    }
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (cursorThrottleRef.current) {
        clearTimeout(cursorThrottleRef.current);
      }
      canvasWsRef.current?.close(1000);
      presenceWsRef.current?.close(1000);
    };
  }, [connect]);

  // Send heartbeat
  useEffect(() => {
    const heartbeat = setInterval(() => {
      if (presenceWsRef.current?.readyState === WebSocket.OPEN) {
        presenceWsRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);

    return () => clearInterval(heartbeat);
  }, []);

  const value: RealtimeContextValue = {
    isConnected,
    connectionState,
    error,
    collaborators,
    activeUsers,
    sendCanvasOperation,
    sendCursorUpdate,
    sendSelectionChange,
    lockObject,
    unlockObject,
    lockedObjects,
    reconnect,
  };

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

// Hook to use realtime context
export function useRealtime() {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
}

// Collaborator cursor display component
export function CollaboratorCursors() {
  const { activeUsers } = useRealtime();

  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      {activeUsers.map(collaborator => 
        collaborator.cursor && (
          <div
            key={collaborator.id}
            className="absolute transition-all duration-75 ease-out"
            style={{
              left: collaborator.cursor.x,
              top: collaborator.cursor.y,
              transform: 'translate(-2px, -2px)',
            }}
          >
            {/* Cursor arrow */}
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              style={{ color: collaborator.color }}
            >
              <path
                d="M5.65376 3.12501L20.4625 10.7927C21.1625 11.1727 21.1625 12.1727 20.4625 12.5527L14.8625 15.6927C14.6625 15.8027 14.5025 15.9627 14.3925 16.1627L11.2525 21.7627C10.8725 22.4627 9.87254 22.4627 9.49254 21.7627L2.09254 6.95377C1.67254 6.17377 2.43254 5.33377 3.25254 5.67377L5.65376 3.12501Z"
                fill="currentColor"
              />
            </svg>
            
            {/* Name label */}
            <div
              className="ml-4 px-2 py-1 rounded text-xs font-medium text-white whitespace-nowrap"
              style={{ backgroundColor: collaborator.color }}
            >
              {collaborator.name}
            </div>
          </div>
        )
      )}
    </div>
  );
}

// Connection status indicator
export function ConnectionStatus() {
  const { connectionState, error, reconnect } = useRealtime();

  if (connectionState === 'connected') {
    return null;
  }

  return (
    <div className={`
      fixed bottom-4 right-4 z-50 px-4 py-2 rounded-lg shadow-lg
      ${connectionState === 'connecting' ? 'bg-yellow-100 text-yellow-800' : ''}
      ${connectionState === 'disconnected' ? 'bg-gray-100 text-gray-800' : ''}
      ${connectionState === 'error' ? 'bg-red-100 text-red-800' : ''}
    `}>
      <div className="flex items-center gap-2">
        {connectionState === 'connecting' && (
          <>
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
            <span>Connecting...</span>
          </>
        )}
        {connectionState === 'disconnected' && (
          <>
            <div className="w-2 h-2 bg-gray-500 rounded-full" />
            <span>Disconnected</span>
            <button 
              onClick={reconnect}
              className="ml-2 text-sm underline hover:no-underline"
            >
              Reconnect
            </button>
          </>
        )}
        {connectionState === 'error' && (
          <>
            <div className="w-2 h-2 bg-red-500 rounded-full" />
            <span>{error || 'Connection error'}</span>
            <button 
              onClick={reconnect}
              className="ml-2 text-sm underline hover:no-underline"
            >
              Retry
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// Active collaborators list
export function ActiveCollaborators() {
  const { activeUsers, isConnected } = useRealtime();

  if (!isConnected || activeUsers.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-1">
      {activeUsers.slice(0, 5).map(user => (
        <div
          key={user.id}
          className="relative group"
          title={user.name}
        >
          {user.avatar ? (
            <Image
              src={user.avatar}
              alt={user.name}
              width={32}
              height={32}
              className="w-8 h-8 rounded-full border-2"
              style={{ borderColor: user.color }}
            />
          ) : (
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
              style={{ backgroundColor: user.color }}
            >
              {user.name.charAt(0).toUpperCase()}
            </div>
          )}
          <div 
            className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white"
            style={{ backgroundColor: user.isActive ? '#22C55E' : '#9CA3AF' }}
          />
        </div>
      ))}
      {activeUsers.length > 5 && (
        <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-sm font-medium text-gray-600">
          +{activeUsers.length - 5}
        </div>
      )}
    </div>
  );
}

export default RealtimeProvider;
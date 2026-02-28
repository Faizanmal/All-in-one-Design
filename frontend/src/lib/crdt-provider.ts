/**
 * CRDT Collaboration Provider
 *
 * Client-side CRDT engine that communicates with the Django
 * CRDTCollaborationConsumer via WebSocket. Provides automatic
 * conflict-free merging of concurrent edits using a Hybrid
 * Logical Clock (HLC) and LWW registers.
 */

// ─── Types ──────────────────────────────────────────────────────────

export interface CRDTClock {
  physical: number;
  logical: number;
  node_id: string;
}

export interface CRDTOperation {
  op_type: 'set' | 'delete' | 'add_element' | 'remove_element';
  element_id: string;
  prop: string;
  value: unknown;
  clock: CRDTClock;
  origin: string;
}

export interface CursorInfo {
  userId: number;
  username: string;
  position: { x: number; y: number };
}

export interface PresenceInfo {
  userId: number;
  username: string;
  status: 'idle' | 'editing' | 'away';
  color: string;
}

type EventHandler = (data: unknown) => void;

// ─── HLC (client-side) ──────────────────────────────────────────────

class HybridLogicalClock {
  physical = 0;
  logical = 0;
  nodeId: string;

  constructor(nodeId: string) {
    this.nodeId = nodeId;
  }

  tick(): CRDTClock {
    const now = Date.now();
    if (now > this.physical) {
      this.physical = now;
      this.logical = 0;
    } else {
      this.logical += 1;
    }
    return { physical: this.physical, logical: this.logical, node_id: this.nodeId };
  }

  merge(remote: CRDTClock): void {
    const now = Date.now();
    if (now > Math.max(this.physical, remote.physical)) {
      this.physical = now;
      this.logical = 0;
    } else if (this.physical === remote.physical) {
      this.logical = Math.max(this.logical, remote.logical) + 1;
    } else if (remote.physical > this.physical) {
      this.physical = remote.physical;
      this.logical = remote.logical + 1;
    } else {
      this.logical += 1;
    }
  }
}

// ─── CRDT Client ────────────────────────────────────────────────────

const CURSOR_COLORS = [
  '#6366f1', '#ec4899', '#f59e0b', '#10b981',
  '#3b82f6', '#8b5cf6', '#ef4444', '#14b8a6',
];

export class CRDTProvider {
  private ws: WebSocket | null = null;
  private clock: HybridLogicalClock;
  private sessionId: string;
  private projectId: string;
  private version = 0;
  private pendingOps: CRDTOperation[] = [];
  private handlers = new Map<string, Set<EventHandler>>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectDelay = 1000;
  private cursors = new Map<number, CursorInfo>();
  private peers = new Map<number, PresenceInfo>();
  private colorIndex = 0;

  constructor(projectId: string) {
    this.projectId = projectId;
    this.sessionId = crypto.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;
    this.clock = new HybridLogicalClock(this.sessionId);
  }

  // ─── Connection ───────────────────────────────────────────────────

  connect(wsUrl?: string): void {
    const url =
      wsUrl ??
      `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/project/${this.projectId}/crdt/`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.reconnectDelay = 1000;
      this.emit('connected', null);
      // Flush pending ops
      if (this.pendingOps.length > 0) {
        this.sendBatch(this.pendingOps);
        this.pendingOps = [];
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.handleMessage(msg);
      } catch {
        // ignore bad frames
      }
    };

    this.ws.onclose = () => {
      this.emit('disconnected', null);
      this.scheduleReconnect();
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
      this.connect();
    }, this.reconnectDelay);
  }

  // ─── Send helpers ──────────────────────────────────────────────────

  private send(data: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  private sendBatch(ops: CRDTOperation[]): void {
    this.send({
      action: 'crdt_batch',
      ops: ops.map((op) => ({
        ...op,
        clock: op.clock,
      })),
    });
  }

  // ─── Public API ────────────────────────────────────────────────────

  /**
   * Set a property on a canvas element.
   */
  setProperty(elementId: string, prop: string, value: unknown): void {
    const clock = this.clock.tick();
    const op: CRDTOperation = {
      op_type: 'set',
      element_id: elementId,
      prop,
      value,
      clock,
      origin: this.sessionId,
    };
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({ action: 'crdt_op', op });
    } else {
      this.pendingOps.push(op);
    }
    this.emit('local_op', op);
  }

  /**
   * Add a new element to the canvas.
   */
  addElement(elementId: string, initialProps: Record<string, unknown>): void {
    const clock = this.clock.tick();
    const op: CRDTOperation = {
      op_type: 'add_element',
      element_id: elementId,
      prop: '',
      value: initialProps,
      clock,
      origin: this.sessionId,
    };
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({ action: 'crdt_op', op });
    } else {
      this.pendingOps.push(op);
    }
    this.emit('local_op', op);
  }

  /**
   * Remove an element from the canvas.
   */
  removeElement(elementId: string): void {
    const clock = this.clock.tick();
    const op: CRDTOperation = {
      op_type: 'remove_element',
      element_id: elementId,
      prop: '',
      value: null,
      clock,
      origin: this.sessionId,
    };
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({ action: 'crdt_op', op });
    } else {
      this.pendingOps.push(op);
    }
    this.emit('local_op', op);
  }

  /**
   * Update cursor position for presence awareness.
   */
  moveCursor(x: number, y: number): void {
    this.send({ action: 'cursor_move', position: { x, y } });
  }

  /**
   * Request full snapshot from server.
   */
  requestSnapshot(): void {
    this.send({ action: 'snapshot_request' });
  }

  /**
   * Request ops since a specific version.
   */
  requestSync(sinceVersion?: number): void {
    this.send({ action: 'sync_request', since_version: sinceVersion ?? this.version });
  }

  /**
   * Get current cursors map.
   */
  getCursors(): Map<number, CursorInfo> {
    return new Map(this.cursors);
  }

  /**
   * Get current presence map.
   */
  getPeers(): Map<number, PresenceInfo> {
    return new Map(this.peers);
  }

  // ─── Incoming message handling ─────────────────────────────────────

  private handleMessage(msg: Record<string, unknown>): void {
    const type = msg.type as string;

    switch (type) {
      case 'crdt_ops': {
        const ops = msg.ops as CRDTOperation[];
        const origin = msg.origin as string;
        if (msg.version) this.version = msg.version as number;
        // Merge clocks
        ops.forEach((op) => {
          if (op.clock) this.clock.merge(op.clock);
        });
        this.emit('remote_ops', { ops, origin, version: this.version });
        break;
      }

      case 'snapshot':
        this.emit('snapshot', msg.data);
        break;

      case 'state_vector':
        if ((msg.data as Record<string, unknown>)?.version) {
          this.version = (msg.data as Record<string, unknown>).version as number;
        }
        this.emit('state_vector', msg.data);
        break;

      case 'cursor_update': {
        const cursor: CursorInfo = {
          userId: msg.user_id as number,
          username: msg.username as string,
          position: msg.position as { x: number; y: number },
        };
        this.cursors.set(cursor.userId, cursor);
        this.emit('cursor', cursor);
        break;
      }

      case 'user_joined': {
        const userId = msg.user_id as number;
        const peer: PresenceInfo = {
          userId,
          username: msg.username as string,
          status: 'idle',
          color: CURSOR_COLORS[this.colorIndex++ % CURSOR_COLORS.length],
        };
        this.peers.set(userId, peer);
        this.emit('peer_joined', peer);
        break;
      }

      case 'user_left': {
        const uid = msg.user_id as number;
        this.cursors.delete(uid);
        this.peers.delete(uid);
        this.emit('peer_left', { userId: uid, username: msg.username });
        break;
      }

      case 'presence_update': {
        const pId = msg.user_id as number;
        const existing = this.peers.get(pId);
        if (existing) {
          existing.status = msg.status as PresenceInfo['status'];
          this.peers.set(pId, existing);
        }
        this.emit('presence', { userId: pId, status: msg.status });
        break;
      }

      case 'pong':
        this.emit('pong', null);
        break;
    }
  }

  // ─── Event emitter ─────────────────────────────────────────────────

  on(event: string, handler: EventHandler): () => void {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }

  private emit(event: string, data: unknown): void {
    this.handlers.get(event)?.forEach((h) => h(data));
  }
}

// ─── React hook ──────────────────────────────────────────────────────

import { useEffect, useRef, useState, useCallback } from 'react';

export function useCRDT(projectId: string | null) {
  const providerRef = useRef<CRDTProvider | null>(null);
  const [connected, setConnected] = useState(false);
  const [peers, setPeers] = useState<PresenceInfo[]>([]);
  const [cursors, setCursors] = useState<CursorInfo[]>([]);

  useEffect(() => {
    if (!projectId) return;

    const provider = new CRDTProvider(projectId);
    providerRef.current = provider;

    provider.on('connected', () => setConnected(true));
    provider.on('disconnected', () => setConnected(false));
    provider.on('peer_joined', () => setPeers([...provider.getPeers().values()]));
    provider.on('peer_left', () => setPeers([...provider.getPeers().values()]));
    provider.on('cursor', () => setCursors([...provider.getCursors().values()]));

    provider.connect();

    return () => {
      provider.disconnect();
      providerRef.current = null;
    };
  }, [projectId]);

  const setProperty = useCallback(
    (elementId: string, prop: string, value: unknown) =>
      providerRef.current?.setProperty(elementId, prop, value),
    [],
  );

  const addElement = useCallback(
    (elementId: string, props: Record<string, unknown>) =>
      providerRef.current?.addElement(elementId, props),
    [],
  );

  const removeElement = useCallback(
    (elementId: string) => providerRef.current?.removeElement(elementId),
    [],
  );

  const moveCursor = useCallback(
    (x: number, y: number) => providerRef.current?.moveCursor(x, y),
    [],
  );

  return {
    provider: providerRef,
    connected,
    peers,
    cursors,
    setProperty,
    addElement,
    removeElement,
    moveCursor,
  };
}

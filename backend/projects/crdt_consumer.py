"""
CRDT-aware WebSocket consumer for conflict-free real-time collaboration.

Wraps the existing CollaborativeCanvasConsumer with CRDT operation
handling so that concurrent edits from multiple users are merged
automatically using LWW (Last-Writer-Wins) semantics and a Hybrid
Logical Clock.
"""

import json
import uuid
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .crdt_engine import (
    CRDTClock,
    CRDTOperation,
    CRDTDocumentStore,
)

logger = logging.getLogger(__name__)


class CRDTCollaborationConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer using CRDT operations for conflict-free editing.

    Protocol messages (client → server):
      { "action": "crdt_op",       "op": <CRDTOperation dict> }
      { "action": "crdt_batch",    "ops": [<CRDTOperation dict>, ...] }
      { "action": "sync_request",  "since_version": <int> }
      { "action": "snapshot_request" }
      { "action": "cursor_move",   "position": {x, y} }
      { "action": "presence_update", "status": "idle" | "editing" | "away" }
      { "action": "ping" }

    Protocol messages (server → client):
      { "type": "crdt_ops",      "ops": [...], "version": <int> }
      { "type": "snapshot",      "data": {...} }
      { "type": "state_vector",  "data": {...} }
      { "type": "cursor_update", ... }
      { "type": "user_joined",   ... }
      { "type": "user_left",     ... }
      { "type": "pong" }
    """

    async def connect(self):
        self.user = self.scope['user']
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room = f'crdt_{self.project_id}'
        self.session_id = str(uuid.uuid4())

        if self.user.is_anonymous:
            await self.close()
            return

        has_access = await self._check_access()
        if not has_access:
            await self.close()
            return

        # Join channel group
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

        # Get (or create) the CRDT document for this project
        self.doc = CRDTDocumentStore.get_or_create(self.project_id)

        # Initialise per-session HLC
        self.clock = CRDTClock(node_id=self.session_id)

        # Send current state to the newly connected client
        await self.send_json({
            'type': 'snapshot',
            'data': self.doc.snapshot(),
        })
        await self.send_json({
            'type': 'state_vector',
            'data': self.doc.state_vector(),
        })

        # Announce presence
        await self.channel_layer.group_send(self.room, {
            'type': 'presence.joined',
            'user_id': self.user.id,
            'username': self.user.username,
            'session_id': self.session_id,
        })

        logger.info(
            'CRDT session %s opened for project %s by %s',
            self.session_id, self.project_id, self.user.username,
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_send(self.room, {
            'type': 'presence.left',
            'user_id': self.user.id,
            'username': self.user.username,
            'session_id': self.session_id,
        })
        await self.channel_layer.group_discard(self.room, self.channel_name)

    # ------------------------------------------------------------------
    # Receive dispatcher
    # ------------------------------------------------------------------

    async def receive_json(self, content: dict, **kwargs):
        action = content.get('action', '')

        handlers = {
            'crdt_op': self._handle_crdt_op,
            'crdt_batch': self._handle_crdt_batch,
            'sync_request': self._handle_sync_request,
            'snapshot_request': self._handle_snapshot_request,
            'cursor_move': self._handle_cursor_move,
            'presence_update': self._handle_presence_update,
            'ping': self._handle_ping,
        }

        handler = handlers.get(action)
        if handler:
            await handler(content)

    # ------------------------------------------------------------------
    # CRDT handlers
    # ------------------------------------------------------------------

    async def _handle_crdt_op(self, content: dict):
        op_dict = content.get('op', {})
        op = CRDTOperation.from_dict(op_dict)
        op.origin = self.session_id

        # Merge clocks
        self.clock = self.clock.merge(op.clock)
        op.clock = self.clock.tick()

        changed = self.doc.apply(op)
        if changed:
            await self.channel_layer.group_send(self.room, {
                'type': 'crdt.broadcast',
                'ops': [op.to_dict()],
                'version': self.doc.version,
                'origin': self.session_id,
            })

    async def _handle_crdt_batch(self, content: dict):
        raw_ops = content.get('ops', [])
        ops = [CRDTOperation.from_dict(d) for d in raw_ops]
        for op in ops:
            op.origin = self.session_id
            self.clock = self.clock.merge(op.clock)
            op.clock = self.clock.tick()

        applied = self.doc.apply_batch(ops)
        if applied:
            await self.channel_layer.group_send(self.room, {
                'type': 'crdt.broadcast',
                'ops': [op.to_dict() for op in applied],
                'version': self.doc.version,
                'origin': self.session_id,
            })

    async def _handle_sync_request(self, content: dict):
        since = content.get('since_version', 0)
        ops = self.doc.ops_since(since)
        await self.send_json({
            'type': 'crdt_ops',
            'ops': ops,
            'version': self.doc.version,
        })

    async def _handle_snapshot_request(self, _content: dict):
        await self.send_json({
            'type': 'snapshot',
            'data': self.doc.snapshot(),
        })

    async def _handle_cursor_move(self, content: dict):
        await self.channel_layer.group_send(self.room, {
            'type': 'cursor.broadcast',
            'user_id': self.user.id,
            'username': self.user.username,
            'position': content.get('position', {}),
            'session_id': self.session_id,
        })

    async def _handle_presence_update(self, content: dict):
        await self.channel_layer.group_send(self.room, {
            'type': 'presence.update',
            'user_id': self.user.id,
            'username': self.user.username,
            'status': content.get('status', 'idle'),
            'session_id': self.session_id,
        })

    async def _handle_ping(self, _content: dict):
        await self.send_json({'type': 'pong'})

    # ------------------------------------------------------------------
    # Group message handlers (channel layer → WebSocket)
    # ------------------------------------------------------------------

    async def crdt_broadcast(self, event: dict):
        """Forward CRDT ops to all clients (including origin for ack)."""
        await self.send_json({
            'type': 'crdt_ops',
            'ops': event['ops'],
            'version': event['version'],
            'origin': event.get('origin', ''),
        })

    async def cursor_broadcast(self, event: dict):
        if event.get('session_id') != self.session_id:
            await self.send_json({
                'type': 'cursor_update',
                'user_id': event['user_id'],
                'username': event['username'],
                'position': event['position'],
            })

    async def presence_joined(self, event: dict):
        if event.get('session_id') != self.session_id:
            await self.send_json({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'username': event['username'],
            })

    async def presence_left(self, event: dict):
        await self.send_json({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
        })

    async def presence_update(self, event: dict):
        if event.get('session_id') != self.session_id:
            await self.send_json({
                'type': 'presence_update',
                'user_id': event['user_id'],
                'username': event['username'],
                'status': event['status'],
            })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @database_sync_to_async
    def _check_access(self) -> bool:
        from .models import Project
        return Project.objects.filter(
            id=self.project_id,
            user=self.user,
        ).exists()

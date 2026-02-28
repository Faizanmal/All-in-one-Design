"""
CRDT (Conflict-free Replicated Data Type) Engine

Provides Last-Writer-Wins Element Set (LWW-Element-Set) and
operation-based CRDT primitives for real-time collaborative editing
without operational conflicts.

Reference: https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type
"""

import time
import json
import hashlib
from typing import Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class CRDTClock:
    """Hybrid Logical Clock (HLC) – ensures causal ordering across peers."""

    physical: int = 0   # wall-clock milliseconds
    logical: int = 0    # counter for same-ms events
    node_id: str = ''   # unique per client session

    def tick(self) -> 'CRDTClock':
        now_ms = int(time.time() * 1000)
        if now_ms > self.physical:
            self.physical = now_ms
            self.logical = 0
        else:
            self.logical += 1
        return CRDTClock(self.physical, self.logical, self.node_id)

    def merge(self, remote: 'CRDTClock') -> 'CRDTClock':
        now_ms = int(time.time() * 1000)
        if now_ms > max(self.physical, remote.physical):
            self.physical = now_ms
            self.logical = 0
        elif self.physical == remote.physical:
            self.logical = max(self.logical, remote.logical) + 1
        elif remote.physical > self.physical:
            self.physical = remote.physical
            self.logical = remote.logical + 1
        else:
            self.logical += 1
        return CRDTClock(self.physical, self.logical, self.node_id)

    def to_tuple(self):
        return (self.physical, self.logical, self.node_id)

    def __gt__(self, other: 'CRDTClock'):
        if self.physical != other.physical:
            return self.physical > other.physical
        if self.logical != other.logical:
            return self.logical > other.logical
        return self.node_id > other.node_id  # deterministic tie-break

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> 'CRDTClock':
        return cls(d.get('physical', 0), d.get('logical', 0), d.get('node_id', ''))


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

@dataclass
class CRDTOperation:
    """An individual CRDT operation broadcast over the wire."""
    op_type: str          # 'set', 'delete', 'add_element', 'remove_element'
    element_id: str       # target canvas element ID
    prop: str             # property name (e.g. 'fill', 'x', 'width') — empty for element ops
    value: Any = None     # new value (None for deletes)
    clock: CRDTClock = field(default_factory=CRDTClock)  # HLC timestamp
    origin: str = ''      # session that produced this op

    def to_dict(self):
        d = asdict(self)
        d['clock'] = self.clock.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> 'CRDTOperation':
        clock = CRDTClock.from_dict(d.get('clock', {}))
        return cls(
            op_type=d.get('op_type', 'set'),
            element_id=d.get('element_id', ''),
            prop=d.get('prop', ''),
            value=d.get('value'),
            clock=clock,
            origin=d.get('origin', ''),
        )


# ---------------------------------------------------------------------------
# LWW Register
# ---------------------------------------------------------------------------

class LWWRegister:
    """Last-Writer-Wins register for a single property."""

    def __init__(self, value: Any = None, clock: Optional[CRDTClock] = None):
        self.value = value
        self.clock = clock or CRDTClock()

    def set(self, value: Any, clock: CRDTClock) -> bool:
        """Returns True if the incoming write wins."""
        if self.clock is None or clock > self.clock:
            self.value = value
            self.clock = clock
            return True
        return False

    def to_dict(self):
        return {'value': self.value, 'clock': self.clock.to_dict()}

    @classmethod
    def from_dict(cls, d: dict) -> 'LWWRegister':
        return cls(d.get('value'), CRDTClock.from_dict(d.get('clock', {})))


# ---------------------------------------------------------------------------
# LWW-Element-Map  (one per canvas element)
# ---------------------------------------------------------------------------

class LWWElementMap:
    """
    LWW-Element-Map: each element property is an independent LWW register.
    Supports add/remove semantics with bias toward add (add-wins on tie).
    """

    def __init__(self, element_id: str):
        self.element_id = element_id
        self.registers: dict[str, LWWRegister] = {}
        self.add_clock: Optional[CRDTClock] = None
        self.remove_clock: Optional[CRDTClock] = None

    @property
    def is_alive(self) -> bool:
        if self.add_clock is None:
            return False
        if self.remove_clock is None:
            return True
        return self.add_clock > self.remove_clock  # add bias

    def apply_op(self, op: CRDTOperation) -> bool:
        """Apply an operation, return True if state changed."""
        if op.op_type == 'add_element':
            if self.add_clock is None or op.clock > self.add_clock:
                self.add_clock = op.clock
                # If value carries initial props, set them
                if isinstance(op.value, dict):
                    for prop, val in op.value.items():
                        self._set_prop(prop, val, op.clock)
                return True
            return False

        if op.op_type == 'remove_element':
            if self.remove_clock is None or op.clock > self.remove_clock:
                self.remove_clock = op.clock
                return True
            return False

        if op.op_type == 'set':
            return self._set_prop(op.prop, op.value, op.clock)

        if op.op_type == 'delete':
            return self._set_prop(op.prop, None, op.clock)

        return False

    def _set_prop(self, prop: str, value: Any, clock: CRDTClock) -> bool:
        if prop not in self.registers:
            self.registers[prop] = LWWRegister()
        return self.registers[prop].set(value, clock)

    def snapshot(self) -> dict:
        """Return a plain dict of current property values."""
        return {k: reg.value for k, reg in self.registers.items() if reg.value is not None}

    def to_dict(self):
        return {
            'element_id': self.element_id,
            'is_alive': self.is_alive,
            'add_clock': self.add_clock.to_dict() if self.add_clock else None,
            'remove_clock': self.remove_clock.to_dict() if self.remove_clock else None,
            'registers': {k: v.to_dict() for k, v in self.registers.items()},
        }


# ---------------------------------------------------------------------------
# CRDT Document (the whole canvas state)
# ---------------------------------------------------------------------------

class CRDTDocument:
    """
    A full canvas CRDT document.  Holds an LWWElementMap for each canvas
    element and provides a high-level API for the WebSocket consumer.
    """

    def __init__(self, document_id: str):
        self.document_id = document_id
        self.elements: dict[str, LWWElementMap] = {}
        self.op_log: list[CRDTOperation] = []
        self.version: int = 0

    def apply(self, op: CRDTOperation) -> bool:
        """Apply a single operation coming from any peer."""
        eid = op.element_id

        # Ensure element exists
        if eid not in self.elements:
            self.elements[eid] = LWWElementMap(eid)

        changed = self.elements[eid].apply_op(op)
        if changed:
            self.op_log.append(op)
            self.version += 1
        return changed

    def apply_batch(self, ops: list[CRDTOperation]) -> list[CRDTOperation]:
        """Apply a batch; return only the ops that actually changed state."""
        applied = []
        for op in ops:
            if self.apply(op):
                applied.append(op)
        return applied

    def snapshot(self) -> dict:
        """Return the full document state as a plain dict."""
        return {
            'document_id': self.document_id,
            'version': self.version,
            'elements': {
                eid: elem.snapshot()
                for eid, elem in self.elements.items()
                if elem.is_alive
            },
        }

    def ops_since(self, since_version: int) -> list[dict]:
        """Return serialized ops since a given version."""
        return [op.to_dict() for op in self.op_log[since_version:]]

    def state_vector(self) -> dict:
        """Return a state vector for sync protocol."""
        return {
            'document_id': self.document_id,
            'version': self.version,
            'element_count': sum(1 for e in self.elements.values() if e.is_alive),
            'checksum': self._checksum(),
        }

    def _checksum(self) -> str:
        """Quick integrity checksum of live elements."""
        snap = json.dumps(self.snapshot(), sort_keys=True)
        return hashlib.md5(snap.encode()).hexdigest()[:12]

    def to_dict(self):
        return {
            'document_id': self.document_id,
            'version': self.version,
            'elements': {eid: elem.to_dict() for eid, elem in self.elements.items()},
        }


# ---------------------------------------------------------------------------
# Document Store (in-memory per server; backed by Redis in production)
# ---------------------------------------------------------------------------

class CRDTDocumentStore:
    """
    In-memory store keyed by project/document ID.
    In production you would persist the op-log to Redis or Postgres.
    """

    _docs: dict[str, CRDTDocument] = {}

    @classmethod
    def get_or_create(cls, document_id: str) -> CRDTDocument:
        if document_id not in cls._docs:
            cls._docs[document_id] = CRDTDocument(document_id)
        return cls._docs[document_id]

    @classmethod
    def remove(cls, document_id: str):
        cls._docs.pop(document_id, None)

    @classmethod
    def list_active(cls) -> list[str]:
        return list(cls._docs.keys())

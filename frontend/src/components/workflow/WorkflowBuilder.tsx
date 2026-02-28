'use client';

import React, { useState, useCallback, useEffect, useMemo } from 'react';

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface TriggerNode {
  id: string;
  type: 'trigger';
  triggerType: string;
  label: string;
  icon: string;
  x: number;
  y: number;
}

interface ActionNode {
  id: string;
  type: 'action';
  actionType: string;
  label: string;
  icon: string;
  category: string;
  x: number;
  y: number;
  config: Record<string, unknown>;
}

type Node = TriggerNode | ActionNode;

interface Edge {
  id: string;
  from: string;
  to: string;
  type: 'success' | 'failure';
}

interface WorkflowData {
  id?: string;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'paused' | 'disabled';
  nodes: Node[];
  edges: Edge[];
}

interface RunLogEntry {
  id: string;
  status: 'completed' | 'failed' | 'running' | 'pending';
  trigger: string;
  startedAt: string;
  durationMs: number | null;
  actionsRun: number;
}

/* ------------------------------------------------------------------ */
/* Constants                                                           */
/* ------------------------------------------------------------------ */

const TRIGGER_PALETTE = [
  { type: 'design_approved', label: 'Design Approved', icon: '✅' },
  { type: 'design_updated', label: 'Design Updated', icon: '✏️' },
  { type: 'comment_added', label: 'Comment Added', icon: '💬' },
  { type: 'brand_colors_changed', label: 'Brand Changed', icon: '🎨' },
  { type: 'schedule', label: 'Scheduled', icon: '⏰' },
  { type: 'webhook', label: 'Webhook', icon: '🔗' },
  { type: 'manual', label: 'Manual', icon: '▶️' },
  { type: 'project_created', label: 'Project Created', icon: '➕' },
  { type: 'export_completed', label: 'Export Done', icon: '📥' },
];

const ACTION_PALETTE = [
  { type: 'export_png', label: 'Export PNG', icon: '🖼️', category: 'export' },
  { type: 'export_pdf', label: 'Export PDF', icon: '📄', category: 'export' },
  { type: 'export_svg', label: 'Export SVG', icon: '📐', category: 'export' },
  { type: 'export_all_formats', label: 'Export All', icon: '📦', category: 'export' },
  { type: 'magic_resize', label: 'Magic Resize', icon: '🔄', category: 'export' },
  { type: 'publish_web', label: 'Publish Web', icon: '🌐', category: 'publish' },
  { type: 'schedule_social', label: 'Social Post', icon: '📅', category: 'publish' },
  { type: 'send_email', label: 'Send Email', icon: '📧', category: 'notify' },
  { type: 'send_slack', label: 'Slack', icon: '#️⃣', category: 'notify' },
  { type: 'notify_team', label: 'Notify Team', icon: '👥', category: 'notify' },
  { type: 'run_accessibility_check', label: 'A11y Check', icon: '♿', category: 'design' },
  { type: 'run_qa_check', label: 'QA Check', icon: '✔️', category: 'design' },
  { type: 'condition', label: 'Condition', icon: '🔀', category: 'logic' },
  { type: 'delay', label: 'Delay', icon: '⏳', category: 'logic' },
];

const TEMPLATES = [
  {
    id: 'auto_export_on_approval',
    name: 'Auto-Export on Approval',
    description: 'Export to all formats and notify team when approved',
    trigger: 'design_approved',
    actions: ['export_all_formats', 'notify_team', 'send_slack'],
  },
  {
    id: 'brand_color_sync',
    name: 'Brand Color Sync',
    description: 'Sync brand colors + run accessibility check on change',
    trigger: 'brand_colors_changed',
    actions: ['run_accessibility_check', 'notify_team'],
  },
  {
    id: 'social_media_pipeline',
    name: 'Social Media Pipeline',
    description: 'Resize for social platforms and schedule posts',
    trigger: 'design_approved',
    actions: ['magic_resize', 'schedule_social', 'send_email'],
  },
  {
    id: 'qa_on_save',
    name: 'QA on Every Save',
    description: 'QA + accessibility check on every design save',
    trigger: 'design_updated',
    actions: ['run_qa_check', 'run_accessibility_check'],
  },
];

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-700',
  active: 'bg-green-100 text-green-700',
  paused: 'bg-yellow-100 text-yellow-700',
  disabled: 'bg-red-100 text-red-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  running: 'bg-blue-100 text-blue-700',
  pending: 'bg-gray-100 text-gray-700',
};

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

const uid = () => crypto.randomUUID?.() ?? `${Date.now()}-${Math.random()}`;

function findPaletteItem(type: string) {
  return (
    TRIGGER_PALETTE.find((t) => t.type === type) ??
    ACTION_PALETTE.find((a) => a.type === type)
  );
}

/* ------------------------------------------------------------------ */
/* Sub-components                                                      */
/* ------------------------------------------------------------------ */

function NodeCard({
  node,
  selected,
  onSelect,
  onDelete,
}: {
  node: Node;
  selected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}) {
  const borderColor =
    node.type === 'trigger'
      ? selected
        ? 'border-purple-500 ring-2 ring-purple-300'
        : 'border-purple-300'
      : selected
        ? 'border-blue-500 ring-2 ring-blue-300'
        : 'border-blue-300';

  return (
    <div
      className={`absolute bg-white rounded-xl shadow-md border-2 ${borderColor} cursor-pointer transition-all hover:shadow-lg group`}
      style={{ left: node.x, top: node.y, width: 180, minHeight: 60 }}
      onClick={onSelect}
    >
      <div className="flex items-center gap-2 px-3 py-2">
        <span className="text-xl">{node.icon}</span>
        <div className="flex-1 min-w-0">
          <span className="text-xs font-medium text-gray-400 uppercase">
            {node.type}
          </span>
          <p className="text-sm font-semibold text-gray-800 truncate">
            {node.label}
          </p>
        </div>
      </div>
      <button
        className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full text-xs hidden group-hover:flex items-center justify-center"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        ×
      </button>
    </div>
  );
}

function EdgeLine({ from, to }: { from: Node; to: Node }) {
  const x1 = from.x + 180;
  const y1 = from.y + 30;
  const x2 = to.x;
  const y2 = to.y + 30;
  const mx = (x1 + x2) / 2;

  return (
    <svg className="absolute inset-0 pointer-events-none" style={{ overflow: 'visible' }}>
      <path
        d={`M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`}
        fill="none"
        stroke="#94a3b8"
        strokeWidth={2}
        markerEnd="url(#arrowhead)"
      />
      <defs>
        <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
          <polygon points="0 0, 8 3, 0 6" fill="#94a3b8" />
        </marker>
      </defs>
    </svg>
  );
}

function PalettePanel({
  onAdd,
  tab,
  setTab,
}: {
  onAdd: (type: string, kind: 'trigger' | 'action') => void;
  tab: string;
  setTab: (t: string) => void;
}) {
  const categories = useMemo(() => {
    const cats = new Map<string, typeof ACTION_PALETTE>();
    ACTION_PALETTE.forEach((a) => {
      if (!cats.has(a.category)) cats.set(a.category, []);
      cats.get(a.category)!.push(a);
    });
    return cats;
  }, []);

  return (
    <div className="w-60 bg-gray-50 border-r overflow-y-auto p-3">
      <h3 className="font-semibold text-sm mb-2">Add Nodes</h3>
      <div className="flex gap-1 mb-3">
        {['triggers', 'actions', 'templates'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-2 py-1 text-xs rounded-md capitalize ${
              tab === t ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 border'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'triggers' && (
        <div className="space-y-1">
          {TRIGGER_PALETTE.map((t) => (
            <button
              key={t.type}
              onClick={() => onAdd(t.type, 'trigger')}
              className="w-full flex items-center gap-2 px-3 py-2 bg-white border rounded-lg text-sm hover:bg-purple-50"
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      )}

      {tab === 'actions' &&
        Array.from(categories.entries()).map(([cat, items]) => (
          <div key={cat} className="mb-3">
            <p className="text-xs font-semibold text-gray-400 uppercase mb-1">{cat}</p>
            <div className="space-y-1">
              {items.map((a) => (
                <button
                  key={a.type}
                  onClick={() => onAdd(a.type, 'action')}
                  className="w-full flex items-center gap-2 px-3 py-2 bg-white border rounded-lg text-sm hover:bg-blue-50"
                >
                  <span>{a.icon}</span>
                  <span>{a.label}</span>
                </button>
              ))}
            </div>
          </div>
        ))}

      {tab === 'templates' && (
        <div className="space-y-2">
          {TEMPLATES.map((t) => (
            <button
              key={t.id}
              className="w-full text-left p-3 bg-white border rounded-lg hover:bg-indigo-50"
              onClick={() => onAdd(t.id, 'trigger')}  
            >
              <p className="text-sm font-semibold">{t.name}</p>
              <p className="text-xs text-gray-500 mt-0.5">{t.description}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function RunHistoryPanel({ runs }: { runs: RunLogEntry[] }) {
  if (runs.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8 text-sm">
        No runs yet. Execute a workflow to see history.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {runs.map((r) => (
        <div key={r.id} className="bg-white border rounded-lg p-3 text-sm">
          <div className="flex items-center justify-between">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_COLORS[r.status] || ''}`}>
              {r.status}
            </span>
            <span className="text-xs text-gray-400">
              {r.durationMs != null ? `${r.durationMs}ms` : '—'}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Trigger: {r.trigger} · {r.actionsRun} actions · {new Date(r.startedAt).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Main Component                                                      */
/* ------------------------------------------------------------------ */

export default function WorkflowBuilder() {
  const [workflow, setWorkflow] = useState<WorkflowData>({
    name: 'Untitled Workflow',
    description: '',
    status: 'draft',
    nodes: [],
    edges: [],
  });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [paletteTab, setPaletteTab] = useState('triggers');
  const [rightTab, setRightTab] = useState<'properties' | 'runs'>('properties');
  const [runs, setRuns] = useState<RunLogEntry[]>([]);
  const [connecting, setConnecting] = useState<string | null>(null);

  const selectedNode = workflow.nodes.find((n) => n.id === selectedNodeId) ?? null;

  /* --- Node operations --- */

  const addNode = useCallback(
    (type: string, kind: 'trigger' | 'action') => {
      const info = findPaletteItem(type);
      const x = 80 + workflow.nodes.length * 60;
      const y = 80 + workflow.nodes.length * 30;

      const node: Node =
        kind === 'trigger'
          ? {
              id: uid(),
              type: 'trigger',
              triggerType: type,
              label: info?.label ?? type,
              icon: info?.icon ?? '⚡',
              x,
              y,
            }
          : {
              id: uid(),
              type: 'action',
              actionType: type,
              label: info?.label ?? type,
              icon: info?.icon ?? '⚙️',
              category: (info as typeof ACTION_PALETTE[0])?.category ?? 'other',
              x,
              y,
              config: {},
            };

      setWorkflow((p) => ({ ...p, nodes: [...p.nodes, node] }));
      setSelectedNodeId(node.id);
    },
    [workflow.nodes],
  );

  const deleteNode = useCallback(
    (id: string) => {
      setWorkflow((p) => ({
        ...p,
        nodes: p.nodes.filter((n) => n.id !== id),
        edges: p.edges.filter((e) => e.from !== id && e.to !== id),
      }));
      if (selectedNodeId === id) setSelectedNodeId(null);
    },
    [selectedNodeId],
  );

  const handleNodeClick = useCallback(
    (id: string) => {
      if (connecting) {
        // Finish edge
        if (connecting !== id) {
          setWorkflow((p) => ({
            ...p,
            edges: [
              ...p.edges,
              { id: uid(), from: connecting, to: id, type: 'success' },
            ],
          }));
        }
        setConnecting(null);
      } else {
        setSelectedNodeId(id);
      }
    },
    [connecting],
  );

  /* --- Simulated run --- */
  const executeWorkflow = useCallback(() => {
    const run: RunLogEntry = {
      id: uid(),
      status: 'completed',
      trigger: workflow.nodes.find((n) => n.type === 'trigger')
        ? 'manual'
        : 'none',
      startedAt: new Date().toISOString(),
      durationMs: Math.floor(Math.random() * 2000) + 100,
      actionsRun: workflow.nodes.filter((n) => n.type === 'action').length,
    };
    setRuns((p) => [run, ...p]);
    setWorkflow((p) => ({ ...p, status: 'active' }));
  }, [workflow.nodes]);

  /* --- Node map for edges --- */
  const nodeMap = useMemo(() => {
    const m = new Map<string, Node>();
    workflow.nodes.forEach((n) => m.set(n.id, n));
    return m;
  }, [workflow.nodes]);

  /* ---------------------------------------------------------------- */
  /* Render                                                            */
  /* ---------------------------------------------------------------- */

  return (
    <div className="h-full flex flex-col bg-gray-100">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b">
        <div className="flex items-center gap-3">
          <input
            className="text-lg font-bold bg-transparent border-b border-transparent hover:border-gray-300 focus:border-indigo-500 outline-none px-1"
            value={workflow.name}
            onChange={(e) =>
              setWorkflow((p) => ({ ...p, name: e.target.value }))
            }
          />
          <span
            className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              STATUS_COLORS[workflow.status]
            }`}
          >
            {workflow.status}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">
            {workflow.nodes.length} nodes · {workflow.edges.length} edges
          </span>
          <button
            className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg"
            onClick={() =>
              setWorkflow((p) => ({
                ...p,
                status: p.status === 'active' ? 'paused' : 'active',
              }))
            }
          >
            {workflow.status === 'active' ? '⏸ Pause' : '▶ Activate'}
          </button>
          <button
            className="px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            onClick={executeWorkflow}
          >
            ⚡ Execute
          </button>
        </div>
      </div>

      {/* Main body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left palette */}
        <PalettePanel onAdd={addNode} tab={paletteTab} setTab={setPaletteTab} />

        {/* Canvas */}
        <div className="flex-1 relative overflow-auto bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9IiNlMmUyZTIiLz48L3N2Zz4=')]">
          {/* Edges */}
          {workflow.edges.map((edge) => {
            const from = nodeMap.get(edge.from);
            const to = nodeMap.get(edge.to);
            if (!from || !to) return null;
            return <EdgeLine key={edge.id} from={from} to={to} />;
          })}

          {/* Nodes */}
          {workflow.nodes.map((node) => (
            <NodeCard
              key={node.id}
              node={node}
              selected={selectedNodeId === node.id}
              onSelect={() => handleNodeClick(node.id)}
              onDelete={() => deleteNode(node.id)}
            />
          ))}

          {workflow.nodes.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center text-gray-400">
                <p className="text-4xl mb-3">🔧</p>
                <p className="text-lg font-medium">Build Your Workflow</p>
                <p className="text-sm mt-1">
                  Add a trigger from the left panel, then connect actions
                </p>
              </div>
            </div>
          )}

          {connecting && (
            <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-indigo-600 text-white px-4 py-2 rounded-full text-sm shadow-lg z-50">
              Click a target node to connect · Press Esc to cancel
            </div>
          )}
        </div>

        {/* Right panel */}
        <div className="w-72 bg-white border-l overflow-y-auto">
          <div className="flex border-b">
            {(['properties', 'runs'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setRightTab(t)}
                className={`flex-1 py-2 text-sm capitalize ${
                  rightTab === t
                    ? 'border-b-2 border-indigo-600 text-indigo-600 font-medium'
                    : 'text-gray-500'
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <div className="p-3">
            {rightTab === 'properties' && selectedNode ? (
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-medium text-gray-500">Label</label>
                  <input
                    className="w-full mt-1 px-2 py-1.5 border rounded-md text-sm"
                    value={selectedNode.label}
                    onChange={(e) => {
                      const val = e.target.value;
                      setWorkflow((p) => ({
                        ...p,
                        nodes: p.nodes.map((n) =>
                          n.id === selectedNode.id ? { ...n, label: val } : n,
                        ),
                      }));
                    }}
                  />
                </div>

                <div>
                  <label className="text-xs font-medium text-gray-500">Type</label>
                  <p className="text-sm font-mono bg-gray-50 px-2 py-1 rounded mt-1">
                    {selectedNode.type === 'trigger'
                      ? (selectedNode as TriggerNode).triggerType
                      : (selectedNode as ActionNode).actionType}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs font-medium text-gray-500">X</label>
                    <input
                      type="number"
                      className="w-full mt-1 px-2 py-1 border rounded-md text-sm"
                      value={selectedNode.x}
                      onChange={(e) => {
                        const v = Number(e.target.value);
                        setWorkflow((p) => ({
                          ...p,
                          nodes: p.nodes.map((n) =>
                            n.id === selectedNode.id ? { ...n, x: v } : n,
                          ),
                        }));
                      }}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500">Y</label>
                    <input
                      type="number"
                      className="w-full mt-1 px-2 py-1 border rounded-md text-sm"
                      value={selectedNode.y}
                      onChange={(e) => {
                        const v = Number(e.target.value);
                        setWorkflow((p) => ({
                          ...p,
                          nodes: p.nodes.map((n) =>
                            n.id === selectedNode.id ? { ...n, y: v } : n,
                          ),
                        }));
                      }}
                    />
                  </div>
                </div>

                <button
                  className="w-full px-3 py-1.5 text-sm border rounded-lg hover:bg-blue-50 text-blue-600 border-blue-300"
                  onClick={() => setConnecting(selectedNode.id)}
                >
                  🔗 Connect to…
                </button>

                <button
                  className="w-full px-3 py-1.5 text-sm border rounded-lg hover:bg-red-50 text-red-600 border-red-300"
                  onClick={() => deleteNode(selectedNode.id)}
                >
                  🗑 Delete Node
                </button>
              </div>
            ) : rightTab === 'properties' ? (
              <p className="text-sm text-gray-400 text-center mt-8">
                Select a node to edit its properties
              </p>
            ) : (
              <RunHistoryPanel runs={runs} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useCallback } from 'react';

// Types
interface BatchOperation {
  id: number;
  operation_type: string;
  status: string;
  component_count: number;
  success_count: number;
  error_count: number;
  created_at: string;
  completed_at?: string;
}

interface BatchOperationsToolbarProps {
  projectId: number;
  selectedComponentIds: number[];
  onOperationComplete?: () => void;
  onSelectionClear?: () => void;
}

// Batch Operations Toolbar Component
export function BatchOperationsToolbar({
  projectId,
  selectedComponentIds,
  onOperationComplete,
  onSelectionClear,
}: BatchOperationsToolbarProps) {
  const [loading, setLoading] = useState(false);
  const [operationHistory, setOperationHistory] = useState<BatchOperation[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showStylePanel, setShowStylePanel] = useState(false);
  const [styleUpdates, setStyleUpdates] = useState<Record<string, string>>({});
  const [showFindReplace, setShowFindReplace] = useState(false);

  const hasSelection = selectedComponentIds.length > 0;
  const multipleSelected = selectedComponentIds.length >= 2;

  // Fetch operation history
  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(
        `/api/v1/projects/batch-operations/history/?project_id=${projectId}`
      );
      const data = await response.json();
      setOperationHistory(data.history || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  }, [projectId]);

  useEffect(() => {
    if (showHistory) {
      fetchHistory();
    }
  }, [showHistory, fetchHistory]);

  // Execute batch operation
  const executeOperation = async (
    endpoint: string,
    payload: Record<string, unknown>
  ) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/projects/batch-operations/${endpoint}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponentIds,
          ...payload,
        }),
      });
      const data = await response.json();
      
      if (data.operation_id) {
        onOperationComplete?.();
      }
      
      return data;
    } catch (error) {
      console.error(`Failed to execute ${endpoint}:`, error);
    } finally {
      setLoading(false);
    }
  };

  // Align operations
  const align = (alignment: string) => {
    executeOperation('align', { alignment });
  };

  // Distribute operations
  const distribute = (direction: string) => {
    executeOperation('distribute', { direction });
  };

  // Delete selected
  const deleteSelected = async () => {
    if (!confirm(`Delete ${selectedComponentIds.length} components?`)) return;
    await executeOperation('delete', {});
    onSelectionClear?.();
  };

  // Duplicate selected
  const duplicateSelected = () => {
    executeOperation('duplicate', { offset_x: 20, offset_y: 20 });
  };

  // Apply style changes
  const applyStyle = () => {
    executeOperation('style', { style_updates: styleUpdates });
    setShowStylePanel(false);
    setStyleUpdates({});
  };

  // Change z-order
  const changeOrder = (action: string) => {
    executeOperation('change-order', { action });
  };

  // Undo operation
  const undoOperation = async (operationId: number) => {
    try {
      await fetch(`/api/v1/projects/batch-operations/${operationId}/undo/`, {
        method: 'POST',
      });
      onOperationComplete?.();
      fetchHistory();
    } catch (error) {
      console.error('Failed to undo:', error);
    }
  };

  if (!hasSelection) {
    return (
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-2 text-sm text-gray-500">
        Select components to enable batch operations
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-2">
      <div className="flex items-center gap-4 flex-wrap">
        {/* Selection info */}
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
          <span className="font-medium">{selectedComponentIds.length}</span>
          <span>selected</span>
          <button
            onClick={onSelectionClear}
            className="text-gray-400 hover:text-gray-600 ml-1"
          >
            ✕
          </button>
        </div>

        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />

        {/* Alignment buttons */}
        <div className="flex items-center gap-1">
          <span className="text-xs text-gray-500 mr-2">Align:</span>
          {[
            { key: 'left', icon: '⬅', title: 'Align Left' },
            { key: 'center', icon: '↔', title: 'Align Center' },
            { key: 'right', icon: '➡', title: 'Align Right' },
            { key: 'top', icon: '⬆', title: 'Align Top' },
            { key: 'middle', icon: '↕', title: 'Align Middle' },
            { key: 'bottom', icon: '⬇', title: 'Align Bottom' },
          ].map(({ key, icon, title }) => (
            <button
              key={key}
              onClick={() => align(key)}
              disabled={!multipleSelected || loading}
              title={title}
              className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {icon}
            </button>
          ))}
        </div>

        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />

        {/* Distribute buttons */}
        <div className="flex items-center gap-1">
          <span className="text-xs text-gray-500 mr-2">Distribute:</span>
          <button
            onClick={() => distribute('horizontal')}
            disabled={selectedComponentIds.length < 3 || loading}
            title="Distribute Horizontally"
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            ⋯
          </button>
          <button
            onClick={() => distribute('vertical')}
            disabled={selectedComponentIds.length < 3 || loading}
            title="Distribute Vertically"
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            ⋮
          </button>
        </div>

        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />

        {/* Z-order buttons */}
        <div className="flex items-center gap-1">
          <span className="text-xs text-gray-500 mr-2">Order:</span>
          {[
            { key: 'bring_front', icon: '⏫', title: 'Bring to Front' },
            { key: 'bring_forward', icon: '🔼', title: 'Bring Forward' },
            { key: 'send_backward', icon: '🔽', title: 'Send Backward' },
            { key: 'send_back', icon: '⏬', title: 'Send to Back' },
          ].map(({ key, icon, title }) => (
            <button
              key={key}
              onClick={() => changeOrder(key)}
              disabled={loading}
              title={title}
              className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-sm"
            >
              {icon}
            </button>
          ))}
        </div>

        <div className="h-6 w-px bg-gray-200 dark:bg-gray-700" />

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={duplicateSelected}
            disabled={loading}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Duplicate
          </button>
          
          <button
            onClick={() => setShowStylePanel(!showStylePanel)}
            disabled={loading}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Style
          </button>
          
          <button
            onClick={() => setShowFindReplace(!showFindReplace)}
            disabled={loading}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Find & Replace
          </button>

          <button
            onClick={deleteSelected}
            disabled={loading}
            className="px-3 py-1.5 text-sm bg-red-500 text-white rounded hover:bg-red-600 disabled:opacity-50"
          >
            Delete
          </button>
        </div>

        <div className="flex-1" />

        {/* History button */}
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
        >
          History
        </button>
      </div>

      {/* Style Panel */}
      {showStylePanel && (
        <div className="mt-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Apply Style to Selected
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Fill Color</label>
              <input
                type="color"
                value={styleUpdates.fill || '#000000'}
                onChange={(e) => setStyleUpdates({ ...styleUpdates, fill: e.target.value })}
                className="w-full h-8 rounded border border-gray-300"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Opacity</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={styleUpdates.opacity || 1}
                onChange={(e) => setStyleUpdates({ ...styleUpdates, opacity: e.target.value })}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Border Radius</label>
              <input
                type="number"
                placeholder="px"
                value={styleUpdates['style.borderRadius'] || ''}
                onChange={(e) =>
                  setStyleUpdates({ ...styleUpdates, 'style.borderRadius': e.target.value })
                }
                className="w-full p-2 text-sm border border-gray-300 rounded"
              />
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Stroke Width</label>
              <input
                type="number"
                placeholder="px"
                value={styleUpdates['style.strokeWidth'] || ''}
                onChange={(e) =>
                  setStyleUpdates({ ...styleUpdates, 'style.strokeWidth': e.target.value })
                }
                className="w-full p-2 text-sm border border-gray-300 rounded"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <button
              onClick={() => setShowStylePanel(false)}
              className="px-3 py-1.5 text-sm text-gray-600"
            >
              Cancel
            </button>
            <button
              onClick={applyStyle}
              className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Apply Style
            </button>
          </div>
        </div>
      )}

      {/* Find & Replace Panel */}
      {showFindReplace && <FindReplacePanel projectId={projectId} componentIds={selectedComponentIds} onComplete={onOperationComplete} onClose={() => setShowFindReplace(false)} />}

      {/* History Panel */}
      {showHistory && (
        <div className="mt-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg max-h-48 overflow-y-auto">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Operation History
          </h4>
          {operationHistory.length === 0 ? (
            <p className="text-sm text-gray-500">No operations yet</p>
          ) : (
            <div className="space-y-2">
              {operationHistory.map((op) => (
                <div
                  key={op.id}
                  className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded text-sm"
                >
                  <div>
                    <span className="font-medium">{op.operation_type}</span>
                    <span className="text-gray-500 ml-2">
                      ({op.success_count}/{op.component_count})
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {new Date(op.created_at).toLocaleTimeString()}
                    </span>
                    {op.status === 'completed' && (
                      <button
                        onClick={() => undoOperation(op.id)}
                        className="text-blue-600 hover:underline text-xs"
                      >
                        Undo
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white/50 dark:bg-gray-800/50 flex items-center justify-center">
          <svg className="animate-spin h-6 w-6 text-blue-500" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        </div>
      )}
    </div>
  );
}

// Find & Replace Panel
function FindReplacePanel({
  projectId,
  componentIds,
  onComplete,
  onClose,
}: {
  projectId: number;
  componentIds: number[];
  onComplete?: () => void;
  onClose: () => void;
}) {
  const [propertyPath, setPropertyPath] = useState('fill');
  const [findValue, setFindValue] = useState('');
  const [replaceValue, setReplaceValue] = useState('');
  const [useRegex, setUseRegex] = useState(false);

  const handleReplace = async () => {
    try {
      await fetch('/api/v1/projects/batch-operations/find-replace/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: componentIds,
          property_path: propertyPath,
          find_value: findValue,
          replace_value: replaceValue,
          use_regex: useRegex,
        }),
      });
      onComplete?.();
      onClose();
    } catch (error) {
      console.error('Find & replace failed:', error);
    }
  };

  return (
    <div className="mt-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
        Find & Replace Property Values
      </h4>
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <label className="text-xs text-gray-500 block mb-1">Property Path</label>
          <input
            type="text"
            value={propertyPath}
            onChange={(e) => setPropertyPath(e.target.value)}
            placeholder="e.g., fill, style.borderRadius"
            className="w-full p-2 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Find</label>
          <input
            type="text"
            value={findValue}
            onChange={(e) => setFindValue(e.target.value)}
            placeholder="Value to find"
            className="w-full p-2 text-sm border border-gray-300 rounded"
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Replace with</label>
          <input
            type="text"
            value={replaceValue}
            onChange={(e) => setReplaceValue(e.target.value)}
            placeholder="Replacement value"
            className="w-full p-2 text-sm border border-gray-300 rounded"
          />
        </div>
        <div className="col-span-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={useRegex}
              onChange={(e) => setUseRegex(e.target.checked)}
              className="rounded"
            />
            Use regular expression
          </label>
        </div>
      </div>
      <div className="flex justify-end gap-2 mt-4">
        <button onClick={onClose} className="px-3 py-1.5 text-sm text-gray-600">
          Cancel
        </button>
        <button
          onClick={handleReplace}
          className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Replace All
        </button>
      </div>
    </div>
  );
}

export default BatchOperationsToolbar;

'use client';

import React, { useState, useEffect } from 'react';

// Types
interface LayoutSuggestion {
  layout_type: string;
  confidence: number;
  properties: Record<string, any>;
  reasoning: string;
  preview?: any;
}

interface LayoutPreset {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
}

interface AutoLayoutPanelProps {
  projectId: number;
  selectedComponentIds: number[];
  onLayoutApplied?: () => void;
}

// Smart Auto-Layout Panel Component
export function AutoLayoutPanel({
  projectId,
  selectedComponentIds,
  onLayoutApplied,
}: AutoLayoutPanelProps) {
  const [suggestions, setSuggestions] = useState<LayoutSuggestion[]>([]);
  const [presets, setPresets] = useState<LayoutPreset[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'presets' | 'align'>('suggestions');
  const [gridSize, setGridSize] = useState(8);
  const [spacing, setSpacing] = useState(16);

  // Fetch layout presets
  useEffect(() => {
    fetch('/api/v1/ai/layout/presets/')
      .then((res) => res.json())
      .then((data) => setPresets(data.presets || []))
      .catch(console.error);
  }, []);

  // Analyze and get suggestions
  const analyzeLa = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/ai/layout/analyze/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponentIds.length > 0 ? selectedComponentIds : undefined,
          constraints: { padding: 16, gap: spacing },
          preferences: { style: 'modern', density: 'comfortable' },
        }),
      });
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setAnalysis(data.analysis);
    } catch (error) {
      console.error('Failed to analyze layout:', error);
    } finally {
      setLoading(false);
    }
  };

  // Apply a layout suggestion
  const applySuggestion = async (suggestion: LayoutSuggestion) => {
    if (!suggestion.preview?.positions) return;
    
    try {
      await fetch('/api/v1/ai/layout/apply/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          layout_type: suggestion.layout_type,
          layout_properties: suggestion.properties,
          positions: suggestion.preview.positions,
        }),
      });
      onLayoutApplied?.();
    } catch (error) {
      console.error('Failed to apply layout:', error);
    }
  };

  // Align components
  const alignComponents = async (alignment: string) => {
    if (selectedComponentIds.length < 2) return;
    
    try {
      await fetch('/api/v1/ai/layout/align/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponentIds,
          alignment,
          distribute: false,
        }),
      });
      onLayoutApplied?.();
    } catch (error) {
      console.error('Failed to align components:', error);
    }
  };

  // Distribute components
  const distributeComponents = async (direction: 'horizontal' | 'vertical') => {
    if (selectedComponentIds.length < 3) return;
    
    try {
      await fetch('/api/v1/ai/layout/auto-spacing/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponentIds,
          spacing,
          direction,
        }),
      });
      onLayoutApplied?.();
    } catch (error) {
      console.error('Failed to distribute components:', error);
    }
  };

  // Snap to grid
  const snapToGrid = async () => {
    try {
      await fetch('/api/v1/ai/layout/snap-to-grid/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          component_ids: selectedComponentIds.length > 0 ? selectedComponentIds : undefined,
          grid_size: gridSize,
        }),
      });
      onLayoutApplied?.();
    } catch (error) {
      console.error('Failed to snap to grid:', error);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
        Smart Auto-Layout
      </h2>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 mb-4">
        {(['suggestions', 'presets', 'align'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === tab
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Suggestions Tab */}
      {activeTab === 'suggestions' && (
        <div className="space-y-4">
          <button
            onClick={analyzeLa}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
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
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span>Analyze & Suggest</span>
              </>
            )}
          </button>

          {analysis && (
            <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm">
              <p className="text-gray-600 dark:text-gray-300">
                <strong>Analysis:</strong> {analysis.component_count} components,{' '}
                {analysis.suggested_layout_type} layout recommended
              </p>
            </div>
          )}

          {suggestions.length > 0 && (
            <div className="space-y-3">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 cursor-pointer transition-colors"
                  onClick={() => applySuggestion(suggestion)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 dark:text-white">
                      {suggestion.layout_type}
                    </span>
                    <span className="text-sm text-gray-500">
                      {Math.round(suggestion.confidence * 100)}% match
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {suggestion.reasoning}
                  </p>
                  <button className="mt-2 text-blue-600 text-sm hover:underline">
                    Apply this layout →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Presets Tab */}
      {activeTab === 'presets' && (
        <div className="grid grid-cols-2 gap-3">
          {presets.map((preset) => (
            <div
              key={preset.id}
              className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div className="aspect-video bg-gray-100 dark:bg-gray-700 rounded mb-2 flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </div>
              <h3 className="font-medium text-sm text-gray-900 dark:text-white">
                {preset.name}
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {preset.description}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Align Tab */}
      {activeTab === 'align' && (
        <div className="space-y-4">
          {/* Alignment buttons */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Align ({selectedComponentIds.length} selected)
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['left', 'center', 'right'].map((align) => (
                <button
                  key={align}
                  onClick={() => alignComponents(align)}
                  disabled={selectedComponentIds.length < 2}
                  className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-sm"
                >
                  {align.charAt(0).toUpperCase() + align.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Distribute buttons */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Distribute
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => distributeComponents('horizontal')}
                disabled={selectedComponentIds.length < 3}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-sm"
              >
                ↔ Horizontal
              </button>
              <button
                onClick={() => distributeComponents('vertical')}
                disabled={selectedComponentIds.length < 3}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 text-sm"
              >
                ↕ Vertical
              </button>
            </div>
          </div>

          {/* Spacing control */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Spacing: {spacing}px
            </label>
            <input
              type="range"
              min="0"
              max="64"
              step="4"
              value={spacing}
              onChange={(e) => setSpacing(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Grid snap */}
          <div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
              Grid Size: {gridSize}px
            </label>
            <div className="flex gap-2">
              <input
                type="range"
                min="4"
                max="32"
                step="4"
                value={gridSize}
                onChange={(e) => setGridSize(Number(e.target.value))}
                className="flex-1"
              />
              <button
                onClick={snapToGrid}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600 text-sm"
              >
                Snap to Grid
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AutoLayoutPanel;

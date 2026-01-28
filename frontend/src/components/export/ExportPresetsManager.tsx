'use client';

import React, { useState, useEffect } from 'react';

// Types
interface ExportPreset {
  id: number;
  name: string;
  description: string;
  format: string;
  scale: string;
  quality: number;
  width?: number;
  height?: number;
  is_default: boolean;
  include_background: boolean;
  optimize_for_web: boolean;
  file_naming_pattern: string;
}

interface ExportBundle {
  id: number;
  name: string;
  description: string;
  platform: string;
  preset_count: number;
  is_default: boolean;
}

interface ScheduledExport {
  id: number;
  name: string;
  schedule_type: string;
  status: string;
  next_run?: string;
  last_run?: string;
  run_count: number;
}

interface ExportHistory {
  id: number;
  status: string;
  format: string;
  component_count: number;
  file_count: number;
  total_size: number;
  duration_ms?: number;
  download_url?: string;
  created_at: string;
}

interface ExportPresetsManagerProps {
  projectId: number;
  selectedComponentIds?: number[];
  onExportComplete?: () => void;
}

// Format icons
const FORMAT_ICONS: Record<string, string> = {
  png: '🖼️',
  jpg: '📷',
  svg: '🔷',
  pdf: '📄',
  webp: '🌐',
  gif: '🎞️',
  ico: '🔳',
};

// Export Presets Manager Component
export function ExportPresetsManager({
  projectId,
  selectedComponentIds = [],
  onExportComplete,
}: ExportPresetsManagerProps) {
  const [presets, setPresets] = useState<ExportPreset[]>([]);
  const [bundles, setBundles] = useState<ExportBundle[]>([]);
  const [scheduledExports, setScheduledExports] = useState<ScheduledExport[]>([]);
  const [history, setHistory] = useState<ExportHistory[]>([]);
  const [defaultPresets, setDefaultPresets] = useState<Record<string, unknown>[]>([]);
  const [platformBundles, setPlatformBundles] = useState<Record<string, Record<string, unknown>>>({});
  
  const [activeTab, setActiveTab] = useState<'quick' | 'presets' | 'bundles' | 'scheduled' | 'history'>('quick');
  const [showCreatePreset, setShowCreatePreset] = useState(false);
  const [loading, setLoading] = useState(false);
  const [exportProgress, setExportProgress] = useState<{ status: string; progress: number } | null>(null);

  // Quick export settings
  const [quickFormat, setQuickFormat] = useState('png');
  const [quickScale, setQuickScale] = useState('1x');

  // Fetch data
  useEffect(() => {
    Promise.all([
      fetch('/api/v1/projects/export-presets/').then((r) => r.json()),
      fetch('/api/v1/projects/export-bundles/').then((r) => r.json()),
      fetch(`/api/v1/projects/scheduled-exports/?project_id=${projectId}`).then((r) => r.json()),
      fetch(`/api/v1/projects/export-history/?project_id=${projectId}`).then((r) => r.json()),
      fetch('/api/v1/projects/export/formats/').then((r) => r.json()),
    ])
      .then(([presetsData, bundlesData, scheduledData, historyData, formatsData]) => {
        setPresets(presetsData.presets || []);
        setBundles(bundlesData.bundles || []);
        setScheduledExports(scheduledData.scheduled_exports || []);
        setHistory(historyData.history || []);
        setDefaultPresets(formatsData.default_presets || []);
        setPlatformBundles(formatsData.platform_bundles || {});
      })
      .catch(console.error);
  }, [projectId]);

  // Quick export
  const quickExport = async () => {
    setLoading(true);
    setExportProgress({ status: 'Starting export...', progress: 0 });
    
    try {
      const response = await fetch('/api/v1/projects/export/quick/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          format: quickFormat,
          scale: quickScale,
          component_ids: selectedComponentIds.length > 0 ? selectedComponentIds : undefined,
        }),
      });
      if (!response.ok) throw new Error('Export failed');
      
      setExportProgress({ status: 'Export complete!', progress: 100 });
      
      setTimeout(() => {
        setExportProgress(null);
        onExportComplete?.();
      }, 1500);
      
      // Refresh history
      const historyResponse = await fetch(`/api/v1/projects/export-history/?project_id=${projectId}`);
      const historyData = await historyResponse.json();
      setHistory(historyData.history || []);
    } catch (error) {
      console.error('Export failed:', error);
      setExportProgress({ status: 'Export failed', progress: 0 });
    } finally {
      setLoading(false);
    }
  };

  // Export with preset
  const exportWithPreset = async (presetId: number) => {
    setLoading(true);
    try {
      await fetch('/api/v1/projects/export/with_preset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          preset_id: presetId,
          component_ids: selectedComponentIds.length > 0 ? selectedComponentIds : undefined,
        }),
      });
      onExportComplete?.();
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Export with bundle
  const exportWithBundle = async (bundleId: number) => {
    setLoading(true);
    try {
      await fetch('/api/v1/projects/export/with_bundle/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          bundle_id: bundleId,
          component_ids: selectedComponentIds.length > 0 ? selectedComponentIds : undefined,
        }),
      });
      onExportComplete?.();
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Create preset
  const createPreset = async (data: Partial<ExportPreset>) => {
    try {
      const response = await fetch('/api/v1/projects/export-presets/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const newPreset = await response.json();
      setPresets([...presets, newPreset]);
      setShowCreatePreset(false);
    } catch (error) {
      console.error('Failed to create preset:', error);
    }
  };

  // Delete preset
  const deletePreset = async (presetId: number) => {
    if (!confirm('Delete this preset?')) return;
    
    try {
      await fetch(`/api/v1/projects/export-presets/${presetId}/`, {
        method: 'DELETE',
      });
      setPresets(presets.filter((p) => p.id !== presetId));
    } catch (error) {
      console.error('Failed to delete preset:', error);
    }
  };

  // Format file size
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Export
        </h2>

        {/* Tabs */}
        <div className="flex gap-2 overflow-x-auto">
          {(['quick', 'presets', 'bundles', 'scheduled', 'history'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 text-sm rounded-lg whitespace-nowrap ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Quick Export Tab */}
        {activeTab === 'quick' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Format
                </label>
                <select
                  value={quickFormat}
                  onChange={(e) => setQuickFormat(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                >
                  {['png', 'jpg', 'svg', 'pdf', 'webp'].map((fmt) => (
                    <option key={fmt} value={fmt}>
                      {FORMAT_ICONS[fmt]} {fmt.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Scale
                </label>
                <select
                  value={quickScale}
                  onChange={(e) => setQuickScale(e.target.value)}
                  className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                >
                  {['0.5x', '1x', '1.5x', '2x', '3x', '4x'].map((scale) => (
                    <option key={scale} value={scale}>
                      {scale}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg text-sm">
              {selectedComponentIds.length > 0 ? (
                <span>{selectedComponentIds.length} components selected</span>
              ) : (
                <span>All components will be exported</span>
              )}
            </div>

            <button
              onClick={quickExport}
              disabled={loading}
              className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <span>Exporting...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Export Now</span>
                </>
              )}
            </button>

            {exportProgress && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
                <p className="text-sm text-blue-700 dark:text-blue-300">{exportProgress.status}</p>
                <div className="mt-2 h-2 bg-blue-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all"
                    style={{ width: `${exportProgress.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Quick presets */}
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Quick Presets
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {defaultPresets.slice(0, 4).map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setQuickFormat(preset.format as string);
                      setQuickScale(preset.scale as string);
                    }}
                    className="p-2 text-left border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 text-sm"
                  >
                    <div className="font-medium">{preset.name as React.ReactNode}</div>
                    <div className="text-xs text-gray-500">
                      {(preset.format as string).toUpperCase()} @ {preset.scale as React.ReactNode}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Presets Tab */}
        {activeTab === 'presets' && (
          <div className="space-y-4">
            <button
              onClick={() => setShowCreatePreset(true)}
              className="w-full py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500"
            >
              + Create New Preset
            </button>

            {presets.map((preset) => (
              <div
                key={preset.id}
                className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {preset.name}
                      </span>
                      {preset.is_default && (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 mt-1">{preset.description}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      <span>{FORMAT_ICONS[preset.format]} {preset.format.toUpperCase()}</span>
                      <span>@ {preset.scale}</span>
                      <span>Quality: {preset.quality}%</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => exportWithPreset(preset.id)}
                      disabled={loading}
                      className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      Export
                    </button>
                    <button
                      onClick={() => deletePreset(preset.id)}
                      className="px-2 py-1.5 text-red-500 hover:bg-red-50 rounded text-sm"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bundles Tab */}
        {activeTab === 'bundles' && (
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Platform Bundles
            </h3>
            <div className="grid gap-3">
              {Object.entries(platformBundles).map(([key, bundle]) => (
                <div
                  key={key}
                  className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900 dark:text-white">
                        {(bundle as Record<string, unknown>).name as React.ReactNode}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {(((bundle as Record<string, unknown>).presets as unknown[])?.length || 0)} export formats
                      </div>
                    </div>
                    <button
                      onClick={() => {/* Would need to create bundle first */}}
                      className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-sm rounded hover:bg-gray-200 dark:hover:bg-gray-600"
                    >
                      Use Bundle
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {bundles.length > 0 && (
              <>
                <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mt-6">
                  Your Bundles
                </h3>
                {bundles.map((bundle) => (
                  <div
                    key={bundle.id}
                    className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">{bundle.name}</div>
                        <div className="text-xs text-gray-500">
                          {bundle.preset_count} presets • {bundle.platform}
                        </div>
                      </div>
                      <button
                        onClick={() => exportWithBundle(bundle.id)}
                        disabled={loading}
                        className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                      >
                        Export All
                      </button>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        )}

        {/* Scheduled Tab */}
        {activeTab === 'scheduled' && (
          <div className="space-y-4">
            <button className="w-full py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500">
              + Schedule New Export
            </button>

            {scheduledExports.length === 0 ? (
              <p className="text-center text-gray-500 py-8">
                No scheduled exports yet
              </p>
            ) : (
              scheduledExports.map((scheduled) => (
                <div
                  key={scheduled.id}
                  className="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{scheduled.name}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {scheduled.schedule_type} • {scheduled.run_count} runs
                      </div>
                      {scheduled.next_run && (
                        <div className="text-xs text-gray-400 mt-1">
                          Next: {new Date(scheduled.next_run).toLocaleString()}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${
                          scheduled.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {scheduled.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-3">
            {history.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No export history yet</p>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  className="p-3 border border-gray-200 dark:border-gray-600 rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{FORMAT_ICONS[item.format]}</span>
                      <div>
                        <div className="text-sm font-medium">
                          {item.file_count} files • {formatSize(item.total_size)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(item.created_at).toLocaleString()}
                          {item.duration_ms && ` • ${item.duration_ms}ms`}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 text-xs rounded ${
                          item.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : item.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {item.status}
                      </span>
                      {item.download_url && (
                        <a
                          href={item.download_url}
                          className="text-blue-600 hover:underline text-sm"
                        >
                          Download
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Create Preset Modal */}
      {showCreatePreset && (
        <CreatePresetModal
          onClose={() => setShowCreatePreset(false)}
          onCreate={createPreset}
        />
      )}
    </div>
  );
}

// Create Preset Modal
function CreatePresetModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (data: Partial<ExportPreset>) => void;
}) {
  const [name, setName] = useState('');
  const [format, setFormat] = useState('png');
  const [scale, setScale] = useState('1x');
  const [quality, setQuality] = useState(90);
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate({ name, format, scale, quality, description });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Create Export Preset
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Web 2x Retina"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Format
              </label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                {['png', 'jpg', 'svg', 'pdf', 'webp'].map((f) => (
                  <option key={f} value={f}>
                    {f.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Scale
              </label>
              <select
                value={scale}
                onChange={(e) => setScale(e.target.value)}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                {['0.5x', '1x', '1.5x', '2x', '3x', '4x'].map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Quality: {quality}%
            </label>
            <input
              type="range"
              min="10"
              max="100"
              value={quality}
              onChange={(e) => setQuality(Number(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description..."
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              rows={2}
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Create Preset
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ExportPresetsManager;

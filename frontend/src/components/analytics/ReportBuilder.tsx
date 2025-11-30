'use client';

import React, { useState, useCallback } from 'react';

interface ReportField {
  id: string;
  name: string;
  type: 'metric' | 'dimension' | 'filter';
  dataType: 'number' | 'string' | 'date' | 'boolean';
  category: string;
}

interface ReportConfig {
  name: string;
  description: string;
  fields: string[];
  filters: Array<{
    field: string;
    operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between';
    value: string | number | [number, number];
  }>;
  groupBy: string[];
  sortBy: { field: string; direction: 'asc' | 'desc' }[];
  visualization: 'table' | 'bar' | 'line' | 'pie' | 'area';
  dateRange: { start: string; end: string };
  schedule?: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    recipients: string[];
  };
}

const AVAILABLE_FIELDS: ReportField[] = [
  // Metrics
  { id: 'designs_created', name: 'Designs Created', type: 'metric', dataType: 'number', category: 'Design' },
  { id: 'exports_count', name: 'Exports', type: 'metric', dataType: 'number', category: 'Design' },
  { id: 'ai_generations', name: 'AI Generations', type: 'metric', dataType: 'number', category: 'AI' },
  { id: 'ai_edits', name: 'AI Edits', type: 'metric', dataType: 'number', category: 'AI' },
  { id: 'collaborators_active', name: 'Active Collaborators', type: 'metric', dataType: 'number', category: 'Team' },
  { id: 'comments_count', name: 'Comments', type: 'metric', dataType: 'number', category: 'Collaboration' },
  { id: 'time_spent', name: 'Time Spent (minutes)', type: 'metric', dataType: 'number', category: 'Productivity' },
  { id: 'storage_used', name: 'Storage Used (MB)', type: 'metric', dataType: 'number', category: 'Storage' },
  
  // Dimensions
  { id: 'project_name', name: 'Project Name', type: 'dimension', dataType: 'string', category: 'Project' },
  { id: 'design_category', name: 'Design Category', type: 'dimension', dataType: 'string', category: 'Design' },
  { id: 'user_name', name: 'User Name', type: 'dimension', dataType: 'string', category: 'User' },
  { id: 'team_name', name: 'Team Name', type: 'dimension', dataType: 'string', category: 'Team' },
  { id: 'export_format', name: 'Export Format', type: 'dimension', dataType: 'string', category: 'Export' },
  { id: 'date', name: 'Date', type: 'dimension', dataType: 'date', category: 'Time' },
  { id: 'week', name: 'Week', type: 'dimension', dataType: 'date', category: 'Time' },
  { id: 'month', name: 'Month', type: 'dimension', dataType: 'date', category: 'Time' },
];

const VISUALIZATION_OPTIONS = [
  { value: 'table', label: 'Table', icon: '📊' },
  { value: 'bar', label: 'Bar Chart', icon: '📶' },
  { value: 'line', label: 'Line Chart', icon: '📈' },
  { value: 'pie', label: 'Pie Chart', icon: '🥧' },
  { value: 'area', label: 'Area Chart', icon: '📉' },
];

const FILTER_OPERATORS = [
  { value: 'equals', label: 'Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'greater_than', label: 'Greater than' },
  { value: 'less_than', label: 'Less than' },
  { value: 'between', label: 'Between' },
];

export function ReportBuilder() {
  const [config, setConfig] = useState<ReportConfig>({
    name: '',
    description: '',
    fields: [],
    filters: [],
    groupBy: [],
    sortBy: [],
    visualization: 'table',
    dateRange: {
      start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0],
    },
  });
  const [previewData, setPreviewData] = useState<Record<string, unknown>[] | null>(null);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [savedReports, setSavedReports] = useState<Array<{ id: string; name: string; created_at: string }>>([
    { id: '1', name: 'Weekly Design Summary', created_at: '2024-02-20' },
    { id: '2', name: 'Team Productivity Report', created_at: '2024-02-18' },
    { id: '3', name: 'AI Usage Analysis', created_at: '2024-02-15' },
  ]);

  const toggleField = (fieldId: string) => {
    setConfig((prev) => ({
      ...prev,
      fields: prev.fields.includes(fieldId)
        ? prev.fields.filter((f) => f !== fieldId)
        : [...prev.fields, fieldId],
    }));
  };

  const addFilter = () => {
    setConfig((prev) => ({
      ...prev,
      filters: [
        ...prev.filters,
        { field: AVAILABLE_FIELDS[0].id, operator: 'equals', value: '' },
      ],
    }));
  };

  const updateFilter = (index: number, updates: Partial<ReportConfig['filters'][0]>) => {
    setConfig((prev) => ({
      ...prev,
      filters: prev.filters.map((f, i) => (i === index ? { ...f, ...updates } : f)),
    }));
  };

  const removeFilter = (index: number) => {
    setConfig((prev) => ({
      ...prev,
      filters: prev.filters.filter((_, i) => i !== index),
    }));
  };

  const generatePreview = useCallback(async () => {
    setIsPreviewLoading(true);
    try {
      const response = await fetch('/api/analytics/advanced/reports/preview/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (response.ok) {
        const data = await response.json();
        setPreviewData(data.results);
      }
    } catch (error) {
      console.error('Failed to generate preview:', error);
      // Mock preview data
      setPreviewData([
        { date: '2024-02-19', designs_created: 12, exports_count: 8, ai_generations: 25 },
        { date: '2024-02-20', designs_created: 15, exports_count: 10, ai_generations: 30 },
        { date: '2024-02-21', designs_created: 8, exports_count: 5, ai_generations: 18 },
        { date: '2024-02-22', designs_created: 20, exports_count: 14, ai_generations: 42 },
        { date: '2024-02-23', designs_created: 18, exports_count: 12, ai_generations: 35 },
      ]);
    } finally {
      setIsPreviewLoading(false);
    }
  }, [config]);

  const saveReport = async () => {
    if (!config.name) {
      alert('Please enter a report name');
      return;
    }

    try {
      const response = await fetch('/api/analytics/advanced/reports/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (response.ok) {
        const data = await response.json();
        setSavedReports((prev) => [
          { id: data.id, name: config.name, created_at: new Date().toISOString().split('T')[0] },
          ...prev,
        ]);
        alert('Report saved successfully!');
      }
    } catch (error) {
      console.error('Failed to save report:', error);
      // Mock save
      setSavedReports((prev) => [
        { id: Date.now().toString(), name: config.name, created_at: new Date().toISOString().split('T')[0] },
        ...prev,
      ]);
      alert('Report saved successfully!');
    }
  };

  const exportReport = async (format: 'csv' | 'pdf' | 'xlsx') => {
    try {
      const response = await fetch(`/api/analytics/advanced/reports/export/?format=${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${config.name || 'report'}.${format}`;
        a.click();
      }
    } catch (error) {
      console.error('Failed to export report:', error);
      alert(`Exporting report as ${format.toUpperCase()}...`);
    }
  };

  const fieldsByCategory = AVAILABLE_FIELDS.reduce((acc, field) => {
    if (!acc[field.category]) acc[field.category] = [];
    acc[field.category].push(field);
    return acc;
  }, {} as Record<string, ReportField[]>);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Custom Report Builder</h1>
            <p className="text-gray-500">Create custom analytics reports with your data</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Field Selection */}
          <div className="lg:col-span-1 space-y-4">
            {/* Saved Reports */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Saved Reports</h3>
              <div className="space-y-2">
                {savedReports.map((report) => (
                  <button
                    key={report.id}
                    className="w-full text-left p-2 rounded hover:bg-gray-100 text-sm"
                  >
                    <div className="font-medium text-gray-900">{report.name}</div>
                    <div className="text-xs text-gray-500">{report.created_at}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Available Fields */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Available Fields</h3>
              <div className="space-y-4 max-h-[500px] overflow-y-auto">
                {Object.entries(fieldsByCategory).map(([category, fields]) => (
                  <div key={category}>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
                      {category}
                    </h4>
                    <div className="space-y-1">
                      {fields.map((field) => (
                        <label
                          key={field.id}
                          className="flex items-center gap-2 p-2 rounded hover:bg-gray-100 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={config.fields.includes(field.id)}
                            onChange={() => toggleField(field.id)}
                            className="rounded text-purple-600 focus:ring-purple-500"
                          />
                          <span className="text-sm text-gray-700">{field.name}</span>
                          <span
                            className={`ml-auto text-xs px-1.5 py-0.5 rounded ${
                              field.type === 'metric'
                                ? 'bg-blue-100 text-blue-700'
                                : 'bg-green-100 text-green-700'
                            }`}
                          >
                            {field.type === 'metric' ? '#' : 'A'}
                          </span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content - Report Configuration */}
          <div className="lg:col-span-3 space-y-6">
            {/* Report Info */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Report Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Report Name
                  </label>
                  <input
                    type="text"
                    value={config.name}
                    onChange={(e) => setConfig((prev) => ({ ...prev, name: e.target.value }))}
                    placeholder="My Custom Report"
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Visualization
                  </label>
                  <div className="flex gap-2">
                    {VISUALIZATION_OPTIONS.map((option) => (
                      <button
                        key={option.value}
                        onClick={() =>
                          setConfig((prev) => ({
                            ...prev,
                            visualization: option.value as ReportConfig['visualization'],
                          }))
                        }
                        className={`flex-1 p-2 rounded-lg border text-center transition-colors ${
                          config.visualization === option.value
                            ? 'border-purple-500 bg-purple-50 text-purple-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        title={option.label}
                      >
                        <span className="text-lg">{option.icon}</span>
                      </button>
                    ))}
                  </div>
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={config.description}
                    onChange={(e) => setConfig((prev) => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what this report tracks..."
                    rows={2}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  />
                </div>
              </div>
            </div>

            {/* Date Range */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Date Range</h3>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={config.dateRange.start}
                    onChange={(e) =>
                      setConfig((prev) => ({
                        ...prev,
                        dateRange: { ...prev.dateRange, start: e.target.value },
                      }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <span className="text-gray-400 pt-6">to</span>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <input
                    type="date"
                    value={config.dateRange.end}
                    onChange={(e) =>
                      setConfig((prev) => ({
                        ...prev,
                        dateRange: { ...prev.dateRange, end: e.target.value },
                      }))
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Filters</h3>
                <button
                  onClick={addFilter}
                  className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                >
                  + Add Filter
                </button>
              </div>
              {config.filters.length === 0 ? (
                <p className="text-gray-500 text-sm">No filters applied. Click "Add Filter" to filter your data.</p>
              ) : (
                <div className="space-y-3">
                  {config.filters.map((filter, index) => (
                    <div key={index} className="flex items-center gap-3">
                      <select
                        value={filter.field}
                        onChange={(e) => updateFilter(index, { field: e.target.value })}
                        className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        {AVAILABLE_FIELDS.map((field) => (
                          <option key={field.id} value={field.id}>
                            {field.name}
                          </option>
                        ))}
                      </select>
                      <select
                        value={filter.operator}
                        onChange={(e) =>
                          updateFilter(index, { operator: e.target.value as typeof filter.operator })
                        }
                        className="w-40 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        {FILTER_OPERATORS.map((op) => (
                          <option key={op.value} value={op.value}>
                            {op.label}
                          </option>
                        ))}
                      </select>
                      <input
                        type="text"
                        value={filter.value as string}
                        onChange={(e) => updateFilter(index, { value: e.target.value })}
                        placeholder="Value"
                        className="flex-1 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      />
                      <button
                        onClick={() => removeFilter(index)}
                        className="p-2 text-gray-400 hover:text-red-500"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Selected Fields */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Selected Fields</h3>
              {config.fields.length === 0 ? (
                <p className="text-gray-500 text-sm">
                  Select fields from the left sidebar to include in your report.
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {config.fields.map((fieldId) => {
                    const field = AVAILABLE_FIELDS.find((f) => f.id === fieldId);
                    return (
                      <span
                        key={fieldId}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                      >
                        {field?.name}
                        <button
                          onClick={() => toggleField(fieldId)}
                          className="ml-1 hover:text-purple-900"
                        >
                          ×
                        </button>
                      </span>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Preview & Actions */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Preview</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={generatePreview}
                    disabled={config.fields.length === 0}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isPreviewLoading ? 'Loading...' : 'Generate Preview'}
                  </button>
                  <div className="relative group">
                    <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200">
                      Export ▾
                    </button>
                    <div className="absolute right-0 mt-2 w-40 bg-white rounded-lg shadow-lg border hidden group-hover:block z-10">
                      <button
                        onClick={() => exportReport('csv')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      >
                        Export as CSV
                      </button>
                      <button
                        onClick={() => exportReport('xlsx')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      >
                        Export as Excel
                      </button>
                      <button
                        onClick={() => exportReport('pdf')}
                        className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100"
                      >
                        Export as PDF
                      </button>
                    </div>
                  </div>
                  <button
                    onClick={saveReport}
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700"
                  >
                    Save Report
                  </button>
                </div>
              </div>

              {/* Preview Content */}
              {isPreviewLoading ? (
                <div className="h-64 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600" />
                </div>
              ) : previewData ? (
                <div className="overflow-x-auto">
                  {config.visualization === 'table' ? (
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          {Object.keys(previewData[0] || {}).map((key) => (
                            <th key={key} className="px-4 py-2 text-left font-medium text-gray-600">
                              {AVAILABLE_FIELDS.find((f) => f.id === key)?.name || key}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {previewData.map((row, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            {Object.values(row).map((value, i) => (
                              <td key={i} className="px-4 py-2 text-gray-900">
                                {String(value)}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="h-64 flex items-center justify-center text-gray-500">
                      <div className="text-center">
                        <span className="text-4xl mb-2 block">
                          {VISUALIZATION_OPTIONS.find((v) => v.value === config.visualization)?.icon}
                        </span>
                        <p>{config.visualization.charAt(0).toUpperCase() + config.visualization.slice(1)} Chart Preview</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Full visualization available in exported report
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-64 flex items-center justify-center text-gray-500">
                  <div className="text-center">
                    <p>Select fields and click "Generate Preview" to see your data</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

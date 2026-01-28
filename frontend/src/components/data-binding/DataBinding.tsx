'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  Database,
  FileText,
  Globe,
  RefreshCw,
  Plus,
  Trash2,
  Edit3,
  Link,
  Unlink,
  Check,
  X,
  ChevronRight,
  Table,
  Code,
  Cloud,
  Layers,
  Settings,
  Play,
  Eye
} from 'lucide-react';

interface DataSource {
  id: string;
  name: string;
  type: 'csv' | 'json' | 'rest_api' | 'graphql' | 'google_sheets' | 'airtable' | 'firebase' | 'supabase' | 'notion';
  url?: string;
  schema?: Record<string, string>;
  lastSync?: Date;
  status: 'connected' | 'error' | 'syncing';
}

interface DataVariable {
  id: string;
  name: string;
  value: unknown;
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  sourceId?: string;
  path?: string;
}

interface DataBinding {
  id: string;
  elementId: string;
  elementName: string;
  property: string;
  variableId: string;
  transform?: string;
}

interface DataBindingProps {
  onBindingCreate?: (binding: DataBinding) => void;
  onVariableChange?: (variable: DataVariable) => void;
}

const SOURCE_TYPES = [
  { type: 'csv', label: 'CSV File', icon: FileText, color: 'bg-green-500' },
  { type: 'json', label: 'JSON', icon: Code, color: 'bg-yellow-500' },
  { type: 'rest_api', label: 'REST API', icon: Globe, color: 'bg-blue-500' },
  { type: 'graphql', label: 'GraphQL', icon: Globe, color: 'bg-pink-500' },
  { type: 'google_sheets', label: 'Google Sheets', icon: Table, color: 'bg-emerald-500' },
  { type: 'airtable', label: 'Airtable', icon: Database, color: 'bg-purple-500' },
  { type: 'firebase', label: 'Firebase', icon: Cloud, color: 'bg-orange-500' },
  { type: 'supabase', label: 'Supabase', icon: Database, color: 'bg-teal-500' },
  { type: 'notion', label: 'Notion', icon: Layers, color: 'bg-gray-700' },
];

const BINDABLE_PROPERTIES = [
  { property: 'text', label: 'Text Content' },
  { property: 'src', label: 'Image Source' },
  { property: 'href', label: 'Link URL' },
  { property: 'fill', label: 'Fill Color' },
  { property: 'stroke', label: 'Stroke Color' },
  { property: 'opacity', label: 'Opacity' },
  { property: 'visibility', label: 'Visibility' },
  { property: 'width', label: 'Width' },
  { property: 'height', label: 'Height' },
  { property: 'x', label: 'X Position' },
  { property: 'y', label: 'Y Position' },
];

export function DataBinding({ onBindingCreate, onVariableChange }: DataBindingProps) {
  const [activeTab, setActiveTab] = useState<'sources' | 'variables' | 'bindings'>('sources');
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [variables, setVariables] = useState<DataVariable[]>([]);
  const [bindings, setBindings] = useState<DataBinding[]>([]);
  const [showAddSource, setShowAddSource] = useState(false);
  const [selectedSourceType, setSelectedSourceType] = useState<string>('rest_api');
  const [newSourceUrl, setNewSourceUrl] = useState('');
  const [newSourceName, setNewSourceName] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [previewData, setPreviewData] = useState<any>(null);

  const handleConnectSource = useCallback(async () => {
    if (!newSourceName || !newSourceUrl) return;

    setIsConnecting(true);
    try {
      const response = await fetch('/api/v1/data-binding/sources/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newSourceName,
          source_type: selectedSourceType,
          url: newSourceUrl
        })
      });

      if (response.ok) {
        const source = await response.json();
        setDataSources([...dataSources, source]);
        setShowAddSource(false);
        setNewSourceName('');
        setNewSourceUrl('');
      }
    } catch (error) {
      console.error('Connection error:', error);
    } finally {
      setIsConnecting(false);
    }
  }, [newSourceName, newSourceUrl, selectedSourceType, dataSources]);

  const handleFetchPreview = useCallback(async (sourceId: string) => {
    try {
      const response = await fetch(`/api/v1/data-binding/sources/${sourceId}/preview/`);
      if (response.ok) {
        const data = await response.json();
        setPreviewData(data);
      }
    } catch (error) {
      console.error('Preview error:', error);
    }
  }, []);

  const handleCreateVariable = useCallback(() => {
    const newVar: DataVariable = {
      id: `var_${Date.now()}`,
      name: `variable${variables.length + 1}`,
      value: '',
      type: 'string'
    };
    setVariables([...variables, newVar]);
    onVariableChange?.(newVar);
  }, [variables, onVariableChange]);

  const handleCreateBinding = useCallback((elementId: string, elementName: string) => {
    if (variables.length === 0) {
      alert('Create a variable first');
      return;
    }

    const newBinding: DataBinding = {
      id: `binding_${Date.now()}`,
      elementId,
      elementName,
      property: 'text',
      variableId: variables[0].id
    };
    setBindings([...bindings, newBinding]);
    onBindingCreate?.(newBinding);
  }, [variables, bindings, onBindingCreate]);

  const handleSyncSource = useCallback(async (sourceId: string) => {
    setDataSources(dataSources.map(s => 
      s.id === sourceId ? { ...s, status: 'syncing' as const } : s
    ));

    try {
      await fetch(`/api/v1/data-binding/sources/${sourceId}/fetch/`, { method: 'POST' });
      setDataSources(dataSources.map(s => 
        s.id === sourceId ? { ...s, status: 'connected' as const, lastSync: new Date() } : s
      ));
    } catch (error) {
      setDataSources(dataSources.map(s => 
        s.id === sourceId ? { ...s, status: 'error' as const } : s
      ));
    }
  }, [dataSources]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Data Binding</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Connect designs to external data sources
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'sources', label: 'Data Sources', icon: Database },
          { id: 'variables', label: 'Variables', icon: Code },
          { id: 'bindings', label: 'Bindings', icon: Link },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as 'variables' | 'sources' | 'bindings')}
            className={`flex items-center gap-2 px-6 py-3 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'sources' && (
          <div className="space-y-4">
            {/* Add Source Button */}
            {!showAddSource ? (
              <button
                onClick={() => setShowAddSource(true)}
                className="w-full py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500 flex items-center justify-center gap-2 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Add Data Source
              </button>
            ) : (
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium text-gray-900 dark:text-white">New Data Source</h3>
                  <button onClick={() => setShowAddSource(false)}>
                    <X className="w-5 h-5 text-gray-400" />
                  </button>
                </div>

                {/* Source Type Selection */}
                <div className="grid grid-cols-3 gap-2">
                  {SOURCE_TYPES.map(st => (
                    <button
                      key={st.type}
                      onClick={() => setSelectedSourceType(st.type)}
                      className={`p-3 rounded-lg border-2 transition-all ${
                        selectedSourceType === st.type
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-8 h-8 ${st.color} rounded-lg flex items-center justify-center mx-auto mb-2`}>
                        <st.icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="text-xs font-medium text-gray-900 dark:text-white">{st.label}</div>
                    </button>
                  ))}
                </div>

                {/* Source Details */}
                <div className="space-y-3">
                  <input
                    type="text"
                    value={newSourceName}
                    onChange={(e) => setNewSourceName(e.target.value)}
                    placeholder="Source name..."
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                  />
                  <input
                    type="url"
                    value={newSourceUrl}
                    onChange={(e) => setNewSourceUrl(e.target.value)}
                    placeholder="URL or connection string..."
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                  />
                </div>

                <button
                  onClick={handleConnectSource}
                  disabled={isConnecting || !newSourceName || !newSourceUrl}
                  className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isConnecting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Cloud className="w-4 h-4" />}
                  Connect
                </button>
              </div>
            )}

            {/* Connected Sources */}
            {dataSources.length > 0 ? (
              <div className="space-y-3">
                {dataSources.map(source => {
                  const sourceType = SOURCE_TYPES.find(st => st.type === source.type);
                  return (
                    <div
                      key={source.id}
                      className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 ${sourceType?.color || 'bg-gray-500'} rounded-lg flex items-center justify-center`}>
                            {sourceType && <sourceType.icon className="w-5 h-5 text-white" />}
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">{source.name}</h4>
                            <p className="text-xs text-gray-500">{sourceType?.label}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {source.status === 'connected' && (
                            <span className="flex items-center gap-1 text-xs text-green-600">
                              <Check className="w-3 h-3" />
                              Connected
                            </span>
                          )}
                          {source.status === 'syncing' && (
                            <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />
                          )}
                          {source.status === 'error' && (
                            <span className="text-xs text-red-600">Error</span>
                          )}
                          <button
                            onClick={() => handleSyncSource(source.id)}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                          >
                            <RefreshCw className="w-4 h-4 text-gray-500" />
                          </button>
                          <button
                            onClick={() => handleFetchPreview(source.id)}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                          >
                            <Eye className="w-4 h-4 text-gray-500" />
                          </button>
                        </div>
                      </div>

                      {source.schema && (
                        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                          <p className="text-xs text-gray-500 mb-2">Schema:</p>
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(source.schema).map(([key, type]) => (
                              <span key={key} className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 rounded">
                                {key}: <span className="text-blue-600">{type}</span>
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              !showAddSource && (
                <div className="text-center py-8 text-gray-500">
                  <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No data sources connected</p>
                </div>
              )
            )}

            {/* Data Preview */}
            {previewData && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Data Preview</h4>
                <pre className="text-xs text-gray-600 dark:text-gray-400 overflow-auto max-h-48">
                  {JSON.stringify(previewData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}

        {activeTab === 'variables' && (
          <div className="space-y-4">
            <button
              onClick={handleCreateVariable}
              className="w-full py-3 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500 flex items-center justify-center gap-2 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Create Variable
            </button>

            {variables.length > 0 ? (
              <div className="space-y-3">
                {variables.map(variable => (
                  <div
                    key={variable.id}
                    className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <input
                        type="text"
                        value={variable.name}
                        onChange={(e) => {
                          const updated = { ...variable, name: e.target.value };
                          setVariables(variables.map(v => v.id === variable.id ? updated : v));
                        }}
                        className="font-mono text-sm bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-1 text-gray-900 dark:text-white"
                      />
                      <select
                        value={variable.type}
                        onChange={(e) => {
                          const updated = { ...variable, type: e.target.value as 'string' | 'number' | 'boolean' | 'array' | 'object' };
                          setVariables(variables.map(v => v.id === variable.id ? updated : v));
                        }}
                        className="text-xs px-2 py-1 border border-gray-200 dark:border-gray-600 rounded bg-white dark:bg-gray-700"
                      >
                        <option value="string">String</option>
                        <option value="number">Number</option>
                        <option value="boolean">Boolean</option>
                        <option value="array">Array</option>
                        <option value="object">Object</option>
                      </select>
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={variable.value?.toString() || ''}
                        onChange={(e) => {
                          const updated = { ...variable, value: e.target.value };
                          setVariables(variables.map(v => v.id === variable.id ? updated : v));
                          onVariableChange?.(updated);
                        }}
                        placeholder="Value..."
                        className="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                      />
                      <button
                        onClick={() => setVariables(variables.filter(v => v.id !== variable.id))}
                        className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    {variable.sourceId && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                        <Link className="w-3 h-3" />
                        Bound to source: {variable.path}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Code className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No variables defined</p>
                <p className="text-sm">Create variables to bind to your design elements</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'bindings' && (
          <div className="space-y-4">
            {bindings.length > 0 ? (
              <div className="space-y-3">
                {bindings.map(binding => {
                  const variable = variables.find(v => v.id === binding.variableId);
                  return (
                    <div
                      key={binding.id}
                      className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900 dark:text-white">
                              {binding.elementName}
                            </span>
                            <ChevronRight className="w-4 h-4 text-gray-400" />
                            <span className="text-blue-600">{binding.property}</span>
                          </div>
                        </div>
                        <Link className="w-4 h-4 text-green-500" />
                        <div className="text-right">
                          <div className="font-mono text-sm text-gray-900 dark:text-white">
                            {variable?.name || 'unbound'}
                          </div>
                          <div className="text-xs text-gray-500">
                            {variable?.value?.toString() || '-'}
                          </div>
                        </div>
                        <button
                          onClick={() => setBindings(bindings.filter(b => b.id !== binding.id))}
                          className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                        >
                          <Unlink className="w-4 h-4" />
                        </button>
                      </div>

                      {binding.transform && (
                        <div className="mt-2 text-xs text-gray-500">
                          Transform: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{binding.transform}</code>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Link className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No bindings created</p>
                <p className="text-sm">Select an element and bind it to a variable</p>
              </div>
            )}

            {/* Bind Element Panel */}
            <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white mb-3">Bind Selected Element</h4>
              <div className="grid grid-cols-2 gap-3">
                <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm">
                  <option value="">Select property...</option>
                  {BINDABLE_PROPERTIES.map(p => (
                    <option key={p.property} value={p.property}>{p.label}</option>
                  ))}
                </select>
                <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm">
                  <option value="">Select variable...</option>
                  {variables.map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => handleCreateBinding('element_1', 'Selected Element')}
                className="w-full mt-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
              >
                <Link className="w-4 h-4" />
                Create Binding
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DataBinding;

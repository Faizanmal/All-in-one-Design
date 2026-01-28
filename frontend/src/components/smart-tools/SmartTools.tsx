'use client';

import React, { useState, useCallback } from 'react';
import {
  Search,
  Replace,
  Layers,
  Type,
  Palette,
  Scale,
  Edit3,
  RefreshCw,
  Check,
  X,
  ChevronDown
} from 'lucide-react';

interface SelectionCriteria {
  type?: string;
  color?: string;
  font?: string;
  layer?: string;
}

interface SmartToolsProps {
  onSelect?: (elementIds: string[]) => void;
  onBatchRename?: (pattern: string) => void;
  onFindReplace?: (find: string, replace: string) => void;
  onBatchResize?: (mode: string, value: number) => void;
}

type TabType = 'select' | 'rename' | 'findReplace' | 'resize';

export function SmartTools({ onSelect, onBatchRename, onFindReplace, onBatchResize }: SmartToolsProps) {
  const [activeTab, setActiveTab] = useState<TabType>('select');
  const [selectionQuery, setSelectionQuery] = useState('');
  const [renamePattern, setRenamePattern] = useState('{name}_{n:3}');
  const [findText, setFindText] = useState('');
  const [replaceText, setReplaceText] = useState('');
  const [resizeMode, setResizeMode] = useState('scale');
  const [resizeValue, setResizeValue] = useState(100);
  const [selectedCount, setSelectedCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);

  const tabs = [
    { id: 'select', label: 'Smart Select', icon: Layers },
    { id: 'rename', label: 'Batch Rename', icon: Edit3 },
    { id: 'findReplace', label: 'Find & Replace', icon: Replace },
    { id: 'resize', label: 'Batch Resize', icon: Scale },
  ];

  const selectionPresets = [
    { label: 'All Text', query: 'type:text' },
    { label: 'All Images', query: 'type:image' },
    { label: 'All Buttons', query: 'type:button OR name:*btn*' },
    { label: 'Primary Color', query: 'fill:#3b82f6' },
    { label: 'Unlabeled', query: '-name:*' },
  ];

  const renamePatterns = [
    { pattern: '{name}_{n:3}', label: 'Name + Number (001, 002...)' },
    { pattern: '{type}_{name}', label: 'Type + Name' },
    { pattern: '{name}_{date}', label: 'Name + Date' },
    { pattern: '{name:upper}', label: 'Uppercase' },
    { pattern: '{name:lower}', label: 'Lowercase' },
  ];

  const resizeModes = [
    { mode: 'scale', label: 'Scale %' },
    { mode: 'width', label: 'Set Width' },
    { mode: 'height', label: 'Set Height' },
    { mode: 'fit', label: 'Fit to Size' },
    { mode: 'fill', label: 'Fill Size' },
  ];

  const handleSmartSelect = useCallback(async () => {
    setIsProcessing(true);
    try {
      // In production, call API
      const response = await fetch('/api/v1/smart-tools/select/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: selectionQuery })
      });
      const data = await response.json();
      setSelectedCount(data.selected?.length || 0);
      onSelect?.(data.selected || []);
    } catch (error) {
      console.error('Selection error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [selectionQuery, onSelect]);

  const handleBatchRename = useCallback(async () => {
    setIsProcessing(true);
    try {
      onBatchRename?.(renamePattern);
      // Simulated success
      setTimeout(() => setIsProcessing(false), 1000);
    } catch (error) {
      console.error('Rename error:', error);
      setIsProcessing(false);
    }
  }, [renamePattern, onBatchRename]);

  const handleFindReplace = useCallback(async () => {
    setIsProcessing(true);
    try {
      onFindReplace?.(findText, replaceText);
      setTimeout(() => setIsProcessing(false), 1000);
    } catch (error) {
      console.error('Find/Replace error:', error);
      setIsProcessing(false);
    }
  }, [findText, replaceText, onFindReplace]);

  const handleBatchResize = useCallback(async () => {
    setIsProcessing(true);
    try {
      onBatchResize?.(resizeMode, resizeValue);
      setTimeout(() => setIsProcessing(false), 1000);
    } catch (error) {
      console.error('Resize error:', error);
      setIsProcessing(false);
    }
  }, [resizeMode, resizeValue, onBatchResize]);

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Smart Tools</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Batch operations and intelligent selection
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as TabType)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'select' && (
          <div className="space-y-4">
            {/* Query input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Selection Query
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={selectionQuery}
                  onChange={(e) => setSelectionQuery(e.target.value)}
                  placeholder="type:text AND fill:#000000"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Presets */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Quick Presets
              </label>
              <div className="flex flex-wrap gap-2">
                {selectionPresets.map(preset => (
                  <button
                    key={preset.query}
                    onClick={() => setSelectionQuery(preset.query)}
                    className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    {preset.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Selection criteria */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Type className="w-4 h-4 inline mr-1" /> By Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Any type</option>
                  <option value="text">Text</option>
                  <option value="image">Image</option>
                  <option value="frame">Frame</option>
                  <option value="component">Component</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Palette className="w-4 h-4 inline mr-1" /> By Color
                </label>
                <input
                  type="color"
                  className="w-full h-10 rounded-lg cursor-pointer"
                />
              </div>
            </div>

            {/* Results */}
            {selectedCount > 0 && (
              <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg flex items-center gap-2">
                <Check className="w-5 h-5 text-green-600" />
                <span className="text-green-700 dark:text-green-400">
                  {selectedCount} elements selected
                </span>
              </div>
            )}

            <button
              onClick={handleSmartSelect}
              disabled={isProcessing || !selectionQuery}
              className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4" />}
              Select Matching Elements
            </button>
          </div>
        )}

        {activeTab === 'rename' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Rename Pattern
              </label>
              <input
                type="text"
                value={renamePattern}
                onChange={(e) => setRenamePattern(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Pattern Templates
              </label>
              <div className="space-y-2">
                {renamePatterns.map(p => (
                  <button
                    key={p.pattern}
                    onClick={() => setRenamePattern(p.pattern)}
                    className={`w-full text-left px-4 py-2 rounded-lg border ${
                      renamePattern === p.pattern
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="font-mono text-sm text-gray-900 dark:text-white">{p.pattern}</div>
                    <div className="text-xs text-gray-500">{p.label}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-300">Preview:</div>
              <div className="font-mono text-sm text-gray-900 dark:text-white mt-1">
                Button → Button_001, Button_002...
              </div>
            </div>

            <button
              onClick={handleBatchRename}
              disabled={isProcessing}
              className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Edit3 className="w-4 h-4" />}
              Apply Rename
            </button>
          </div>
        )}

        {activeTab === 'findReplace' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Find
              </label>
              <input
                type="text"
                value={findText}
                onChange={(e) => setFindText(e.target.value)}
                placeholder="Text or color to find..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Replace with
              </label>
              <input
                type="text"
                value={replaceText}
                onChange={(e) => setReplaceText(e.target.value)}
                placeholder="Replacement text or color..."
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Case sensitive</span>
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Use regex</span>
              </label>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleFindReplace}
                disabled={isProcessing || !findText}
                className="flex-1 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Replace className="w-4 h-4" />}
                Replace All
              </button>
            </div>
          </div>
        )}

        {activeTab === 'resize' && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Resize Mode
              </label>
              <select
                value={resizeMode}
                onChange={(e) => setResizeMode(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {resizeModes.map(m => (
                  <option key={m.mode} value={m.mode}>{m.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Value {resizeMode === 'scale' ? '(%)' : '(px)'}
              </label>
              <input
                type="number"
                value={resizeValue}
                onChange={(e) => setResizeValue(Number(e.target.value))}
                min={resizeMode === 'scale' ? 1 : 0}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input type="checkbox" defaultChecked className="rounded" />
                <span className="text-sm text-gray-700 dark:text-gray-300">Maintain aspect ratio</span>
              </label>
            </div>

            <button
              onClick={handleBatchResize}
              disabled={isProcessing}
              className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isProcessing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Scale className="w-4 h-4" />}
              Apply Resize
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default SmartTools;

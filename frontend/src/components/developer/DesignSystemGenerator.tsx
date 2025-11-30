/**
 * Design System Generator Component
 * Generate and export design systems from projects
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Palette,
  Type,
  Box,
  Layers,
  Download,
  Plus,
  Trash2,
  Edit3,
  Save,
  Loader2,
  Check,
} from 'lucide-react';

interface ColorToken {
  name: string;
  value: string;
  variants?: { name: string; value: string }[];
}

interface TypographyToken {
  name: string;
  fontFamily: string;
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
}

interface SpacingToken {
  name: string;
  value: string;
}

interface ComponentSpec {
  name: string;
  description: string;
  variants: string[];
  props: { name: string; type: string; required: boolean }[];
}

interface DesignSystem {
  id: string;
  name: string;
  description: string;
  colors: ColorToken[];
  typography: TypographyToken[];
  spacing: SpacingToken[];
  components: ComponentSpec[];
  createdAt: string;
  updatedAt: string;
}

interface DesignSystemGeneratorProps {
  projectId: string;
  onSave?: (system: DesignSystem) => void;
}

export const DesignSystemGenerator: React.FC<DesignSystemGeneratorProps> = ({
  projectId,
  onSave,
}) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'colors' | 'typography' | 'spacing' | 'components'>('colors');
  const [system, setSystem] = useState<DesignSystem>({
    id: '',
    name: 'My Design System',
    description: '',
    colors: [],
    typography: [],
    spacing: [],
    components: [],
    createdAt: '',
    updatedAt: '',
  });

  const extractFromProject = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/projects/design-systems/extract/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ project_id: projectId }),
      });

      if (response.ok) {
        const data = await response.json();
        setSystem((prev) => ({
          ...prev,
          colors: data.colors || [],
          typography: data.typography || [],
          spacing: data.spacing || [],
          components: data.components || [],
        }));
      }
    } catch (err) {
      console.error('Failed to extract design system:', err);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  const saveSystem = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/v1/projects/design-systems/', {
        method: system.id ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          ...system,
          project: projectId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSystem(data);
        onSave?.(data);
      }
    } catch (err) {
      console.error('Failed to save design system:', err);
    } finally {
      setSaving(false);
    }
  };

  const exportSystem = async (format: 'json' | 'css' | 'scss' | 'tokens') => {
    try {
      const response = await fetch(
        `/api/v1/projects/design-systems/${system.id}/export/?format=${format}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `design-system.${format === 'tokens' ? 'json' : format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      console.error('Failed to export design system:', err);
    }
  };

  // Color management
  const addColor = () => {
    setSystem((prev) => ({
      ...prev,
      colors: [
        ...prev.colors,
        { name: `color-${prev.colors.length + 1}`, value: '#000000' },
      ],
    }));
  };

  const updateColor = (index: number, updates: Partial<ColorToken>) => {
    setSystem((prev) => ({
      ...prev,
      colors: prev.colors.map((c, i) => (i === index ? { ...c, ...updates } : c)),
    }));
  };

  const removeColor = (index: number) => {
    setSystem((prev) => ({
      ...prev,
      colors: prev.colors.filter((_, i) => i !== index),
    }));
  };

  // Typography management
  const addTypography = () => {
    setSystem((prev) => ({
      ...prev,
      typography: [
        ...prev.typography,
        {
          name: `text-${prev.typography.length + 1}`,
          fontFamily: 'Inter',
          fontSize: '16px',
          fontWeight: '400',
          lineHeight: '1.5',
        },
      ],
    }));
  };

  const updateTypography = (index: number, updates: Partial<TypographyToken>) => {
    setSystem((prev) => ({
      ...prev,
      typography: prev.typography.map((t, i) =>
        i === index ? { ...t, ...updates } : t
      ),
    }));
  };

  const removeTypography = (index: number) => {
    setSystem((prev) => ({
      ...prev,
      typography: prev.typography.filter((_, i) => i !== index),
    }));
  };

  // Spacing management
  const addSpacing = () => {
    setSystem((prev) => ({
      ...prev,
      spacing: [
        ...prev.spacing,
        { name: `space-${prev.spacing.length + 1}`, value: '8px' },
      ],
    }));
  };

  const updateSpacing = (index: number, updates: Partial<SpacingToken>) => {
    setSystem((prev) => ({
      ...prev,
      spacing: prev.spacing.map((s, i) => (i === index ? { ...s, ...updates } : s)),
    }));
  };

  const removeSpacing = (index: number) => {
    setSystem((prev) => ({
      ...prev,
      spacing: prev.spacing.filter((_, i) => i !== index),
    }));
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
              <Layers className="w-5 h-5 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Design System
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Generate and manage design tokens
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={extractFromProject}
              disabled={loading}
              className="px-3 py-1.5 text-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/20 rounded-lg text-sm font-medium"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                'Extract from Design'
              )}
            </button>
            <button
              onClick={saveSystem}
              disabled={saving}
              className="flex items-center gap-1 px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium"
            >
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Save
            </button>
          </div>
        </div>

        {/* System Name */}
        <input
          type="text"
          value={system.name}
          onChange={(e) => setSystem({ ...system, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white text-lg font-medium"
          placeholder="Design System Name"
        />
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'colors', label: 'Colors', icon: Palette },
          { id: 'typography', label: 'Typography', icon: Type },
          { id: 'spacing', label: 'Spacing', icon: Box },
          { id: 'components', label: 'Components', icon: Layers },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as typeof activeTab)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px ${
              activeTab === id
                ? 'border-purple-500 text-purple-600 dark:text-purple-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Colors */}
        {activeTab === 'colors' && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-medium text-gray-900 dark:text-white">Color Tokens</h3>
              <button
                onClick={addColor}
                className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700"
              >
                <Plus className="w-4 h-4" />
                Add Color
              </button>
            </div>
            {system.colors.map((color, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <input
                  type="color"
                  value={color.value}
                  onChange={(e) => updateColor(index, { value: e.target.value })}
                  className="w-10 h-10 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={color.name}
                  onChange={(e) => updateColor(index, { name: e.target.value })}
                  className="flex-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-1 focus:ring-purple-500 dark:bg-gray-600 dark:text-white text-sm"
                  placeholder="Color name"
                />
                <code className="px-2 py-1 bg-gray-200 dark:bg-gray-600 rounded text-xs">
                  {color.value}
                </code>
                <button
                  onClick={() => removeColor(index)}
                  className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
            {system.colors.length === 0 && (
              <p className="text-center py-8 text-gray-500">
                No colors defined. Add colors or extract from your design.
              </p>
            )}
          </div>
        )}

        {/* Typography */}
        {activeTab === 'typography' && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-medium text-gray-900 dark:text-white">Typography Tokens</h3>
              <button
                onClick={addTypography}
                className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700"
              >
                <Plus className="w-4 h-4" />
                Add Style
              </button>
            </div>
            {system.typography.map((typo, index) => (
              <div
                key={index}
                className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg space-y-2"
              >
                <div className="flex items-center justify-between">
                  <input
                    type="text"
                    value={typo.name}
                    onChange={(e) => updateTypography(index, { name: e.target.value })}
                    className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-1 focus:ring-purple-500 dark:bg-gray-600 dark:text-white text-sm font-medium"
                  />
                  <button
                    onClick={() => removeTypography(index)}
                    className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="grid grid-cols-4 gap-2">
                  <input
                    type="text"
                    value={typo.fontFamily}
                    onChange={(e) => updateTypography(index, { fontFamily: e.target.value })}
                    placeholder="Font family"
                    className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-xs dark:bg-gray-600 dark:text-white"
                  />
                  <input
                    type="text"
                    value={typo.fontSize}
                    onChange={(e) => updateTypography(index, { fontSize: e.target.value })}
                    placeholder="Size"
                    className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-xs dark:bg-gray-600 dark:text-white"
                  />
                  <input
                    type="text"
                    value={typo.fontWeight}
                    onChange={(e) => updateTypography(index, { fontWeight: e.target.value })}
                    placeholder="Weight"
                    className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-xs dark:bg-gray-600 dark:text-white"
                  />
                  <input
                    type="text"
                    value={typo.lineHeight}
                    onChange={(e) => updateTypography(index, { lineHeight: e.target.value })}
                    placeholder="Line height"
                    className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-xs dark:bg-gray-600 dark:text-white"
                  />
                </div>
                <div
                  style={{
                    fontFamily: typo.fontFamily,
                    fontSize: typo.fontSize,
                    fontWeight: typo.fontWeight as any,
                    lineHeight: typo.lineHeight,
                  }}
                  className="text-gray-900 dark:text-white"
                >
                  The quick brown fox jumps over the lazy dog
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Spacing */}
        {activeTab === 'spacing' && (
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="font-medium text-gray-900 dark:text-white">Spacing Tokens</h3>
              <button
                onClick={addSpacing}
                className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-700"
              >
                <Plus className="w-4 h-4" />
                Add Spacing
              </button>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {system.spacing.map((space, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div
                    className="bg-purple-500"
                    style={{ width: space.value, height: space.value, minWidth: '8px', minHeight: '8px' }}
                  />
                  <input
                    type="text"
                    value={space.name}
                    onChange={(e) => updateSpacing(index, { name: e.target.value })}
                    className="flex-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-600 dark:text-white"
                  />
                  <input
                    type="text"
                    value={space.value}
                    onChange={(e) => updateSpacing(index, { value: e.target.value })}
                    className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-600 dark:text-white"
                  />
                  <button
                    onClick={() => removeSpacing(index)}
                    className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Components */}
        {activeTab === 'components' && (
          <div className="space-y-3">
            <h3 className="font-medium text-gray-900 dark:text-white">Component Specifications</h3>
            {system.components.length === 0 ? (
              <p className="text-center py-8 text-gray-500">
                No components defined. Extract from your design to generate specs.
              </p>
            ) : (
              system.components.map((comp, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                    {comp.name}
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                    {comp.description}
                  </p>
                  {comp.variants.length > 0 && (
                    <div className="flex gap-2 mb-2">
                      {comp.variants.map((v, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs"
                        >
                          {v}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Export Footer */}
      {system.id && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Export as:</span>
            <button
              onClick={() => exportSystem('json')}
              className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-sm"
            >
              JSON
            </button>
            <button
              onClick={() => exportSystem('css')}
              className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-sm"
            >
              CSS
            </button>
            <button
              onClick={() => exportSystem('scss')}
              className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-sm"
            >
              SCSS
            </button>
            <button
              onClick={() => exportSystem('tokens')}
              className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded text-sm"
            >
              Design Tokens
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DesignSystemGenerator;

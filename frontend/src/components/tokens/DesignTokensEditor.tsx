'use client';

import React, { useState, useEffect } from 'react';

// Types
interface DesignToken {
  id: number;
  name: string;
  category: string;
  token_type: string;
  value: string;
  resolved_value: string;
  css_variable: string;
  description: string;
  deprecated: boolean;
}

interface DesignTokenLibrary {
  id: number;
  name: string;
  description: string;
  version: string;
  token_count: number;
  theme_count: number;
  is_public: boolean;
  is_default: boolean;
}

interface DesignTheme {
  id: number;
  name: string;
  slug: string;
  description: string;
  theme_type: string;
  is_default: boolean;
}

interface DesignTokensEditorProps {
  projectId?: number;
  onTokenSelect?: (token: DesignToken) => void;
}

// Token type colors for visualization
const TOKEN_TYPE_COLORS: Record<string, string> = {
  color: 'bg-gradient-to-r from-red-500 via-yellow-500 to-blue-500',
  typography: 'bg-gray-600',
  spacing: 'bg-green-500',
  sizing: 'bg-blue-500',
  border_radius: 'bg-purple-500',
  shadow: 'bg-gray-800',
  opacity: 'bg-gradient-to-r from-transparent to-black',
  z_index: 'bg-indigo-500',
  custom: 'bg-gray-400',
};

// Design Tokens Editor Component
export function DesignTokensEditor({
  onTokenSelect,
}: DesignTokensEditorProps) {
  const [libraries, setLibraries] = useState<DesignTokenLibrary[]>([]);
  const [selectedLibrary, setSelectedLibrary] = useState<DesignTokenLibrary | null>(null);
  const [tokens, setTokens] = useState<DesignToken[]>([]);
  const [themes, setThemes] = useState<DesignTheme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<DesignTheme | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('');
  const [filterCategory] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Fetch libraries
  useEffect(() => {
    fetch('/api/v1/projects/design-token-libraries/?include_public=true')
      .then((res) => res.json())
      .then((data) => {
        setLibraries(data.libraries || []);
        if (data.libraries?.length > 0) {
          setSelectedLibrary(data.libraries[0]);
        }
      })
      .catch(console.error);
  }, []);

  // Fetch tokens when library changes
  useEffect(() => {
    if (!selectedLibrary) return;

    let mounted = true;

    Promise.all([
      fetch(`/api/v1/projects/design-token-libraries/${selectedLibrary.id}/`).then((r) => r.json()),
    ])
      .then(([libraryData]) => {
        if (mounted) {
          setLoading(true);
          setTokens(libraryData.tokens || []);
          setThemes(libraryData.themes || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [selectedLibrary]);

  // Get unique categories and types
  const categories = [...new Set(tokens.map((t) => t.category).filter(Boolean))];
  const types = [...new Set(tokens.map((t) => t.token_type).filter(Boolean))];

  // Filter tokens
  const filteredTokens = tokens.filter((token) => {
    const matchesSearch =
      !searchQuery ||
      token.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      token.value.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !filterType || token.token_type === filterType;
    const matchesCategory = !filterCategory || token.category === filterCategory;
    return matchesSearch && matchesType && matchesCategory;
  });

  // Group tokens by category
  const groupedTokens = filteredTokens.reduce((acc, token) => {
    const cat = token.category || 'Uncategorized';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(token);
    return acc;
  }, {} as Record<string, DesignToken[]>);

  // Export tokens
  const exportTokens = async (format: string) => {
    if (!selectedLibrary) return;

    try {
      const response = await fetch(
        `/api/v1/projects/design-token-libraries/${selectedLibrary.id}/export/?format=${format}&download=true`
      );
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedLibrary.name.toLowerCase().replace(/ /g, '-')}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Create new token
  const createToken = async (data: Partial<DesignToken>) => {
    if (!selectedLibrary) return;

    try {
      const response = await fetch(`/api/v1/projects/design-tokens/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          library_pk: selectedLibrary.id,
          ...data,
        }),
      });
      const newToken = await response.json();
      setTokens([...tokens, newToken]);
      setShowCreateModal(false);
    } catch (error) {
      console.error('Failed to create token:', error);
    }
  };

  // Render color preview
  const renderColorPreview = (value: string) => {
    const isColor = /^#|^rgb|^hsl/.test(value);
    if (!isColor) return null;
    return (
      <div
        className="w-6 h-6 rounded border border-gray-300"
        style={{ backgroundColor: value }}
      />
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Design Tokens
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
            >
              + New Token
            </button>
            <div className="relative group">
              <button className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 text-sm rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                Export ▾
              </button>
              <div className="absolute right-0 mt-1 w-40 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg hidden group-hover:block z-10">
                {['css', 'scss', 'json', 'js', 'ts', 'tailwind'].map((format) => (
                  <button
                    key={format}
                    onClick={() => exportTokens(format)}
                    className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    Export as {format.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Library selector */}
        <select
          value={selectedLibrary?.id || ''}
          onChange={(e) => {
            const lib = libraries.find((l) => l.id === Number(e.target.value));
            setSelectedLibrary(lib || null);
          }}
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-3"
        >
          {libraries.map((lib) => (
            <option key={lib.id} value={lib.id}>
              {lib.name} ({lib.token_count} tokens)
            </option>
          ))}
        </select>

        {/* Search and filters */}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search tokens..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="p-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
          >
            <option value="">All Types</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* Theme selector */}
        {themes.length > 0 && (
          <div className="mt-3 flex gap-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Theme:</span>
            {themes.map((theme) => (
              <button
                key={theme.id}
                onClick={() => setSelectedTheme(theme.id === selectedTheme?.id ? null : theme)}
                className={`px-3 py-1 text-xs rounded-full ${
                  selectedTheme?.id === theme.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                {theme.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Token list */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <svg className="animate-spin h-8 w-8 text-blue-500" viewBox="0 0 24 24">
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
        ) : (
          Object.entries(groupedTokens).map(([category, categoryTokens]) => (
            <div key={category} className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">
                {category}
              </h3>
              <div className="space-y-2">
                {categoryTokens.map((token) => (
                  <div
                    key={token.id}
                    onClick={() => onTokenSelect?.(token)}
                    className={`p-3 border border-gray-200 dark:border-gray-600 rounded-lg hover:border-blue-500 cursor-pointer transition-colors ${
                      token.deprecated ? 'opacity-50' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {/* Type indicator */}
                        <div
                          className={`w-3 h-3 rounded-full ${
                            TOKEN_TYPE_COLORS[token.token_type] || TOKEN_TYPE_COLORS.custom
                          }`}
                        />
                        {/* Color preview for color tokens */}
                        {token.token_type === 'color' && renderColorPreview(token.value)}
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-sm text-gray-900 dark:text-white">
                              {token.name}
                            </span>
                            {token.deprecated && (
                              <span className="px-1.5 py-0.5 text-xs bg-yellow-100 text-yellow-800 rounded">
                                Deprecated
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {token.css_variable}
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-mono text-sm text-gray-700 dark:text-gray-300">
                          {token.value}
                        </span>
                        {token.resolved_value !== token.value && (
                          <div className="text-xs text-gray-400">
                            → {token.resolved_value}
                          </div>
                        )}
                      </div>
                    </div>
                    {token.description && (
                      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        {token.description}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Token Modal */}
      {showCreateModal && (
        <CreateTokenModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createToken}
          categories={categories}
        />
      )}
    </div>
  );
}

// Create Token Modal
function CreateTokenModal({
  onClose,
  onCreate,
  categories,
}: {
  onClose: () => void;
  onCreate: (data: Partial<DesignToken>) => void;
  categories: string[];
}) {
  const [name, setName] = useState('');
  const [value, setValue] = useState('');
  const [tokenType, setTokenType] = useState('color');
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate({ name, value, token_type: tokenType, category, description });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Create New Token
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
              placeholder="e.g., color-primary-500"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Type
            </label>
            <select
              value={tokenType}
              onChange={(e) => setTokenType(e.target.value)}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
            >
              <option value="color">Color</option>
              <option value="typography">Typography</option>
              <option value="spacing">Spacing</option>
              <option value="sizing">Sizing</option>
              <option value="border_radius">Border Radius</option>
              <option value="shadow">Shadow</option>
              <option value="opacity">Opacity</option>
              <option value="z_index">Z-Index</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Value
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="e.g., #3B82F6"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="e.g., Brand Colors"
              list="categories"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg"
            />
            <datalist id="categories">
              {categories.map((cat) => (
                <option key={cat} value={cat} />
              ))}
            </datalist>
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
              Create Token
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DesignTokensEditor;

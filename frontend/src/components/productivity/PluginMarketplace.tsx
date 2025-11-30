/**
 * Plugin Marketplace Component
 * Browse, install, and manage plugins
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Puzzle,
  Search,
  Star,
  Download,
  Check,
  Settings,
  ExternalLink,
  Filter,
  Loader2,
  ToggleLeft,
  ToggleRight,
} from 'lucide-react';

interface Plugin {
  id: string;
  slug: string;
  name: string;
  description: string;
  version: string;
  category: string;
  icon?: string;
  creatorName: string;
  installs: number;
  ratingAverage: number;
  ratingCount: number;
  price: number;
  isFree: boolean;
  isInstalled: boolean;
}

interface PluginInstallation {
  id: string;
  pluginId: string;
  pluginName: string;
  installedVersion: string;
  isEnabled: boolean;
  config: Record<string, unknown>;
}

interface PluginMarketplaceProps {
  onPluginAction?: (action: string, plugin: Plugin) => void;
}

const CATEGORIES = [
  { id: 'all', name: 'All' },
  { id: 'tools', name: 'Tools' },
  { id: 'effects', name: 'Effects' },
  { id: 'integrations', name: 'Integrations' },
  { id: 'ai', name: 'AI & Automation' },
  { id: 'export', name: 'Export' },
  { id: 'collaboration', name: 'Collaboration' },
  { id: 'analytics', name: 'Analytics' },
];

export const PluginMarketplace: React.FC<PluginMarketplaceProps> = ({
  onPluginAction,
}) => {
  const [view, setView] = useState<'browse' | 'installed'>('browse');
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [installed, setInstalled] = useState<PluginInstallation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('all');
  const [sortBy, setSortBy] = useState<'installs' | 'rating'>('installs');
  const [selectedPlugin, setSelectedPlugin] = useState<Plugin | null>(null);

  const fetchPlugins = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        ...(searchQuery && { search: searchQuery }),
        ...(category !== 'all' && { category }),
        ordering: sortBy === 'rating' ? '-rating_average' : '-installs',
      });

      const response = await fetch(`/api/v1/projects/plugins/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPlugins(data.results || []);
      }
    } catch (err) {
      console.error('Failed to fetch plugins:', err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, category, sortBy]);

  const fetchInstalled = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/projects/plugin-installations/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setInstalled(data.results || []);
      }
    } catch (err) {
      console.error('Failed to fetch installed plugins:', err);
    }
  }, []);

  useEffect(() => {
    if (view === 'browse') {
      fetchPlugins();
    } else {
      fetchInstalled();
    }
  }, [view, fetchPlugins, fetchInstalled]);

  const installPlugin = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/plugins/${pluginId}/install/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        fetchPlugins();
        fetchInstalled();
        onPluginAction?.('install', plugins.find((p) => p.id === pluginId)!);
      }
    } catch (err) {
      console.error('Failed to install plugin:', err);
    }
  };

  const uninstallPlugin = async (pluginId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/plugins/${pluginId}/uninstall/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        fetchPlugins();
        fetchInstalled();
      }
    } catch (err) {
      console.error('Failed to uninstall plugin:', err);
    }
  };

  const togglePlugin = async (installationId: string) => {
    try {
      const response = await fetch(
        `/api/v1/projects/plugin-installations/${installationId}/toggle/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      if (response.ok) {
        fetchInstalled();
      }
    } catch (err) {
      console.error('Failed to toggle plugin:', err);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300 dark:text-gray-600'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
              <Puzzle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Plugins
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Extend your design capabilities
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setView('browse')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                view === 'browse'
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Browse
            </button>
            <button
              onClick={() => setView('installed')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                view === 'installed'
                  ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Installed ({installed.length})
            </button>
          </div>
        </div>

        {view === 'browse' && (
          <div className="space-y-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search plugins..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex items-center gap-2 overflow-x-auto">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setCategory(cat.id)}
                    className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
                      category === cat.id
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'installs' | 'rating')}
                className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 rounded-lg text-sm dark:bg-gray-700 dark:text-white"
              >
                <option value="installs">Most Popular</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : view === 'browse' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plugins.map((plugin) => (
              <div
                key={plugin.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
                    {plugin.icon ? (
                      <img src={plugin.icon} alt={plugin.name} className="w-full h-full object-cover" />
                    ) : (
                      <Puzzle className="w-6 h-6 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {plugin.name}
                        </h3>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          by {plugin.creatorName}
                        </p>
                      </div>
                      <span className="text-xs text-gray-500">v{plugin.version}</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                      {plugin.description}
                    </p>
                    <div className="flex items-center gap-3 mt-2">
                      <div className="flex items-center gap-1">
                        {renderStars(plugin.ratingAverage)}
                        <span className="text-xs text-gray-500">
                          ({plugin.ratingCount})
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        <Download className="w-3 h-3 inline mr-1" />
                        {plugin.installs.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <span className="text-sm font-medium">
                    {plugin.isFree ? (
                      <span className="text-green-600 dark:text-green-400">Free</span>
                    ) : (
                      <span className="text-gray-900 dark:text-white">
                        ${plugin.price.toFixed(2)}
                      </span>
                    )}
                  </span>
                  {plugin.isInstalled ? (
                    <span className="flex items-center gap-1 text-green-600 dark:text-green-400 text-sm">
                      <Check className="w-4 h-4" />
                      Installed
                    </span>
                  ) : (
                    <button
                      onClick={() => installPlugin(plugin.id)}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium"
                    >
                      Install
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {installed.length === 0 ? (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                <Puzzle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No plugins installed yet</p>
                <button
                  onClick={() => setView('browse')}
                  className="mt-2 text-blue-600 hover:text-blue-700"
                >
                  Browse plugins
                </button>
              </div>
            ) : (
              installed.map((installation) => (
                <div
                  key={installation.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                      <Puzzle className="w-5 h-5 text-gray-400" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {installation.pluginName}
                      </h4>
                      <p className="text-xs text-gray-500">
                        v{installation.installedVersion}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => togglePlugin(installation.id)}
                      className={`p-2 rounded-lg ${
                        installation.isEnabled
                          ? 'text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20'
                          : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                      }`}
                    >
                      {installation.isEnabled ? (
                        <ToggleRight className="w-6 h-6" />
                      ) : (
                        <ToggleLeft className="w-6 h-6" />
                      )}
                    </button>
                    <button
                      onClick={() => uninstallPlugin(installation.pluginId)}
                      className="px-3 py-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-sm"
                    >
                      Uninstall
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PluginMarketplace;

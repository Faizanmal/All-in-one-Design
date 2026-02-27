'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Image from 'next/image';
import { searchAPI, AdvancedFilters } from '@/lib/search-api';
import { Search, Filter, X, Palette, Wand2, TrendingUp, Clock } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface SearchResult {
  id: number;
  name: string;
  description: string;
  thumbnail?: string;
  created_at: string;
  updated_at: string;
  canvas_data?: Record<string, unknown>;
  ai_generated?: boolean;
}

export default function SearchPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [autocompleteResults, setAutocompleteResults] = useState<SearchResult[]>([]);
  const [popularSearches, setPopularSearches] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  
  const [filters, setFilters] = useState<AdvancedFilters>({
    project_types: undefined,
    created_after: undefined,
    created_before: undefined,
    min_width: undefined,
    max_width: undefined,
    min_height: undefined,
    max_height: undefined,
    has_ai_prompt: undefined,
    has_color_palette: undefined,
    is_public: undefined,
    owner_username: undefined,
    colors: undefined,
    sort_by: undefined,
  });

  const loadPopularSearches = async () => {
    try {
      const data = await searchAPI.getPopularSearches();
      setPopularSearches(data);
    } catch (error) {
      console.error('Failed to load popular searches:', error);
    }
  };

  const handleAutocomplete = useCallback(async () => {
    if (query.length < 2) return;
    
    try {
      const data = await searchAPI.autocomplete(query, 5);
      setAutocompleteResults(data.results || data);
      setShowAutocomplete(true);
    } catch (error) {
      console.error('Autocomplete failed:', error);
    }
  }, [query]);

  useEffect(() => {
    loadPopularSearches();
  }, []);

  useEffect(() => {
    if (query.length >= 2) {
      const delayDebounce = setTimeout(() => {
        handleAutocomplete();
      }, 300);
      return () => clearTimeout(delayDebounce);
    } else {
      setShowAutocomplete(false);
    }
  }, [query, handleAutocomplete]);

  const handleSearch = async (searchQuery?: string) => {
    const searchTerm = searchQuery || query;
    if (!searchTerm.trim()) return;

    setLoading(true);
    setShowAutocomplete(false);

    try {
      const data = await searchAPI.searchProjects(searchTerm);
      setResults(data.results || data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvancedSearch = async () => {
    setLoading(true);
    setShowAutocomplete(false);

    try {
      const data = await searchAPI.advancedFilter(filters);
      setResults(data.results || data);
      setShowFilters(false);
    } catch (error) {
      console.error('Advanced search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePopularSearch = (search: string) => {
    setQuery(search);
    handleSearch(search);
  };

  const clearFilters = () => {
    setFilters({
      project_types: undefined,
      created_after: undefined,
      created_before: undefined,
      min_width: undefined,
      max_width: undefined,
      min_height: undefined,
      max_height: undefined,
      has_ai_prompt: undefined,
      has_color_palette: undefined,
      is_public: undefined,
      owner_username: undefined,
      colors: undefined,
      sort_by: undefined,
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-purple-50 via-white to-blue-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-linear-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
            Search Projects
          </h1>
          <p className="text-gray-600">Find designs with powerful search and filters</p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative mb-6"
        >
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                ref={searchInputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search projects by name, description, or tags..."
                className="w-full pl-12 pr-4 py-4 bg-white border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:outline-none text-lg shadow-lg"
              />
              {query && (
                <button
                  onClick={() => {
                    setQuery('');
                    setResults([]);
                    setShowAutocomplete(false);
                  }}
                  className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              )}

              {/* Autocomplete Dropdown */}
              <AnimatePresence>
                {showAutocomplete && autocompleteResults.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full mt-2 w-full bg-white rounded-xl shadow-2xl border border-gray-200 z-50 overflow-hidden"
                  >
                    {autocompleteResults.map((result) => (
                      <button
                        key={result.id}
                        onClick={() => {
                          setQuery(result.name);
                          handleSearch(result.name);
                        }}
                        className="w-full px-4 py-3 text-left hover:bg-purple-50 transition-colors border-b border-gray-100 last:border-b-0"
                      >
                        <p className="font-medium">{result.name}</p>
                        {result.description && (
                          <p className="text-sm text-gray-600 truncate">{result.description}</p>
                        )}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <button
              onClick={() => handleSearch()}
              className="px-8 py-4 bg-linear-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all font-medium"
            >
              Search
            </button>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-6 py-4 rounded-xl transition-all font-medium flex items-center gap-2 ${
                showFilters
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-700 border-2 border-gray-200'
              }`}
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>
        </motion.div>

        {/* Popular Searches */}
        {!query && popularSearches.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-6"
          >
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold text-gray-700">Popular Searches</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              {popularSearches.map((search, index) => (
                <button
                  key={index}
                  onClick={() => handlePopularSearch(search)}
                  className="px-4 py-2 bg-white border border-gray-200 rounded-full hover:border-purple-500 hover:bg-purple-50 transition-all"
                >
                  {search}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Advanced Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 overflow-hidden"
            >
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Advanced Filters</h3>
                  <button
                    onClick={clearFilters}
                    className="text-sm text-purple-600 hover:text-purple-700"
                  >
                    Clear All
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {/* Project Type */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Project Type</label>
                    <select
                      value={filters.project_types?.[0] || ''}
                      onChange={(e) => setFilters({ ...filters, project_types: e.target.value ? [e.target.value] : undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    >
                      <option value="">All Types</option>
                      <option value="logo">Logo</option>
                      <option value="poster">Poster</option>
                      <option value="social_media">Social Media</option>
                      <option value="presentation">Presentation</option>
                    </select>
                  </div>

                  {/* Date From */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Date From</label>
                    <input
                      type="date"
                      value={filters.created_after || ''}
                      onChange={(e) => setFilters({ ...filters, created_after: e.target.value || undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    />
                  </div>

                  {/* Date To */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Date To</label>
                    <input
                      type="date"
                      value={filters.created_before || ''}
                      onChange={(e) => setFilters({ ...filters, created_before: e.target.value || undefined })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    />
                  </div>

                  {/* Canvas Width */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Min Width (px)</label>
                    <input
                      type="number"
                      value={filters.min_width || ''}
                      onChange={(e) => setFilters({ ...filters, min_width: e.target.value ? parseInt(e.target.value) : undefined })}
                      placeholder="e.g. 800"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Max Width (px)</label>
                    <input
                      type="number"
                      value={filters.max_width || ''}
                      onChange={(e) => setFilters({ ...filters, max_width: e.target.value ? parseInt(e.target.value) : undefined })}
                      placeholder="e.g. 1920"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    />
                  </div>

                  {/* Color Filter */}
                  <div>
                    <label className="block text-sm font-medium mb-2">Dominant Color</label>
                    <input
                      type="color"
                      value={filters.colors?.[0] || '#000000'}
                      onChange={(e) => setFilters({ ...filters, colors: e.target.value ? [e.target.value] : undefined })}
                      className="w-full h-10 px-2 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                    />
                  </div>

                  {/* Boolean Filters */}
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.has_ai_prompt || false}
                        onChange={(e) => setFilters({ ...filters, has_ai_prompt: e.target.checked || undefined })}
                        className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                      />
                      <span className="text-sm font-medium flex items-center gap-1">
                        <Wand2 className="w-4 h-4" />
                        AI Generated
                      </span>
                    </label>
                  </div>

                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.has_color_palette || false}
                        onChange={(e) => setFilters({ ...filters, has_color_palette: e.target.checked || undefined })}
                        className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                      />
                      <span className="text-sm font-medium">Has Color Palette</span>
                    </label>
                  </div>
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleAdvancedSearch}
                    className="flex-1 px-6 py-3 bg-linear-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition-all font-medium"
                  >
                    Apply Filters
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching...</p>
          </div>
        ) : results.length > 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {results.map((result, index) => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => router.push(`/editor?project=${result.id}`)}
                className="bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer hover:shadow-2xl transition-all group"
              >
                <div className="aspect-video bg-linear-to-br from-purple-100 to-blue-100 relative overflow-hidden">
                  {result.thumbnail ? (
                    <Image
                      src={result.thumbnail}
                      alt={result.name}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Palette className="w-16 h-16 text-purple-300" />
                    </div>
                  )}
                  {result.ai_generated && (
                    <div className="absolute top-3 right-3 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1">
                      <Wand2 className="w-3 h-3" />
                      AI
                    </div>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-lg mb-1 group-hover:text-purple-600 transition-colors">
                    {result.name}
                  </h3>
                  {result.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2">{result.description}</p>
                  )}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDate(result.updated_at)}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        ) : query || Object.values(filters).some(v => v !== undefined) ? (
          <div className="text-center py-16">
            <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No results found</h3>
            <p className="text-gray-600">Try adjusting your search or filters</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

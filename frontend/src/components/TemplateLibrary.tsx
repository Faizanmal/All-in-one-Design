/**
 * Template Library Component
 * Browse and use design templates
 */
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, Star, Heart, Download } from 'lucide-react';
import Image from 'next/image';

interface Template {
  id: number;
  name: string;
  description: string;
  category: string;
  thumbnail_url: string;
  is_premium: boolean;
  is_featured: boolean;
  use_count: number;
  favorite_count: number;
  rating: number;
  tags: string[];
  is_favorited: boolean; // Added this property
}

export default function TemplateLibrary() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showPremiumOnly, setShowPremiumOnly] = useState(false);
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const categories = [
    { value: 'all', label: 'All Templates' },
    { value: 'social_media', label: 'Social Media' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'branding', label: 'Branding' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'web', label: 'Web Design' },
    { value: 'mobile', label: 'Mobile App' },
    { value: 'print', label: 'Print Design' },
  ];

  useEffect(() => {
    fetchTemplates();
  }, []);

  // Memoize filterTemplates to prevent re-creation on every render
  const filterTemplates = useCallback(() => {
    let filtered = [...templates];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (t) =>
          t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          t.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter((t) => t.category === selectedCategory);
    }

    // Premium filter
    if (showPremiumOnly) {
      filtered = filtered.filter((t) => t.is_premium);
    }

    // Featured filter
    if (showFeaturedOnly) {
      filtered = filtered.filter((t) => t.is_featured);
    }

    setFilteredTemplates(filtered);
  }, [templates, searchQuery, selectedCategory, showPremiumOnly, showFeaturedOnly]);

  // This effect now correctly depends on the memoized filterTemplates function
  useEffect(() => {
    filterTemplates();
  }, [filterTemplates]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('/api/projects/templates/');
      const data = await response.json();
      setTemplates(data.results || []);
      // We no longer setFilteredTemplates here; the effect will do it.
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    } finally {
      setIsLoading(false);
    }
  };

  function handleUseTemplate(templateId: number, templateName: string) {
    (async () => {
      try {
        const projectName = prompt('Enter a name for your new project:', `${templateName} - Copy`);
        if (!projectName) return;

        const response = await fetch(`/api/projects/templates/${templateId}/use_template/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({ name: projectName }),
        });

        if (response.ok) {
          const data = await response.json();
          alert(`Project "${data.project_name}" created successfully!`);
          // Navigate to the project
          window.location.href = `/projects/${data.project_id}`;
        } else {
          alert('Failed to use template.');
        }
      } catch (error) {
        console.error('Failed to use template:', error);
        alert('Error using template.');
      }
    })();
  }

  const toggleFavorite = async (templateId: number, isFavorited: boolean) => {
    try {
      const endpoint = isFavorited ? 'unfavorite' : 'favorite';
      await fetch(`/api/projects/templates/${templateId}/${endpoint}/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      // Refresh templates to show updated favorite status
      fetchTemplates();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  // --- RETURN STATEMENT ---
  // All JSX for the component's UI must be inside the return statement.
  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Filter Bar Area - Added missing wrapper divs */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            
            {/* Search Bar */}
            <div className="flex-1 min-w-[300px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Category Filter */}
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>

            {/* Filter Toggles */}
            <label className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="checkbox"
                checked={showFeaturedOnly}
                onChange={(e) => setShowFeaturedOnly(e.target.checked)}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-sm text-gray-700">Featured Only</span>
            </label>

            <label className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="checkbox"
                checked={showPremiumOnly}
                onChange={(e) => setShowPremiumOnly(e.target.checked)}
                className="w-4 h-4 text-blue-600"
              />
              <span className="text-sm text-gray-700">Premium Only</span>
            </label>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : filteredTemplates.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No templates found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredTemplates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition group"
              >
                {/* Thumbnail */}
                <div className="relative aspect-video bg-gray-100">
                  {template.thumbnail_url ? (
                    <Image
                      src={template.thumbnail_url}
                      alt={template.name}
                      fill={true} // Use fill to respect aspect-video container
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No preview
                    </div>
                  )}

                  {/* Badges - Moved outside of the conditional to show on all cards */}
                  <div className="absolute top-2 left-2 flex gap-2">
                    {template.is_featured && (
                      <span className="px-2 py-1 bg-yellow-500 text-white text-xs font-semibold rounded">
                        Featured
                      </span>
                    )}
                    {template.is_premium && (
                      <span className="px-2 py-1 bg-purple-500 text-white text-xs font-semibold rounded">
                        Premium
                      </span>
                    )}
                  </div>

                  {/* Hover Actions */}
                  <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition flex items-center justify-center gap-2">
                    <button
                      onClick={() => handleUseTemplate(template.id, template.name)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Use Template
                    </button>
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 truncate">{template.name}</h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">{template.description}</p>

                  {/* Stats */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center gap-3 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                        <span>{template.rating.toFixed(1)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Download className="w-4 h-4" />
                        <span>{template.use_count}</span>
                      </div>
                    </div>
                    <button
                      // Corrected onClick to pass dynamic 'is_favorited' status
                      onClick={() => toggleFavorite(template.id, template.is_favorited)}
                      className="transition"
                    >
                      {/* Corrected Heart to show fill state */}
                      <Heart
                        className={`w-5 h-5 ${
                          template.is_favorited
                            ? 'fill-red-500 text-red-500'
                            : 'text-gray-400 hover:text-red-500'
                        }`}
                      />
                    </button>
                  </div>

                  {/* Tags */}
                  {template.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {template.tags.slice(0, 3).map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
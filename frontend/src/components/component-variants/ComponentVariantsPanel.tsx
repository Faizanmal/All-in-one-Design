'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Layers,
  Plus,
  Copy,
  Trash2,
  Edit2,
  ChevronDown,
  ChevronRight,
  Settings,
  Search,
  Grid,
  List,
  MoreHorizontal,
  Link2,
  Unlink,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  Play,
  Zap,
  Palette,
  Type,
  ToggleLeft,
  Hash,
  RefreshCw,
  ExternalLink,
  Check,
  X,
  AlertCircle,
  Star,
  Sparkles,
  Filter,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

// Types
interface PropertyValue {
  id: string;
  name: string;
  value: string | number | boolean;
}

interface ComponentProperty {
  id: string;
  name: string;
  type: 'variant' | 'boolean' | 'text' | 'instance_swap';
  values: PropertyValue[];
  defaultValue: string;
}

interface ComponentVariant {
  id: string;
  name: string;
  properties: Record<string, string>;
  thumbnail?: string;
  isDefault?: boolean;
}

interface ComponentSet {
  id: string;
  name: string;
  description?: string;
  properties: ComponentProperty[];
  variants: ComponentVariant[];
  instanceCount: number;
  lastModified: string;
}

interface ComponentInstance {
  id: string;
  componentSetId: string;
  variantId: string;
  overrides: Record<string, unknown>;
  name: string;
  location: string;
}

// Mock data
const mockComponentSet: ComponentSet = {
  id: 'cs-btn',
  name: 'Button',
  description: 'Primary button component with multiple variants',
  properties: [
    {
      id: 'prop-size',
      name: 'Size',
      type: 'variant',
      values: [
        { id: 'v-sm', name: 'Small', value: 'sm' },
        { id: 'v-md', name: 'Medium', value: 'md' },
        { id: 'v-lg', name: 'Large', value: 'lg' },
      ],
      defaultValue: 'md',
    },
    {
      id: 'prop-variant',
      name: 'Variant',
      type: 'variant',
      values: [
        { id: 'v-primary', name: 'Primary', value: 'primary' },
        { id: 'v-secondary', name: 'Secondary', value: 'secondary' },
        { id: 'v-outline', name: 'Outline', value: 'outline' },
        { id: 'v-ghost', name: 'Ghost', value: 'ghost' },
      ],
      defaultValue: 'primary',
    },
    {
      id: 'prop-state',
      name: 'State',
      type: 'variant',
      values: [
        { id: 's-default', name: 'Default', value: 'default' },
        { id: 's-hover', name: 'Hover', value: 'hover' },
        { id: 's-pressed', name: 'Pressed', value: 'pressed' },
        { id: 's-disabled', name: 'Disabled', value: 'disabled' },
      ],
      defaultValue: 'default',
    },
    {
      id: 'prop-icon',
      name: 'Show Icon',
      type: 'boolean',
      values: [
        { id: 'b-true', name: 'True', value: true },
        { id: 'b-false', name: 'False', value: false },
      ],
      defaultValue: 'false',
    },
    {
      id: 'prop-label',
      name: 'Label',
      type: 'text',
      values: [],
      defaultValue: 'Button',
    },
  ],
  variants: [
    { id: 'var-1', name: 'Size=Small, Variant=Primary, State=Default', properties: { Size: 'sm', Variant: 'primary', State: 'default' }, isDefault: true },
    { id: 'var-2', name: 'Size=Medium, Variant=Primary, State=Default', properties: { Size: 'md', Variant: 'primary', State: 'default' } },
    { id: 'var-3', name: 'Size=Large, Variant=Primary, State=Default', properties: { Size: 'lg', Variant: 'primary', State: 'default' } },
    { id: 'var-4', name: 'Size=Medium, Variant=Secondary, State=Default', properties: { Size: 'md', Variant: 'secondary', State: 'default' } },
    { id: 'var-5', name: 'Size=Medium, Variant=Outline, State=Default', properties: { Size: 'md', Variant: 'outline', State: 'default' } },
    { id: 'var-6', name: 'Size=Medium, Variant=Ghost, State=Default', properties: { Size: 'md', Variant: 'ghost', State: 'default' } },
  ],
  instanceCount: 156,
  lastModified: '2024-01-15T14:30:00Z',
};

const mockInstances: ComponentInstance[] = [
  { id: 'inst-1', componentSetId: 'cs-btn', variantId: 'var-2', overrides: {}, name: 'Submit Button', location: 'Login Form' },
  { id: 'inst-2', componentSetId: 'cs-btn', variantId: 'var-4', overrides: { Label: 'Cancel' }, name: 'Cancel Button', location: 'Login Form' },
  { id: 'inst-3', componentSetId: 'cs-btn', variantId: 'var-2', overrides: {}, name: 'Save Button', location: 'Settings Page' },
];

// Helper components
const PropertyIcon: React.FC<{ type: ComponentProperty['type'] }> = ({ type }) => {
  const icons = {
    variant: Layers,
    boolean: ToggleLeft,
    text: Type,
    instance_swap: Link2,
  };
  const Icon = icons[type];
  return <Icon size={12} className="text-gray-400" />;
};

const VariantPreview: React.FC<{ variant: ComponentVariant }> = ({ variant }) => {
  // Get variant styles based on properties
  const getStyles = () => {
    const { Size, Variant } = variant.properties;
    
    const sizeClasses = {
      sm: 'px-2 py-1 text-xs',
      md: 'px-3 py-1.5 text-sm',
      lg: 'px-4 py-2 text-base',
    }[Size as string] || 'px-3 py-1.5 text-sm';

    const variantClasses = {
      primary: 'bg-blue-500 text-white',
      secondary: 'bg-gray-600 text-white',
      outline: 'bg-transparent border border-blue-500 text-blue-500',
      ghost: 'bg-transparent text-blue-500 hover:bg-blue-500/10',
    }[Variant as string] || 'bg-blue-500 text-white';

    return `${sizeClasses} ${variantClasses} rounded-lg font-medium`;
  };

  return (
    <div className="flex items-center justify-center p-4 bg-gray-950 rounded-lg">
      <button className={getStyles()}>Button</button>
    </div>
  );
};

// Property Editor Component
interface PropertyEditorProps {
  property: ComponentProperty;
  value: string;
  onChange: (value: string) => void;
}

const PropertyEditor: React.FC<PropertyEditorProps> = ({ property, value, onChange }) => {
  switch (property.type) {
    case 'boolean':
      return (
        <button
          onClick={() => onChange(value === 'true' ? 'false' : 'true')}
          className={`relative w-10 h-5 rounded-full transition-colors ${
            value === 'true' ? 'bg-blue-500' : 'bg-gray-600'
          }`}
        >
          <span
            className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
              value === 'true' ? 'translate-x-5' : 'translate-x-0.5'
            }`}
          />
        </button>
      );

    case 'text':
      return (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded text-white"
        />
      );

    case 'variant':
    case 'instance_swap':
    default:
      return (
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded text-white"
        >
          {property.values.map((v) => (
            <option key={v.id} value={String(v.value)}>
              {v.name}
            </option>
          ))}
        </select>
      );
  }
};

// Variant Matrix Component
interface VariantMatrixProps {
  componentSet: ComponentSet;
  onSelectVariant: (variantId: string) => void;
  selectedVariantId?: string;
}

const VariantMatrix: React.FC<VariantMatrixProps> = ({
  componentSet,
  onSelectVariant,
  selectedVariantId,
}) => {
  // Get primary properties (first two variant types)
  const variantProps = componentSet.properties.filter((p) => p.type === 'variant');
  const rowProp = variantProps[0];
  const colProp = variantProps[1];

  if (!rowProp || !colProp) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p className="text-sm">Need at least 2 variant properties for matrix view</p>
      </div>
    );
  }

  return (
    <div className="overflow-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="p-2 text-xs text-gray-500 font-normal text-left border-b border-gray-700">
              {rowProp.name} / {colProp.name}
            </th>
            {colProp.values.map((col) => (
              <th
                key={col.id}
                className="p-2 text-xs text-gray-400 font-medium text-center border-b border-gray-700"
              >
                {col.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rowProp.values.map((row) => (
            <tr key={row.id}>
              <td className="p-2 text-xs text-gray-400 font-medium border-b border-gray-700/50">
                {row.name}
              </td>
              {colProp.values.map((col) => {
                const variant = componentSet.variants.find(
                  (v) =>
                    v.properties[rowProp.name] === row.value &&
                    v.properties[colProp.name] === col.value
                );
                
                return (
                  <td
                    key={col.id}
                    className="p-2 border-b border-gray-700/50"
                  >
                    {variant ? (
                      <button
                        onClick={() => onSelectVariant(variant.id)}
                        className={`w-full p-2 rounded-lg transition-all ${
                          selectedVariantId === variant.id
                            ? 'ring-2 ring-blue-500 bg-blue-500/10'
                            : 'bg-gray-800 hover:bg-gray-750'
                        }`}
                      >
                        <VariantPreview variant={variant} />
                      </button>
                    ) : (
                      <div className="flex items-center justify-center p-4 bg-gray-800/50 rounded-lg border border-dashed border-gray-700">
                        <button
                          className="text-xs text-gray-500 hover:text-gray-300 flex items-center gap-1"
                        >
                          <Plus size={12} />
                          Add
                        </button>
                      </div>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Main Component
interface ComponentVariantsPanelProps {
  componentSet?: ComponentSet;
  instances?: ComponentInstance[];
  onUpdateProperty?: (propertyId: string, updates: Partial<ComponentProperty>) => void;
  onAddVariant?: () => void;
  onDeleteVariant?: (variantId: string) => void;
  onSelectInstance?: (instanceId: string) => void;
}

export const ComponentVariantsPanel: React.FC<ComponentVariantsPanelProps> = ({
  componentSet = mockComponentSet,
  instances = mockInstances,
  onUpdateProperty,
  onAddVariant,
  onDeleteVariant,
  onSelectInstance,
}) => {
  const [activeTab, setActiveTab] = useState<'properties' | 'variants' | 'instances'>('properties');
  const [viewMode, setViewMode] = useState<'grid' | 'matrix'>('grid');
  const [selectedVariantId, setSelectedVariantId] = useState<string | undefined>(componentSet.variants[0]?.id);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedProps, setExpandedProps] = useState<Set<string>>(new Set(componentSet.properties.map(p => p.id)));

  // Selected variant
  const selectedVariant = useMemo(
    () => componentSet.variants.find((v) => v.id === selectedVariantId),
    [componentSet.variants, selectedVariantId]
  );

  // Filtered instances
  const filteredInstances = useMemo(() => {
    if (!searchQuery) return instances;
    return instances.filter(
      (inst) =>
        inst.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        inst.location.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [instances, searchQuery]);

  // Handlers
  const handleToggleProp = useCallback((propId: string) => {
    setExpandedProps((prev) => {
      const next = new Set(prev);
      if (next.has(propId)) {
        next.delete(propId);
      } else {
        next.add(propId);
      }
      return next;
    });
  }, []);

  return (
    <TooltipProvider>
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Box size={18} className="text-purple-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">{componentSet.name}</h3>
            <p className="text-xs text-gray-500">
              {componentSet.variants.length} variants • {componentSet.instanceCount} instances
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={onAddVariant}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                <Plus size={14} />
                Add Variant
              </button>
            </TooltipTrigger>
            <TooltipContent>Create a new variant combination</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                <Settings size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent>Component settings</TooltipContent>
          </Tooltip>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        <button
          onClick={() => setActiveTab('properties')}
          className={`flex-1 px-4 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === 'properties'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Properties
          <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
            {componentSet.properties.length}
          </Badge>
        </button>
        <button
          onClick={() => setActiveTab('variants')}
          className={`flex-1 px-4 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === 'variants'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Variants
          <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
            {componentSet.variants.length}
          </Badge>
        </button>
        <button
          onClick={() => setActiveTab('instances')}
          className={`flex-1 px-4 py-2 text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
            activeTab === 'instances'
              ? 'text-purple-400 border-b-2 border-purple-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Instances
          <Badge variant="secondary" className="text-[9px] px-1 py-0 h-4">
            {instances.length}
          </Badge>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden flex">
        {activeTab === 'properties' && (
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {componentSet.properties.map((prop) => (
              <div
                key={prop.id}
                className="bg-gray-800/50 rounded-lg border border-gray-700/50"
              >
                <button
                  onClick={() => handleToggleProp(prop.id)}
                  className="w-full flex items-center gap-2 px-3 py-2 hover:bg-gray-800"
                >
                  {expandedProps.has(prop.id) ? (
                    <ChevronDown size={14} className="text-gray-400" />
                  ) : (
                    <ChevronRight size={14} className="text-gray-400" />
                  )}
                  <PropertyIcon type={prop.type} />
                  <span className="text-sm font-medium text-white">{prop.name}</span>
                  <span className="text-xs text-gray-500 capitalize">{prop.type.replace('_', ' ')}</span>
                  <span className="text-xs text-gray-600 ml-auto">
                    {prop.values.length > 0 ? `${prop.values.length} values` : prop.defaultValue}
                  </span>
                </button>

                {expandedProps.has(prop.id) && (
                  <div className="px-3 pb-3 space-y-2">
                    {prop.type === 'variant' && (
                      <div className="space-y-1">
                        {prop.values.map((value, index) => (
                          <div
                            key={value.id}
                            className="flex items-center gap-2 px-2 py-1.5 bg-gray-900 rounded"
                          >
                            <span className="text-xs text-gray-500 w-4">{index + 1}</span>
                            <input
                              type="text"
                              value={value.name}
                              className="flex-1 bg-transparent text-sm text-white outline-none"
                              readOnly
                            />
                            <button className="p-0.5 text-gray-500 hover:text-white">
                              <Edit2 size={10} />
                            </button>
                            <button className="p-0.5 text-gray-500 hover:text-red-400">
                              <Trash2 size={10} />
                            </button>
                          </div>
                        ))}
                        <button className="w-full py-1.5 text-xs text-gray-500 hover:text-white border border-dashed border-gray-700 rounded hover:border-gray-600">
                          + Add Value
                        </button>
                      </div>
                    )}

                    {prop.type === 'boolean' && (
                      <div className="flex items-center gap-4 px-2 py-1">
                        <span className="text-xs text-gray-400">Default:</span>
                        <button
                          className={`relative w-10 h-5 rounded-full transition-colors ${
                            prop.defaultValue === 'true' ? 'bg-purple-500' : 'bg-gray-600'
                          }`}
                        >
                          <span
                            className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
                              prop.defaultValue === 'true' ? 'translate-x-5' : 'translate-x-0.5'
                            }`}
                          />
                        </button>
                      </div>
                    )}

                    {prop.type === 'text' && (
                      <div className="px-2 py-1">
                        <label className="text-xs text-gray-400 block mb-1">Default Value</label>
                        <input
                          type="text"
                          value={prop.defaultValue}
                          className="w-full px-2 py-1 text-sm bg-gray-900 border border-gray-700 rounded text-white"
                        />
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}

            <button className="w-full py-2 text-sm text-gray-500 hover:text-white border border-dashed border-gray-700 rounded-lg hover:border-gray-600 flex items-center justify-center gap-2 transition-colors">
              <Plus size={14} />
              Add Property
            </button>
            <button className="w-full py-2 text-sm text-gray-500 hover:text-purple-400 border border-dashed border-gray-700 rounded-lg hover:border-purple-500/40 flex items-center justify-center gap-2 transition-colors">
              <Sparkles size={14} />
              AI Suggest Properties
            </button>
          </div>
        )}

        {activeTab === 'variants' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* View mode toggle */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
              <span className="text-xs text-gray-400">
                {componentSet.variants.length} variants
              </span>
              <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-0.5">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-1.5 rounded ${
                        viewMode === 'grid' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      <Grid size={14} />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Grid view</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <button
                      onClick={() => setViewMode('matrix')}
                      className={`p-1.5 rounded ${
                        viewMode === 'matrix' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      <Layers size={14} />
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>Matrix view</TooltipContent>
                </Tooltip>
              </div>
            </div>

            {/* Variants view */}
            <div className="flex-1 overflow-auto p-4">
              {viewMode === 'matrix' ? (
                <VariantMatrix
                  componentSet={componentSet}
                  onSelectVariant={setSelectedVariantId}
                  selectedVariantId={selectedVariantId}
                />
              ) : (
                <div className="grid grid-cols-2 gap-3">
                  {componentSet.variants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariantId(variant.id)}
                      className={`p-3 rounded-lg border transition-all ${
                        selectedVariantId === variant.id
                          ? 'border-purple-500 ring-2 ring-purple-500/30 bg-purple-500/10'
                          : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                      }`}
                    >
                      <VariantPreview variant={variant} />
                      <div className="mt-2 text-left">
                        <p className="text-xs text-gray-300 truncate">
                          {Object.entries(variant.properties)
                            .map(([k, v]) => `${k}=${v}`)
                            .join(', ')}
                        </p>
                        {variant.isDefault && (
                          <Badge className="mt-1 text-[9px] px-1 py-0 h-4 bg-purple-500/20 text-purple-400 border-purple-500/30">
                            <Star size={8} className="mr-0.5" />
                            Default
                          </Badge>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'instances' && (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Search */}
            <div className="px-4 py-2 border-b border-gray-700">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search instances..."
                  className="w-full pl-9 pr-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>

            {/* Instances list */}
            <div className="flex-1 overflow-y-auto">
              {filteredInstances.map((instance) => (
                <button
                  key={instance.id}
                  onClick={() => onSelectInstance?.(instance.id)}
                  className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-800 border-b border-gray-700/50 text-left"
                >
                  <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center">
                    <Box size={14} className="text-purple-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{instance.name}</p>
                    <p className="text-xs text-gray-500 truncate">{instance.location}</p>
                  </div>
                  {Object.keys(instance.overrides).length > 0 && (
                    <span className="flex items-center gap-1 text-xs text-yellow-500">
                      <AlertCircle size={10} />
                      Overrides
                    </span>
                  )}
                  <ExternalLink size={14} className="text-gray-500" />
                </button>
              ))}

              {filteredInstances.length === 0 && (
                <div className="flex flex-col items-center justify-center h-48 text-gray-500 px-6 text-center">
                  <Box size={36} className="mb-3 opacity-30" />
                  <p className="text-sm font-medium text-gray-400 mb-1">
                    {searchQuery ? 'No matching instances' : 'No instances yet'}
                  </p>
                  <p className="text-xs text-gray-600">
                    {searchQuery
                      ? 'Try a different search term'
                      : 'Use this component in your designs to see instances here'}
                  </p>
                </div>
              )}
            </div>

            {/* Stats footer */}
            <div className="px-4 py-2 bg-gray-850 border-t border-gray-700 text-xs text-gray-500 flex items-center justify-between">
              <span>{filteredInstances.length} instances</span>
              <span>
                {filteredInstances.filter((i) => Object.keys(i.overrides).length > 0).length} with overrides
              </span>
            </div>
          </div>
        )}

        {/* Selected variant sidebar */}
        {activeTab === 'variants' && selectedVariant && (
          <div className="w-64 bg-gray-850 border-l border-gray-700 p-4 space-y-4 overflow-y-auto">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium text-white">Properties</h4>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
                    <MoreHorizontal size={14} />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-44">
                  <DropdownMenuItem onClick={onAddVariant} className="gap-2">
                    <Copy size={14} />Duplicate Variant
                  </DropdownMenuItem>
                  <DropdownMenuItem className="gap-2">
                    <Star size={14} />Set as Default
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => onDeleteVariant?.(selectedVariant!.id)}
                    className="gap-2 text-red-400 focus:text-red-400"
                  >
                    <Trash2 size={14} />Delete Variant
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            <VariantPreview variant={selectedVariant} />

            <div className="space-y-3">
              {componentSet.properties.map((prop) => (
                <div key={prop.id}>
                  <label className="text-xs text-gray-400 block mb-1">{prop.name}</label>
                  <PropertyEditor
                    property={prop}
                    value={selectedVariant.properties[prop.name] || prop.defaultValue}
                    onChange={() => {}}
                  />
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-gray-700 space-y-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <button className="w-full py-1.5 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600 flex items-center justify-center gap-1 transition-colors">
                    <Copy size={12} />
                    Duplicate Variant
                  </button>
                </TooltipTrigger>
                <TooltipContent>Create a copy of this variant</TooltipContent>
              </Tooltip>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    onClick={() => onDeleteVariant?.(selectedVariant.id)}
                    className="w-full py-1.5 text-xs bg-red-900/20 text-red-400 rounded hover:bg-red-900/30 flex items-center justify-center gap-1 transition-colors"
                  >
                    <Trash2 size={12} />
                    Delete Variant
                  </button>
                </TooltipTrigger>
                <TooltipContent>Permanently remove this variant</TooltipContent>
              </Tooltip>
            </div>
          </div>
        )}
      </div>
    </div>
    </TooltipProvider>
  );
};

export default ComponentVariantsPanel;

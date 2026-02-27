/**
 * Component Variants API Client
 * Production-ready API for Component Variants & Properties feature
 */
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/variants`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Types
export type PropertyType = 'boolean' | 'text' | 'instance_swap' | 'variant' | 'number' | 'color';

export interface PropertyOption {
  id: string;
  property: string;
  value: string;
  label: string;
  order: number;
  preview_data: Record<string, unknown>;
}

export interface ComponentProperty {
  id: string;
  component_set: string;
  name: string;
  property_type: PropertyType;
  default_value: string;
  options: PropertyOption[];
  is_required: boolean;
  description: string;
  order: number;
  validation_rules: Record<string, unknown>;
  affects_layout: boolean;
  created_at: string;
  updated_at: string;
}

export interface ComponentVariant {
  id: string;
  component_set: string;
  name: string;
  description: string;
  property_values: Record<string, string>;
  node_id: string;
  thumbnail_url: string | null;
  is_default: boolean;
  is_deprecated: boolean;
  deprecation_message: string;
  order: number;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface ComponentSet {
  id: string;
  project: number;
  name: string;
  description: string;
  node_id: string;
  properties: ComponentProperty[];
  variants: ComponentVariant[];
  default_variant: string | null;
  category: string;
  tags: string[];
  thumbnail_url: string | null;
  documentation_url: string;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

export interface ComponentInstance {
  id: string;
  main_component: string;
  current_variant: string | null;
  node_id: string;
  property_overrides: Record<string, string>;
  is_detached: boolean;
  nested_instances: string[];
  created_at: string;
  updated_at: string;
}

export interface VariantOverride {
  id: string;
  instance: string;
  property: string;
  original_value: string;
  override_value: string;
  is_reset: boolean;
}

export interface ComponentSlot {
  id: string;
  component_set: string;
  name: string;
  slot_type: 'single' | 'multiple';
  allowed_types: string[];
  default_content: Record<string, unknown>;
  is_required: boolean;
  description: string;
}

export interface InteractiveState {
  id: string;
  component_set: string;
  name: string;
  state_type: 'hover' | 'pressed' | 'focused' | 'disabled' | 'selected' | 'loading' | 'error' | 'custom';
  style_overrides: Record<string, unknown>;
  property_changes: Record<string, string>;
  transition_duration: number;
  easing_function: string;
  is_enabled: boolean;
}

export interface VariantMatrix {
  properties: string[];
  combinations: Array<{
    values: Record<string, string>;
    variant: ComponentVariant | null;
    exists: boolean;
  }>;
  coverage: number;
}

export interface VariantSuggestion {
  id: string;
  name: string;
  property_values: Record<string, string>;
  reason: string;
  confidence: number;
}

// API Functions
export const componentVariantsApi = {
  // Component Set operations
  async getComponentSets(projectId: number, options?: {
    category?: string;
    search?: string;
  }): Promise<ComponentSet[]> {
    const params = new URLSearchParams();
    params.append('project', String(projectId));
    if (options?.category) params.append('category', options.category);
    if (options?.search) params.append('search', options.search);
    const { data } = await apiClient.get(`/component-sets/?${params}`);
    return data.results || data;
  },

  async getComponentSet(setId: string): Promise<ComponentSet> {
    const { data } = await apiClient.get(`/component-sets/${setId}/`);
    return data;
  },

  async createComponentSet(componentSet: Partial<ComponentSet>): Promise<ComponentSet> {
    const { data } = await apiClient.post('/component-sets/', componentSet);
    return data;
  },

  async updateComponentSet(setId: string, updates: Partial<ComponentSet>): Promise<ComponentSet> {
    const { data } = await apiClient.patch(`/component-sets/${setId}/`, updates);
    return data;
  },

  async deleteComponentSet(setId: string): Promise<void> {
    await apiClient.delete(`/component-sets/${setId}/`);
  },

  async getVariantMatrix(setId: string): Promise<VariantMatrix> {
    const { data } = await apiClient.get(`/component-sets/${setId}/variant_matrix/`);
    return data;
  },

  async generateMissingVariants(setId: string): Promise<ComponentVariant[]> {
    const { data } = await apiClient.post(`/component-sets/${setId}/generate_missing_variants/`);
    return data.variants;
  },

  async duplicateComponentSet(setId: string, name?: string): Promise<ComponentSet> {
    const { data } = await apiClient.post(`/component-sets/${setId}/duplicate/`, { name });
    return data;
  },

  async exportAsLibrary(setId: string): Promise<{ download_url: string }> {
    const { data } = await apiClient.post(`/component-sets/${setId}/export_library/`);
    return data;
  },

  async getUsageStats(setId: string): Promise<{
    total_instances: number;
    instances_by_file: Record<string, number>;
    variant_usage: Record<string, number>;
    property_usage: Record<string, Record<string, number>>;
  }> {
    const { data } = await apiClient.get(`/component-sets/${setId}/usage_stats/`);
    return data;
  },

  // Property operations
  async getProperties(setId: string): Promise<ComponentProperty[]> {
    const { data } = await apiClient.get(`/properties/?component_set=${setId}`);
    return data.results || data;
  },

  async createProperty(property: Partial<ComponentProperty>): Promise<ComponentProperty> {
    const { data } = await apiClient.post('/properties/', property);
    return data;
  },

  async updateProperty(propertyId: string, updates: Partial<ComponentProperty>): Promise<ComponentProperty> {
    const { data } = await apiClient.patch(`/properties/${propertyId}/`, updates);
    return data;
  },

  async deleteProperty(propertyId: string): Promise<void> {
    await apiClient.delete(`/properties/${propertyId}/`);
  },

  async reorderProperties(setId: string, propertyIds: string[]): Promise<void> {
    await apiClient.post('/properties/reorder/', {
      component_set: setId,
      property_ids: propertyIds,
    });
  },

  async addPropertyOption(propertyId: string, option: Partial<PropertyOption>): Promise<PropertyOption> {
    const { data } = await apiClient.post(`/properties/${propertyId}/add_option/`, option);
    return data;
  },

  async removePropertyOption(propertyId: string, optionId: string): Promise<void> {
    await apiClient.post(`/properties/${propertyId}/remove_option/`, { option_id: optionId });
  },

  // Variant operations
  async getVariants(setId: string): Promise<ComponentVariant[]> {
    const { data } = await apiClient.get(`/variants/?component_set=${setId}`);
    return data.results || data;
  },

  async getVariant(variantId: string): Promise<ComponentVariant> {
    const { data } = await apiClient.get(`/variants/${variantId}/`);
    return data;
  },

  async createVariant(variant: Partial<ComponentVariant>): Promise<ComponentVariant> {
    const { data } = await apiClient.post('/variants/', variant);
    return data;
  },

  async updateVariant(variantId: string, updates: Partial<ComponentVariant>): Promise<ComponentVariant> {
    const { data } = await apiClient.patch(`/variants/${variantId}/`, updates);
    return data;
  },

  async deleteVariant(variantId: string): Promise<void> {
    await apiClient.delete(`/variants/${variantId}/`);
  },

  async setAsDefault(variantId: string): Promise<ComponentVariant> {
    const { data } = await apiClient.post(`/variants/${variantId}/set_default/`);
    return data;
  },

  async deprecateVariant(variantId: string, message: string): Promise<ComponentVariant> {
    const { data } = await apiClient.post(`/variants/${variantId}/deprecate/`, { message });
    return data;
  },

  async undeprecateVariant(variantId: string): Promise<ComponentVariant> {
    const { data } = await apiClient.post(`/variants/${variantId}/undeprecate/`);
    return data;
  },

  async duplicateVariant(variantId: string, name?: string): Promise<ComponentVariant> {
    const { data } = await apiClient.post(`/variants/${variantId}/duplicate/`, { name });
    return data;
  },

  async swapVariants(variantId1: string, variantId2: string): Promise<void> {
    await apiClient.post('/variants/swap/', {
      variant_1: variantId1,
      variant_2: variantId2,
    });
  },

  // Instance operations
  async getInstances(componentSetId: string): Promise<ComponentInstance[]> {
    const { data } = await apiClient.get(`/instances/?main_component=${componentSetId}`);
    return data.results || data;
  },

  async getInstance(instanceId: string): Promise<ComponentInstance> {
    const { data } = await apiClient.get(`/instances/${instanceId}/`);
    return data;
  },

  async createInstance(instance: Partial<ComponentInstance>): Promise<ComponentInstance> {
    const { data } = await apiClient.post('/instances/', instance);
    return data;
  },

  async updateInstance(instanceId: string, updates: Partial<ComponentInstance>): Promise<ComponentInstance> {
    const { data } = await apiClient.patch(`/instances/${instanceId}/`, updates);
    return data;
  },

  async resetOverrides(instanceId: string): Promise<ComponentInstance> {
    const { data } = await apiClient.post(`/instances/${instanceId}/reset_overrides/`);
    return data;
  },

  async detachInstance(instanceId: string): Promise<{ detached_node_id: string }> {
    const { data } = await apiClient.post(`/instances/${instanceId}/detach/`);
    return data;
  },

  async swapComponent(instanceId: string, newComponentSetId: string): Promise<ComponentInstance> {
    const { data } = await apiClient.post(`/instances/${instanceId}/swap_component/`, {
      new_component_set: newComponentSetId,
    });
    return data;
  },

  async pushOverridesToMain(instanceId: string, overrideKeys: string[]): Promise<void> {
    await apiClient.post(`/instances/${instanceId}/push_to_main/`, {
      override_keys: overrideKeys,
    });
  },

  async findAndReplace(projectId: number, sourceVariant: string, targetVariant: string): Promise<{
    replaced_count: number;
    instances: string[];
  }> {
    const { data } = await apiClient.post('/instances/find_replace/', {
      project_id: projectId,
      source_variant: sourceVariant,
      target_variant: targetVariant,
    });
    return data;
  },

  // Override operations
  async getOverrides(instanceId: string): Promise<VariantOverride[]> {
    const { data } = await apiClient.get(`/overrides/?instance=${instanceId}`);
    return data.results || data;
  },

  async createOverride(override: Partial<VariantOverride>): Promise<VariantOverride> {
    const { data } = await apiClient.post('/overrides/', override);
    return data;
  },

  async deleteOverride(overrideId: string): Promise<void> {
    await apiClient.delete(`/overrides/${overrideId}/`);
  },

  // Slot operations
  async getSlots(setId: string): Promise<ComponentSlot[]> {
    const { data } = await apiClient.get(`/slots/?component_set=${setId}`);
    return data.results || data;
  },

  async createSlot(slot: Partial<ComponentSlot>): Promise<ComponentSlot> {
    const { data } = await apiClient.post('/slots/', slot);
    return data;
  },

  async updateSlot(slotId: string, updates: Partial<ComponentSlot>): Promise<ComponentSlot> {
    const { data } = await apiClient.patch(`/slots/${slotId}/`, updates);
    return data;
  },

  async deleteSlot(slotId: string): Promise<void> {
    await apiClient.delete(`/slots/${slotId}/`);
  },

  // Interactive State operations
  async getInteractiveStates(setId: string): Promise<InteractiveState[]> {
    const { data } = await apiClient.get(`/states/?component_set=${setId}`);
    return data.results || data;
  },

  async createInteractiveState(state: Partial<InteractiveState>): Promise<InteractiveState> {
    const { data } = await apiClient.post('/states/', state);
    return data;
  },

  async updateInteractiveState(stateId: string, updates: Partial<InteractiveState>): Promise<InteractiveState> {
    const { data } = await apiClient.patch(`/states/${stateId}/`, updates);
    return data;
  },

  async deleteInteractiveState(stateId: string): Promise<void> {
    await apiClient.delete(`/states/${stateId}/`);
  },

  async toggleState(stateId: string): Promise<InteractiveState> {
    const { data } = await apiClient.post(`/states/${stateId}/toggle/`);
    return data;
  },

  async previewState(stateId: string): Promise<{ preview_url: string }> {
    const { data } = await apiClient.get(`/states/${stateId}/preview/`);
    return data;
  },

  // AI suggestions
  async suggestVariants(setId: string): Promise<VariantSuggestion[]> {
    const { data } = await apiClient.post(`/component-sets/${setId}/suggest_variants/`);
    return data.suggestions;
  },

  async suggestProperties(setId: string): Promise<Array<{
    name: string;
    type: PropertyType;
    reason: string;
  }>> {
    const { data } = await apiClient.post(`/component-sets/${setId}/suggest_properties/`);
    return data.suggestions;
  },
};

export default componentVariantsApi;

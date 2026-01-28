import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/interactive';

interface ComponentState {
  id: string;
  name: string;
  is_default: boolean;
  properties: Record<string, unknown>;
}

interface Interaction {
  id: string;
  trigger: string;
  action: string;
  target?: string;
  delay?: number;
  options?: Record<string, unknown>;
}

interface InteractiveComponent {
  id: string;
  name: string;
  component_type: string;
  states: ComponentState[];
  interactions: Interaction[];
  variables: Array<{ name: string; type: string; default_value: unknown }>;
  description?: string;
}

interface ComponentInstance {
  id: string;
  component: string;
  current_state: string;
  variable_values: Record<string, unknown>;
}

export function useInteractiveComponents(projectId?: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [components, setComponents] = useState<InteractiveComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<InteractiveComponent | null>(null);

  const fetchComponents = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/components/?project=${projectId}`);
      if (response.ok) {
        const data = await response.json();
        setComponents(data.results || data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const createComponent = useCallback(async (
    name: string,
    componentType: string,
    description?: string
  ): Promise<InteractiveComponent> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/components/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          name,
          component_type: componentType,
          description
        })
      });
      if (!response.ok) throw new Error('Failed to create component');
      const component = await response.json();
      setComponents(prev => [...prev, component]);
      return component;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const updateComponent = useCallback(async (
    componentId: string,
    updates: Partial<InteractiveComponent>
  ): Promise<InteractiveComponent> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update component');
      const component = await response.json();
      setComponents(prev => prev.map(c => c.id === componentId ? component : c));
      return component;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const deleteComponent = useCallback(async (componentId: string) => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete component');
      setComponents(prev => prev.filter(c => c.id !== componentId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const addState = useCallback(async (
    componentId: string,
    stateName: string,
    properties: Record<string, unknown>,
    isDefault: boolean = false
  ): Promise<ComponentState> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/states/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: stateName,
          properties,
          is_default: isDefault
        })
      });
      if (!response.ok) throw new Error('Failed to add state');
      const state = await response.json();
      setComponents(prev => prev.map(c => 
        c.id === componentId 
          ? { ...c, states: [...c.states, state] }
          : c
      ));
      return state;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const updateState = useCallback(async (
    componentId: string,
    stateId: string,
    updates: Partial<ComponentState>
  ): Promise<ComponentState> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/states/${stateId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update state');
      const state = await response.json();
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, states: c.states.map(s => s.id === stateId ? state : s) }
          : c
      ));
      return state;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const deleteState = useCallback(async (componentId: string, stateId: string) => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/states/${stateId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete state');
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, states: c.states.filter(s => s.id !== stateId) }
          : c
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const addInteraction = useCallback(async (
    componentId: string,
    trigger: string,
    action: string,
    options?: {
      target?: string;
      delay?: number;
      options?: Record<string, unknown>;
    }
  ): Promise<Interaction> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/interactions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trigger, action, ...options })
      });
      if (!response.ok) throw new Error('Failed to add interaction');
      const interaction = await response.json();
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, interactions: [...c.interactions, interaction] }
          : c
      ));
      return interaction;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const updateInteraction = useCallback(async (
    componentId: string,
    interactionId: string,
    updates: Partial<Interaction>
  ): Promise<Interaction> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/interactions/${interactionId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update interaction');
      const interaction = await response.json();
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, interactions: c.interactions.map(i => i.id === interactionId ? interaction : i) }
          : c
      ));
      return interaction;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const deleteInteraction = useCallback(async (componentId: string, interactionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/interactions/${interactionId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete interaction');
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, interactions: c.interactions.filter(i => i.id !== interactionId) }
          : c
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const addVariable = useCallback(async (
    componentId: string,
    name: string,
    variableType: string,
    defaultValue: unknown
  ) => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/variables/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          variable_type: variableType,
          default_value: defaultValue
        })
      });
      if (!response.ok) throw new Error('Failed to add variable');
      const variable = await response.json();
      setComponents(prev => prev.map(c =>
        c.id === componentId
          ? { ...c, variables: [...c.variables, variable] }
          : c
      ));
      return variable;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const previewComponent = useCallback(async (
    componentId: string,
    stateId: string,
    variableOverrides?: Record<string, unknown>
  ) => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/preview/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          state_id: stateId,
          variable_overrides: variableOverrides
        })
      });
      if (!response.ok) throw new Error('Preview failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const duplicateComponent = useCallback(async (
    componentId: string,
    newName?: string
  ): Promise<InteractiveComponent> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/duplicate/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName })
      });
      if (!response.ok) throw new Error('Failed to duplicate component');
      const component = await response.json();
      setComponents(prev => [...prev, component]);
      return component;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const exportComponent = useCallback(async (
    componentId: string,
    format: 'json' | 'html' | 'react' = 'json'
  ): Promise<string> => {
    try {
      const response = await fetch(`${API_BASE}/components/${componentId}/export/?format=${format}`);
      if (!response.ok) throw new Error('Export failed');
      const result = await response.json();
      return result.content;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  useEffect(() => {
    if (projectId) {
      fetchComponents();
    }
  }, [projectId, fetchComponents]);

  return {
    isLoading,
    error,
    components,
    selectedComponent,
    setSelectedComponent,
    createComponent,
    updateComponent,
    deleteComponent,
    addState,
    updateState,
    deleteState,
    addInteraction,
    updateInteraction,
    deleteInteraction,
    addVariable,
    previewComponent,
    duplicateComponent,
    exportComponent,
    refresh: fetchComponents
  };
}

export default useInteractiveComponents;

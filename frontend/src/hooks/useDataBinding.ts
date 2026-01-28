import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/data-binding';

interface DataSource {
  id: string;
  name: string;
  source_type: string;
  url?: string;
  schema?: Record<string, string>;
  is_connected: boolean;
  last_sync?: string;
}

interface DataVariable {
  id: string;
  name: string;
  value: unknown;
  variable_type: string;
  source?: string;
  path?: string;
}

interface DataBinding {
  id: string;
  element_id: string;
  property: string;
  variable: string;
  transform?: string;
}

export function useDataBinding(projectId?: string) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [variables, setVariables] = useState<DataVariable[]>([]);
  const [bindings, setBindings] = useState<DataBinding[]>([]);

  const fetchDataSources = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/sources/?project=${projectId}`);
      if (response.ok) {
        setDataSources(await response.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const createDataSource = useCallback(async (
    sourceType: string,
    name: string,
    url: string,
    config?: Record<string, unknown>
  ): Promise<DataSource> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/sources/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          source_type: sourceType,
          name,
          url,
          config
        })
      });
      if (!response.ok) throw new Error('Failed to create data source');
      const source = await response.json();
      setDataSources(prev => [...prev, source]);
      return source;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const testConnection = useCallback(async (
    sourceType: string,
    url: string,
    config?: Record<string, unknown>
  ): Promise<{ success: boolean; message?: string; schema?: Record<string, string> }> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/test-connection/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source_type: sourceType, url, config })
      });
      return await response.json();
    } catch (err) {
      return { success: false, message: err instanceof Error ? err.message : 'Connection failed' };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchData = useCallback(async (sourceId: string): Promise<unknown> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/sources/${sourceId}/fetch/`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to fetch data');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const previewData = useCallback(async (sourceId: string, limit: number = 10): Promise<unknown[]> => {
    try {
      const response = await fetch(`${API_BASE}/sources/${sourceId}/preview/?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to preview data');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const createVariable = useCallback(async (
    name: string,
    variableType: string,
    defaultValue?: unknown,
    sourceId?: string,
    path?: string
  ): Promise<DataVariable> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/variables/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          name,
          variable_type: variableType,
          default_value: defaultValue,
          source: sourceId,
          path
        })
      });
      if (!response.ok) throw new Error('Failed to create variable');
      const variable = await response.json();
      setVariables(prev => [...prev, variable]);
      return variable;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const updateVariable = useCallback(async (
    variableId: string,
    updates: Partial<DataVariable>
  ): Promise<DataVariable> => {
    try {
      const response = await fetch(`${API_BASE}/variables/${variableId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update variable');
      const variable = await response.json();
      setVariables(prev => prev.map(v => v.id === variableId ? variable : v));
      return variable;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const createBinding = useCallback(async (
    elementId: string,
    property: string,
    variableId: string,
    transform?: string
  ): Promise<DataBinding> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/bindings/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project: projectId,
          element_id: elementId,
          property,
          variable: variableId,
          transform
        })
      });
      if (!response.ok) throw new Error('Failed to create binding');
      const binding = await response.json();
      setBindings(prev => [...prev, binding]);
      return binding;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const removeBinding = useCallback(async (bindingId: string) => {
    try {
      const response = await fetch(`${API_BASE}/bindings/${bindingId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to remove binding');
      setBindings(prev => prev.filter(b => b.id !== bindingId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const transformPreview = useCallback(async (
    value: unknown,
    transform: string
  ): Promise<unknown> => {
    try {
      const response = await fetch(`${API_BASE}/transform-preview/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value, transform })
      });
      if (!response.ok) throw new Error('Transform preview failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  useEffect(() => {
    if (projectId) {
      fetchDataSources();
    }
  }, [projectId, fetchDataSources]);

  return {
    isLoading,
    error,
    dataSources,
    variables,
    bindings,
    createDataSource,
    testConnection,
    fetchData,
    previewData,
    createVariable,
    updateVariable,
    createBinding,
    removeBinding,
    transformPreview,
    refresh: fetchDataSources
  };
}

export default useDataBinding;

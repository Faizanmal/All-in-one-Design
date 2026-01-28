import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/smart-tools';

interface SelectionResult {
  selected: string[];
  count: number;
}

interface RenameResult {
  renamed: Array<{ id: string; oldName: string; newName: string }>;
}

interface FindReplaceResult {
  matched: number;
  replaced: number;
}

interface ResizeResult {
  resized: string[];
}

export function useSmartTools() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const smartSelect = useCallback(async (
    projectId: string, 
    query: string
  ): Promise<SelectionResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/select/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, query })
      });
      if (!response.ok) throw new Error('Selection failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectByType = useCallback(async (projectId: string, elementType: string): Promise<SelectionResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/select/by-type/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, element_type: elementType })
      });
      if (!response.ok) throw new Error('Selection by type failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectByColor = useCallback(async (
    projectId: string, 
    color: string, 
    tolerance: number = 0
  ): Promise<SelectionResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/select/by-color/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, color, tolerance })
      });
      if (!response.ok) throw new Error('Selection by color failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const selectByFont = useCallback(async (
    projectId: string, 
    fontFamily: string,
    fontSize?: number
  ): Promise<SelectionResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/select/by-font/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, font_family: fontFamily, font_size: fontSize })
      });
      if (!response.ok) throw new Error('Selection by font failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const batchRename = useCallback(async (
    elementIds: string[], 
    pattern: string,
    startNumber: number = 1
  ): Promise<RenameResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/batch-rename/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ element_ids: elementIds, pattern, start_number: startNumber })
      });
      if (!response.ok) throw new Error('Batch rename failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const findAndReplace = useCallback(async (
    projectId: string,
    find: string,
    replace: string,
    options: {
      caseSensitive?: boolean;
      useRegex?: boolean;
      scope?: 'text' | 'names' | 'all';
    } = {}
  ): Promise<FindReplaceResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/find-replace/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          find,
          replace,
          case_sensitive: options.caseSensitive ?? false,
          use_regex: options.useRegex ?? false,
          scope: options.scope ?? 'all'
        })
      });
      if (!response.ok) throw new Error('Find and replace failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const batchResize = useCallback(async (
    elementIds: string[],
    mode: 'scale' | 'width' | 'height' | 'fit' | 'fill',
    value: number,
    maintainAspectRatio: boolean = true
  ): Promise<ResizeResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/batch-resize/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          element_ids: elementIds,
          mode,
          value,
          maintain_aspect_ratio: maintainAspectRatio
        })
      });
      if (!response.ok) throw new Error('Batch resize failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    smartSelect,
    selectByType,
    selectByColor,
    selectByFont,
    batchRename,
    findAndReplace,
    batchResize
  };
}

export default useSmartTools;

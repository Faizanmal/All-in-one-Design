import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/vector';

interface VectorPath {
  id: string;
  points: Array<{ x: number; y: number; handleIn?: { x: number; y: number }; handleOut?: { x: number; y: number } }>;
  closed: boolean;
  stroke: string;
  strokeWidth: number;
  fill: string;
}

interface BooleanOperationResult {
  id: string;
  result_path: unknown;
  operation: string;
}

export function useVectorEditing() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createPath = useCallback(async (projectId: string, pathData: Partial<VectorPath>) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project: projectId, ...pathData })
      });
      if (!response.ok) throw new Error('Failed to create path');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updatePath = useCallback(async (pathId: string, pathData: Partial<VectorPath>) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/${pathId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pathData)
      });
      if (!response.ok) throw new Error('Failed to update path');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deletePath = useCallback(async (pathId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/${pathId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete path');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const booleanOperation = useCallback(async (
    paths: string[], 
    operation: 'union' | 'subtract' | 'intersect' | 'exclude'
  ): Promise<BooleanOperationResult> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/boolean-operations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ paths, operation })
      });
      if (!response.ok) throw new Error('Boolean operation failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const offsetPath = useCallback(async (pathId: string, offset: number, joinType: string = 'round') => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/${pathId}/offset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ offset, join_type: joinType })
      });
      if (!response.ok) throw new Error('Path offset failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const roundCorners = useCallback(async (pathId: string, radius: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/${pathId}/round_corners/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ radius })
      });
      if (!response.ok) throw new Error('Corner rounding failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const simplifyPath = useCallback(async (pathId: string, tolerance: number = 1) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/paths/${pathId}/simplify/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tolerance })
      });
      if (!response.ok) throw new Error('Path simplification failed');
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
    createPath,
    updatePath,
    deletePath,
    booleanOperation,
    offsetPath,
    roundCorners,
    simplifyPath
  };
}

export default useVectorEditing;

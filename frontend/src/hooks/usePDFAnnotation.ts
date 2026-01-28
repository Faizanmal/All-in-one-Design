import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/pdf';

interface PDFDocument {
  id: string;
  name: string;
  file_size: number;
  page_count: number;
  status: 'uploading' | 'processing' | 'ready' | 'error';
}

interface PDFPage {
  id: string;
  page_number: number;
  width: number;
  height: number;
  image_url?: string;
}

interface PDFAnnotation {
  id: string;
  page_number: number;
  annotation_type: string;
  bounds: { x: number; y: number; width: number; height: number };
  color: string;
  content?: string;
  points?: Array<{ x: number; y: number }>;
}

interface ImportResult {
  success: boolean;
  imported_count: number;
  created_elements: string[];
}

export function usePDFAnnotation() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [document, setDocument] = useState<PDFDocument | null>(null);
  const [pages, setPages] = useState<PDFPage[]>([]);
  const [annotations, setAnnotations] = useState<PDFAnnotation[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadPDF = useCallback(async (file: File, projectId: string): Promise<PDFDocument> => {
    setIsLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project', projectId);

      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            setUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const doc = JSON.parse(xhr.responseText);
            setDocument(doc);
            resolve(doc);
          } else {
            reject(new Error('Upload failed'));
          }
        });

        xhr.addEventListener('error', () => reject(new Error('Upload failed')));
        
        xhr.open('POST', `${API_BASE}/documents/`);
        xhr.send(formData);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
      setUploadProgress(0);
    }
  }, []);

  const fetchPages = useCallback(async (documentId: string): Promise<PDFPage[]> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/documents/${documentId}/pages/`);
      if (!response.ok) throw new Error('Failed to fetch pages');
      const data = await response.json();
      setPages(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchAnnotations = useCallback(async (documentId: string): Promise<PDFAnnotation[]> => {
    try {
      const response = await fetch(`${API_BASE}/documents/${documentId}/annotations/`);
      if (!response.ok) throw new Error('Failed to fetch annotations');
      const data = await response.json();
      setAnnotations(data);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const createAnnotation = useCallback(async (
    pageId: string,
    annotationType: string,
    bounds: { x: number; y: number; width: number; height: number },
    options?: {
      color?: string;
      content?: string;
      points?: Array<{ x: number; y: number }>;
    }
  ): Promise<PDFAnnotation> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/annotations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          page: pageId,
          annotation_type: annotationType,
          bounds,
          ...options
        })
      });
      if (!response.ok) throw new Error('Failed to create annotation');
      const annotation = await response.json();
      setAnnotations(prev => [...prev, annotation]);
      return annotation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateAnnotation = useCallback(async (
    annotationId: string,
    updates: Partial<PDFAnnotation>
  ): Promise<PDFAnnotation> => {
    try {
      const response = await fetch(`${API_BASE}/annotations/${annotationId}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!response.ok) throw new Error('Failed to update annotation');
      const annotation = await response.json();
      setAnnotations(prev => prev.map(a => a.id === annotationId ? annotation : a));
      return annotation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const deleteAnnotation = useCallback(async (annotationId: string) => {
    try {
      const response = await fetch(`${API_BASE}/annotations/${annotationId}/`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete annotation');
      setAnnotations(prev => prev.filter(a => a.id !== annotationId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const importAnnotationsToDesign = useCallback(async (
    documentId: string,
    annotationIds: string[],
    options?: {
      convertToShapes?: boolean;
      preserveColors?: boolean;
      scaleToCanvas?: boolean;
      createGroups?: boolean;
      targetFrameId?: string;
    }
  ): Promise<ImportResult> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/import-annotations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: documentId,
          annotation_ids: annotationIds,
          options
        })
      });
      if (!response.ok) throw new Error('Import failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const exportPDF = useCallback(async (
    projectId: string,
    options?: {
      includeAnnotations?: boolean;
      pageRange?: string;
      quality?: 'draft' | 'standard' | 'high';
    }
  ): Promise<string> => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/export/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project: projectId, ...options })
      });
      if (!response.ok) throw new Error('Export failed');
      const result = await response.json();
      return result.download_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const reprocessDocument = useCallback(async (documentId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/documents/${documentId}/reprocess/`, { method: 'POST' });
      if (!response.ok) throw new Error('Reprocess failed');
      const doc = await response.json();
      setDocument(doc);
      return doc;
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
    document,
    pages,
    annotations,
    uploadProgress,
    uploadPDF,
    fetchPages,
    fetchAnnotations,
    createAnnotation,
    updateAnnotation,
    deleteAnnotation,
    importAnnotationsToDesign,
    exportPDF,
    reprocessDocument
  };
}

export default usePDFAnnotation;

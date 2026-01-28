import { useState, useCallback } from 'react';

const API_BASE = '/api/v1/media';

interface VideoAsset {
  id: string;
  name: string;
  source_type: 'upload' | 'youtube' | 'vimeo' | 'url';
  url: string;
  thumbnail_url?: string;
  duration?: number;
  width?: number;
  height?: number;
}

interface GIFAsset {
  id: string;
  name: string;
  file: string;
  width: number;
  height: number;
  frame_count: number;
  duration: number;
}

interface AnimatedExport {
  id: string;
  format: 'gif' | 'mp4' | 'webm' | 'lottie' | 'apng' | 'webp';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  output_url?: string;
}

interface ExportSettings {
  format: 'gif' | 'mp4' | 'webm' | 'lottie' | 'apng' | 'webp';
  quality: 'low' | 'medium' | 'high';
  fps: number;
  width: number;
  height: number;
  loop: boolean;
  start_frame?: number;
  end_frame?: number;
}

export function useMediaAssets() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadVideo = useCallback(async (file: File, projectId: string): Promise<VideoAsset> => {
    setIsLoading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project', projectId);
      formData.append('name', file.name);

      const xhr = new XMLHttpRequest();
      
      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            setUploadProgress(Math.round((e.loaded / e.total) * 100));
          }
        });

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error('Upload failed'));
          }
        });

        xhr.addEventListener('error', () => reject(new Error('Upload failed')));
        
        xhr.open('POST', `${API_BASE}/videos/`);
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

  const embedFromUrl = useCallback(async (
    url: string, 
    projectId: string,
    name?: string
  ): Promise<VideoAsset> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/videos/from_url/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, project: projectId, name })
      });
      if (!response.ok) throw new Error('Failed to embed video');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const uploadGIF = useCallback(async (file: File, projectId: string): Promise<GIFAsset> => {
    setIsLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('project', projectId);
      formData.append('name', file.name);

      const response = await fetch(`${API_BASE}/gifs/`, {
        method: 'POST',
        body: formData
      });
      if (!response.ok) throw new Error('GIF upload failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const extractFrames = useCallback(async (
    videoId: string,
    timestamps: number[]
  ): Promise<string[]> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/videos/${videoId}/extract_frames/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timestamps })
      });
      if (!response.ok) throw new Error('Frame extraction failed');
      const result = await response.json();
      return result.frames;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createAnimatedExport = useCallback(async (
    projectId: string,
    settings: ExportSettings
  ): Promise<AnimatedExport> => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/exports/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project: projectId, ...settings })
      });
      if (!response.ok) throw new Error('Export creation failed');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getExportStatus = useCallback(async (exportId: string): Promise<AnimatedExport> => {
    try {
      const response = await fetch(`${API_BASE}/exports/${exportId}/`);
      if (!response.ok) throw new Error('Failed to get export status');
      return await response.json();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    }
  }, []);

  const listAssets = useCallback(async (projectId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const [videosRes, gifsRes] = await Promise.all([
        fetch(`${API_BASE}/videos/?project=${projectId}`),
        fetch(`${API_BASE}/gifs/?project=${projectId}`)
      ]);

      const videos = videosRes.ok ? await videosRes.json() : [];
      const gifs = gifsRes.ok ? await gifsRes.json() : [];

      return { videos, gifs };
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
    uploadProgress,
    uploadVideo,
    embedFromUrl,
    uploadGIF,
    extractFrames,
    createAnimatedExport,
    getExportStatus,
    listAssets
  };
}

export default useMediaAssets;

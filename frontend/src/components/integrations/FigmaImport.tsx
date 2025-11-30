/**
 * Third-party Integrations - Figma Import Component
 */
'use client';

import React, { useState, useCallback } from 'react';
import { Upload, Link, FileImage, Check, AlertCircle, Loader2 } from 'lucide-react';

interface FigmaFile {
  id: string;
  name: string;
  lastModified: string;
  thumbnailUrl?: string;
}

interface ImportedAsset {
  id: string;
  name: string;
  type: string;
  previewUrl: string;
}

interface FigmaImportProps {
  onImportComplete: (assets: ImportedAsset[]) => void;
  onError: (error: string) => void;
}

export const FigmaImport: React.FC<FigmaImportProps> = ({
  onImportComplete,
  onError,
}) => {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [figmaUrl, setFigmaUrl] = useState('');
  const [files, setFiles] = useState<FigmaFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const [importProgress, setImportProgress] = useState(0);

  const connectFigma = useCallback(async () => {
    setLoading(true);
    try {
      // Initiate OAuth flow
      const response = await fetch('/api/v1/integrations/figma/connect/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.auth_url) {
          window.open(data.auth_url, '_blank', 'width=600,height=700');
        }
        setConnected(true);
        // Fetch user's files
        await fetchFigmaFiles();
      }
    } catch (err) {
      onError('Failed to connect to Figma');
    } finally {
      setLoading(false);
    }
  }, [onError]);

  const fetchFigmaFiles = async () => {
    try {
      const response = await fetch('/api/v1/integrations/figma/files/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }
    } catch (err) {
      console.error('Failed to fetch Figma files:', err);
    }
  };

  const importFromUrl = async () => {
    if (!figmaUrl) return;

    setImporting(true);
    setImportProgress(0);

    try {
      const response = await fetch('/api/v1/integrations/figma/import/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ figma_url: figmaUrl }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Poll for progress
        const pollInterval = setInterval(async () => {
          const statusResponse = await fetch(
            `/api/v1/integrations/figma/imports/${data.import_id}/status/`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
              },
            }
          );
          
          if (statusResponse.ok) {
            const status = await statusResponse.json();
            setImportProgress(status.progress || 0);
            
            if (status.status === 'completed') {
              clearInterval(pollInterval);
              setImporting(false);
              onImportComplete(status.assets || []);
            } else if (status.status === 'failed') {
              clearInterval(pollInterval);
              setImporting(false);
              onError(status.error || 'Import failed');
            }
          }
        }, 1000);
      } else {
        throw new Error('Import request failed');
      }
    } catch (err) {
      setImporting(false);
      onError('Failed to import from Figma');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
          <FileImage className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Import from Figma
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Import designs directly from your Figma files
          </p>
        </div>
      </div>

      {!connected ? (
        <div className="text-center py-8">
          <button
            onClick={connectFigma}
            disabled={loading}
            className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Link className="w-5 h-5" />
            )}
            Connect Figma Account
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* URL Import */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Import from URL
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={figmaUrl}
                onChange={(e) => setFigmaUrl(e.target.value)}
                placeholder="https://www.figma.com/file/..."
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
              />
              <button
                onClick={importFromUrl}
                disabled={importing || !figmaUrl}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium disabled:opacity-50"
              >
                {importing ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  'Import'
                )}
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          {importing && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                <span>Importing...</span>
                <span>{importProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${importProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Recent Files */}
          {files.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Recent Files
              </h4>
              <div className="grid grid-cols-2 gap-3">
                {files.map((file) => (
                  <button
                    key={file.id}
                    onClick={() => {
                      setSelectedFile(file.id);
                      setFigmaUrl(`https://www.figma.com/file/${file.id}`);
                    }}
                    className={`p-3 rounded-lg border-2 transition-colors text-left ${
                      selectedFile === file.id
                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-purple-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {file.thumbnailUrl ? (
                        <img
                          src={file.thumbnailUrl}
                          alt={file.name}
                          className="w-12 h-12 rounded object-cover"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                          <FileImage className="w-6 h-6 text-gray-400" />
                        </div>
                      )}
                      <div className="overflow-hidden">
                        <p className="font-medium text-gray-900 dark:text-white truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(file.lastModified).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FigmaImport;

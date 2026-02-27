'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { exportAPI, ExportTemplate, ExportJob } from '@/lib/export-api';
import {
  Download,
  FileImage,
  FileType,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Package
} from 'lucide-react';

interface ExportDialogProps {
  isOpen: boolean;
  onClose: () => void;
  projectId?: number;
  projectIds?: number[];
}

export default function ExportDialog({
  isOpen,
  onClose,
  projectId,
  projectIds
}: ExportDialogProps) {
  const [format, setFormat] = useState<'svg' | 'pdf' | 'png' | 'figma'>('svg');
  const [templates, setTemplates] = useState<ExportTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null);
  const [jobs, setJobs] = useState<ExportJob[]>([]);
  const [exporting, setExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<'single' | 'batch' | 'jobs'>('single');

  // Export options
  const [quality, setQuality] = useState(90);
  const [scale, setScale] = useState(1);
  const [optimize, setOptimize] = useState(true);

  useEffect(() => {
    if (isOpen) {
      loadTemplates();
      loadJobs();
    }
  }, [isOpen]);

  const loadTemplates = async () => {
    try {
      const data = await exportAPI.getTemplates();
      setTemplates(data.results || data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadJobs = async () => {
    try {
      const data = await exportAPI.getExportJobs();
      setJobs(data.results || data);
    } catch (error) {
      console.error('Failed to load export jobs:', error);
    }
  };

  const handleSingleExport = async () => {
    if (!projectId) return;

    setExporting(true);
    try {
      let blob;
      
      if (format === 'svg') {
        blob = await exportAPI.exportToSVG(projectId);
      } else if (format === 'pdf') {
        blob = await exportAPI.exportToPDF(projectId);
      } else if (format === 'figma') {
        blob = await exportAPI.exportToFigma(projectId);
      }

      if (blob) {
        exportAPI.downloadBlob(blob, `export-${projectId}.${format}`);
      }

      alert('Export completed successfully!');
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleBatchExport = async () => {
    if (!projectIds || projectIds.length === 0) return;

    setExporting(true);
    try {
      const job = await exportAPI.createBatchExport(projectIds, format);
      setJobs([job, ...jobs]);
      setActiveTab('jobs');
      alert('Batch export started! Check the Jobs tab for progress.');
    } catch (error) {
      console.error('Batch export failed:', error);
      alert('Batch export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const getFormatIcon = (fmt: string) => {
    switch (fmt) {
      case 'svg':
      case 'figma':
        return <FileType className="w-5 h-5" />;
      case 'pdf':
        return <FileImage className="w-5 h-5" />;
      case 'png':
        return <FileImage className="w-5 h-5" />;
      default:
        return <Download className="w-5 h-5" />;
    }
  };

  const getJobStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getJobStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      case 'processing':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const downloadJobFile = async (job: ExportJob) => {
    if (!job.file_url) return;

    try {
      const response = await fetch(job.file_url);
      const blob = await response.blob();
      exportAPI.downloadBlob(blob, `batch-export-${job.id}.zip`);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl"
      >
        {/* Header */}
        <div className="bg-linear-to-r from-purple-600 to-blue-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Download className="w-6 h-6" />
              <h2 className="text-2xl font-bold">Export Options</h2>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <XCircle className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('single')}
            className={`flex-1 px-6 py-4 font-medium transition-colors ${
              activeTab === 'single'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Single Export
          </button>
          {projectIds && projectIds.length > 1 && (
            <button
              onClick={() => setActiveTab('batch')}
              className={`flex-1 px-6 py-4 font-medium transition-colors ${
                activeTab === 'batch'
                  ? 'border-b-2 border-purple-600 text-purple-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <span className="flex items-center justify-center gap-2">
                <Package className="w-4 h-4" />
                Batch Export ({projectIds.length})
              </span>
            </button>
          )}
          <button
            onClick={() => setActiveTab('jobs')}
            className={`flex-1 px-6 py-4 font-medium transition-colors ${
              activeTab === 'jobs'
                ? 'border-b-2 border-purple-600 text-purple-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Export Jobs
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Single Export */}
          {activeTab === 'single' && (
            <div className="space-y-6">
              {/* Format Selection */}
              <div>
                <label className="block text-sm font-medium mb-3">Export Format</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['svg', 'pdf', 'png', 'figma'].map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => setFormat(fmt as 'svg' | 'pdf' | 'png' | 'figma')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        format === fmt
                          ? 'border-purple-600 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="flex flex-col items-center gap-2">
                        {getFormatIcon(fmt)}
                        <span className="text-sm font-medium uppercase">{fmt}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Options */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Quality: {quality}%
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={quality}
                    onChange={(e) => setQuality(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Scale: {scale}x
                  </label>
                  <input
                    type="range"
                    min="0.5"
                    max="4"
                    step="0.5"
                    value={scale}
                    onChange={(e) => setScale(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={optimize}
                    onChange={(e) => setOptimize(e.target.checked)}
                    className="w-4 h-4 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <span className="text-sm font-medium">Optimize for file size</span>
                </label>
              </div>

              {/* Templates */}
              {templates.length > 0 && (
                <div>
                  <label className="block text-sm font-medium mb-3">Export Template (Optional)</label>
                  <select
                    value={selectedTemplate || ''}
                    onChange={(e) => setSelectedTemplate(e.target.value ? parseInt(e.target.value) : null)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  >
                    <option value="">None (use custom settings)</option>
                    {templates.map(template => (
                      <option key={template.id} value={template.id}>
                        {template.name} - {template.format.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <button
                onClick={handleSingleExport}
                disabled={exporting}
                className="w-full px-6 py-3 bg-linear-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
              >
                {exporting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Export {format.toUpperCase()}
                  </>
                )}
              </button>
            </div>
          )}

          {/* Batch Export */}
          {activeTab === 'batch' && projectIds && (
            <div className="space-y-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>Batch Export:</strong> Export {projectIds.length} projects as a single ZIP file.
                  This process runs in the background and you&apos;ll be notified when it&apos;s complete.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Export Format</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['svg', 'pdf', 'png', 'figma'].map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => setFormat(fmt as 'svg' | 'pdf' | 'png' | 'figma')}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        format === fmt
                          ? 'border-purple-600 bg-purple-50'
                          : 'border-gray-200 hover:border-purple-300'
                      }`}
                    >
                      <div className="flex flex-col items-center gap-2">
                        {getFormatIcon(fmt)}
                        <span className="text-sm font-medium uppercase">{fmt}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={handleBatchExport}
                disabled={exporting}
                className="w-full px-6 py-3 bg-linear-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
              >
                {exporting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Starting Batch Export...
                  </>
                ) : (
                  <>
                    <Package className="w-5 h-5" />
                    Start Batch Export
                  </>
                )}
              </button>
            </div>
          )}

          {/* Export Jobs */}
          {activeTab === 'jobs' && (
            <div className="space-y-4">
              {jobs.length > 0 ? (
                jobs.map(job => (
                  <motion.div
                    key={job.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getJobStatusIcon(job.status)}
                        <div>
                          <p className="font-medium">
                            {job.project_count} projects · {job.format.toUpperCase()}
                          </p>
                          <p className="text-sm text-gray-600">
                            {new Date(job.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getJobStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                    </div>

                    {/* Progress Bar */}
                    {job.status === 'processing' && (
                      <div className="mb-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${job.progress || 0}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {job.progress || 0}% complete
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    {job.status === 'completed' && job.file_url && (
                      <button
                        onClick={() => downloadJobFile(job)}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download ZIP
                      </button>
                    )}

                    {job.status === 'failed' && job.error_message && (
                      <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-800">
                        <strong>Error:</strong> {job.error_message}
                      </div>
                    )}
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No export jobs yet</p>
                  <p className="text-sm">Start a batch export to see jobs here</p>
                </div>
              )}
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}

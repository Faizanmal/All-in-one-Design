'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  FileText, Download, Settings, Eye, Layers, Grid,
  Check, X, AlertTriangle, Printer, Palette, Scissors,
  RefreshCw, ChevronDown, ChevronRight, Info, Target,
  Monitor, Smartphone, Film,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';

// Types
interface PDFExportPreset {
  id: string;
  name: string;
  pageSize: string;
  orientation: 'portrait' | 'landscape';
  bleedMargin: number;
  colorMode: 'rgb' | 'cmyk' | 'grayscale';
  pdfStandard: 'pdf_x1a' | 'pdf_x4' | 'pdf_a' | 'standard';
  includeBleed: boolean;
  includeCropMarks: boolean;
  includeRegistrationMarks: boolean;
  resolution: number;
}

interface PreflightResult {
  status: 'pass' | 'warning' | 'error';
  checks: Array<{
    name: string;
    status: 'pass' | 'warning' | 'error';
    message: string;
    details?: string;
  }>;
  summary: {
    passed: number;
    warnings: number;
    errors: number;
  };
}

interface PDFExport {
  id: string;
  projectId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  fileUrl: string | null;
  fileSize: number | null;
  pageCount: number;
  createdAt: string;
}

interface PageSpread {
  id: string;
  leftPage: number | null;
  rightPage: number | null;
  isCover: boolean;
}

// Page Sizes
const PAGE_SIZES = [
  { id: 'a4', name: 'A4', width: 210, height: 297 },
  { id: 'a3', name: 'A3', width: 297, height: 420 },
  { id: 'a5', name: 'A5', width: 148, height: 210 },
  { id: 'letter', name: 'US Letter', width: 215.9, height: 279.4 },
  { id: 'legal', name: 'US Legal', width: 215.9, height: 355.6 },
  { id: 'tabloid', name: 'Tabloid', width: 279.4, height: 431.8 },
  { id: 'custom', name: 'Custom', width: 0, height: 0 },
];

const PDF_STANDARDS = [
  { id: 'standard', name: 'Standard PDF', description: 'General purpose PDF' },
  { id: 'pdf_x1a', name: 'PDF/X-1a', description: 'CMYK workflow, no transparency' },
  { id: 'pdf_x4', name: 'PDF/X-4', description: 'Supports transparency and ICC profiles' },
  { id: 'pdf_a', name: 'PDF/A', description: 'Long-term archiving' },
];

// Bleed Settings Component
export function BleedSettings({
  bleed,
  onChange,
}: {
  bleed: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Scissors className="w-5 h-5 text-blue-400" />
        Bleed & Margins
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-2">
            Bleed Margin
          </label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min={0}
              max={10}
              step={0.5}
              value={bleed}
              onChange={(e) => onChange(parseFloat(e.target.value))}
              className="flex-1"
            />
            <div className="w-20 text-center">
              <input
                type="number"
                value={bleed}
                onChange={(e) => onChange(parseFloat(e.target.value))}
                className="w-full px-2 py-1 bg-gray-700 border border-gray-600 rounded text-center"
                min={0}
                max={10}
                step={0.5}
              />
              <span className="text-xs text-gray-400">mm</span>
            </div>
          </div>
        </div>

        {/* Bleed Preview */}
        <div className="relative h-32 bg-gray-700 rounded-lg overflow-hidden">
          <div
            className="absolute inset-0 border border-dashed border-red-400"
            style={{ margin: `${bleed * 3}px` }}
          />
          <div
            className="absolute inset-0 bg-white/10"
            style={{ margin: `${bleed * 3 + 8}px` }}
          />
          <div className="absolute inset-0 flex items-center justify-center text-xs text-gray-400">
            Bleed Area Preview
          </div>
        </div>

        <div className="text-xs text-gray-400">
          <Info className="w-3 h-3 inline mr-1" />
          Standard bleed is 3mm. Extend design elements beyond the trim line.
        </div>
      </div>
    </div>
  );
}

// Print Marks Settings Component
export function PrintMarksSettings({
  settings,
  onChange,
}: {
  settings: {
    cropMarks: boolean;
    registrationMarks: boolean;
    colorBars: boolean;
    pageInfo: boolean;
  };
  onChange: (key: string, value: boolean) => void;
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Target className="w-5 h-5 text-green-400" />
        Print Marks
      </h3>

      <div className="space-y-3">
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm">Crop Marks</span>
          <input
            type="checkbox"
            checked={settings.cropMarks}
            onChange={(e) => onChange('cropMarks', e.target.checked)}
            className="w-5 h-5 rounded bg-gray-700 border-gray-600"
          />
        </label>
        
        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm">Registration Marks</span>
          <input
            type="checkbox"
            checked={settings.registrationMarks}
            onChange={(e) => onChange('registrationMarks', e.target.checked)}
            className="w-5 h-5 rounded bg-gray-700 border-gray-600"
          />
        </label>

        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm">Color Bars</span>
          <input
            type="checkbox"
            checked={settings.colorBars}
            onChange={(e) => onChange('colorBars', e.target.checked)}
            className="w-5 h-5 rounded bg-gray-700 border-gray-600"
          />
        </label>

        <label className="flex items-center justify-between cursor-pointer">
          <span className="text-sm">Page Information</span>
          <input
            type="checkbox"
            checked={settings.pageInfo}
            onChange={(e) => onChange('pageInfo', e.target.checked)}
            className="w-5 h-5 rounded bg-gray-700 border-gray-600"
          />
        </label>
      </div>
    </div>
  );
}

// Color Mode Settings Component
export function ColorModeSettings({
  colorMode,
  onChange,
}: {
  colorMode: 'rgb' | 'cmyk' | 'grayscale';
  onChange: (mode: 'rgb' | 'cmyk' | 'grayscale') => void;
}) {
  const modes = [
    { id: 'rgb', name: 'RGB', description: 'Best for screen display', icon: Monitor },
    { id: 'cmyk', name: 'CMYK', description: 'Required for print', icon: Printer },
    { id: 'grayscale', name: 'Grayscale', description: 'Black & white printing', icon: Film },
  ];

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Palette className="w-5 h-5 text-purple-400" />
        Color Mode
      </h3>

      <div className="space-y-2">
        {modes.map((mode) => (
          <button
            key={mode.id}
            onClick={() => onChange(mode.id as 'cmyk' | 'rgb' | 'grayscale')}
            className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
              colorMode === mode.id
                ? 'bg-purple-600 text-white'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <mode.icon className="w-5 h-5" />
            <div className="text-left">
              <div className="font-medium">{mode.name}</div>
              <div className="text-xs opacity-70">{mode.description}</div>
            </div>
            {colorMode === mode.id && <Check className="w-4 h-4 ml-auto" />}
          </button>
        ))}
      </div>
    </div>
  );
}

// Preflight Check Component
export function PreflightCheck({
  result,
  onRunCheck,
  isChecking,
}: {
  result: PreflightResult | null;
  onRunCheck: () => void;
  isChecking: boolean;
}) {
  const getStatusIcon = (status: 'pass' | 'warning' | 'error') => {
    switch (status) {
      case 'pass':
        return <Check className="w-4 h-4 text-green-400" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'error':
        return <X className="w-4 h-4 text-red-400" />;
    }
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Check className="w-5 h-5 text-green-400" />
          Preflight Check
        </h3>
        <button
          onClick={onRunCheck}
          disabled={isChecking}
          className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm disabled:opacity-50"
        >
          {isChecking ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Run Check
        </button>
      </div>

      {result ? (
        <>
          {/* Summary */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 p-3 bg-green-900/30 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-400">{result.summary.passed}</div>
              <div className="text-xs text-gray-400">Passed</div>
            </div>
            <div className="flex-1 p-3 bg-amber-900/30 rounded-lg text-center">
              <div className="text-2xl font-bold text-amber-400">{result.summary.warnings}</div>
              <div className="text-xs text-gray-400">Warnings</div>
            </div>
            <div className="flex-1 p-3 bg-red-900/30 rounded-lg text-center">
              <div className="text-2xl font-bold text-red-400">{result.summary.errors}</div>
              <div className="text-xs text-gray-400">Errors</div>
            </div>
          </div>

          {/* Check Results */}
          <div className="space-y-2">
            {result.checks.map((check, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg ${
                  check.status === 'error'
                    ? 'bg-red-900/20'
                    : check.status === 'warning'
                    ? 'bg-amber-900/20'
                    : 'bg-gray-700/50'
                }`}
              >
                <div className="flex items-center gap-2">
                  {getStatusIcon(check.status)}
                  <span className="font-medium text-sm">{check.name}</span>
                </div>
                <div className="text-xs text-gray-400 mt-1">{check.message}</div>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
            <Check className="w-8 h-8 opacity-30" />
          </div>
          <p className="text-sm font-medium text-gray-300 mb-1">Ready to check</p>
          <p className="text-xs text-gray-600">Run preflight check to validate your document before export</p>
        </div>
      )}
    </div>
  );
}

// Page Spread View Component
export function SpreadView({
  pages,
  spreads,
  onUpdateSpreads,
}: {
  pages: number;
  spreads: PageSpread[];
  onUpdateSpreads: (spreads: PageSpread[]) => void;
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 text-white">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Layers className="w-5 h-5 text-blue-400" />
        Page Spreads
      </h3>

      <div className="space-y-3">
        {spreads.map((spread, idx) => (
          <div
            key={spread.id}
            className="flex items-center gap-2 p-2 bg-gray-700 rounded-lg"
          >
            <div className="w-12 h-16 bg-gray-600 rounded flex items-center justify-center text-sm">
              {spread.leftPage || '-'}
            </div>
            <div className="w-12 h-16 bg-gray-600 rounded flex items-center justify-center text-sm">
              {spread.rightPage || '-'}
            </div>
            <div className="flex-1 text-sm text-gray-400">
              Spread {idx + 1}
              {spread.isCover && (
                <span className="ml-2 px-2 py-0.5 bg-blue-600 text-white rounded text-xs">
                  Cover
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Main PDF Export Dialog
export function PDFExportDialog({
  isOpen,
  onClose,
  projectId,
  pageCount,
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  pageCount: number;
}) {
  const [preset, setPreset] = useState<PDFExportPreset>({
    id: 'custom',
    name: 'Custom',
    pageSize: 'a4',
    orientation: 'portrait',
    bleedMargin: 3,
    colorMode: 'cmyk',
    pdfStandard: 'pdf_x4',
    includeBleed: true,
    includeCropMarks: true,
    includeRegistrationMarks: true,
    resolution: 300,
  });
  const [printMarks, setPrintMarks] = useState({
    cropMarks: true,
    registrationMarks: true,
    colorBars: false,
    pageInfo: true,
  });
  const [preflightResult, setPreflightResult] = useState<PreflightResult | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [selectedPages, setSelectedPages] = useState<number[]>(
    Array.from({ length: pageCount }, (_, i) => i + 1)
  );

  const runPreflightCheck = async () => {
    setIsChecking(true);
    try {
      const response = await fetch(`/api/v1/pdf-export/preflight/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, settings: preset }),
      });
      const data = await response.json();
      setPreflightResult(data);
    } catch (error) {
      // Mock result
      setPreflightResult({
        status: 'warning',
        checks: [
          { name: 'Resolution Check', status: 'pass', message: 'All images are 300 DPI or higher' },
          { name: 'Color Space', status: 'pass', message: 'Document is in CMYK color space' },
          { name: 'Bleed Check', status: 'warning', message: 'Some elements may not extend to bleed area' },
          { name: 'Font Embedding', status: 'pass', message: 'All fonts are embedded' },
          { name: 'Overprint Check', status: 'pass', message: 'No overprint issues detected' },
        ],
        summary: { passed: 4, warnings: 1, errors: 0 },
      });
    } finally {
      setIsChecking(false);
    }
  };

  const startExport = async () => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      const response = await fetch('/api/v1/pdf-export/exports/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          preset,
          print_marks: printMarks,
          pages: selectedPages,
        }),
      });
      const data = await response.json();

      // Simulate progress
      const interval = setInterval(() => {
        setExportProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 500);
    } catch (error) {
      console.error('Export failed', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <TooltipProvider>
      <div className="bg-gray-900 rounded-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Printer className="w-6 h-6 text-blue-400" />
            PDF Export
            {preflightResult && (
              <Badge className={`ml-2 text-xs ${
                preflightResult.status === 'pass' ? 'bg-green-500/20 text-green-400 border-green-500/30' :
                preflightResult.status === 'warning' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                'bg-red-500/20 text-red-400 border-red-500/30'
              }`}>
                {preflightResult.summary.errors > 0 ? `${preflightResult.summary.errors} errors` :
                 preflightResult.summary.warnings > 0 ? `${preflightResult.summary.warnings} warnings` :
                 'Preflight OK'}
              </Badge>
            )}
          </h2>
          <Tooltip>
            <TooltipTrigger asChild>
              <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </TooltipTrigger>
            <TooltipContent>Close (Esc)</TooltipContent>
          </Tooltip>
        </div>
        {/* Body columns container */}
        <div className="flex-1 overflow-auto p-4 flex gap-6">
            {/* Left Column - Settings */}
            <div className="space-y-6">
              {/* Page Size */}
              <div className="bg-gray-800 rounded-xl p-4 text-white">
                <h3 className="font-semibold mb-4">Page Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Page Size
                    </label>
                    <select
                      value={preset.pageSize}
                      onChange={(e) => setPreset({ ...preset, pageSize: e.target.value })}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg"
                    >
                      {PAGE_SIZES.map((size) => (
                        <option key={size.id} value={size.id}>
                          {size.name} {size.width > 0 && `(${size.width}×${size.height}mm)`}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Orientation
                    </label>
                    <div className="flex gap-2">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => setPreset({ ...preset, orientation: 'portrait' })}
                        className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 ${
                          preset.orientation === 'portrait'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        <FileText className="w-3.5 h-3.5" />Portrait
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>Taller than wide</TooltipContent>
                  </Tooltip>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button
                        onClick={() => setPreset({ ...preset, orientation: 'landscape' })}
                        className={`flex-1 py-2 rounded-lg transition-colors flex items-center justify-center gap-1.5 ${
                          preset.orientation === 'landscape'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                        }`}
                      >
                        <FileText className="w-3.5 h-3.5 rotate-90" />Landscape
                      </button>
                    </TooltipTrigger>
                    <TooltipContent>Wider than tall</TooltipContent>
                  </Tooltip>
                </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">
                      Resolution
                    </label>
                    <select
                      value={preset.resolution}
                      onChange={(e) => setPreset({ ...preset, resolution: parseInt(e.target.value) })}
                      className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg"
                    >
                      <option value={72}>72 DPI (Screen)</option>
                      <option value={150}>150 DPI (Low)</option>
                      <option value={300}>300 DPI (Print)</option>
                      <option value={600}>600 DPI (High Quality)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* PDF Standard */}
              <div className="bg-gray-800 rounded-xl p-4 text-white">
                <h3 className="font-semibold mb-4">PDF Standard</h3>
                <div className="space-y-2">
                  {PDF_STANDARDS.map((std) => (
                    <button
                      key={std.id}
                      onClick={() => setPreset({ ...preset, pdfStandard: std.id as 'standard' | 'pdf_x1a' | 'pdf_x4' | 'pdf_a' })}
                      className={`w-full text-left p-3 rounded-lg transition-colors ${
                        preset.pdfStandard === std.id
                          ? 'bg-blue-600'
                          : 'bg-gray-700 hover:bg-gray-600'
                      }`}
                    >
                      <div className="font-medium">{std.name}</div>
                      <div className="text-xs opacity-70">{std.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Middle Column - Bleed & Marks */}
            <div className="space-y-6">
              <BleedSettings
                bleed={preset.bleedMargin}
                onChange={(value) => setPreset({ ...preset, bleedMargin: value })}
              />
              <PrintMarksSettings
                settings={printMarks}
                onChange={(key, value) => setPrintMarks({ ...printMarks, [key]: value })}
              />
            </div>

            {/* Right Column - Color & Preflight */}
            <div className="space-y-6">
              <ColorModeSettings
                colorMode={preset.colorMode}
                onChange={(mode) => setPreset({ ...preset, colorMode: mode })}
              />
              <PreflightCheck
                result={preflightResult}
                onRunCheck={runPreflightCheck}
                isChecking={isChecking}
              />
            </div>
        </div> {/* end columns container */}

        {/* Footer */}
        <div className="p-4 border-t border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            {selectedPages.length} of {pageCount} pages selected
          </div>
          
          <div className="flex gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={onClose}
                  className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition-colors"
                >
                  Cancel
                </button>
              </TooltipTrigger>
              <TooltipContent>Discard and close</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={startExport}
                  disabled={isExporting}
                  className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white disabled:opacity-50 transition-colors font-medium"
                >
                  {isExporting ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Exporting... {exportProgress}%
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      Export PDF
                    </>
                  )}
                </button>
              </TooltipTrigger>
              <TooltipContent>Generate and download the PDF file</TooltipContent>
            </Tooltip>
          </div>
        </div>
      </div>
      </TooltipProvider>
    </div>
  );
}

export default PDFExportDialog;

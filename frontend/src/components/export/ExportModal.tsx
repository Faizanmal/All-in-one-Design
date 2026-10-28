/**
 * Export Modal Component
 * Export project in various formats — honors scale, quality, and background options.
 */
'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Download, FileImage, FileText, Package } from 'lucide-react';
import { projectsAPI } from '@/lib/design-api';

interface ExportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: number;
}

export function ExportModal({ open, onOpenChange, projectId }: ExportModalProps) {
  const [format, setFormat] = useState<'png' | 'svg' | 'pdf' | 'jpg'>('png');
  const [options, setOptions] = useState({
    includeBackground: true,
    scale: 2,
    quality: 100,
  });
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setExporting(true);
    setError(null);

    const exportOpts = {
      multiplier: options.scale,
      quality: Math.min(1, Math.max(0.1, options.quality / 100)),
      includeBackground: options.includeBackground,
    };

    try {
      if (format === 'png' && window.canvasEditor?.exportAsPNG) {
        window.canvasEditor.exportAsPNG(exportOpts);
        onOpenChange(false);
        return;
      }
      if (format === 'svg' && window.canvasEditor?.exportAsSVG) {
        window.canvasEditor.exportAsSVG();
        onOpenChange(false);
        return;
      }
      if (format === 'jpg' && window.canvasEditor?.exportAsJPG) {
        window.canvasEditor.exportAsJPG(exportOpts);
        onOpenChange(false);
        return;
      }
      if (format === 'pdf' && window.canvasEditor?.exportAsPDF) {
        await window.canvasEditor.exportAsPDF(projectId);
        onOpenChange(false);
        return;
      }

      const blob = await projectsAPI.exportDesign(projectId, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `design.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      onOpenChange(false);
    } catch (err) {
      console.error('Export failed:', err);
      if (format === 'pdf' && window.canvasEditor?.exportAsPNG) {
        window.canvasEditor.exportAsPNG({
          ...exportOpts,
          fileName: 'design-fallback.png',
        });
        setError('PDF export failed. Downloaded PNG instead.');
        return;
      }
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Export design</DialogTitle>
          <DialogDescription>
            Download your canvas as an image or document.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-2">
            <Label>Format</Label>
            <RadioGroup
              value={format}
              onValueChange={(v) => setFormat(v as typeof format)}
              className="grid grid-cols-2 gap-2"
            >
              <label className="flex items-center gap-2 border rounded-md p-3 cursor-pointer">
                <RadioGroupItem value="png" />
                <FileImage className="h-4 w-4" />
                PNG
              </label>
              <label className="flex items-center gap-2 border rounded-md p-3 cursor-pointer">
                <RadioGroupItem value="jpg" />
                <FileImage className="h-4 w-4" />
                JPG
              </label>
              <label className="flex items-center gap-2 border rounded-md p-3 cursor-pointer">
                <RadioGroupItem value="svg" />
                <Package className="h-4 w-4" />
                SVG
              </label>
              <label className="flex items-center gap-2 border rounded-md p-3 cursor-pointer">
                <RadioGroupItem value="pdf" />
                <FileText className="h-4 w-4" />
                PDF
              </label>
            </RadioGroup>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox
              id="include-bg"
              checked={options.includeBackground}
              onCheckedChange={(checked) =>
                setOptions((prev) => ({ ...prev, includeBackground: Boolean(checked) }))
              }
            />
            <Label htmlFor="include-bg">Include background</Label>
          </div>

          {(format === 'png' || format === 'jpg' || format === 'pdf') && (
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="export-scale">Scale</Label>
                <select
                  id="export-scale"
                  className="w-full border rounded-md h-9 px-2 text-sm bg-background"
                  value={options.scale}
                  onChange={(e) =>
                    setOptions((prev) => ({ ...prev, scale: Number(e.target.value) }))
                  }
                >
                  <option value={1}>1x</option>
                  <option value={2}>2x</option>
                  <option value={3}>3x</option>
                </select>
              </div>
              {format === 'jpg' && (
                <div className="space-y-1">
                  <Label htmlFor="export-quality">Quality ({options.quality}%)</Label>
                  <input
                    id="export-quality"
                    type="range"
                    min={50}
                    max={100}
                    value={options.quality}
                    onChange={(e) =>
                      setOptions((prev) => ({ ...prev, quality: Number(e.target.value) }))
                    }
                    className="w-full"
                  />
                </div>
              )}
            </div>
          )}

          {error && <p className="text-sm text-destructive">{error}</p>}

          <Button className="w-full gap-2" onClick={handleExport} disabled={exporting}>
            <Download className="h-4 w-4" />
            {exporting ? 'Exporting…' : `Export ${format.toUpperCase()}`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

/**
 * Export Modal Component
 * Export project in various formats
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

    try {
      if (format === 'png' && window.canvasEditor?.exportAsPNG) {
        window.canvasEditor.exportAsPNG();
        onOpenChange(false);
        return;
      }
      if (format === 'svg' && window.canvasEditor?.exportAsSVG) {
        window.canvasEditor.exportAsSVG();
        onOpenChange(false);
        return;
      }
      if (format === 'jpg' && window.canvasEditor?.exportAsJPG) {
        window.canvasEditor.exportAsJPG();
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

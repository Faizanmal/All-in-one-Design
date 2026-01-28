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

interface ExportModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: number;
}

export function ExportModal({ open, onOpenChange, projectId }: ExportModalProps) {
  const [format, setFormat] = useState<'png' | 'svg' | 'pdf' | 'figma'>('png');
  const [options, setOptions] = useState({
    includeBackground: true,
    scale: 2,
    quality: 100
  });
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    setExporting(true);

    try {
      const token = localStorage.getItem('token');
      let endpoint = '';

      switch (format) {
        case 'svg':
          endpoint = `/api/projects/enhanced-export/projects/${projectId}/export-svg/`;
          break;
        case 'pdf':
          endpoint = `/api/projects/enhanced-export/projects/${projectId}/export-pdf/`;
          break;
        case 'figma':
          endpoint = `/api/projects/enhanced-export/projects/${projectId}/export-figma/`;
          break;
        default:
          endpoint = `/api/projects/enhanced-export/projects/${projectId}/export-png/`;
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          include_background: options.includeBackground,
          scale: options.scale,
          quality: options.quality
        })
      });

      if (res.ok) {
        const data = await res.json();

        if (format === 'figma') {
          // Download JSON file
          const blob = new Blob([JSON.stringify(data.figma_json, null, 2)], {
            type: 'application/json'
          });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${data.project_name}.figma.json`;
          a.click();
        } else if (data.download_url) {
          // Download file from URL
          const a = document.createElement('a');
          a.href = data.download_url;
          a.download = data.filename || `export.${format}`;
          a.click();
        }

        onOpenChange(false);
      } else {
        alert('Export failed. Please try again.');
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Project</DialogTitle>
          <DialogDescription>
            Choose a format and options for exporting your design
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Format Selection */}
          <div className="space-y-3">
            <Label>Export Format</Label>
            <RadioGroup value={format} onValueChange={(val: string) => setFormat(val as 'png' | 'svg' | 'pdf' | 'figma')}>
              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="png" id="png" />
                <FileImage className="w-4 h-4 text-blue-500" />
                <div className="flex-1">
                  <Label htmlFor="png" className="cursor-pointer font-medium">PNG</Label>
                  <p className="text-xs text-gray-500">High-quality raster image</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="svg" id="svg" />
                <FileText className="w-4 h-4 text-green-500" />
                <div className="flex-1">
                  <Label htmlFor="svg" className="cursor-pointer font-medium">SVG</Label>
                  <p className="text-xs text-gray-500">Scalable vector graphics</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="pdf" id="pdf" />
                <FileText className="w-4 h-4 text-red-500" />
                <div className="flex-1">
                  <Label htmlFor="pdf" className="cursor-pointer font-medium">PDF</Label>
                  <p className="text-xs text-gray-500">Portable document format</p>
                </div>
              </div>

              <div className="flex items-center space-x-2 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <RadioGroupItem value="figma" id="figma" />
                <Package className="w-4 h-4 text-purple-500" />
                <div className="flex-1">
                  <Label htmlFor="figma" className="cursor-pointer font-medium">Figma JSON</Label>
                  <p className="text-xs text-gray-500">Import to Figma</p>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <Label>Options</Label>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="background"
                checked={options.includeBackground}
                onCheckedChange={(checked) =>
                  setOptions({ ...options, includeBackground: checked as boolean })
                }
              />
              <Label htmlFor="background" className="cursor-pointer">
                Include background
              </Label>
            </div>

            {(format === 'png' || format === 'pdf') && (
              <div className="space-y-2">
                <Label htmlFor="scale">Scale: {options.scale}x</Label>
                <input
                  id="scale"
                  type="range"
                  min="1"
                  max="4"
                  step="0.5"
                  value={options.scale}
                  onChange={(e) =>
                    setOptions({ ...options, scale: parseFloat(e.target.value) })
                  }
                  className="w-full"
                />
              </div>
            )}

            {format === 'png' && (
              <div className="space-y-2">
                <Label htmlFor="quality">Quality: {options.quality}%</Label>
                <input
                  id="quality"
                  type="range"
                  min="10"
                  max="100"
                  step="10"
                  value={options.quality}
                  onChange={(e) =>
                    setOptions({ ...options, quality: parseInt(e.target.value) })
                  }
                  className="w-full"
                />
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={exporting}>
            <Download className="w-4 h-4 mr-2" />
            {exporting ? 'Exporting...' : 'Export'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

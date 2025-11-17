'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Download, FileText, Image, Code, Package, Zap,
  Share2, Printer, CheckCircle, Loader2, X
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface ExportFormat {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  extensions: string[];
  vector: boolean;
}

const exportFormats: ExportFormat[] = [
  {
    id: 'pdf',
    name: 'PDF',
    icon: <FileText className="h-5 w-5" />,
    description: 'Print-ready documents and presentations',
    extensions: ['.pdf'],
    vector: true
  },
  {
    id: 'svg',
    name: 'SVG',
    icon: <Code className="h-5 w-5" />,
    description: 'Scalable vector graphics for web',
    extensions: ['.svg'],
    vector: true
  },
  {
    id: 'png',
    name: 'PNG',
    icon: <Image className="h-5 w-5" />,
    description: 'High-quality raster images',
    extensions: ['.png'],
    vector: false
  },
  {
    id: 'figma',
    name: 'Figma JSON',
    icon: <Package className="h-5 w-5" />,
    description: 'Import directly into Figma',
    extensions: ['.figma.json'],
    vector: true
  }
];

export default function ExportPage() {
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportComplete, setExportComplete] = useState(false);
  
  // PDF options
  const [pdfOptions, setPdfOptions] = useState({
    quality: 'high',
    pageSize: 'A4',
    orientation: 'portrait',
    compress: true,
    includeMetadata: true
  });
  
  // SVG options
  const [svgOptions, setSvgOptions] = useState({
    optimize: true,
    removeIds: true,
    minify: true,
    embedFonts: true
  });
  
  // Social media options
  const [socialPlatforms, setSocialPlatforms] = useState({
    instagram: true,
    facebook: true,
    twitter: true,
    linkedin: false
  });

  const handleExport = async (type: string) => {
    setExporting(true);
    setExportProgress(0);
    setExportComplete(false);
    
    // Simulate export progress
    const interval = setInterval(() => {
      setExportProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setExporting(false);
          setExportComplete(true);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
    
    try {
      // Replace with actual API call
      const projectId = 1; // Get from context
      let endpoint = '';
      
      switch (type) {
        case 'pdf':
          endpoint = `/api/v1/projects/${projectId}/export/pdf/`;
          break;
        case 'svg':
          endpoint = `/api/v1/projects/${projectId}/export/svg/optimized/`;
          break;
        case 'figma':
          endpoint = `/api/v1/projects/${projectId}/export/figma/`;
          break;
        case 'social':
          endpoint = `/api/v1/projects/${projectId}/export/social-pack/`;
          break;
        case 'print':
          endpoint = `/api/v1/projects/${projectId}/export/print-ready/`;
          break;
      }
      
      // API call would go here
      console.log(`Exporting to ${endpoint}`);
      
    } catch (error) {
      console.error('Export failed:', error);
      clearInterval(interval);
      setExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-2">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
              <Download className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Export Manager
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Export your designs in multiple formats with advanced options
          </p>
        </motion.div>

        <Tabs defaultValue="single" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="single">
              <Download className="mr-2 h-4 w-4" />
              Single Export
            </TabsTrigger>
            <TabsTrigger value="batch">
              <Package className="mr-2 h-4 w-4" />
              Batch Export
            </TabsTrigger>
            <TabsTrigger value="social">
              <Share2 className="mr-2 h-4 w-4" />
              Social Media
            </TabsTrigger>
            <TabsTrigger value="print">
              <Printer className="mr-2 h-4 w-4" />
              Print Ready
            </TabsTrigger>
          </TabsList>

          {/* Single Export Tab */}
          <TabsContent value="single">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Format Selection */}
              <div className="lg:col-span-1">
                <Card>
                  <CardHeader>
                    <CardTitle>Export Format</CardTitle>
                    <CardDescription>
                      Choose your preferred format
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {exportFormats.map((format) => (
                      <motion.button
                        key={format.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setSelectedFormat(format.id)}
                        className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                          selectedFormat === format.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <div className={`p-2 rounded-lg ${
                            selectedFormat === format.id
                              ? 'bg-blue-500 text-white'
                              : 'bg-gray-100'
                          }`}>
                            {format.icon}
                          </div>
                          <div className="flex-1">
                            <div className="font-semibold flex items-center space-x-2">
                              <span>{format.name}</span>
                              {format.vector && (
                                <Badge variant="outline" className="text-xs">Vector</Badge>
                              )}
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {format.description}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {format.extensions.join(', ')}
                            </div>
                          </div>
                        </div>
                      </motion.button>
                    ))}
                  </CardContent>
                </Card>
              </div>

              {/* Options Panel */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Export Options</CardTitle>
                    <CardDescription>
                      Customize your export settings
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {selectedFormat === 'pdf' && (
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label>Quality</Label>
                          <Select
                            value={pdfOptions.quality}
                            onValueChange={(value) => setPdfOptions({ ...pdfOptions, quality: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="low">Low (smaller file)</SelectItem>
                              <SelectItem value="medium">Medium</SelectItem>
                              <SelectItem value="high">High</SelectItem>
                              <SelectItem value="ultra">Ultra (largest file)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Page Size</Label>
                          <Select
                            value={pdfOptions.pageSize}
                            onValueChange={(value) => setPdfOptions({ ...pdfOptions, pageSize: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="A4">A4 (210 × 297 mm)</SelectItem>
                              <SelectItem value="A3">A3 (297 × 420 mm)</SelectItem>
                              <SelectItem value="Letter">Letter (8.5 × 11 in)</SelectItem>
                              <SelectItem value="Legal">Legal (8.5 × 14 in)</SelectItem>
                              <SelectItem value="Custom">Custom</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Orientation</Label>
                          <Select
                            value={pdfOptions.orientation}
                            onValueChange={(value) => setPdfOptions({ ...pdfOptions, orientation: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="portrait">Portrait</SelectItem>
                              <SelectItem value="landscape">Landscape</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-3 pt-4 border-t">
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              checked={pdfOptions.compress}
                              onCheckedChange={(checked) => 
                                setPdfOptions({ ...pdfOptions, compress: checked as boolean })
                              }
                            />
                            <Label>Compress PDF (reduce file size)</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Checkbox
                              checked={pdfOptions.includeMetadata}
                              onCheckedChange={(checked) => 
                                setPdfOptions({ ...pdfOptions, includeMetadata: checked as boolean })
                              }
                            />
                            <Label>Include metadata</Label>
                          </div>
                        </div>
                      </div>
                    )}

                    {selectedFormat === 'svg' && (
                      <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={svgOptions.optimize}
                            onCheckedChange={(checked) => 
                              setSvgOptions({ ...svgOptions, optimize: checked as boolean })
                            }
                          />
                          <Label>Optimize SVG (remove unnecessary data)</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={svgOptions.removeIds}
                            onCheckedChange={(checked) => 
                              setSvgOptions({ ...svgOptions, removeIds: checked as boolean })
                            }
                          />
                          <Label>Remove IDs</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={svgOptions.minify}
                            onCheckedChange={(checked) => 
                              setSvgOptions({ ...svgOptions, minify: checked as boolean })
                            }
                          />
                          <Label>Minify output</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={svgOptions.embedFonts}
                            onCheckedChange={(checked) => 
                              setSvgOptions({ ...svgOptions, embedFonts: checked as boolean })
                            }
                          />
                          <Label>Embed fonts</Label>
                        </div>
                        
                        {svgOptions.optimize && (
                          <div className="mt-4 p-3 bg-green-50 rounded-lg text-sm text-green-700">
                            <Zap className="inline h-4 w-4 mr-2" />
                            Optimization can reduce file size by 30-50%
                          </div>
                        )}
                      </div>
                    )}

                    {selectedFormat === 'figma' && (
                      <div className="space-y-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <h4 className="font-semibold text-blue-900 mb-2">About Figma Export</h4>
                          <p className="text-sm text-blue-700">
                            Export your design as Figma-compatible JSON that can be imported directly into Figma.
                            Includes layers, shapes, text, and styling information.
                          </p>
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2">
                            <Checkbox defaultChecked />
                            <Label>Include constraints and auto-layout</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Checkbox defaultChecked />
                            <Label>Convert effects (shadows, blurs)</Label>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Checkbox />
                            <Label>Flatten groups</Label>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Export Button */}
                    <div className="mt-6 space-y-3">
                      {exporting && (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Exporting...</span>
                            <span>{exportProgress}%</span>
                          </div>
                          <Progress value={exportProgress} />
                        </div>
                      )}

                      {exportComplete && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-3 bg-green-50 text-green-700 rounded-lg flex items-center justify-between"
                        >
                          <div className="flex items-center">
                            <CheckCircle className="mr-2 h-5 w-5" />
                            <span>Export complete!</span>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setExportComplete(false)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </motion.div>
                      )}

                      <Button
                        onClick={() => handleExport(selectedFormat)}
                        disabled={exporting}
                        className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700"
                        size="lg"
                      >
                        {exporting ? (
                          <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Exporting...
                          </>
                        ) : (
                          <>
                            <Download className="mr-2 h-5 w-5" />
                            Export as {selectedFormat.toUpperCase()}
                          </>
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Batch Export Tab */}
          <TabsContent value="batch">
            <Card>
              <CardHeader>
                <CardTitle>Batch Export</CardTitle>
                <CardDescription>
                  Export multiple projects at once in a ZIP file
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Package className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-600">
                    Select multiple projects from your dashboard to enable batch export
                  </p>
                  <Button className="mt-4">
                    Go to Projects
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Social Media Tab */}
          <TabsContent value="social">
            <Card>
              <CardHeader>
                <CardTitle>Social Media Pack</CardTitle>
                <CardDescription>
                  Export in all required sizes for social media platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-3">Select Platforms</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(socialPlatforms).map(([platform, enabled]) => (
                        <div key={platform} className="flex items-center space-x-2">
                          <Checkbox
                            checked={enabled}
                            onCheckedChange={(checked) =>
                              setSocialPlatforms({ ...socialPlatforms, [platform]: checked as boolean })
                            }
                          />
                          <Label className="capitalize">{platform}</Label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900 mb-2">Included Sizes</h4>
                    <div className="text-sm text-blue-700 space-y-1">
                      {socialPlatforms.instagram && <div>• Instagram: Post (1080×1080), Story (1080×1920), Profile (320×320)</div>}
                      {socialPlatforms.facebook && <div>• Facebook: Post (1200×630), Cover (820×312), Profile (180×180)</div>}
                      {socialPlatforms.twitter && <div>• Twitter: Post (1200×675), Header (1500×500), Profile (400×400)</div>}
                      {socialPlatforms.linkedin && <div>• LinkedIn: Post (1200×627), Cover (1584×396), Profile (400×400)</div>}
                    </div>
                  </div>

                  <Button
                    onClick={() => handleExport('social')}
                    disabled={!Object.values(socialPlatforms).some(v => v)}
                    className="w-full"
                    size="lg"
                  >
                    <Download className="mr-2 h-5 w-5" />
                    Export Social Media Pack
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Print Ready Tab */}
          <TabsContent value="print">
            <Card>
              <CardHeader>
                <CardTitle>Print-Ready Export</CardTitle>
                <CardDescription>
                  Export with bleed marks and print specifications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Print Size</Label>
                    <Select defaultValue="A4">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="A4">A4 (210 × 297 mm)</SelectItem>
                        <SelectItem value="A3">A3 (297 × 420 mm)</SelectItem>
                        <SelectItem value="A5">A5 (148 × 210 mm)</SelectItem>
                        <SelectItem value="Letter">US Letter</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Bleed (mm)</Label>
                    <Select defaultValue="3">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="0">No bleed</SelectItem>
                        <SelectItem value="3">3mm (standard)</SelectItem>
                        <SelectItem value="5">5mm</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Checkbox defaultChecked />
                      <Label>Include crop marks</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox defaultChecked />
                      <Label>Convert to CMYK color mode</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox />
                      <Label>Embed all fonts</Label>
                    </div>
                  </div>

                  <Button
                    onClick={() => handleExport('print')}
                    className="w-full"
                    size="lg"
                  >
                    <Printer className="mr-2 h-5 w-5" />
                    Export Print-Ready PDF
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

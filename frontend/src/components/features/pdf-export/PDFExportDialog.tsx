"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Slider } from '@/components/ui/slider';
import { FileDown, FileType, Palette, Ruler, CheckCircle2, AlertCircle, BookOpen } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export const PDFExportDialog: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { toast } = useToast();

  const handleExport = () => {
    toast({ title: "Exporting PDF", description: "Your design is being exported with print settings" });
    setTimeout(() => {
      toast({ title: "Export complete", description: "PDF downloaded successfully" });
      setIsOpen(false);
    }, 2000);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <FileDown className="h-4 w-4 mr-2" />
          Export PDF
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle>Export PDF with Print Settings</DialogTitle>
          <DialogDescription>Configure professional print-ready PDF export settings</DialogDescription>
        </DialogHeader>
        <ScrollArea className="max-h-[70vh] pr-4">
          <Tabs defaultValue="basic" className="space-y-4">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="basic">Basic</TabsTrigger>
              <TabsTrigger value="bleed">Bleed</TabsTrigger>
              <TabsTrigger value="marks">Marks</TabsTrigger>
              <TabsTrigger value="color">Color</TabsTrigger>
              <TabsTrigger value="preflight">Preflight</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Page Size</Label>
                  <Select defaultValue="a4">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="a4">A4 (210 × 297 mm)</SelectItem>
                      <SelectItem value="a3">A3 (297 × 420 mm)</SelectItem>
                      <SelectItem value="letter">Letter (8.5 × 11 in)</SelectItem>
                      <SelectItem value="tabloid">Tabloid (11 × 17 in)</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Orientation</Label>
                  <Select defaultValue="portrait">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="portrait">Portrait</SelectItem>
                      <SelectItem value="landscape">Landscape</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Quality</Label>
                <Select defaultValue="high">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="screen">Screen (72 DPI)</SelectItem>
                    <SelectItem value="high">High Quality (150 DPI)</SelectItem>
                    <SelectItem value="print">Print (300 DPI)</SelectItem>
                    <SelectItem value="prepress">Prepress (600 DPI)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            <TabsContent value="bleed">
              <BleedSettings />
            </TabsContent>

            <TabsContent value="marks">
              <PrintMarksSettings />
            </TabsContent>

            <TabsContent value="color">
              <ColorModeSettings />
            </TabsContent>

            <TabsContent value="preflight">
              <PreflightCheck />
            </TabsContent>
          </Tabs>
        </ScrollArea>

        <div className="flex justify-between items-center pt-4 border-t">
          <SpreadView />
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setIsOpen(false)}>Cancel</Button>
            <Button onClick={handleExport}>
              <FileDown className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export const BleedSettings: React.FC = () => {
  const [bleed, setBleed] = useState([3]);

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <Label>Enable Bleed</Label>
            <p className="text-sm text-muted-foreground">Add bleed area for professional printing</p>
          </div>
          <Switch defaultChecked />
        </div>
        
        <Separator />
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label>Bleed Size: {bleed[0]} mm</Label>
            <Badge variant="secondary">Standard: 3mm</Badge>
          </div>
          <Slider
            value={bleed}
            onValueChange={setBleed}
            min={0}
            max={10}
            step={0.5}
            className="w-full"
          />
          <div className="grid grid-cols-4 gap-2">
            {['Top', 'Right', 'Bottom', 'Left'].map((side) => (
              <div key={side} className="text-center p-2 border rounded">
                <p className="text-xs text-muted-foreground mb-1">{side}</p>
                <p className="text-sm font-semibold">{bleed[0]} mm</p>
              </div>
            ))}
          </div>
        </div>

        <Separator />

        <div className="p-4 bg-muted rounded-lg">
          <div className="flex gap-2 mb-2">
            <Ruler className="h-5 w-5" />
            <p className="font-medium">What is Bleed?</p>
          </div>
          <p className="text-sm text-muted-foreground">
            Bleed is the area outside your design that will be trimmed off after printing. 
            It ensures no white edges appear if the cutting is slightly off.
          </p>
        </div>
      </div>
    </div>
  );
};

export const PrintMarksSettings: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <Label>Crop Marks</Label>
          <p className="text-sm text-muted-foreground">Corner marks for trimming</p>
        </div>
        <Switch defaultChecked />
      </div>
      <Separator />
      <div className="flex items-center justify-between">
        <div>
          <Label>Registration Marks</Label>
          <p className="text-sm text-muted-foreground">Alignment marks for color printing</p>
        </div>
        <Switch defaultChecked />
      </div>
      <Separator />
      <div className="flex items-center justify-between">
        <div>
          <Label>Color Bars</Label>
          <p className="text-sm text-muted-foreground">Color accuracy reference</p>
        </div>
        <Switch />
      </div>
      <Separator />
      <div className="flex items-center justify-between">
        <div>
          <Label>Page Information</Label>
          <p className="text-sm text-muted-foreground">Filename and date stamp</p>
        </div>
        <Switch />
      </div>
      <Separator />
      <div className="space-y-2">
        <Label>Mark Offset</Label>
        <div className="flex items-center gap-2">
          <Input type="number" defaultValue="5" className="flex-1" />
          <span className="text-sm text-muted-foreground">mm</span>
        </div>
      </div>
    </div>
  );
};

export const ColorModeSettings: React.FC = () => {
  const [colorMode, setColorMode] = useState('cmyk');

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label>Color Mode</Label>
        <Select value={colorMode} onValueChange={setColorMode}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="rgb">RGB (Screen)</SelectItem>
            <SelectItem value="cmyk">CMYK (Print)</SelectItem>
            <SelectItem value="grayscale">Grayscale</SelectItem>
            <SelectItem value="spot">Spot Colors</SelectItem>
          </SelectContent>
        </Select>
        <p className="text-sm text-muted-foreground">
          {colorMode === 'cmyk' && 'Best for professional printing'}
          {colorMode === 'rgb' && 'Best for digital display'}
          {colorMode === 'grayscale' && 'Black and white printing'}
          {colorMode === 'spot' && 'Specific ink colors (Pantone)'}
        </p>
      </div>

      <Separator />

      <div className="flex items-center justify-between">
        <div>
          <Label>Embed Color Profile</Label>
          <p className="text-sm text-muted-foreground">ICC profile for accurate colors</p>
        </div>
        <Switch defaultChecked />
      </div>

      <Separator />

      <div className="space-y-2">
        <Label>Color Profile</Label>
        <Select defaultValue="coated">
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="coated">Coated FOGRA39</SelectItem>
            <SelectItem value="uncoated">Uncoated FOGRA29</SelectItem>
            <SelectItem value="srgb">sRGB IEC61966-2.1</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      <div className="p-4 bg-muted rounded-lg space-y-2">
        <div className="flex gap-2">
          <Palette className="h-5 w-5" />
          <p className="font-medium">Color Conversion</p>
        </div>
        <p className="text-sm text-muted-foreground">
          All colors will be converted to {colorMode.toUpperCase()} mode. 
          Some color shifts may occur during conversion.
        </p>
      </div>
    </div>
  );
};

export const PreflightCheck: React.FC = () => {
  const checks = [
    { name: 'Image Resolution', status: 'pass', message: 'All images are 300 DPI or higher' },
    { name: 'Color Mode', status: 'pass', message: 'CMYK color mode set' },
    { name: 'Fonts Embedded', status: 'pass', message: 'All fonts properly embedded' },
    { name: 'Bleed Settings', status: 'warning', message: '3mm bleed recommended, currently 0mm' },
    { name: 'Transparency', status: 'pass', message: 'No transparency issues detected' },
    { name: 'Overprint', status: 'pass', message: 'Overprint settings correct' },
  ];

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle2 className="h-5 w-5 text-green-500" />
          <p className="font-semibold">Ready for Print</p>
        </div>
        <p className="text-sm text-muted-foreground">
          Your document has passed most preflight checks. Review warnings below.
        </p>
      </div>

      <div className="space-y-2">
        {checks.map((check, index) => (
          <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
            {check.status === 'pass' ? (
              <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <p className="font-medium">{check.name}</p>
              <p className="text-sm text-muted-foreground">{check.message}</p>
            </div>
            <Badge variant={check.status === 'pass' ? 'default' : 'secondary'}>
              {check.status}
            </Badge>
          </div>
        ))}
      </div>

      <Button variant="outline" className="w-full">
        <BookOpen className="h-4 w-4 mr-2" />
        View Detailed Report
      </Button>
    </div>
  );
};

export const SpreadView: React.FC = () => {
  return (
    <div className="flex items-center gap-2">
      <Label className="text-sm">Spread View</Label>
      <Switch />
    </div>
  );
};
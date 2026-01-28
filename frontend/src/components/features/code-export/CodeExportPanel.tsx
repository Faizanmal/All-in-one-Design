"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, Download, Code2, FileCode, Layers, Ruler, Palette, Check } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface CodeExportPanelProps {
  projectId?: string;
  selectedElements?: unknown[];
}

export const CodeExportPanel: React.FC<CodeExportPanelProps> = ({ projectId, selectedElements = [] }) => {
  const [framework, setFramework] = useState('react');
  const [styling, setStyling] = useState('tailwind');
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const generateCode = () => {
    // Mock code generation
    return `import React from 'react';

export const Component = () => {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">Generated Component</h2>
        <p className="text-gray-600">Your design exported as code</p>
      </div>
    </div>
  );
};`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateCode());
    setCopied(true);
    toast({ title: "Copied to clipboard", description: "Code copied successfully" });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([generateCode()], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `component.${framework}.tsx`;
    a.click();
    toast({ title: "Downloaded", description: "Code file downloaded successfully" });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5" />
              Code Export
            </CardTitle>
            <CardDescription>Export your design as production-ready code</CardDescription>
          </div>
          <Badge variant="secondary">{selectedElements.length} elements</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Framework</label>
            <Select value={framework} onValueChange={setFramework}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="react">React</SelectItem>
                <SelectItem value="vue">Vue</SelectItem>
                <SelectItem value="angular">Angular</SelectItem>
                <SelectItem value="svelte">Svelte</SelectItem>
                <SelectItem value="html">HTML</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Styling</label>
            <Select value={styling} onValueChange={setStyling}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="tailwind">Tailwind CSS</SelectItem>
                <SelectItem value="css">CSS Modules</SelectItem>
                <SelectItem value="styled">Styled Components</SelectItem>
                <SelectItem value="emotion">Emotion</SelectItem>
                <SelectItem value="sass">SASS</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Separator />

        <div className="relative">
          <ScrollArea className="h-[300px] w-full rounded-md border bg-slate-950 p-4">
            <pre className="text-sm text-slate-50">
              <code>{generateCode()}</code>
            </pre>
          </ScrollArea>
          <div className="absolute top-2 right-2 flex gap-2">
            <Button size="sm" variant="secondary" onClick={handleCopy}>
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </Button>
            <Button size="sm" variant="secondary" onClick={handleDownload}>
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex gap-2">
          <Button className="flex-1">
            <FileCode className="h-4 w-4 mr-2" />
            Export Full Project
          </Button>
          <Button variant="outline">
            View Docs
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export const DesignSpecPanel: React.FC = () => {
  const specs = [
    { label: 'Width', value: '1920px', icon: Ruler },
    { label: 'Height', value: '1080px', icon: Ruler },
    { label: 'Layers', value: '24', icon: Layers },
    { label: 'Colors', value: '12', icon: Palette },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Design Specifications</CardTitle>
        <CardDescription>Technical details and measurements</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          {specs.map((spec) => (
            <div key={spec.label} className="flex items-center gap-3 p-4 border rounded-lg">
              <spec.icon className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">{spec.label}</p>
                <p className="text-lg font-semibold">{spec.value}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export const DeveloperHandoff: React.FC = () => {
  const [activeTab, setActiveTab] = useState('assets');

  return (
    <Card>
      <CardHeader>
        <CardTitle>Developer Handoff</CardTitle>
        <CardDescription>Complete package for development team</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="assets">Assets</TabsTrigger>
            <TabsTrigger value="tokens">Tokens</TabsTrigger>
            <TabsTrigger value="docs">Documentation</TabsTrigger>
          </TabsList>
          <TabsContent value="assets" className="space-y-4">
            <div className="grid gap-2">
              <Button variant="outline" className="justify-start">
                <Download className="h-4 w-4 mr-2" />
                Download All Assets (.zip)
              </Button>
              <Button variant="outline" className="justify-start">
                <FileCode className="h-4 w-4 mr-2" />
                Export SVG Sprites
              </Button>
              <Button variant="outline" className="justify-start">
                <Palette className="h-4 w-4 mr-2" />
                Export Icon Set
              </Button>
            </div>
          </TabsContent>
          <TabsContent value="tokens" className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Design tokens for consistent styling</p>
              <Button className="w-full">Generate Design Tokens</Button>
            </div>
          </TabsContent>
          <TabsContent value="docs" className="space-y-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Automated documentation for developers</p>
              <Button className="w-full">Generate Documentation</Button>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};
/**
 * Design Tokens Manager
 * Centralized design system tokens (colors, typography, spacing)
 */
'use client';

import React, { useState } from 'react';
import { Palette, Type, Ruler, Download, Upload, Copy } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';

interface ColorToken {
  name: string;
  value: string;
  description?: string;
}

interface TypographyToken {
  name: string;
  fontFamily: string;
  fontSize: string;
  fontWeight: string;
  lineHeight: string;
}

interface SpacingToken {
  name: string;
  value: string;
}

interface DesignTokensManagerProps {
  onApplyToken?: (token: unknown) => void;
}

export function DesignTokensManager({ onApplyToken }: DesignTokensManagerProps) {
  const { toast } = useToast();
  
  const [colorTokens, setColorTokens] = useState<ColorToken[]>([
    { name: 'primary', value: '#3B82F6', description: 'Primary brand color' },
    { name: 'secondary', value: '#10B981', description: 'Secondary accent' },
    { name: 'accent', value: '#F59E0B', description: 'Accent color' },
    { name: 'background', value: '#FFFFFF', description: 'Background' },
    { name: 'foreground', value: '#1F2937', description: 'Text color' },
    { name: 'muted', value: '#9CA3AF', description: 'Muted text' },
    { name: 'border', value: '#E5E7EB', description: 'Border color' },
    { name: 'success', value: '#10B981', description: 'Success state' },
    { name: 'warning', value: '#F59E0B', description: 'Warning state' },
    { name: 'error', value: '#EF4444', description: 'Error state' },
  ]);

  const [typographyTokens, setTypographyTokens] = useState<TypographyToken[]>([
    { name: 'h1', fontFamily: 'Inter', fontSize: '48px', fontWeight: '700', lineHeight: '1.2' },
    { name: 'h2', fontFamily: 'Inter', fontSize: '36px', fontWeight: '700', lineHeight: '1.3' },
    { name: 'h3', fontFamily: 'Inter', fontSize: '24px', fontWeight: '600', lineHeight: '1.4' },
    { name: 'body', fontFamily: 'Inter', fontSize: '16px', fontWeight: '400', lineHeight: '1.5' },
    { name: 'small', fontFamily: 'Inter', fontSize: '14px', fontWeight: '400', lineHeight: '1.5' },
    { name: 'caption', fontFamily: 'Inter', fontSize: '12px', fontWeight: '400', lineHeight: '1.4' },
  ]);

  const [spacingTokens, setSpacingTokens] = useState<SpacingToken[]>([
    { name: 'xs', value: '4px' },
    { name: 'sm', value: '8px' },
    { name: 'md', value: '16px' },
    { name: 'lg', value: '24px' },
    { name: 'xl', value: '32px' },
    { name: '2xl', value: '48px' },
    { name: '3xl', value: '64px' },
  ]);

  // Add new color token
  const addColorToken = () => {
    setColorTokens([...colorTokens, { name: 'new-color', value: '#000000' }]);
  };

  // Update color token
  const updateColorToken = (index: number, updates: Partial<ColorToken>) => {
    const newTokens = [...colorTokens];
    newTokens[index] = { ...newTokens[index], ...updates };
    setColorTokens(newTokens);
  };

  // Delete color token
  const deleteColorToken = (index: number) => {
    setColorTokens(colorTokens.filter((_, i) => i !== index));
  };

  // Export tokens as JSON
  const exportTokens = () => {
    const tokens = {
      colors: colorTokens,
      typography: typographyTokens,
      spacing: spacingTokens,
    };

    const blob = new Blob([JSON.stringify(tokens, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = 'design-tokens.json';
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);

    toast({ title: 'Tokens exported successfully!' });
  };

  // Import tokens from JSON
  const importTokens = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const tokens = JSON.parse(event.target?.result as string);
            if (tokens.colors) setColorTokens(tokens.colors);
            if (tokens.typography) setTypographyTokens(tokens.typography);
            if (tokens.spacing) setSpacingTokens(tokens.spacing);
            toast({ title: 'Tokens imported successfully!' });
          } catch (_error) {
            toast({ title: 'Failed to import tokens', variant: 'destructive' });
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  // Copy CSS variables
  const copyCSSVariables = () => {
    const css = `:root {\n  /* Colors */\n${colorTokens.map(t => `  --${t.name}: ${t.value};`).join('\n')}\n\n  /* Typography */\n${typographyTokens.map(t => `  --font-${t.name}: ${t.fontFamily};\n  --font-size-${t.name}: ${t.fontSize};`).join('\n')}\n\n  /* Spacing */\n${spacingTokens.map(t => `  --spacing-${t.name}: ${t.value};`).join('\n')}\n}`;
    
    navigator.clipboard.writeText(css);
    toast({ title: 'CSS variables copied to clipboard!' });
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Palette className="w-4 h-4" />
            Design Tokens
          </span>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={importTokens}>
              <Upload className="w-3.5 h-3.5" />
            </Button>
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={exportTokens}>
              <Download className="w-3.5 h-3.5" />
            </Button>
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={copyCSSVariables}>
              <Copy className="w-3.5 h-3.5" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex-1 p-0 overflow-hidden">
        <Tabs defaultValue="colors" className="h-full flex flex-col">
          <TabsList className="grid w-full grid-cols-3 mx-2">
            <TabsTrigger value="colors" className="text-xs">
              <Palette className="w-3 h-3 mr-1" />
              Colors
            </TabsTrigger>
            <TabsTrigger value="typography" className="text-xs">
              <Type className="w-3 h-3 mr-1" />
              Type
            </TabsTrigger>
            <TabsTrigger value="spacing" className="text-xs">
              <Ruler className="w-3 h-3 mr-1" />
              Spacing
            </TabsTrigger>
          </TabsList>

          <ScrollArea className="flex-1">
            {/* Colors Tab */}
            <TabsContent value="colors" className="p-4 space-y-3 mt-0">
              {colorTokens.map((token, index) => (
                <div key={index} className="flex items-center gap-2 p-2 rounded border bg-card">
                  <div
                    className="w-10 h-10 rounded border-2 border-background shadow-sm cursor-pointer"
                    style={{ backgroundColor: token.value }}
                    onClick={() => {
                      const input = document.createElement('input');
                      input.type = 'color';
                      input.value = token.value;
                      input.onchange = (e) => {
                        updateColorToken(index, { value: (e.target as HTMLInputElement).value });
                      };
                      input.click();
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <Input
                      value={token.name}
                      onChange={(e) => updateColorToken(index, { name: e.target.value })}
                      className="h-7 text-sm mb-1"
                      placeholder="Token name"
                    />
                    {token.description && (
                      <p className="text-xs text-muted-foreground">{token.description}</p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0"
                    onClick={() => {
                      navigator.clipboard.writeText(token.value);
                      toast({ title: 'Color copied!', description: token.value });
                    }}
                  >
                    <Copy className="w-3.5 h-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 w-7 p-0 text-destructive"
                    onClick={() => deleteColorToken(index)}
                  >
                    ×
                  </Button>
                </div>
              ))}
              <Button variant="outline" size="sm" className="w-full" onClick={addColorToken}>
                Add Color Token
              </Button>
            </TabsContent>

            {/* Typography Tab */}
            <TabsContent value="typography" className="p-4 space-y-3 mt-0">
              {typographyTokens.map((token, index) => (
                <Card key={index} className="p-3">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline">{token.name}</Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 px-2"
                      onClick={() => onApplyToken?.(token)}
                    >
                      Apply
                    </Button>
                  </div>
                  <div 
                    className="text-sm mb-2"
                    style={{
                      fontFamily: token.fontFamily,
                      fontSize: token.fontSize,
                      fontWeight: token.fontWeight,
                      lineHeight: token.lineHeight,
                    }}
                  >
                    The quick brown fox jumps
                  </div>
                  <Separator className="my-2" />
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="text-muted-foreground">Font:</span> {token.fontFamily}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Size:</span> {token.fontSize}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Weight:</span> {token.fontWeight}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Line:</span> {token.lineHeight}
                    </div>
                  </div>
                </Card>
              ))}
            </TabsContent>

            {/* Spacing Tab */}
            <TabsContent value="spacing" className="p-4 space-y-3 mt-0">
              {spacingTokens.map((token, index) => (
                <div key={index} className="flex items-center gap-3 p-2 rounded border bg-card">
                  <Badge variant="outline" className="min-w-[60px]">
                    {token.name}
                  </Badge>
                  <div className="flex-1">
                    <div 
                      className="bg-primary h-8 rounded"
                      style={{ width: token.value }}
                    />
                  </div>
                  <span className="text-sm font-mono text-muted-foreground min-w-[50px] text-right">
                    {token.value}
                  </span>
                </div>
              ))}
            </TabsContent>
          </ScrollArea>
        </Tabs>
      </CardContent>
    </Card>
  );
}

'use client';

import type { FabricObject } from '@/types/fabric';
/**
 * Properties Panel Component
 * Edit selected element properties — enhanced with shadow, blend modes,
 * border radius, aspect ratio lock, and rich text controls.
 */

import { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Settings,
  Palette,
  Type as TypeIcon,
  Layout,
  BoxSelect,
  Link2,
  Unlink2,
  Bold,
  Italic,
  Underline,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Strikethrough,
} from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';

interface PropertiesPanelProps {
  selectedElements: FabricObject[];
  onPropertyChange: (property: string, value: unknown) => void;
}

interface PropertiesState extends Record<string, unknown> {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  rotation?: number;
  opacity?: number;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  borderRadius?: number;
  blendMode?: string;
  // Shadow
  shadowColor?: string;
  shadowOffsetX?: number;
  shadowOffsetY?: number;
  shadowBlur?: number;
  shadowEnabled?: boolean;
  // Text
  fontSize?: number;
  fontFamily?: string;
  fontWeight?: string;
  fontStyle?: string;
  textAlign?: string;
  textDecoration?: string;
  lineHeight?: number;
  letterSpacing?: number;
  textColor?: string;
}

const BLEND_MODES = [
  'normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten',
  'color-dodge', 'color-burn', 'hard-light', 'soft-light',
  'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity',
];

const FONT_FAMILIES = [
  'Arial', 'Helvetica', 'Inter', 'Roboto', 'Open Sans', 'Poppins',
  'Montserrat', 'Lato', 'Nunito', 'Raleway', 'Source Sans Pro',
  'Playfair Display', 'Merriweather', 'Georgia', 'Times New Roman',
  'Courier New', 'Fira Code', 'Verdana', 'Trebuchet MS',
];

const FONT_WEIGHTS = [
  { value: '100', label: 'Thin' },
  { value: '300', label: 'Light' },
  { value: 'normal', label: 'Regular' },
  { value: '500', label: 'Medium' },
  { value: '600', label: 'Semi Bold' },
  { value: 'bold', label: 'Bold' },
  { value: '800', label: 'Extra Bold' },
  { value: '900', label: 'Black' },
];

export function PropertiesPanel({ selectedElements, onPropertyChange }: PropertiesPanelProps) {
  const [lockAspectRatio, setLockAspectRatio] = useState(false);

  // Calculate aspect ratio from selected element
  const aspectRatio = selectedElements.length === 1
    ? (() => {
        const el = selectedElements[0] as FabricObject & { width?: number; height?: number };
        const w = el.width || 0;
        const h = el.height || 0;
        return w && h ? w / h : 1;
      })()
    : 1;

  const derivedProperties = useMemo<PropertiesState>(() => {
    if (selectedElements.length === 1) {
      // bypass strict object typing
      const el = selectedElements[0] as FabricObject & {
        left?: number;
        top?: number;
        width?: number;
        height?: number;
        angle?: number;
        opacity?: number;
        fill?: string;
        stroke?: string;
        strokeWidth?: number;
        rx?: number;
        globalCompositeOperation?: string;
        shadow?: Record<string, unknown> | null;
        fontSize?: number;
        fontFamily?: string;
        fontWeight?: string;
        fontStyle?: string;
        textAlign?: string;
        textDecoration?: string;
        lineHeight?: number;
        charSpacing?: number;
      };
      const w = el.width || 0;
      const h = el.height || 0;
      const shadow = el.shadow;
      return {
        x: el.left || 0,
        y: el.top || 0,
        width: w,
        height: h,
        rotation: el.angle || 0,
        opacity: ((el.opacity || 1) * 100),
        fill: el.fill || '#3B82F6',
        stroke: el.stroke || 'transparent',
        strokeWidth: el.strokeWidth || 0,
        borderRadius: el.rx || 0,
        blendMode: el.globalCompositeOperation || 'normal',
        shadowEnabled: !!shadow,
        shadowColor: (shadow?.color as string) || '#000000',
        shadowOffsetX: (shadow?.offsetX as number) || 0,
        shadowOffsetY: (shadow?.offsetY as number) || 0,
        shadowBlur: (shadow?.blur as number) || 10,
        fontSize: el.fontSize || 16,
        fontFamily: el.fontFamily || 'Arial',
        fontWeight: el.fontWeight || 'normal',
        fontStyle: el.fontStyle || 'normal',
        textAlign: el.textAlign || 'left',
        textDecoration: el.textDecoration || '',
        lineHeight: el.lineHeight || 1.16,
        letterSpacing: el.charSpacing || 0,
        textColor: el.fill || '#000000',
      };
    }
    return {};
  }, [selectedElements]);

  const [overrides, setOverrides] = useState<PropertiesState>({});
  const properties = { ...derivedProperties, ...overrides };

  const handleChange = (key: string, value: unknown) => {
    setOverrides(prev => ({ ...prev, [key]: value }));
    onPropertyChange(key, value);
  };

  const handleWidthChange = (val: number) => {
    if (lockAspectRatio) {
      const newHeight = Math.round(val / aspectRatio);
      setOverrides(prev => ({ ...prev, width: val, height: newHeight }));
      onPropertyChange('width', val);
      onPropertyChange('height', newHeight);
    } else {
      handleChange('width', val);
    }
  };

  const handleHeightChange = (val: number) => {
    if (lockAspectRatio) {
      const newWidth = Math.round(val * aspectRatio);
      setOverrides(prev => ({ ...prev, width: newWidth, height: val }));
      onPropertyChange('width', newWidth);
      onPropertyChange('height', val);
    } else {
      handleChange('height', val);
    }
  };

  if (selectedElements.length === 0) {
    return (
      <div className="flex flex-col h-full p-6">
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground">
          <BoxSelect className="w-10 h-10 opacity-30" />
          <p className="text-sm text-center">Select an element to edit its properties</p>
        </div>
      </div>
    );
  }

  if (selectedElements.length > 1) {
    return (
      <div className="flex flex-col h-full p-4 gap-3">
        <div className="text-sm font-medium">{selectedElements.length} elements selected</div>
        <div className="space-y-2">
          <div>
            <Label className="text-xs">Opacity: {properties.opacity ?? 100}%</Label>
            <Slider min={0} max={100} step={1} value={[properties.opacity ?? 100]}
              onValueChange={([v]) => handleChange('opacity', v)} className="mt-1" />
          </div>
          <Button variant="outline" size="sm" className="w-full" onClick={() => onPropertyChange('group', true)}>
            Group Selection
          </Button>
          <Button variant="outline" size="sm" className="w-full" onClick={() => onPropertyChange('alignCenter', true)}>
            Align Centers
          </Button>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider delayDuration={200}>
      <div className="flex flex-col h-full">
        <div className="px-4 py-3 border-b">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Settings className="w-4 h-4 text-muted-foreground" />
            Properties
          </h3>
        </div>

        <Tabs defaultValue="transform" className="flex-1 flex flex-col">
          <TabsList className="w-full grid grid-cols-4 rounded-none border-b h-9">
            <TabsTrigger value="transform" className="text-xs gap-1 rounded-none">
              <Layout className="w-3.5 h-3.5" /> Layout
            </TabsTrigger>
            <TabsTrigger value="style" className="text-xs gap-1 rounded-none">
              <Palette className="w-3.5 h-3.5" /> Style
            </TabsTrigger>
            <TabsTrigger value="text" className="text-xs gap-1 rounded-none">
              <TypeIcon className="w-3.5 h-3.5" /> Text
            </TabsTrigger>
            <TabsTrigger value="effects" className="text-xs gap-1 rounded-none">
              <BoxSelect className="w-3.5 h-3.5" /> FX
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-y-auto">
            {/* ── Layout Tab ─────────────────────────────── */}
            <TabsContent value="transform" className="p-4 space-y-4 m-0">
              {/* Position */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Position</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div>
                    <Label htmlFor="x" className="text-xs">X</Label>
                    <Input id="x" type="number" value={Math.round(properties.x ?? 0)}
                      onChange={(e) => handleChange('left', parseFloat(e.target.value))} className="h-8 mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="y" className="text-xs">Y</Label>
                    <Input id="y" type="number" value={Math.round(properties.y ?? 0)}
                      onChange={(e) => handleChange('top', parseFloat(e.target.value))} className="h-8 mt-1" />
                  </div>
                </div>
              </div>

              {/* Size */}
              <div>
                <div className="flex items-center justify-between">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Size</Label>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-6 w-6"
                        onClick={() => setLockAspectRatio(r => !r)}>
                        {lockAspectRatio
                          ? <Link2 className="h-3.5 w-3.5 text-primary" />
                          : <Unlink2 className="h-3.5 w-3.5 text-muted-foreground" />}
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>{lockAspectRatio ? 'Unlock' : 'Lock'} aspect ratio</TooltipContent>
                  </Tooltip>
                </div>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  <div>
                    <Label htmlFor="width" className="text-xs">W</Label>
                    <Input id="width" type="number" value={Math.round(properties.width || 0)}
                      onChange={(e) => handleWidthChange(parseFloat(e.target.value))} className="h-8 mt-1" />
                  </div>
                  <div>
                    <Label htmlFor="height" className="text-xs">H</Label>
                    <Input id="height" type="number" value={Math.round(properties.height || 0)}
                      onChange={(e) => handleHeightChange(parseFloat(e.target.value))} className="h-8 mt-1" />
                  </div>
                </div>
              </div>

              {/* Rotation */}
              <div>
                <Label className="text-xs">Rotation: {Math.round(properties.rotation ?? 0)}°</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Slider min={0} max={360} step={1} value={[properties.rotation ?? 0]}
                    onValueChange={([v]) => handleChange('angle', v)} className="flex-1" />
                  <Input type="number" value={Math.round(properties.rotation ?? 0)}
                    onChange={(e) => handleChange('angle', parseFloat(e.target.value))}
                    className="h-8 w-16 text-center" />
                </div>
              </div>

              {/* Opacity */}
              <div>
                <Label className="text-xs">Opacity: {Math.round(properties.opacity ?? 100)}%</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Slider min={0} max={100} step={1} value={[properties.opacity ?? 100]}
                    onValueChange={([v]) => handleChange('opacity', v / 100)} className="flex-1" />
                  <Input type="number" value={Math.round(properties.opacity ?? 100)}
                    onChange={(e) => handleChange('opacity', parseFloat(e.target.value) / 100)}
                    className="h-8 w-16 text-center" />
                </div>
              </div>

              {/* Border Radius */}
              <div>
                <Label className="text-xs">Corner Radius: {properties.borderRadius ?? 0}px</Label>
                <div className="flex items-center gap-2 mt-1">
                  <Slider min={0} max={200} step={1} value={[properties.borderRadius ?? 0]}
                    onValueChange={([v]) => { handleChange('rx', v); handleChange('ry', v); }} className="flex-1" />
                  <Input type="number" value={properties.borderRadius ?? 0}
                    onChange={(e) => { const v = parseFloat(e.target.value); handleChange('rx', v); handleChange('ry', v); }}
                    className="h-8 w-16 text-center" />
                </div>
              </div>
            </TabsContent>

            {/* ── Style Tab ─────────────────────────────── */}
            <TabsContent value="style" className="p-4 space-y-4 m-0">
              {/* Fill */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Fill</Label>
                <div className="flex gap-2 mt-2">
                  <Input type="color" value={(properties.fill as string) || '#3B82F6'}
                    onChange={(e) => handleChange('fill', e.target.value)}
                    className="h-9 w-14 p-1 cursor-pointer" />
                  <Input type="text" value={(properties.fill as string) || '#3B82F6'}
                    onChange={(e) => handleChange('fill', e.target.value)} className="h-9 flex-1 font-mono text-sm" />
                </div>
              </div>

              <Separator />

              {/* Stroke */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Stroke</Label>
                <div className="flex gap-2 mt-2">
                  <Input type="color" value={(properties.stroke as string) || '#000000'}
                    onChange={(e) => handleChange('stroke', e.target.value)}
                    className="h-9 w-14 p-1 cursor-pointer" />
                  <Input type="text" value={(properties.stroke as string) || '#000000'}
                    onChange={(e) => handleChange('stroke', e.target.value)} className="h-9 flex-1 font-mono text-sm" />
                </div>
                <Label className="text-xs mt-3 block">Width: {properties.strokeWidth ?? 0}px</Label>
                <Slider min={0} max={40} step={1} value={[properties.strokeWidth ?? 0]}
                  onValueChange={([v]) => handleChange('strokeWidth', v)} className="mt-1" />
              </div>

              <Separator />

              {/* Blend Mode */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Blend Mode</Label>
                <select value={(properties.blendMode as string) || 'normal'}
                  onChange={(e) => handleChange('globalCompositeOperation', e.target.value)}
                  className="w-full mt-2 h-9 border rounded-md px-3 text-sm bg-background">
                  {BLEND_MODES.map(mode => (
                    <option key={mode} value={mode} className="capitalize">{mode.charAt(0).toUpperCase() + mode.slice(1)}</option>
                  ))}
                </select>
              </div>
            </TabsContent>

            {/* ── Text Tab ─────────────────────────────── */}
            <TabsContent value="text" className="p-4 space-y-4 m-0">
              {/* Text Color */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Text Color</Label>
                <div className="flex gap-2 mt-2">
                  <Input type="color" value={(properties.textColor as string) || '#000000'}
                    onChange={(e) => handleChange('fill', e.target.value)}
                    className="h-9 w-14 p-1 cursor-pointer" />
                  <Input type="text" value={(properties.textColor as string) || '#000000'}
                    onChange={(e) => handleChange('fill', e.target.value)} className="h-9 flex-1 font-mono text-sm" />
                </div>
              </div>

              {/* Font Family */}
              <div>
                <Label className="text-xs">Font Family</Label>
                <select value={(properties.fontFamily as string) || 'Arial'}
                  onChange={(e) => handleChange('fontFamily', e.target.value)}
                  className="w-full mt-1 h-9 border rounded-md px-3 text-sm bg-background">
                  {FONT_FAMILIES.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>

              {/* Font Size + Weight */}
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label className="text-xs">Size</Label>
                  <Input type="number" value={properties.fontSize ?? 16}
                    onChange={(e) => handleChange('fontSize', parseFloat(e.target.value))}
                    className="h-9 mt-1" min={6} max={400} />
                </div>
                <div>
                  <Label className="text-xs">Weight</Label>
                  <select value={(properties.fontWeight as string) || 'normal'}
                    onChange={(e) => handleChange('fontWeight', e.target.value)}
                    className="w-full mt-1 h-9 border rounded-md px-3 text-sm bg-background">
                    {FONT_WEIGHTS.map(fw => <option key={fw.value} value={fw.value}>{fw.label}</option>)}
                  </select>
                </div>
              </div>

              {/* Style Buttons */}
              <div>
                <Label className="text-xs">Style</Label>
                <div className="flex gap-1 mt-1">
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant={(properties.fontWeight === 'bold' || properties.fontWeight === '700') ? 'default' : 'outline'}
                        className="h-8 w-8" onClick={() => handleChange('fontWeight', properties.fontWeight === 'bold' ? 'normal' : 'bold')}>
                        <Bold className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Bold</TooltipContent>
                  </Tooltip>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant={properties.fontStyle === 'italic' ? 'default' : 'outline'}
                        className="h-8 w-8" onClick={() => handleChange('fontStyle', properties.fontStyle === 'italic' ? 'normal' : 'italic')}>
                        <Italic className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Italic</TooltipContent>
                  </Tooltip>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant={properties.textDecoration === 'underline' ? 'default' : 'outline'}
                        className="h-8 w-8" onClick={() => handleChange('underline', properties.textDecoration !== 'underline')}>
                        <Underline className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Underline</TooltipContent>
                  </Tooltip>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant={properties.textDecoration === 'line-through' ? 'default' : 'outline'}
                        className="h-8 w-8" onClick={() => handleChange('linethrough', properties.textDecoration !== 'line-through')}>
                        <Strikethrough className="h-4 w-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>Strikethrough</TooltipContent>
                  </Tooltip>
                </div>
              </div>

              {/* Alignment */}
              <div>
                <Label className="text-xs">Alignment</Label>
                <div className="flex gap-1 mt-1">
                  {([
                    { val: 'left', Icon: AlignLeft },
                    { val: 'center', Icon: AlignCenter },
                    { val: 'right', Icon: AlignRight },
                    { val: 'justify', Icon: AlignJustify },
                  ] as const).map(({ val, Icon }) => (
                    <Tooltip key={val}>
                      <TooltipTrigger asChild>
                        <Button size="icon" variant={properties.textAlign === val ? 'default' : 'outline'}
                          className="h-8 w-8 flex-1" onClick={() => handleChange('textAlign', val)}>
                          <Icon className="h-4 w-4" />
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent className="capitalize">{val}</TooltipContent>
                    </Tooltip>
                  ))}
                </div>
              </div>

              {/* Line Height & Letter Spacing */}
              <div>
                <Label className="text-xs">Line Height: {((properties.lineHeight as number) ?? 1.16).toFixed(2)}</Label>
                <Slider min={0.5} max={4} step={0.01} value={[(properties.lineHeight as number) ?? 1.16]}
                  onValueChange={([v]) => handleChange('lineHeight', v)} className="mt-1" />
              </div>
              <div>
                <Label className="text-xs">Letter Spacing: {properties.letterSpacing ?? 0}</Label>
                <Slider min={-200} max={800} step={1} value={[(properties.letterSpacing as number) ?? 0]}
                  onValueChange={([v]) => handleChange('charSpacing', v)} className="mt-1" />
              </div>
            </TabsContent>

            {/* ── Effects Tab ─────────────────────────────── */}
            <TabsContent value="effects" className="p-4 space-y-4 m-0">
              {/* Shadow */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Drop Shadow</Label>
                  <Switch checked={!!(properties.shadowEnabled)}
                    onCheckedChange={(v) => {
                      handleChange('shadowEnabled', v);
                      if (!v) {
                        onPropertyChange('shadow', null);
                      } else {
                        onPropertyChange('shadow', {
                          color: properties.shadowColor || '#00000066',
                          offsetX: properties.shadowOffsetX ?? 4,
                          offsetY: properties.shadowOffsetY ?? 4,
                          blur: properties.shadowBlur ?? 10,
                        });
                      }
                    }} />
                </div>

                {properties.shadowEnabled && (
                  <div className="space-y-3 pl-1">
                    <div>
                      <Label className="text-xs">Shadow Color</Label>
                      <div className="flex gap-2 mt-1">
                        <Input type="color" value={(properties.shadowColor as string) || '#000000'}
                          onChange={(e) => handleChange('shadowColor', e.target.value)}
                          className="h-9 w-14 p-1 cursor-pointer" />
                        <Input type="text" value={(properties.shadowColor as string) || '#000000'}
                          onChange={(e) => handleChange('shadowColor', e.target.value)}
                          className="h-9 flex-1 font-mono text-sm" />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label className="text-xs">Offset X: {properties.shadowOffsetX ?? 0}</Label>
                        <Slider min={-100} max={100} step={1} value={[(properties.shadowOffsetX as number) ?? 0]}
                          onValueChange={([v]) => handleChange('shadowOffsetX', v)} className="mt-1" />
                      </div>
                      <div>
                        <Label className="text-xs">Offset Y: {properties.shadowOffsetY ?? 0}</Label>
                        <Slider min={-100} max={100} step={1} value={[(properties.shadowOffsetY as number) ?? 0]}
                          onValueChange={([v]) => handleChange('shadowOffsetY', v)} className="mt-1" />
                      </div>
                    </div>
                    <div>
                      <Label className="text-xs">Blur: {properties.shadowBlur ?? 10}px</Label>
                      <Slider min={0} max={100} step={1} value={[(properties.shadowBlur as number) ?? 10]}
                        onValueChange={([v]) => handleChange('shadowBlur', v)} className="mt-1" />
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              {/* Blend Mode (also available here) */}
              <div>
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2 block">Blend Mode</Label>
                <select value={(properties.blendMode as string) || 'normal'}
                  onChange={(e) => handleChange('globalCompositeOperation', e.target.value)}
                  className="w-full h-9 border rounded-md px-3 text-sm bg-background">
                  {BLEND_MODES.map(mode => (
                    <option key={mode} value={mode}>{mode.charAt(0).toUpperCase() + mode.slice(1)}</option>
                  ))}
                </select>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </TooltipProvider>
  );
}

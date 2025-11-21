/**
 * Properties Panel Component
 * Edit selected element properties
 */
'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Settings, Palette, Type as TypeIcon, Layout } from 'lucide-react';

interface PropertiesPanelProps {
  selectedElements: any[];
  onPropertyChange: (property: string, value: any) => void;
}

export function PropertiesPanel({ selectedElements, onPropertyChange }: PropertiesPanelProps) {
  const [properties, setProperties] = useState<any>({});

  useEffect(() => {
    if (selectedElements.length === 1) {
      // Get properties from selected element
      const element = selectedElements[0];
      setProperties({
        x: element.left || 0,
        y: element.top || 0,
        width: element.width || 0,
        height: element.height || 0,
        rotation: element.angle || 0,
        opacity: (element.opacity || 1) * 100,
        fill: element.fill || '#000000',
        stroke: element.stroke || '#000000',
        strokeWidth: element.strokeWidth || 0,
        fontSize: element.fontSize || 16,
        fontFamily: element.fontFamily || 'Arial',
        fontWeight: element.fontWeight || 'normal',
        textAlign: element.textAlign || 'left'
      });
    } else if (selectedElements.length === 0) {
      setProperties({});
    }
  }, [selectedElements]);

  const handleChange = (key: string, value: any) => {
    setProperties({ ...properties, [key]: value });
    onPropertyChange(key, value);
  };

  if (selectedElements.length === 0) {
    return (
      <div className="flex flex-col h-full p-4">
        <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
          Select an element to edit properties
        </div>
      </div>
    );
  }

  if (selectedElements.length > 1) {
    return (
      <div className="flex flex-col h-full p-4">
        <div className="text-sm text-gray-600 mb-4">
          {selectedElements.length} elements selected
        </div>
        <Button variant="outline" size="sm" className="w-full">
          Group Selection
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h3 className="font-semibold flex items-center gap-2">
          <Settings className="w-4 h-4" />
          Properties
        </h3>
      </div>

      <Tabs defaultValue="transform" className="flex-1">
        <TabsList className="w-full grid grid-cols-3">
          <TabsTrigger value="transform">
            <Layout className="w-4 h-4" />
          </TabsTrigger>
          <TabsTrigger value="style">
            <Palette className="w-4 h-4" />
          </TabsTrigger>
          <TabsTrigger value="text">
            <TypeIcon className="w-4 h-4" />
          </TabsTrigger>
        </TabsList>

        <div className="overflow-y-auto">
          {/* Transform Tab */}
          <TabsContent value="transform" className="p-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="x" className="text-xs">X</Label>
                <Input
                  id="x"
                  type="number"
                  value={Math.round(properties.x || 0)}
                  onChange={(e) => handleChange('x', parseFloat(e.target.value))}
                  className="h-8"
                />
              </div>
              <div>
                <Label htmlFor="y" className="text-xs">Y</Label>
                <Input
                  id="y"
                  type="number"
                  value={Math.round(properties.y || 0)}
                  onChange={(e) => handleChange('y', parseFloat(e.target.value))}
                  className="h-8"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="width" className="text-xs">Width</Label>
                <Input
                  id="width"
                  type="number"
                  value={Math.round(properties.width || 0)}
                  onChange={(e) => handleChange('width', parseFloat(e.target.value))}
                  className="h-8"
                />
              </div>
              <div>
                <Label htmlFor="height" className="text-xs">Height</Label>
                <Input
                  id="height"
                  type="number"
                  value={Math.round(properties.height || 0)}
                  onChange={(e) => handleChange('height', parseFloat(e.target.value))}
                  className="h-8"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="rotation" className="text-xs">Rotation: {properties.rotation}°</Label>
              <Slider
                id="rotation"
                min={0}
                max={360}
                step={1}
                value={[properties.rotation || 0]}
                onValueChange={([value]) => handleChange('rotation', value)}
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="opacity" className="text-xs">Opacity: {properties.opacity}%</Label>
              <Slider
                id="opacity"
                min={0}
                max={100}
                step={1}
                value={[properties.opacity || 100]}
                onValueChange={([value]) => handleChange('opacity', value)}
                className="mt-2"
              />
            </div>
          </TabsContent>

          {/* Style Tab */}
          <TabsContent value="style" className="p-4 space-y-4">
            <div>
              <Label htmlFor="fill" className="text-xs">Fill Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  id="fill"
                  type="color"
                  value={properties.fill || '#000000'}
                  onChange={(e) => handleChange('fill', e.target.value)}
                  className="h-10 w-16 p-1"
                />
                <Input
                  type="text"
                  value={properties.fill || '#000000'}
                  onChange={(e) => handleChange('fill', e.target.value)}
                  className="h-10 flex-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="stroke" className="text-xs">Stroke Color</Label>
              <div className="flex gap-2 mt-1">
                <Input
                  id="stroke"
                  type="color"
                  value={properties.stroke || '#000000'}
                  onChange={(e) => handleChange('stroke', e.target.value)}
                  className="h-10 w-16 p-1"
                />
                <Input
                  type="text"
                  value={properties.stroke || '#000000'}
                  onChange={(e) => handleChange('stroke', e.target.value)}
                  className="h-10 flex-1"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="strokeWidth" className="text-xs">Stroke Width: {properties.strokeWidth}px</Label>
              <Slider
                id="strokeWidth"
                min={0}
                max={20}
                step={1}
                value={[properties.strokeWidth || 0]}
                onValueChange={([value]) => handleChange('strokeWidth', value)}
                className="mt-2"
              />
            </div>
          </TabsContent>

          {/* Text Tab */}
          <TabsContent value="text" className="p-4 space-y-4">
            <div>
              <Label htmlFor="fontSize" className="text-xs">Font Size: {properties.fontSize}px</Label>
              <Slider
                id="fontSize"
                min={8}
                max={72}
                step={1}
                value={[properties.fontSize || 16]}
                onValueChange={([value]) => handleChange('fontSize', value)}
                className="mt-2"
              />
            </div>

            <div>
              <Label htmlFor="fontFamily" className="text-xs">Font Family</Label>
              <select
                id="fontFamily"
                value={properties.fontFamily || 'Arial'}
                onChange={(e) => handleChange('fontFamily', e.target.value)}
                className="w-full mt-1 h-10 border rounded-md px-3"
              >
                <option value="Arial">Arial</option>
                <option value="Helvetica">Helvetica</option>
                <option value="Times New Roman">Times New Roman</option>
                <option value="Georgia">Georgia</option>
                <option value="Courier New">Courier New</option>
                <option value="Verdana">Verdana</option>
              </select>
            </div>

            <div>
              <Label htmlFor="fontWeight" className="text-xs">Font Weight</Label>
              <select
                id="fontWeight"
                value={properties.fontWeight || 'normal'}
                onChange={(e) => handleChange('fontWeight', e.target.value)}
                className="w-full mt-1 h-10 border rounded-md px-3"
              >
                <option value="normal">Normal</option>
                <option value="bold">Bold</option>
                <option value="lighter">Light</option>
              </select>
            </div>

            <div>
              <Label htmlFor="textAlign" className="text-xs">Text Align</Label>
              <select
                id="textAlign"
                value={properties.textAlign || 'left'}
                onChange={(e) => handleChange('textAlign', e.target.value)}
                className="w-full mt-1 h-10 border rounded-md px-3"
              >
                <option value="left">Left</option>
                <option value="center">Center</option>
                <option value="right">Right</option>
              </select>
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

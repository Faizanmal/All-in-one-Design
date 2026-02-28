'use client';

import React, { useState, useCallback } from 'react';
import { 
  Code2, Download, Copy, Check,
  RefreshCw, Layers, FileJson,
  Monitor, Tablet, Smartphone, FileCode2
} from 'lucide-react';

// Types
interface ExportConfiguration {
  id: string;
  name: string;
  framework: 'react' | 'vue' | 'angular' | 'svelte' | 'html' | 'swiftui' | 'jetpack';
  stylingApproach: 'tailwind' | 'css-modules' | 'styled-components' | 'css-in-js' | 'inline';
  useTypeScript: boolean;
  responsive: boolean;
  includeAssets: boolean;
  componentNaming: 'pascal' | 'kebab' | 'camel';
}

interface DesignSpec {
  colors: Array<{ name: string; hex: string; usage: string }>;
  typography: Array<{ name: string; fontFamily: string; fontSize: string; weight: number }>;
  spacing: Array<{ name: string; value: string }>;
  components: Array<{ name: string; props: Record<string, unknown> }>;
}

interface HandoffAnnotation {
  id: string;
  elementId: string;
  type: 'measurement' | 'spec' | 'note' | 'interaction';
  content: string;
  position: { x: number; y: number };
}

// Framework options
const FRAMEWORKS = [
  { id: 'react', name: 'React', icon: '⚛️' },
  { id: 'vue', name: 'Vue.js', icon: '💚' },
  { id: 'angular', name: 'Angular', icon: '🅰️' },
  { id: 'svelte', name: 'Svelte', icon: '🔶' },
  { id: 'html', name: 'HTML/CSS', icon: '🌐' },
  { id: 'swiftui', name: 'SwiftUI', icon: '🍎' },
  { id: 'jetpack', name: 'Jetpack Compose', icon: '🤖' },
];

const STYLING_OPTIONS = [
  { id: 'tailwind', name: 'Tailwind CSS' },
  { id: 'css-modules', name: 'CSS Modules' },
  { id: 'styled-components', name: 'Styled Components' },
  { id: 'css-in-js', name: 'CSS-in-JS' },
  { id: 'inline', name: 'Inline Styles' },
];

// Code Export Panel Component
export function CodeExportPanel({ projectId }: { projectId: string }) {
  const [_selectedLayers] = useState<string[]>([]);
  const [config, setConfig] = useState<ExportConfiguration>({
    id: '',
    name: 'Default Export',
    framework: 'react',
    stylingApproach: 'tailwind',
    useTypeScript: true,
    responsive: true,
    includeAssets: true,
    componentNaming: 'pascal',
  });
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const generateCode = useCallback(async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/v1/code-export/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          layers: selectedLayers,
          config,
        }),
      });
      
      const data = await response.json();
      setGeneratedCode(data.code || generateMockCode(config));
    } catch (_error) {
      // Generate mock code for demo
      setGeneratedCode(generateMockCode(config));
    } finally {
      setIsGenerating(false);
    }
  }, [config]);

  const copyToClipboard = useCallback(() => {
    navigator.clipboard.writeText(generatedCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [generatedCode]);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Code2 className="w-5 h-5 text-blue-400" />
          <h2 className="font-semibold">Code Export</h2>
        </div>
        <button
          onClick={generateCode}
          disabled={isGenerating}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50"
        >
          {isGenerating ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <Code2 className="w-4 h-4" />
          )}
          Generate Code
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Settings Panel */}
        <div className="w-72 border-r border-gray-700 p-4 space-y-6 overflow-y-auto">
          {/* Framework Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Framework
            </label>
            <div className="grid grid-cols-2 gap-2">
              {FRAMEWORKS.map((fw) => (
                <button
                  key={fw.id}
                  onClick={() => setConfig({ ...config, framework: fw.id as typeof config.framework })}
                  className={`flex items-center gap-2 p-2 rounded-lg text-sm transition-colors ${
                    config.framework === fw.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                  }`}
                >
                  <span>{fw.icon}</span>
                  <span>{fw.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Styling Approach */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Styling
            </label>
            <select
              value={config.stylingApproach}
              onChange={(e) => setConfig({ ...config, stylingApproach: e.target.value as ExportConfiguration["stylingApproach"] })}
              className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg"
            >
              {STYLING_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>{opt.name}</option>
              ))}
            </select>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.useTypeScript}
                onChange={(e) => setConfig({ ...config, useTypeScript: e.target.checked })}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700"
              />
              <span className="text-sm">Use TypeScript</span>
            </label>
            
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.responsive}
                onChange={(e) => setConfig({ ...config, responsive: e.target.checked })}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700"
              />
              <span className="text-sm">Responsive Design</span>
            </label>
            
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={config.includeAssets}
                onChange={(e) => setConfig({ ...config, includeAssets: e.target.checked })}
                className="w-4 h-4 rounded bg-gray-800 border-gray-700"
              />
              <span className="text-sm">Include Assets</span>
            </label>
          </div>

          {/* Responsive Preview */}
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Preview Device
            </label>
            <div className="flex gap-2">
              <button className="flex-1 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg">
                <Monitor className="w-5 h-5 mx-auto" />
              </button>
              <button className="flex-1 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg">
                <Tablet className="w-5 h-5 mx-auto" />
              </button>
              <button className="flex-1 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg">
                <Smartphone className="w-5 h-5 mx-auto" />
              </button>
            </div>
          </div>
        </div>

        {/* Code Preview */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex items-center justify-between p-3 border-b border-gray-700">
            <div className="flex items-center gap-2">
              <FileCode2 className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-400">
                {config.useTypeScript ? 'Component.tsx' : 'Component.jsx'}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg"
              >
                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg">
                <Download className="w-4 h-4" />
                Download
              </button>
            </div>
          </div>
          
          <div className="flex-1 overflow-auto p-4 bg-gray-950 font-mono text-sm">
            <pre className="text-gray-300 whitespace-pre-wrap">
              {generatedCode || 'Select elements and click "Generate Code" to see the output'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

// Design Spec Panel Component
export function DesignSpecPanel({ projectId: _projectId }: { projectId: string }) {
  const [spec, _setSpec] = useState<DesignSpec | null>({
    colors: [
      { name: 'Primary', hex: '#3B82F6', usage: 'Buttons, links, primary actions' },
      { name: 'Secondary', hex: '#6B7280', usage: 'Secondary text, borders' },
      { name: 'Success', hex: '#10B981', usage: 'Success states, positive actions' },
      { name: 'Error', hex: '#EF4444', usage: 'Error states, destructive actions' },
      { name: 'Background', hex: '#111827', usage: 'Page background' },
    ],
    typography: [
      { name: 'Heading 1', fontFamily: 'Inter', fontSize: '36px', weight: 700 },
      { name: 'Heading 2', fontFamily: 'Inter', fontSize: '24px', weight: 600 },
      { name: 'Body', fontFamily: 'Inter', fontSize: '16px', weight: 400 },
      { name: 'Caption', fontFamily: 'Inter', fontSize: '12px', weight: 400 },
    ],
      spacing: [
        { name: 'xs', value: '4px' },
        { name: 'sm', value: '8px' },
        { name: 'md', value: '16px' },
        { name: 'lg', value: '24px' },
        { name: 'xl', value: '32px' },
      ],
      components: [
        { name: 'Button', props: { variant: 'primary | secondary', size: 'sm | md | lg' } },
        { name: 'Input', props: { type: 'text | email | password', error: 'boolean' } },
        { name: 'Card', props: { elevation: '0 | 1 | 2 | 3' } },
      ],
    });
  const [activeTab, setActiveTab] = useState<'colors' | 'typography' | 'spacing' | 'components'>('colors');

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="flex items-center gap-2 p-4 border-b border-gray-700">
        <FileJson className="w-5 h-5 text-purple-400" />
        <h2 className="font-semibold">Design Specifications</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {(['colors', 'typography', 'spacing', 'components'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'colors' && spec && (
          <div className="space-y-3">
            {spec.colors.map((color) => (
              <div key={color.name} className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">
                <div
                  className="w-12 h-12 rounded-lg border border-gray-600"
                  style={{ backgroundColor: color.hex }}
                />
                <div className="flex-1">
                  <div className="font-medium">{color.name}</div>
                  <div className="text-sm text-gray-400">{color.hex}</div>
                  <div className="text-xs text-gray-500">{color.usage}</div>
                </div>
                <button
                  onClick={() => navigator.clipboard.writeText(color.hex)}
                  className="p-2 hover:bg-gray-700 rounded"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'typography' && spec && (
          <div className="space-y-3">
            {spec.typography.map((typo) => (
              <div key={typo.name} className="p-3 bg-gray-800 rounded-lg">
                <div
                  style={{
                    fontFamily: typo.fontFamily,
                    fontSize: typo.fontSize,
                    fontWeight: typo.weight,
                  }}
                >
                  {typo.name}
                </div>
                <div className="mt-2 text-sm text-gray-400">
                  {typo.fontFamily} • {typo.fontSize} • {typo.weight}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'spacing' && spec && (
          <div className="space-y-3">
            {spec.spacing.map((space) => (
              <div key={space.name} className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">
                <div className="w-16 text-center font-mono text-sm">{space.name}</div>
                <div
                  className="bg-blue-500 h-4"
                  style={{ width: space.value }}
                />
                <div className="text-sm text-gray-400">{space.value}</div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'components' && spec && (
          <div className="space-y-3">
            {spec.components.map((comp) => (
              <div key={comp.name} className="p-3 bg-gray-800 rounded-lg">
                <div className="font-medium flex items-center gap-2">
                  <Layers className="w-4 h-4 text-green-400" />
                  {comp.name}
                </div>
                <div className="mt-2 space-y-1">
                  {Object.entries(comp.props).map(([key, value]) => (
                    <div key={key} className="text-sm text-gray-400">
                      <span className="text-purple-400">{key}</span>: {String(value)}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Developer Handoff Component
export function DeveloperHandoff({ projectId: _projectId }: { projectId: string }) {
  const [_annotations, _setAnnotations] = useState<HandoffAnnotation[]>([]);
  const [showMeasurements, setShowMeasurements] = useState(true);
  const [showSpecs, setShowSpecs] = useState(true);

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h2 className="font-semibold">Developer Handoff</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMeasurements(!showMeasurements)}
            className={`p-2 rounded ${showMeasurements ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Measurements
          </button>
          <button
            onClick={() => setShowSpecs(!showSpecs)}
            className={`p-2 rounded ${showSpecs ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Specs
          </button>
        </div>
      </div>
      
      <div className="flex-1 p-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-medium mb-3">Quick Actions</h3>
            <div className="space-y-2">
              <button className="w-full p-2 text-left bg-gray-700 hover:bg-gray-600 rounded">
                📐 Export CSS
              </button>
              <button className="w-full p-2 text-left bg-gray-700 hover:bg-gray-600 rounded">
                📱 Export React Native
              </button>
              <button className="w-full p-2 text-left bg-gray-700 hover:bg-gray-600 rounded">
                🎨 Export Design Tokens
              </button>
              <button className="w-full p-2 text-left bg-gray-700 hover:bg-gray-600 rounded">
                📦 Download All Assets
              </button>
            </div>
          </div>
          
          <div className="p-4 bg-gray-800 rounded-lg">
            <h3 className="font-medium mb-3">Recent Exports</h3>
            <div className="space-y-2 text-sm text-gray-400">
              <div>React Components - 2 hours ago</div>
              <div>Design Tokens JSON - Yesterday</div>
              <div>SVG Assets - 3 days ago</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Helper function to generate mock code
function generateMockCode(config: ExportConfiguration): string {
  if (config.framework === 'react') {
    return `${config.useTypeScript ? `import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick
}) => {
  return (
    <button
      onClick={onClick}
      className={\`
        inline-flex items-center justify-center font-medium
        rounded-lg transition-colors
        \${variant === 'primary' 
          ? 'bg-blue-600 hover:bg-blue-700 text-white'
          : 'bg-gray-200 hover:bg-gray-300 text-gray-900'}
        \${size === 'sm' ? 'px-3 py-1.5 text-sm' :
          size === 'lg' ? 'px-6 py-3 text-lg' : 'px-4 py-2'}
      \`}
    >
      {children}
    </button>
  );
};` : `import React from 'react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick
}) => {
  return (
    <button
      onClick={onClick}
      className={\`btn btn-\${variant} btn-\${size}\`}
    >
      {children}
    </button>
  );
};`}`;
  }
  
  if (config.framework === 'vue') {
    return `<template>
  <button
    :class="[
      'btn',
      \`btn-\${variant}\`,
      \`btn-\${size}\`
    ]"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<script${config.useTypeScript ? ' lang="ts"' : ''}>
${config.useTypeScript ? `
import { defineComponent, PropType } from 'vue';

export default defineComponent({
  props: {
    variant: {
      type: String as PropType<'primary' | 'secondary'>,
      default: 'primary'
    },
    size: {
      type: String as PropType<'sm' | 'md' | 'lg'>,
      default: 'md'
    }
  }
});
` : `
export default {
  props: {
    variant: { type: String, default: 'primary' },
    size: { type: String, default: 'md' }
  }
};
`}
</script>`;
  }

  if (config.framework === 'swiftui') {
    return `import SwiftUI

struct CustomButton: View {
    var text: String
    var variant: ButtonVariant = .primary
    var size: ButtonSize = .medium
    var action: () -> Void
    
    enum ButtonVariant {
        case primary, secondary
    }
    
    enum ButtonSize {
        case small, medium, large
    }
    
    var body: some View {
        Button(action: action) {
            Text(text)
                .font(fontSize)
                .padding(padding)
                .foregroundColor(foregroundColor)
                .background(backgroundColor)
                .cornerRadius(8)
        }
    }
    
    private var backgroundColor: Color {
        variant == .primary ? .blue : .gray
    }
    
    private var foregroundColor: Color {
        variant == .primary ? .white : .black
    }
    
    private var padding: EdgeInsets {
        switch size {
        case .small: return EdgeInsets(top: 6, leading: 12, bottom: 6, trailing: 12)
        case .medium: return EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16)
        case .large: return EdgeInsets(top: 12, leading: 24, bottom: 12, trailing: 24)
        }
    }
    
    private var fontSize: Font {
        switch size {
        case .small: return .caption
        case .medium: return .body
        case .large: return .title3
        }
    }
}`;
  }

  return '// Select a framework to generate code';
}

export default CodeExportPanel;

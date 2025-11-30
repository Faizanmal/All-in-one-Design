/**
 * Code Export Component
 * Export designs as React, Vue, HTML, or Tailwind code
 */
'use client';

import React, { useState, useCallback } from 'react';
import {
  Code,
  Copy,
  Download,
  Check,
  FileCode,
  Loader2,
  ChevronDown,
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface CodeExportProps {
  projectId: string;
  onExportComplete?: (exportId: string) => void;
}

type Framework = 'react' | 'vue' | 'html' | 'tailwind';
type CSSFramework = 'css' | 'tailwind' | 'styled-components' | 'scss';

const FRAMEWORKS = [
  { id: 'react', name: 'React', icon: '⚛️', extension: 'tsx' },
  { id: 'vue', name: 'Vue 3', icon: '💚', extension: 'vue' },
  { id: 'html', name: 'HTML', icon: '🌐', extension: 'html' },
  { id: 'tailwind', name: 'Tailwind', icon: '🎨', extension: 'tsx' },
];

const CSS_OPTIONS = [
  { id: 'css', name: 'Plain CSS' },
  { id: 'tailwind', name: 'Tailwind CSS' },
  { id: 'styled-components', name: 'Styled Components' },
  { id: 'scss', name: 'SCSS' },
];

export const CodeExport: React.FC<CodeExportProps> = ({
  projectId,
  onExportComplete,
}) => {
  const [framework, setFramework] = useState<Framework>('react');
  const [cssFramework, setCssFramework] = useState<CSSFramework>('tailwind');
  const [generating, setGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<string>('');
  const [cssCode, setCssCode] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState<'component' | 'styles'>('component');
  
  // Options
  const [options, setOptions] = useState({
    includeAnimations: true,
    responsiveBreakpoints: true,
    useTypeScript: true,
    includeComments: true,
    componentName: 'DesignComponent',
  });

  const generateCode = useCallback(async () => {
    setGenerating(true);
    setGeneratedCode('');
    setCssCode('');

    try {
      const response = await fetch(`/api/v1/projects/projects/${projectId}/generate-code/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          framework,
          css_framework: cssFramework,
          options: {
            include_animations: options.includeAnimations,
            responsive_breakpoints: options.responsiveBreakpoints,
            use_typescript: options.useTypeScript,
            include_comments: options.includeComments,
            component_name: options.componentName,
          },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setGeneratedCode(data.component_code || '');
        setCssCode(data.css_code || '');
        onExportComplete?.(data.export_id);
      }
    } catch (err) {
      console.error('Failed to generate code:', err);
    } finally {
      setGenerating(false);
    }
  }, [projectId, framework, cssFramework, options, onExportComplete]);

  const copyToClipboard = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const downloadCode = () => {
    const frameworkInfo = FRAMEWORKS.find((f) => f.id === framework);
    const blob = new Blob([generatedCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${options.componentName}.${frameworkInfo?.extension || 'tsx'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getLanguage = () => {
    switch (framework) {
      case 'react':
      case 'tailwind':
        return options.useTypeScript ? 'tsx' : 'jsx';
      case 'vue':
        return 'vue';
      case 'html':
        return 'html';
      default:
        return 'javascript';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900 flex items-center justify-center">
            <Code className="w-5 h-5 text-green-600 dark:text-green-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Export as Code
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Generate production-ready code from your design
            </p>
          </div>
        </div>

        {/* Framework Selection */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          {FRAMEWORKS.map((fw) => (
            <button
              key={fw.id}
              onClick={() => setFramework(fw.id as Framework)}
              className={`p-3 rounded-lg border-2 text-center transition-colors ${
                framework === fw.id
                  ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-green-300'
              }`}
            >
              <span className="text-2xl">{fw.icon}</span>
              <p className="text-sm font-medium text-gray-900 dark:text-white mt-1">
                {fw.name}
              </p>
            </button>
          ))}
        </div>

        {/* Options */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              CSS Framework
            </label>
            <select
              value={cssFramework}
              onChange={(e) => setCssFramework(e.target.value as CSSFramework)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
            >
              {CSS_OPTIONS.map((opt) => (
                <option key={opt.id} value={opt.id}>
                  {opt.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Component Name
            </label>
            <input
              type="text"
              value={options.componentName}
              onChange={(e) =>
                setOptions({ ...options, componentName: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
        </div>

        {/* Toggles */}
        <div className="flex flex-wrap gap-4 mt-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={options.useTypeScript}
              onChange={(e) =>
                setOptions({ ...options, useTypeScript: e.target.checked })
              }
              className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              TypeScript
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={options.includeAnimations}
              onChange={(e) =>
                setOptions({ ...options, includeAnimations: e.target.checked })
              }
              className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Animations
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={options.responsiveBreakpoints}
              onChange={(e) =>
                setOptions({ ...options, responsiveBreakpoints: e.target.checked })
              }
              className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Responsive
            </span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={options.includeComments}
              onChange={(e) =>
                setOptions({ ...options, includeComments: e.target.checked })
              }
              className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              Comments
            </span>
          </label>
        </div>

        <button
          onClick={generateCode}
          disabled={generating}
          className="w-full mt-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {generating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileCode className="w-5 h-5" />
              Generate Code
            </>
          )}
        </button>
      </div>

      {/* Generated Code */}
      {generatedCode && (
        <div className="p-4">
          {/* Tabs */}
          <div className="flex items-center gap-2 mb-3">
            <button
              onClick={() => setActiveTab('component')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                activeTab === 'component'
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                  : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              Component
            </button>
            {cssCode && (
              <button
                onClick={() => setActiveTab('styles')}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                  activeTab === 'styles'
                    ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                Styles
              </button>
            )}
            <div className="flex-1" />
            <button
              onClick={() =>
                copyToClipboard(activeTab === 'component' ? generatedCode : cssCode)
              }
              className="flex items-center gap-1 px-3 py-1.5 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
              <span className="text-sm">{copied ? 'Copied!' : 'Copy'}</span>
            </button>
            <button
              onClick={downloadCode}
              className="flex items-center gap-1 px-3 py-1.5 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm">Download</span>
            </button>
          </div>

          {/* Code Display */}
          <div className="rounded-lg overflow-hidden max-h-96 overflow-y-auto">
            <SyntaxHighlighter
              language={activeTab === 'component' ? getLanguage() : 'css'}
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                borderRadius: '0.5rem',
                fontSize: '0.875rem',
              }}
            >
              {activeTab === 'component' ? generatedCode : cssCode}
            </SyntaxHighlighter>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeExport;

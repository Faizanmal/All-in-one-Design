'use client';

import React, { useState, useCallback, useEffect } from 'react';
import {
  Eye,
  EyeOff,
  Volume2,
  VolumeX,
  Keyboard,
  Mouse,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Play,
  Pause,
  RefreshCw,
  Download,
  Settings,
  ArrowRight,
  Contrast,
  Palette,
  Type,
  Target,
  Clock,
  Globe,
  ChevronDown,
  ChevronRight,
  Wrench,
  EyeOff as IgnoreIcon,
  FileText,
  FileJson,
  Table2,
  Filter,
  Zap,
} from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

interface AccessibilityIssue {
  id: string;
  category: 'contrast' | 'focus' | 'keyboard' | 'screen_reader' | 'alt_text' | 'semantics' | 'motion' | 'color_alone' | 'text_size' | 'touch_target';
  severity: 'error' | 'warning' | 'info';
  title: string;
  description: string;
  element?: string;
  wcag_criteria?: string;
  suggestion?: string;
  is_fixed: boolean;
  is_ignored: boolean;
}

interface ContrastResult {
  foreground: string;
  background: string;
  ratio: number;
  aa_normal: boolean;
  aa_large: boolean;
  aaa_normal: boolean;
  aaa_large: boolean;
}

interface ColorBlindnessType {
  type: 'protanopia' | 'deuteranopia' | 'tritanopia' | 'protanomaly' | 'deuteranomaly' | 'tritanomaly' | 'achromatopsia' | 'achromatomaly';
  label: string;
  description: string;
  prevalence: string;
}

interface AccessibilityTestingProps {
  designId?: string;
  onIssueSelect?: (issue: AccessibilityIssue) => void;
  onFix?: (issueId: string) => void;
}

const COLOR_BLINDNESS_TYPES: ColorBlindnessType[] = [
  { type: 'protanopia', label: 'Protanopia', description: 'Red-blind', prevalence: '1% of males' },
  { type: 'deuteranopia', label: 'Deuteranopia', description: 'Green-blind', prevalence: '1% of males' },
  { type: 'tritanopia', label: 'Tritanopia', description: 'Blue-blind', prevalence: '0.003% of population' },
  { type: 'protanomaly', label: 'Protanomaly', description: 'Red-weak', prevalence: '1% of males' },
  { type: 'deuteranomaly', label: 'Deuteranomaly', description: 'Green-weak', prevalence: '5% of males' },
  { type: 'tritanomaly', label: 'Tritanomaly', description: 'Blue-weak', prevalence: '0.01% of population' },
  { type: 'achromatopsia', label: 'Achromatopsia', description: 'Total color blindness', prevalence: '0.003%' },
  { type: 'achromatomaly', label: 'Achromatomaly', description: 'Partial color blindness', prevalence: '0.001%' },
];

const ISSUE_CATEGORIES = [
  { key: 'contrast', label: 'Contrast', icon: Contrast },
  { key: 'focus', label: 'Focus Order', icon: Target },
  { key: 'keyboard', label: 'Keyboard', icon: Keyboard },
  { key: 'screen_reader', label: 'Screen Reader', icon: Volume2 },
  { key: 'alt_text', label: 'Alt Text', icon: Type },
  { key: 'semantics', label: 'Semantics', icon: Globe },
  { key: 'motion', label: 'Motion', icon: Play },
  { key: 'touch_target', label: 'Touch Target', icon: Mouse },
];

export function AccessibilityTesting({ designId, onIssueSelect, onFix }: AccessibilityTestingProps) {
  const [activeTab, setActiveTab] = useState<'issues' | 'colorblind' | 'screenreader' | 'focus' | 'contrast'>('issues');
  const [issues, setIssues] = useState<AccessibilityIssue[]>([
    {
      id: 'issue_1',
      category: 'contrast',
      severity: 'error',
      title: 'Insufficient color contrast',
      description: 'Text color #999999 on background #ffffff has a contrast ratio of 2.85:1, which fails WCAG AA requirements.',
      element: 'Button/Secondary label',
      wcag_criteria: 'WCAG 2.1 - 1.4.3 Contrast (Minimum)',
      suggestion: 'Use a darker text color like #666666 for a ratio of 5.74:1.',
      is_fixed: false,
      is_ignored: false
    },
    {
      id: 'issue_2',
      category: 'alt_text',
      severity: 'error',
      title: 'Missing alternative text',
      description: 'Image element has no alt text defined.',
      element: 'Hero/Background Image',
      wcag_criteria: 'WCAG 2.1 - 1.1.1 Non-text Content',
      suggestion: 'Add descriptive alt text or mark as decorative.',
      is_fixed: false,
      is_ignored: false
    },
    {
      id: 'issue_3',
      category: 'focus',
      severity: 'warning',
      title: 'Inconsistent focus order',
      description: 'Visual order does not match DOM order, which may confuse keyboard users.',
      element: 'Navigation/Menu Items',
      wcag_criteria: 'WCAG 2.1 - 2.4.3 Focus Order',
      suggestion: 'Reorder elements to match visual layout.',
      is_fixed: false,
      is_ignored: false
    },
    {
      id: 'issue_4',
      category: 'touch_target',
      severity: 'warning',
      title: 'Touch target too small',
      description: 'Interactive element is only 24x24px, below the recommended 44x44px minimum.',
      element: 'Icon Button/Close',
      wcag_criteria: 'WCAG 2.1 - 2.5.5 Target Size',
      suggestion: 'Increase touch target to at least 44x44px.',
      is_fixed: false,
      is_ignored: false
    }
  ]);
  const [selectedColorBlindness, setSelectedColorBlindness] = useState<ColorBlindnessType>(COLOR_BLINDNESS_TYPES[0]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [contrastColors, setContrastColors] = useState({ foreground: '#333333', background: '#ffffff' });
  const [contrastResult, setContrastResult] = useState<ContrastResult | null>(null);
  const [screenReaderText, setScreenReaderText] = useState<string[]>([]);
  const [focusOrder, setFocusOrder] = useState<{ id: string; name: string; order: number }[]>([]);
  const [expandedCategories, setExpandedCategories] = useState<string[]>(['contrast', 'alt_text']);

  const runAccessibilityTest = useCallback(async () => {
    setIsRunningTest(true);
    try {
      const response = await fetch('/api/v1/accessibility/tests/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_id: designId })
      });

      if (response.ok) {
        const result = await response.json();
        // Fetch issues for this test
        const issuesResponse = await fetch(`/api/v1/accessibility/tests/${result.id}/issues/`);
        if (issuesResponse.ok) {
          const issuesData = await issuesResponse.json();
          setIssues(issuesData);
        }
      }
    } catch (error) {
      console.error('Test error:', error);
    } finally {
      setIsRunningTest(false);
    }
  }, [designId]);

  const checkContrast = useCallback(() => {
    // Simple contrast calculation
    const getLuminance = (hex: string) => {
      const rgb = parseInt(hex.slice(1), 16);
      const r = ((rgb >> 16) & 0xff) / 255;
      const g = ((rgb >> 8) & 0xff) / 255;
      const b = (rgb & 0xff) / 255;

      const transform = (c: number) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      return 0.2126 * transform(r) + 0.7152 * transform(g) + 0.0722 * transform(b);
    };

    const l1 = getLuminance(contrastColors.foreground);
    const l2 = getLuminance(contrastColors.background);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

    setContrastResult({
      foreground: contrastColors.foreground,
      background: contrastColors.background,
      ratio: Math.round(ratio * 100) / 100,
      aa_normal: ratio >= 4.5,
      aa_large: ratio >= 3,
      aaa_normal: ratio >= 7,
      aaa_large: ratio >= 4.5
    });
  }, [contrastColors]);

  const simulateColorBlindness = useCallback(async () => {
    setIsSimulating(true);
    try {
      await fetch('/api/v1/accessibility/simulate-colorblindness/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          design_id: designId,
          type: selectedColorBlindness.type 
        })
      });
    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setIsSimulating(false);
    }
  }, [designId, selectedColorBlindness]);

  const generateScreenReaderPreview = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/accessibility/screen-reader-preview/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ design_id: designId })
      });

      if (response.ok) {
        const result = await response.json();
        setScreenReaderText(result.reading_order || [
          'Navigation landmark',
          'Link: Home',
          'Link: About, current page',
          'Link: Products',
          'Link: Contact',
          'Main content landmark',
          'Heading level 1: Welcome to Our Site',
          'Paragraph: We provide excellent services...',
          'Button: Get Started',
          'Image: Team photo, A diverse group of professionals'
        ]);
      }
    } catch (error) {
      console.error('Screen reader preview error:', error);
    }
  }, [designId]);

  const groupedIssues = ISSUE_CATEGORIES.map(cat => ({
    ...cat,
    issues: issues.filter(i => i.category === cat.key && !i.is_ignored)
  })).filter(cat => cat.issues.length > 0);

  const toggleCategory = (key: string) => {
    setExpandedCategories(prev => 
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'text-red-500 bg-red-100 dark:bg-red-900/30';
      case 'warning': return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900/30';
      case 'info': return 'text-blue-500 bg-blue-100 dark:bg-blue-900/30';
      default: return 'text-gray-500 bg-gray-100';
    }
  };

  const errorCount = issues.filter(i => i.severity === 'error' && !i.is_ignored).length;
  const warningCount = issues.filter(i => i.severity === 'warning' && !i.is_ignored).length;

  return (
    <TooltipProvider>
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Accessibility Testing</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Test and improve design accessibility
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  onClick={runAccessibilityTest}
                  disabled={isRunningTest}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {isRunningTest ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {isRunningTest ? 'Running...' : 'Run Test'}
                </button>
              </TooltipTrigger>
              <TooltipContent>Scan the design for accessibility issues</TooltipContent>
            </Tooltip>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                  <Download className="w-4 h-4" />
                  Export Report
                  <ChevronDown className="w-3 h-3 ml-0.5" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-44">
                <DropdownMenuItem className="gap-2"><FileText size={14} />Export as PDF</DropdownMenuItem>
                <DropdownMenuItem className="gap-2"><Table2 size={14} />Export as CSV</DropdownMenuItem>
                <DropdownMenuItem className="gap-2"><FileJson size={14} />Export as JSON</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 mt-4 flex-wrap">
          {[
            { id: 'issues', label: 'Issues', icon: AlertTriangle, badge: errorCount + warningCount },
            { id: 'colorblind', label: 'Color Blindness', icon: Eye, badge: null },
            { id: 'screenreader', label: 'Screen Reader', icon: Volume2, badge: null },
            { id: 'focus', label: 'Focus Order', icon: Target, badge: null },
            { id: 'contrast', label: 'Contrast Checker', icon: Contrast, badge: null },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'issues' | 'colorblind' | 'screenreader' | 'focus' | 'contrast')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                  : 'text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.badge !== null && tab.badge > 0 && (
                <Badge className={`ml-0.5 text-[9px] px-1 py-0 h-4 ${
                  tab.id === 'issues' && errorCount > 0
                    ? 'bg-red-500/20 text-red-500 border-red-500/30'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
                }`}>
                  {tab.badge}
                </Badge>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === 'issues' && (
          <div className="space-y-4">
            {/* Summary */}
            <div className="grid grid-cols-4 gap-4">
              {[
                { label: 'Errors', count: issues.filter(i => i.severity === 'error' && !i.is_ignored).length, color: 'bg-red-500' },
                { label: 'Warnings', count: issues.filter(i => i.severity === 'warning' && !i.is_ignored).length, color: 'bg-yellow-500' },
                { label: 'Info', count: issues.filter(i => i.severity === 'info' && !i.is_ignored).length, color: 'bg-blue-500' },
                { label: 'Fixed', count: issues.filter(i => i.is_fixed).length, color: 'bg-green-500' },
              ].map(stat => (
                <div key={stat.label} className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
                      <span className="text-lg font-bold text-white">{stat.count}</span>
                    </div>
                    <span className="text-gray-600 dark:text-gray-300">{stat.label}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Grouped Issues */}
            <div className="space-y-3">
              {groupedIssues.map(category => (
                <div key={category.key} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
                  <button
                    onClick={() => toggleCategory(category.key)}
                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50"
                  >
                    <div className="flex items-center gap-3">
                      <category.icon className="w-5 h-5 text-gray-500" />
                      <span className="font-medium text-gray-900 dark:text-white">{category.label}</span>
                      <span className="px-2 py-0.5 text-xs bg-gray-100 dark:bg-gray-700 rounded-full">
                        {category.issues.length}
                      </span>
                    </div>
                    {expandedCategories.includes(category.key) 
                      ? <ChevronDown className="w-5 h-5 text-gray-400" />
                      : <ChevronRight className="w-5 h-5 text-gray-400" />
                    }
                  </button>
                  
                  {expandedCategories.includes(category.key) && (
                    <div className="border-t border-gray-200 dark:border-gray-700 divide-y divide-gray-200 dark:divide-gray-700">
                      {category.issues.map(issue => (
                        <div
                          key={issue.id}
                          onClick={() => onIssueSelect?.(issue)}
                          className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                        >
                          <div className="flex items-start gap-3">
                            <div className={`p-1.5 rounded-lg ${getSeverityColor(issue.severity)}`}>
                              {issue.severity === 'error' && <XCircle className="w-4 h-4" />}
                              {issue.severity === 'warning' && <AlertTriangle className="w-4 h-4" />}
                              {issue.severity === 'info' && <Info className="w-4 h-4" />}
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">{issue.title}</h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{issue.description}</p>
                              {issue.element && (
                                <p className="text-xs text-gray-500 mt-2">
                                  Element: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{issue.element}</code>
                                </p>
                              )}
                              {issue.suggestion && (
                                <p className="text-sm text-green-600 mt-2 flex items-center gap-1">
                                  <CheckCircle className="w-4 h-4" />
                                  {issue.suggestion}
                                </p>
                              )}
                              <div className="flex items-center gap-3 mt-3">
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); onFix?.(issue.id); }}
                                      className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-500 font-medium transition-colors"
                                    >
                                      <Zap size={12} />
                                      Auto-fix
                                    </button>
                                  </TooltipTrigger>
                                  <TooltipContent>Automatically apply the suggested fix</TooltipContent>
                                </Tooltip>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); }}
                                      className="text-xs text-gray-500 hover:text-gray-400 transition-colors"
                                    >
                                      Ignore
                                    </button>
                                  </TooltipTrigger>
                                  <TooltipContent>Mark this issue as ignored</TooltipContent>
                                </Tooltip>
                                {issue.wcag_criteria && (
                                  <span className="text-xs text-gray-400 font-mono">{issue.wcag_criteria}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {groupedIssues.length === 0 && (
                <div className="text-center py-16 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                  <CheckCircle className="w-20 h-20 mx-auto mb-4 text-green-500" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">All Clear!</h3>
                  <p className="text-gray-500 mb-4">No accessibility issues found. Great work!</p>
                  <button
                    onClick={runAccessibilityTest}
                    className="flex items-center gap-2 mx-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Run Another Test
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'colorblind' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Color Blindness Simulation</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Preview how your design appears to people with different types of color vision deficiency.
              </p>

              <div className="grid grid-cols-4 gap-3">
                {COLOR_BLINDNESS_TYPES.map(type => (
                  <button
                    key={type.type}
                    onClick={() => setSelectedColorBlindness(type)}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      selectedColorBlindness.type === type.type
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium text-gray-900 dark:text-white">{type.label}</div>
                    <div className="text-xs text-gray-500 mt-1">{type.description}</div>
                    <div className="text-xs text-gray-400 mt-1">{type.prevalence}</div>
                  </button>
                ))}
              </div>

              <button
                onClick={simulateColorBlindness}
                disabled={isSimulating}
                className="mt-6 flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isSimulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Eye className="w-4 h-4" />}
                Apply Simulation
              </button>
            </div>

            {/* Preview area */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h4 className="font-medium text-gray-900 dark:text-white mb-4">Preview</h4>
              <div className="aspect-video bg-gray-100 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                <span className="text-gray-500">Design preview will appear here</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'screenreader' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900 dark:text-white">Screen Reader Preview</h3>
                <button
                  onClick={generateScreenReaderPreview}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <RefreshCw className="w-4 h-4" />
                  Generate Preview
                </button>
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                This shows how a screen reader would announce your design elements in order.
              </p>

              <div className="space-y-2 max-h-96 overflow-auto">
                {screenReaderText.map((text, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                  >
                    <span className="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium">
                      {i + 1}
                    </span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{text}</span>
                  </div>
                ))}
                {screenReaderText.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Volume2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>Click &ldquo;Generate Preview&rdquo; to see screen reader output</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'focus' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Focus Order Testing</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Verify that keyboard navigation follows a logical, predictable order.
              </p>

              <div className="space-y-2">
                {[
                  { id: '1', name: 'Skip to main content link', order: 1 },
                  { id: '2', name: 'Logo (Home link)', order: 2 },
                  { id: '3', name: 'Navigation: Home', order: 3 },
                  { id: '4', name: 'Navigation: About', order: 4 },
                  { id: '5', name: 'Navigation: Products', order: 5 },
                  { id: '6', name: 'Search input', order: 6 },
                  { id: '7', name: 'Main heading', order: 7 },
                  { id: '8', name: 'Call to action button', order: 8 },
                ].map((item, i) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-8 h-8 bg-blue-500 text-white rounded-lg flex items-center justify-center font-medium">
                        {item.order}
                      </span>
                      <ArrowRight className="w-4 h-4 text-gray-400" />
                    </div>
                    <span className="text-sm text-gray-700 dark:text-gray-300">{item.name}</span>
                    <CheckCircle className="w-4 h-4 text-green-500 ml-auto" />
                  </div>
                ))}
              </div>

              <button className="mt-4 flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                <Keyboard className="w-4 h-4" />
                Test with Keyboard (Tab through)
              </button>
            </div>
          </div>
        )}

        {activeTab === 'contrast' && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Contrast Checker</h3>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Foreground Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={contrastColors.foreground}
                      onChange={(e) => setContrastColors({ ...contrastColors, foreground: e.target.value })}
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={contrastColors.foreground}
                      onChange={(e) => setContrastColors({ ...contrastColors, foreground: e.target.value })}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 font-mono"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Background Color
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="color"
                      value={contrastColors.background}
                      onChange={(e) => setContrastColors({ ...contrastColors, background: e.target.value })}
                      className="w-12 h-10 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={contrastColors.background}
                      onChange={(e) => setContrastColors({ ...contrastColors, background: e.target.value })}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 font-mono"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={checkContrast}
                className="mt-4 flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Contrast className="w-4 h-4" />
                Check Contrast
              </button>

              {/* Preview */}
              <div 
                className="mt-6 p-8 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: contrastColors.background }}
              >
                <span 
                  className="text-2xl font-bold"
                  style={{ color: contrastColors.foreground }}
                >
                  Sample Text
                </span>
              </div>

              {/* Results */}
              {contrastResult && (
                <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <div className="text-center mb-4">
                    <span className="text-4xl font-bold text-gray-900 dark:text-white">
                      {contrastResult.ratio}:1
                    </span>
                    <p className="text-gray-500 mt-1">Contrast Ratio</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { level: 'AA', size: 'Normal Text', pass: contrastResult.aa_normal, required: '4.5:1' },
                      { level: 'AA', size: 'Large Text', pass: contrastResult.aa_large, required: '3:1' },
                      { level: 'AAA', size: 'Normal Text', pass: contrastResult.aaa_normal, required: '7:1' },
                      { level: 'AAA', size: 'Large Text', pass: contrastResult.aaa_large, required: '4.5:1' },
                    ].map((item, i) => (
                      <div key={i} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <div>
                          <span className="font-medium text-gray-900 dark:text-white">{item.level}</span>
                          <span className="text-gray-500 ml-2">{item.size}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400">{item.required}</span>
                          {item.pass 
                            ? <CheckCircle className="w-5 h-5 text-green-500" />
                            : <XCircle className="w-5 h-5 text-red-500" />
                          }
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
    </TooltipProvider>
  );
}

export default AccessibilityTesting;

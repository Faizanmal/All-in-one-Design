'use client';

import React, { useState, useMemo, useCallback } from 'react';
import {
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
  Eye,
  EyeOff,
  Settings,
  Play,
  RefreshCw,
  Filter,
  Search,
  ChevronDown,
  ChevronRight,
  Zap,
  Shield,
  Palette,
  Type,
  Layout,
  Layers,
  MoreHorizontal,
  Download,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Check,
  X,
  ExternalLink,
  Accessibility,
  Contrast,
  Focus,
  Keyboard,
} from 'lucide-react';

// Types
interface LintIssue {
  id: string;
  type: 'error' | 'warning' | 'info';
  category: 'style' | 'accessibility' | 'naming' | 'layout' | 'consistency';
  ruleId: string;
  ruleName: string;
  message: string;
  suggestion?: string;
  elementId: string;
  elementName: string;
  elementType: string;
  autoFixable: boolean;
  ignored: boolean;
  location?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface AccessibilityIssue {
  id: string;
  type: 'critical' | 'serious' | 'moderate' | 'minor';
  wcagLevel: 'A' | 'AA' | 'AAA';
  wcagCriteria: string;
  title: string;
  description: string;
  elementId: string;
  elementName: string;
  impact: string;
  suggestion: string;
  resources?: { title: string; url: string }[];
}

interface LintReport {
  id: string;
  name: string;
  createdAt: string;
  duration: number;
  totalIssues: number;
  errors: number;
  warnings: number;
  infos: number;
  passedRules: number;
  failedRules: number;
  issues: LintIssue[];
}

interface AccessibilityReport {
  id: string;
  name: string;
  createdAt: string;
  wcagVersion: string;
  conformanceLevel: 'A' | 'AA' | 'AAA';
  score: number;
  criticalCount: number;
  seriousCount: number;
  moderateCount: number;
  minorCount: number;
  issues: AccessibilityIssue[];
}

interface QAStats {
  totalChecks: number;
  passedChecks: number;
  failedChecks: number;
  averageScore: number;
  trend: 'up' | 'down' | 'stable';
  lastCheckDate: string;
}

// Mock data
const mockLintIssues: LintIssue[] = [
  {
    id: 'lint-1',
    type: 'error',
    category: 'style',
    ruleId: 'color-not-in-system',
    ruleName: 'Color not in design system',
    message: 'Color #FF5733 is not defined in the design system',
    suggestion: 'Replace with Primary Red (#EF4444)',
    elementId: 'btn-cta',
    elementName: 'CTA Button',
    elementType: 'Component',
    autoFixable: true,
    ignored: false,
    location: { x: 100, y: 200, width: 120, height: 40 },
  },
  {
    id: 'lint-2',
    type: 'error',
    category: 'naming',
    ruleId: 'naming-convention',
    ruleName: 'Naming convention violation',
    message: 'Layer name "Frame 47" does not follow naming convention',
    suggestion: 'Rename to follow pattern: ComponentName/VariantName',
    elementId: 'frame-47',
    elementName: 'Frame 47',
    elementType: 'Frame',
    autoFixable: false,
    ignored: false,
  },
  {
    id: 'lint-3',
    type: 'warning',
    category: 'consistency',
    ruleId: 'font-size-not-standard',
    ruleName: 'Non-standard font size',
    message: 'Font size 15px is not in the type scale',
    suggestion: 'Use 14px (sm) or 16px (base) instead',
    elementId: 'text-1',
    elementName: 'Description Text',
    elementType: 'Text',
    autoFixable: true,
    ignored: false,
  },
  {
    id: 'lint-4',
    type: 'warning',
    category: 'layout',
    ruleId: 'spacing-not-standard',
    ruleName: 'Non-standard spacing',
    message: 'Padding of 18px is not in the spacing scale',
    suggestion: 'Use 16px (4) or 20px (5) instead',
    elementId: 'card-1',
    elementName: 'Product Card',
    elementType: 'Component',
    autoFixable: true,
    ignored: false,
  },
  {
    id: 'lint-5',
    type: 'info',
    category: 'consistency',
    ruleId: 'detached-style',
    ruleName: 'Detached from style',
    message: 'This element has overrides that detach it from the base style',
    elementId: 'heading-1',
    elementName: 'Page Title',
    elementType: 'Text',
    autoFixable: false,
    ignored: false,
  },
];

const mockAccessibilityIssues: AccessibilityIssue[] = [
  {
    id: 'a11y-1',
    type: 'critical',
    wcagLevel: 'A',
    wcagCriteria: '1.4.3',
    title: 'Insufficient color contrast',
    description: 'Text has a contrast ratio of 2.5:1 which fails WCAG AA requirements (4.5:1 for normal text)',
    elementId: 'light-text',
    elementName: 'Light Gray Text',
    impact: 'Users with visual impairments may not be able to read this text',
    suggestion: 'Darken the text color to at least #737373 to meet 4.5:1 contrast ratio',
    resources: [
      { title: 'Understanding SC 1.4.3', url: 'https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html' },
    ],
  },
  {
    id: 'a11y-2',
    type: 'serious',
    wcagLevel: 'A',
    wcagCriteria: '2.4.4',
    title: 'Link purpose unclear',
    description: 'Link text "Click here" does not describe its purpose',
    elementId: 'link-1',
    elementName: 'Generic Link',
    impact: 'Screen reader users may not understand where this link leads',
    suggestion: 'Replace with descriptive text like "View product details" or "Learn more about pricing"',
  },
  {
    id: 'a11y-3',
    type: 'moderate',
    wcagLevel: 'AA',
    wcagCriteria: '1.4.11',
    title: 'UI component contrast issue',
    description: 'Button border has insufficient contrast against background',
    elementId: 'btn-secondary',
    elementName: 'Secondary Button',
    impact: 'Users may have difficulty perceiving button boundaries',
    suggestion: 'Increase border contrast to at least 3:1 against the background',
  },
  {
    id: 'a11y-4',
    type: 'minor',
    wcagLevel: 'AAA',
    wcagCriteria: '1.4.6',
    title: 'Enhanced contrast recommendation',
    description: 'Large text could have better contrast for AAA compliance',
    elementId: 'heading-main',
    elementName: 'Main Heading',
    impact: 'Users with low vision would benefit from increased contrast',
    suggestion: 'Consider using #1a1a1a for text on white backgrounds',
  },
];

const mockStats: QAStats = {
  totalChecks: 156,
  passedChecks: 142,
  failedChecks: 14,
  averageScore: 91,
  trend: 'up',
  lastCheckDate: '2024-01-15T14:30:00Z',
};

// Helper Components
const IssueIcon: React.FC<{ type: LintIssue['type'] | AccessibilityIssue['type'] }> = ({ type }) => {
  const config = {
    error: { icon: XCircle, color: 'text-red-400' },
    critical: { icon: XCircle, color: 'text-red-400' },
    warning: { icon: AlertTriangle, color: 'text-yellow-400' },
    serious: { icon: AlertTriangle, color: 'text-orange-400' },
    moderate: { icon: AlertCircle, color: 'text-yellow-400' },
    info: { icon: Info, color: 'text-blue-400' },
    minor: { icon: Info, color: 'text-blue-400' },
  };

  const { icon: Icon, color } = config[type];
  return <Icon size={14} className={color} />;
};

const CategoryIcon: React.FC<{ category: LintIssue['category'] }> = ({ category }) => {
  const icons = {
    style: Palette,
    accessibility: Accessibility,
    naming: Type,
    layout: Layout,
    consistency: Layers,
  };

  const Icon = icons[category];
  return <Icon size={12} className="text-gray-400" />;
};

const ScoreGauge: React.FC<{ score: number; size?: 'sm' | 'lg' }> = ({ score, size = 'lg' }) => {
  const radius = size === 'lg' ? 45 : 25;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 90) return '#22C55E';
    if (s >= 70) return '#F59E0B';
    if (s >= 50) return '#F97316';
    return '#EF4444';
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={radius * 2 + 10} height={radius * 2 + 10} className="-rotate-90">
        <circle
          cx={radius + 5}
          cy={radius + 5}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={size === 'lg' ? 8 : 4}
          className="text-gray-700"
        />
        <circle
          cx={radius + 5}
          cy={radius + 5}
          r={radius}
          fill="none"
          stroke={getColor(score)}
          strokeWidth={size === 'lg' ? 8 : 4}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
      </svg>
      <span
        className={`absolute font-bold ${size === 'lg' ? 'text-2xl' : 'text-sm'}`}
        style={{ color: getColor(score) }}
      >
        {score}
      </span>
    </div>
  );
};

const TrendIndicator: React.FC<{ trend: QAStats['trend']; value?: number }> = ({ trend, value }) => {
  const config = {
    up: { icon: TrendingUp, color: 'text-green-400', bg: 'bg-green-500/20' },
    down: { icon: TrendingDown, color: 'text-red-400', bg: 'bg-red-500/20' },
    stable: { icon: Minus, color: 'text-gray-400', bg: 'bg-gray-500/20' },
  };

  const { icon: Icon, color, bg } = config[trend];

  return (
    <span className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs ${color} ${bg}`}>
      <Icon size={12} />
      {value !== undefined && `${value}%`}
    </span>
  );
};

// Lint Issue Item Component
interface LintIssueItemProps {
  issue: LintIssue;
  isExpanded: boolean;
  onToggle: () => void;
  onFix: (id: string) => void;
  onIgnore: (id: string) => void;
  onJumpTo: (id: string) => void;
}

const LintIssueItem: React.FC<LintIssueItemProps> = ({
  issue,
  isExpanded,
  onToggle,
  onFix,
  onIgnore,
  onJumpTo,
}) => {
  return (
    <div
      className={`border-b border-gray-700/50 ${
        issue.ignored ? 'opacity-50' : ''
      }`}
    >
      <div
        className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800/50 cursor-pointer"
        onClick={onToggle}
      >
        <button className="p-0.5">
          {isExpanded ? (
            <ChevronDown size={12} className="text-gray-400" />
          ) : (
            <ChevronRight size={12} className="text-gray-400" />
          )}
        </button>
        
        <IssueIcon type={issue.type} />
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-200 truncate">{issue.message}</p>
          <div className="flex items-center gap-2 mt-0.5">
            <CategoryIcon category={issue.category} />
            <span className="text-xs text-gray-500">{issue.elementName}</span>
            <span className="text-xs text-gray-600">•</span>
            <span className="text-xs text-gray-500">{issue.ruleName}</span>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {issue.autoFixable && !issue.ignored && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onFix(issue.id);
              }}
              className="p-1 text-green-400 hover:bg-green-500/20 rounded"
              title="Auto-fix"
            >
              <Zap size={12} />
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onJumpTo(issue.elementId);
            }}
            className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Jump to element"
          >
            <ExternalLink size={12} />
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="px-8 pb-3 space-y-2">
          {issue.suggestion && (
            <div className="bg-gray-800/50 rounded p-2">
              <p className="text-xs text-gray-400 mb-1">Suggestion</p>
              <p className="text-sm text-gray-200">{issue.suggestion}</p>
            </div>
          )}
          <div className="flex items-center gap-2">
            {issue.autoFixable && !issue.ignored && (
              <button
                onClick={() => onFix(issue.id)}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
              >
                <Zap size={10} />
                Apply Fix
              </button>
            )}
            <button
              onClick={() => onIgnore(issue.id)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
            >
              {issue.ignored ? <Eye size={10} /> : <EyeOff size={10} />}
              {issue.ignored ? 'Unignore' : 'Ignore'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Accessibility Issue Item Component
interface A11yIssueItemProps {
  issue: AccessibilityIssue;
  isExpanded: boolean;
  onToggle: () => void;
  onJumpTo: (id: string) => void;
}

const A11yIssueItem: React.FC<A11yIssueItemProps> = ({
  issue,
  isExpanded,
  onToggle,
  onJumpTo,
}) => {
  return (
    <div className="border-b border-gray-700/50">
      <div
        className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800/50 cursor-pointer"
        onClick={onToggle}
      >
        <button className="p-0.5">
          {isExpanded ? (
            <ChevronDown size={12} className="text-gray-400" />
          ) : (
            <ChevronRight size={12} className="text-gray-400" />
          )}
        </button>
        
        <IssueIcon type={issue.type} />
        
        <div className="flex-1 min-w-0">
          <p className="text-sm text-gray-200 truncate">{issue.title}</p>
          <div className="flex items-center gap-2 mt-0.5">
            <span className="text-xs px-1 py-0.5 rounded bg-purple-500/20 text-purple-400">
              WCAG {issue.wcagLevel} - {issue.wcagCriteria}
            </span>
            <span className="text-xs text-gray-500">{issue.elementName}</span>
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            onJumpTo(issue.elementId);
          }}
          className="p-1 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
          title="Jump to element"
        >
          <ExternalLink size={12} />
        </button>
      </div>

      {isExpanded && (
        <div className="px-8 pb-3 space-y-2">
          <p className="text-sm text-gray-300">{issue.description}</p>
          
          <div className="bg-orange-900/20 border border-orange-800/50 rounded p-2">
            <p className="text-xs text-orange-400 mb-1">Impact</p>
            <p className="text-sm text-gray-200">{issue.impact}</p>
          </div>
          
          <div className="bg-green-900/20 border border-green-800/50 rounded p-2">
            <p className="text-xs text-green-400 mb-1">How to fix</p>
            <p className="text-sm text-gray-200">{issue.suggestion}</p>
          </div>

          {issue.resources && issue.resources.length > 0 && (
            <div className="pt-2">
              <p className="text-xs text-gray-400 mb-1">Learn more</p>
              <div className="flex flex-wrap gap-2">
                {issue.resources.map((resource, i) => (
                  <a
                    key={i}
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-400 hover:underline flex items-center gap-1"
                  >
                    {resource.title}
                    <ExternalLink size={10} />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Main Component
interface DesignQAPanelProps {
  projectId?: string;
  onRunCheck?: () => Promise<void>;
  onJumpToElement?: (elementId: string) => void;
  onExportReport?: (format: 'pdf' | 'csv' | 'json') => void;
}

export const DesignQAPanel: React.FC<DesignQAPanelProps> = ({
  projectId,
  onRunCheck,
  onJumpToElement,
  onExportReport,
}) => {
  const [activeTab, setActiveTab] = useState<'lint' | 'accessibility'>('lint');
  const [lintIssues, setLintIssues] = useState<LintIssue[]>(mockLintIssues);
  const [a11yIssues] = useState<AccessibilityIssue[]>(mockAccessibilityIssues);
  const [stats] = useState<QAStats>(mockStats);
  const [isRunning, setIsRunning] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'error' | 'warning' | 'info'>('all');
  const [categoryFilter, setCategoryFilter] = useState<'all' | LintIssue['category']>('all');
  const [showIgnored, setShowIgnored] = useState(false);
  const [expandedIssues, setExpandedIssues] = useState<Set<string>>(new Set());

  // Filtered issues
  const filteredLintIssues = useMemo(() => {
    let result = lintIssues;

    if (searchQuery) {
      result = result.filter(
        (issue) =>
          issue.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
          issue.elementName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          issue.ruleName.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (typeFilter !== 'all') {
      result = result.filter((issue) => issue.type === typeFilter);
    }

    if (categoryFilter !== 'all') {
      result = result.filter((issue) => issue.category === categoryFilter);
    }

    if (!showIgnored) {
      result = result.filter((issue) => !issue.ignored);
    }

    return result;
  }, [lintIssues, searchQuery, typeFilter, categoryFilter, showIgnored]);

  const filteredA11yIssues = useMemo(() => {
    let result = a11yIssues;

    if (searchQuery) {
      result = result.filter(
        (issue) =>
          issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          issue.elementName.toLowerCase().includes(searchQuery.toLowerCase()) ||
          issue.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return result;
  }, [a11yIssues, searchQuery]);

  // Counts
  const lintCounts = useMemo(() => {
    const active = lintIssues.filter((i) => !i.ignored);
    return {
      total: active.length,
      errors: active.filter((i) => i.type === 'error').length,
      warnings: active.filter((i) => i.type === 'warning').length,
      infos: active.filter((i) => i.type === 'info').length,
      autoFixable: active.filter((i) => i.autoFixable).length,
    };
  }, [lintIssues]);

  const a11yCounts = useMemo(() => ({
    total: a11yIssues.length,
    critical: a11yIssues.filter((i) => i.type === 'critical').length,
    serious: a11yIssues.filter((i) => i.type === 'serious').length,
    moderate: a11yIssues.filter((i) => i.type === 'moderate').length,
    minor: a11yIssues.filter((i) => i.type === 'minor').length,
  }), [a11yIssues]);

  // Handlers
  const handleRunCheck = useCallback(async () => {
    setIsRunning(true);
    try {
      await onRunCheck?.();
      // Simulate check
      await new Promise((r) => setTimeout(r, 2000));
    } finally {
      setIsRunning(false);
    }
  }, [onRunCheck]);

  const handleToggleExpand = useCallback((id: string) => {
    setExpandedIssues((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleFixIssue = useCallback((id: string) => {
    setLintIssues((prev) => prev.filter((issue) => issue.id !== id));
  }, []);

  const handleFixAll = useCallback(() => {
    setLintIssues((prev) => prev.filter((issue) => !issue.autoFixable || issue.ignored));
  }, []);

  const handleIgnoreIssue = useCallback((id: string) => {
    setLintIssues((prev) =>
      prev.map((issue) =>
        issue.id === id ? { ...issue, ignored: !issue.ignored } : issue
      )
    );
  }, []);

  const handleJumpTo = useCallback((elementId: string) => {
    onJumpToElement?.(elementId);
  }, [onJumpToElement]);

  // Calculate accessibility score
  const a11yScore = useMemo(() => {
    const weights = { critical: 25, serious: 15, moderate: 8, minor: 3 };
    const totalPenalty = a11yIssues.reduce(
      (sum, issue) => sum + weights[issue.type],
      0
    );
    return Math.max(0, 100 - totalPenalty);
  }, [a11yIssues]);

  return (
    <div className="flex flex-col h-full bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-850 border-b border-gray-700">
        <div className="flex items-center gap-3">
          <Shield size={18} className="text-blue-400" />
          <div>
            <h3 className="text-sm font-semibold text-white">Design QA</h3>
            <p className="text-xs text-gray-500">
              Last check: {new Date(stats.lastCheckDate).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRunCheck}
            disabled={isRunning}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {isRunning ? (
              <RefreshCw size={14} className="animate-spin" />
            ) : (
              <Play size={14} />
            )}
            {isRunning ? 'Running...' : 'Run Check'}
          </button>
          <button
            onClick={() => onExportReport?.('pdf')}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            title="Export Report"
          >
            <Download size={16} />
          </button>
          <button className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded">
            <Settings size={16} />
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4 p-4 border-b border-gray-700">
        <div className="text-center">
          <ScoreGauge score={stats.averageScore} size="lg" />
          <p className="text-xs text-gray-400 mt-2">Overall Score</p>
          <TrendIndicator trend={stats.trend} value={5} />
        </div>
        <div className="flex flex-col justify-center">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Passed</span>
            <span className="text-sm font-medium text-green-400">{stats.passedChecks}</span>
          </div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Failed</span>
            <span className="text-sm font-medium text-red-400">{stats.failedChecks}</span>
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 to-green-400"
              style={{ width: `${(stats.passedChecks / stats.totalChecks) * 100}%` }}
            />
          </div>
        </div>
        <div className="flex flex-col justify-center space-y-1">
          <div className="flex items-center gap-2">
            <XCircle size={12} className="text-red-400" />
            <span className="text-xs text-gray-400">Errors</span>
            <span className="text-sm font-medium text-gray-200 ml-auto">{lintCounts.errors}</span>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle size={12} className="text-yellow-400" />
            <span className="text-xs text-gray-400">Warnings</span>
            <span className="text-sm font-medium text-gray-200 ml-auto">{lintCounts.warnings}</span>
          </div>
          <div className="flex items-center gap-2">
            <Info size={12} className="text-blue-400" />
            <span className="text-xs text-gray-400">Info</span>
            <span className="text-sm font-medium text-gray-200 ml-auto">{lintCounts.infos}</span>
          </div>
        </div>
        <div className="flex flex-col justify-center items-center">
          <div className="text-center mb-2">
            <span className="text-2xl font-bold text-white">{a11yScore}</span>
            <span className="text-xs text-gray-400 block">A11y Score</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-500">{a11yCounts.critical} critical</span>
            <span className="text-gray-600">•</span>
            <span className="text-xs text-gray-500">{a11yCounts.serious} serious</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        <button
          onClick={() => setActiveTab('lint')}
          className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'lint'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Design Lint ({lintCounts.total})
        </button>
        <button
          onClick={() => setActiveTab('accessibility')}
          className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'accessibility'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Accessibility ({a11yCounts.total})
        </button>
      </div>

      {/* Search and Filters */}
      <div className="px-4 py-2 border-b border-gray-700 space-y-2">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search issues..."
            className="w-full pl-9 pr-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        
        {activeTab === 'lint' && (
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-0.5">
              {(['all', 'error', 'warning', 'info'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => setTypeFilter(type)}
                  className={`px-2 py-1 text-xs rounded-md transition-colors ${
                    typeFilter === type
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
            
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value as typeof categoryFilter)}
              className="px-2 py-1 text-xs bg-gray-800 border border-gray-700 rounded-lg text-gray-300"
            >
              <option value="all">All Categories</option>
              <option value="style">Style</option>
              <option value="naming">Naming</option>
              <option value="layout">Layout</option>
              <option value="consistency">Consistency</option>
              <option value="accessibility">Accessibility</option>
            </select>

            <label className="flex items-center gap-1.5 text-xs text-gray-400 cursor-pointer">
              <input
                type="checkbox"
                checked={showIgnored}
                onChange={(e) => setShowIgnored(e.target.checked)}
                className="rounded bg-gray-700 border-gray-600"
              />
              Show ignored
            </label>

            {lintCounts.autoFixable > 0 && (
              <button
                onClick={handleFixAll}
                className="ml-auto flex items-center gap-1 px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
              >
                <Zap size={10} />
                Fix All ({lintCounts.autoFixable})
              </button>
            )}
          </div>
        )}
      </div>

      {/* Issues List */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'lint' ? (
          filteredLintIssues.length > 0 ? (
            filteredLintIssues.map((issue) => (
              <LintIssueItem
                key={issue.id}
                issue={issue}
                isExpanded={expandedIssues.has(issue.id)}
                onToggle={() => handleToggleExpand(issue.id)}
                onFix={handleFixIssue}
                onIgnore={handleIgnoreIssue}
                onJumpTo={handleJumpTo}
              />
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-gray-500">
              <CheckCircle size={32} className="mb-2 text-green-400 opacity-50" />
              <p className="text-sm">No issues found</p>
              <p className="text-xs">Your design looks great!</p>
            </div>
          )
        ) : (
          filteredA11yIssues.length > 0 ? (
            filteredA11yIssues.map((issue) => (
              <A11yIssueItem
                key={issue.id}
                issue={issue}
                isExpanded={expandedIssues.has(issue.id)}
                onToggle={() => handleToggleExpand(issue.id)}
                onJumpTo={handleJumpTo}
              />
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-32 text-gray-500">
              <Accessibility size={32} className="mb-2 text-green-400 opacity-50" />
              <p className="text-sm">No accessibility issues</p>
              <p className="text-xs">Great job on accessibility!</p>
            </div>
          )
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 bg-gray-850 border-t border-gray-700 text-xs text-gray-500 flex items-center justify-between">
        <span>
          {activeTab === 'lint'
            ? `${filteredLintIssues.length} issues`
            : `${filteredA11yIssues.length} issues`}
        </span>
        <span className="flex items-center gap-1">
          <Clock size={10} />
          Check duration: 1.2s
        </span>
      </div>
    </div>
  );
};

export default DesignQAPanel;

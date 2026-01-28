'use client';

import React, { useState } from 'react';
import { 
  useAccessibilityAudit,
  useApplyAccessibilityFixes,
  useCheckContrast,
  AccessibilityIssue
} from '@/hooks/use-new-features';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { 
  Accessibility,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Lightbulb,
  Wand2,
  Eye,
  Palette,
  Type,
  MousePointer,
  Image,
  Layout,
  RefreshCw
} from 'lucide-react';

interface AccessibilityAuditProps {
  projectId: string;
}

const severityConfig = {
  error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50', border: 'border-red-200' },
  warning: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-50', border: 'border-yellow-200' },
  suggestion: { icon: Lightbulb, color: 'text-blue-500', bg: 'bg-blue-50', border: 'border-blue-200' },
};

const categoryIcons: Record<string, React.ReactNode> = {
  color_contrast: <Eye className="h-4 w-4" />,
  text_sizing: <Type className="h-4 w-4" />,
  touch_targets: <MousePointer className="h-4 w-4" />,
  color_blindness: <Palette className="h-4 w-4" />,
  images: (
    // eslint-disable-next-line jsx-a11y/alt-text
    <Image className="h-4 w-4" aria-hidden="true" />
  ),
  layout: <Layout className="h-4 w-4" />,
  interactive: <MousePointer className="h-4 w-4" />,
  readability: <Type className="h-4 w-4" />,
};

function ScoreGauge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 90) return 'text-green-500';
    if (s >= 70) return 'text-yellow-500';
    if (s >= 50) return 'text-orange-500';
    return 'text-red-500';
  };

  const getScoreLabel = (s: number) => {
    if (s >= 90) return 'Excellent';
    if (s >= 70) return 'Good';
    if (s >= 50) return 'Needs Work';
    return 'Poor';
  };

  return (
    <div className="flex flex-col items-center">
      <div className={`text-5xl font-bold ${getScoreColor(score)}`}>{score}</div>
      <div className="text-sm text-muted-foreground mt-1">{getScoreLabel(score)}</div>
      <Progress value={score} className="w-32 mt-2" />
    </div>
  );
}

function IssueCard({ issue, selected, onSelect }: { 
  issue: AccessibilityIssue; 
  selected: boolean;
  onSelect: (checked: boolean) => void;
}) {
  const config = severityConfig[issue.severity];
  const Icon = config.icon;

  return (
    <div className={`p-4 rounded-lg border ${config.border} ${config.bg}`}>
      <div className="flex items-start gap-3">
        {issue.auto_fixable && (
          <Checkbox 
            checked={selected}
            onCheckedChange={onSelect}
            className="mt-1"
          />
        )}
        <Icon className={`h-5 w-5 ${config.color} flex-shrink-0 mt-0.5`} />
        <div className="flex-grow">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="font-medium">{issue.title}</h4>
            <Badge variant="outline" className="text-xs">{issue.wcag_criterion}</Badge>
            <Badge variant="secondary" className="text-xs">WCAG {issue.wcag_level}</Badge>
            {issue.auto_fixable && (
              <Badge className="text-xs bg-green-100 text-green-800">Auto-fixable</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">{issue.description}</p>
          {issue.component_id && (
            <p className="text-xs text-muted-foreground mt-2">
              Component: {issue.component_type} ({issue.component_id})
            </p>
          )}
          {issue.suggested_fix && (
            <div className="mt-2 p-2 bg-white rounded text-xs">
              <strong>Suggested fix:</strong>
              <pre className="mt-1 overflow-x-auto">
                {JSON.stringify(issue.suggested_fix, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ContrastChecker() {
  const [foreground, setForeground] = useState('#333333');
  const [background, setBackground] = useState('#FFFFFF');
  const checkContrast = useCheckContrast();

  const handleCheck = () => {
    checkContrast.mutate({ foreground, background });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Color Contrast Checker</CardTitle>
        <CardDescription>Check if your colors meet WCAG requirements</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="text-sm font-medium">Foreground</label>
            <div className="flex gap-2 mt-1">
              <Input 
                type="color" 
                value={foreground}
                onChange={(e) => setForeground(e.target.value)}
                className="w-12 h-10 p-1"
              />
              <Input 
                value={foreground}
                onChange={(e) => setForeground(e.target.value)}
                className="flex-1"
              />
            </div>
          </div>
          <div className="flex-1">
            <label className="text-sm font-medium">Background</label>
            <div className="flex gap-2 mt-1">
              <Input 
                type="color" 
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                className="w-12 h-10 p-1"
              />
              <Input 
                value={background}
                onChange={(e) => setBackground(e.target.value)}
                className="flex-1"
              />
            </div>
          </div>
        </div>

        <Button onClick={handleCheck} disabled={checkContrast.isPending}>
          Check Contrast
        </Button>

        {checkContrast.data && (
          <div className="p-4 border rounded-lg space-y-3">
            <div 
              className="p-4 rounded text-center text-lg font-medium"
              style={{ color: foreground, backgroundColor: background }}
            >
              Sample Text
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Contrast Ratio:</span>
                <span className="ml-2 font-bold">{checkContrast.data.contrast_ratio}:1</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">WCAG AA:</span>
                {checkContrast.data.passes_wcag_aa ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">WCAG AAA:</span>
                {checkContrast.data.passes_wcag_aaa ? (
                  <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-red-500" />
                )}
              </div>
              {checkContrast.data.suggested_color && (
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Suggested:</span>
                  <div 
                    className="w-6 h-6 rounded border"
                    style={{ backgroundColor: checkContrast.data.suggested_color }}
                  />
                  <span className="font-mono text-xs">{checkContrast.data.suggested_color}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function AccessibilityAuditPanel({ projectId }: AccessibilityAuditProps) {
  const [targetLevel, setTargetLevel] = useState<'A' | 'AA' | 'AAA'>('AA');
  const [selectedIssues, setSelectedIssues] = useState<Set<string>>(new Set());
  
  const { data: audit, isLoading, refetch } = useAccessibilityAudit(projectId, { targetLevel });
  const applyFixes = useApplyAccessibilityFixes();

  const handleSelectIssue = (issueId: string, checked: boolean) => {
    const newSelected = new Set(selectedIssues);
    if (checked) {
      newSelected.add(issueId);
    } else {
      newSelected.delete(issueId);
    }
    setSelectedIssues(newSelected);
  };

  const handleSelectAllFixable = () => {
    if (!audit) return;
    const fixableIds = audit.issues.filter(i => i.auto_fixable).map(i => i.id);
    setSelectedIssues(new Set(fixableIds));
  };

  const handleApplyFixes = async (applyAll = false) => {
    await applyFixes.mutateAsync({
      projectId,
      applyAll,
      issueIds: Array.from(selectedIssues),
    });
    setSelectedIssues(new Set());
    refetch();
  };

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (!audit) {
    return (
      <Alert>
        <AlertDescription>Unable to load accessibility audit.</AlertDescription>
      </Alert>
    );
  }

  const groupedIssues = audit.issues.reduce((acc, issue) => {
    if (!acc[issue.category]) acc[issue.category] = [];
    acc[issue.category].push(issue);
    return acc;
  }, {} as Record<string, AccessibilityIssue[]>);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Accessibility className="h-6 w-6" />
          <h2 className="text-xl font-semibold">Accessibility Audit</h2>
        </div>
        <div className="flex items-center gap-2">
          <select 
            value={targetLevel}
            onChange={(e) => setTargetLevel(e.target.value as 'A' | 'AA' | 'AAA')}
            className="border rounded px-3 py-1.5 text-sm"
          >
            <option value="A">WCAG A</option>
            <option value="AA">WCAG AA</option>
            <option value="AAA">WCAG AAA</option>
          </select>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Re-run Audit
          </Button>
        </div>
      </div>

      {/* Score Card */}
      <Card>
        <CardContent className="py-6">
          <div className="flex items-center justify-around">
            <ScoreGauge score={audit.score} />
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Level Achieved:</span>
                <Badge variant={audit.level_achieved ? 'default' : 'destructive'}>
                  {audit.level_achieved || 'None'}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Target Level:</span>
                <Badge variant="outline">{audit.target_level}</Badge>
              </div>
            </div>
            
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span>{audit.issues_by_severity.error} Errors</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                <span>{audit.issues_by_severity.warning} Warnings</span>
              </div>
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-blue-500" />
                <span>{audit.issues_by_severity.suggestion} Suggestions</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Auto-fix Actions */}
      {audit.auto_fixable_count > 0 && (
        <Alert className="border-green-200 bg-green-50">
          <Wand2 className="h-4 w-4 text-green-600" />
          <AlertTitle className="text-green-800">Auto-fix Available</AlertTitle>
          <AlertDescription className="text-green-700">
            {audit.auto_fixable_count} issues can be automatically fixed.
            <div className="flex gap-2 mt-2">
              <Button 
                size="sm" 
                variant="outline"
                onClick={handleSelectAllFixable}
              >
                Select All Fixable
              </Button>
              <Button 
                size="sm"
                onClick={() => handleApplyFixes(true)}
                disabled={applyFixes.isPending}
              >
                <Wand2 className="h-4 w-4 mr-2" />
                Fix All ({audit.auto_fixable_count})
              </Button>
              {selectedIssues.size > 0 && (
                <Button 
                  size="sm"
                  variant="secondary"
                  onClick={() => handleApplyFixes(false)}
                  disabled={applyFixes.isPending}
                >
                  Fix Selected ({selectedIssues.size})
                </Button>
              )}
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Tabs */}
      <Tabs defaultValue="issues">
        <TabsList>
          <TabsTrigger value="issues">Issues ({audit.total_issues})</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="tools">Tools</TabsTrigger>
        </TabsList>

        <TabsContent value="issues" className="space-y-4 mt-4">
          {audit.total_issues === 0 ? (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertTitle className="text-green-800">All Clear!</AlertTitle>
              <AlertDescription className="text-green-700">
                No accessibility issues found at WCAG {audit.target_level} level.
              </AlertDescription>
            </Alert>
          ) : (
            <Accordion type="multiple" className="space-y-2">
              {Object.entries(groupedIssues).map(([category, issues]) => (
                <AccordionItem key={category} value={category} className="border rounded-lg px-4">
                  <AccordionTrigger className="hover:no-underline">
                    <div className="flex items-center gap-2">
                      {categoryIcons[category] || <AlertCircle className="h-4 w-4" />}
                      <span className="capitalize">{category.replace(/_/g, ' ')}</span>
                      <Badge variant="secondary">{issues.length}</Badge>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="space-y-3 pt-2">
                    {issues.map((issue) => (
                      <IssueCard 
                        key={issue.id} 
                        issue={issue}
                        selected={selectedIssues.has(issue.id)}
                        onSelect={(checked) => handleSelectIssue(issue.id, checked)}
                      />
                    ))}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4 mt-4">
          {audit.recommendations.map((rec, index) => (
            <Alert key={index} variant={rec.priority === 'high' ? 'destructive' : 'default'}>
              <AlertTitle>{rec.title}</AlertTitle>
              <AlertDescription>{rec.description}</AlertDescription>
            </Alert>
          ))}
        </TabsContent>

        <TabsContent value="tools" className="mt-4">
          <ContrastChecker />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default AccessibilityAuditPanel;

'use client';

/* eslint-disable jsx-a11y/alt-text */

import React from 'react';
import { useCurrentQuota, useUsageSummary, useQuotaDashboard } from '@/hooks/use-new-features';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Zap, 
  Image, 
  DollarSign, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react';

interface QuotaRecommendation {
  title: string;
  description: string;
  type: 'info' | 'warning' | 'success';
  action?: string;
}

interface QuotaDashboardData {
  recommendations?: QuotaRecommendation[];
  // Add other fields as needed
}

interface QuotaGaugeProps {
  label: string;
  used: number;
  limit: number;
  icon: React.ReactNode;
  format?: 'number' | 'currency' | 'tokens';
}

function ResetTimer({ resetDate }: { resetDate: Date }) {
  const [daysRemaining, setDaysRemaining] = React.useState(0);

  React.useEffect(() => {
    const calculateDays = () => {
      const days = Math.ceil((resetDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      setDaysRemaining(days);
    };
    
    calculateDays();
    const interval = setInterval(calculateDays, 1000 * 60 * 60); // Update every hour
    
    return () => clearInterval(interval);
  }, [resetDate]);

  return (
    <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
      <Clock className="h-4 w-4" />
      <span>
        Quota resets in {daysRemaining} days
      </span>
    </div>
  );
}

function QuotaGauge({ label, used, limit, icon, format = 'number' }: QuotaGaugeProps) {
  const isUnlimited = limit === -1;
  const percentage = isUnlimited ? 0 : Math.min((used / limit) * 100, 100);
  const isWarning = percentage >= 75;
  const isCritical = percentage >= 90;

  const formatValue = (value: number) => {
    switch (format) {
      case 'currency':
        return `$${value.toFixed(2)}`;
      case 'tokens':
        return value >= 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
      default:
        return value.toString();
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {icon}
          <span className="text-sm font-medium">{label}</span>
        </div>
        <span className="text-sm text-muted-foreground">
          {formatValue(used)} / {isUnlimited ? '∞' : formatValue(limit)}
        </span>
      </div>
      {!isUnlimited && (
        <Progress 
          value={percentage} 
          className={`h-2 ${isCritical ? 'bg-red-100' : isWarning ? 'bg-yellow-100' : ''}`}
        />
      )}
      {isCritical && (
        <p className="text-xs text-red-600">Limit almost reached!</p>
      )}
    </div>
  );
}

export function QuotaDashboard() {
  const { data: quota, isLoading: quotaLoading } = useCurrentQuota();
  const { data: summary } = useUsageSummary('month');
  const { data: dashboard } = useQuotaDashboard() as { data: QuotaDashboardData | undefined };

  if (quotaLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-32 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (!quota) {
    return (
      <Alert>
        <AlertDescription>Unable to load quota information.</AlertDescription>
      </Alert>
    );
  }

  const resetDate = new Date(quota.period_end);

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      {quota.is_request_limit_reached || quota.is_budget_exceeded ? (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            {quota.is_request_limit_reached && 'You have reached your AI request limit. '}
            {quota.is_budget_exceeded && 'You have exceeded your AI budget. '}
            <a href="/pricing" className="underline">Upgrade your plan</a> to continue.
          </AlertDescription>
        </Alert>
      ) : (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            Your AI quota is in good standing. Resets on {resetDate.toLocaleDateString()}.
          </AlertDescription>
        </Alert>
      )}

      {/* Main Quota Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>AI Usage This Month</CardTitle>
              <CardDescription>
                Period: {new Date(quota.period_start).toLocaleDateString()} - {resetDate.toLocaleDateString()}
              </CardDescription>
            </div>
            <Badge variant={quota.success_rate >= 90 ? 'default' : 'secondary'}>
              {quota.success_rate.toFixed(1)}% Success Rate
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <QuotaGauge
            label="AI Requests"
            used={quota.ai_requests_used}
            limit={quota.ai_requests_limit}
            icon={<Zap className="h-4 w-4 text-yellow-500" />}
          />
          
          <QuotaGauge
            label="Tokens Used"
            used={quota.ai_tokens_used}
            limit={quota.ai_tokens_limit}
            icon={<TrendingUp className="h-4 w-4 text-blue-500" />}
            format="tokens"
          />
          
          { }
          { }
          { }
          <QuotaGauge
            label="Image Generations"
            used={quota.image_generations_used}
            limit={quota.image_generations_limit}
            icon={<Image className="h-4 w-4 text-purple-500" aria-hidden="true" />}
          />
          
          <QuotaGauge
            label="Budget Spent"
            used={parseFloat(quota.total_cost)}
            limit={parseFloat(quota.budget_limit)}
            icon={<DollarSign className="h-4 w-4 text-green-500" />}
            format="currency"
          />
        </CardContent>
      </Card>

      {/* Usage Breakdown */}
      {summary && Object.keys(summary.by_type).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Usage by Type</CardTitle>
            <CardDescription>Breakdown of AI usage by request type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(summary.by_type).map(([type, data]) => (
                <div key={type} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="font-medium capitalize">{type.replace(/_/g, ' ')}</p>
                    <p className="text-sm text-muted-foreground">
                      {data.count} requests • {data.success_rate.toFixed(0)}% success
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">${data.cost.toFixed(2)}</p>
                    <p className="text-sm text-muted-foreground">{data.tokens.toLocaleString()} tokens</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {dashboard?.recommendations && dashboard.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {dashboard.recommendations.map((rec, index: number) => (
                <Alert key={index} variant={rec.type === 'warning' ? 'destructive' : 'default'}>
                  <AlertDescription>
                    <strong>{rec.title}</strong>
                    <p className="text-sm mt-1">{rec.description}</p>
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reset Timer */}
      <ResetTimer resetDate={resetDate} />
    </div>
  );
}

export default QuotaDashboard;

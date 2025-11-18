'use client';

import { useState, useEffect, useCallback } from 'react';
import { subscriptionsApi, couponsApi, Subscription, SubscriptionUsage, SubscriptionTier, Coupon } from '@/lib/subscription-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/use-toast';
import { 
  CreditCard, 
  Tag, 
  TrendingUp, 
  Check,
  Zap
} from 'lucide-react';

export default function SubscriptionPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [usage, setUsage] = useState<SubscriptionUsage | null>(null);
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [couponCode, setCouponCode] = useState('');
  const [validatingCoupon, setValidatingCoupon] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Load subscription data
  const loadSubscription = useCallback(async () => {
    try {
      setLoading(true);
      const [subResponse, usageResponse, tiersResponse] = await Promise.all([
        subscriptionsApi.current(),
        subscriptionsApi.usage(),
        subscriptionsApi.tiers(),
      ]);
      setSubscription(subResponse.data);
      setUsage(usageResponse.data);
      setTiers(tiersResponse.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load subscription data',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  // Load available coupons
  const loadCoupons = useCallback(async () => {
    try {
      const response = await couponsApi.list();
      setCoupons(response.data);
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to load coupons',
        variant: 'destructive',
      });
    }
  }, [toast]);

  useEffect(() => {
    loadSubscription();
    loadCoupons();
  }, [loadSubscription, loadCoupons]);

  // Validate coupon
  const handleValidateCoupon = async () => {
    if (!couponCode.trim()) return;
    
    try {
      setValidatingCoupon(true);
      const response = await couponsApi.validate(couponCode);
      if (response.data.valid) {
        toast({
          title: 'Valid Coupon',
          description: `You'll save ${response.data.discount_amount}!`,
        });
      } else {
        toast({
          title: 'Invalid Coupon',
          description: response.data.error || 'Coupon is not valid',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to validate coupon',
        variant: 'destructive',
      });
    } finally {
      setValidatingCoupon(false);
    }
  };

  // Subscribe to tier
  const handleSubscribe = async (tier: string) => {
    try {
      await subscriptionsApi.create({ tier, coupon_code: couponCode || undefined });
      toast({
        title: 'Success',
        description: 'Subscription created successfully',
      });
      loadSubscription();
      setCouponCode('');
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to create subscription',
        variant: 'destructive',
      });
    }
  };

  // Cancel subscription
  const handleCancelSubscription = async () => {
    try {
      await subscriptionsApi.cancel();
      toast({
        title: 'Success',
        description: 'Subscription cancelled',
      });
      loadSubscription();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to cancel subscription',
        variant: 'destructive',
      });
    }
  };

  // Resume subscription
  const handleResumeSubscription = async () => {
    try {
      await subscriptionsApi.resume();
      toast({
        title: 'Success',
        description: 'Subscription resumed',
      });
      loadSubscription();
    } catch (error) {
      console.error(error);
      toast({
        title: 'Error',
        description: 'Failed to resume subscription',
        variant: 'destructive',
      });
    }
  };

  // Get usage percentage
  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Subscription</h1>
        <p className="text-muted-foreground">Manage your subscription and billing</p>
      </div>

      <Tabs defaultValue="current" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="current">
            <CreditCard className="w-4 h-4 mr-2" />
            Current Plan
          </TabsTrigger>
          <TabsTrigger value="plans">
            <TrendingUp className="w-4 h-4 mr-2" />
            Available Plans
          </TabsTrigger>
          <TabsTrigger value="coupons">
            <Tag className="w-4 h-4 mr-2" />
            Coupons
          </TabsTrigger>
        </TabsList>

        <TabsContent value="current" className="space-y-4">
          {loading ? (
            <Card>
              <CardContent className="pt-6">
                <p>Loading subscription...</p>
              </CardContent>
            </Card>
          ) : subscription ? (
            <>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="capitalize">{subscription.tier} Plan</CardTitle>
                      <CardDescription>
                        Status: <Badge variant={subscription.status === 'active' ? 'default' : 'secondary'}>
                          {subscription.status}
                        </Badge>
                      </CardDescription>
                    </div>
                    {subscription.cancel_at_period_end ? (
                      <Button onClick={handleResumeSubscription}>Resume</Button>
                    ) : (
                      <Button variant="destructive" onClick={handleCancelSubscription}>
                        Cancel Subscription
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Current Period:</span>
                      <span>
                        {new Date(subscription.current_period_start).toLocaleDateString()} -{' '}
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </span>
                    </div>
                    {subscription.cancel_at_period_end && (
                      <p className="text-sm text-destructive">
                        Your subscription will be cancelled at the end of the current period.
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {usage && (
                <Card>
                  <CardHeader>
                    <CardTitle>Usage Statistics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Projects</span>
                        <span>{usage.projects_used} / {usage.projects_limit === -1 ? '∞' : usage.projects_limit}</span>
                      </div>
                      <Progress value={getUsagePercentage(usage.projects_used, usage.projects_limit)} />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Storage</span>
                        <span>{(usage.storage_used / 1024 / 1024).toFixed(2)} MB / {usage.storage_limit === -1 ? '∞' : `${usage.storage_limit} MB`}</span>
                      </div>
                      <Progress value={getUsagePercentage(usage.storage_used, usage.storage_limit * 1024 * 1024)} />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>AI Requests</span>
                        <span>{usage.ai_requests_used} / {usage.ai_requests_limit === -1 ? '∞' : usage.ai_requests_limit}</span>
                      </div>
                      <Progress value={getUsagePercentage(usage.ai_requests_used, usage.ai_requests_limit)} />
                    </div>

                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Team Members</span>
                        <span>{usage.team_members_used} / {usage.team_members_limit === -1 ? '∞' : usage.team_members_limit}</span>
                      </div>
                      <Progress value={getUsagePercentage(usage.team_members_used, usage.team_members_limit)} />
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <Card>
              <CardContent className="pt-6">
                <p className="text-muted-foreground">No active subscription</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="plans" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {tiers.map((tier) => (
              <Card key={tier.name} className={tier.name === 'pro' ? 'border-primary' : ''}>
                <CardHeader>
                  <CardTitle className="capitalize">{tier.name}</CardTitle>
                  <CardDescription>
                    <span className="text-3xl font-bold">${tier.price}</span> / month
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{tier.projects_limit === -1 ? 'Unlimited' : tier.projects_limit} projects</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{tier.storage_limit === -1 ? 'Unlimited' : `${tier.storage_limit} MB`} storage</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{tier.ai_requests_limit === -1 ? 'Unlimited' : tier.ai_requests_limit} AI requests</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-green-500" />
                      <span className="text-sm">{tier.team_members_limit === -1 ? 'Unlimited' : tier.team_members_limit} team members</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    {tier.features.map((feature, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <Zap className="w-3 h-3 text-yellow-500" />
                        <span className="text-xs">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button 
                    className="w-full"
                    disabled={subscription?.tier === tier.name}
                    onClick={() => handleSubscribe(tier.name)}
                  >
                    {subscription?.tier === tier.name ? 'Current Plan' : 'Subscribe'}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="coupons" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Apply Coupon</CardTitle>
              <CardDescription>Enter a coupon code to get a discount</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter coupon code"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                />
                <Button onClick={handleValidateCoupon} disabled={validatingCoupon}>
                  {validatingCoupon ? 'Validating...' : 'Validate'}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Available Coupons</CardTitle>
            </CardHeader>
            <CardContent>
              {coupons.length === 0 ? (
                <p className="text-muted-foreground">No coupons available</p>
              ) : (
                <div className="space-y-2">
                  {coupons.map((coupon) => (
                    <Card key={coupon.id}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold">{coupon.code}</p>
                            <p className="text-sm text-muted-foreground">
                              {coupon.discount_type === 'percentage' 
                                ? `${coupon.discount_value}% off`
                                : `$${coupon.discount_value} off`
                              }
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Valid until {new Date(coupon.valid_until || '').toLocaleDateString()}
                            </p>
                          </div>
                          <Badge variant={coupon.is_active ? 'default' : 'secondary'}>
                            {coupon.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

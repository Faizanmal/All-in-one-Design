'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Check, 
  Crown, 
  Zap, 
  Shield, 
  Sparkles, 
  Users, 
  Globe,
  Lock,
  TrendingUp
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';

const tiers = [
  {
    name: 'Free',
    slug: 'free',
    icon: Sparkles,
    price: { monthly: 0, yearly: 0 },
    description: 'Perfect for trying out our platform',
    popular: false,
    features: [
      { text: '3 Projects', included: true },
      { text: '10 AI Requests/month', included: true },
      { text: '100 MB Storage', included: true },
      { text: '10 Exports/month', included: true },
      { text: 'Basic Templates', included: true },
      { text: 'Community Support', included: true },
      { text: 'Advanced AI', included: false },
      { text: 'Priority Support', included: false },
      { text: 'Custom Branding', included: false },
      { text: 'API Access', included: false }
    ],
    color: 'from-gray-500 to-gray-600'
  },
  {
    name: 'Pro',
    slug: 'pro',
    icon: Zap,
    price: { monthly: 29.99, yearly: 299.99 },
    description: 'For professional designers and small teams',
    popular: true,
    features: [
      { text: '50 Projects', included: true },
      { text: '500 AI Requests/month', included: true },
      { text: '10 GB Storage', included: true },
      { text: '1,000 Exports/month', included: true },
      { text: 'All Templates', included: true },
      { text: '5 Collaborators/project', included: true },
      { text: 'Advanced AI Features', included: true },
      { text: 'Priority Support', included: true },
      { text: 'Custom Branding', included: true },
      { text: 'API Access', included: true },
      { text: 'Version History', included: true },
      { text: 'Advanced Export Options', included: true }
    ],
    color: 'from-purple-500 to-pink-500'
  },
  {
    name: 'Enterprise',
    slug: 'enterprise',
    icon: Crown,
    price: { monthly: 99.99, yearly: 999.99 },
    description: 'For large teams and organizations',
    popular: false,
    features: [
      { text: 'Unlimited Projects', included: true },
      { text: 'Unlimited AI Requests', included: true },
      { text: 'Unlimited Storage', included: true },
      { text: 'Unlimited Exports', included: true },
      { text: 'All Templates + Custom', included: true },
      { text: 'Unlimited Collaborators', included: true },
      { text: 'Advanced AI + Priority Queue', included: true },
      { text: 'Dedicated Support', included: true },
      { text: 'White Labeling', included: true },
      { text: 'Full API Access', included: true },
      { text: 'Complete Version History', included: true },
      { text: 'Advanced Export + Automation', included: true },
      { text: 'SSO Integration', included: true },
      { text: 'Audit Logs', included: true },
      { text: 'Custom SLA', included: true }
    ],
    color: 'from-yellow-500 to-orange-500'
  }
];

const usageStats = {
  projects: { used: 12, limit: 50, percentage: 24, unit: '' },
  aiRequests: { used: 234, limit: 500, percentage: 47, unit: '' },
  storage: { used: 2.4, limit: 10, percentage: 24, unit: 'GB' },
  exports: { used: 145, limit: 1000, percentage: 14.5, unit: '' }
};

export default function SubscriptionPage() {
  const [isYearly, setIsYearly] = useState(false);
  const currentPlan = 'pro';

  return (
    <div className="min-h-screen bg-linear-to-br from-background via-background to-primary/5">
      <div className="container mx-auto p-6 space-y-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-4"
        >
          <h1 className="text-5xl font-bold bg-linear-to-r from-primary via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Choose Your Plan
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Unlock the full potential of AI-powered design. Upgrade anytime.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 pt-4">
            <span className={`text-sm font-medium ${!isYearly ? 'text-primary' : 'text-muted-foreground'}`}>
              Monthly
            </span>
            <Switch
              checked={isYearly}
              onCheckedChange={setIsYearly}
              className="data-[state=checked]:bg-primary"
            />
            <span className={`text-sm font-medium ${isYearly ? 'text-primary' : 'text-muted-foreground'}`}>
              Yearly
            </span>
            {isYearly && (
              <Badge variant="secondary" className="bg-green-500/20 text-green-500 border-green-500/50">
                Save 20%
              </Badge>
            )}
          </div>
        </motion.div>

        {/* Current Usage Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-linear-to-br from-primary/10 to-purple-500/10 border-2 border-primary/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Current Usage - Pro Plan
              </CardTitle>
              <CardDescription>Your monthly usage statistics</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {Object.entries(usageStats).map(([key, stat]) => (
                <div key={key} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                    <span className="text-sm text-muted-foreground">
                      {stat.used}{stat.unit || ''} / {stat.limit}{stat.unit || ''}
                    </span>
                  </div>
                  <Progress value={stat.percentage} className="h-2" />
                  <span className="text-xs text-muted-foreground">{stat.percentage.toFixed(1)}% used</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>

        {/* Pricing Cards */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid gap-8 md:grid-cols-2 lg:grid-cols-3"
        >
          {tiers.map((tier, index) => {
            const Icon = tier.icon;
            const monthlyPrice = isYearly ? (tier.price.yearly / 12).toFixed(2) : tier.price.monthly;
            const isCurrentPlan = tier.slug === currentPlan;

            return (
              <motion.div
                key={tier.slug}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
                className={`relative ${tier.popular ? 'md:-mt-4 md:mb-4' : ''}`}
              >
                {tier.popular && (
                  <div className="absolute -top-5 left-0 right-0 flex justify-center">
                    <Badge className="bg-linear-to-r from-purple-500 to-pink-500 text-white px-4 py-1">
                      Most Popular
                    </Badge>
                  </div>
                )}
                
                <Card className={`relative overflow-hidden h-full border-2 transition-all duration-300 hover:shadow-2xl hover:scale-105 ${
                  tier.popular 
                    ? 'border-primary shadow-lg shadow-primary/20' 
                    : isCurrentPlan
                    ? 'border-green-500 shadow-lg shadow-green-500/20'
                    : 'hover:border-primary/50'
                }`}>
                  {/* Gradient Background */}
                  <div className={`absolute inset-0 bg-linear-to-br ${tier.color} opacity-5`} />
                  
                  <CardHeader className="relative">
                    <div className="flex items-center justify-between">
                      <div className={`p-3 rounded-xl bg-linear-to-br ${tier.color}`}>
                        <Icon className="h-6 w-6 text-white" />
                      </div>
                      {isCurrentPlan && (
                        <Badge variant="secondary" className="bg-green-500/20 text-green-500 border-green-500/50">
                          Current Plan
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-2xl">{tier.name}</CardTitle>
                    <CardDescription>{tier.description}</CardDescription>
                  </CardHeader>

                  <CardContent className="relative space-y-6">
                    {/* Price */}
                    <div className="space-y-1">
                      <div className="flex items-baseline gap-1">
                        <span className="text-4xl font-bold bg-linear-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                          ${monthlyPrice}
                        </span>
                        <span className="text-muted-foreground">/month</span>
                      </div>
                      {isYearly && tier.price.yearly > 0 && (
                        <p className="text-sm text-muted-foreground">
                          Billed ${tier.price.yearly}/year
                        </p>
                      )}
                    </div>

                    {/* Features */}
                    <ul className="space-y-3">
                      {tier.features.map((feature, i) => (
                        <motion.li
                          key={i}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.05 * i }}
                          className="flex items-start gap-3"
                        >
                          <div className={`mt-1 rounded-full p-1 ${
                            feature.included 
                              ? 'bg-green-500/20 text-green-500' 
                              : 'bg-muted text-muted-foreground'
                          }`}>
                            <Check className="h-3 w-3" />
                          </div>
                          <span className={`text-sm ${!feature.included && 'text-muted-foreground line-through'}`}>
                            {feature.text}
                          </span>
                        </motion.li>
                      ))}
                    </ul>
                  </CardContent>

                  <CardFooter className="relative">
                    <Button 
                      className={`w-full ${tier.popular ? 'bg-linear-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600' : ''}`}
                      variant={tier.popular ? 'default' : 'outline'}
                      size="lg"
                      disabled={isCurrentPlan}
                    >
                      {isCurrentPlan ? 'Current Plan' : tier.price.monthly === 0 ? 'Get Started' : 'Upgrade Now'}
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Enterprise Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-linear-to-br from-yellow-500/10 to-orange-500/10 border-2 border-yellow-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Crown className="h-6 w-6 text-yellow-500" />
                Enterprise Features
              </CardTitle>
              <CardDescription>
                Additional benefits for large teams and organizations
              </CardDescription>
            </CardHeader>
            <CardContent className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[
                { icon: Users, title: 'Team Management', desc: 'Advanced user roles and permissions' },
                { icon: Shield, title: 'Security', desc: 'SSO, 2FA, and audit logs' },
                { icon: Globe, title: 'Global CDN', desc: 'Lightning-fast asset delivery' },
                { icon: Lock, title: 'Compliance', desc: 'GDPR, SOC 2, and HIPAA ready' }
              ].map((feature, i) => {
                const Icon = feature.icon;
                return (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 * i }}
                    className="flex flex-col items-center text-center space-y-2 p-4 rounded-lg bg-background/50 hover:bg-background/80 transition-colors"
                  >
                    <div className="p-3 rounded-xl bg-linear-to-br from-yellow-500 to-orange-500">
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">{feature.desc}</p>
                  </motion.div>
                );
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="max-w-3xl mx-auto"
        >
          <Card>
            <CardHeader>
              <CardTitle>Frequently Asked Questions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { q: 'Can I change plans anytime?', a: 'Yes, upgrade or downgrade your plan at any time. Changes take effect immediately.' },
                { q: 'What happens if I exceed my limits?', a: 'You\'ll be notified when approaching limits. Upgrade anytime or wait for the next billing cycle.' },
                { q: 'Is there a free trial?', a: 'Yes! Start with our Free plan and upgrade when you\'re ready. No credit card required.' },
                { q: 'Do you offer refunds?', a: 'Yes, we offer a 30-day money-back guarantee on all paid plans.' }
              ].map((faq, i) => (
                <div key={i} className="p-4 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors">
                  <h4 className="font-semibold mb-2">{faq.q}</h4>
                  <p className="text-sm text-muted-foreground">{faq.a}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}

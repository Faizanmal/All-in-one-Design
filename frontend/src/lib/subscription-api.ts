// API service for subscription and coupon management
import api from './api';

// Subscription Types
export interface Subscription {
  id: number;
  user: number;
  tier: 'free' | 'pro' | 'enterprise';
  status: 'active' | 'cancelled' | 'expired' | 'past_due';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  stripe_subscription_id?: string;
  stripe_customer_id?: string;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionUsage {
  projects_used: number;
  projects_limit: number;
  storage_used: number;
  storage_limit: number;
  ai_requests_used: number;
  ai_requests_limit: number;
  team_members_used: number;
  team_members_limit: number;
}

export interface SubscriptionTier {
  name: string;
  price: number;
  projects_limit: number;
  storage_limit: number;
  ai_requests_limit: number;
  team_members_limit: number;
  features: string[];
}

// Coupon Types
export interface Coupon {
  id: number;
  code: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  valid_from: string;
  valid_until?: string;
  max_uses?: number;
  times_used: number;
  max_uses_per_user?: number;
  tier_restrictions?: string[];
  is_active: boolean;
  created_at: string;
}

export interface CouponUsage {
  id: number;
  coupon: number;
  user: number;
  subscription?: number;
  discount_applied: number;
  used_at: string;
}

export interface CouponValidationResponse {
  valid: boolean;
  coupon?: Coupon;
  discount_amount?: number;
  error?: string;
}

// Subscriptions API
export const subscriptionsApi = {
  // Get current subscription
  current: () => api.get<Subscription>('/v1/subscriptions/current/'),
  
  // Get subscription usage
  usage: () => api.get<SubscriptionUsage>('/v1/subscriptions/usage/'),
  
  // Get available tiers
  tiers: () => api.get<SubscriptionTier[]>('/v1/subscriptions/tiers/'),
  
  // Create subscription
  create: (data: { tier: string; payment_method_id?: string; coupon_code?: string }) => 
    api.post<Subscription>('/v1/subscriptions/subscribe/', data),
  
  // Update subscription
  update: (data: { tier: string }) => 
    api.patch<Subscription>('/v1/subscriptions/update/', data),
  
  // Cancel subscription
  cancel: (immediate?: boolean) => 
    api.post('/v1/subscriptions/cancel/', { immediate }),
  
  // Resume subscription
  resume: () => api.post('/v1/subscriptions/resume/'),
  
  // Get billing history
  billingHistory: () => api.get('/v1/subscriptions/billing-history/'),
};

// Coupons API
export const couponsApi = {
  // List available coupons
  list: () => api.get<Coupon[]>('/v1/subscriptions/coupons/'),
  
  // Validate coupon
  validate: (code: string, tier?: string) => {
    const params = new URLSearchParams({ code });
    if (tier) params.append('tier', tier);
    return api.post<CouponValidationResponse>(`/v1/subscriptions/coupons/validate/?${params.toString()}`);
  },
  
  // Apply coupon (for admins)
  create: (data: {
    code: string;
    discount_type: 'percentage' | 'fixed';
    discount_value: number;
    valid_from: string;
    valid_until?: string;
    max_uses?: number;
    max_uses_per_user?: number;
    tier_restrictions?: string[];
  }) => api.post<Coupon>('/v1/subscriptions/coupons/', data),
  
  // Get coupon details
  get: (couponId: number) => api.get<Coupon>(`/v1/subscriptions/coupons/${couponId}/`),
  
  // Update coupon
  update: (couponId: number, data: Partial<Coupon>) => 
    api.patch<Coupon>(`/v1/subscriptions/coupons/${couponId}/`, data),
  
  // Delete coupon
  delete: (couponId: number) => api.delete(`/v1/subscriptions/coupons/${couponId}/`),
  
  // Get coupon usage history
  usageHistory: (couponId: number) => 
    api.get<CouponUsage[]>(`/v1/subscriptions/coupons/${couponId}/usage/`),
};

const subscriptionApi = {
  subscriptions: subscriptionsApi,
  coupons: couponsApi,
};

export default subscriptionApi;

// API service for template marketplace
import api from './api';

// Template Category Types
export interface TemplateCategory {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon?: string;
  parent?: number;
  template_count: number;
  created_at: string;
}

// Template Types
export interface MarketplaceTemplate {
  id: number;
  name: string;
  slug: string;
  description: string;
  thumbnail: string;
  preview_images: string[];
  category: TemplateCategory;
  creator: CreatorProfile;
  price: number;
  is_free: boolean;
  license_type: 'free' | 'personal' | 'commercial' | 'extended';
  tags: string[];
  file_format: 'figma' | 'sketch' | 'xd' | 'ai' | 'psd' | 'other';
  file_size: number;
  rating: number;
  review_count: number;
  download_count: number;
  is_featured: boolean;
  is_new: boolean;
  created_at: string;
  updated_at: string;
}

// Creator Profile Types
export interface CreatorProfile {
  id: number;
  user: {
    id: number;
    username: string;
    avatar?: string;
  };
  display_name: string;
  bio?: string;
  portfolio_url?: string;
  social_links?: {
    dribbble?: string;
    behance?: string;
    twitter?: string;
    instagram?: string;
  };
  is_verified: boolean;
  total_sales: number;
  total_templates: number;
  rating: number;
  joined_at: string;
}

// Template Review Types
export interface TemplateReview {
  id: number;
  template: number;
  user: {
    id: number;
    username: string;
    avatar?: string;
  };
  rating: number;
  title: string;
  content: string;
  is_verified_purchase: boolean;
  helpful_count: number;
  created_at: string;
}

// Template Purchase Types
export interface TemplatePurchase {
  id: number;
  template: MarketplaceTemplate;
  user: number;
  amount_paid: number;
  license_type: string;
  download_url: string;
  downloaded_at?: string;
  purchased_at: string;
}

// Collection Types
export interface TemplateCollection {
  id: number;
  name: string;
  description: string;
  cover_image?: string;
  templates: MarketplaceTemplate[];
  is_public: boolean;
  created_by: {
    id: number;
    username: string;
  };
  created_at: string;
}

// Template Categories API
export const templateCategoriesApi = {
  list: () =>
    api.get<TemplateCategory[]>('/v1/template-marketplace/categories/'),

  get: (categoryId: number) =>
    api.get<TemplateCategory>(`/v1/template-marketplace/categories/${categoryId}/`),

  getTemplates: (categoryId: number, params?: { page?: number; page_size?: number }) =>
    api.get<{ results: MarketplaceTemplate[]; count: number }>(
      `/v1/template-marketplace/categories/${categoryId}/templates/`,
      { params }
    ),
};

// Marketplace Templates API
export const marketplaceTemplatesApi = {
  list: (params?: {
    category?: number;
    search?: string;
    is_free?: boolean;
    license_type?: string;
    file_format?: string;
    min_price?: number;
    max_price?: number;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) =>
    api.get<{ results: MarketplaceTemplate[]; count: number; next?: string; previous?: string }>(
      '/v1/template-marketplace/templates/',
      { params }
    ),

  get: (templateId: number) =>
    api.get<MarketplaceTemplate>(`/v1/template-marketplace/templates/${templateId}/`),

  getFeatured: () =>
    api.get<MarketplaceTemplate[]>('/v1/template-marketplace/templates/featured/'),

  getNew: () =>
    api.get<MarketplaceTemplate[]>('/v1/template-marketplace/templates/new/'),

  getPopular: () =>
    api.get<MarketplaceTemplate[]>('/v1/template-marketplace/templates/popular/'),

  getSimilar: (templateId: number) =>
    api.get<MarketplaceTemplate[]>(`/v1/template-marketplace/templates/${templateId}/similar/`),

  purchase: (templateId: number, licenseType: string) =>
    api.post<TemplatePurchase>(`/v1/template-marketplace/templates/${templateId}/purchase/`, {
      license_type: licenseType
    }),

  download: (templateId: number) =>
    api.get(`/v1/template-marketplace/templates/${templateId}/download/`, {
      responseType: 'blob'
    }),

  addToFavorites: (templateId: number) =>
    api.post(`/v1/template-marketplace/templates/${templateId}/favorite/`),

  removeFromFavorites: (templateId: number) =>
    api.delete(`/v1/template-marketplace/templates/${templateId}/favorite/`),
};

// Template Reviews API
export const templateReviewsApi = {
  list: (templateId: number) =>
    api.get<TemplateReview[]>(`/v1/template-marketplace/templates/${templateId}/reviews/`),

  create: (templateId: number, data: { rating: number; title: string; content: string }) =>
    api.post<TemplateReview>(`/v1/template-marketplace/templates/${templateId}/reviews/`, data),

  update: (templateId: number, reviewId: number, data: Partial<TemplateReview>) =>
    api.patch<TemplateReview>(
      `/v1/template-marketplace/templates/${templateId}/reviews/${reviewId}/`,
      data
    ),

  delete: (templateId: number, reviewId: number) =>
    api.delete(`/v1/template-marketplace/templates/${templateId}/reviews/${reviewId}/`),

  markHelpful: (templateId: number, reviewId: number) =>
    api.post(`/v1/template-marketplace/templates/${templateId}/reviews/${reviewId}/helpful/`),
};

// Creator Profiles API
export const creatorProfilesApi = {
  list: (params?: { search?: string; ordering?: string }) =>
    api.get<CreatorProfile[]>('/v1/template-marketplace/creators/', { params }),

  get: (creatorId: number) =>
    api.get<CreatorProfile>(`/v1/template-marketplace/creators/${creatorId}/`),

  getTemplates: (creatorId: number) =>
    api.get<MarketplaceTemplate[]>(`/v1/template-marketplace/creators/${creatorId}/templates/`),

  getMyProfile: () =>
    api.get<CreatorProfile>('/v1/template-marketplace/creators/me/'),

  updateMyProfile: (data: Partial<CreatorProfile>) =>
    api.patch<CreatorProfile>('/v1/template-marketplace/creators/me/', data),

  follow: (creatorId: number) =>
    api.post(`/v1/template-marketplace/creators/${creatorId}/follow/`),

  unfollow: (creatorId: number) =>
    api.delete(`/v1/template-marketplace/creators/${creatorId}/follow/`),
};

// User Purchases API
export const userPurchasesApi = {
  list: () =>
    api.get<TemplatePurchase[]>('/v1/template-marketplace/purchases/'),

  get: (purchaseId: number) =>
    api.get<TemplatePurchase>(`/v1/template-marketplace/purchases/${purchaseId}/`),
};

// User Favorites API
export const userFavoritesApi = {
  list: () =>
    api.get<MarketplaceTemplate[]>('/v1/template-marketplace/favorites/'),
};

// Template Collections API
export const templateCollectionsApi = {
  list: () =>
    api.get<TemplateCollection[]>('/v1/template-marketplace/collections/'),

  get: (collectionId: number) =>
    api.get<TemplateCollection>(`/v1/template-marketplace/collections/${collectionId}/`),

  create: (data: { name: string; description: string; is_public: boolean }) =>
    api.post<TemplateCollection>('/v1/template-marketplace/collections/', data),

  update: (collectionId: number, data: Partial<TemplateCollection>) =>
    api.patch<TemplateCollection>(`/v1/template-marketplace/collections/${collectionId}/`, data),

  delete: (collectionId: number) =>
    api.delete(`/v1/template-marketplace/collections/${collectionId}/`),

  addTemplate: (collectionId: number, templateId: number) =>
    api.post(`/v1/template-marketplace/collections/${collectionId}/add/`, { template_id: templateId }),

  removeTemplate: (collectionId: number, templateId: number) =>
    api.post(`/v1/template-marketplace/collections/${collectionId}/remove/`, { template_id: templateId }),
};

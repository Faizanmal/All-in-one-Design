'use client';

import React, { useState, useEffect, useCallback } from 'react';

interface CreatorStats {
  totalEarnings: number;
  totalSales: number;
  totalDownloads: number;
  averageRating: number;
  pendingPayout: number;
  thisMonthEarnings: number;
  thisMonthSales: number;
}

interface CreatorTemplate {
  id: string;
  name: string;
  status: 'published' | 'draft' | 'pending' | 'rejected';
  price: number;
  isFree: boolean;
  thumbnail: string;
  stats: {
    downloads: number;
    revenue: number;
    rating: number;
    reviews: number;
  };
  created_at: string;
  updated_at: string;
}

interface EarningsData {
  date: string;
  earnings: number;
  sales: number;
}

interface Review {
  id: string;
  template_name: string;
  user_name: string;
  rating: number;
  comment: string;
  created_at: string;
}

type TabType = 'overview' | 'templates' | 'earnings' | 'reviews' | 'settings';

export function CreatorDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [stats, setStats] = useState<CreatorStats | null>(null);
  const [templates, setTemplates] = useState<CreatorTemplate[]>([]);
  const [earningsData, setEarningsData] = useState<EarningsData[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCreatorData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, templatesRes, earningsRes, reviewsRes] = await Promise.all([
        fetch('/api/marketplace/creator/stats/'),
        fetch('/api/marketplace/creator/templates/'),
        fetch('/api/marketplace/creator/earnings/'),
        fetch('/api/marketplace/creator/reviews/'),
      ]);

      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      if (templatesRes.ok) {
        const data = await templatesRes.json();
        setTemplates(data.results || []);
      }
      if (earningsRes.ok) {
        const data = await earningsRes.json();
        setEarningsData(data.results || []);
      }
      if (reviewsRes.ok) {
        const data = await reviewsRes.json();
        setReviews(data.results || []);
      }
    } catch (error) {
      console.error('Failed to fetch creator data:', error);
      // Mock data
      setStats({
        totalEarnings: 12450.75,
        totalSales: 847,
        totalDownloads: 28500,
        averageRating: 4.7,
        pendingPayout: 1250.50,
        thisMonthEarnings: 2340.25,
        thisMonthSales: 156,
      });
      setTemplates([
        {
          id: '1',
          name: 'Social Media Pack Pro',
          status: 'published',
          price: 29.99,
          isFree: false,
          thumbnail: '/templates/social.jpg',
          stats: { downloads: 1542, revenue: 4625.58, rating: 4.8, reviews: 89 },
          created_at: '2024-01-15',
          updated_at: '2024-02-20',
        },
        {
          id: '2',
          name: 'Business Card Bundle',
          status: 'published',
          price: 19.99,
          isFree: false,
          thumbnail: '/templates/cards.jpg',
          stats: { downloads: 892, revenue: 1783.08, rating: 4.6, reviews: 54 },
          created_at: '2024-02-01',
          updated_at: '2024-02-18',
        },
        {
          id: '3',
          name: 'Instagram Story Kit',
          status: 'pending',
          price: 14.99,
          isFree: false,
          thumbnail: '/templates/story.jpg',
          stats: { downloads: 0, revenue: 0, rating: 0, reviews: 0 },
          created_at: '2024-02-25',
          updated_at: '2024-02-25',
        },
      ]);
      setEarningsData([
        { date: '2024-02-01', earnings: 245.50, sales: 12 },
        { date: '2024-02-08', earnings: 312.75, sales: 15 },
        { date: '2024-02-15', earnings: 189.25, sales: 9 },
        { date: '2024-02-22', earnings: 456.80, sales: 22 },
      ]);
      setReviews([
        {
          id: '1',
          template_name: 'Social Media Pack Pro',
          user_name: 'John D.',
          rating: 5,
          comment: 'Amazing templates! Very professional and easy to customize.',
          created_at: '2024-02-20',
        },
        {
          id: '2',
          template_name: 'Business Card Bundle',
          user_name: 'Sarah M.',
          rating: 4,
          comment: 'Great designs, would love to see more variations.',
          created_at: '2024-02-18',
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCreatorData();
  }, [fetchCreatorData]);

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getStatusBadge = (status: CreatorTemplate['status']) => {
    const styles = {
      published: 'bg-green-100 text-green-800',
      draft: 'bg-gray-100 text-gray-800',
      pending: 'bg-yellow-100 text-yellow-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${styles[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const renderStars = (rating: number) => {
    return [...Array(5)].map((_, i) => (
      <span key={i} className={i < rating ? 'text-yellow-400' : 'text-gray-300'}>
        ★
      </span>
    ));
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Earnings</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatCurrency(stats?.totalEarnings || 0)}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💰</span>
            </div>
          </div>
          <p className="text-sm text-green-600 mt-2">
            +{formatCurrency(stats?.thisMonthEarnings || 0)} this month
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Sales</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalSales || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📊</span>
            </div>
          </div>
          <p className="text-sm text-blue-600 mt-2">
            +{stats?.thisMonthSales || 0} this month
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Downloads</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.totalDownloads?.toLocaleString() || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⬇️</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Average Rating</p>
              <p className="text-2xl font-bold text-gray-900">{stats?.averageRating?.toFixed(1) || 0}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⭐</span>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Payout */}
      {(stats?.pendingPayout ?? 0) > 0 && (
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100">Pending Payout</p>
              <p className="text-3xl font-bold">{formatCurrency(stats?.pendingPayout || 0)}</p>
              <p className="text-sm text-purple-200 mt-1">Next payout: March 1, 2024</p>
            </div>
            <button className="px-4 py-2 bg-white text-purple-600 rounded-lg font-medium hover:bg-purple-50">
              Request Payout
            </button>
          </div>
        </div>
      )}

      {/* Recent Templates */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-gray-900">Your Templates</h3>
          <button
            onClick={() => setActiveTab('templates')}
            className="text-sm text-purple-600 hover:underline"
          >
            View All
          </button>
        </div>
        <div className="divide-y">
          {templates.slice(0, 3).map((template) => (
            <div key={template.id} className="flex items-center gap-4 p-4">
              <div className="w-16 h-12 bg-gray-100 rounded flex items-center justify-center">
                <span className="text-gray-400 text-xs">Preview</span>
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{template.name}</h4>
                <p className="text-sm text-gray-500">
                  {template.stats.downloads} downloads • {formatCurrency(template.stats.revenue)}
                </p>
              </div>
              {getStatusBadge(template.status)}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Reviews */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-gray-900">Recent Reviews</h3>
          <button
            onClick={() => setActiveTab('reviews')}
            className="text-sm text-purple-600 hover:underline"
          >
            View All
          </button>
        </div>
        <div className="divide-y">
          {reviews.slice(0, 3).map((review) => (
            <div key={review.id} className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <span className="font-medium text-gray-900">{review.user_name}</span>
                  <span className="text-gray-400 mx-2">on</span>
                  <span className="text-gray-600">{review.template_name}</span>
                </div>
                <div className="flex">{renderStars(review.rating)}</div>
              </div>
              <p className="text-gray-600 text-sm">{review.comment}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTemplates = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Your Templates</h3>
        <button className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700">
          + Upload New Template
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Template</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Status</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Price</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Downloads</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Revenue</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Rating</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {templates.map((template) => (
              <tr key={template.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-9 bg-gray-100 rounded" />
                    <span className="font-medium text-gray-900">{template.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3">{getStatusBadge(template.status)}</td>
                <td className="px-4 py-3 text-gray-600">
                  {template.isFree ? 'Free' : formatCurrency(template.price)}
                </td>
                <td className="px-4 py-3 text-gray-600">{template.stats.downloads}</td>
                <td className="px-4 py-3 text-gray-600">{formatCurrency(template.stats.revenue)}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <span className="text-yellow-400">★</span>
                    <span className="text-gray-600">{template.stats.rating || '-'}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                      </svg>
                    </button>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button className="p-1 text-gray-400 hover:text-red-600">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderEarnings = () => (
    <div className="space-y-6">
      {/* Earnings Chart Placeholder */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Earnings Overview</h3>
        <div className="h-64 flex items-end justify-between gap-2">
          {earningsData.map((data, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div
                className="w-full bg-purple-500 rounded-t"
                style={{ height: `${(data.earnings / 500) * 100}%`, minHeight: '10px' }}
              />
              <span className="text-xs text-gray-500 mt-2">
                {new Date(data.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Payout History */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="p-4 border-b">
          <h3 className="font-semibold text-gray-900">Payout History</h3>
        </div>
        <div className="p-4">
          <div className="space-y-3">
            {[
              { date: '2024-02-01', amount: 1245.50, status: 'completed' },
              { date: '2024-01-01', amount: 987.25, status: 'completed' },
              { date: '2023-12-01', amount: 1567.80, status: 'completed' },
            ].map((payout, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{formatCurrency(payout.amount)}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(payout.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                  {payout.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderReviews = () => (
    <div className="space-y-4">
      <h3 className="font-semibold text-gray-900">Customer Reviews</h3>
      <div className="bg-white rounded-lg shadow-sm divide-y">
        {reviews.map((review) => (
          <div key={review.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-gray-900">{review.user_name}</span>
                  <span className="text-gray-400">•</span>
                  <span className="text-sm text-gray-500">{review.template_name}</span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex">{renderStars(review.rating)}</div>
                  <span className="text-sm text-gray-500">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-600">{review.comment}</p>
              </div>
              <button className="text-purple-600 text-sm hover:underline">Reply</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Creator Profile</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Display Name
            </label>
            <input
              type="text"
              defaultValue="Design Studio"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
            <textarea
              rows={3}
              defaultValue="Professional design studio creating beautiful templates."
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Website</label>
            <input
              type="url"
              defaultValue="https://designstudio.com"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Payout Settings</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payout Method
            </label>
            <select className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500">
              <option>PayPal</option>
              <option>Bank Transfer</option>
              <option>Stripe</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              PayPal Email
            </label>
            <input
              type="email"
              defaultValue="payments@designstudio.com"
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
        </div>
      </div>

      <button className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700">
        Save Changes
      </button>
    </div>
  );

  const TABS: { key: TabType; label: string; icon: string }[] = [
    { key: 'overview', label: 'Overview', icon: '📊' },
    { key: 'templates', label: 'Templates', icon: '📦' },
    { key: 'earnings', label: 'Earnings', icon: '💰' },
    { key: 'reviews', label: 'Reviews', icon: '⭐' },
    { key: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">Creator Dashboard</h1>
          <p className="text-gray-500">Manage your templates and track your earnings</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Sidebar Tabs */}
          <div className="w-64 flex-shrink-0">
            <nav className="bg-white rounded-lg shadow-sm p-2">
              {TABS.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                    activeTab === tab.key
                      ? 'bg-purple-100 text-purple-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'templates' && renderTemplates()}
            {activeTab === 'earnings' && renderEarnings()}
            {activeTab === 'reviews' && renderReviews()}
            {activeTab === 'settings' && renderSettings()}
          </div>
        </div>
      </div>
    </div>
  );
}

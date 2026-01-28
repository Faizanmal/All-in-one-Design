/**
 * A/B Testing Dashboard Component
 * Create, manage, and analyze A/B tests for designs
 */
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  TestTube,
  Play,
  Pause,
  CheckCircle,
  BarChart3,
  Plus,
  Trash2,
  TrendingUp,
  Users,
  MousePointer,
  Target,
  Loader2,
} from 'lucide-react';

interface ABTestVariant {
  id: string;
  name: string;
  description: string;
  trafficPercentage: number;
  isControl: boolean;
  results?: {
    impressions: number;
    clicks: number;
    conversions: number;
    clickRate: number;
    conversionRate: number;
    avgEngagementTime: number;
    confidenceLevel: number;
  };
}

interface ABTest {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  primaryGoal: 'clicks' | 'conversions' | 'engagement_time';
  variants: ABTestVariant[];
  winningVariantId?: string;
  startDate?: string;
  endDate?: string;
  createdAt: string;
}

interface ABTestDashboardProps {
  projectId: string;
}

export const ABTestDashboard: React.FC<ABTestDashboardProps> = ({ projectId }) => {
  const [tests, setTests] = useState<ABTest[]>([]);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const fetchTests = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/projects/ab-tests/?project=${projectId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTests(data.results || []);
      }
    } catch (err) {
      console.error('Failed to fetch tests:', err);
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchTests();
  }, [fetchTests]);

  const startTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/ab-tests/${testId}/start/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        fetchTests();
      }
    } catch (err) {
      console.error('Failed to start test:', err);
    }
  };

  const pauseTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/ab-tests/${testId}/pause/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        fetchTests();
      }
    } catch (err) {
      console.error('Failed to pause test:', err);
    }
  };

  const completeTest = async (testId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/ab-tests/${testId}/complete/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        fetchTests();
      }
    } catch (err) {
      console.error('Failed to complete test:', err);
    }
  };

  const getStatusColor = (status: ABTest['status']) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300';
      case 'paused':
        return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300';
      case 'completed':
        return 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const getGoalIcon = (goal: ABTest['primaryGoal']) => {
    switch (goal) {
      case 'clicks':
        return <MousePointer className="w-4 h-4" />;
      case 'conversions':
        return <Target className="w-4 h-4" />;
      case 'engagement_time':
        return <TrendingUp className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
            <TestTube className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              A/B Testing
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Test design variations to optimize performance
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium"
        >
          <Plus className="w-4 h-4" />
          New Test
        </button>
      </div>

      {/* Tests List */}
      {tests.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
          <TestTube className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No A/B Tests Yet
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Create your first test to start optimizing your designs
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium"
          >
            <Plus className="w-4 h-4" />
            Create Test
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {tests.map((test) => (
            <div
              key={test.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow"
            >
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        test.status
                      )}`}
                    >
                      {test.status.charAt(0).toUpperCase() + test.status.slice(1)}
                    </span>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {test.name}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2">
                    {test.status === 'draft' && (
                      <button
                        onClick={() => startTest(test.id)}
                        className="p-2 text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    {test.status === 'running' && (
                      <>
                        <button
                          onClick={() => pauseTest(test.id)}
                          className="p-2 text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 rounded"
                        >
                          <Pause className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => completeTest(test.id)}
                          className="p-2 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setSelectedTest(test)}
                      className="p-2 text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                    >
                      <BarChart3 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                {test.description && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    {test.description}
                  </p>
                )}
                <div className="flex items-center gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
                  <span className="flex items-center gap-1">
                    {getGoalIcon(test.primaryGoal)}
                    {test.primaryGoal.replace('_', ' ')}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {test.variants.length} variants
                  </span>
                </div>
              </div>

              {/* Variants Summary */}
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {test.variants.map((variant) => (
                    <div
                      key={variant.id}
                      className={`p-3 rounded-lg border-2 ${
                        test.winningVariantId === variant.id
                          ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                          : 'border-gray-200 dark:border-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {variant.name}
                        </span>
                        {variant.isControl && (
                          <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                            Control
                          </span>
                        )}
                        {test.winningVariantId === variant.id && (
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded text-xs">
                            Winner
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        {variant.trafficPercentage}% traffic
                      </div>
                      {variant.results && (
                        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 grid grid-cols-2 gap-2 text-xs">
                          <div>
                            <span className="text-gray-500">Impressions</span>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {variant.results.impressions.toLocaleString()}
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-500">Click Rate</span>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {variant.results.clickRate.toFixed(2)}%
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-500">Conv. Rate</span>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {variant.results.conversionRate.toFixed(2)}%
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-500">Confidence</span>
                            <p className="font-medium text-gray-900 dark:text-white">
                              {variant.results.confidenceLevel.toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Test Modal */}
      {showCreateModal && (
        <CreateTestModal
          projectId={projectId}
          onClose={() => setShowCreateModal(false)}
          onCreated={() => {
            setShowCreateModal(false);
            fetchTests();
          }}
        />
      )}

      {/* Test Results Modal */}
      {selectedTest && (
        <TestResultsModal
          test={selectedTest}
          onClose={() => setSelectedTest(null)}
        />
      )}
    </div>
  );
};

// Create Test Modal Component
interface CreateTestModalProps {
  projectId: string;
  onClose: () => void;
  onCreated: () => void;
}

const CreateTestModal: React.FC<CreateTestModalProps> = ({
  projectId,
  onClose,
  onCreated,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [goal, setGoal] = useState<ABTest['primaryGoal']>('clicks');
  const [variants, setVariants] = useState([
    { name: 'Control', traffic: 50, isControl: true },
    { name: 'Variant A', traffic: 50, isControl: false },
  ]);
  const [saving, setSaving] = useState(false);

  const addVariant = () => {
    const newTraffic = Math.floor(100 / (variants.length + 1));
    setVariants([
      ...variants.map((v) => ({ ...v, traffic: newTraffic })),
      { name: `Variant ${String.fromCharCode(65 + variants.length - 1)}`, traffic: newTraffic, isControl: false },
    ]);
  };

  const removeVariant = (index: number) => {
    if (variants.length <= 2) return;
    const newVariants = variants.filter((_, i) => i !== index);
    const newTraffic = Math.floor(100 / newVariants.length);
    setVariants(newVariants.map((v) => ({ ...v, traffic: newTraffic })));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const response = await fetch('/api/v1/projects/ab-tests/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          project: projectId,
          name,
          description,
          primary_goal: goal,
          variants: variants.map((v) => ({
            name: v.name,
            traffic_percentage: v.traffic,
            is_control: v.isControl,
          })),
        }),
      });

      if (response.ok) {
        onCreated();
      }
    } catch (err) {
      console.error('Failed to create test:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Create A/B Test
            </h3>
          </div>

          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Test Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Primary Goal
              </label>
              <select
                value={goal}
                onChange={(e) => setGoal(e.target.value as ABTest['primaryGoal'])}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="clicks">Clicks</option>
                <option value="conversions">Conversions</option>
                <option value="engagement_time">Engagement Time</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Variants
                </label>
                <button
                  type="button"
                  onClick={addVariant}
                  className="text-sm text-purple-600 hover:text-purple-700"
                >
                  + Add Variant
                </button>
              </div>
              <div className="space-y-2">
                {variants.map((variant, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <input
                      type="text"
                      value={variant.name}
                      onChange={(e) => {
                        const newVariants = [...variants];
                        newVariants[index].name = e.target.value;
                        setVariants(newVariants);
                      }}
                      className="flex-1 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-1 focus:ring-purple-500 dark:bg-gray-600 dark:text-white text-sm"
                    />
                    <div className="flex items-center gap-1">
                      <input
                        type="number"
                        value={variant.traffic}
                        onChange={(e) => {
                          const newVariants = [...variants];
                          newVariants[index].traffic = parseInt(e.target.value) || 0;
                          setVariants(newVariants);
                        }}
                        min="0"
                        max="100"
                        className="w-16 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded focus:ring-1 focus:ring-purple-500 dark:bg-gray-600 dark:text-white text-sm"
                      />
                      <span className="text-sm text-gray-500">%</span>
                    </div>
                    {variant.isControl && (
                      <span className="px-2 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-xs">
                        Control
                      </span>
                    )}
                    {!variant.isControl && variants.length > 2 && (
                      <button
                        type="button"
                        onClick={() => removeVariant(index)}
                        className="p-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving || !name}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create Test'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Test Results Modal Component
interface TestResultsModalProps {
  test: ABTest;
  onClose: () => void;
}

const TestResultsModal: React.FC<TestResultsModalProps> = ({ test, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Test Results: {test.name}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {test.variants.map((variant) => (
              <div
                key={variant.id}
                className={`p-4 rounded-lg border-2 ${
                  test.winningVariantId === variant.id
                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                    : 'border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white">
                    {variant.name}
                  </h4>
                  {test.winningVariantId === variant.id && (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  )}
                </div>

                {variant.results ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Impressions</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {variant.results.impressions.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Clicks</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {variant.results.clicks.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Click Rate</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {variant.results.clickRate.toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Conversions</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {variant.results.conversions.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500 dark:text-gray-400">Conv. Rate</span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {variant.results.conversionRate.toFixed(2)}%
                      </span>
                    </div>
                    <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex justify-between">
                        <span className="text-gray-500 dark:text-gray-400">Confidence</span>
                        <span className={`font-medium ${
                          variant.results.confidenceLevel >= 95
                            ? 'text-green-600 dark:text-green-400'
                            : 'text-yellow-600 dark:text-yellow-400'
                        }`}>
                          {variant.results.confidenceLevel.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    No results yet. Start the test to begin collecting data.
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ABTestDashboard;

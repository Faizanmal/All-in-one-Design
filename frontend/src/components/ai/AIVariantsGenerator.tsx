/**
 * AI Design Variants Generator Component
 */
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Sparkles, CheckCircle } from 'lucide-react';

interface DesignVariant {
  variant_id: number;
  concept: string;
  style: string;
  color_palette: Array<{ hex: string; name: string; role: string }>;
  typography: {
    heading: { font: string; size: number; weight: string };
    body: { font: string; size: number; weight: string };
  };
  elements: unknown[];
  rationale: string;
}

interface AIVariantsResponse {
  variants: DesignVariant[];
  comparison: string;
  recommendation: string;
  tokens_used: number;
}

export function AIVariantsGenerator({ onVariantSelect }: { onVariantSelect?: (variant: DesignVariant) => void }) {
  const [prompt, setPrompt] = useState('');
  const [numVariants, setNumVariants] = useState(3);
  const [designType, setDesignType] = useState<'graphic' | 'ui_ux' | 'logo'>('graphic');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AIVariantsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a design prompt');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/ai/enhanced/generate_variants/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          prompt,
          design_type: designType,
          num_variants: numVariants,
          style_preferences: {}
        })
      });

      if (!res.ok) {
        throw new Error('Failed to generate variants');
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            AI Design Variants Generator
          </CardTitle>
          <CardDescription>
            Generate multiple design concepts from a single prompt
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="prompt">Design Prompt</Label>
            <Input
              id="prompt"
              placeholder="e.g., Modern tech startup landing page with blue accents"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="design-type">Design Type</Label>
              <select
                id="design-type"
                className="w-full border rounded-md p-2"
                value={designType}
                onChange={(e) => setDesignType(e.target.value as 'graphic' | 'ui_ux' | 'logo')}
                disabled={loading}
              >
                <option value="graphic">Graphic Design</option>
                <option value="ui_ux">UI/UX Design</option>
                <option value="logo">Logo Design</option>
              </select>
            </div>

            <div>
              <Label htmlFor="num-variants">Number of Variants</Label>
              <Input
                id="num-variants"
                type="number"
                min={1}
                max={5}
                value={numVariants}
                onChange={(e) => setNumVariants(parseInt(e.target.value) || 3)}
                disabled={loading}
              />
            </div>
          </div>

          <Button
            onClick={handleGenerate}
            disabled={loading || !prompt.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Variants
              </>
            )}
          </Button>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}
        </CardContent>
      </Card>

      {/* Results Section */}
      {response && (
        <div className="space-y-6">
          {/* Recommendation */}
          {response.recommendation && (
            <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200">
              <CardHeader>
                <CardTitle className="text-blue-900 dark:text-blue-100 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  AI Recommendation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-blue-800 dark:text-blue-200">{response.recommendation}</p>
              </CardContent>
            </Card>
          )}

          {/* Variants Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {response.variants.map((variant) => (
              <Card key={variant.variant_id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="text-lg">Variant {variant.variant_id}</CardTitle>
                  <CardDescription>{variant.concept}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Style Badge */}
                  <Badge variant="secondary">{variant.style}</Badge>

                  {/* Color Palette */}
                  <div>
                    <p className="text-sm font-medium mb-2">Colors</p>
                    <div className="flex gap-2 flex-wrap">
                      {variant.color_palette.slice(0, 5).map((color, idx) => (
                        <div
                          key={idx}
                          className="w-8 h-8 rounded border border-gray-300"
                          style={{ backgroundColor: color.hex }}
                          title={`${color.name} - ${color.role}`}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Typography */}
                  <div>
                    <p className="text-sm font-medium mb-1">Typography</p>
                    <p className="text-xs text-gray-600">
                      Heading: {variant.typography.heading.font}<br />
                      Body: {variant.typography.body.font}
                    </p>
                  </div>

                  {/* Rationale */}
                  <div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {variant.rationale}
                    </p>
                  </div>

                  {/* Action Button */}
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => onVariantSelect?.(variant)}
                  >
                    Use This Variant
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Comparison */}
          {response.comparison && (
            <Card>
              <CardHeader>
                <CardTitle>Comparison</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 dark:text-gray-300">{response.comparison}</p>
              </CardContent>
            </Card>
          )}

          {/* Tokens Used */}
          <div className="text-sm text-gray-500 text-center">
            AI Tokens Used: {response.tokens_used}
          </div>
        </div>
      )}
    </div>
  );
}

'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Wand2, Palette, Type, Layout, TrendingUp, Sparkles,
  ArrowRight, CheckCircle, AlertCircle, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface CritiqueResult {
  overall_score: number;
  scores: {
    color_harmony: number;
    typography: number;
    layout_spacing: number;
    visual_hierarchy: number;
    overall_impact: number;
  };
  strengths: string[];
  improvements: string[];
  summary: string;
}

interface ColorPalette {
  palette: Array<{
    hex: string;
    name: string;
    role: string;
    usage: string;
  }>;
  description: string;
  color_scheme: string;
  accessibility: {
    wcag_compliant: boolean;
    notes: string;
  };
}

export default function AIAssistantPage() {
  const [loading, setLoading] = useState(false);
  const [critiqueResult, setCritiqueResult] = useState<CritiqueResult | null>(null);
  const [colorPalette, setColorPalette] = useState<ColorPalette | null>(null);
  const [typographySuggestions, setTypographySuggestions] = useState<any>(null);
  const [layoutOptimization, setLayoutOptimization] = useState<any>(null);
  const [trendAnalysis, setTrendAnalysis] = useState<any>(null);

  // Form states
  const [designData, setDesignData] = useState({
    project_type: 'website',
    colors: ['#FF6B6B', '#4ECDC4'],
    fonts: ['Roboto', 'Open Sans'],
    element_count: 12,
    layout_type: 'grid'
  });

  const [colorData, setColorData] = useState({
    base_color: '#FF6B6B',
    mood: 'professional',
    industry: 'tech',
    count: 5
  });

  const [typographyData, setTypographyData] = useState({
    design_type: 'website',
    mood: 'professional',
    brand_attributes: ['modern', 'trustworthy']
  });

  const critiqueDesign = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/ai/critique-design/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(designData),
      });
      const data = await response.json();
      if (data.success) {
        setCritiqueResult(data.critique);
      }
    } catch (error) {
      console.error('Failed to critique design:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateColorHarmony = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/ai/generate-color-harmony/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(colorData),
      });
      const data = await response.json();
      if (data.success) {
        setColorPalette(data.palette);
      }
    } catch (error) {
      console.error('Failed to generate color palette:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSuggestedTypography = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/ai/suggest-typography/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(typographyData),
      });
      const data = await response.json();
      if (data.success) {
        setTypographySuggestions(data.typography);
      }
    } catch (error) {
      console.error('Failed to get typography suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeDesignTrends = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/ai/analyze-design-trends/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          industry: 'tech',
          design_type: 'website'
        }),
      });
      const data = await response.json();
      if (data.success) {
        setTrendAnalysis(data.trends);
      }
    } catch (error) {
      console.error('Failed to analyze trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const ScoreBar = ({ score, label }: { score: number; label: string }) => (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-semibold">{score}/10</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score * 10}%` }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className={`h-full ${
            score >= 8 ? 'bg-green-500' : score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
          }`}
        />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-2">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              AI Design Assistant
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Get AI-powered insights, critiques, and suggestions to improve your designs
          </p>
        </motion.div>

        <Tabs defaultValue="critique" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="critique">
              <Wand2 className="mr-2 h-4 w-4" />
              Critique
            </TabsTrigger>
            <TabsTrigger value="colors">
              <Palette className="mr-2 h-4 w-4" />
              Colors
            </TabsTrigger>
            <TabsTrigger value="typography">
              <Type className="mr-2 h-4 w-4" />
              Typography
            </TabsTrigger>
            <TabsTrigger value="layout">
              <Layout className="mr-2 h-4 w-4" />
              Layout
            </TabsTrigger>
            <TabsTrigger value="trends">
              <TrendingUp className="mr-2 h-4 w-4" />
              Trends
            </TabsTrigger>
          </TabsList>

          {/* Design Critique Tab */}
          <TabsContent value="critique">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Design Information</CardTitle>
                  <CardDescription>
                    Provide details about your design for AI analysis
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Project Type</Label>
                    <Select
                      value={designData.project_type}
                      onValueChange={(value) => setDesignData({ ...designData, project_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="website">Website</SelectItem>
                        <SelectItem value="social_media">Social Media</SelectItem>
                        <SelectItem value="logo">Logo</SelectItem>
                        <SelectItem value="poster">Poster</SelectItem>
                        <SelectItem value="ui_ux">UI/UX</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Colors Used (comma-separated hex codes)</Label>
                    <Input
                      placeholder="#FF6B6B, #4ECDC4"
                      value={designData.colors.join(', ')}
                      onChange={(e) => setDesignData({
                        ...designData,
                        colors: e.target.value.split(',').map(c => c.trim())
                      })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Fonts Used (comma-separated)</Label>
                    <Input
                      placeholder="Roboto, Open Sans"
                      value={designData.fonts.join(', ')}
                      onChange={(e) => setDesignData({
                        ...designData,
                        fonts: e.target.value.split(',').map(f => f.trim())
                      })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Element Count</Label>
                    <Input
                      type="number"
                      value={designData.element_count}
                      onChange={(e) => setDesignData({ ...designData, element_count: parseInt(e.target.value) })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Layout Type</Label>
                    <Select
                      value={designData.layout_type}
                      onValueChange={(value) => setDesignData({ ...designData, layout_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="grid">Grid</SelectItem>
                        <SelectItem value="flex">Flexbox</SelectItem>
                        <SelectItem value="freeform">Freeform</SelectItem>
                        <SelectItem value="masonry">Masonry</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Button onClick={critiqueDesign} disabled={loading} className="w-full">
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                    Analyze Design
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>AI Critique Results</CardTitle>
                  <CardDescription>
                    Professional feedback on your design
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {critiqueResult ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-6"
                    >
                      {/* Overall Score */}
                      <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl">
                        <div className="text-5xl font-bold text-purple-600 mb-2">
                          {critiqueResult.overall_score}/10
                        </div>
                        <div className="text-gray-600">Overall Score</div>
                      </div>

                      {/* Individual Scores */}
                      <div className="space-y-3">
                        <ScoreBar score={critiqueResult.scores.color_harmony} label="Color Harmony" />
                        <ScoreBar score={critiqueResult.scores.typography} label="Typography" />
                        <ScoreBar score={critiqueResult.scores.layout_spacing} label="Layout & Spacing" />
                        <ScoreBar score={critiqueResult.scores.visual_hierarchy} label="Visual Hierarchy" />
                        <ScoreBar score={critiqueResult.scores.overall_impact} label="Overall Impact" />
                      </div>

                      {/* Summary */}
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <p className="text-gray-700">{critiqueResult.summary}</p>
                      </div>

                      {/* Strengths */}
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center text-green-600">
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Strengths
                        </h4>
                        <ul className="space-y-2">
                          {critiqueResult.strengths.map((strength, i) => (
                            <li key={i} className="flex items-start space-x-2">
                              <span className="text-green-500 mt-1">•</span>
                              <span className="text-gray-700">{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Improvements */}
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center text-orange-600">
                          <AlertCircle className="mr-2 h-4 w-4" />
                          Suggested Improvements
                        </h4>
                        <ul className="space-y-2">
                          {critiqueResult.improvements.map((improvement, i) => (
                            <li key={i} className="flex items-start space-x-2">
                              <ArrowRight className="h-4 w-4 text-orange-500 mt-1 flex-shrink-0" />
                              <span className="text-gray-700">{improvement}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </motion.div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Wand2 className="mx-auto h-12 w-12 mb-4 text-gray-300" />
                      <p>Enter your design details and click Analyze to get AI feedback</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Color Harmony Tab */}
          <TabsContent value="colors">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Color Palette Generator</CardTitle>
                  <CardDescription>
                    Generate harmonious color palettes with AI
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Base Color (Optional)</Label>
                    <Input
                      type="color"
                      value={colorData.base_color}
                      onChange={(e) => setColorData({ ...colorData, base_color: e.target.value })}
                      className="h-12"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Mood</Label>
                    <Select
                      value={colorData.mood}
                      onValueChange={(value) => setColorData({ ...colorData, mood: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Professional</SelectItem>
                        <SelectItem value="playful">Playful</SelectItem>
                        <SelectItem value="elegant">Elegant</SelectItem>
                        <SelectItem value="energetic">Energetic</SelectItem>
                        <SelectItem value="calming">Calming</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Industry</Label>
                    <Select
                      value={colorData.industry}
                      onValueChange={(value) => setColorData({ ...colorData, industry: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="tech">Technology</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="fashion">Fashion</SelectItem>
                        <SelectItem value="food">Food & Beverage</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Number of Colors</Label>
                    <Input
                      type="number"
                      min="3"
                      max="10"
                      value={colorData.count}
                      onChange={(e) => setColorData({ ...colorData, count: parseInt(e.target.value) })}
                    />
                  </div>

                  <Button onClick={generateColorHarmony} disabled={loading} className="w-full">
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Palette className="mr-2 h-4 w-4" />}
                    Generate Palette
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Generated Palette</CardTitle>
                  <CardDescription>
                    AI-generated harmonious color combinations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {colorPalette ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="space-y-4"
                    >
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <p className="text-gray-700 mb-2">{colorPalette.description}</p>
                        <Badge variant="outline">{colorPalette.color_scheme}</Badge>
                      </div>

                      <div className="grid gap-3">
                        {colorPalette.palette.map((color, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="flex items-center space-x-4 p-3 rounded-lg border hover:shadow-md transition-shadow"
                          >
                            <div
                              className="h-16 w-16 rounded-lg shadow-md flex-shrink-0"
                              style={{ backgroundColor: color.hex }}
                            />
                            <div className="flex-1">
                              <div className="font-semibold">{color.name}</div>
                              <code className="text-sm text-gray-600">{color.hex}</code>
                              <div className="text-xs text-gray-500 mt-1">
                                <Badge variant="secondary" className="mr-2">{color.role}</Badge>
                                {color.usage}
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>

                      {colorPalette.accessibility.wcag_compliant ? (
                        <div className="p-3 bg-green-50 text-green-700 rounded-lg flex items-center">
                          <CheckCircle className="mr-2 h-4 w-4" />
                          WCAG Compliant
                        </div>
                      ) : (
                        <div className="p-3 bg-yellow-50 text-yellow-700 rounded-lg flex items-start">
                          <AlertCircle className="mr-2 h-4 w-4 mt-0.5" />
                          <div>
                            <div className="font-semibold">Accessibility Note</div>
                            <div className="text-sm">{colorPalette.accessibility.notes}</div>
                          </div>
                        </div>
                      )}
                    </motion.div>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <Palette className="mx-auto h-12 w-12 mb-4 text-gray-300" />
                      <p>Configure your preferences and generate a color palette</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Typography Tab */}
          <TabsContent value="typography">
            <Card>
              <CardHeader>
                <CardTitle>Typography Suggestions</CardTitle>
                <CardDescription>
                  Get AI-powered font pairing recommendations
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Design Type</Label>
                      <Select
                        value={typographyData.design_type}
                        onValueChange={(value) => setTypographyData({ ...typographyData, design_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="website">Website</SelectItem>
                          <SelectItem value="app">Mobile App</SelectItem>
                          <SelectItem value="poster">Poster</SelectItem>
                          <SelectItem value="logo">Logo</SelectItem>
                          <SelectItem value="presentation">Presentation</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Mood</Label>
                      <Select
                        value={typographyData.mood}
                        onValueChange={(value) => setTypographyData({ ...typographyData, mood: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="professional">Professional</SelectItem>
                          <SelectItem value="creative">Creative</SelectItem>
                          <SelectItem value="friendly">Friendly</SelectItem>
                          <SelectItem value="bold">Bold</SelectItem>
                          <SelectItem value="minimal">Minimal</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <Button onClick={getSuggestedTypography} disabled={loading} className="w-full">
                      {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Type className="mr-2 h-4 w-4" />}
                      Get Suggestions
                    </Button>
                  </div>

                  <div>
                    {typographySuggestions ? (
                      <div className="space-y-4">
                        {typographySuggestions.pairings?.slice(0, 3).map((pairing: any, i: number) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                          >
                            <div className="mb-3">
                              <div className="text-2xl font-bold mb-1" style={{ fontFamily: pairing.heading_font.name }}>
                                {pairing.heading_font.name}
                              </div>
                              <div className="text-sm text-gray-600">Heading Font</div>
                            </div>
                            <div className="mb-3">
                              <div className="text-lg" style={{ fontFamily: pairing.body_font.name }}>
                                {pairing.body_font.name}
                              </div>
                              <div className="text-sm text-gray-600">Body Font</div>
                            </div>
                            <div className="text-sm text-gray-700 italic border-l-4 border-purple-500 pl-3">
                              {pairing.rationale}
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-12 text-gray-500">
                        <Type className="mx-auto h-12 w-12 mb-4 text-gray-300" />
                        <p>Select your preferences to get typography recommendations</p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Layout Tab - Placeholder */}
          <TabsContent value="layout">
            <Card>
              <CardHeader>
                <CardTitle>Layout Optimization</CardTitle>
                <CardDescription>
                  Get AI suggestions for improving your layout
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center py-12 text-gray-500">
                <Layout className="mx-auto h-12 w-12 mb-4 text-gray-300" />
                <p>Layout optimization coming soon!</p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Trends Tab */}
          <TabsContent value="trends">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Design Trends Analysis</CardTitle>
                    <CardDescription>
                      Stay up-to-date with current design trends
                    </CardDescription>
                  </div>
                  <Button onClick={analyzeDesignTrends} disabled={loading}>
                    {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <TrendingUp className="mr-2 h-4 w-4" />}
                    Analyze Trends
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {trendAnalysis ? (
                  <div className="space-y-6">
                    {trendAnalysis.current_trends?.map((trend: any, i: number) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-4 border rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-semibold text-lg">{trend.name}</h4>
                          <Badge variant={trend.popularity === 'high' ? 'default' : 'secondary'}>
                            {trend.popularity}
                          </Badge>
                        </div>
                        <p className="text-gray-700 mb-2">{trend.description}</p>
                        <p className="text-sm text-gray-600 italic">{trend.examples}</p>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <TrendingUp className="mx-auto h-12 w-12 mb-4 text-gray-300" />
                    <p>Click Analyze Trends to get current design trend insights</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

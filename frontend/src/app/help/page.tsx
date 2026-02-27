"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import {
  HelpCircle,
  Search,
  MessageCircle,
  PlayCircle,
  FileText,
  AlertCircle,
  Zap,
  Users,
  Eye,
  Code,
  Share2,
  Shield,
} from 'lucide-react';

interface HelpArticle {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  content: string;
  category: 'getting-started' | 'features' | 'faq' | 'troubleshooting';
}

const helpArticles: HelpArticle[] = [
  {
    id: 'getting-started-1',
    title: 'Getting Started with Design Studio',
    description: 'Learn the basics of creating your first design project',
    icon: <PlayCircle className="h-6 w-6" />,
    content: 'Welcome to Design Studio! Here\'s how to get started: 1. Create a new project by clicking "New Project" button. 2. Choose your project type (UI/UX, Graphic, or Logo). 3. Start designing with our intuitive tools.',
    category: 'getting-started',
  },
  {
    id: 'getting-started-2',
    title: 'Understanding the Workspace',
    description: 'Explore tools, panels, and how to navigate',
    icon: <Eye className="h-6 w-6" />,
    content: 'The workspace consists of: Canvas (center), Toolbar (top), Layers panel (left), Properties panel (right). Use keyboard shortcuts to speed up your workflow. Press "?" to see all available shortcuts.',
    category: 'getting-started',
  },
  {
    id: 'features-1',
    title: 'AI-Powered Design Generation',
    description: 'Leverage AI tools for faster design creation',
    icon: <Zap className="h-6 w-6" />,
    content: 'Our AI tools help you generate designs instantly. Use the "AI Logo Designer" for professional logos or "AI UI/UX Generator" for complete UI designs. Just describe what you want, and let AI do the work!',
    category: 'features',
  },
  {
    id: 'features-2',
    title: 'Collaboration & Sharing',
    description: 'Work with team members in real-time',
    icon: <Users className="h-6 w-6" />,
    content: 'Share your projects with team members to collaborate. Set permissions (view, edit, comment) for each collaborator. Real-time updates ensure everyone is working with the latest version.',
    category: 'features',
  },
  {
    id: 'features-3',
    title: 'Export to Code',
    description: 'Convert designs to production-ready code',
    icon: <Code className="h-6 w-6" />,
    content: 'Export your designs as HTML/CSS, React, Vue, or other frameworks. Our code generation engine creates clean, optimized code ready for development teams.',
    category: 'features',
  },
  {
    id: 'faq-1',
    title: 'How do I reset my password?',
    description: 'Password recovery steps',
    icon: <Shield className="h-6 w-6" />,
    content: 'Click "Forgot Password" on the login page. Enter your email address. Check your inbox for the reset link. Follow the link and create a new password. You\'ll be redirected to login with your new password.',
    category: 'faq',
  },
  {
    id: 'faq-2',
    title: 'What file formats can I import?',
    description: 'Supported import file types',
    icon: <FileText className="h-6 w-6" />,
    content: 'We support: PNG, JPG, SVG, PDF, Sketch, Figma files. You can also paste content from the clipboard.',
    category: 'faq',
  },
  {
    id: 'faq-3',
    title: 'How do I delete a project?',
    description: 'Project deletion process',
    icon: <AlertCircle className="h-6 w-6" />,
    content: 'Right-click on the project in the projects list. Select "Delete" from the context menu. Confirm the deletion (projects can be recovered from trash for 30 days).',
    category: 'faq',
  },
  {
    id: 'troubleshooting-1',
    title: 'Projects not loading?',
    description: 'Fix project loading issues',
    icon: <AlertCircle className="h-6 w-6" />,
    content: 'Try: 1. Refresh the page. 2. Clear browser cache. 3. Check your internet connection. 4. Log out and log back in. 5. Contact support if the issue persists.',
    category: 'troubleshooting',
  },
  {
    id: 'troubleshooting-2',
    title: 'Export failing?',
    description: 'Resolve export issues',
    icon: <AlertCircle className="h-6 w-6" />,
    content: 'If export fails: 1. Ensure all assets are properly named. 2. Check file size (max 100MB). 3. Try exporting in a different format. 4. Contact our support team with error details.',
    category: 'troubleshooting',
  },
];

export default function HelpPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | HelpArticle['category']>('all');
  const [selectedArticle, setSelectedArticle] = useState<HelpArticle | null>(null);

  const filteredArticles = helpArticles.filter((article) => {
    const matchesSearch = article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <DashboardSidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <MainHeader />

        <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Help & Support</h1>
            <p className="text-gray-600">Find answers and get help with Design Studio</p>
          </div>

          {/* Search Bar */}
          <div className="mb-8 relative">
            <Search className="absolute left-4 top-3 h-5 w-5 text-gray-400" />
            <Input
              placeholder="Search help articles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-12 h-12 text-lg"
            />
          </div>

          {/* Main Content */}
          {selectedArticle ? (
            // Article Detail View
            <div className="mb-8">
              <Button
                variant="ghost"
                className="mb-4"
                onClick={() => setSelectedArticle(null)}
              >
                ← Back to Help
              </Button>
              <Card>
                <CardHeader>
                  <div className="flex items-start gap-4">
                    <div className="text-blue-600">{selectedArticle.icon}</div>
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-2">{selectedArticle.title}</CardTitle>
                      <CardDescription>{selectedArticle.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{selectedArticle.content}</p>
                  <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-900">
                      <strong>Still need help?</strong> Contact our support team at{' '}
                      <a href="mailto:support@designstudio.com" className="underline">
                        support@designstudio.com
                      </a>
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            // Articles List View
            <>
              {/* Category Tabs */}
              <Tabs defaultValue="all" className="mb-8" onValueChange={(value) => setSelectedCategory(value as 'all' | HelpArticle['category'])}>
                <TabsList className="grid w-full grid-cols-5 mb-8">
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="getting-started">Getting Started</TabsTrigger>
                  <TabsTrigger value="features">Features</TabsTrigger>
                  <TabsTrigger value="faq">FAQ</TabsTrigger>
                  <TabsTrigger value="troubleshooting">Troubleshooting</TabsTrigger>
                </TabsList>

                {/* Articles Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredArticles.length > 0 ? (
                    filteredArticles.map((article) => (
                      <Card
                        key={article.id}
                        className="cursor-pointer hover:shadow-lg transition-shadow hover:border-blue-200"
                        onClick={() => setSelectedArticle(article)}
                      >
                        <CardHeader>
                          <div className="flex items-start gap-4">
                            <div className="text-blue-600 mt-1">{article.icon}</div>
                            <div className="flex-1 min-w-0">
                              <CardTitle className="text-lg truncate">{article.title}</CardTitle>
                              <CardDescription className="mt-1">{article.description}</CardDescription>
                            </div>
                          </div>
                        </CardHeader>
                      </Card>
                    ))
                  ) : (
                    <Card className="col-span-full">
                      <CardContent className="text-center py-12">
                        <HelpCircle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500 text-lg">No articles found</p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </Tabs>

              {/* Contact Support Section */}
              <Card className="bg-linear-to-r from-blue-50 to-indigo-50 border-blue-200 mt-12">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageCircle className="h-5 w-5 text-blue-600" />
                    Need More Help?
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-4">
                    Can&apos;t find what you&apos;re looking for? Our support team is here to help!
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4">
                    <Button className="bg-blue-600 hover:bg-blue-700">
                      <MessageCircle className="h-4 w-4 mr-2" />
                      Email Support
                    </Button>
                    <Button variant="outline">
                      <Share2 className="h-4 w-4 mr-2" />
                      Chat with us
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

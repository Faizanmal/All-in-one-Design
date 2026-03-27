"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Home,
  FileText,
  Layout,
  Palette,
  Sparkles,
  Wand2,
  Clock,
  Heart,
  Users,
  Settings,
  HelpCircle,
  LogOut,
  Zap,
  Code,
  Database,
  BarChart3,
  Share2,
  Archive,
  Search,
  ChevronDown,
  Plus,
  LayoutTemplate,
  Image as ImageIcon,
  Type,
  Activity,
  Bell,
  Bot,
  Box,
  Edit3,
  Play,
  Plug,
  Gauge,
  Briefcase,
  CreditCard,
  Globe,
  Shield,
  MessageSquare,
  Layers,
  Grid,
  GitBranch,
  CheckCircle,
  Pen,
  FileType,
  Presentation,
  Lightbulb,
  ShoppingCart,
  Timer,
  Pencil,
  Eye,
  Lock,
  Package,
  Link as LinkIcon,
  Smartphone,
  WifiOff,
  FileDown,
} from 'lucide-react';

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  description?: string;
  badge?: string;
}

interface SidebarSection {
  title: string;
  items: SidebarItem[];
}

export function DashboardSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    workspace: true,
    'design tools': true,
    'brand & design systems': true,
    'animation & prototyping': true,
    'assets & resources': true,
    collaboration: true,
    'export & publishing': true,
    integrations: true,
    'analytics & optimization': true,
    productivity: true,
    'agency & whitelabel': true,
    account: true,
  });


  const sections: SidebarSection[] = [
    {
      title: 'WORKSPACE',
      items: [
        {
          name: 'Dashboard',
          href: '/dashboard',
          icon: <Home className="h-5 w-5" />,
          description: 'Overview and quick access',
        },
        {
          name: 'Projects',
          href: '/projects',
          icon: <FileText className="h-5 w-5" />,
          description: 'All your design projects',
        },
        {
          name: 'Recent',
          href: '/dashboard?filter=recent',
          icon: <Clock className="h-5 w-5" />,
          description: 'Recently accessed files',
        },
        {
          name: 'Favorites',
          href: '/dashboard?filter=favorites',
          icon: <Heart className="h-5 w-5" />,
          description: 'Starred projects',
        },
        {
          name: 'Archived',
          href: '/dashboard?filter=archived',
          icon: <Archive className="h-5 w-5" />,
          description: 'Archived projects',
        },
        {
          name: 'Activity',
          href: '/activity',
          icon: <Activity className="h-5 w-5" />,
          description: 'Recent actions',
        },
        {
          name: 'Notifications',
          href: '/notifications',
          icon: <Bell className="h-5 w-5" />,
          description: 'Updates and alerts',
        },
      ],
    },
    {
      title: 'DESIGN TOOLS',
      items: [
        {
          name: 'Design Hub',
          href: '/design-hub',
          icon: <Layout className="h-5 w-5" />,
          description: 'Main design workspace',
        },
        {
          name: 'Pro Editor',
          href: '/editor-v2',
          icon: <Edit3 className="h-5 w-5" />,
          description: 'Advanced canvas editor',
        },
        {
          name: 'AI Logo Designer',
          href: '/ai-logo-designer',
          icon: <Wand2 className="h-5 w-5" />,
          description: 'AI-powered logo creation',
          badge: 'AI',
        },
        {
          name: 'AI UI/UX Generator',
          href: '/ai-uiux-generator',
          icon: <Sparkles className="h-5 w-5" />,
          description: 'Instant UI/UX designs',
          badge: 'AI',
        },
        {
          name: 'AI Assistant',
          href: '/ai-assistant',
          icon: <Bot className="h-5 w-5" />,
          description: 'Chat and generate',
          badge: 'AI',
        },
        {
          name: 'Vector Editing',
          href: '/vector-editing',
          icon: <Pen className="h-5 w-5" />,
          description: 'Advanced vector tools',
        },
        {
          name: 'Auto Layout',
          href: '/auto-layout',
          icon: <Grid className="h-5 w-5" />,
          description: 'Smart layout system',
          badge: 'Smart',
        },
        {
          name: 'Whiteboard',
          href: '/whiteboard',
          icon: <Pencil className="h-5 w-5" />,
          description: 'Collaborative canvas',
        },
        {
          name: '3D Studio',
          href: '/studio-3d',
          icon: <Box className="h-5 w-5" />,
          description: '3D modeling & render',
        },
      ],
    },
    {
      title: 'BRAND & DESIGN SYSTEMS',
      items: [
        {
          name: 'Design System',
          href: '/design-system',
          icon: <Palette className="h-5 w-5" />,
          description: 'Manage design tokens',
        },
        {
          name: 'Brand Kit Guardian',
          href: '/brand-kit',
          icon: <Shield className="h-5 w-5" />,
          description: 'Enforce brand rules',
          badge: 'Pro',
        },
        {
          name: 'Component Variants',
          href: '/component-variants',
          icon: <Layers className="h-5 w-5" />,
          description: 'Manage component states',
        },
        {
          name: 'Interactive Components',
          href: '/interactive-components',
          icon: <Package className="h-5 w-5" />,
          description: 'Clickable prototypes',
        },
        {
          name: 'Design Branches',
          href: '/design-branches',
          icon: <GitBranch className="h-5 w-5" />,
          description: 'Version control designs',
        },
        {
          name: 'Design QA',
          href: '/design-qa',
          icon: <CheckCircle className="h-5 w-5" />,
          description: 'Quality assurance',
        },
      ],
    },
    {
      title: 'ANIMATION & PROTOTYPING',
      items: [
        {
          name: 'Animation Studio',
          href: '/animation-studio',
          icon: <Zap className="h-5 w-5" />,
          description: 'Create animations',
        },
        {
          name: 'Animation Timeline',
          href: '/animation-timeline',
          icon: <Timer className="h-5 w-5" />,
          description: 'Advanced timeline editor',
        },
        {
          name: 'Presentation Mode',
          href: '/presentation-mode',
          icon: <Presentation className="h-5 w-5" />,
          description: 'Present your designs',
        },
      ],
    },
    {
      title: 'ASSETS & RESOURCES',
      items: [
        {
          name: 'Assets Library',
          href: '/assets',
          icon: <ImageIcon className="h-5 w-5" />,
          description: 'Media and graphics',
        },
        {
          name: 'Asset Management',
          href: '/asset-management',
          icon: <Database className="h-5 w-5" />,
          description: 'Organize your assets',
        },
        {
          name: 'Font Assets',
          href: '/font-assets',
          icon: <Type className="h-5 w-5" />,
          description: 'Typography resources',
        },
        {
          name: 'Templates',
          href: '/templates',
          icon: <LayoutTemplate className="h-5 w-5" />,
          description: 'Ready-to-use templates',
        },
        {
          name: 'Template Marketplace',
          href: '/template-marketplace',
          icon: <ShoppingCart className="h-5 w-5" />,
          description: 'Buy & sell templates',
        },
        {
          name: 'Media Assets',
          href: '/media-assets',
          icon: <ImageIcon className="h-5 w-5" />,
          description: 'Stock photos & videos',
        },
      ],
    },
    {
      title: 'COLLABORATION',
      items: [
        {
          name: 'Teams',
          href: '/teams',
          icon: <Users className="h-5 w-5" />,
          description: 'Manage your team',
        },
        {
          name: 'Collaboration',
          href: '/collaboration',
          icon: <Share2 className="h-5 w-5" />,
          description: 'Share and collaborate',
        },
        {
          name: 'Commenting',
          href: '/commenting',
          icon: <MessageSquare className="h-5 w-5" />,
          description: 'Design feedback',
        },
        {
          name: 'Granular Permissions',
          href: '/granular-permissions',
          icon: <Lock className="h-5 w-5" />,
          description: 'Access control',
          badge: 'Pro',
        },
        {
          name: 'Slack Integration',
          href: '/slack-teams-integration',
          icon: <MessageSquare className="h-5 w-5" />,
          description: 'Connect with Slack/Teams',
        },
      ],
    },
    {
      title: 'EXPORT & PUBLISHING',
      items: [
        {
          name: 'Code Export',
          href: '/export',
          icon: <Code className="h-5 w-5" />,
          description: 'Export to code',
        },
        {
          name: 'Web Publishing',
          href: '/web-publishing',
          icon: <Globe className="h-5 w-5" />,
          description: '1-Click hosting',
          badge: 'New',
        },
        {
          name: 'Social Scheduler',
          href: '/social-scheduler',
          icon: <Share2 className="h-5 w-5" />,
          description: 'Auto-post designs',
          badge: 'New',
        },
        {
          name: 'PDF Export',
          href: '/pdf-export',
          icon: <FileDown className="h-5 w-5" />,
          description: 'Export to PDF',
        },
        {
          name: 'PDF Annotation',
          href: '/pdf-annotation',
          icon: <FileType className="h-5 w-5" />,
          description: 'Annotate PDFs',
        },
      ],
    },
    {
      title: 'INTEGRATIONS',
      items: [
        {
          name: 'Integrations Hub',
          href: '/integrations-hub',
          icon: <LinkIcon className="h-5 w-5" />,
          description: 'Connect tools',
        },
        {
          name: 'Advanced Integrations',
          href: '/advanced-integrations',
          icon: <Database className="h-5 w-5" />,
          description: 'API & webhooks',
          badge: 'Pro',
        },
        {
          name: 'Data Binding',
          href: '/data-binding',
          icon: <Database className="h-5 w-5" />,
          description: 'Dynamic data sources',
        },
        {
          name: 'Plugin Marketplace',
          href: '/plugin-marketplace',
          icon: <Plug className="h-5 w-5" />,
          description: 'Extend functionality',
        },
        {
          name: 'Mobile API',
          href: '/mobile-api',
          icon: <Smartphone className="h-5 w-5" />,
          description: 'Mobile SDK',
        },
      ],
    },
    {
      title: 'ANALYTICS & OPTIMIZATION',
      items: [
        {
          name: 'Analytics Dashboard',
          href: '/analytics-dashboard',
          icon: <BarChart3 className="h-5 w-5" />,
          description: 'Track performance',
        },
        {
          name: 'Design Analytics',
          href: '/design-analytics',
          icon: <Activity className="h-5 w-5" />,
          description: 'Design metrics',
        },
        {
          name: 'Optimization',
          href: '/optimization',
          icon: <Gauge className="h-5 w-5" />,
          description: 'Speed & SEO',
        },
        {
          name: 'Accessibility Testing',
          href: '/accessibility-testing',
          icon: <Eye className="h-5 w-5" />,
          description: 'WCAG compliance',
        },
        {
          name: 'Time Tracking',
          href: '/time-tracking',
          icon: <Clock className="h-5 w-5" />,
          description: 'Track project time',
        },
      ],
    },
    {
      title: 'PRODUCTIVITY',
      items: [
        {
          name: 'Advanced Search',
          href: '/advanced-search',
          icon: <Search className="h-5 w-5" />,
          description: 'Deep content search',
        },
        {
          name: 'Smart Tools',
          href: '/smart-tools',
          icon: <Lightbulb className="h-5 w-5" />,
          description: 'AI-powered helpers',
          badge: 'AI',
        },
        {
          name: 'Offline PWA',
          href: '/offline-pwa',
          icon: <WifiOff className="h-5 w-5" />,
          description: 'Work offline',
        },
        {
          name: 'Features Demo',
          href: '/features-demo',
          icon: <Play className="h-5 w-5" />,
          description: 'Learn capabilities',
        },
      ],
    },
    {
      title: 'AGENCY & WHITELABEL',
      items: [
        {
          name: 'Agency Mode',
          href: '/agency',
          icon: <Briefcase className="h-5 w-5" />,
          description: 'Client management',
        },
        {
          name: 'Whitelabel',
          href: '/whitelabel',
          icon: <Shield className="h-5 w-5" />,
          description: 'Custom branding',
          badge: 'Pro',
        },
      ],
    },
    {
      title: 'ACCOUNT',
      items: [
        {
          name: 'Settings',
          href: '/settings',
          icon: <Settings className="h-5 w-5" />,
          description: 'User preferences',
        },
        {
          name: 'Subscription',
          href: '/subscription',
          icon: <Zap className="h-5 w-5" />,
          description: 'Upgrade plan',
        },
        {
          name: 'Manage Billing',
          href: '/subscription-manage',
          icon: <CreditCard className="h-5 w-5" />,
          description: 'Invoices & cards',
        },
        {
          name: 'Help & Support',
          href: '/help',
          icon: <HelpCircle className="h-5 w-5" />,
          description: 'Get help',
        },
      ],
    },
  ];

  const toggleSection = (sectionTitle: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [sectionTitle.toLowerCase()]: !prev[sectionTitle.toLowerCase()],
    }));
  };

  const isActive = (href: string) => pathname === href || pathname.startsWith(href);

  const filteredSections = sections.map((section) => ({
    ...section,
    items: section.items.filter(
      (item) =>
        searchTerm === '' ||
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.description &&
          item.description.toLowerCase().includes(searchTerm.toLowerCase()))
    ),
  }));

  return (
    <div className="hidden lg:flex w-72 h-screen bg-linear-to-b from-white to-gray-50 border-r border-gray-200 flex-col sticky top-0 left-0 z-40 shadow-sm">
      {/* Header */}
      <div className="p-5 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-linear-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Layout className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Design Co.
            </h1>
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search features..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-10 bg-gray-50 border-gray-200 hover:border-gray-300 focus:border-blue-400 transition-colors"
          />
        </div>
      </div>

      {/* Create New Button */}
      <div className="px-5 py-4 border-b border-gray-200 bg-white">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button className="w-full bg-linear-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-md hover:shadow-lg transition-all" size="default">
              <Plus className="h-4 w-4 mr-2" />
              Create New Project
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-56">
            <DropdownMenuLabel>Create New Project</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=ui_ux')}>
              <Layout className="h-4 w-4 mr-3 text-blue-600" />
              <span>UI/UX Project</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=graphic')}>
              <Palette className="h-4 w-4 mr-3 text-purple-600" />
              <span>Graphic Design</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=logo')}>
              <Wand2 className="h-4 w-4 mr-3 text-pink-600" />
              <span>Logo Design</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Sidebar Content */}
      <ScrollArea className="flex-1">
        <div className="px-3 py-4 space-y-5">
          {filteredSections.map((section) => (
            section.items.length > 0 && (
              <div key={section.title}>
                <div
                  className="flex items-center justify-between px-3 mb-3 cursor-pointer group hover:bg-gray-100 rounded-md py-1.5 transition-colors"
                  onClick={() =>
                    toggleSection(section.title)
                  }
                >
                  <h3 className="text-xs font-bold text-gray-600 uppercase tracking-wider flex items-center gap-2">
                    {section.title}
                  </h3>
                  <ChevronDown
                    className={cn(
                      'h-4 w-4 text-gray-400 transition-transform',
                      expandedSections[section.title.toLowerCase()] &&
                      'transform rotate-180'
                    )}
                  />
                </div>

                {expandedSections[section.title.toLowerCase()] && (
                  <div className="space-y-0.5">
                    {section.items.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-all group relative',
                          isActive(item.href)
                            ? 'bg-linear-to-r from-blue-50 to-purple-50 text-blue-700 font-medium shadow-sm border border-blue-100'
                            : 'text-gray-700 hover:bg-gray-100 hover:shadow-sm'
                        )}
                      >
                        <div
                          className={cn(
                            'shrink-0 transition-colors',
                            isActive(item.href)
                              ? 'text-blue-600'
                              : 'text-gray-400 group-hover:text-gray-600'
                          )}
                        >
                          {item.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate text-sm">{item.name}</div>
                          {item.description && (
                            <div className="text-xs text-gray-500 truncate mt-0.5">
                              {item.description}
                            </div>
                          )}
                        </div>
                        {item.badge && (
                          <span className={cn(
                            "text-xs font-bold px-2 py-1 rounded-full shrink-0",
                            item.badge === 'AI' && "bg-linear-to-r from-purple-100 to-pink-100 text-purple-700",
                            item.badge === 'Pro' && "bg-linear-to-r from-amber-100 to-orange-100 text-amber-700",
                            item.badge === 'New' && "bg-linear-to-r from-green-100 to-emerald-100 text-green-700",
                            item.badge === 'Smart' && "bg-linear-to-r from-blue-100 to-cyan-100 text-blue-700"
                          )}>
                            {item.badge}
                          </span>
                        )}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            )
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4 space-y-2 bg-white">
        <Button
          variant="ghost"
          className="w-full justify-start text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors"
          size="sm"
        >
          <HelpCircle className="h-4 w-4 mr-3" />
          Keyboard Shortcuts
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors"
          size="sm"
          onClick={() => {
            // Handle logout
            router.push('/login');
          }}
        >
          <LogOut className="h-4 w-4 mr-3" />
          Sign Out
        </Button>
      </div>
    </div>
  );
}

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
    tools: true,
    resources: true,
    integrations: true,
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
          name: 'Templates',
          href: '/templates',
          icon: <LayoutTemplate className="h-5 w-5" />,
          description: 'Ready-to-use templates',
        },
        {
          name: 'Assets',
          href: '/assets',
          icon: <ImageIcon className="h-5 w-5" />,
          description: 'Media and graphics',
        },
        {
          name: 'Fonts',
          href: '/font-assets',
          icon: <Type className="h-5 w-5" />,
          description: 'Typography resources',
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
          name: 'Animation Studio',
          href: '/animation-studio',
          icon: <Zap className="h-5 w-5" />,
          description: 'Create animations',
        },
        {
          name: 'Social Scheduler',
          href: '/social-scheduler',
          icon: <Share2 className="h-5 w-5" />,
          description: 'Auto-post designs',
          badge: 'New',
        },
        {
          name: 'Web Publishing',
          href: '/web-publishing',
          icon: <Globe className="h-5 w-5" />,
          description: '1-Click Hosting',
          badge: 'New',
        },
        {
          name: 'Code Export',
          href: '/export',
          icon: <Code className="h-5 w-5" />,
          description: 'Export to code',
        },
        {
          name: 'AI Assistant',
          href: '/ai-assistant',
          icon: <Bot className="h-5 w-5" />,
          description: 'Chat and generate',
          badge: 'AI',
        },
        {
          name: '3D Studio',
          href: '/studio-3d',
          icon: <Box className="h-5 w-5" />,
          description: '3D modeling & render',
        },
        {
          name: 'Pro Editor',
          href: '/editor-v2',
          icon: <Edit3 className="h-5 w-5" />,
          description: 'Advanced canvas editor',
        },
        {
          name: 'Advanced Search',
          href: '/advanced-search',
          icon: <Search className="h-5 w-5" />,
          description: 'Deep content search',
        },
      ],
    },
    {
      title: 'RESOURCES & PLUGINS',
      items: [
        {
          name: 'Plugin Marketplace',
          href: '/plugin-marketplace',
          icon: <Plug className="h-5 w-5" />,
          description: 'Extend functionality',
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
      title: 'INTEGRATIONS & PERF',
      items: [
        {
          name: 'Integrations Hub',
          href: '/integrations-hub',
          icon: <Database className="h-5 w-5" />,
          description: 'Connect tools',
        },
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
          name: 'Analytics',
          href: '/analytics-dashboard',
          icon: <BarChart3 className="h-5 w-5" />,
          description: 'Track performance',
        },
        {
          name: 'Optimization',
          href: '/optimization',
          icon: <Gauge className="h-5 w-5" />,
          description: 'Speed & SEO',
        },
        {
          name: 'Agency Mode',
          href: '/agency',
          icon: <Briefcase className="h-5 w-5" />,
          description: 'Whitelabel & clients',
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
    <div className="hidden lg:flex w-64 h-screen bg-white border-r border-gray-200 flex-col sticky top-0 left-0 z-40">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-bold text-gray-900">Design Co.</h1>
        </div>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-500" />
          <Input
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8 h-9 bg-gray-50 border-gray-200"
          />
        </div>
      </div>

      {/* Create New Button */}
      <div className="px-4 py-3 border-b border-gray-200">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white" size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create New
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-48">
            <DropdownMenuLabel>Create New Project</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=ui_ux')}>
              <Layout className="h-4 w-4 mr-2" />
              <span>UI/UX Project</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=graphic')}>
              <Palette className="h-4 w-4 mr-2" />
              <span>Graphic Design</span>
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => router.push('/dashboard?newProject=logo')}>
              <Wand2 className="h-4 w-4 mr-2" />
              <span>Logo Design</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Sidebar Content */}
      <ScrollArea className="flex-1">
        <div className="px-2 py-4 space-y-4">
          {filteredSections.map((section) => (
            section.items.length > 0 && (
              <div key={section.title}>
                <div
                  className="flex items-center justify-between px-2 mb-2 cursor-pointer"
                  onClick={() =>
                    toggleSection(section.title)
                  }
                >
                  <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
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
                  <div className="space-y-1">
                    {section.items.map((item) => (
                      <Link
                        key={item.href}
                        href={item.href}
                        className={cn(
                          'flex items-center gap-3 px-3 py-2.5 text-sm rounded-lg transition-colors group relative',
                          isActive(item.href)
                            ? 'bg-blue-50 text-blue-700 font-medium'
                            : 'text-gray-700 hover:bg-gray-50'
                        )}
                      >
                        <div
                          className={cn(
                            'flex-shrink-0',
                            isActive(item.href)
                              ? 'text-blue-600'
                              : 'text-gray-400 group-hover:text-gray-600'
                          )}
                        >
                          {item.icon}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{item.name}</div>
                          {item.description && (
                            <div className="text-xs text-gray-500 truncate">
                              {item.description}
                            </div>
                          )}
                        </div>
                        {item.badge && (
                          <span className="text-xs font-semibold px-2 py-1 bg-purple-100 text-purple-700 rounded-full flex-shrink-0">
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
      <div className="border-t border-gray-200 p-4 space-y-2">
        <Button
          variant="ghost"
          className="w-full justify-start text-gray-700 hover:bg-gray-50"
          size="sm"
        >
          <HelpCircle className="h-4 w-4 mr-2" />
          Keyboard Shortcuts
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start text-red-600 hover:bg-red-50"
          size="sm"
          onClick={() => {
            // Handle logout
            router.push('/login');
          }}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign Out
        </Button>
      </div>
    </div>
  );
}

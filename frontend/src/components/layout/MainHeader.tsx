"use client";

import React from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Home,
  Palette,
  FileImage,
  Layout,
  Search,
  BarChart3,
  Settings,
  Users,
  Bell,
  Zap,
  Globe,
  Code,
  Layers,
  Sparkles,
  Database,
  ShoppingCart,
  User,
  LogOut,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Main dashboard'
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FileImage,
    description: 'Manage your projects'
  },
  {
    name: 'Editor',
    href: '/editor',
    icon: Palette,
    description: 'Design editor'
  },
  {
    name: 'Templates',
    href: '/templates',
    icon: Layout,
    description: 'Browse templates'
  },
  {
    name: 'Search',
    href: '/search',
    icon: Search,
    description: 'Advanced search'
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    description: 'View analytics'
  },
  {
    name: 'AI Assistant',
    href: '/ai-assistant',
    icon: Sparkles,
    description: 'AI-powered assistance'
  },
  {
    name: 'Teams',
    href: '/teams',
    icon: Users,
    description: 'Team collaboration'
  },
  {
    name: 'Assets',
    href: '/assets',
    icon: Database,
    description: 'Asset management'
  },
  {
    name: 'Integrations',
    href: '/integrations-hub',
    icon: Globe,
    description: 'Third-party integrations'
  },
  {
    name: 'Plugins',
    href: '/plugin-marketplace',
    icon: Code,
    description: 'Plugin marketplace'
  },
  {
    name: 'Design System',
    href: '/design-system',
    icon: Layers,
    description: 'Design system'
  },
  {
    name: 'Animation Studio',
    href: '/animation-studio',
    icon: Zap,
    description: 'Animation tools'
  },
  {
    name: '3D Studio',
    href: '/studio-3d',
    icon: Layers,
    description: '3D design tools'
  },
  {
    name: 'Font Assets',
    href: '/font-assets',
    icon: FileImage,
    description: 'Font management'
  },
  {
    name: 'Optimization',
    href: '/optimization',
    icon: Zap,
    description: 'Performance optimization'
  },
  {
    name: 'Export',
    href: '/export',
    icon: FileImage,
    description: 'Export tools'
  },
  {
    name: 'Subscription',
    href: '/subscription',
    icon: ShoppingCart,
    description: 'Manage subscription'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'Application settings'
  }
];

export function MainHeader() {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('token');
    router.push('/login');
  };

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-linear-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Palette className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">AI Design Tool</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex space-x-1">
            {navigationItems.slice(0, 8).map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}

            {/* More dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2 px-3 py-2">
                  <Menu className="w-4 h-4" />
                  <span>More</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Additional Tools</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {navigationItems.slice(8).map((item) => {
                  const Icon = item.icon;
                  return (
                    <DropdownMenuItem
                      key={item.href}
                      onClick={() => router.push(item.href)}
                      className="flex items-center space-x-2"
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </DropdownMenuItem>
                  );
                })}
              </DropdownMenuContent>
            </DropdownMenu>
          </nav>

          {/* Right side actions */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </Button>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src="/avatars/01.png" alt="User" />
                    <AvatarFallback>JD</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">John Doe</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      john@example.com
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => router.push('/settings')}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/subscription')}>
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  <span>Subscription</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => router.push('/teams')}>
                  <Users className="mr-2 h-4 w-4" />
                  <span>Teams</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200 py-4">
            <nav className="grid grid-cols-2 gap-2">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-blue-50 text-blue-700 border border-blue-200'
                        : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}
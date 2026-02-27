"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import {
  Home,
  FileText,
  Layout,
  BarChart3,
  Menu,
  X,
} from 'lucide-react';

interface MobileNavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: MobileNavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: <Home className="h-5 w-5" />,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: <FileText className="h-5 w-5" />,
  },
  {
    name: 'Design Hub',
    href: '/design-hub',
    icon: <Layout className="h-5 w-5" />,
  },
  {
    name: 'Analytics',
    href: '/analytics-dashboard',
    icon: <BarChart3 className="h-5 w-5" />,
  },
];

export function MobileNavigation() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) => pathname === href;

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-64 p-0">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-gray-900">Design Co.</h1>
          </div>

          {/* Navigation Items */}
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
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
                      : 'text-gray-400'
                  )}
                >
                  {item.icon}
                </div>
                <span>{item.name}</span>
              </Link>
            ))}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

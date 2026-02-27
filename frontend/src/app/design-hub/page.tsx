'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function DesignHubPage() {
  const [activeNav, setActiveNav] = useState('home');

  return (
    <div className="flex h-screen w-full bg-[#f6f6f8] dark:bg-[#101622]">
      {/* Sidebar */}
      <aside className="flex w-72 flex-col justify-between border-r border-slate-200 dark:border-[#232f48] bg-[#111722] p-4 flex-shrink-0 z-20 overflow-y-auto">
        <div className="flex flex-col gap-8">
          {/* Brand */}
          <div className="flex items-center gap-3 px-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-linear-to-br from-[#2b6cee] to-[#8b5cf6] shadow-lg shadow-[#2b6cee]/20">
              <span className="material-symbols-outlined text-white text-2xl">design_services</span>
            </div>
            <div className="flex flex-col">
              <h1 className="text-white text-lg font-bold leading-none tracking-tight">Design Hub</h1>
              <p className="text-slate-400 text-xs font-medium">Pro Workspace</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex flex-col gap-1">
            <div className="px-3 pb-2 pt-1 text-xs font-semibold uppercase tracking-wider text-slate-500">Menu</div>
            
            <NavLink
              href="/design-hub"
              icon="home"
              label="Home"
              active={activeNav === 'home'}
              onClick={() => setActiveNav('home')}
            />
            
            <NavLink
              href="/projects"
              icon="folder_open"
              label="All Projects"
              active={activeNav === 'projects'}
              onClick={() => setActiveNav('projects')}
            />
            
            <NavLink
              href="/brand-kits"
              icon="palette"
              label="Brand Kits"
              active={activeNav === 'brand-kits'}
              onClick={() => setActiveNav('brand-kits')}
            />
            
            <NavLink
              href="/templates"
              icon="grid_view"
              label="Templates"
              active={activeNav === 'templates'}
              onClick={() => setActiveNav('templates')}
            />

            <div className="px-3 pb-2 pt-6 text-xs font-semibold uppercase tracking-wider text-slate-500">AI Tools</div>
            
            <NavLink
              href="/ai-uiux-generator"
              icon="auto_awesome"
              label="AI Generators"
              active={activeNav === 'ai-generators'}
              onClick={() => setActiveNav('ai-generators')}
              iconColor="text-[#06b6d4]"
            />
            
            <NavLink
              href="/ai-logo-designer"
              icon="smart_toy"
              label="Logo AI"
              active={activeNav === 'logo-ai'}
              onClick={() => setActiveNav('logo-ai')}
              iconColor="text-[#ec4899]"
            />
          </nav>
        </div>

        <div className="flex flex-col gap-4">
          {/* CTA */}
          <button className="flex w-full items-center justify-center gap-2 rounded-lg bg-linear-to-r from-[#2b6cee] to-blue-600 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition-all hover:shadow-blue-500/40 hover:-translate-y-0.5">
            <span className="material-symbols-outlined text-xl">add</span>
            New Design
          </button>

          {/* Bottom Actions */}
          <div className="flex flex-col gap-1 border-t border-slate-800 pt-4">
            <Link href="/settings" className="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-400 hover:bg-[#232f48] hover:text-white transition-colors">
              <span className="material-symbols-outlined text-xl">settings</span>
              <span className="text-sm font-medium">Settings</span>
            </Link>
            <Link href="/help" className="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-400 hover:bg-[#232f48] hover:text-white transition-colors">
              <span className="material-symbols-outlined text-xl">help</span>
              <span className="text-sm font-medium">Help Center</span>
            </Link>
          </div>

          {/* User Profile */}
          <div className="mt-2 flex items-center gap-3 rounded-xl bg-[#1a2332] p-2 border border-slate-800">
            <div className="h-9 w-9 rounded-lg bg-linear-to-br from-purple-500 to-pink-500" />
            <div className="flex flex-col overflow-hidden">
              <span className="truncate text-sm font-medium text-white">Alex Morgan</span>
              <span className="text-xs text-slate-400">alex@design.pro</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {/* Top Header */}
        <header className="flex items-center justify-between border-b border-slate-200 dark:border-[#232f48] bg-white dark:bg-[#111722] px-6 py-4 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h2>
          </div>
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span className="material-symbols-outlined text-slate-600 dark:text-slate-400">search</span>
            </button>
            <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative">
              <span className="material-symbols-outlined text-slate-600 dark:text-slate-400">notifications</span>
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="p-6 space-y-6">
          {/* Quick Actions */}
          <section>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Quick Start</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <QuickActionCard
                icon="draw"
                title="Blank Canvas"
                description="Start from scratch"
                gradient="from-blue-500 to-cyan-500"
              />
              <QuickActionCard
                icon="auto_awesome"
                title="AI Generator"
                description="Let AI create for you"
                gradient="from-purple-500 to-pink-500"
              />
              <QuickActionCard
                icon="grid_view"
                title="Use Template"
                description="Browse templates"
                gradient="from-orange-500 to-red-500"
              />
              <QuickActionCard
                icon="upload"
                title="Import"
                description="Upload your files"
                gradient="from-green-500 to-emerald-500"
              />
            </div>
          </section>

          {/* Recent Projects */}
          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Recent Projects</h3>
              <Link href="/projects" className="text-sm text-[#2b6cee] hover:underline">
                View all
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <ProjectCard key={i} index={i} />
              ))}
            </div>
          </section>

          {/* Activity Feed */}
          <section>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Recent Activity</h3>
            <div className="bg-white dark:bg-[#1a2332] rounded-xl border border-slate-200 dark:border-[#232f48] p-4 space-y-3">
              <ActivityItem
                action="Created new project"
                name="Mobile App Design"
                time="2 hours ago"
                icon="add_circle"
              />
              <ActivityItem
                action="Updated"
                name="Logo Concepts V2"
                time="5 hours ago"
                icon="edit"
              />
              <ActivityItem
                action="Shared"
                name="Brand Guidelines"
                time="Yesterday"
                icon="share"
              />
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

// Helper Components
function NavLink({
  href,
  icon,
  label,
  active,
  onClick,
  iconColor = ''
}: {
  href: string;
  icon: string;
  label: string;
  active?: boolean;
  onClick?: () => void;
  iconColor?: string;
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={`group flex items-center gap-3 rounded-lg px-3 py-2.5 transition-all ${
        active
          ? 'bg-[#232f48] text-white shadow-lg'
          : 'text-slate-400 hover:bg-[#232f48] hover:text-white'
      }`}
    >
      <span className={`material-symbols-outlined text-xl ${iconColor || (active ? 'text-white' : '')}`}>
        {icon}
      </span>
      <span className="text-sm font-medium">{label}</span>
    </Link>
  );
}

function QuickActionCard({
  icon,
  title,
  description,
  gradient
}: {
  icon: string;
  title: string;
  description: string;
  gradient: string;
}) {
  return (
    <button className="flex flex-col items-start p-6 rounded-xl border border-slate-200 dark:border-[#232f48] bg-white dark:bg-[#1a2332] hover:scale-105 transition-transform cursor-pointer group">
      <div className={`flex items-center justify-center w-12 h-12 rounded-lg bg-linear-to-br ${gradient} mb-4 shadow-lg`}>
        <span className="material-symbols-outlined text-white text-2xl">{icon}</span>
      </div>
      <h4 className="text-base font-semibold text-slate-900 dark:text-white mb-1">{title}</h4>
      <p className="text-sm text-slate-500 dark:text-slate-400">{description}</p>
    </button>
  );
}

function ProjectCard({ index }: { index: number }) {
  const colors = ['bg-blue-500', 'bg-purple-500', 'bg-pink-500', 'bg-green-500'];
  return (
    <div className="group cursor-pointer">
      <div className={`aspect-video rounded-lg ${colors[index - 1]} mb-3 flex items-center justify-center text-white font-semibold text-xl hover:scale-105 transition-transform`}>
        Project {index}
      </div>
      <h4 className="text-sm font-medium text-slate-900 dark:text-white mb-1">Design Project {index}</h4>
      <p className="text-xs text-slate-500 dark:text-slate-400">Modified 2 days ago</p>
    </div>
  );
}

function ActivityItem({
  action,
  name,
  time,
  icon
}: {
  action: string;
  name: string;
  time: string;
  icon: string;
}) {
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800">
        <span className="material-symbols-outlined text-sm text-slate-600 dark:text-slate-400">{icon}</span>
      </div>
      <div className="flex-1">
        <p className="text-sm text-slate-900 dark:text-white">
          {action} <span className="font-medium">{name}</span>
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400">{time}</p>
      </div>
    </div>
  );
}

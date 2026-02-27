'use client';

import { useState } from 'react';

export default function AIUIUXGeneratorPage() {
  const [prompt, setPrompt] = useState('');
  const [selectedScreen, setSelectedScreen] = useState<number | null>(null);

  return (
    <div className="h-screen flex flex-col bg-[#f6f6f8] dark:bg-[#101622] text-slate-900 dark:text-slate-100">
      {/* Top Navigation Bar */}
      <header className="flex shrink-0 items-center justify-between border-b border-[#e5e7eb] dark:border-[#232f48] bg-white dark:bg-[#111722] px-4 py-2 select-none z-50">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-[#2b6cee]">
            <span className="material-symbols-outlined text-3xl">token</span>
            <h2 className="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-tight">
              DesignAI Studio
            </h2>
          </div>
          <div className="h-6 w-px bg-[#e5e7eb] dark:bg-[#232f48] mx-2" />
          <div className="flex items-center gap-1">
            <button className="px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-xs font-medium text-slate-600 dark:text-slate-400">
              File
            </button>
            <button className="px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-xs font-medium text-slate-600 dark:text-slate-400">
              Edit
            </button>
            <button className="px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-xs font-medium text-slate-600 dark:text-slate-400">
              View
            </button>
            <button className="px-3 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded text-xs font-medium text-slate-600 dark:text-slate-400">
              Plugins
            </button>
          </div>
        </div>

        <div className="flex flex-1 justify-center max-w-xl mx-4">
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-[#1a2332] rounded-md px-3 py-1.5 w-full border border-transparent focus-within:border-[#2b6cee] transition-colors">
            <span className="material-symbols-outlined text-slate-400 text-[18px]">search</span>
            <input
              className="bg-transparent border-none outline-none text-xs w-full text-slate-700 dark:text-slate-200 placeholder-slate-400 focus:ring-0 p-0"
              placeholder="Search commands, layers, or assets..."
              type="text"
            />
            <span className="text-[10px] text-slate-400 border border-slate-300 dark:border-slate-600 rounded px-1">
              ⌘K
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex -space-x-2 overflow-hidden">
            <div className="inline-block h-8 w-8 rounded-full ring-2 ring-white dark:ring-[#111722] bg-linear-to-br from-purple-500 to-pink-500" />
            <div className="inline-block h-8 w-8 rounded-full ring-2 ring-white dark:ring-[#111722] bg-linear-to-br from-blue-500 to-cyan-500" />
            <div className="flex h-8 w-8 items-center justify-center rounded-full ring-2 ring-white dark:ring-[#111722] bg-slate-100 dark:bg-slate-700 text-xs font-medium text-slate-500 dark:text-slate-300">
              +3
            </div>
          </div>
          <button className="flex items-center gap-2 bg-[#2b6cee] hover:bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-colors">
            <span className="material-symbols-outlined text-[18px]">share</span>
            <span>Share</span>
          </button>
          <div className="h-8 w-px bg-[#e5e7eb] dark:bg-[#232f48] mx-1" />
          <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg text-slate-600 dark:text-slate-400 transition-colors">
            <span className="material-symbols-outlined text-[20px]">play_arrow</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Area */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar: Prompt & History */}
        <aside className="w-80 flex flex-col border-r border-[#e5e7eb] dark:border-[#232f48] bg-white dark:bg-[#111722] z-20 shrink-0">
          {/* Project Info */}
          <div className="p-4 border-b border-[#e5e7eb] dark:border-[#232f48]">
            <h1 className="text-base font-semibold text-slate-900 dark:text-white mb-1">Finance App V1</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Last edited 5 minutes ago</p>
          </div>

          {/* AI Prompt Section */}
          <div className="p-4 border-b border-[#e5e7eb] dark:border-[#232f48]">
            <label className="text-sm font-medium text-slate-900 dark:text-white mb-2 block">
              AI Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the UI you want to generate..."
              rows={4}
              className="w-full px-3 py-2 rounded-lg bg-slate-50 dark:bg-[#192233] border border-slate-200 dark:border-[#232f48] text-slate-900 dark:text-white placeholder-slate-400 text-sm focus:border-[#2b6cee] focus:ring-2 focus:ring-[#2b6cee]/20 transition-all outline-none resize-none"
            />
            <button className="w-full mt-3 py-2.5 rounded-lg bg-linear-to-r from-[#2b6cee] to-[#8b5cf6] text-white font-semibold text-sm shadow-lg shadow-[#2b6cee]/30 hover:shadow-[#2b6cee]/50 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-lg">auto_awesome</span>
              Generate UI
            </button>
          </div>

          {/* Generation History */}
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">
              Generation History
            </h3>
            <div className="space-y-2">
              {[
                { title: 'Login Screen', time: 'Just now', screens: 3 },
                { title: 'Dashboard', time: '5 min ago', screens: 5 },
                { title: 'Profile Page', time: '1 hour ago', screens: 2 },
                { title: 'Settings', time: '2 hours ago', screens: 4 }
              ].map((item, i) => (
                <HistoryItem key={i} {...item} />
              ))}
            </div>
          </div>

          {/* Quick Settings */}
          <div className="p-4 border-t border-[#e5e7eb] dark:border-[#232f48] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Style</span>
              <select className="text-xs bg-slate-100 dark:bg-[#192233] border border-slate-200 dark:border-[#232f48] rounded px-2 py-1 text-slate-900 dark:text-white">
                <option>Modern</option>
                <option>Classic</option>
                <option>Minimal</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Platform</span>
              <select className="text-xs bg-slate-100 dark:bg-[#192233] border border-slate-200 dark:border-[#232f48] rounded px-2 py-1 text-slate-900 dark:text-white">
                <option>Web</option>
                <option>Mobile</option>
                <option>Desktop</option>
              </select>
            </div>
          </div>
        </aside>

        {/* Center Canvas Area */}
        <main className="flex-1 flex flex-col bg-slate-50 dark:bg-[#101622] relative overflow-hidden">
          {/* Canvas Grid Background */}
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: 'radial-gradient(#232f48 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }} />

          {/* Canvas Content */}
          <div className="relative z-10 flex-1 overflow-auto p-12">
            <div className="max-w-6xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((screen) => (
                  <ScreenPreview
                    key={screen}
                    index={screen}
                    selected={selectedScreen === screen}
                    onClick={() => setSelectedScreen(screen)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Canvas Toolbar */}
          <div className="border-t border-[#e5e7eb] dark:border-[#232f48] bg-white dark:bg-[#111722] p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ToolButton icon="pan_tool" label="Hand" />
                <ToolButton icon="square" label="Frame" />
                <ToolButton icon="crop_square" label="Rectangle" />
                <ToolButton icon="circle" label="Ellipse" />
                <ToolButton icon="edit" label="Text" />
              </div>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                  <span className="material-symbols-outlined text-sm">remove</span>
                </button>
                <span className="text-xs text-slate-600 dark:text-slate-400">100%</span>
                <button className="px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white">
                  <span className="material-symbols-outlined text-sm">add</span>
                </button>
              </div>
            </div>
          </div>
        </main>

        {/* Right Sidebar: Properties */}
        <aside className="w-80 flex flex-col border-l border-[#e5e7eb] dark:border-[#232f48] bg-white dark:bg-[#111722] z-20 shrink-0 overflow-y-auto">
          <div className="p-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
              {selectedScreen ? 'Design Properties' : 'No Selection'}
            </h3>

            {selectedScreen ? (
              <div className="space-y-4">
                {/* Layers */}
                <div>
                  <h4 className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Layers</h4>
                  <div className="space-y-1">
                    {['Header', 'Content', 'Card 1', 'Card 2', 'Footer'].map((layer, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-100 dark:hover:bg-[#192233] cursor-pointer text-sm text-slate-700 dark:text-slate-300"
                      >
                        <span className="material-symbols-outlined text-xs text-slate-400">layers</span>
                        {layer}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Spacing */}
                <div>
                  <h4 className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Spacing</h4>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      placeholder="Width"
                      className="px-2 py-1.5 text-xs rounded bg-slate-50 dark:bg-[#192233] border border-slate-200 dark:border-[#232f48] text-slate-900 dark:text-white"
                    />
                    <input
                      type="number"
                      placeholder="Height"
                      className="px-2 py-1.5 text-xs rounded bg-slate-50 dark:bg-[#192233] border border-slate-200 dark:border-[#232f48] text-slate-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* Colors */}
                <div>
                  <h4 className="text-xs font-medium text-slate-600 dark:text-slate-400 mb-2">Colors</h4>
                  <div className="space-y-2">
                    <ColorPicker label="Background" color="#ffffff" />
                    <ColorPicker label="Text" color="#000000" />
                    <ColorPicker label="Accent" color="#2b6cee" />
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Select a screen to view its properties
              </p>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

function HistoryItem({ title, time, screens }: { title: string; time: string; screens: number }) {
  return (
    <button className="w-full p-3 rounded-lg border border-slate-200 dark:border-border-dark bg-slate-50 dark:bg-surface-dark hover:border-primary transition-colors text-left">
      <div className="flex items-center justify-between mb-1">
        <h4 className="text-sm font-medium text-slate-900 dark:text-white">{title}</h4>
        <span className="text-xs text-slate-500 dark:text-slate-400">{screens} screens</span>
      </div>
      <p className="text-xs text-slate-500 dark:text-slate-400">{time}</p>
    </button>
  );
}

function ScreenPreview({
  index,
  selected,
  onClick
}: {
  index: number;
  selected: boolean;
  onClick: () => void;
}) {
  const gradients = [
    'from-blue-500 to-cyan-500',
    'from-purple-500 to-pink-500',
    'from-orange-500 to-red-500',
    'from-green-500 to-emerald-500',
    'from-indigo-500 to-purple-500',
    'from-pink-500 to-rose-500'
  ];

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer group ${selected ? 'ring-2 ring-primary' : ''} rounded-lg`}
    >
      <div
        className={`aspect-3/4 rounded-lg bg-linear-to-br ${gradients[index - 1]} p-4 flex flex-col gap-2 hover:scale-105 transition-transform shadow-lg`}
      >
        <div className="h-8 bg-white/20 backdrop-blur-sm rounded" />
        <div className="flex-1 bg-white/10 backdrop-blur-sm rounded" />
        <div className="h-6 bg-white/20 backdrop-blur-sm rounded" />
      </div>
      <p className="text-sm font-medium text-slate-900 dark:text-white mt-2">Screen {index}</p>
    </div>
  );
}

function ToolButton({ icon, label }: { icon: string; label: string }) {
  return (
    <button className="p-2 rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors group relative">
      <span className="material-symbols-outlined text-sm text-slate-600 dark:text-slate-400 group-hover:text-slate-900 dark:group-hover:text-white">
        {icon}
      </span>
      <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 text-xs bg-slate-900 text-white rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        {label}
      </span>
    </button>
  );
}

function ColorPicker({ label, color }: { label: string; color: string }) {
  const [currentColor, setCurrentColor] = useState(color);

  const handleColorChange = (newColor: string) => {
    setCurrentColor(newColor);
  };

  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-600 dark:text-slate-400">{label}</span>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={currentColor}
          onChange={(e) => handleColorChange(e.target.value)}
          className="w-8 h-8 rounded border border-slate-200 dark:border-border-dark cursor-pointer"
        />
        <input
          type="text"
          value={currentColor}
          onChange={(e) => handleColorChange(e.target.value)}
          className="w-20 px-2 py-1 text-xs rounded bg-slate-50 dark:bg-surface-dark border border-slate-200 dark:border-border-dark text-slate-900 dark:text-white"
        />
      </div>
    </div>
  );
}

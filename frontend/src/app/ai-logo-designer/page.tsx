'use client';

import { useState } from 'react';

export default function AILogoDesignerPage() {
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [style, setStyle] = useState('modern');
  const [colors, setColors] = useState<string[]>([]);
  const [generatedLogos, setGeneratedLogos] = useState<number[]>([]);

  const handleGenerate = () => {
    // Simulate AI generation
    setGeneratedLogos([1, 2, 3, 4, 5, 6]);
  };

  return (
    <div className="h-screen flex flex-col bg-[#f6f6f8] dark:bg-[#101622]">
      {/* Top Navigation Bar */}
      <header className="flex items-center justify-between border-b border-[#232f48] bg-[#111722] px-6 py-3 shrink-0 z-20">
        <div className="flex items-center gap-4 text-white">
          <div className="size-8 flex items-center justify-center rounded-lg bg-[#2b6cee]/20 text-[#2b6cee]">
            <span className="material-symbols-outlined text-2xl">design_services</span>
          </div>
          <h2 className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">LogoGen AI</h2>
        </div>

        {/* Center Action Bar */}
        <div className="hidden md:flex items-center bg-[#192233] rounded-lg p-1 border border-[#232f48]">
          <button className="px-4 py-1.5 rounded bg-[#2b6cee] text-white text-sm font-medium shadow-sm">
            Design
          </button>
          <button className="px-4 py-1.5 rounded text-[#92a4c9] hover:text-white text-sm font-medium transition-colors">
            Prototype
          </button>
          <button className="px-4 py-1.5 rounded text-[#92a4c9] hover:text-white text-sm font-medium transition-colors">
            Code
          </button>
        </div>

        <div className="flex flex-1 justify-end gap-4">
          <div className="flex gap-2">
            <button className="flex items-center justify-center rounded-lg size-10 bg-[#192233] text-white hover:bg-[#232f48] transition-colors border border-[#232f48]">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="flex items-center justify-center rounded-lg h-10 px-4 bg-[#2b6cee] hover:bg-blue-600 text-white gap-2 text-sm font-bold transition-colors shadow-lg shadow-[#2b6cee]/20">
              <span className="material-symbols-outlined text-lg">ios_share</span>
              <span className="truncate">Export</span>
            </button>
          </div>
          <div className="bg-linear-to-br from-purple-500 to-pink-500 rounded-full size-10 border-2 border-[#192233] ring-2 ring-[#232f48]" />
        </div>
      </header>

      {/* Main Content Area: Split Screen */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Sidebar: AI Generator Panel */}
        <aside className="w-full md:w-[400px] lg:w-[450px] flex flex-col border-r border-[#232f48] bg-[#111722] overflow-y-auto z-10 shadow-xl shrink-0">
          <div className="p-6 space-y-8">
            {/* Header Section */}
            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">Create New Logo</h1>
              <p className="text-[#92a4c9] text-sm">
                Define your brand identity and let AI generate unique concepts.
              </p>
            </div>

            {/* Form Section */}
            <div className="space-y-6">
              {/* Company Name */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white">Company Name</label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Enter your company name"
                  className="w-full px-4 py-3 rounded-lg bg-[#192233] border border-[#324467] text-white placeholder-[#92a4c9] focus:border-[#2b6cee] focus:ring-2 focus:ring-[#2b6cee]/20 transition-all outline-none"
                />
              </div>

              {/* Industry */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-white">Industry</label>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg bg-[#192233] border border-[#324467] text-white focus:border-[#2b6cee] focus:ring-2 focus:ring-[#2b6cee]/20 transition-all outline-none"
                >
                  <option value="">Select industry</option>
                  <option value="technology">Technology</option>
                  <option value="finance">Finance</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="education">Education</option>
                  <option value="retail">Retail</option>
                  <option value="food">Food & Beverage</option>
                </select>
              </div>

              {/* Style Selection */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Logo Style</label>
                <div className="grid grid-cols-2 gap-3">
                  {['modern', 'classic', 'minimal', 'playful'].map((s) => (
                    <button
                      key={s}
                      onClick={() => setStyle(s)}
                      className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        style === s
                          ? 'border-[#2b6cee] bg-[#2b6cee]/10 text-white'
                          : 'border-[#324467] bg-[#192233] text-[#92a4c9] hover:border-[#2b6cee]/50'
                      }`}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Color Palette */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Preferred Colors</label>
                <div className="grid grid-cols-6 gap-2">
                  {['#2b6cee', '#8b5cf6', '#ec4899', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#6366f1'].map(
                    (color) => (
                      <button
                        key={color}
                        onClick={() => {
                          if (colors.includes(color)) {
                            setColors(colors.filter((c) => c !== color));
                          } else {
                            setColors([...colors, color]);
                          }
                        }}
                        className={`w-full aspect-square rounded-lg border-2 transition-all ${
                          colors.includes(color)
                            ? 'border-white scale-110'
                            : 'border-[#324467] hover:scale-105'
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    )
                  )}
                </div>
              </div>

              {/* Additional Options */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Additional Preferences</label>
                <textarea
                  placeholder="Describe your vision (optional)"
                  rows={4}
                  className="w-full px-4 py-3 rounded-lg bg-[#192233] border border-[#324467] text-white placeholder-[#92a4c9] focus:border-[#2b6cee] focus:ring-2 focus:ring-[#2b6cee]/20 transition-all outline-none resize-none"
                />
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                className="w-full py-4 rounded-lg bg-linear-to-r from-[#2b6cee] to-[#8b5cf6] text-white font-bold text-base shadow-lg shadow-[#2b6cee]/30 hover:shadow-[#2b6cee]/50 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined">auto_awesome</span>
                Generate Logo Concepts
              </button>
            </div>
          </div>
        </aside>

        {/* Right Side: Canvas/Preview Area */}
        <main className="flex-1 flex flex-col bg-[#101622] relative overflow-hidden">
          {/* Canvas Grid Background */}
          <div className="absolute inset-0 opacity-30" style={{
            backgroundImage: 'radial-gradient(#324467 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }} />

          <div className="relative z-10 flex-1 overflow-y-auto p-8">
            {generatedLogos.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-24 h-24 rounded-full bg-[#192233] flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-5xl text-[#92a4c9]">
                    palette
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Ready to Create Your Logo</h3>
                <p className="text-[#92a4c9] max-w-md">
                  Fill in the details on the left and click Generate to see AI-powered logo concepts
                </p>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-white mb-2">Generated Concepts</h3>
                  <p className="text-[#92a4c9] text-sm">
                    Click on any logo to edit and customize
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {generatedLogos.map((logo) => (
                    <LogoCard key={logo} index={logo} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Toolbar */}
          <div className="border-t border-[#232f48] bg-[#111722] p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 rounded bg-[#192233] text-white text-sm hover:bg-[#232f48] transition-colors border border-[#232f48]">
                  <span className="material-symbols-outlined text-sm">undo</span>
                </button>
                <button className="px-3 py-1.5 rounded bg-[#192233] text-white text-sm hover:bg-[#232f48] transition-colors border border-[#232f48]">
                  <span className="material-symbols-outlined text-sm">redo</span>
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-[#92a4c9]">Zoom:</span>
                <button className="px-3 py-1.5 rounded bg-[#192233] text-white text-sm hover:bg-[#232f48] transition-colors border border-[#232f48]">
                  100%
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

function LogoCard({ index }: { index: number }) {
  const colors = [
    'from-blue-500 to-cyan-500',
    'from-purple-500 to-pink-500',
    'from-orange-500 to-red-500',
    'from-green-500 to-emerald-500',
    'from-indigo-500 to-purple-500',
    'from-pink-500 to-rose-500'
  ];

  return (
    <div className="group cursor-pointer">
      <div className={`aspect-square rounded-xl bg-linear-to-br ${colors[index - 1]} p-8 flex items-center justify-center mb-3 hover:scale-105 transition-transform shadow-lg`}>
        <div className="w-full h-full bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-3xl">L{index}</span>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-medium text-white">Concept {index}</h4>
          <p className="text-xs text-[#92a4c9]">AI Generated</p>
        </div>
        <button className="p-1.5 rounded hover:bg-[#192233] transition-colors">
          <span className="material-symbols-outlined text-sm text-[#92a4c9]">more_horiz</span>
        </button>
      </div>
    </div>
  );
}

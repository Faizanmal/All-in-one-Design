'use client';

import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { aiAPI, projectsAPI } from '@/lib/design-api';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface LogoConcept {
  id: string;
  label: string;
  style: string;
  components: Record<string, unknown>[];
  metadata?: Record<string, unknown>;
}

const STYLE_GRADIENTS = [
  'from-blue-500 to-cyan-500',
  'from-purple-500 to-pink-500',
  'from-orange-500 to-red-500',
  'from-green-500 to-emerald-500',
  'from-indigo-500 to-purple-500',
  'from-pink-500 to-rose-500',
];

export default function AILogoDesignerPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [companyName, setCompanyName] = useState('');
  const [industry, setIndustry] = useState('');
  const [style, setStyle] = useState('modern');
  const [colors, setColors] = useState<string[]>([]);
  const [vision, setVision] = useState('');
  const [generatedLogos, setGeneratedLogos] = useState<LogoConcept[]>([]);
  const [loading, setLoading] = useState(false);
  const [openingId, setOpeningId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selectedConcept = useMemo(
    () => generatedLogos.find((logo) => logo.id === selectedId) || null,
    [generatedLogos, selectedId]
  );

  const handleGenerate = async () => {
    if (!companyName.trim()) {
      toast({
        title: 'Company name required',
        description: 'Enter a company name to generate logo concepts.',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    setSelectedId(null);

    try {
      const baseParams = {
        company_name: companyName.trim(),
        industry: industry || undefined,
        colors: colors.length ? colors : undefined,
      };

      const stylesToTry = [style, 'minimalist', 'bold'].filter(
        (value, index, arr) => arr.indexOf(value) === index
      );

      const results = await Promise.allSettled(
        stylesToTry.map((variantStyle) =>
          aiAPI.generateLogo({
            ...baseParams,
            style: variantStyle,
            canvas_width: 1024,
            canvas_height: 1024,
          })
        )
      );

      const concepts: LogoConcept[] = [];
      results.forEach((result, index) => {
        if (result.status !== 'fulfilled') return;
        const payload = result.value as Record<string, unknown>;
        const nested = payload.result as Record<string, unknown> | undefined;
        const metadata =
          (payload.metadata as Record<string, unknown> | undefined) ||
          (nested?.metadata as Record<string, unknown> | undefined);
        if (metadata?.status === 'fallback') return;

        const components =
          (payload.components as Record<string, unknown>[]) ||
          (nested?.components as Record<string, unknown>[]) ||
          [];
        if (!components.length) return;

        concepts.push({
          id: `logo-${Date.now()}-${index}`,
          label: `${stylesToTry[index]} concept`,
          style: stylesToTry[index],
          components,
          metadata,
        });
      });

      // If API returns a single rich result, still show it once
      if (!concepts.length && results[0]?.status === 'fulfilled') {
        const payload = results[0].value as Record<string, unknown>;
        const nested = payload.result as Record<string, unknown> | undefined;
        const metadata =
          (payload.metadata as Record<string, unknown> | undefined) ||
          (nested?.metadata as Record<string, unknown> | undefined);
        if (metadata?.status !== 'fallback') {
          const components =
            (payload.components as Record<string, unknown>[]) ||
            (nested?.components as Record<string, unknown>[]) ||
            [];
          if (components.length) {
            concepts.push({
              id: `logo-${Date.now()}`,
              label: `${style} concept`,
              style,
              components,
              metadata,
            });
          }
        }
      }

      if (!concepts.length) {
        toast({
          title: 'Generation failed',
          description: vision
            ? 'AI could not generate logo concepts. Check your API keys and try again.'
            : 'AI could not generate logo concepts. Check your API keys and try again.',
          variant: 'destructive',
        });
        setGeneratedLogos([]);
        return;
      }

      setGeneratedLogos(concepts);
      setSelectedId(concepts[0].id);
      toast({
        title: 'Logos ready',
        description: `Generated ${concepts.length} concept${concepts.length === 1 ? '' : 's'}.`,
      });
    } catch (error: unknown) {
      console.error('Logo generation failed:', error);
      const axiosError = error as { response?: { data?: { error?: string } } };
      toast({
        title: 'Generation failed',
        description: axiosError.response?.data?.error || 'Could not reach the logo API.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const openInEditor = async (concept: LogoConcept) => {
    setOpeningId(concept.id);
    try {
      const meta = concept.metadata || {};
      const canvasWidth =
        typeof meta.canvas_width === 'number' ? meta.canvas_width : 1024;
      const canvasHeight =
        typeof meta.canvas_height === 'number' ? meta.canvas_height : 1024;

      const project = await projectsAPI.create({
        name: `${companyName || 'Logo'} — ${concept.label}`,
        description: `AI logo concept (${concept.style})${vision ? `: ${vision}` : ''}`,
        canvas_width: canvasWidth,
        canvas_height: canvasHeight,
        canvas_background: '#FFFFFF',
        design_data: {
          components: concept.components,
          metadata: {
            source: 'ai-logo-designer',
            style: concept.style,
            company_name: companyName,
            industry,
            colors,
            canvas_width: canvasWidth,
            canvas_height: canvasHeight,
            ...concept.metadata,
          },
        },
      });

      toast({
        title: 'Opening editor',
        description: 'Your logo concept is ready to refine.',
      });
      router.push(`/editor?project=${project.id}`);
    } catch (error: unknown) {
      console.error('Failed to open logo in editor:', error);
      // Still allow editor navigation with components in session for local preview path
      try {
        sessionStorage.setItem(
          'pending-ai-design',
          JSON.stringify({ components: concept.components, companyName, style: concept.style })
        );
      } catch {
        // ignore storage errors
      }
      toast({
        title: 'Could not create project',
        description: 'Open the editor manually and use AI Generate with logo type.',
        variant: 'destructive',
      });
    } finally {
      setOpeningId(null);
    }
  };

  const exportSelected = () => {
    if (!selectedConcept) {
      toast({
        title: 'Select a concept',
        description: 'Choose a logo concept before exporting.',
        variant: 'destructive',
      });
      return;
    }
    const blob = new Blob([JSON.stringify(selectedConcept, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${(companyName || 'logo').replace(/\s+/g, '-').toLowerCase()}-concept.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast({ title: 'Exported', description: 'Logo concept JSON downloaded.' });
  };

  return (
    <div className="h-screen flex flex-col bg-[#f6f6f8] dark:bg-[#101622]">
      <header className="flex items-center justify-between border-b border-[#232f48] bg-[#111722] px-6 py-3 shrink-0 z-20">
        <div className="flex items-center gap-4 text-white">
          <div className="size-8 flex items-center justify-center rounded-lg bg-[#2b6cee]/20 text-[#2b6cee]">
            <span className="material-symbols-outlined text-2xl">design_services</span>
          </div>
          <h2 className="text-white text-lg font-bold leading-tight tracking-[-0.015em]">LogoGen AI</h2>
        </div>

        <div className="flex flex-1 justify-end gap-4">
          <div className="flex gap-2">
            <button
              type="button"
              onClick={exportSelected}
              disabled={!selectedConcept}
              className="flex items-center justify-center rounded-lg h-10 px-4 bg-[#2b6cee] hover:bg-blue-600 disabled:opacity-50 text-white gap-2 text-sm font-bold transition-colors shadow-lg shadow-[#2b6cee]/20"
            >
              <span className="material-symbols-outlined text-lg">ios_share</span>
              <span className="truncate">Export</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        <aside className="w-full md:w-[400px] lg:w-[450px] flex flex-col border-r border-[#232f48] bg-[#111722] overflow-y-auto z-10 shadow-xl shrink-0">
          <div className="p-6 space-y-8">
            <div className="space-y-2">
              <h1 className="text-2xl font-bold text-white tracking-tight">Create New Logo</h1>
              <p className="text-[#92a4c9] text-sm">
                Define your brand identity and let AI generate unique concepts.
              </p>
            </div>

            <div className="space-y-6">
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

              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Logo Style</label>
                <div className="grid grid-cols-2 gap-3">
                  {['modern', 'classic', 'minimal', 'playful'].map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setStyle(s === 'minimal' ? 'minimalist' : s)}
                      className={`px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        (s === 'minimal' ? style === 'minimalist' : style === s)
                          ? 'border-[#2b6cee] bg-[#2b6cee]/10 text-white'
                          : 'border-[#324467] bg-[#192233] text-[#92a4c9] hover:border-[#2b6cee]/50'
                      }`}
                    >
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Preferred Colors</label>
                <div className="grid grid-cols-6 gap-2">
                  {['#2b6cee', '#8b5cf6', '#ec4899', '#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#6366f1'].map(
                    (color) => (
                      <button
                        key={color}
                        type="button"
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

              <div className="space-y-3">
                <label className="text-sm font-medium text-white">Additional Preferences</label>
                <textarea
                  value={vision}
                  onChange={(e) => setVision(e.target.value)}
                  placeholder="Describe your vision (optional)"
                  rows={4}
                  className="w-full px-4 py-3 rounded-lg bg-[#192233] border border-[#324467] text-white placeholder-[#92a4c9] focus:border-[#2b6cee] focus:ring-2 focus:ring-[#2b6cee]/20 transition-all outline-none resize-none"
                />
              </div>

              <button
                type="button"
                onClick={handleGenerate}
                disabled={loading}
                className="w-full py-4 rounded-lg bg-linear-to-r from-[#2b6cee] to-[#8b5cf6] text-white font-bold text-base shadow-lg shadow-[#2b6cee]/30 hover:shadow-[#2b6cee]/50 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2 disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <span className="material-symbols-outlined">auto_awesome</span>
                )}
                {loading ? 'Generating…' : 'Generate Logo Concepts'}
              </button>
            </div>
          </div>
        </aside>

        <main className="flex-1 flex flex-col bg-[#101622] relative overflow-hidden">
          <div
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: 'radial-gradient(#324467 1px, transparent 1px)',
              backgroundSize: '20px 20px',
            }}
          />

          <div className="relative z-10 flex-1 overflow-y-auto p-8">
            {generatedLogos.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-24 h-24 rounded-full bg-[#192233] flex items-center justify-center mb-6">
                  <span className="material-symbols-outlined text-5xl text-[#92a4c9]">palette</span>
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
                    Click a concept, then open it in the editor to refine and export
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {generatedLogos.map((logo, index) => (
                    <LogoCard
                      key={logo.id}
                      concept={logo}
                      index={index}
                      companyName={companyName}
                      selected={selectedId === logo.id}
                      opening={openingId === logo.id}
                      onSelect={() => setSelectedId(logo.id)}
                      onOpen={() => openInEditor(logo)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function LogoCard({
  concept,
  index,
  companyName,
  selected,
  opening,
  onSelect,
  onOpen,
}: {
  concept: LogoConcept;
  index: number;
  companyName: string;
  selected: boolean;
  opening: boolean;
  onSelect: () => void;
  onOpen: () => void;
}) {
  const previewText =
    (concept.components.find((c) => c.type === 'text' || c.subtype === 'wordmark')?.content as string) ||
    companyName ||
    'Logo';
  const accent =
    (concept.components.find((c) => typeof c.style === 'object' && (c.style as { fill?: string }).fill)?.style as
      | { fill?: string }
      | undefined)?.fill || '#ffffff';

  return (
    <div
      className={`group cursor-pointer rounded-xl border-2 transition-all ${
        selected ? 'border-[#2b6cee]' : 'border-transparent'
      }`}
      onClick={onSelect}
    >
      <div
        className={`aspect-square rounded-xl bg-linear-to-br ${STYLE_GRADIENTS[index % STYLE_GRADIENTS.length]} p-8 flex items-center justify-center mb-3 hover:scale-[1.02] transition-transform shadow-lg`}
      >
        <div className="w-full h-full bg-white/10 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center gap-2 p-4 text-center">
          <span className="text-white font-bold text-2xl truncate max-w-full" style={{ color: accent }}>
            {String(previewText).slice(0, 24)}
          </span>
          <span className="text-white/80 text-xs uppercase tracking-wide">{concept.style}</span>
          <span className="text-white/60 text-[10px]">{concept.components.length} elements</span>
        </div>
      </div>
      <div className="flex items-center justify-between gap-2">
        <div>
          <h4 className="text-sm font-medium text-white capitalize">{concept.label}</h4>
          <p className="text-xs text-[#92a4c9]">AI Generated</p>
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onOpen();
          }}
          disabled={opening}
          className="px-3 py-1.5 rounded-lg bg-[#192233] border border-[#324467] text-xs text-white hover:bg-[#232f48] disabled:opacity-50"
        >
          {opening ? 'Opening…' : 'Edit'}
        </button>
      </div>
    </div>
  );
}

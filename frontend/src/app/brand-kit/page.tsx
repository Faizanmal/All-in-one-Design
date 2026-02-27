"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Shield, Plus, Lock, Image as ImageIcon, Type, Palette, UploadCloud, Users, Hash } from 'lucide-react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { brandKitAPI } from '@/lib/brand-kit-api';
import { useToast } from '@/hooks/use-toast';
import { useEffect } from 'react';

export default function BrandKitPage() {
    const [activeTab, setActiveTab] = useState('colors');
    const [enforcement, setEnforcement] = useState<any>(null);
    const [saving, setSaving] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        // dummy design system id
        brandKitAPI.getEnforcementRules('123e4567-e89b-12d3-a456-426614174000')
            .then(data => {
                if (data && data.length > 0) {
                    setEnforcement(data[0]);
                }
            })
            .catch(err => console.error(err))
            .finally(() => setIsLoading(false));
    }, []);

    const toggleRule = (rule: string) => {
        if (!enforcement) return;
        setEnforcement((prev: any) => ({ ...prev, [rule]: !prev[rule] }));
    };

    const saveGuidelines = async () => {
        if (!enforcement) return;
        setSaving(true);
        try {
            await brandKitAPI.updateEnforcementRules(enforcement.id, enforcement);
            toast({
                title: "Guidelines Saved",
                description: "Brand enforcement rules updated globally.",
            });
        } catch (error) {
            toast({
                title: "Update Failed",
                description: "Could not save brand rules.",
                variant: "destructive"
            });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            <DashboardSidebar />
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
                <MainHeader />

                {/* Sub-header specifically for Brand Kit */}
                <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between shadow-sm z-10">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center">
                            <Shield className="h-5 w-5" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900 leading-tight">Brand Kit Guardian</h1>
                            <p className="text-sm text-gray-500">Enforce global brand compliance across your team</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <span className="flex items-center gap-2 text-sm font-medium text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
                            <Lock className="h-4 w-4" /> Strictly Enforced
                        </span>
                        <Button
                            className="bg-indigo-600 hover:bg-indigo-700"
                            onClick={saveGuidelines}
                            disabled={saving || !enforcement}
                        >
                            {saving ? 'Saving...' : 'Save Guidelines'}
                        </Button>
                    </div>
                </div>

                <div className="flex-1 flex overflow-hidden">
                    {/* Internal Sidebar */}
                    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
                        <ScrollArea className="flex-1 py-4">
                            <nav className="space-y-1 px-4">
                                {[
                                    { id: 'colors', name: 'Brand Colors', icon: Palette },
                                    { id: 'typography', name: 'Typography', icon: Type },
                                    { id: 'logos', name: 'Logos & Marks', icon: ImageIcon },
                                    { id: 'assets', name: 'Approved Imagery', icon: UploadCloud },
                                    { id: 'permissions', name: 'Team Access', icon: Users },
                                ].map((item) => {
                                    const Icon = item.icon;
                                    return (
                                        <button
                                            key={item.id}
                                            onClick={() => setActiveTab(item.id)}
                                            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${activeTab === item.id
                                                ? 'bg-indigo-50 text-indigo-700'
                                                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                                }`}
                                        >
                                            <Icon className="h-4 w-4" />
                                            {item.name}
                                        </button>
                                    );
                                })}
                            </nav>
                        </ScrollArea>
                    </div>

                    {/* Settings Canvas */}
                    <div className="flex-1 overflow-auto bg-gray-50/50 p-8">
                        <div className="max-w-4xl max-auto space-y-6">

                            {activeTab === 'colors' && (
                                <>
                                    <div className="flex justify-between items-end">
                                        <div>
                                            <h2 className="text-2xl font-bold text-gray-900">Brand Color Palette</h2>
                                            <p className="text-gray-500 mt-1">These colors will be locked in the editor. Team members cannot pick unstructured hex codes.</p>
                                        </div>
                                        <Button variant="outline" size="sm"><Plus className="h-4 w-4 mr-2" /> Add Swatch</Button>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        {/* Primary Palette */}
                                        <Card>
                                            <CardHeader className="pb-3">
                                                <CardTitle className="text-lg">Primary Colors</CardTitle>
                                                <CardDescription>The core identity of your brand.</CardDescription>
                                            </CardHeader>
                                            <CardContent className="space-y-3">
                                                {[
                                                    { name: 'Brand Blue', hex: '#2563EB', role: 'Primary Button, Active States' },
                                                    { name: 'Deep Navy', hex: '#1E40AF', role: 'Headings, Dark Sections' },
                                                    { name: 'Pure White', hex: '#FFFFFF', role: 'Backgrounds, Cards' },
                                                ].map((color, i) => (
                                                    <div key={i} className="flex items-center gap-4 p-2 rounded-lg border border-gray-100 hover:border-gray-300 transition-colors bg-white">
                                                        <div className="h-12 w-12 rounded-md border border-gray-200 shadow-inner" style={{ backgroundColor: color.hex }}></div>
                                                        <div className="flex-1">
                                                            <div className="font-semibold text-gray-900 text-sm">{color.name}</div>
                                                            <div className="text-xs text-gray-500">{color.role}</div>
                                                        </div>
                                                        <div className="font-mono text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                                            {color.hex}
                                                        </div>
                                                    </div>
                                                ))}
                                            </CardContent>
                                        </Card>

                                        {/* Secondary/Accent Palette */}
                                        <Card>
                                            <CardHeader className="pb-3">
                                                <CardTitle className="text-lg">Secondary & Accents</CardTitle>
                                                <CardDescription>Used sparingly for emphasis.</CardDescription>
                                            </CardHeader>
                                            <CardContent className="space-y-3">
                                                {[
                                                    { name: 'Alert Orange', hex: '#F97316', role: 'Warnings, Highlights' },
                                                    { name: 'Success Green', hex: '#10B981', role: 'Success States' },
                                                    { name: 'Stone Gray', hex: '#F3F4F6', role: 'Secondary Backgrounds' },
                                                ].map((color, i) => (
                                                    <div key={i} className="flex items-center gap-4 p-2 rounded-lg border border-gray-100 hover:border-gray-300 transition-colors bg-white">
                                                        <div className="h-12 w-12 rounded-md border border-gray-200 shadow-inner" style={{ backgroundColor: color.hex }}></div>
                                                        <div className="flex-1">
                                                            <div className="font-semibold text-gray-900 text-sm">{color.name}</div>
                                                            <div className="text-xs text-gray-500">{color.role}</div>
                                                        </div>
                                                        <div className="font-mono text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                                            {color.hex}
                                                        </div>
                                                    </div>
                                                ))}
                                            </CardContent>
                                        </Card>
                                    </div>

                                    {/* Enforcement Rules Settings */}
                                    <Card className="border-indigo-100 shadow-sm bg-gradient-to-br from-white to-indigo-50/30">
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2"><Lock className="h-5 w-5 text-indigo-500" /> Enforcement Rules</CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            {isLoading ? (
                                                <div className="space-y-4">
                                                    <Skeleton className="h-16 w-full rounded-lg" />
                                                    <Skeleton className="h-16 w-full rounded-lg" />
                                                </div>
                                            ) : (
                                                <>
                                                    <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200">
                                                        <div>
                                                            <div className="font-medium text-gray-900">Lock Color Picker</div>
                                                            <div className="text-sm text-gray-500">Prevent team members from using colors outside this palette.</div>
                                                        </div>
                                                        <div
                                                            className={`relative inline-flex h-6 w-11 items-center rounded-full cursor-pointer transition-colors ${enforcement?.lock_color_picker ? 'bg-indigo-600' : 'bg-gray-200'}`}
                                                            onClick={() => toggleRule('lock_color_picker')}
                                                        >
                                                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${enforcement?.lock_color_picker ? 'translate-x-6' : 'translate-x-1'}`} />
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200 opacity-75">
                                                        <div>
                                                            <div className="font-medium text-gray-900">AI Variant Constraint</div>
                                                            <div className="text-sm text-gray-500">Force the AI Generator engine to strictly use these Hex codes.</div>
                                                        </div>
                                                        <div
                                                            className={`relative inline-flex h-6 w-11 items-center rounded-full cursor-pointer transition-colors ${enforcement?.force_ai_variants ? 'bg-indigo-600' : 'bg-gray-200'}`}
                                                            onClick={() => toggleRule('force_ai_variants')}
                                                        >
                                                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${enforcement?.force_ai_variants ? 'translate-x-6' : 'translate-x-1'}`} />
                                                        </div>
                                                    </div>
                                                </>
                                            )}
                                        </CardContent>
                                    </Card>
                                </>
                            )}

                            {activeTab === 'typography' && (
                                <div className="text-center py-20">
                                    <Type className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                                    <h2 className="text-xl font-semibold text-gray-900">Typography Lock-in</h2>
                                    <p className="text-gray-500 mt-2">Upload custom fonts and lock Heading/Body hierarchies. <br />Coming soon in v2.1</p>
                                </div>
                            )}

                            {activeTab === 'logos' && (
                                <div className="text-center py-20">
                                    <ImageIcon className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                                    <h2 className="text-xl font-semibold text-gray-900">Verified Logos</h2>
                                    <p className="text-gray-500 mt-2">Upload your SVG wordmarks and icons. Stop the team from using fuzzy JPEGs. <br />Coming soon in v2.1</p>
                                </div>
                            )}

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

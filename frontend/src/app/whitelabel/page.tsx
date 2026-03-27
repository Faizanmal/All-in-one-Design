"use client";

import React, { useState } from 'react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Shield,
  Palette,
  Type,
  Image as ImageIcon,
  Globe,
  Mail,
  Eye,
  Save,
  RefreshCw,
  Upload,
  Check,
  Code,
  Smartphone,
  Monitor,
  Copy,
  Crown,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Types
interface BrandSettings {
  companyName: string;
  logoUrl: string;
  faviconUrl: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  customDomain: string;
  customEmail: string;
  hidePoweredBy: boolean;
  customLoginPage: boolean;
  customEmails: boolean;
}

export default function WhitelabelPage() {
  const { toast } = useToast();
  const [settings, setSettings] = useState<BrandSettings>({
    companyName: 'Acme Design Studio',
    logoUrl: '/logo.png',
    faviconUrl: '/favicon.ico',
    primaryColor: '#3B82F6',
    secondaryColor: '#1F2937',
    accentColor: '#10B981',
    customDomain: 'design.acmestudio.com',
    customEmail: 'hello@acmestudio.com',
    hidePoweredBy: true,
    customLoginPage: true,
    customEmails: true,
  });
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'mobile'>('desktop');
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      toast({ title: 'Settings Saved', description: 'Whitelabel configuration has been updated' });
    }, 1500);
  };

  const handleColorChange = (key: keyof BrandSettings, value: string) => {
    setSettings({ ...settings, [key]: value });
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <MainHeader />
        <main className="flex-1 overflow-hidden p-6">
          <div className="max-w-7xl mx-auto h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                    <Shield className="h-7 w-7 text-blue-600" />Whitelabel
                  </h1>
                  <p className="text-gray-500">Custom branding and whitelabel solutions</p>
                </div>
                <Badge className="bg-purple-100 text-purple-700"><Crown className="h-3 w-3 mr-1" />Enterprise</Badge>
              </div>
              <div className="flex gap-3">
                <Button variant="outline"><Eye className="h-4 w-4 mr-2" />Preview</Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? <><RefreshCw className="h-4 w-4 mr-2 animate-spin" />Saving...</> : <><Save className="h-4 w-4 mr-2" />Save Changes</>}
                </Button>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-5 gap-6 overflow-hidden">
              {/* Settings Panel */}
              <div className="col-span-2 flex flex-col overflow-hidden">
                <Tabs defaultValue="branding" className="flex-1 flex flex-col overflow-hidden">
                  <TabsList className="grid grid-cols-3 mb-4">
                    <TabsTrigger value="branding">Branding</TabsTrigger>
                    <TabsTrigger value="domain">Domain</TabsTrigger>
                    <TabsTrigger value="features">Features</TabsTrigger>
                  </TabsList>

                  <TabsContent value="branding" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-6 pr-4">
                        {/* Company Name */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2"><Type className="h-4 w-4" />Company Name</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <Input value={settings.companyName} onChange={(e) => setSettings({ ...settings, companyName: e.target.value })} />
                          </CardContent>
                        </Card>

                        {/* Logo */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2"><ImageIcon className="h-4 w-4" />Logo</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="flex items-center gap-4">
                              <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
                                <ImageIcon className="h-8 w-8 text-gray-400" />
                              </div>
                              <div className="flex-1">
                                <Button variant="outline" size="sm"><Upload className="h-4 w-4 mr-2" />Upload Logo</Button>
                                <p className="text-xs text-gray-500 mt-2">Recommended: 240x60px, PNG or SVG</p>
                              </div>
                            </div>
                            <div>
                              <Label className="text-xs">Favicon</Label>
                              <div className="flex items-center gap-2 mt-1">
                                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center border">
                                  <ImageIcon className="h-4 w-4 text-gray-400" />
                                </div>
                                <Button variant="outline" size="sm"><Upload className="h-4 w-4 mr-2" />Upload</Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        {/* Colors */}
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2"><Palette className="h-4 w-4" />Brand Colors</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <Label className="text-xs">Primary Color</Label>
                              <div className="flex items-center gap-2 mt-1">
                                <input type="color" value={settings.primaryColor} onChange={(e) => handleColorChange('primaryColor', e.target.value)} className="w-10 h-10 rounded-lg cursor-pointer" />
                                <Input value={settings.primaryColor} onChange={(e) => handleColorChange('primaryColor', e.target.value)} className="flex-1 font-mono" />
                              </div>
                            </div>
                            <div>
                              <Label className="text-xs">Secondary Color</Label>
                              <div className="flex items-center gap-2 mt-1">
                                <input type="color" value={settings.secondaryColor} onChange={(e) => handleColorChange('secondaryColor', e.target.value)} className="w-10 h-10 rounded-lg cursor-pointer" />
                                <Input value={settings.secondaryColor} onChange={(e) => handleColorChange('secondaryColor', e.target.value)} className="flex-1 font-mono" />
                              </div>
                            </div>
                            <div>
                              <Label className="text-xs">Accent Color</Label>
                              <div className="flex items-center gap-2 mt-1">
                                <input type="color" value={settings.accentColor} onChange={(e) => handleColorChange('accentColor', e.target.value)} className="w-10 h-10 rounded-lg cursor-pointer" />
                                <Input value={settings.accentColor} onChange={(e) => handleColorChange('accentColor', e.target.value)} className="flex-1 font-mono" />
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </ScrollArea>
                  </TabsContent>

                  <TabsContent value="domain" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-6 pr-4">
                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2"><Globe className="h-4 w-4" />Custom Domain</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <Label>Domain</Label>
                              <div className="flex gap-2 mt-1">
                                <Input value={settings.customDomain} onChange={(e) => setSettings({ ...settings, customDomain: e.target.value })} placeholder="app.yourdomain.com" />
                                <Button variant="outline"><Check className="h-4 w-4" /></Button>
                              </div>
                              <p className="text-xs text-gray-500 mt-2">Add a CNAME record pointing to our servers</p>
                            </div>
                            <div className="p-3 bg-gray-50 rounded-lg">
                              <p className="text-xs font-medium text-gray-700 mb-2">DNS Configuration</p>
                              <div className="flex items-center justify-between text-xs">
                                <code className="bg-gray-200 px-2 py-1 rounded">CNAME → app.designplatform.io</code>
                                <Button size="sm" variant="ghost"><Copy className="h-3 w-3" /></Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader className="pb-3">
                            <CardTitle className="text-base flex items-center gap-2"><Mail className="h-4 w-4" />Email Settings</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div>
                              <Label>From Email</Label>
                              <Input value={settings.customEmail} onChange={(e) => setSettings({ ...settings, customEmail: e.target.value })} placeholder="hello@yourdomain.com" className="mt-1" />
                            </div>
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">Custom Email Templates</p>
                                <p className="text-sm text-gray-500">Use your own email designs</p>
                              </div>
                              <Switch checked={settings.customEmails} onCheckedChange={(v) => setSettings({ ...settings, customEmails: v })} />
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </ScrollArea>
                  </TabsContent>

                  <TabsContent value="features" className="flex-1 overflow-hidden mt-0">
                    <ScrollArea className="h-full">
                      <div className="space-y-4 pr-4">
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">Hide &quot;Powered By&quot;</p>
                                <p className="text-sm text-gray-500">Remove platform branding</p>
                              </div>
                              <Switch checked={settings.hidePoweredBy} onCheckedChange={(v) => setSettings({ ...settings, hidePoweredBy: v })} />
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">Custom Login Page</p>
                                <p className="text-sm text-gray-500">Branded sign-in experience</p>
                              </div>
                              <Switch checked={settings.customLoginPage} onCheckedChange={(v) => setSettings({ ...settings, customLoginPage: v })} />
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">Custom CSS</p>
                                <p className="text-sm text-gray-500">Advanced styling options</p>
                              </div>
                              <Button size="sm" variant="outline"><Code className="h-4 w-4 mr-1" />Edit</Button>
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">White-labeled Mobile App</p>
                                <p className="text-sm text-gray-500">Your brand on iOS & Android</p>
                              </div>
                              <Badge variant="outline">Coming Soon</Badge>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </div>

              {/* Preview Panel */}
              <div className="col-span-3 flex flex-col overflow-hidden bg-white rounded-xl border border-gray-200">
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900">Live Preview</h3>
                  <div className="flex gap-2">
                    <Button size="sm" variant={previewDevice === 'desktop' ? 'default' : 'outline'} onClick={() => setPreviewDevice('desktop')}>
                      <Monitor className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant={previewDevice === 'mobile' ? 'default' : 'outline'} onClick={() => setPreviewDevice('mobile')}>
                      <Smartphone className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <div className="flex-1 bg-gray-100 p-8 flex items-center justify-center overflow-auto">
                  <div className={`bg-white rounded-xl shadow-2xl overflow-hidden ${previewDevice === 'desktop' ? 'w-full max-w-3xl' : 'w-80'}`}>
                    {/* Preview Header */}
                    <div className="h-14 flex items-center justify-between px-6" style={{ backgroundColor: settings.primaryColor }}>
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                          <ImageIcon className="h-4 w-4 text-white" />
                        </div>
                        <span className="font-semibold text-white">{settings.companyName}</span>
                      </div>
                      <div className="flex items-center gap-4 text-white/80 text-sm">
                        <span>Projects</span>
                        <span>Templates</span>
                        <span>Assets</span>
                      </div>
                    </div>
                    {/* Preview Content */}
                    <div className="p-8">
                      <h2 className="text-2xl font-bold mb-4" style={{ color: settings.secondaryColor }}>Welcome back!</h2>
                      <p className="text-gray-500 mb-6">Create stunning designs with {settings.companyName}.</p>
                      <div className="grid grid-cols-3 gap-4">
                        {[1, 2, 3].map(i => (
                          <div key={i} className="aspect-square bg-gray-100 rounded-xl" />
                        ))}
                      </div>
                      <Button className="mt-6" style={{ backgroundColor: settings.accentColor }}>
                        Create New Design
                      </Button>
                    </div>
                    {/* Preview Footer */}
                    {!settings.hidePoweredBy && (
                      <div className="border-t border-gray-100 p-4 text-center">
                        <span className="text-xs text-gray-400">Powered by Design Platform</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

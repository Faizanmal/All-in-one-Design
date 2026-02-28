"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Check, Globe, Link as LinkIcon, Lock, Server, Zap } from 'lucide-react';
import { MainHeader } from '@/components/layout/MainHeader';
import { DashboardSidebar } from '@/components/layout/DashboardSidebar';
import { webPublishingAPI } from '@/lib/web-publishing-api';
import { useToast } from '@/hooks/use-toast';

interface PublishedSite {
    id: number;
    subdomain: string;
    published_url: string;
    status: 'active' | 'inactive';
    published_at: string;
    [key: string]: unknown;
}

export default function WebPublishingPage() {
    const [subdomain, setSubdomain] = useState('');
    const [subdomainError, setSubdomainError] = useState('');
    const [isPublishing, setIsPublishing] = useState(false);
    const [isPublished, setIsPublished] = useState(false);
    const [pastSites, setPastSites] = useState<PublishedSite[]>([]);
    const [isLoadingSites, setIsLoadingSites] = useState(true);
    const { toast } = useToast();

    useEffect(() => {
        webPublishingAPI.getSites()
            .then(data => {
                setPastSites(data);
            })
            .catch(error => {
                console.error("Failed to load sites", error);
            })
            .finally(() => {
                setIsLoadingSites(false);
            });
    }, [isPublished]);

    const handleSubdomainChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value.toLowerCase();
        setSubdomain(val);
        if (val && !/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(val)) {
            setSubdomainError("Only lowercase letters, numbers, and hyphens.");
        } else {
            setSubdomainError("");
        }
    };

    const handlePublish = async () => {
        setIsPublishing(true);
        try {
            // Dummy project ID 1 for simulation
            await webPublishingAPI.publishSite(1, subdomain);
            setIsPublished(true);
            toast({
                title: "Successfully Deployed!",
                description: `Your site is now live at https://${subdomain}.designco.site`
            });
        } catch (error: unknown) {
            const err = error as { response?: { data?: { subdomain?: string[] } } };
            toast({
                title: "Deployment Failed",
                description: err?.response?.data?.subdomain ? err.response.data.subdomain[0] : "There was an error deploying the site.",
                variant: "destructive"
            });
            console.error(error);
        } finally {
            setIsPublishing(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            <DashboardSidebar />
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
                <MainHeader />
                <main className="flex-1 overflow-auto p-8">
                    <div className="max-w-4xl mx-auto space-y-8">
                        <div className="text-center mb-10">
                            <h1 className="text-4xl font-bold text-gray-900 mb-4">Launch Your Project</h1>
                            <p className="text-lg text-gray-500">Deploy your designs to live servers with a single click.</p>
                        </div>

                        {!isPublished ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Free Tier */}
                                <Card className="border-2 hover:border-blue-500 transition-all flex flex-col">
                                    <CardHeader>
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="p-3 bg-blue-100 rounded-lg text-blue-600">
                                                <Globe className="h-6 w-6" />
                                            </div>
                                            <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm font-medium">Free</span>
                                        </div>
                                        <CardTitle className="text-2xl">Design Co. Hosting</CardTitle>
                                        <CardDescription>Publish to a secure `.designco.site` subdomain instantly.</CardDescription>
                                    </CardHeader>
                                    <CardContent className="flex-1 space-y-4">
                                        <div className="space-y-2">
                                            <Label>Choose your subdomain</Label>
                                            <div className="flex items-center gap-2">
                                                <Input
                                                    placeholder="my-portfolio"
                                                    value={subdomain}
                                                    onChange={handleSubdomainChange}
                                                    className={subdomainError ? "border-red-500" : ""}
                                                />
                                                <span className="text-gray-500 text-sm font-medium whitespace-nowrap">.designco.site</span>
                                            </div>
                                            {subdomainError && <p className="text-xs text-red-500 mt-1">{subdomainError}</p>}
                                        </div>
                                        <div className="space-y-3 mt-6">
                                            <div className="flex items-center gap-2 text-sm text-gray-600"><Check className="h-4 w-4 text-green-500" /> Free SSL Certificate</div>
                                            <div className="flex items-center gap-2 text-sm text-gray-600"><Check className="h-4 w-4 text-green-500" /> Global Edge CDN</div>
                                            <div className="flex items-center gap-2 text-sm text-gray-600"><Check className="h-4 w-4 text-green-500" /> Automatic Deployments</div>
                                        </div>
                                    </CardContent>
                                    <CardFooter>
                                        <Button
                                            className="w-full bg-blue-600 hover:bg-blue-700 h-12"
                                            disabled={!subdomain || isPublishing || !!subdomainError}
                                            onClick={handlePublish}
                                        >
                                            {isPublishing ? 'Deploying to Edge...' : 'Publish to web'}
                                        </Button>
                                    </CardFooter>
                                </Card>

                                {/* Pro Tier */}
                                <Card className="border-2 border-transparent bg-gray-900 text-white flex flex-col relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4">
                                        <Zap className="h-6 w-6 text-yellow-500" />
                                    </div>
                                    <CardHeader>
                                        <div className="mb-4 p-3 bg-gray-800 rounded-lg text-white w-fit">
                                            <Lock className="h-6 w-6" />
                                        </div>
                                        <CardTitle className="text-2xl">Custom Domain</CardTitle>
                                        <CardDescription className="text-gray-400">Connect your own branding and domains.</CardDescription>
                                    </CardHeader>
                                    <CardContent className="flex-1 space-y-6">
                                        <div className="p-4 bg-gray-800 rounded-xl space-y-3">
                                            <div className="flex justify-between items-center text-sm font-medium">
                                                <span className="text-gray-400">Type</span>
                                                <span>CNAME Record</span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm font-medium">
                                                <span className="text-gray-400">Name</span>
                                                <span>www</span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm font-medium">
                                                <span className="text-gray-400">Value</span>
                                                <span>cname.designco.site</span>
                                            </div>
                                        </div>
                                        <div className="space-y-3">
                                            <div className="flex items-center gap-2 text-sm text-gray-300"><Check className="h-4 w-4 text-blue-500" /> Custom DNS Routing</div>
                                            <div className="flex items-center gap-2 text-sm text-gray-300"><Check className="h-4 w-4 text-blue-500" /> Advanced Analytics</div>
                                            <div className="flex items-center gap-2 text-sm text-gray-300"><Check className="h-4 w-4 text-blue-500" /> Remove Branding</div>
                                        </div>
                                    </CardContent>
                                    <CardFooter>
                                        <Button variant="outline" className="w-full h-12 border-gray-700 text-gray-900 bg-white hover:bg-gray-100">
                                            Upgrade to Pro
                                        </Button>
                                    </CardFooter>
                                </Card>
                            </div>
                        ) : (
                            <Card className="border-2 border-green-500 bg-green-50">
                                <CardContent className="flex flex-col items-center justify-center p-12 text-center space-y-6">
                                    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center text-green-600">
                                        <Check className="w-10 h-10" />
                                    </div>
                                    <div>
                                        <h2 className="text-3xl font-bold text-gray-900 mb-2">Successfully Deployed!</h2>
                                        <p className="text-gray-600 text-lg">Your design is now live on the global edge network.</p>
                                    </div>
                                    <div className="bg-white px-6 py-4 rounded-xl shadow-sm border border-gray-200 flex items-center gap-4 w-full max-w-md">
                                        <LinkIcon className="text-gray-400" />
                                        <span className="flex-1 text-left font-medium text-blue-600 truncate">
                                            https://{subdomain}.designco.site
                                        </span>
                                        <Button variant="secondary" size="sm">Visit</Button>
                                    </div>
                                    <div className="flex gap-4 pt-4">
                                        <Button variant="outline" onClick={() => setIsPublished(false)}>Deploy Changes</Button>
                                        <Button onClick={() => window.location.href = '/analytics-dashboard'}><Server className="w-4 h-4 mr-2" />View Analytics</Button>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Past Deployments */}
                        <div className="mt-12">
                            <h3 className="text-xl font-bold mb-4">Previous Deployments</h3>
                            {isLoadingSites ? (
                                <div className="space-y-3">
                                    <Skeleton className="h-16 w-full" />
                                    <Skeleton className="h-16 w-full" />
                                </div>
                            ) : pastSites.length === 0 ? (
                                <p className="text-gray-500 text-sm border-2 border-dashed border-gray-200 p-8 rounded-xl text-center">No previous deployments found.</p>
                            ) : (
                                <div className="space-y-3">
                                    {pastSites.map(site => (
                                        <div key={site.id} className="bg-white p-4 rounded-xl border border-gray-200 flex items-center justify-between shadow-sm">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-2 rounded-full ${site.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                                                <div>
                                                    <p className="font-semibold text-gray-900">{site.published_url}</p>
                                                </div>
                                            </div>
                                            <Button variant="outline" size="sm" onClick={() => window.open(site.published_url, '_blank')}>
                                                Visit <LinkIcon className="h-3 w-3 ml-2" />
                                            </Button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                    </div>
                </main>
            </div>
        </div>
    );
}

import React from 'react';
import { useAdvancedIntegrations } from '@/hooks/useAdvancedIntegrations';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { RefreshCw, Link2, DownloadCloud, UploadCloud, AlertCircle, Settings } from 'lucide-react';

export function AdvancedIntegrationsPanel() {
    const {
        providers,
        connections,
        isLoading,
        disconnectIntegration,
        refreshOAuthToken,
        triggerSync
    } = useAdvancedIntegrations();

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
                {/* Connected Services */}
                <Card className="col-span-1 border-primary/20">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Link2 className="h-5 w-5 text-primary" />
                            Connected Services
                        </CardTitle>
                        <CardDescription>
                            Manage your active third-party integrations
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {isLoading && connections.length === 0 ? (
                            <div className="flex justify-center p-4">
                                <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
                            </div>
                        ) : connections.length > 0 ? (
                            connections.map(conn => (
                                <div key={conn.id} className="flex flex-col gap-2 p-4 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            {conn.provider.icon_url ? (
                                                <img src={conn.provider.icon_url} alt={conn.provider.name} className="w-8 h-8 rounded" />
                                            ) : (
                                                <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary font-bold">
                                                    {conn.provider.name.charAt(0)}
                                                </div>
                                            )}
                                            <div>
                                                <h4 className="font-medium text-sm">{conn.provider.name}</h4>
                                                <p className="text-xs text-muted-foreground">{conn.account_name || 'Connected Account'}</p>
                                            </div>
                                        </div>
                                        <Badge variant={conn.status === 'connected' ? 'default' : 'destructive'}>
                                            {conn.status}
                                        </Badge>
                                    </div>

                                    <div className="flex justify-between items-center mt-2 border-t pt-2">
                                        <span className="text-xs text-muted-foreground">
                                            Last Sync: {conn.last_sync ? new Date(conn.last_sync).toLocaleDateString() : 'Never'}
                                        </span>
                                        <div className="flex gap-2">
                                            <Button variant="outline" size="sm" onClick={() => triggerSync(conn.id)}>
                                                <RefreshCw className="h-3 w-3 mr-1" /> Sync
                                            </Button>
                                            <Button variant="ghost" size="sm" className="text-destructive h-8" onClick={() => disconnectIntegration(conn.id)}>
                                                Disconnect
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center p-6 border border-dashed rounded-lg bg-muted/20">
                                <AlertCircle className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                                <p className="text-sm font-medium">No integrations connected</p>
                                <p className="text-xs text-muted-foreground">Connect a service below to get started</p>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Available Integrations */}
                <Card className="col-span-1">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <DownloadCloud className="h-5 w-5" />
                            Available Integrations
                        </CardTitle>
                        <CardDescription>
                            Connect new productivity and storage tools
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Dummy providers if API fails or empty for demo */}
                            {[
                                { id: 'jira', name: 'Jira', type: 'productivity' },
                                { id: 'dropbox', name: 'Dropbox', type: 'storage' },
                                { id: 'notion', name: 'Notion', type: 'productivity' },
                                { id: 'adobe', name: 'Adobe CC', type: 'design' },
                                { id: 'zapier', name: 'Zapier', type: 'automation' }
                            ].map(provider => {
                                const isConnected = connections.some(c => c.provider.slug === provider.id);
                                if (isConnected) return null; // Hide if already connected

                                return (
                                    <div key={provider.id} className="p-3 border rounded-lg hover:border-primary transition-colors cursor-pointer flex items-center justify-between group">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded bg-muted flex items-center justify-center font-bold text-muted-foreground">
                                                {provider.name.charAt(0)}
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium">{provider.name}</p>
                                                <p className="text-[10px] text-muted-foreground uppercase">{provider.type}</p>
                                            </div>
                                        </div>
                                        <Button size="sm" variant="secondary" className="opacity-0 group-hover:opacity-100 transition-opacity">
                                            Connect
                                        </Button>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                    <CardFooter className="border-t bg-muted/20 text-xs text-muted-foreground py-3">
                        Supports Jira, Adobe CC, Google Drive, Dropbox, Notion, Zapier & more.
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}

import { useState, useCallback, useEffect } from 'react';

const API_BASE = '/api/v1/advanced-integrations';

export interface Provider {
    id: string;
    name: string;
    slug: string;
    description: string;
    provider_type: 'productivity' | 'storage' | 'social' | 'cms' | 'automation' | 'other';
    icon_url: string;
    is_active: boolean;
}

export interface UserIntegration {
    id: string;
    provider: Provider;
    status: 'connected' | 'disconnected' | 'error' | 'pending';
    last_sync: string | null;
    account_name: string;
}

export interface WebhookEndpoint {
    id: string;
    name: string;
    url: string;
    events: string[];
    is_active: boolean;
    secret: string | null;
    created_at: string;
    last_triggered: string | null;
}

export interface WebhookLog {
    id: string;
    event_type: string;
    status: 'success' | 'failed';
    response_code: number;
    completed_at: string;
    payload: Record<string, unknown>;
}

export interface SyncStatus {
    id: string;
    sync_type: string;
    status: 'in_progress' | 'completed' | 'failed';
    items_synced: number;
    started_at: string;
    completed_at: string | null;
}

export function useAdvancedIntegrations() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [providers, setProviders] = useState<Provider[]>([]);
    const [connections, setConnections] = useState<UserIntegration[]>([]);

    const fetchProviders = useCallback(async () => {
        try {
            setIsLoading(true);
            const res = await fetch(`${API_BASE}/providers/`);
            if (!res.ok) throw new Error('Failed to load providers');
            const data = await res.json();
            setProviders(data.results || data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchConnections = useCallback(async () => {
        try {
            setIsLoading(true);
            const res = await fetch(`${API_BASE}/connections/`);
            if (!res.ok) throw new Error('Failed to load connections');
            const data = await res.json();
            setConnections(data.results || data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    }, []);

    const disconnectIntegration = useCallback(async (connectionId: string) => {
        try {
            const res = await fetch(`${API_BASE}/connections/${connectionId}/disconnect/`, {
                method: 'POST',
            });
            if (!res.ok) throw new Error('Failed to disconnect');
            await fetchConnections();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        }
    }, [fetchConnections]);

    const refreshOAuthToken = useCallback(async (connectionId: string) => {
        try {
            const res = await fetch(`${API_BASE}/connections/${connectionId}/refresh_token/`, {
                method: 'POST',
            });
            if (!res.ok) throw new Error('Failed to refresh token');
            return await res.json();
        } catch (err) {
            if (err instanceof Error) setError(err.message);
            throw err;
        }
    }, []);

    const triggerSync = useCallback(async (connectionId: string, syncType = 'two_way'): Promise<SyncStatus> => {
        try {
            const res = await fetch(`${API_BASE}/connections/${connectionId}/sync/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sync_type: syncType }),
            });
            if (!res.ok) throw new Error('Sync failed');
            return await res.json();
        } catch (err) {
            if (err instanceof Error) setError(err.message);
            throw err;
        }
    }, []);

    // Webhooks Management
    const [webhooks, setWebhooks] = useState<WebhookEndpoint[]>([]);

    const fetchWebhooks = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/webhooks/`);
            if (res.ok) {
                const data = await res.json();
                setWebhooks(data.results || data);
            }
        } catch (err) {
            console.error(err);
        }
    }, []);

    const createWebhook = useCallback(async (data: Partial<WebhookEndpoint>) => {
        try {
            const res = await fetch(`${API_BASE}/webhooks/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!res.ok) throw new Error('Failed to create webhook');
            await fetchWebhooks();
        } catch (err) {
            if (err instanceof Error) setError(err.message);
            throw err;
        }
    }, [fetchWebhooks]);

    const testWebhook = useCallback(async (webhookId: string): Promise<WebhookLog> => {
        try {
            const res = await fetch(`${API_BASE}/webhooks/${webhookId}/test/`, {
                method: 'POST',
            });
            if (!res.ok) throw new Error('Failed to test webhook');
            return await res.json();
        } catch (err) {
            throw err;
        }
    }, []);

    useEffect(() => {
        fetchProviders();
        fetchConnections();
        fetchWebhooks();
    }, [fetchProviders, fetchConnections, fetchWebhooks]);

    return {
        isLoading,
        error,
        providers,
        connections,
        webhooks,
        refreshIntegrations: fetchConnections,
        disconnectIntegration,
        refreshOAuthToken,
        triggerSync,
        fetchWebhooks,
        createWebhook,
        testWebhook,
    };
}

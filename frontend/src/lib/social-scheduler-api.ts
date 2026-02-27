import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1/social-scheduler',
});

// Add auth interceptor
api.interceptors.request.use((config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

export const socialSchedulerAPI = {
    getAccounts: async () => {
        const response = await api.get('/accounts/');
        return response.data;
    },

    connectAccount: async (platform: string, accountName: string, accessToken: string) => {
        // In a real flow, this would handle OAuth callbacks. For simulation we just mock token injection
        const response = await api.post('/accounts/', {
            platform,
            account_name: accountName,
            access_token: accessToken,
            account_id: `mock_id_${Math.random()}`
        });
        return response.data;
    },

    schedulePost: async (content: string, scheduledTime: string, accountIds: string[], mediaUrl?: string) => {
        const response = await api.post('/posts/', {
            content,
            scheduled_time: scheduledTime,
            accounts: accountIds,
            media_url: mediaUrl,
        });
        return response.data;
    },

    getScheduledPosts: async () => {
        const response = await api.get('/posts/');
        return response.data;
    }
};

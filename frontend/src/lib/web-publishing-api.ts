import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1/web-publishing',
});

api.interceptors.request.use((config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

export const webPublishingAPI = {
    getSites: async () => {
        const response = await api.get('/sites/');
        return response.data;
    },

    publishSite: async (projectId: number, subdomain: string, customDomain?: string) => {
        const response = await api.post('/sites/', {
            project_id: projectId,
            subdomain,
            custom_domain: customDomain,
        });
        return response.data;
    }
};

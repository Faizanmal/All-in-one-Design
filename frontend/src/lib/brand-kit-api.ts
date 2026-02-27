import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1/brand-kit',
});

api.interceptors.request.use((config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }
    return config;
});

export const brandKitAPI = {
    getEnforcementRules: async (designSystemId: string) => {
        const response = await api.get(`/enforcement/`, {
            params: { design_system_id: designSystemId }
        });
        return response.data;
    },

    updateEnforcementRules: async (enforcementId: string, data: any) => {
        const response = await api.patch(`/enforcement/${enforcementId}/`, data);
        return response.data;
    },

    logViolation: async (enforcementId: string, eventType: string, details: any) => {
        const response = await api.post(`/violations/`, {
            enforcement: enforcementId,
            event_type: eventType,
            details
        });
        return response.data;
    }
};

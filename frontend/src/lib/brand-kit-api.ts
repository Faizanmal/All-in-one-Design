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

interface EnforcementRuleData {
    [key: string]: unknown;
}

interface ViolationDetails {
    [key: string]: unknown;
}

export const brandKitAPI = {
    getEnforcementRules: async (designSystemId: string) => {
        const response = await api.get(`/enforcement/`, {
            params: { design_system_id: designSystemId }
        });
        return response.data;
    },

    updateEnforcementRules: async (enforcementId: string, data: EnforcementRuleData) => {
        const response = await api.patch(`/enforcement/${enforcementId}/`, data);
        return response.data;
    },

    logViolation: async (enforcementId: string, eventType: string, details: ViolationDetails) => {
        const response = await api.post(`/violations/`, {
            enforcement: enforcementId,
            event_type: eventType,
            details
        });
        return response.data;
    }
};

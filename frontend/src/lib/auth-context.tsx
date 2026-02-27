"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Types
export interface User {
  id: number;
  email: string;
  name: string;
  username?: string;
  avatar?: string;
  emailVerified?: boolean;
  providers?: string[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export type AuthProvider = 'email' | 'google' | 'github' | 'firebase';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  // Email/Password Auth
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  
  // OAuth Methods
  loginWithGoogle: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  loginWithFirebase: (idToken: string) => Promise<void>;
  
  // OAuth Callbacks
  handleGoogleCallback: (code: string, state: string) => Promise<void>;
  handleGitHubCallback: (code: string, state: string) => Promise<void>;
  
  // Token Management
  refreshToken: () => Promise<boolean>;
  verifyToken: () => Promise<boolean>;
  
  // User Management
  updateUser: (data: Partial<User>) => Promise<void>;
  getSecurityProfile: () => Promise<SecurityProfile>;
  getLoginHistory: () => Promise<LoginAttempt[]>;
  
  // OAuth Connections
  listConnections: () => Promise<OAuthConnection[]>;
  disconnectProvider: (provider: AuthProvider) => Promise<void>;
  
  // Utilities
  clearError: () => void;
}

interface SecurityProfile {
  two_factor_enabled: boolean;
  two_factor_method: string;
  password_changed_at: string | null;
  last_login_ip: string | null;
  last_login_at: string | null;
  is_locked: boolean;
  active_sessions_count: number;
}

interface LoginAttempt {
  timestamp: string;
  ip_address: string;
  success: boolean;
  provider: string | null;
  failure_reason: string | null;
  country: string | null;
  city: string | null;
}

interface OAuthConnection {
  id: string;
  provider: string;
  provider_email: string;
  provider_username: string;
  is_primary: boolean;
  created_at: string;
  last_used_at: string | null;
}

// API Configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage Keys
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
} as const;

// Auth Provider Component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  const clearAuthState = () => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER);
    
    setState({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  };

  // Token Verification
  const verifyTokenInternal = async (token: string): Promise<boolean> => {
    try {
      await fetch(`${API_URL}/token/verify/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      return true;
    } catch {
      return false;
    }
  };

  const verifyToken = async (): Promise<boolean> => {
    if (!state.tokens?.access) return false;
    return verifyTokenInternal(state.tokens.access);
  };

  // Token Refresh
  const refreshTokenInternal = async (refreshToken: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_URL}/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      const newTokens = {
        access: data.access,
        refresh: data.refresh || refreshToken,
      };

      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, newTokens.access);
      if (data.refresh) {
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, newTokens.refresh);
      }

      setState(prev => ({
        ...prev,
        tokens: newTokens,
        isLoading: false,
      }));

      return true;
    } catch {
      return false;
    }
  };

  const refreshToken = async (): Promise<boolean> => {
    if (!state.tokens?.refresh) return false;
    return refreshTokenInternal(state.tokens.refresh);
  };

  // Fetch Current User
  const fetchCurrentUser = async (token: string) => {
    try {
      const response = await fetch(`${API_URL}/v1/auth/users/me/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const user = await response.json();
        localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
        setState(prev => ({ ...prev, user }));
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
    }
  };



  // Initialize auth state from storage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const accessToken = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
        const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        const storedUser = localStorage.getItem(STORAGE_KEYS.USER);

        if (accessToken && refreshToken) {
          // Verify token is still valid
          const isValid = await verifyTokenInternal(accessToken);
          
          if (isValid) {
            setState({
              user: storedUser ? JSON.parse(storedUser) : null,
              tokens: { access: accessToken, refresh: refreshToken },
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            // Fetch fresh user data
            fetchCurrentUser(accessToken);
          } else {
            // Try to refresh token
            const refreshed = await refreshTokenInternal(refreshToken);
            if (!refreshed) {
              clearAuthState();
            }
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        clearAuthState();
      }
    };

    initializeAuth();
  }, []);

  const setAuthState = (tokens: AuthTokens, user: User) => {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokens.access);
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokens.refresh);
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
    
    setState({
      user,
      tokens,
      isAuthenticated: true,
      isLoading: false,
      error: null,
    });
  };

  const setError = (error: string) => {
    setState(prev => ({ ...prev, error, isLoading: false }));
  };

  const clearError = () => {
    setState(prev => ({ ...prev, error: null }));
  };

  // API Helper
  const apiRequest = async (
    endpoint: string,
    options: RequestInit = {},
    requiresAuth: boolean = false
  ) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (requiresAuth && state.tokens?.access) {
      headers['Authorization'] = `Bearer ${state.tokens.access}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.detail || 'Request failed');
    }

    return response.json();
  };

  // Email/Password Login
  const login = async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await fetch(`${API_URL}/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Invalid credentials');
      }

      const data = await response.json();
      const tokens = { access: data.access, refresh: data.refresh };

      // Fetch user data
      const userResponse = await fetch(`${API_URL}/v1/auth/users/me/`, {
        headers: { Authorization: `Bearer ${tokens.access}` },
      });

      const user = userResponse.ok ? await userResponse.json() : { email };

      setAuthState(tokens, user);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Login failed';
      setError(message);
      throw error;
    }
  };

  // Register
  const register = async (name: string, email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      await apiRequest('/v1/auth/register/', {
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
      });

      // Auto-login after registration
      await login(email, password);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Registration failed';
      setError(message);
      throw error;
    }
  };

  // Logout
  const logout = async () => {
    clearAuthState();
  };

  // Google OAuth
  const loginWithGoogle = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await apiRequest('/v1/auth/oauth/google/');
      
      // Store state for callback verification
      sessionStorage.setItem('oauth_state', data.state);
      
      // Redirect to Google
      window.location.href = data.authorization_url;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to initiate Google login';
      setError(message);
      throw error;
    }
  };

  const handleGoogleCallback = async (code: string, state: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      // Verify state matches
      const storedState = sessionStorage.getItem('oauth_state');
      if (storedState && storedState !== state) {
        throw new Error('Invalid OAuth state');
      }
      sessionStorage.removeItem('oauth_state');

      const data = await apiRequest('/v1/auth/oauth/google/callback/', {
        method: 'POST',
        body: JSON.stringify({ code, state }),
      });

      setAuthState(data.tokens, data.user);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Google authentication failed';
      setError(message);
      throw error;
    }
  };

  // GitHub OAuth
  const loginWithGitHub = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await apiRequest('/v1/auth/oauth/github/');
      
      sessionStorage.setItem('oauth_state', data.state);
      window.location.href = data.authorization_url;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to initiate GitHub login';
      setError(message);
      throw error;
    }
  };

  const handleGitHubCallback = async (code: string, state: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const storedState = sessionStorage.getItem('oauth_state');
      if (storedState && storedState !== state) {
        throw new Error('Invalid OAuth state');
      }
      sessionStorage.removeItem('oauth_state');

      const data = await apiRequest('/v1/auth/oauth/github/callback/', {
        method: 'POST',
        body: JSON.stringify({ code, state }),
      });

      setAuthState(data.tokens, data.user);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'GitHub authentication failed';
      setError(message);
      throw error;
    }
  };

  // Firebase Auth
  const loginWithFirebase = async (idToken: string) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const data = await apiRequest('/v1/auth/oauth/firebase/verify/', {
        method: 'POST',
        body: JSON.stringify({ id_token: idToken }),
      });

      setAuthState(data.tokens, data.user);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Firebase authentication failed';
      setError(message);
      throw error;
    }
  };

  // User Management
  const updateUser = async (data: Partial<User>) => {
    const response = await apiRequest('/v1/auth/users/me/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }, true);

    setState(prev => ({ ...prev, user: { ...prev.user!, ...response } }));
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify({ ...state.user, ...response }));
  };

  // Security Profile
  const getSecurityProfile = async (): Promise<SecurityProfile> => {
    return apiRequest('/v1/auth/security/profile/', {}, true);
  };

  const getLoginHistory = async (): Promise<LoginAttempt[]> => {
    const data = await apiRequest('/v1/auth/security/login-history/', {}, true);
    return data.login_history;
  };

  // OAuth Connections
  const listConnections = async (): Promise<OAuthConnection[]> => {
    const data = await apiRequest('/v1/auth/oauth/connections/', {}, true);
    return data.connections;
  };

  const disconnectProvider = async (provider: AuthProvider) => {
    await apiRequest(`/v1/auth/oauth/disconnect/${provider}/`, {
      method: 'DELETE',
    }, true);
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    loginWithGoogle,
    loginWithGitHub,
    loginWithFirebase,
    handleGoogleCallback,
    handleGitHubCallback,
    refreshToken,
    verifyToken,
    updateUser,
    getSecurityProfile,
    getLoginHistory,
    listConnections,
    disconnectProvider,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook for using auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// HOC for protected routes
export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  redirectTo: string = '/login'
) {
  return function AuthenticatedComponent(props: P) {
    const { isAuthenticated, isLoading } = useAuth();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
      setMounted(true);
    }, []);

    useEffect(() => {
      if (mounted && !isLoading && !isAuthenticated) {
        window.location.href = redirectTo;
      }
    }, [mounted, isLoading, isAuthenticated]);

    if (!mounted || isLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return null;
    }

    return <WrappedComponent {...props} />;
  };
}

export default AuthContext;

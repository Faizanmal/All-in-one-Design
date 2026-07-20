/**
 * Canonical JWT storage helpers.
 * Prefer `access_token`; keep `auth_token` in sync for legacy call sites.
 */

export const ACCESS_TOKEN_KEY = 'access_token';
export const REFRESH_TOKEN_KEY = 'refresh_token';
export const LEGACY_AUTH_TOKEN_KEY = 'auth_token';

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return (
    localStorage.getItem(ACCESS_TOKEN_KEY) ||
    localStorage.getItem(LEGACY_AUTH_TOKEN_KEY)
  );
}

export function setAccessToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
  localStorage.setItem(LEGACY_AUTH_TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(LEGACY_AUTH_TOKEN_KEY);
}

export function clearAuthTokens(): void {
  if (typeof window === 'undefined') return;
  clearAccessToken();
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getBearerAuthHeader(): Record<string, string> {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

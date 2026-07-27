import { describe, it, expect, beforeEach } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '@/stores/auth';

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();
  });

  it('starts unauthenticated', () => {
    const store = useAuthStore();
    expect(store.isAuthenticated).toBe(false);
    expect(store.accessToken).toBeNull();
    expect(store.user).toBeNull();
  });

  it('setTokens stores tokens and marks authenticated', () => {
    const store = useAuthStore();
    store.setTokens('access-123', 'refresh-456');
    expect(store.isAuthenticated).toBe(true);
    expect(store.accessToken).toBe('access-123');
    expect(store.refreshToken).toBe('refresh-456');
    expect(localStorage.getItem('isekai_access_token')).toBe('access-123');
    expect(localStorage.getItem('isekai_refresh_token')).toBe('refresh-456');
  });

  it('setUser stores user info', () => {
    const store = useAuthStore();
    store.setUser({
      id: 'u1',
      email: 'test@example.com',
      onboardingCompleted: false,
      emailVerified: true,
    });
    expect(store.user).not.toBeNull();
    expect(store.user?.email).toBe('test@example.com');
    expect(store.user?.onboardingCompleted).toBe(false);
  });

  it('logout clears everything', () => {
    const store = useAuthStore();
    store.setTokens('access-123', 'refresh-456');
    store.setUser({
      id: 'u1',
      email: 'test@example.com',
      onboardingCompleted: true,
      emailVerified: true,
    });
    store.logout();
    expect(store.isAuthenticated).toBe(false);
    expect(store.accessToken).toBeNull();
    expect(store.refreshToken).toBeNull();
    expect(store.user).toBeNull();
    expect(localStorage.getItem('isekai_access_token')).toBeNull();
  });
});

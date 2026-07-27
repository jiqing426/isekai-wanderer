import { api } from './http';
import type { AuthTokens, LoginRequest, RegisterRequest } from '@/types/auth';

export const authApi = {
  login(data: LoginRequest): Promise<AuthTokens> {
    return api.post('/auth/login', data);
  },

  register(data: RegisterRequest): Promise<AuthTokens & { id: string; email: string; display_name: string }> {
    return api.post('/auth/register', data);
  },

  verifyEmail(token: string): Promise<{ message: string }> {
    return api.post('/auth/verify-email', { token });
  },

  resendVerification(): Promise<{ message: string }> {
    return api.post('/auth/resend-verification');
  },

  refreshToken(refreshToken: string): Promise<AuthTokens> {
    return api.post('/auth/refresh', { refresh_token: refreshToken });
  },

  forgotPassword(email: string): Promise<{ message: string }> {
    return api.post('/auth/forgot-password', { email });
  },

  resetPassword(token: string, password: string): Promise<{ message: string }> {
    return api.post('/auth/reset-password', { token, new_password: password });
  },

  getProfile(): Promise<{ id: string; email: string; display_name?: string; avatar_url?: string; onboarding_completed: boolean; email_verified: boolean }> {
    return api.get('/user/profile', { skipAutoLogout: true });
  },

  updateOnboardingCompleted(): Promise<void> {
    return api.put('/user/profile', { onboarding_completed: true });
  },

  oauthCallback(provider: string, code: string): Promise<AuthTokens> {
    return api.get(`/auth/oauth/${provider}/callback?code=${encodeURIComponent(code)}`);
  },

  oauthLogin(provider: string, code: string): Promise<AuthTokens & { user_id: string; email: string; display_name: string; provider: string }> {
    return api.post(`/auth/oauth/${provider}`, { code });
  },
};

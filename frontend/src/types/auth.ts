export interface User {
  id: string;
  email: string;
  displayName?: string;
  onboardingCompleted: boolean;
  emailVerified: boolean;
  avatar?: string;
  username?: string;
  subscription_tier?: 'free' | 'basic' | 'standard' | 'premium';
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface ApiError {
  error_code: string;
  detail: string;
}

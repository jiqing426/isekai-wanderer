/**
 * User-related types from API Contract (CR-008)
 */

export interface UserProfile {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  signature: string | null;
  email_verified: boolean;
  subscription_tier: 'free' | 'basic' | 'standard' | 'premium';
  preferred_genre: string | null;
  locale: string;
  onboarding_completed: boolean;
  created_at: string;
}

export interface ProfileUpdateRequest {
  display_name?: string;
  avatar_url?: string;
  signature?: string;
  locale?: string;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

export interface SubscriptionStatus {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  status: 'active' | 'trialing' | 'cancelled' | 'expired';
  trial_started_at: string | null;
  trial_ends_at: string | null;
  renew_at: string | null;
}

export interface PlaySetting {
  typing_speed: 'slow' | 'normal' | 'fast' | 'instant';
  auto_play: boolean;
  auto_play_delay_ms: number;
  bgm_volume: number;
  sfx_volume: number;
}

export interface NotifySetting {
  update_notify: boolean;
  activity_reminder: boolean;
  ending_unlock: boolean;
  checkin_push: boolean;
  affection_change: boolean;
  new_script: boolean;
}

export interface LoginDevice {
  id: string;
  device_name: string;
  device_type: 'ios' | 'android' | 'web' | 'desktop';
  browser: string;
  os: string;
  ip_address: string;
  location: string | null;
  last_active_at: string;
  is_current: boolean;
  created_at: string;
}

export interface DeviceList {
  devices: LoginDevice[];
  total: number;
}

export interface BillRecord {
  id: string;
  type: 'subscription' | 'purchase' | 'refund';
  description: string;
  amount: number;
  currency: string;
  created_at: string;
}

export interface MemberInfo {
  tier: 'free' | 'basic' | 'standard' | 'premium';
  status: 'active' | 'inactive' | 'cancelled' | 'trialing';
  member_since: string | null;
  expires_at: string | null;
  auto_renew: boolean;
  fragment_balance: number;
  benefits: string[];
  recent_bills: BillRecord[];
}

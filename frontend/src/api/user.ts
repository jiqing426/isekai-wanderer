/**
 * User API functions (CR-008)
 * All endpoints require Bearer token authentication
 */

import { api } from './http';
import type { 
  UserProfile, 
  ProfileUpdateRequest, 
  ChangePasswordRequest, 
  SubscriptionStatus,
  PlaySetting,
  NotifySetting,
  DeviceList,
  MemberInfo
} from '@/types/user';
import type {
  UserStats,
  UserAsset,
  SignInfo,
  LatestSave,
  MemorySummary,
  BondList,
  EndingsList,
  RecentEndings,
  FullMemoryList,
} from '@/types/personal-center';

// ── User Profile APIs ──

export function getMe() {
  return api.get<UserProfile>('/users/me');
}

export function updateMe(data: ProfileUpdateRequest) {
  return api.patch<UserProfile>('/users/me', data);
}

export function changePassword(data: ChangePasswordRequest) {
  return api.post<{ status: string; message: string }>('/users/me/change-password', data);
}

export function deleteAccount() {
  return api.delete<{ status: string; message: string }>('/users/me');
}

export function getMySubscription() {
  return api.get<SubscriptionStatus>('/users/me/subscription');
}

// ── Personal Center APIs ──

export function getMyStats() {
  return api.get<UserStats>('/users/me/stats');
}

export function getMyAsset() {
  return api.get<UserAsset>('/users/me/asset');
}

export function getSignInfo() {
  return api.get<SignInfo>('/sign/info');
}

export function getLatestSave() {
  return api.get<LatestSave | null>('/users/me/latest-save');
}

export function getMemorySummary() {
  return api.get<MemorySummary>('/users/me/memory/summary');
}

export function getCharacterBond() {
  return api.get<BondList>('/users/me/characters/bond');
}

export function getMyEndings() {
  return api.get<EndingsList>('/users/me/endings');
}

export function getRecentEndings() {
  return api.get<RecentEndings>('/users/me/endings/recent');
}

export function getFullMemory() {
  return api.get<FullMemoryList>('/users/me/memory/full');
}

// ── Settings APIs (CR-008 w07-settings v4.2) ──

export function getPlaySetting() {
  return api.get<PlaySetting>('/users/me/play-setting');
}

export function updatePlaySetting(data: Partial<PlaySetting>) {
  return api.patch<PlaySetting>('/users/me/play-setting', data);
}

export function getNotifySetting() {
  return api.get<NotifySetting>('/users/me/notify-setting');
}

export function updateNotifySetting(data: Partial<NotifySetting>) {
  return api.patch<NotifySetting>('/users/me/notify-setting', data);
}

export function getDevices() {
  return api.get<DeviceList>('/users/me/devices');
}

export function logoutDevice(deviceId: string) {
  return api.post<{ status: string; message: string; device_id: string }>(`/users/me/devices/${deviceId}/logout`);
}

export function getMemberInfo() {
  return api.get<MemberInfo>('/users/me/member-info');
}

// ── Achievements API ──

export interface UserAchievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
  claimed: boolean;
  progress: number;
  reward: number;
}

export function getMyAchievements(): Promise<{ achievements: UserAchievement[] }> {
  return api.get('/users/me/achievements');
}

// ── CR-009: Personal Center Enhancement APIs ──

export function dailyCheckin(): Promise<{
  status: 'ok';
  fragments_earned: number;
  streak_days: number;
  message: string;
}> {
  return api.post('/daily/checkin');
}

export function getGameStats(): Promise<{
  total_play_time_minutes: number;
  total_sessions: number;
  completed_sessions: number;
  total_choices: number;
  total_dialogues: number;
  favorite_character_id: string;
  favorite_character_name: string;
}> {
  return api.get('/users/me/game-stats');
}

export function getLatestSession(): Promise<{
  session_id: string;
  script_id: string;
  script_name: string;
  script_cover_url: string;
  current_node_id: string;
  last_played_at: string;
  progress: number;
} | null> {
  return api.get('/users/me/latest-session');
}

// ── Avatar Upload API ──

export function uploadAvatar(file: File): Promise<{ avatar_url: string }> {
  const doUpload = async (token: string): Promise<Response> => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch('/api/v1/users/me/avatar', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  };

  const tryRefresh = async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('isekai_refresh_token');
    if (!refreshToken) return null;
    
    try {
      const refreshRes = await fetch('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json();
        localStorage.setItem('isekai_access_token', data.access_token);
        localStorage.setItem('isekai_refresh_token', data.refresh_token);
        return data.access_token;
      }
    } catch {
      // refresh failed
    }
    return null;
  };

  return (async () => {
    let accessToken = localStorage.getItem('isekai_access_token');
    
    // If no token, try refresh first
    if (!accessToken) {
      accessToken = await tryRefresh();
      if (!accessToken) {
        throw new Error('未登录，请先登录');
      }
    }
    
    let response = await doUpload(accessToken);
    
    // If 401, try refresh and retry
    if (response.status === 401) {
      const newToken = await tryRefresh();
      if (newToken) {
        response = await doUpload(newToken);
      }
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: '上传失败' }));
      throw new Error(error.message || '上传失败');
    }
    
    return response.json();
  })();
}

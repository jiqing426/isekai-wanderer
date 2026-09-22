import { defHttp } from '@/utils/http/axios';

// The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

export interface UserSummary {
  id: string;
  email: string;
  display_name?: string;
  is_admin: boolean;
  email_verified: boolean;
  subscription_tier: string;
  created_at?: string;
  last_login?: string;
}

export interface UserDetail extends UserSummary {
  avatar_url?: string;
  oauth_provider?: string;
  locale?: string;
  onboarding_completed?: boolean;
  updated_at?: string;
}

export interface UserListResponse {
  items: UserSummary[];
  total: number;
  page: number;
  page_size: number;
}

export interface UserUpdatePayload {
  display_name?: string;
  is_admin?: boolean;
  email_verified?: boolean;
}

export const userManagementApi = {
  getAll(params?: {
    page?: number;
    page_size?: number;
    search?: string;
  }): Promise<UserListResponse> {
    return defHttp.get<UserListResponse>(
      { url: '/admin/users', params },
      { isTransformResponse: false },
    );
  },

  get(userId: string): Promise<UserDetail> {
    return defHttp.get<UserDetail>(
      { url: `/admin/users/${userId}` },
      { isTransformResponse: false },
    );
  },

  update(
    userId: string,
    payload: UserUpdatePayload,
  ): Promise<UserDetail> {
    return defHttp.patch<UserDetail>(
      { url: `/admin/users/${userId}`, data: payload },
      { isTransformResponse: false },
    );
  },
};

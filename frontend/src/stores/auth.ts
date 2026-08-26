import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/auth';

const ACCESS_TOKEN_KEY = 'isekai_access_token';
const REFRESH_TOKEN_KEY = 'isekai_refresh_token';
const TOKEN_ISSUED_AT_KEY = 'isekai_token_issued_at';

// Token 有效期（毫秒）
const ACCESS_TOKEN_LIFETIME = 24 * 60 * 60 * 1000; // 24 小时
const REFRESH_THRESHOLD = 5 * 60 * 1000; // 提前 5 分钟刷新

// Cookie 工具函数
function setCookie(name: string, value: string, days: number = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

function removeCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(getCookie(ACCESS_TOKEN_KEY));
  const refreshToken = ref<string | null>(getCookie(REFRESH_TOKEN_KEY));
  const tokenIssuedAt = ref<number>(parseInt(localStorage.getItem(TOKEN_ISSUED_AT_KEY) || '0'));
  const user = ref<User | null>(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!accessToken.value);

  // 检查 token 是否即将过期
  function isTokenExpiringSoon(): boolean {
    if (!tokenIssuedAt.value) return false;
    const elapsed = Date.now() - tokenIssuedAt.value;
    const remaining = ACCESS_TOKEN_LIFETIME - elapsed;
    return remaining < REFRESH_THRESHOLD;
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access;
    refreshToken.value = refresh;
    tokenIssuedAt.value = Date.now();
    // Access token: 7 天（cookie 过期时间），Refresh token: 30 天
    setCookie(ACCESS_TOKEN_KEY, access, 7);
    setCookie(REFRESH_TOKEN_KEY, refresh, 30);
    // 记录 token 获取时间（用于判断是否需要提前刷新）
    localStorage.setItem(TOKEN_ISSUED_AT_KEY, tokenIssuedAt.value.toString());
  }

  function setUser(u: User) {
    user.value = u;
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    tokenIssuedAt.value = 0;
    user.value = null;
    removeCookie(ACCESS_TOKEN_KEY);
    removeCookie(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_ISSUED_AT_KEY);
  }

  // 从 cookie 同步 token（用于多 tab 场景）
  function syncFromCookie() {
    const newAccessToken = getCookie(ACCESS_TOKEN_KEY);
    const newRefreshToken = getCookie(REFRESH_TOKEN_KEY);
    const newIssuedAt = parseInt(localStorage.getItem(TOKEN_ISSUED_AT_KEY) || '0');
    
    if (newAccessToken !== accessToken.value) {
      accessToken.value = newAccessToken;
      if (!newAccessToken) {
        user.value = null;
      }
    }
    
    if (newRefreshToken !== refreshToken.value) {
      refreshToken.value = newRefreshToken;
    }
    
    if (newIssuedAt !== tokenIssuedAt.value) {
      tokenIssuedAt.value = newIssuedAt;
    }
  }

  return {
    accessToken,
    refreshToken,
    tokenIssuedAt,
    user,
    loading,
    isAuthenticated,
    isTokenExpiringSoon,
    setTokens,
    setUser,
    logout,
    syncFromCookie,
  };
});

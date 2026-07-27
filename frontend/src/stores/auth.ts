import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/auth';

const ACCESS_TOKEN_KEY = 'isekai_access_token';
const REFRESH_TOKEN_KEY = 'isekai_refresh_token';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(
    typeof localStorage !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null,
  );
  const refreshToken = ref<string | null>(
    typeof localStorage !== 'undefined' ? localStorage.getItem(REFRESH_TOKEN_KEY) : null,
  );
  const user = ref<User | null>(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!accessToken.value);

  function setTokens(access: string, refresh: string) {
    accessToken.value = access;
    refreshToken.value = refresh;
    localStorage.setItem(ACCESS_TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }

  function setUser(u: User) {
    user.value = u;
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  // 从 localStorage 同步 token（用于测试场景或外部修改）
  function syncFromLocalStorage() {
    if (typeof localStorage !== 'undefined') {
      const newAccessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      const newRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
      
      if (newAccessToken !== accessToken.value) {
        accessToken.value = newAccessToken;
        if (!newAccessToken) {
          user.value = null;
        }
      }
      
      if (newRefreshToken !== refreshToken.value) {
        refreshToken.value = newRefreshToken;
      }
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    loading,
    isAuthenticated,
    setTokens,
    setUser,
    logout,
    syncFromLocalStorage,
  };
});

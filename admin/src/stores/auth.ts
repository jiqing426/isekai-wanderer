import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/http';

const ACCESS_TOKEN_KEY = 'isekai_admin_access_token';

interface User {
  id: string;
  email: string;
  display_name?: string;
  is_admin: boolean;
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_TOKEN_KEY));
  const user = ref<User | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value);
  const isAdmin = computed(() => user.value?.is_admin ?? false);

  async function login(email: string, password: string) {
    const data = await api.post<{ access_token: string; refresh_token: string }>(
      '/auth/login',
      { email, password }
    );
    accessToken.value = data.access_token;
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    await fetchProfile();
  }

  async function fetchProfile() {
    try {
      const profile = await api.get<User & { is_admin?: boolean }>('/user/profile');
      user.value = {
        id: profile.id,
        email: profile.email,
        display_name: profile.display_name,
        is_admin: profile.is_admin ?? false,
      };
    } catch (err) {
      console.error('Failed to fetch profile:', err);
    }
  }

  function logout() {
    accessToken.value = null;
    user.value = null;
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  }

  function syncFromStorage() {
    accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    isAdmin,
    login,
    fetchProfile,
    logout,
    syncFromStorage,
  };
});

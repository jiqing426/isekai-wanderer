<template>
  <div class="page-bg">
    <div class="callback-page">
      <div class="callback-card glass-card fade-in-up">
        <div v-if="loading" class="callback-loading">
          <n-spin size="large" />
          <p>{{ $t('oauth.loggingIn') }}</p>
        </div>
        <div v-else-if="error" class="callback-error">
          <div class="error-icon">✗</div>
          <h2>{{ $t('oauth.loginFailed') }}</h2>
          <p>{{ error }}</p>
          <n-button type="primary" @click="$router.push('/login')">{{ $t('oauth.backToLogin') }}</n-button>
        </div>
        <div v-else class="callback-success">
          <div class="success-icon">✓</div>
          <h2>{{ $t('oauth.loginSuccess') }}</h2>
          <p>{{ $t('oauth.redirecting') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { authApi } from '@/api/auth';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const message = useMessage();
const auth = useAuthStore();

const loading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  const code = route.query.code as string;
  const provider = (route.query.provider as string) || 'google';

  if (!code) {
    error.value = t('oauth.missingCallback');
    loading.value = false;
    return;
  }

  try {
    const resp = await authApi.oauthLogin(provider, code);
    auth.setTokens(resp.access_token, resp.refresh_token);
    auth.setUser({
      id: resp.user_id,
      email: resp.email,
      displayName: resp.display_name,
      onboardingCompleted: false,
      emailVerified: true,
    });

    try {
      const profile = await authApi.getProfile();
      auth.setUser({
        id: profile.id,
        email: profile.email,
        displayName: profile.display_name,
        onboardingCompleted: profile.onboarding_completed,
        emailVerified: profile.email_verified,
      });
      message.success(t('oauth.providerLoginSuccess', { provider }));
      router.push(profile.onboarding_completed ? '/discover' : '/onboarding');
    } catch (err) {
      console.warn('getProfile failed:', err instanceof Error ? err.message : err);
      router.push('/discover');
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('oauth.oauthFailed');
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.callback-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 16px; }
.callback-card { width: 100%; max-width: 400px; padding: 48px 36px; text-align: center; }
.callback-loading p { color: var(--text-muted); font-size: 14px; margin-top: 16px; }
.success-icon, .error-icon { width: 64px; height: 64px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-size: 32px; font-weight: 700; }
.success-icon { background: rgba(134, 239, 172, 0.15); color: #86efac; }
.error-icon { background: rgba(248, 113, 113, 0.15); color: #f87171; }
.callback-success h2, .callback-error h2 { font-size: 20px; font-weight: 700; margin: 0 0 8px; }
.callback-success p, .callback-error p { color: var(--text-muted); font-size: 14px; margin: 0 0 20px; }
</style>

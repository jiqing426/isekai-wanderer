<template>
  <div class="auth-page">
    <!-- Background effects -->
    <div class="auth-bg-effects">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="star-field"></div>
    </div>
    
    <div class="auth-container">
      <!-- Logo -->
      <div class="logo-section">
        <div class="logo">Isekai-Wanderer</div>
      </div>

      <!-- OAuth Buttons -->
      <div class="oauth-section">
        <button class="oauth-btn google-btn" @click="handleGoogleLogin" :disabled="loading">
          <span class="oauth-icon google-icon"></span>
          <span>Google</span>
        </button>
        <button class="oauth-btn discord-btn" @click="handleDiscordLogin" :disabled="loading">
          <span class="oauth-icon discord-icon"></span>
          <span>Discord</span>
        </button>
      </div>

      <!-- Divider -->
      <div class="divider">
        <span class="divider-line"></span>
        <span class="divider-text">{{ t('auth.orLoginWithEmail') }}</span>
        <span class="divider-line"></span>
      </div>

      <!-- Login Form -->
      <form class="auth-form" @submit.prevent="handleEmailLogin">
        <!-- Email Input -->
        <div class="input-group">
          <span class="input-icon">✉️</span>
          <input
            type="email"
            v-model="email"
            :placeholder="t('auth.email')"
            @blur="validateEmail"
            :class="{ error: emailError }"
          />
        </div>
        <div v-if="emailError" class="error-text">{{ emailError }}</div>

        <!-- Password Input -->
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            :placeholder="t('auth.password')"
            @blur="validatePassword"
            :class="{ error: passwordError }"
          />
          <button type="button" class="password-toggle" @click="showPassword = !showPassword">
            {{ showPassword ? '🙈' : '👁️' }}
          </button>
        </div>
        <div v-if="passwordError" class="error-text">{{ passwordError }}</div>

        <!-- Login Button -->
        <button
          type="submit"
          class="auth-btn"
          :disabled="!isFormValid || loading"
          :class="{ loading: loading }"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ t('common.login') }}</span>
        </button>

        <!-- Error Message -->
        <div v-if="loginError" class="auth-error">{{ loginError }}</div>
      </form>

      <!-- Forgot Password + Sign Up -->
      <div class="auth-links">
        <a href="#" class="forgot-link" @click.prevent="goToForgotPassword">{{ t('auth.forgotPassword') }}</a>
        <span class="auth-switch">
          {{ t('auth.noAccount') }} <a href="#" @click.prevent="goToSignup">{{ t('auth.registerNow') }}</a>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { authApi } from '@/api/auth';

const { t } = useI18n();

const router = useRouter();
const route = useRoute();
const message = useMessage();
const authStore = useAuthStore();

// Form state
const email = ref('');
const password = ref('');
const showPassword = ref(false);
const emailError = ref('');
const passwordError = ref('');
const loginError = ref('');
const loading = ref(false);

// Validation
const validateEmail = () => {
  emailError.value = '';
  if (!email.value) {
    emailError.value = t('login.validation.emailRequired');
    return false;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    emailError.value = t('login.validation.emailInvalid');
    return false;
  }
  return true;
};

const validatePassword = () => {
  passwordError.value = '';
  if (!password.value) {
    passwordError.value = t('login.validation.passwordRequired');
    return false;
  }
  if (password.value.length < 6) {
    passwordError.value = t('login.validation.passwordMinLength');
    return false;
  }
  return true;
};

const isFormValid = computed(() => {
  const emailValid = email.value && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value);
  const passwordValid = password.value && password.value.length >= 6;
  return emailValid && passwordValid;
});

// Get redirect path
const getRedirectPath = () => {
  const redirect = route.query.redirect as string;
  return redirect && redirect.startsWith('/') ? redirect : '/';
};

// Track event
const trackEvent = (eventName: string, data?: Record<string, any>) => {
  // TODO: 接入实际的埋点系统
};

// OAuth handlers
const handleGoogleLogin = async () => {
  trackEvent('auth_click_google_login');
  loading.value = true;
  loginError.value = '';

  try {
    const resp = await authApi.oauthLogin('google', `mock_code_${Date.now()}`);
    authStore.setTokens(resp.access_token, resp.refresh_token);
    authStore.setUser({
      id: resp.user_id,
      email: resp.email,
      displayName: resp.display_name,
      onboardingCompleted: false,
      emailVerified: true,
    });
    message.success(t('auth.loginSuccess'));
    router.push(getRedirectPath());
  } catch (error: any) {
    const msg = error?.message || '';
    if (msg.includes('timeout') || msg.includes('TIMEOUT')) {
      message.error(t('login.error.oauthUnavailable'));
    } else if (msg.includes('500') || msg.includes('SERVER_ERROR')) {
      message.error(t('login.error.serverBusy'));
    } else {
      message.error(t('login.error.googleFailed'));
    }
  } finally {
    loading.value = false;
  }
};

const handleDiscordLogin = async () => {
  trackEvent('auth_click_discord_login');
  loading.value = true;
  loginError.value = '';

  try {
    const resp = await authApi.oauthLogin('discord', `mock_code_${Date.now()}`);
    authStore.setTokens(resp.access_token, resp.refresh_token);
    authStore.setUser({
      id: resp.user_id,
      email: resp.email,
      displayName: resp.display_name,
      onboardingCompleted: false,
      emailVerified: true,
    });
    message.success(t('auth.loginSuccess'));
    router.push(getRedirectPath());
  } catch (error: any) {
    const msg = error?.message || '';
    if (msg.includes('timeout') || msg.includes('TIMEOUT')) {
      message.error(t('login.error.oauthUnavailable'));
    } else if (msg.includes('500') || msg.includes('SERVER_ERROR')) {
      message.error(t('login.error.serverBusy'));
    } else {
      message.error(t('login.error.discordFailed'));
    }
  } finally {
    loading.value = false;
  }
};

// Email login handler with debounce
let lastSubmitTime = 0;
const handleEmailLogin = async () => {
  // 300ms 防抖
  const now = Date.now();
  if (now - lastSubmitTime < 300) return;
  lastSubmitTime = now;

  if (!validateEmail() || !validatePassword()) return;

  trackEvent('auth_submit_email_login', { email: email.value });
  loading.value = true;
  loginError.value = '';

  try {
    const tokens = await authApi.login({
      email: email.value,
      password: password.value,
    });
    authStore.setTokens(tokens.access_token, tokens.refresh_token);
    // Fetch user profile
    const profile = await authApi.getProfile();
    authStore.setUser({
      id: profile.id,
      email: profile.email,
      displayName: profile.display_name,
      onboardingCompleted: profile.onboarding_completed,
      emailVerified: profile.email_verified,
    });
    message.success(t('auth.loginSuccess'));
    router.push(getRedirectPath());
  } catch (error: any) {
    const errCode = error?.message || '';
    // 处理不同的错误类型
    if (errCode.includes('USER_NOT_FOUND') || errCode.includes('404')) {
      loginError.value = t('login.error.userNotFound');
    } else if (errCode.includes('INVALID_CREDENTIALS') || errCode.includes('401')) {
      loginError.value = t('login.error.invalidCredentials');
    } else if (errCode.includes('ACCOUNT_BANNED') || errCode.includes('FORBIDDEN')) {
      loginError.value = t('login.error.accountBanned');
    } else if (errCode.includes('500') || errCode.includes('SERVER_ERROR')) {
      loginError.value = t('login.error.serverBusy');
    } else {
      loginError.value = t('login.error.loginFailed');
    }
  } finally {
    loading.value = false;
  }
};

// Go to forgot password
const goToForgotPassword = () => {
  router.push('/forgot-password');
};

// Go to signup
const goToSignup = () => {
  trackEvent('auth_click_goto_signup');
  const redirect = route.query.redirect as string;
  const query = redirect ? { redirect } : {};
  router.push({ path: '/register', query });
};
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
}

/* Background effects */
.auth-bg-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #4F46E5;
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #F472B6;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #fbbf24;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.star-field {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 15% 25%, rgba(192,132,252,.6) 0%, transparent 100%),
    radial-gradient(2px 2px at 35% 55%, rgba(249,168,212,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 55% 15%, rgba(251,191,36,.4) 0%, transparent 100%),
    radial-gradient(2px 2px at 75% 70%, rgba(192,132,252,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 85% 35%, rgba(249,168,212,.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 80%, rgba(251,191,36,.3) 0%, transparent 100%);
}

.auth-container {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

/* Logo */
.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
  text-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
}

/* OAuth Buttons */
.oauth-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.oauth-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.oauth-btn:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.1);
}

.oauth-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.oauth-icon {
  width: 20px;
  height: 20px;
  display: inline-block;
}

.google-icon {
  background: linear-gradient(45deg, #4285f4 25%, #34a853 25%, #34a853 50%, #fbbc05 50%, #fbbc05 75%, #ea4335 75%);
  border-radius: 50%;
}

.discord-icon {
  background: #5865f2;
  border-radius: 4px;
  position: relative;
}

.discord-icon::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 24px 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.divider-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
}

/* Form */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  pointer-events: none;
  z-index: 1;
}

.password-toggle {
  position: absolute;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.password-toggle:hover {
  opacity: 0.7;
}

input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.2s;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

input.error {
  border-color: #ef4444;
}

input.error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}

.error-text {
  font-size: 13px;
  color: #ef4444;
  margin-top: -8px;
  margin-left: 4px;
}

/* Auth Button */
.auth-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.auth-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.auth-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.auth-btn.loading {
  pointer-events: none;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Auth Error */
.auth-error {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #ef4444;
  font-size: 14px;
  text-align: center;
}

/* Auth Switch Link */
.auth-switch {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.auth-links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
}

.forgot-link {
  font-size: 13px;
  color: rgba(192, 132, 252, 0.8);
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: rgba(192, 132, 252, 1);
}

.auth-switch a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.auth-switch a:hover {
  text-decoration: underline;
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .auth-container {
    padding: 32px 24px;
  }

  .logo {
    font-size: 24px;
  }

  .oauth-section {
    flex-direction: column;
  }

  .oauth-btn {
    width: 100%;
  }
}
</style>

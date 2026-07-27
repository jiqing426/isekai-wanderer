<template>
  <div class="page-bg">
    <div class="auth-page">
      <div class="auth-card fade-in-up">
        <div class="auth-header">
          <div class="brand-logo">✦</div>
          <h1 class="gradient-text">{{ $t('auth.resetPassword') }}</h1>
          <p>{{ $t('auth.resetPasswordDesc') }}</p>
        </div>

        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-form-item :label="$t('auth.email')" path="email">
            <n-input v-model:value="form.email" placeholder="your@email.com" type="email" size="large">
              <template #prefix>
                <n-icon :component="MailOutline" />
              </template>
            </n-input>
          </n-form-item>
        </n-form>

        <n-button
          type="primary"
          block
          size="large"
          :loading="submitting"
          :disabled="submitting"
          @click="handleSubmit"
          style="margin-top: 16px"
        >
          {{ $t('auth.sendResetLink') }}
        </n-button>

        <div class="auth-footer">
          <router-link to="/login">{{ $t('auth.loginNow') }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, type FormRules } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { NIcon } from 'naive-ui';
import { MailOutline } from '@vicons/ionicons5';
import { authApi } from '@/api/auth';

const { t } = useI18n();
const router = useRouter();
const message = useMessage();

const form = reactive({ email: '' });

const rules: FormRules = {
  email: [
    { required: true, message: () => t('auth.email'), trigger: 'blur' },
    { type: 'email', message: () => t('auth.email'), trigger: 'blur' },
  ],
};

const submitting = ref(false);

async function handleSubmit() {
  if (!form.email) { message.warning(t('auth.email')); return; }
  submitting.value = true;
  try {
    await authApi.forgotPassword(form.email);
    message.success(t('auth.emailSent'));
    router.push('/login');
  } catch (err) {
    message.error(`${t('common.error')}: ${err instanceof Error ? err.message : ''}`);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.auth-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 16px; }
.auth-card { width: 100%; max-width: 440px; padding: 40px 36px; background: var(--glass-bg, rgba(15, 10, 26, 0.85)); border-radius: 24px; backdrop-filter: blur(20px); border: 1px solid var(--border-color, rgba(167, 139, 250, 0.12)); box-shadow: var(--card-shadow, 0 24px 64px rgba(0, 0, 0, 0.4)); }
.auth-header { text-align: center; margin-bottom: 32px; }
.brand-logo { font-size: 36px; color: var(--brand-primary); margin-bottom: 8px; filter: drop-shadow(0 0 12px rgba(192, 132, 252, 0.4)); }
.auth-header h1 { font-size: 28px; font-weight: 700; margin: 0 0 8px; }
.auth-header p { color: var(--text-muted); font-size: 14px; margin: 0; }
.auth-footer { text-align: center; margin-top: 24px; color: var(--text-muted); font-size: 14px; }
.auth-footer a { color: var(--brand-primary); text-decoration: none; font-weight: 600; }

/* === 移动端适配 === */
</style>

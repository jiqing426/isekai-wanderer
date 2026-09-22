<template>
  <div class="page-bg">
    <div class="auth-page">
      <div class="auth-card fade-in-up">
        <div class="auth-header">
          <div class="brand-logo">✦</div>
          <h1 class="gradient-text">{{ $t('auth.resetTitle') }}</h1>
          <p>{{ $t('auth.newPassword') }}</p>
        </div>

        <n-form ref="formRef" :model="form" :rules="rules" label-placement="top">
          <n-form-item :label="$t('auth.newPassword')" path="password">
            <n-input
              v-model:value="form.password"
              :placeholder="$t('auth.newPassword')"
              type="password"
              show-password-on="click"
              size="large"
            />
          </n-form-item>
          <n-form-item :label="$t('auth.confirmNewPassword')" path="confirmPassword">
            <n-input
              v-model:value="form.confirmPassword"
              :placeholder="$t('auth.confirmNewPassword')"
              type="password"
              show-password-on="click"
              size="large"
            />
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
          {{ $t('auth.resetPassword') }}
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage, type FormRules } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { authApi } from '@/api/auth';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const message = useMessage();

const form = reactive({ password: '', confirmPassword: '' });

const rules: FormRules = {
  password: [{ required: true, message: () => t('auth.password'), trigger: 'blur' }, { min: 8, message: () => t('auth.password'), trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: () => t('auth.confirmPassword'), trigger: 'blur' },
    { validator: (_r: unknown, v: string) => v !== form.password ? new Error('❌') : true, trigger: 'blur' },
  ],
};

const submitting = ref(false);

async function handleSubmit() {
  if (!form.password || !form.confirmPassword) { message.warning(t('auth.password')); return; }
  if (form.password !== form.confirmPassword) { message.warning(t('auth.confirmPassword')); return; }
  
  const token = route.params.token as string;
  submitting.value = true;
  try {
    await authApi.resetPassword(token, form.password);
    message.success(t('auth.resetSuccess'));
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

/* === 移动端适配 === */
@media (max-width: 768px) {
  .auth-page { padding: 8px; }
  .auth-card { padding: 28px 20px; border-radius: 20px; }
  .auth-header { margin-bottom: 24px; }
  .brand-logo { font-size: 30px; }
  .auth-header h1 { font-size: 24px; }
  .auth-header p { font-size: 13px; }
}
</style>

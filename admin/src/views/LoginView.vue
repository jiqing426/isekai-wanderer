<template>
  <div style="max-width: 600px; margin: 100px auto; padding: 24px">
    <n-card title="管理员登录">
      <n-form @submit.prevent="handleLogin">
        <n-form-item label="邮箱">
          <n-input v-model:value="email" type="email" placeholder="admin@example.com" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="password" type="password" placeholder="密码" show-password-on="click" />
        </n-form-item>
        <n-button type="primary" attr-type="submit" :loading="loading" block>
          登录
        </n-button>
        <n-alert v-if="error" type="error" style="margin-top: 16px" :title="error" />
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useMessage } from 'naive-ui';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();
const message = useMessage();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function handleLogin() {
  if (!email.value || !password.value) {
    error.value = '请填写邮箱和密码';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    await auth.login(email.value, password.value);
    if (!auth.isAdmin) {
      auth.logout();
      error.value = '该账号没有管理员权限';
      return;
    }
    message.success('登录成功');
    const redirect = (route.query.redirect as string) || '/';
    router.push(redirect);
  } catch (err: any) {
    error.value = err.message || '登录失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="not-found-page">
    <div style="font-size: 64px; margin-bottom: 16px">🗺️</div>
    <h1>{{ $t('notFound.title') }}</h1>
    <p>{{ $t('notFound.desc') }}</p>
    <n-button type="primary" @click="router.push('/discover')" style="margin-top: 16px">
      {{ $t('notFound.backHome') }}
    </n-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();
</script>

<style scoped>
.not-found-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #e2e8f0;
}
.not-found-page h1 { font-size: 48px; margin-bottom: 8px; }
.not-found-page p { color: #94a3b8; }

</style>

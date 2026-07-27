<template>
  <transition name="slide-up">
    <div v-if="visible" class="notification-prompt glass-card" role="alert" aria-live="polite">
      <div class="prompt-icon">🔔</div>
      <div class="prompt-body">
        <h4 class="prompt-title">{{ $t('notification.title') }}</h4>
        <p class="prompt-desc">{{ $t('notification.desc') }}</p>
      </div>
      <div class="prompt-actions">
        <n-button size="small" @click="handleDismiss" :aria-label="$t('notification.dismiss')">
          {{ $t('notification.dismiss') }}
        </n-button>
        <n-button size="small" type="primary" @click="handleEnable" :loading="requesting">
          {{ $t('notification.enable') }}
        </n-button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { NButton } from 'naive-ui';
import { ref, computed } from 'vue';
import { useNotification } from '@/composables/useNotification';

const { shouldShowPrompt, requestPermission, dismissPrompt } = useNotification();

const visible = computed(() => shouldShowPrompt.value);
const requesting = ref(false);

async function handleEnable() {
  requesting.value = true;
  try {
    await requestPermission();
  } finally {
    requesting.value = false;
  }
}

function handleDismiss() {
  dismissPrompt();
}
</script>

<style scoped>
.notification-prompt {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9000;
  max-width: 340px;
  padding: 16px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  background: rgba(26, 15, 46, 0.92);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(192, 132, 252, 0.25);
  border-radius: 14px;
}
.prompt-icon {
  font-size: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}
.prompt-body {
  flex: 1;
  min-width: 0;
}
.prompt-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #e2d9f3);
  margin: 0 0 2px;
}
.prompt-desc {
  font-size: 12px;
  color: var(--text-muted, #9c8fb8);
  margin: 0;
  line-height: 1.4;
}
.prompt-actions {
  display: flex;
  gap: 8px;
  width: 100%;
  justify-content: flex-end;
}

/* Slide-up transition */
.slide-up-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.slide-up-leave-active {
  transition: all 0.25s ease-in;
}
.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}
</style>

<template>
  <Transition name="toast-fade">
    <div v-if="visible" class="paywall-toast" role="alert">
      <span class="toast-icon">⚠️</span>
      <span class="toast-message">{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  message: string;
  visible: boolean;
}

defineProps<Props>();
</script>

<style scoped>
.paywall-toast {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8500;
  background: rgba(15, 10, 26, 0.95);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 10px;
  padding: 10px 18px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 90vw;
}

.toast-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.toast-message {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.4;
}

/* 动画 */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.25s ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}
</style>

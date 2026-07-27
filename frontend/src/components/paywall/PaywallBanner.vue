<template>
  <Transition name="banner-slide">
    <div v-if="visible" class="paywall-banner" role="banner">
      <div class="banner-content">
        <span class="banner-icon">💎</span>
        <span class="banner-text">{{ text }}</span>
        <button v-if="actionText" class="banner-action" @click="handleAction">
          {{ actionText }}
        </button>
        <button class="banner-close" @click="handleClose" aria-label="关闭">
          ✕
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  text: string;
  actionText?: string;
  visible: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: 'action'): void;
  (e: 'close'): void;
}>();

function handleAction() {
  emit('action');
}

function handleClose() {
  emit('close');
}
</script>

<style scoped>
.paywall-banner {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 8000;
  width: 90vw;
  max-width: 480px;
  background: rgba(15, 10, 26, 0.95);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(16px);
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.banner-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.banner-text {
  flex: 1;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.banner-action {
  flex-shrink: 0;
  padding: 6px 14px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border: none;
  border-radius: 6px;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.banner-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.banner-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.banner-close:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* 动画 */
.banner-slide-enter-active,
.banner-slide-leave-active {
  transition: all 0.3s ease;
}

.banner-slide-enter-from,
.banner-slide-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>

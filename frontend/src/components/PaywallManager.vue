<template>
  <div v-if="visible" class="paywall-manager">
    <!-- 全屏弹窗 -->
    <div v-if="type === 'fullscreen'" class="paywall-fullscreen" @click.self="close">
      <div class="paywall-content">
        <button class="close-btn" @click="close">✕</button>
        <div class="paywall-icon">🔒</div>
        <h2 class="paywall-title">{{ $t('paywallManagerComp.upgradeTitle') }}</h2>
        <p class="paywall-message">{{ message }}</p>
        <div class="paywall-actions">
          <button class="btn-primary" @click="goToSubscription">{{ $t('paywallManagerComp.viewPlans') }}</button>
          <button class="btn-secondary" @click="close">{{ $t('paywallManagerComp.later') }}</button>
        </div>
      </div>
    </div>

    <!-- 横幅 -->
    <div v-else-if="type === 'banner'" class="paywall-banner">
      <div class="banner-content">
        <span class="banner-icon">💎</span>
        <span class="banner-message">{{ message }}</span>
        <button class="banner-btn" @click="goToSubscription">{{ $t('paywallManagerComp.upgrade') }}</button>
        <button class="banner-close" @click="close">✕</button>
      </div>
    </div>

    <!-- Toast 提示 -->
    <div v-else-if="type === 'toast'" class="paywall-toast">
      <div class="toast-content">
        <span class="toast-icon">⚠️</span>
        <span class="toast-message">{{ message }}</span>
        <button class="toast-btn" @click="goToSubscription">{{ $t('paywallManagerComp.learnMore') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { checkPaywall } from '@/api/subscription';

const router = useRouter();
const visible = ref(false);
const type = ref<'fullscreen' | 'banner' | 'toast'>('fullscreen');
const message = ref('');
const scene = ref('');

const props = defineProps<{
  triggerScene?: string;
}>();

async function checkAndShow(triggerScene?: string) {
  if (!triggerScene) return;
  
  try {
    const response = await checkPaywall(triggerScene);
    if (response.should_show) {
      visible.value = true;
      type.value = response.type;
      message.value = response.message;
      scene.value = response.scene;
    }
  } catch (error) {
    console.error('检查付费墙失败:', error);
  }
}

function close() {
  visible.value = false;
}

function goToSubscription() {
  visible.value = false;
  router.push('/subscription');
}

onMounted(() => {
  if (props.triggerScene) {
    checkAndShow(props.triggerScene);
  }
});

defineExpose({
  checkAndShow
});
</script>

<style scoped>
.paywall-manager {
  position: fixed;
  z-index: 9999;
}

/* 全屏弹窗 */
.paywall-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

.paywall-content {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 48px;
  max-width: 480px;
  text-align: center;
  position: relative;
  animation: slideUp 0.3s ease;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--bg-hover);
}

.paywall-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.paywall-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 16px;
  color: var(--text-primary);
}

.paywall-message {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0 0 32px;
  line-height: 1.6;
}

.paywall-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.btn-primary {
  padding: 12px 32px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
}

.btn-secondary {
  padding: 12px 32px;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--bg-hover);
}

/* 横幅 */
.paywall-banner {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  border: 1px solid var(--color-primary);
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideDown 0.3s ease;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.banner-icon {
  font-size: 24px;
}

.banner-message {
  font-size: 14px;
  color: var(--text-primary);
}

.banner-btn {
  padding: 6px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.banner-btn:hover {
  background: var(--color-primary-dark);
}

.banner-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 18px;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-close:hover {
  color: var(--text-primary);
}

/* Toast */
.paywall-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toast-icon {
  font-size: 20px;
}

.toast-message {
  font-size: 14px;
  color: var(--text-primary);
}

.toast-btn {
  padding: 6px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.toast-btn:hover {
  background: var(--color-primary-dark);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>

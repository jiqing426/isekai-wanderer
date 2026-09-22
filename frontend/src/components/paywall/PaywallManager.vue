<template>
  <div v-if="shouldRender" class="paywall-manager-root">
    <!-- 横幅 -->
    <PaywallBanner
      v-if="currentTrigger?.display_type === 'banner'"
      :visible="bannerVisible"
      :text="bannerText"
      :action-text="bannerActionText"
      @action="handleBannerAction"
      @close="handleClose"
    />

    <!-- Toast -->
    <PaywallToast
      v-if="currentTrigger?.display_type === 'toast'"
      :visible="toastVisible"
      :message="toastMessage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSubscriptionStore } from '@/stores/subscription';
import { useI18n } from 'vue-i18n'
import type { PaywallTrigger } from '@/types/subscription';
import PaywallBanner from './PaywallBanner.vue';
import PaywallToast from './PaywallToast.vue';

const { t } = useI18n();
const router = useRouter();
const subscriptionStore = useSubscriptionStore();

const triggerQueue = ref<PaywallTrigger[]>([]);
const currentTrigger = ref<PaywallTrigger | null>(null);
const bannerVisible = ref(false);
const toastVisible = ref(false);

// 订阅用户不渲染任何引导
const shouldRender = computed(() => {
  return !subscriptionStore.isSubscriber;
});

const bannerText = computed(() => {
  if (!currentTrigger.value) return '';
  return currentTrigger.value.payload?.text ?? t('paywallManager.defaultUpgradeText');
});

const bannerActionText = computed(() => {
  if (!currentTrigger.value) return undefined;
  return currentTrigger.value.payload?.actionText ?? t('paywallManager.defaultActionText');
});

const toastMessage = computed(() => {
  if (!currentTrigger.value) return '';
  return currentTrigger.value.payload?.message ?? t('paywallManager.defaultMessage');
});

// 处理队列
function processQueue() {
  if (currentTrigger.value) return; // 当前有展示中的，等待
  if (triggerQueue.value.length === 0) return;

  const next = triggerQueue.value.shift();
  if (!next) return;

  currentTrigger.value = next;

  // 展示
  if (next.display_type === 'banner') {
    bannerVisible.value = true;
  } else if (next.display_type === 'toast') {
    toastVisible.value = true;
    // Toast 3.5s 自动消失
    setTimeout(() => {
      toastVisible.value = false;
      setTimeout(() => {
        currentTrigger.value = null;
        processQueue();
      }, 300);
    }, 3500);
  }
}

// 接收外部触发指令
function triggerPaywall(trigger: PaywallTrigger) {
  if (!shouldRender.value) return;
  triggerQueue.value.push(trigger);
  processQueue();
}

function handleClose() {
  bannerVisible.value = false;
  toastVisible.value = false;
  setTimeout(() => {
    currentTrigger.value = null;
    processQueue();
  }, 300);
}

function handleSubscribe() {
  handleClose();
  router.push('/subscription');
}

function handleBannerAction() {
  handleSubscribe();
}

// 监听订阅状态变化
watch(() => subscriptionStore.isSubscriber, (isSub) => {
  if (isSub) {
    // 变成订阅用户，关闭所有引导
    handleClose();
    triggerQueue.value = [];
  }
});

onMounted(() => {
  // 初始化时获取订阅状态
  if (!subscriptionStore.subscriptionStatus) {
    subscriptionStore.fetchSubscriptionStatus();
  }
});

onUnmounted(() => {
  triggerQueue.value = [];
  currentTrigger.value = null;
});

defineExpose({
  triggerPaywall
});
</script>

<style scoped>
.paywall-manager-root {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 9998;
}

.paywall-manager-root > * {
  pointer-events: auto;
}
</style>

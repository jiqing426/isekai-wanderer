import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  SubscriptionStatus,
  DialogueQuotaStatus,
  SubscriptionTier,
  TierPermissions
} from '@/types/subscription';
import { getSubscriptionStatus, getDialogueQuota } from '@/api/subscription';

export const useSubscriptionStore = defineStore('subscription', () => {
  const subscriptionStatus = ref<SubscriptionStatus | null>(null);
  const dialogueQuota = ref<DialogueQuotaStatus | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isSubscriber = computed(() => {
    return subscriptionStatus.value?.status === 'active' &&
           subscriptionStatus.value?.tier !== 'free';
  });

  const currentTier = computed<SubscriptionTier>(() => {
    return subscriptionStatus.value?.tier ?? 'free';
  });

  const permissions = computed<TierPermissions | null>(() => {
    return subscriptionStatus.value?.permissions ?? null;
  });

  async function fetchSubscriptionStatus() {
    loading.value = true;
    error.value = null;
    try {
      const response = await getSubscriptionStatus();
      subscriptionStatus.value = response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取订阅状态失败';
      console.error('Failed to fetch subscription status:', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchDialogueQuota() {
    loading.value = true;
    error.value = null;
    try {
      const response = await getDialogueQuota();
      dialogueQuota.value = response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取对话额度失败';
      console.error('Failed to fetch dialogue quota:', err);
    } finally {
      loading.value = false;
    }
  }

  function hasPermission(permissionName: keyof TierPermissions): boolean {
    if (!permissions.value) return false;
    const value = permissions.value[permissionName];
    if (typeof value === 'boolean') return value;
    if (typeof value === 'number') return value !== 0;
    if (typeof value === 'string') return value !== 'trial_only';
    return false;
  }

  function $reset() {
    subscriptionStatus.value = null;
    dialogueQuota.value = null;
    loading.value = false;
    error.value = null;
  }

  return {
    subscriptionStatus,
    dialogueQuota,
    loading,
    error,
    isSubscriber,
    currentTier,
    permissions,
    fetchSubscriptionStatus,
    fetchDialogueQuota,
    hasPermission,
    $reset
  };
});

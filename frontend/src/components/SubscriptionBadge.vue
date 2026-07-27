<template>
  <div class="subscription-badge" :class="tier">
    <div class="badge-content">
      <span class="badge-icon">{{ tierIcon }}</span>
      <span class="badge-text">{{ tierText }}</span>
    </div>
    <div v-if="showQuota" class="quota-info">
      <div class="quota-text">
        <span>{{ quota?.remaining }}</span>
        <span class="quota-separator">/</span>
        <span>{{ quota?.total }}</span>
      </div>
      <div class="quota-bar">
        <div class="quota-progress" :style="{ width: quotaPercentage + '%' }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  tier: 'free' | 'basic' | 'standard' | 'premium';
  quota?: {
    total: number;
    used: number;
    remaining: number;
  };
  showQuota?: boolean;
}>();

const tierIcon = computed(() => {
  const icons: Record<string, string> = {
    free: '🆓',
    basic: '⭐',
    standard: '💎',
    premium: '👑'
  };
  return icons[props.tier] || '🆓';
});

const tierText = computed(() => {
  const texts: Record<string, string> = {
    free: '免费版',
    basic: '基础版',
    standard: '标准版',
    premium: '高级版'
  };
  return texts[props.tier] || '免费版';
});

const quotaPercentage = computed(() => {
  if (!props.quota || props.quota.total === 0) return 0;
  return Math.round((props.quota.remaining / props.quota.total) * 100);
});
</script>

<style scoped>
.subscription-badge {
  display: inline-flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
}

.subscription-badge.free {
  border-color: var(--border-color);
}

.subscription-badge.basic {
  border-color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), transparent);
}

.subscription-badge.standard {
  border-color: #8b5cf6;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), transparent);
}

.subscription-badge.premium {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), transparent);
}

.badge-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge-icon {
  font-size: 20px;
}

.badge-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.quota-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quota-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.quota-text span:first-child {
  font-weight: 600;
  color: var(--text-primary);
}

.quota-separator {
  margin: 0 2px;
}

.quota-bar {
  width: 100%;
  height: 4px;
  background: var(--bg-hover);
  border-radius: 2px;
  overflow: hidden;
}

.quota-progress {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.subscription-badge.premium .quota-progress {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}
</style>

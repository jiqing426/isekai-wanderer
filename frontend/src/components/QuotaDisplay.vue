<template>
  <div class="quota-display">
    <div class="quota-header">
      <h3 class="quota-title">{{ $t('quotaDisplay.title') }}</h3>
      <button class="refresh-btn" @click="refreshQuota" :disabled="refreshing">
        <span class="refresh-icon" :class="{ spinning: refreshing }">🔄</span>
      </button>
    </div>

    <div class="quota-info">
      <div class="quota-numbers">
        <span class="quota-remaining">{{ quota.remaining }}</span>
        <span class="quota-separator">/</span>
        <span class="quota-total">{{ quota.total }}</span>
      </div>
      <div class="quota-label">{{ $t('quotaDisplay.remaining') }}</div>
    </div>

    <div class="quota-bar">
      <div
        class="quota-progress"
        :style="{ width: quotaPercentage + '%' }"
        :class="{ low: quotaPercentage < 20 }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  quota: {
    total: number;
    used: number;
    remaining: number;
  };
}>();

const emit = defineEmits<{
  (e: 'refresh'): void;
  (e: 'update', quota: { total: number; used: number; remaining: number }): void;
}>();

const refreshing = ref(false);

const quotaPercentage = computed(() => {
  if (props.quota.total === -1) return 100;
  if (props.quota.total === 0) return 0;
  return Math.round((props.quota.remaining / props.quota.total) * 100);
});

async function refreshQuota() {
  refreshing.value = true;
  try {
    emit('refresh');
  } finally {
    refreshing.value = false;
  }
}
</script>

<style scoped>
.quota-display {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
}

.quota-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.quota-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.refresh-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--bg-hover);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.refresh-icon {
  font-size: 18px;
  display: inline-block;
}

.refresh-icon.spinning {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.quota-info {
  text-align: center;
  margin-bottom: 16px;
}

.quota-numbers {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.quota-remaining {
  color: var(--color-primary);
}

.quota-separator {
  color: var(--text-secondary);
  margin: 0 4px;
}

.quota-total {
  color: var(--text-secondary);
}

.quota-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.quota-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-hover);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 20px;
}

.quota-progress {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.quota-progress.low {
  background: #ef4444;
}
</style>

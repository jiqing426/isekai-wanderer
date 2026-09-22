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

    <div class="quota-actions">
      <button
        class="btn-buy"
        @click="showBuyDialog = true"
        :disabled="quota.total === -1"
      >
        {{ $t('quotaDisplay.buyExtra') }}
      </button>
    </div>

    <!-- 购买额度弹窗 -->
    <div v-if="showBuyDialog" class="dialog-overlay" @click.self="showBuyDialog = false">
      <div class="dialog-content">
        <button class="dialog-close" @click="showBuyDialog = false">✕</button>
        <h3 class="dialog-title">{{ $t('quotaDisplay.buyDialogTitle') }}</h3>
        
        <div class="buy-options">
          <div
            v-for="option in buyOptions"
            :key="option.id"
            class="buy-option"
            :class="{ selected: selectedOption === option.id }"
            @click="selectedOption = option.id"
          >
            <div class="option-quota">{{ $t('quotaDisplay.quotaOption', { n: option.quota }) }}</div>
            <div class="option-price">{{ $t('quotaDisplay.costOption', { n: option.cost }) }}</div>
          </div>
        </div>

        <div class="dialog-actions">
          <button class="btn-cancel" @click="showBuyDialog = false">{{ $t('quotaDisplay.cancel') }}</button>
          <button
            class="btn-confirm"
            @click="handleBuyQuota"
            :disabled="!selectedOption || buying"
          >
            {{ buying ? $t('quotaDisplay.buying') : $t('quotaDisplay.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useMessage } from 'naive-ui';
import { exchangeQuota } from '@/api/subscription';
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

const message = useMessage();
const refreshing = ref(false);
const showBuyDialog = ref(false);
const selectedOption = ref<string | null>(null);
const buying = ref(false);

const buyOptions = [
  { id: 'dialogue_quota_10', quota: 10, cost: 50 },
  { id: 'dialogue_quota_30', quota: 30, cost: 120 },
  { id: 'dialogue_quota_50', quota: 50, cost: 180 }
];

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

async function handleBuyQuota() {
  if (!selectedOption.value) return;

  buying.value = true;
  try {
    const response = await exchangeQuota({
      goods_id: selectedOption.value,
      quantity: 1
    });

    message.success(t('quotaDisplay.buySuccess', { n: response.quota_added }));
    showBuyDialog.value = false;
    selectedOption.value = null;

    emit('update', {
      total: props.quota.total + response.quota_added,
      used: props.quota.used,
      remaining: response.new_quota
    });
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : t('quotaDisplay.buyFailed');
    message.error(errorMsg);
  } finally {
    buying.value = false;
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

.quota-actions {
  display: flex;
  gap: 12px;
}

.btn-buy {
  flex: 1;
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-buy:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-buy:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 弹窗样式 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dialog-content {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 32px;
  max-width: 480px;
  width: 90%;
  position: relative;
  animation: slideUp 0.3s ease;
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

.dialog-close {
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

.dialog-close:hover {
  background: var(--bg-hover);
}

.dialog-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 24px;
  color: var(--text-primary);
}

.buy-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.buy-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-hover);
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.buy-option:hover {
  background: var(--bg-card);
  border-color: var(--border-color);
}

.buy-option.selected {
  background: var(--bg-card);
  border-color: var(--color-primary);
}

.option-quota {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.option-price {
  font-size: 14px;
  color: var(--text-secondary);
}

.dialog-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--bg-hover);
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: var(--bg-card);
}

.btn-confirm {
  background: var(--color-primary);
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

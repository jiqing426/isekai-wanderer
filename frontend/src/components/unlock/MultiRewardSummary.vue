<template>
  <div class="multi-reward-summary">
    <h3 class="summary-title">{{ $t('multiRewardSummary.title') }}</h3>

    <div class="rewards-grid">
      <div
        v-for="(reward, index) in rewards"
        :key="index"
        class="reward-item"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <span class="reward-icon">{{ rewardIcon(reward.type) }}</span>
        <span class="reward-amount">+{{ formatAmount(reward.amount) }}</span>
        <span class="reward-label">{{ rewardLabel(reward.type) }}</span>
      </div>
    </div>

    <button class="confirm-btn" @click="$emit('confirm')">{{ $t('multiRewardSummary.confirm') }}</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { UnlockReward } from '@/types/unlock'

const { t } = useI18n()

defineProps<{
  rewards: UnlockReward[]
}>()

defineEmits<{
  (e: 'confirm'): void
}>()

function formatAmount(amount: number): string {
  return amount >= 1000 ? `${(amount / 1000).toFixed(1)}k` : String(amount)
}

function rewardIcon(type: string): string {
  const icons: Record<string, string> = {
    fragment: '💎',
    exp: '⭐',
    gold: '🪙'
  }
  return icons[type] || '🎁'
}

function rewardLabel(type: string): string {
  const keyMap: Record<string, string> = {
    fragment: 'rewardFloat.fragment',
    exp: 'rewardFloat.exp',
    gold: 'rewardFloat.gold'
  }
  const i18nKey = keyMap[type]
  return i18nKey ? t(i18nKey) : type
}
</script>

<style scoped>
.multi-reward-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.summary-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.rewards-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}

.reward-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 12px;
  opacity: 0;
  animation: rewardPop 400ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes rewardPop {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.reward-icon {
  font-size: 36px;
}

.reward-amount {
  font-size: 24px;
  font-weight: 700;
  color: #ffd700;
}

.reward-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.confirm-btn {
  padding: 12px 48px;
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
  opacity: 0;
  animation: fadeInUp 400ms ease 800ms forwards;
}

.confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .rewards-grid {
    gap: 12px;
  }

  .reward-item {
    padding: 12px 18px;
  }

  .reward-icon {
    font-size: 28px;
  }

  .reward-amount {
    font-size: 20px;
  }
}
</style>

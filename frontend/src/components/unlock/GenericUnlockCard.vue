<template>
  <div class="generic-unlock-card">
    <div class="card-inner">
      <!-- 图标 -->
      <div class="icon-container">
        <span class="icon">{{ typeIcon }}</span>
      </div>

      <!-- 解锁标签 -->
      <div class="unlock-label">{{ typeLabel }} 已解锁</div>

      <!-- 标题 -->
      <h3 class="unlock-title">{{ title }}</h3>

      <!-- 描述 -->
      <p v-if="description" class="unlock-description">{{ description }}</p>

      <!-- 奖励 -->
      <div v-if="reward" class="reward-section">
        <span class="reward-icon">{{ rewardIcon(reward.type) }}</span>
        <span class="reward-amount">+{{ reward.amount }}</span>
        <span class="reward-label">{{ rewardLabel(reward.type) }}</span>
      </div>

      <!-- 按钮组 -->
      <div class="button-group">
        <button class="btn-confirm" @click="$emit('confirm')">确认</button>
        <button v-if="showLater" class="btn-later" @click="$emit('later')">稍后</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UnlockType, UnlockReward } from '@/types/unlock'

const props = defineProps<{
  type: UnlockType
  title: string
  description?: string
  image?: string
  reward?: UnlockReward
}>()

defineEmits<{
  (e: 'confirm'): void
  (e: 'later'): void
}>()

const typeIcon = computed(() => {
  const icons: Record<string, string> = {
    cg: '🖼️',
    achievement: '🏆',
    hidden_story: '📖',
    voice: '🎙️',
    exclusive_script: '🎭',
    reward_float: '✨',
    multi_reward: '🎁'
  }
  return icons[props.type] || '✨'
})

const typeLabel = computed(() => {
  const labels: Record<string, string> = {
    cg: 'CG',
    achievement: '成就',
    hidden_story: '隐藏剧情',
    voice: '语音',
    exclusive_script: '专属剧本',
    reward_float: '奖励',
    multi_reward: '奖励'
  }
  return labels[props.type] || '内容'
})

const showLater = computed(() => {
  return props.type === 'hidden_story' || props.type === 'voice' || props.type === 'exclusive_script'
})

function rewardIcon(type: string): string {
  const icons: Record<string, string> = {
    fragment: '💎',
    exp: '⭐',
    gold: '🪙'
  }
  return icons[type] || '🎁'
}

function rewardLabel(type: string): string {
  const labels: Record<string, string> = {
    fragment: '碎片',
    exp: '经验',
    gold: '金币'
  }
  return labels[type] || type
}
</script>

<style scoped>
.generic-unlock-card {
  position: relative;
  width: 300px;
  max-width: 90vw;
}

.card-inner {
  position: relative;
  background: linear-gradient(135deg, rgba(20, 20, 40, 0.95), rgba(30, 30, 50, 0.95));
  border: 2px solid rgba(255, 215, 0, 0.3);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  overflow: hidden;
  animation: cardSlideIn 400ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transform: translateY(100px) scale(0.8);
  opacity: 0;
}

@keyframes cardSlideIn {
  0% {
    transform: translateY(100px) scale(0.8);
    opacity: 0;
  }
  100% {
    transform: translateY(0) scale(1);
    opacity: 1;
  }
}

.icon-container {
  margin-bottom: 16px;
  animation: iconBounce 500ms cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards;
  transform: scale(0);
  opacity: 0;
}

@keyframes iconBounce {
  0% {
    transform: scale(0) rotate(-30deg);
    opacity: 0;
  }
  100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

.icon {
  font-size: 56px;
}

.unlock-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
  opacity: 0;
  animation: fadeIn 600ms ease 0.6s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.unlock-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  opacity: 0;
  animation: fadeIn 600ms ease 0.7s forwards;
}

.unlock-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 16px 0;
  line-height: 1.5;
  opacity: 0;
  animation: fadeIn 600ms ease 0.8s forwards;
}

.reward-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  margin-bottom: 20px;
  opacity: 0;
  animation: fadeIn 600ms ease 0.9s forwards;
}

.reward-icon {
  font-size: 24px;
}

.reward-amount {
  font-size: 20px;
  font-weight: 700;
  color: #ffd700;
}

.reward-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.button-group {
  display: flex;
  gap: 12px;
  opacity: 0;
  animation: fadeIn 400ms ease 0.8s forwards;
}

.btn-confirm {
  flex: 1;
  padding: 12px 24px;
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

.btn-later {
  flex: 1;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
}

.btn-later:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .generic-unlock-card {
    width: 280px;
  }

  .icon {
    font-size: 48px;
  }

  .unlock-title {
    font-size: 18px;
  }
}
</style>

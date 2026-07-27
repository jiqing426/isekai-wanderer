<template>
  <div class="achievement-unlock-card">
    <div class="card-inner">
      <!-- 光效背景 -->
      <div class="glow-bg"></div>

      <!-- 成就徽章 -->
      <div class="badge-container">
        <div class="badge">
          <div class="badge-inner">
            <span class="badge-icon">🏆</span>
          </div>
          <div class="badge-ring"></div>
          <div class="badge-rays">
            <span v-for="i in 8" :key="i" class="ray" :style="rayStyle(i)"></span>
          </div>
        </div>
      </div>

      <!-- 成就信息 -->
      <div class="info-section">
        <div class="unlock-label">成就已解锁</div>
        <h3 class="achievement-title">{{ title }}</h3>
        <p v-if="description" class="achievement-description">{{ description }}</p>
      </div>

      <!-- 奖励展示 -->
      <div v-if="reward" class="reward-section">
        <div class="reward-item">
          <span class="reward-icon">{{ rewardIcon(reward.type) }}</span>
          <span class="reward-amount">+{{ reward.amount }}</span>
          <span class="reward-label">{{ rewardLabel(reward.type) }}</span>
        </div>
      </div>

      <!-- 确认按钮 -->
      <button class="btn-confirm" @click="$emit('confirm')">确认</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UnlockReward } from '@/types/unlock'

defineProps<{
  title: string
  description?: string
  reward?: UnlockReward
}>()

defineEmits<{
  (e: 'confirm'): void
}>()

function rayStyle(index: number) {
  const angle = (index / 8) * 360
  return { '--angle': `${angle}deg` }
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
  const labels: Record<string, string> = {
    fragment: '碎片',
    exp: '经验',
    gold: '金币'
  }
  return labels[type] || type
}
</script>

<style scoped>
.achievement-unlock-card {
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

/* 光效背景 */
.glow-bg {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%);
  background: radial-gradient(
    circle,
    rgba(255, 215, 0, 0.1) 0%,
    transparent 70%
  );
  animation: glowPulse 2s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glowPulse {
  0%, 100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

/* 徽章容器 */
.badge-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 20px;
}

.badge {
  position: relative;
  width: 100%;
  height: 100%;
  animation: badgeSpinIn 500ms cubic-bezier(0.34, 1.56, 0.64, 1) 0.2s forwards;
  transform: rotate(-180deg) scale(0);
  opacity: 0;
}

@keyframes badgeSpinIn {
  0% {
    transform: rotate(-180deg) scale(0);
    opacity: 0;
  }
  100% {
    transform: rotate(0deg) scale(1);
    opacity: 1;
  }
}

.badge-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(255, 215, 0, 0.4);
}

.badge-icon {
  font-size: 40px;
}

.badge-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border: 3px solid rgba(255, 215, 0, 0.5);
  border-radius: 50%;
  animation: ringPulse 1.5s ease-in-out infinite;
}

@keyframes ringPulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.1);
    opacity: 1;
  }
}

/* 光芒效果 */
.badge-rays {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.ray {
  position: absolute;
  width: 2px;
  height: 20px;
  background: linear-gradient(to top, transparent, #ffd700);
  transform-origin: bottom center;
  transform: rotate(var(--angle)) translateY(-60px);
  animation: rayGlow 1.5s ease-in-out infinite;
  animation-delay: calc(var(--angle) / 360 * 1.5s);
}

@keyframes rayGlow {
  0%, 100% {
    opacity: 0.3;
    height: 20px;
  }
  50% {
    opacity: 1;
    height: 30px;
  }
}

/* 信息区域 */
.info-section {
  margin-bottom: 20px;
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

.achievement-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
  opacity: 0;
  animation: fadeIn 600ms ease 0.7s forwards;
}

.achievement-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.5;
  opacity: 0;
  animation: fadeIn 600ms ease 0.8s forwards;
}

/* 奖励展示 */
.reward-section {
  margin-bottom: 20px;
  opacity: 0;
  animation: fadeIn 600ms ease 0.9s forwards;
}

.reward-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
}

.reward-icon {
  font-size: 24px;
}

.reward-amount {
  font-size: 20px;
  font-weight: 700;
  color: #ffd700;
  animation: numberJump 500ms ease 1s;
}

@keyframes numberJump {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.3);
  }
}

.reward-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* 确认按钮 */
.btn-confirm {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, #ffd700, #ffaa00);
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease;
  opacity: 0;
  animation: fadeIn 400ms ease 0.8s forwards;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.4);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .achievement-unlock-card {
    width: 280px;
  }

  .badge-container {
    width: 100px;
    height: 100px;
  }

  .badge-inner {
    width: 64px;
    height: 64px;
  }

  .badge-icon {
    font-size: 32px;
  }

  .badge-ring {
    width: 84px;
    height: 84px;
  }

  .achievement-title {
    font-size: 18px;
  }
}
</style>

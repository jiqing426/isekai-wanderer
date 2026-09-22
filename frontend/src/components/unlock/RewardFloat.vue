<template>
  <div class="reward-float-container">
    <TransitionGroup name="float" tag="div" class="float-wrapper">
      <div
        v-for="item in visibleItems"
        :key="item.id"
        class="float-item"
        :class="`type-${item.type}`"
      >
        <span class="float-icon">{{ iconMap[item.type] }}</span>
        <span class="float-amount">+{{ item.amount }}</span>
        <span class="float-label">{{ labelMap[item.type] }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { UnlockReward } from '@/types/unlock'

interface FloatItem extends UnlockReward {
  id: number
}

const { t } = useI18n()

const props = defineProps<{
  rewards: UnlockReward[]
  duration?: number
}>()

const visibleItems = ref<FloatItem[]>([])
let nextId = 0
let timers: number[] = []

const iconMap: Record<string, string> = {
  fragment: '💎',
  exp: '⭐',
  gold: '🪙'
}

const labelMap = computed<Record<string, string>>(() => ({
  fragment: t('rewardFloat.fragment'),
  exp: t('rewardFloat.exp'),
  gold: t('rewardFloat.gold')
}))

onMounted(() => {
  props.rewards.forEach((reward, index) => {
    const delay = index * 300
    const timer = window.setTimeout(() => {
      const item: FloatItem = { ...reward, id: nextId++ }
      visibleItems.value.push(item)

      // 自动移除
      const removeTimer = window.setTimeout(() => {
        const idx = visibleItems.value.findIndex(i => i.id === item.id)
        if (idx !== -1) visibleItems.value.splice(idx, 1)
      }, props.duration || 2000)
      timers.push(removeTimer)
    }, delay)
    timers.push(timer)
  })
})

onUnmounted(() => {
  timers.forEach(t => clearTimeout(t))
})
</script>

<style scoped>
.reward-float-container {
  position: relative;
  width: 100%;
  height: 120px;
  pointer-events: none;
}

.float-wrapper {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: 8px;
}

.float-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 20px;
  white-space: nowrap;
}

.float-icon {
  font-size: 18px;
}

.float-amount {
  font-size: 16px;
  font-weight: 700;
  color: #ffd700;
}

.float-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* Transition */
.float-enter-active {
  animation: floatUp 600ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

.float-leave-active {
  animation: floatFade 400ms ease forwards;
}

@keyframes floatUp {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.5);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes floatFade {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-30px) scale(0.8);
  }
}
</style>

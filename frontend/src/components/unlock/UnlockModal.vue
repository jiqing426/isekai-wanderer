<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isVisible" class="unlock-modal-overlay" @click.self="handleOverlayClick">
        <div class="unlock-modal-content">
          <!-- 跳过按钮 -->
          <button v-if="canSkip" class="skip-btn" @click="handleSkip">
            {{ $t('unlockModal.skip') }}
          </button>

          <!-- 根据类型渲染不同卡片 -->
          <CGUnlockCard
            v-if="currentUnlock?.type === 'cg'"
            :title="currentUnlock.title"
            :description="currentUnlock.description"
            :image="currentUnlock.image"
            :rarity="currentUnlock.rarity || 'R'"
            @view="handleConfirm"
            @later="handleSkip"
          />

          <AchievementUnlockCard
            v-else-if="currentUnlock?.type === 'achievement'"
            :title="currentUnlock.title"
            :description="currentUnlock.description"
            :reward="currentUnlock.reward"
            @confirm="handleConfirm"
          />

          <MultiRewardSummary
            v-else-if="currentUnlock?.type === 'multi_reward' && currentUnlock.rewards"
            :rewards="currentUnlock.rewards"
            @confirm="handleConfirm"
          />

          <!-- 其他类型的通用卡片 -->
          <GenericUnlockCard
            v-else-if="currentUnlock"
            :type="currentUnlock.type"
            :title="currentUnlock.title"
            :description="currentUnlock.description"
            :image="currentUnlock.image"
            :reward="currentUnlock.reward"
            @confirm="handleConfirm"
            @later="handleSkip"
          />
        </div>
      </div>
    </Transition>

    <!-- 飘字奖励（独立于弹窗） -->
    <div v-if="showFloat && currentUnlock?.reward" class="float-reward-layer">
      <RewardFloat :rewards="[currentUnlock.reward]" />
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useUnlockModal } from '@/composables/useUnlockModal'
import CGUnlockCard from './CGUnlockCard.vue'
import AchievementUnlockCard from './AchievementUnlockCard.vue'
import MultiRewardSummary from './MultiRewardSummary.vue'
import RewardFloat from './RewardFloat.vue'
import GenericUnlockCard from './GenericUnlockCard.vue'

const router = useRouter()
const { t } = useI18n()

defineProps<{
  autoProcess?: boolean
}>()

const { currentUnlock, isVisible, confirm, skip } = useUnlockModal()

const showFloat = ref(false)
const canSkip = computed(() => {
  const type = currentUnlock.value?.type
  return type === 'cg' || type === 'hidden_story' || type === 'voice' || type === 'exclusive_script'
})

watch(isVisible, (val) => {
  if (val && currentUnlock.value?.type === 'reward_float') {
    showFloat.value = true
    setTimeout(() => {
      showFloat.value = false
      confirm()
    }, 2500)
  } else {
    showFloat.value = false
  }
})

function handleConfirm() {
  // 如果是CG类型，跳转到收藏馆
  if (currentUnlock.value?.type === 'cg') {
    router.push('/gallery')
  }
  confirm()
}

function handleSkip() {
  skip()
}

function handleOverlayClick() {
  if (canSkip.value) {
    skip()
  }
}

// ESC 关闭
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isVisible.value && canSkip.value) {
      skip()
    }
  })
}

defineExpose({
  currentUnlock,
  isVisible
})
</script>

<style scoped>
.unlock-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: overlayDarken 200ms ease forwards;
}

@keyframes overlayDarken {
  to {
    background: rgba(0, 0, 0, 0.85);
  }
}

.unlock-modal-content {
  position: relative;
}

.skip-btn {
  position: absolute;
  top: -40px;
  right: 0;
  padding: 6px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 200ms ease;
  z-index: 10;
}

.skip-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.float-reward-layer {
  position: fixed;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9998;
  pointer-events: none;
}

/* Modal transitions */
.modal-enter-active {
  transition: opacity 200ms ease;
}

.modal-leave-active {
  transition: opacity 300ms ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .unlock-modal-content {
  transform: scale(0.9);
}

.modal-leave-to .unlock-modal-content {
  transform: scale(0.8);
  opacity: 0;
}

@media (max-width: 768px) {
  .skip-btn {
    top: -36px;
    right: 10px;
  }
}
</style>

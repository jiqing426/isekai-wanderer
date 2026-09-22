<template>
  <div class="choice-panel">
    <div class="choice-label">{{ $t('choicePanel.makeChoice') }}</div>
    <div v-if="loading" class="choice-loading">
      <div class="loading-spinner"></div>
      <span>{{ $t('choicePanel.thinking') }}</span>
    </div>
    <div class="choice-list">
      <div
        v-for="(choice, i) in choices"
        :key="choice.id"
        class="choice-card glass-card fade-in-up"
        :style="{ animationDelay: `${i * 0.08}s` }"
        :class="{
          selected: selectedId === choice.id,
          disabled: submitting || choice.locked || loading,
          locked: choice.locked,
          premium: choice.is_premium,
        }"
        @click="handleSelect(choice)"
      >
        <div class="choice-indicator">
          <span class="choice-letter" v-if="!choice.locked">{{ String.fromCharCode(65 + i) }}</span>
          <span class="choice-lock" v-else>🔒</span>
        </div>
        <div class="choice-content">
          <span class="choice-text">{{ choice.text }}</span>
          <span class="affection-delta" v-if="choice.affection_delta && !choice.locked" :class="choice.affection_delta > 0 ? 'positive' : 'negative'">
            {{ choice.affection_delta > 0 ? '+' : '' }}{{ choice.affection_delta }} {{ $t('choicePanel.affectionPoints') }}
          </span>
          <!-- AC-GAME-005: Consequence warning tag -->
          <span class="consequence-tag" v-if="choice.has_consequence && !choice.locked">
            {{ $t('choicePanel.affectsStory') }}
          </span>
          <!-- AC-GAME-006: Locked state with required affection -->
          <span class="locked-tag" v-if="choice.locked">
            {{ $t('choicePanel.requiresAffection', { n: choice.required_affection }) }}
          </span>
          <!-- AC-GAME-007: Consequence preview hint on hover -->
          <n-tooltip v-if="choice.hint && !choice.locked" trigger="hover" placement="top">
            <template #trigger>
              <span class="hint-icon">💡</span>
            </template>
            {{ choice.hint }}
          </n-tooltip>
        </div>
        <div class="choice-arrow" v-if="!choice.locked">→</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NTooltip } from 'naive-ui';
import { ref, watch } from 'vue';

interface Choice {
  id: string;
  text: string;
  affection_delta?: number;
  has_consequence?: boolean;
  locked?: boolean;
  required_affection?: number;
  is_premium?: boolean;
  hint?: string;
}

const props = defineProps<{ 
  choices: Choice[];
  loading?: boolean;
}>();
const emit = defineEmits<{ select: [id: string] }>();

const selectedId = ref<string | null>(null);
const submitting = ref(false);

function reset() {
  selectedId.value = null;
  submitting.value = false;
}

defineExpose({ reset });

async function handleSelect(choice: Choice) {
  if (submitting.value || choice.locked || props.loading) return;
  selectedId.value = choice.id;
  submitting.value = true;
  
  try {
    emit('select', choice.id);
  } finally {
    // 500ms 后释放锁，允许下次选择
    setTimeout(() => { submitting.value = false; }, 500);
  }
}

// 新选项到达时重置状态，避免上次选择锁死面板
watch(() => props.choices, () => {
  selectedId.value = null;
  submitting.value = false;
})
</script>

<style scoped>
.choice-panel {
  margin-top: 16px;
}

.choice-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-secondary);
  margin-bottom: 12px;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.choice-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 14px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(192, 132, 252, 0.2);
  border-top-color: var(--brand-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.choice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.choice-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.choice-card:hover {
  border-color: var(--brand-primary) !important;
  background: rgba(192, 132, 252, 0.08) !important;
  transform: translateX(4px);
}

.choice-card.selected {
  border-color: var(--brand-primary) !important;
  background: rgba(192, 132, 252, 0.12) !important;
  box-shadow: 0 0 20px rgba(192, 132, 252, 0.12);
}

.choice-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.choice-indicator {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(192, 132, 252, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.25s;
}

.choice-card:hover .choice-indicator,
.choice-card.selected .choice-indicator {
  background: rgba(192, 132, 252, 0.2);
  border-color: var(--brand-primary);
}

.choice-letter {
  font-size: 13px;
  font-weight: 700;
  color: var(--brand-primary);
}

.choice-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.choice-text {
  font-size: 14px;
  color: var(--text-main);
  line-height: 1.4;
}

.affection-delta {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
}

.affection-delta.positive {
  background: rgba(134, 239, 172, 0.1);
  color: #86efac;
}

.affection-delta.negative {
  background: rgba(252, 165, 165, 0.1);
  color: #fca5a5;
}

.consequence-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.choice-arrow {
  color: var(--brand-primary);
  font-size: 16px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.choice-card:hover .choice-arrow {
  opacity: 1;
}

/* AC-GAME-006: Locked choice styles */
.choice-card.locked {
  opacity: 0.5;
  cursor: not-allowed;
  border-color: rgba(100, 100, 100, 0.2) !important;
}
.choice-card.locked:hover {
  transform: none;
  border-color: rgba(100, 100, 100, 0.2) !important;
  background: rgba(192, 132, 252, 0.0) !important;
}
.choice-card.locked .choice-indicator {
  background: rgba(100, 100, 100, 0.1);
  border-color: rgba(100, 100, 100, 0.15);
}
.choice-lock {
  font-size: 14px;
}
.locked-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  white-space: nowrap;
  flex-shrink: 0;
  background: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
  border: 1px solid rgba(156, 163, 175, 0.3);
}

/* AC-GAME-006: Premium/golden choice */
.choice-card.premium {
  border-color: rgba(251, 191, 36, 0.3) !important;
  background: rgba(251, 191, 36, 0.04) !important;
}
.choice-card.premium:hover {
  border-color: rgba(251, 191, 36, 0.5) !important;
  background: rgba(251, 191, 36, 0.08) !important;
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.12);
}
.choice-card.premium .choice-indicator {
  background: rgba(251, 191, 36, 0.15);
  border-color: rgba(251, 191, 36, 0.4);
}
.choice-card.premium .choice-letter {
  color: #fbbf24;
}

/* AC-GAME-007: Hint icon */
.hint-icon {
  font-size: 14px;
  cursor: help;
  flex-shrink: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.hint-icon:hover {
  opacity: 1;
}

/* {{ $t('choicePanel.affectionPoints') }}度变化动画 */
.affection-animation {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  font-weight: 800;
  padding: 20px 40px;
  border-radius: 16px;
  z-index: 9999;
  pointer-events: none;
  animation: affectionPop 1.5s ease-out;
}

.affection-animation.positive {
  background: rgba(134, 239, 172, 0.9);
  color: #065f46;
  box-shadow: 0 8px 32px rgba(134, 239, 172, 0.5);
}

.affection-animation.negative {
  background: rgba(252, 165, 165, 0.9);
  color: #991b1b;
  box-shadow: 0 8px 32px rgba(252, 165, 165, 0.5);
}

@keyframes affectionPop {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  20% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.2);
  }
  40% {
    transform: translate(-50%, -50%) scale(1);
  }
  80% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

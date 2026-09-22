<template>
  <div class="chapter-progress">
    <div class="chapter-info">
      <transition name="chapter-fade" mode="out-in">
        <span class="chapter-title" :key="chapterDisplay">
          {{ chapterDisplay }}
        </span>
      </transition>
      <span v-if="convergencePoint" class="convergence-point">
        <span class="cp-dot"></span>
        {{ convergencePoint }}
      </span>
    </div>
    <div class="progress-row">
      <n-progress
        :percentage="clampedProgress"
        :show-indicator="false"
        :height="6"
        :color="progressColor"
        rail-color="rgba(167,139,250,0.08)"
        border-radius="3px"
      />
      <span class="progress-text">{{ clampedProgress }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = withDefaults(defineProps<{
  chapter?: string;
  chapterNumber?: number | null;
  chapterTitle?: string | null;
  convergencePoint?: string;
  progress?: number;
}>(), {
  chapter: t('chapterProgress.prologue'),
  chapterNumber: null,
  chapterTitle: null,
  progress: 0,
});

// CR-030: 优先使用 chapterNumber + chapterTitle 显示 "第X章：章节名"
const chapterDisplay = computed(() => {
  if (props.chapterNumber != null && props.chapterTitle) {
    return t('chapterProgress.chapterFormat', { n: props.chapterNumber, title: props.chapterTitle });
  }
  // 向后兼容：旧 session 返回 chapter_number=null，使用 chapter prop 或默认值
  return props.chapter || t('chapterProgress.prologue');
});

const clampedProgress = computed(() => {
  return Math.max(0, Math.min(100, Math.round(props.progress || 0)));
});

const progressColor = computed(() => {
  const p = clampedProgress.value;
  if (p >= 80) return '#10B981';
  if (p >= 50) return '#A78BFA';
  if (p >= 20) return '#FBBF24';
  return '#9CA3AF';
});
</script>

<style scoped>
.chapter-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.chapter-label {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chapter-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.convergence-point {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--brand-accent, #fbbf24);
}

.cp-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--brand-accent, #fbbf24);
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-row .n-progress {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  min-width: 32px;
  text-align: right;
}

/* CR-030: 章节切换过渡动画 */
.chapter-fade-enter-active,
.chapter-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.chapter-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.chapter-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>

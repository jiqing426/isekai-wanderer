<template>
  <div class="chapter-progress">
    <div class="chapter-info">
      <span class="chapter-label">章节</span>
      <span class="chapter-title">{{ chapter || '序章' }}</span>
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

const props = withDefaults(defineProps<{
  chapter?: string;
  convergencePoint?: string;
  progress?: number;
}>(), {
  chapter: '序章',
  progress: 0,
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
</style>

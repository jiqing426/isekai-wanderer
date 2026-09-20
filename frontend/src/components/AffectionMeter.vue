<template>
  <div class="affection-meter" :class="{ compact: compact }">
    <div class="meter-header">
      <span class="meter-label">{{ label }}</span>
      <span class="meter-value" :style="{ color: levelColor }">{{ value }}/100</span>
    </div>
    <div class="meter-track">
      <div
        class="meter-fill"
        :style="{ width: `${clampedValue}%`, background: levelColor }"
      ></div>
      <!-- Level markers -->
      <div v-for="marker in levelMarkers" :key="marker.threshold" class="meter-marker" :style="{ left: `${marker.threshold}%` }">
        <n-tooltip trigger="hover">
          <template #trigger>
            <div class="marker-dot"></div>
          </template>
          {{ marker.label }} ({{ marker.threshold }})
        </n-tooltip>
      </div>
    </div>
    <div class="meter-footer" v-if="!compact">
      <span class="meter-level" :style="{ color: levelColor }">{{ levelLabel }}</span>
      <span v-if="nextLevel" class="meter-next">
        距离 <strong :style="{ color: nextLevelColor }">{{ nextLevelLabel }}</strong>
        还需 <strong>{{ nextLevelRemaining }}</strong> 点
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NTooltip } from 'naive-ui';
import { computed } from 'vue';

/**
 * CR3-011: AffectionMeter component
 * Displays affection value with visual progress bar and level markers.
 */

const props = withDefaults(defineProps<{
  value: number;
  label?: string;
  compact?: boolean;
}>(), {
  label: '好感度',
  compact: false,
});

const LEVELS = [
  { min: 0, max: 19, label: '相识', color: '#9CA3AF' },
  { min: 20, max: 39, label: '暧昧', color: '#F472B6' },
  { min: 40, max: 59, label: '信赖', color: '#38BDF8' },
  { min: 60, max: 79, label: '羁绊', color: '#A78BFA' },
  { min: 80, max: 100, label: '挚友', color: '#F43F5E' },
];

const clampedValue = computed(() => Math.max(0, Math.min(100, props.value)));

const currentLevel = computed(() =>
  LEVELS.find(l => clampedValue.value >= l.min && clampedValue.value <= l.max) || LEVELS[0]
);

const levelColor = computed(() => currentLevel.value.color);
const levelLabel = computed(() => currentLevel.value.label);

const nextLevel = computed(() => {
  const idx = LEVELS.indexOf(currentLevel.value);
  return idx < LEVELS.length - 1 ? LEVELS[idx + 1] : null;
});

const nextLevelLabel = computed(() => nextLevel.value?.label || '');
const nextLevelColor = computed(() => nextLevel.value?.color || '');
const nextLevelRemaining = computed(() => {
  if (!nextLevel.value) return 0;
  return Math.max(0, nextLevel.value.min - clampedValue.value);
});

const levelMarkers = LEVELS.filter(l => l.min > 0).map(l => ({
  threshold: l.min,
  label: l.label,
}));
</script>

<style scoped>
.affection-meter {
  width: 100%;
}
.meter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.meter-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}
.meter-value {
  font-size: 13px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.meter-track {
  position: relative;
  height: 8px;
  border-radius: 4px;
  background: rgba(167, 139, 250, 0.08);
  overflow: visible;
}
.meter-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease, background 0.3s ease;
}
.meter-marker {
  position: absolute;
  top: -2px;
  width: 12px;
  height: 12px;
  transform: translateX(-50%);
  z-index: 1;
}
.marker-dot {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(167, 139, 250, 0.3);
  border: 2px solid var(--bg-card, #1a1a2e);
  cursor: pointer;
}
.meter-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.meter-level {
  font-size: 12px;
  font-weight: 600;
}
.meter-next {
  font-size: 11px;
  color: var(--text-muted);
}
.compact .meter-header { margin-bottom: 4px; }
.compact .meter-track { height: 6px; }
.compact .meter-footer { display: none; }
</style>

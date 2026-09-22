<template>
  <div class="affection-display">
    <div class="affection-header">
      <span class="affection-label">
        <span class="heart-icon">♥</span>
        {{ $t('affectionDisplay.affectionLabel') }}
      </span>
      <span class="affection-value">{{ clampedValue }} / 100</span>
    </div>
    <n-progress
      :percentage="clampedValue"
      :show-indicator="false"
      :height="8"
      :color="levelColor"
      rail-color="rgba(167,139,250,0.08)"
      border-radius="4px"
    />
    <div class="level-row">
      <span class="level-badge" :style="{ background: levelBgColor, color: levelColor }">
        {{ currentLevelLabel }}
      </span>
      <div class="level-track">
        <span
          v-for="(lv, i) in levels"
          :key="i"
          class="level-marker"
          :class="{ active: clampedValue >= lv.threshold, current: lv.key === currentLevelLabel }"
        >
          {{ lv.threshold }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface LevelDef {
  key: string;
  threshold: number;
  color: string;
}

const levels: LevelDef[] = [
  { key: t('affectionDisplay.tierAcquainted'), threshold: 0, color: '#9CA3AF' },
  { key: t('affectionDisplay.tierAmbiguous'), threshold: 20, color: '#F472B6' },
  { key: t('affectionDisplay.tierTrusted'), threshold: 40, color: '#38BDF8' },
  { key: t('affectionDisplay.tierBonded'), threshold: 60, color: '#A78BFA' },
  { key: t('affectionDisplay.tierBestFriend'), threshold: 80, color: '#F43F5E' },
  { key: t('affectionDisplay.tierTrueLove'), threshold: 100, color: '#EC4899' },
];

const props = withDefaults(defineProps<{
  characterId?: string;
  value: number;
  level?: string;
}>(), {
  value: 0,
});

const clampedValue = computed(() => Math.max(0, Math.min(100, Math.round(props.value))));

const currentLevel = computed(() => {
  if (props.level) {
    return levels.find(l => l.key === props.level) || levels[0];
  }
  const v = clampedValue.value;
  for (let i = levels.length - 1; i >= 0; i--) {
    if (v >= levels[i].threshold) return levels[i];
  }
  return levels[0];
});

const currentLevelLabel = computed(() => currentLevel.value.key);
const levelColor = computed(() => currentLevel.value.color);
const levelBgColor = computed(() => currentLevel.value.color + '18');
</script>

<style scoped>
.affection-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.affection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.affection-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-main);
}

.heart-icon {
  color: #F43F5E;
  font-size: 12px;
}

.affection-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

.level-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.level-track {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.level-marker {
  font-size: 10px;
  color: var(--text-subtle);
  font-variant-numeric: tabular-nums;
  opacity: 0.5;
  transition: all 0.2s ease;
}

.level-marker.active {
  opacity: 1;
  color: var(--text-muted);
}

.level-marker.current {
  font-weight: 700;
  color: var(--text-main);
}
</style>

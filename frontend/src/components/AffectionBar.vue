<template>
  <div class="affection-bar glass-card" @click="expanded = !expanded">
    <div class="bar-main">
      <span class="bar-avatar">{{ avatarEmoji }}</span>
      <div class="bar-info">
        <div class="bar-name">
          {{ displayName }} <span class="bar-value">{{ clampedValue }}/100</span>
          <!-- 变化箭头动画 -->
          <transition name="arrow-up">
            <span v-if="showUpArrow" class="delta-arrow up">▲ +{{ lastDelta }}</span>
          </transition>
          <transition name="arrow-down">
            <span v-if="showDownArrow" class="delta-arrow down">▼ {{ lastDelta }}</span>
          </transition>
        </div>
        <n-progress
          type="line"
          :percentage="animatedValue"
          :color="levelColor"
          rail-color="rgba(167,139,250,0.08)"
          :height="6"
          :show-indicator="false"
        />
      </div>
      <span class="bar-level-tag" :style="{ color: levelColor, background: levelColor + '18' }">
        {{ levelLabel }}
      </span>
    </div>
    <transition name="expand">
      <div class="bar-detail" v-if="expanded">
        <div class="detail-row">
          <span class="detail-label">{{ $t('affectionBar.affectionLabel') }}</span>
          <span class="detail-value">{{ clampedValue }} / 100</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">{{ $t('affectionBar.levelLabel') }}</span>
          <span class="detail-value" :style="{ color: levelColor }">{{ levelLabel }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { NProgress } from 'naive-ui';
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps<{
  characterId: string;
  characterName?: string;
  value: number;
}>();

const displayName = computed(() => props.characterName || t('affection.unknownCharacter'));

const expanded = ref(false);
const clampedValue = computed(() => Math.max(0, Math.min(100, props.value)));

// 动画过渡值
const animatedValue = ref(clampedValue.value);
const showUpArrow = ref(false);
const showDownArrow = ref(false);
const lastDelta = ref(0);
let _arrowTimer: ReturnType<typeof setTimeout> | null = null;
let _animFrame: number | null = null;

watch(
  () => props.value,
  (newVal, oldVal) => {
    const delta = newVal - (oldVal ?? newVal);
    if (delta === 0) return;
    lastDelta.value = Math.abs(delta);
    // 清掉上次的定时器和动画
    if (_arrowTimer) clearTimeout(_arrowTimer);
    if (_animFrame) cancelAnimationFrame(_animFrame);
    // 显示箭头
    if (delta > 0) { showUpArrow.value = true; showDownArrow.value = false; }
    else { showDownArrow.value = true; showUpArrow.value = false; }
    // 平滑动画过渡进度条
    const startVal = animatedValue.value;
    const endVal = Math.max(0, Math.min(100, newVal));
    const startTime = performance.now();
    const duration = 600; // ms
    const animate = (now: number) => {
      const t = Math.min(1, (now - startTime) / duration);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      animatedValue.value = startVal + (endVal - startVal) * eased;
      if (t < 1) _animFrame = requestAnimationFrame(animate);
    };
    _animFrame = requestAnimationFrame(animate);
    // 2秒后隐藏箭头
    _arrowTimer = setTimeout(() => { showUpArrow.value = false; showDownArrow.value = false; }, 2000);
  },
  { immediate: false },
);

const levels = [
  { min: 0, max: 19, label: t('affectionBar.tierAcquainted'), color: '#9CA3AF' },
  { min: 20, max: 39, label: t('affectionBar.tierAmbiguous'), color: '#F472B6' },
  { min: 40, max: 59, label: t('affectionBar.tierTrusted'), color: '#38BDF8' },
  { min: 60, max: 79, label: t('affectionBar.tierBonded'), color: '#A78BFA' },
  { min: 80, max: 100, label: t('affectionBar.tierBestFriend'), color: '#F43F5E' },
];

const currentLevel = computed(() => levels.find(l => clampedValue.value >= l.min && clampedValue.value <= l.max) || levels[0]);
const levelLabel = computed(() => currentLevel.value.label);
const levelColor = computed(() => currentLevel.value.color);

const avatarEmoji = computed(() => {
  const map: Record<string, string> = { [t('affectionBar.emojiInitial')]: '🤝', [t('affectionBar.emojiAmbiguous')]: '💫', [t('affectionBar.emojiTrust')]: '🤝', [t('affectionBar.emojiBonded')]: '💜', [t('affectionBar.emojiLove')]: '💕' };
  return map[levelLabel.value] || '💫';
});
</script>

<style scoped>
.affection-bar {
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.25s;
}

.affection-bar:hover {
  background: rgba(139, 92, 246, 0.1) !important;
}

.bar-main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-avatar {
  font-size: 20px;
  flex-shrink: 0;
}

.bar-info {
  flex: 1;
  min-width: 0;
}

.bar-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 4px;
}

.bar-value {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  margin-left: 4px;
  font-variant-numeric: tabular-nums;
}

.bar-level-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.bar-detail {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(167, 139, 250, 0.1);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 12px;
  color: var(--text-muted);
}

.detail-value {
  font-size: 12px;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
}

.expand-enter-active, .expand-leave-active {
  transition: all 0.25s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
}
.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 80px;
}

/* 箭头动画 */
.delta-arrow {
  font-size: 11px;
  font-weight: 700;
  margin-left: 6px;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.delta-arrow.up { color: #10b981; }
.delta-arrow.down { color: #f87171; }

.arrow-up-enter-active, .arrow-up-leave-active,
.arrow-down-enter-active, .arrow-down-leave-active {
  transition: all 0.4s ease;
}
.arrow-up-enter-from { opacity: 0; transform: translateY(8px); }
.arrow-up-leave-to { opacity: 0; transform: translateY(-12px); }
.arrow-down-enter-from { opacity: 0; transform: translateY(-8px); }
.arrow-down-leave-to { opacity: 0; transform: translateY(12px); }
</style>

<template>
  <div class="ending-progress">
    <div class="progress-header">
      <span class="progress-title">🏆 结局收集</span>
      <span class="progress-count">{{ progress.unlocked_count }}/{{ progress.total_endings }}</span>
    </div>

    <!-- Progress bar -->
    <div class="progress-track">
      <div
        class="progress-fill"
        :style="{ width: `${progressPercent}%` }"
      ></div>
    </div>

    <!-- All collected celebration (AC-SAVE-004.3) -->
    <div v-if="allCollected" class="all-collected">
      🎉 全部结局已收集！
      <span class="badge">🏅 完美通关</span>
    </div>

    <!-- Unlocked endings list -->
    <div class="endings-grid" v-if="progress.unlocked_endings.length > 0">
      <div
        v-for="ending in progress.unlocked_endings"
        :key="ending.ending_id"
        class="ending-card unlocked"
      >
        <span class="ending-icon">{{ endingIcon(ending.ending_type) }}</span>
        <span class="ending-name">{{ ending.ending_name }}</span>
        <span class="ending-type">{{ endingTypeLabel(ending.ending_type) }}</span>
      </div>
    </div>

    <!-- Locked endings (AC-SAVE-004.4) -->
    <div class="endings-grid" v-if="progress.locked_endings.length > 0">
      <div
        v-for="locked in progress.locked_endings"
        :key="locked.ending_id"
        class="ending-card locked"
      >
        <span class="ending-icon">🔒</span>
        <span class="ending-name">???</span>
        <span class="ending-hint">{{ locked.hint }}</span>
      </div>
    </div>

    <!-- No endings defined (AC-SAVE-004.5) -->
    <n-empty v-if="progress.total_endings === 0" description="该剧本暂无结局收集" size="small" />
  </div>
</template>

<script setup lang="ts">
import { NEmpty } from 'naive-ui';
import { computed } from 'vue';
import type { EndingProgressResponse } from '@/api/game';

const props = defineProps<{
  progress: EndingProgressResponse;
}>();

const progressPercent = computed(() => {
  if (props.progress.total_endings === 0) return 0;
  return Math.round((props.progress.unlocked_count / props.progress.total_endings) * 100);
});

const allCollected = computed(() =>
  props.progress.total_endings > 0 && props.progress.unlocked_count >= props.progress.total_endings
);

function endingIcon(type: string): string {
  const map: Record<string, string> = {
    happy: '😊', bad: '😢', normal: '😌', true_end: '⭐', hidden: '🔮', secret: '✨',
  };
  return map[type] || '📖';
}

function endingTypeLabel(type: string): string {
  const map: Record<string, string> = {
    happy: 'HE', bad: 'BE', normal: 'NE', true_end: 'TE', hidden: '隐藏', secret: '秘密',
  };
  return map[type] || type;
}
</script>

<style scoped>
.ending-progress { width: 100%; }
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.progress-title { font-size: 14px; font-weight: 600; color: var(--text-main); }
.progress-count { font-size: 14px; font-weight: 700; color: var(--brand-primary); font-variant-numeric: tabular-nums; }
.progress-track {
  height: 8px;
  border-radius: 4px;
  background: rgba(167, 139, 250, 0.08);
  overflow: hidden;
  margin-bottom: 12px;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #A78BFA, #F472B6);
  transition: width 0.5s ease;
}
.all-collected {
  text-align: center;
  padding: 12px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(244, 114, 182, 0.1));
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 12px;
}
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
  font-size: 12px;
  margin-left: 8px;
}
.endings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
  margin-bottom: 8px;
}
.ending-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
}
.ending-card.unlocked {
  background: rgba(167, 139, 250, 0.08);
  color: var(--text-main);
}
.ending-card.locked {
  background: rgba(0, 0, 0, 0.04);
  color: var(--text-subtle);
}
.ending-icon { font-size: 16px; }
.ending-name { font-weight: 600; flex: 1; }
.ending-type { font-size: 10px; color: var(--text-muted); }
.ending-hint { font-size: 10px; color: var(--text-subtle); font-style: italic; }
</style>

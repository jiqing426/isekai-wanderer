<template>
  <div class="activity-chest">
    <div class="chest-header">
      <h3 class="chest-title">🎁 {{ $t('activityChest.title') }}</h3>
      <span class="activity-score">{{ currentScore }}/{{ maxScore }}</span>
    </div>

    <!-- Progress bar with milestones -->
    <div class="progress-container">
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${(currentScore / maxScore) * 100}%` }"></div>
      </div>
      <div class="milestones">
        <div
          v-for="ms in milestones"
          :key="ms.threshold"
          class="milestone"
          :class="{ reached: currentScore >= ms.threshold, claimed: ms.claimed }"
          :style="{ left: `${(ms.threshold / maxScore) * 100}%` }"
        >
          <div class="ms-dot"></div>
          <span class="ms-label">{{ ms.threshold }}</span>
          <n-tooltip trigger="hover">
            <template #trigger>
              <span class="ms-icon">{{ ms.claimed ? '✅' : currentScore >= ms.threshold ? '🎁' : '🔒' }}</span>
            </template>
            {{ ms.reward }} 💎
          </n-tooltip>
        </div>
      </div>
    </div>

    <!-- Claim buttons -->
    <div class="chest-actions">
      <n-button
        v-for="ms in claimableMilestones"
        :key="ms.threshold"
        size="small"
        type="primary"
        @click="claimChest(ms.threshold)"
      >{{ $t('activityChest.claimReward', { threshold: ms.threshold }) }}</n-button>
    </div>

    <!-- Daily activity sources -->
    <div class="activity-sources">
      <div class="source" v-for="source in activitySources" :key="source.id">
        <span class="source-icon">{{ source.icon }}</span>
        <span class="source-name">{{ $t(`activityChest.sources.${source.id}`) }}</span>
        <span class="source-points">+{{ source.points }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';

const { t } = useI18n();
const message = useMessage();

interface Milestone {
  threshold: number;
  reward: number;
  claimed: boolean;
}

interface ActivitySource {
  id: string;
  name: string;
  icon: string;
  points: number;
}

const currentScore = ref(0);
const maxScore = ref(100);
const milestones = ref<Milestone[]>([
  { threshold: 20, reward: 10, claimed: false },
  { threshold: 50, reward: 30, claimed: false },
  { threshold: 80, reward: 60, claimed: false },
  { threshold: 100, reward: 100, claimed: false },
]);

const activitySources = ref<ActivitySource[]>([
  { id: 'login', name: '登录', icon: '📱', points: 10 },
  { id: 'play', name: '游玩剧本', icon: '🎮', points: 20 },
  { id: 'choice', name: '做出选择', icon: '🎯', points: 15 },
  { id: 'share', name: '分享', icon: '📤', points: 10 },
  { id: 'community', name: '社区互动', icon: '💬', points: 15 },
]);

const claimableMilestones = computed(() =>
  milestones.value.filter(ms => currentScore.value >= ms.threshold && !ms.claimed)
);

async function claimChest(threshold: number) {
  try {
    await gameApi.claimActivityChest(threshold);
    const ms = milestones.value.find(m => m.threshold === threshold);
    if (ms) ms.claimed = true;
    message.success(t('activityChest.claimSuccess', { threshold }));
  } catch (err) {
    message.error(t('activityChest.claimFailed', { error: err instanceof Error ? err.message : '' }));
  }
}

async function loadProgress() {
  try {
    const resp = await gameApi.getActivityProgress();
    currentScore.value = resp.current_score;
    maxScore.value = resp.max_score;
    if (resp.milestones) {
      milestones.value = resp.milestones;
    }
  } catch (err) {
    console.warn('加载活跃度失败:', err instanceof Error ? err.message : err);
  }
}

onMounted(() => {
  loadProgress();
});
</script>

<style scoped>
.activity-chest { width: 100%; }
.chest-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.chest-title { font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0; }
.activity-score {
  font-size: 14px;
  font-weight: 700;
  color: var(--brand-primary);
  font-variant-numeric: tabular-nums;
}
.progress-container {
  position: relative;
  margin-bottom: 24px;
}
.progress-track {
  height: 8px;
  border-radius: 4px;
  background: rgba(167, 139, 250, 0.08);
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #A78BFA, #F472B6);
  transition: width 0.5s ease;
}
.milestones {
  position: relative;
  height: 32px;
  margin-top: 4px;
}
.milestone {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
}
.ms-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(167, 139, 250, 0.3);
  margin: 0 auto 2px;
}
.milestone.reached .ms-dot { background: #18A058; }
.ms-label { font-size: 9px; color: var(--text-subtle); display: block; }
.ms-icon { font-size: 14px; cursor: pointer; }
.chest-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.activity-sources {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.source {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--text-muted);
}
.source-icon { font-size: 14px; }
.source-points { color: var(--brand-primary); font-weight: 600; }
</style>

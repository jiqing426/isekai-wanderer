<template>
  <div class="page-bg">
    <div class="achievement-page">
      <header class="page-header">
        <h1 class="gradient-text">🏆 {{ $t('achievement.title') }}</h1>
        <p class="subtitle">{{ $t('achievement.subtitle') }}</p>
        <div class="stats">
          <div class="stat">
            <span class="stat-num">{{ unlockedCount }}</span>
            <span class="stat-label">{{ $t('achievement.unlocked') }}</span>
          </div>
          <div class="stat">
            <span class="stat-num">{{ achievements.length }}</span>
            <span class="stat-label">{{ $t('achievement.total') }}</span>
          </div>
        </div>
      </header>

      <n-spin :show="loading">
        <n-empty v-if="!loading && achievements.length === 0" :description="$t('achievement.noAchievements')" />

        <div v-else class="achievement-grid">
          <div
            v-for="(ach, i) in achievements"
            :key="ach.id"
            class="ach-card glass-card fade-in-up"
            :class="{ locked: !ach.isUnlocked, claimed: ach.isClaimed }"
            :style="{ animationDelay: `${i * 0.05}s` }"
          >
            <div class="ach-icon" :class="{ 'locked-icon': !ach.isUnlocked }">
              {{ ach.isUnlocked ? ach.icon : '🔒' }}
            </div>
            <div class="ach-body">
              <div class="ach-name">{{ ach.name }}</div>
              <div class="ach-desc">{{ ach.description }}</div>
              <div v-if="ach.condition" class="ach-condition">
                <span class="condition-value">{{ conditionLabel(ach.condition, ach.progress) }}</span>
              </div>
              <div v-if="ach.condition" class="ach-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${progressPercentage(ach)}%` }"
                  ></div>
                </div>
              </div>
              <div v-if="ach.reward" class="ach-reward">
                {{ rewardLabel(ach.reward) }}
              </div>
              <div v-if="ach.isUnlocked" class="ach-time">
                {{ formatDate(ach.unlockedAt) }}
              </div>
            </div>
            <div class="ach-action" v-if="ach.isUnlocked && !ach.isClaimed">
              <n-button size="small" type="primary" @click="claimAchievement(ach)">{{ $t('achievement.claim') }}</n-button>
            </div>
            <n-tag v-if="ach.isClaimed" size="small" type="success" :bordered="false">{{ $t('achievement.claimed') }}</n-tag>
          </div>
        </div>
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi, type Achievement } from '@/api/game';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Achievements',
  meta: [{ name: 'description', content: () => t('achievement.metaDesc') }],
});

const message = useMessage();
const loading = ref(false);

type AchievementCondition = NonNullable<Achievement['condition']>;
type AchievementProgress = NonNullable<Achievement['progress']>;
type AchievementReward = NonNullable<Achievement['reward']>;

function conditionLabel(condition: AchievementCondition | undefined, progress: AchievementProgress | undefined): string {
  if (!condition) return '';
  const typeMap: Record<string, string> = {
    'dialogue_count': t('achievementView.condDialogueCount'),
    'completed_scripts': t('achievementView.condCompletedScripts'),
    'affection': t('achievementView.condAffection'),
    'cg_count': t('achievementView.condCgCount'),
    'gifts_sent': t('achievementView.condGiftsSent'),
    'choice_count': t('achievementView.condChoiceCount'),
    'streak': t('achievementView.condStreak'),
    'friends_count': t('achievementView.condFriendsCount'),
    'branches_explored': t('achievementView.condBranchesExplored'),
    'characters_unlocked': t('achievementView.condCharactersUnlocked'),
    'all_good_endings': t('achievementView.condAllGoodEndings'),
    'all_achievements_unlocked': t('achievementView.condAllAchievementsUnlocked'),
    // Legacy keys
    'dialogue': t('achievementView.condDialogueCount'),
    'choice': t('achievementView.condChoiceCount'),
    'ending': t('achievementView.condEnding'),
    'script': t('achievementView.condCompletedScripts'),
    'checkin': t('achievementView.condCheckin'),
    'gift': t('achievementView.condGiftsSent'),
    'fragments': t('achievementView.condFragments'),
    'cg': t('achievementView.condCgCount'),
  };
  const label = typeMap[condition.type] || condition.type;
  const current = progress?.current ?? condition.current ?? 0;
  const target = progress?.target ?? condition.target ?? condition.value ?? 0;
  return `${label}：${current} / ${target}`;
}

function rewardLabel(reward: AchievementReward | undefined): string {
  if (!reward) return '';
  const typeMap: Record<string, string> = {
    'fragments': t('achievementView.rewardFragments'),
    'fragment': t('achievementView.rewardFragments'),
    'gold': t('achievementView.rewardGold'),
    'exp': t('achievementView.rewardExp'),
    'dialogue': t('achievementView.condDialogueCount'),
  };
  const label = typeMap[reward.type] || reward.type;
  return `🎁 ${reward.amount} ${label}`;
}

function progressPercentage(ach: Achievement): number {
  const progress = ach.progress;
  const condition = ach.condition;
  const current = progress?.current ?? condition?.current ?? 0;
  const target = progress?.target ?? condition?.target ?? condition?.value ?? 1;
  if (target <= 0) return 0;
  return Math.min(100, Math.round((current / target) * 100));
}

const achievements = ref<Achievement[]>([]);
const unlockedCount = computed(() => achievements.value.filter(a => a.isUnlocked).length);

function formatDate(iso: string | null): string {
  if (!iso) return t('achievementView.unknownDate');
  const date = new Date(iso);
  if (isNaN(date.getTime())) return t('achievementView.unknownDate');
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

async function claimAchievement(ach: Achievement) {
  try {
    await gameApi.claimAchievement(ach.id);
    ach.isClaimed = true;
    ach.claimedAt = new Date().toISOString();
    message.success(t('achievement.claimSuccess', { name: ach.name }));
  } catch (err) {
    message.error(t('achievement.claimFailed'));
  }
}

async function loadAchievements() {
  loading.value = true;
  try {
    const resp = await gameApi.getAchievements();
    achievements.value = resp.achievements;
  } catch (err) {
    message.error(t('achievement.loadFailed'));
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadAchievements();
});
</script>

<style scoped>
.achievement-page { max-width: 800px; margin: 0 auto; padding: 24px 16px 48px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 700; margin: 0; }
.subtitle { color: var(--text-muted); font-size: 14px; margin: 4px 0 12px; }
.stats { display: flex; gap: 24px; }
.stat { text-align: center; }
.stat-num { display: block; font-size: 24px; font-weight: 800; color: var(--brand-primary); }
.stat-label { font-size: 12px; color: var(--text-muted); }
.achievement-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ach-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}
.ach-card.locked { opacity: 0.5; }
.ach-card.claimed { border: 1px solid rgba(24, 160, 88, 0.2); }
.ach-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(244, 114, 182, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}
.locked-icon { filter: grayscale(1); }
.ach-body { flex: 1; min-width: 0; }
.ach-name { font-size: 15px; font-weight: 600; color: var(--text-main); margin-bottom: 2px; }
.ach-desc { font-size: 12px; color: var(--text-muted); }
.ach-time { font-size: 10px; color: var(--text-subtle); margin-top: 4px; }
.ach-action { flex-shrink: 0; }
.ach-condition {
  font-size: 11px;
  color: var(--text-subtle);
  margin-top: 4px;
}
.condition-label {
  opacity: 0.8;
}
.condition-value {
  color: var(--brand-primary);
  font-weight: 600;
}

.ach-progress {
  margin-top: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #f472b6);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .achievement-page { padding: 16px 12px 32px; }
  .page-header { margin-bottom: 16px; }
  .page-header h1 { font-size: 20px; }
  .subtitle { font-size: 13px; margin: 4px 0 10px; }
  .stats { gap: 16px; }
  .stat-num { font-size: 20px; }
  .stat-label { font-size: 11px; }
  .achievement-grid { gap: 10px; }
  .ach-card { flex-direction: column; align-items: stretch; gap: 10px; padding: 14px; }
  .ach-icon { width: 40px; height: 40px; font-size: 24px; align-self: center; }
  .ach-body { width: 100%; }
  .ach-name { font-size: 14px; }
  .ach-desc { font-size: 11px; }
  .ach-condition { font-size: 10px; }
  .ach-time { font-size: 10px; }
  .ach-action { align-self: stretch; }
}
</style>

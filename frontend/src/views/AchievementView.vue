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
            :class="{ locked: !ach.unlocked, claimed: ach.claimed }"
            :style="{ animationDelay: `${i * 0.05}s` }"
          >
            <div class="ach-icon" :class="{ 'locked-icon': !ach.unlocked }">
              {{ ach.unlocked ? ach.icon : '🔒' }}
            </div>
            <div class="ach-body">
              <div class="ach-name">{{ ach.name }}</div>
              <div class="ach-desc">{{ ach.description }}</div>
              <div v-if="ach.condition && !ach.unlocked" class="ach-condition">
                <span class="condition-value">{{ conditionLabel(ach.condition) }}</span>
              </div>
              <div v-if="ach.reward" class="ach-reward">
                {{ rewardLabel(ach.reward) }}
              </div>
              <div v-if="ach.unlocked" class="ach-time">
                {{ formatDate(ach.unlocked_at) }}
              </div>
            </div>
            <div class="ach-action" v-if="ach.unlocked && !ach.claimed">
              <n-button size="small" type="primary" @click="claimAchievement(ach)">{{ $t('achievement.claim') }}</n-button>
            </div>
            <n-tag v-if="ach.claimed" size="small" type="success" :bordered="false">{{ $t('achievement.claimed') }}</n-tag>
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
import { gameApi } from '@/api/game';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Achievements',
  meta: [{ name: 'description', content: () => t('achievement.metaDesc') }],
});

const message = useMessage();
const loading = ref(false);

interface AchievementReward {
  type: string;
  amount: number;
  claimed: boolean;
}

interface AchievementCondition {
  type: string;
  target?: number;
  current?: number;
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  unlocked: boolean;
  unlocked_at: string | null;
  claimed: boolean;
  condition?: AchievementCondition | string;
  reward?: AchievementReward | string;
}

function parseJsonField<T>(field: T | string | undefined): T | null {
  if (!field) return null;
  if (typeof field === 'string') {
    try { return JSON.parse(field) as T; } catch { return null; }
  }
  return field as T;
}

function conditionLabel(condition: AchievementCondition | string | undefined): string {
  const parsed = parseJsonField<AchievementCondition>(condition);
  if (!parsed) return '';
  const typeMap: Record<string, string> = {
    'dialogue': '对话次数',
    'choice': '做出选择',
    'affection': '好感度',
    'ending': '解锁结局',
    'script': '完成剧本',
    'checkin': '签到',
    'gift': '赠送礼物',
    'fragments': '碎片收集',
    'cg': '收集 CG',
  };
  const label = typeMap[parsed.type] || parsed.type;
  const current = parsed.current ?? 0;
  const target = parsed.target ?? '?';
  return `${label}：${current} / ${target}`;
}

function rewardLabel(reward: AchievementReward | string | undefined): string {
  const parsed = parseJsonField<AchievementReward>(reward);
  if (!parsed) return '';
  const typeMap: Record<string, string> = {
    'fragments': '碎片',
    'fragment': '碎片',
    'gold': '金币',
    'exp': '经验',
    'dialogue': '对话次数',
  };
  const label = typeMap[parsed.type] || parsed.type;
  return `🎁 ${parsed.amount} ${label}`;
}

const achievements = ref<Achievement[]>([]);
const unlockedCount = computed(() => achievements.value.filter(a => a.unlocked).length);

function formatDate(iso: string | null): string {
  if (!iso) return '未知时间';
  const date = new Date(iso);
  if (isNaN(date.getTime())) return '未知时间';
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

async function claimAchievement(ach: Achievement) {
  try {
    await gameApi.claimAchievement(ach.id);
    ach.claimed = true;
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

</style>

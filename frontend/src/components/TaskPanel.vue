<template>
  <div class="task-panel">
    <div class="panel-header">
      <h3 class="panel-title">📋 {{ $t('taskPanel.title') }}</h3>
      <span class="reset-hint">{{ resetHint }}</span>
    </div>

    <n-spin :show="loading" size="small">
      <n-empty v-if="!loading && tasks.length === 0" :description="$t('taskPanel.allDone')" size="small" />

      <div v-else class="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          :class="{ completed: task.completed, claimed: task.claimed }"
        >
          <div class="task-icon">{{ task.completed ? '✅' : '⬜' }}</div>
          <div class="task-info">
            <div class="task-name">{{ task.name }}</div>
            <div class="task-progress">
              <n-progress
                type="line"
                :percentage="Math.min(100, Math.round((task.progress / task.target) * 100))"
                :show-indicator="false"
                :height="4"
                :color="task.completed ? '#18A058' : '#A78BFA'"
                :rail-color="'rgba(167, 139, 250, 0.1)'"
                style="width: 80px"
              />
              <span class="progress-text">{{ task.progress }}/{{ task.target }}</span>
            </div>
          </div>
          <div class="task-reward">
            <span class="reward-badge">💎 {{ task.reward }}</span>
            <n-button
              v-if="task.completed && !task.claimed"
              size="tiny"
              type="primary"
              @click="claimTask(task)"
            >{{ $t('taskPanel.claim') }}</n-button>
            <n-tag v-if="task.claimed" size="tiny" type="success" :bordered="false">{{ $t('taskPanel.claimed') }}</n-tag>
          </div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';

const { t } = useI18n();
const message = useMessage();
const loading = ref(false);

interface DailyTask {
  id: string;
  name: string;
  description: string;
  progress: number;
  target: number;
  completed: boolean;
  claimed: boolean;
  reward: number;
}

const tasks = ref<DailyTask[]>([]);
const resetHint = ref('');

function updateResetHint() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);
  const hours = Math.floor((tomorrow.getTime() - now.getTime()) / 3600000);
  const mins = Math.floor(((tomorrow.getTime() - now.getTime()) % 3600000) / 60000);
  resetHint.value = t('taskPanel.resetHint', { hours, mins });
}

async function claimTask(task: DailyTask) {
  try {
    await gameApi.claimDailyTask(task.id);
    task.claimed = true;
    message.success(t('taskPanel.claimSuccess', { name: task.name, reward: task.reward }));
  } catch (err) {
    message.error(t('taskPanel.claimFailed', { error: err instanceof Error ? err.message : '' }));
  }
}

async function loadTasks() {
  loading.value = true;
  try {
    const resp = await gameApi.getDailyTasks();
    tasks.value = resp.tasks;
    updateResetHint();
  } catch (err) {
    console.warn('加载每日任务失败:', err instanceof Error ? err.message : err);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadTasks();
});
</script>

<style scoped>
.task-panel { width: 100%; }
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.panel-title { font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0; }
.reset-hint { font-size: 11px; color: var(--text-subtle); }
.task-list { display: flex; flex-direction: column; gap: 8px; }
.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.03);
}
.task-item.completed { background: rgba(24, 160, 88, 0.04); }
.task-item.claimed { opacity: 0.6; }
.task-icon { font-size: 16px; flex-shrink: 0; }
.task-info { flex: 1; min-width: 0; }
.task-name { font-size: 13px; font-weight: 500; color: var(--text-main); margin-bottom: 2px; }
.task-progress { display: flex; align-items: center; gap: 6px; }
.progress-text { font-size: 11px; color: var(--text-muted); font-variant-numeric: tabular-nums; }
.task-reward { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.reward-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--brand-primary);
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.08);
}
</style>

<template>
  <div class="page-bg">
    <div class="recap-page">
      <header class="recap-header fade-in-up">
        <n-button text @click="$router.push('/discover')" size="small">
          <template #icon><span style="color: var(--text-muted)">←</span></template>
        </n-button>
        <h1 class="gradient-text">📖 {{ $t('recap.title') }}</h1>
        <p class="subtitle">{{ $t('recap.subtitle') }}</p>
      </header>

      <n-spin :show="loading">
        <n-empty v-if="!loading && recap.length === 0" :description="$t('recap.noRecords')" />

        <div v-else class="recap-timeline">
          <div
            v-for="(event, idx) in recap"
            :key="event.id"
            class="recap-event glass-card fade-in-up"
            :class="{ 'is-choice': event.type === 'choice', 'is-ending': event.type === 'ending' }"
            :style="{ animationDelay: `${idx * 0.08}s` }"
          >
            <div class="event-dot" :class="event.type"></div>
            <div class="event-body">
              <div class="event-meta">
                <span class="event-type-badge" :class="event.type">
                  {{ typeLabel(event.type) }}
                </span>
                <span class="event-scene" v-if="event.scene">🎬 {{ event.scene }}</span>
                <span class="event-time" v-if="event.timestamp">{{ formatTime(event.timestamp) }}</span>
              </div>
              <div class="event-text">{{ event.text }}</div>
              <div v-if="event.choice_text" class="event-choice">
                <span class="choice-arrow">→</span>
                <span class="choice-label">{{ event.choice_text }}</span>
                <span v-if="event.affection_delta" class="choice-delta" :class="event.affection_delta > 0 ? 'pos' : 'neg'">
                  {{ event.affection_delta > 0 ? '+' : '' }}{{ event.affection_delta }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="recap.length > 0" class="recap-summary glass-card fade-in-up">
          <h3>{{ $t('recap.summary') }}</h3>
          <div class="summary-stats">
            <div class="sum-item">
              <span class="sum-num">{{ recap.filter(e => e.type === 'choice').length }}</span>
              <span class="sum-label">{{ $t('recap.choicesMade') }}</span>
            </div>
            <div class="sum-item">
              <span class="sum-num">{{ uniqueScenes }}</span>
              <span class="sum-label">{{ $t('recap.scenesVisited') }}</span>
            </div>
            <div class="sum-item">
              <span class="sum-num">{{ recap.filter(e => e.type === 'ending').length }}</span>
              <span class="sum-label">{{ $t('recap.endingsReached') }}</span>
            </div>
          </div>
        </div>
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Recap',
  meta: [{ name: 'description', content: () => t('recap.subtitle') }],
});

const route = useRoute();
const message = useMessage();
const loading = ref(false);

interface RecapEvent {
  id: string;
  type: 'dialogue' | 'choice' | 'scene_change' | 'ending';
  text: string;
  scene?: string;
  choice_text?: string;
  affection_delta?: number;
  timestamp?: string;
}

const recap = ref<RecapEvent[]>([]);

const uniqueScenes = computed(() => {
  const scenes = new Set(recap.value.filter(e => e.scene).map(e => e.scene));
  return scenes.size;
});

function typeLabel(type: string): string {
  const map: Record<string, string> = {
    dialogue: t('recap.dialogue'),
    choice: t('recap.choice'),
    scene_change: t('recap.sceneChange'),
    ending: t('recap.ending'),
  };
  return map[type] || type;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function loadRecap() {
  const sessionId = route.params.sessionId as string;
  if (!sessionId) return;
  loading.value = true;
  try {
    const resp = await gameApi.getRecap(sessionId);
    recap.value = resp.events || [];
  } catch (err) {
    message.error(t('recap.loadFailed'));
  } finally {
    loading.value = false;
  }
}

onMounted(() => { loadRecap(); });
</script>

<style scoped>
.recap-page { max-width: 700px; margin: 0 auto; padding: 24px 16px 48px; }
.recap-header { margin-bottom: 24px; }
.recap-header h1 { font-size: 24px; font-weight: 700; margin: 8px 0 4px; }
.subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }

.recap-timeline { position: relative; padding-left: 24px; }
.recap-timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(167, 139, 250, 0.15);
}

.recap-event { position: relative; margin-bottom: 12px; padding: 14px 16px; }
.recap-event.is-choice { border-color: rgba(192, 132, 252, 0.2); }
.recap-event.is-ending { border-color: rgba(251, 191, 36, 0.3); }

.event-dot { position: absolute; left: -20px; top: 18px; width: 10px; height: 10px; border-radius: 50%; background: rgba(167, 139, 250, 0.4); }
.event-dot.choice { background: var(--brand-primary); }
.event-dot.ending { background: #fbbf24; }
.event-dot.scene_change { background: #38bdf8; }

.event-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; flex-wrap: wrap; }
.event-type-badge { font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 6px; background: rgba(167, 139, 250, 0.1); color: var(--text-muted); }
.event-type-badge.choice { background: rgba(192, 132, 252, 0.15); color: var(--brand-primary); }
.event-type-badge.ending { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.event-scene { font-size: 11px; color: var(--text-subtle); }
.event-time { font-size: 10px; color: var(--text-subtle); }
.event-text { font-size: 14px; color: var(--text-main); line-height: 1.5; }

.event-choice { display: flex; align-items: center; gap: 8px; margin-top: 8px; padding: 6px 10px; border-radius: 8px; background: rgba(192, 132, 252, 0.06); }
.choice-arrow { color: var(--brand-primary); font-size: 14px; }
.choice-label { font-size: 13px; color: var(--text-main); flex: 1; }
.choice-delta { font-size: 11px; font-weight: 600; }
.choice-delta.pos { color: #86efac; }
.choice-delta.neg { color: #fca5a5; }

.recap-summary { margin-top: 24px; padding: 20px; text-align: center; }
.recap-summary h3 { font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0 0 16px; }
.summary-stats { display: flex; justify-content: center; gap: 32px; }
.sum-item { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.sum-num { font-size: 22px; font-weight: 800; color: var(--brand-primary); font-variant-numeric: tabular-nums; }
.sum-label { font-size: 12px; color: var(--text-muted); }

</style>

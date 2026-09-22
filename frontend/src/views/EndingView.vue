<template>
  <div class="page-bg">
    <div class="ending-page">
      <n-spin :show="loading" size="large">
        <div v-if="ending" class="ending-container fade-in-up">
          <EndingCard
            :title="ending.title"
            :description="ending.description"
            :ending-type="ending.ending_type"
            :monologue="ending.monologue"
            :stats="ending.stats"
          />
          <div class="ending-actions">
            <n-button v-if="ending.ending_type === 'bad'" type="primary" size="large" @click="handleRestart">
              🔄 {{ $t('endingExtra.restartRoute') }}
            </n-button>
            <n-button size="large" secondary @click="router.push('/discover')">
              {{ $t('endingExtra.backToScripts') }}
            </n-button>
          </div>
        </div>
        <n-result v-if="error" status="error" :title="$t('endingExtra.loadFailed')" :description="error">
          <template #footer>
            <n-button @click="loadEnding" type="primary">{{ $t('endingExtra.retry') }}</n-button>
          </template>
        </n-result>
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { api } from '@/api/http';
import EndingCard from '@/components/EndingCard.vue';

const { t } = useI18n();

type EndingType = 'good' | 'bad' | 'normal' | 'true_end' | 'hidden';

interface Ending {
  title: string;
  description: string;
  ending_type: EndingType;
  monologue?: string;
  stats?: { choices: number; finalAffection: number };
}

const route = useRoute();
const router = useRouter();
const ending = ref<Ending | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const sessionId = route.params.sessionId as string;
const scriptId = route.query.script as string || '';

async function loadEnding() {
  loading.value = true;
  error.value = null;
  try {
    ending.value = await api.get<Ending>(`/game/${sessionId}/ending`);
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('endingExtra.loadEndingFailed');
  } finally {
    loading.value = false;
  }
}

onMounted(() => { loadEnding(); });

function handleRestart() {
  // BUG-030-002: 清除 localStorage 中的旧 session，强制重新开始
  localStorage.removeItem('game_session');
  localStorage.removeItem('game_script');
  router.push(`/game?script=${scriptId}`);
}
</script>

<style scoped>
.ending-page { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 24px 16px; }
.ending-container { max-width: 600px; width: 100%; }
.ending-actions { display: flex; justify-content: center; gap: 12px; margin-top: 24px; }

/* Mobile Responsive */
@media (max-width: 768px) {
  .ending-page { padding: 16px 12px; }
  .ending-container { max-width: 100%; }
  .ending-actions { flex-direction: column; gap: 10px; margin-top: 16px; }
  .ending-actions :deep(.n-button) { width: 100%; }
}
</style>

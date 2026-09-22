<template>
  <div class="page-bg">
    <div class="route-map-page">
      <header class="map-header fade-in-up">
        <n-button text @click="router.back()" class="back-btn">← {{ $t('common.back') }}</n-button>
        <h1 class="gradient-text">🗺️ {{ $t('routeMap.title') }}</h1>
        <p class="map-subtitle">{{ scriptTitle }}</p>
      </header>

      <n-spin :show="loading" :description="$t('common.loading')">
        <div v-if="nodes.length > 0" class="route-map-container">
          <div class="route-nodes">
            <div
              v-for="(node, index) in nodes"
              :key="node.node_id"
              class="route-node glass-card"
              :class="{
                'node-current': node.node_id === currentNodeId,
                'node-visited': isVisited(node.node_id),
              }"
            >
              <div class="node-index">{{ index + 1 }}</div>
              <div class="node-body">
                <div class="node-label">{{ node.label }}</div>
                <div class="node-meta">
                  <span v-if="node.emotion" class="node-emotion">{{ emotionEmoji(node.emotion) }}</span>
                  <span class="node-scene">Scene {{ node.scene_index }}</span>
                </div>
                <div v-if="node.choices.length > 0" class="node-choices">
                  <n-tag
                    v-for="choice in node.choices"
                    :key="choice.choice_id"
                    size="small"
                    :type="choice.next_node_id === currentNodeId ? 'primary' : 'default'"
                    class="choice-tag"
                  >
                    {{ choice.label }}
                  </n-tag>
                </div>
              </div>
              <div v-if="index < nodes.length - 1" class="node-connector">
                <svg viewBox="0 0 40 40" class="connector-line">
                  <line x1="20" y1="0" x2="20" y2="40" stroke="var(--brand-primary)" stroke-width="2" stroke-dasharray="4 4" />
                </svg>
              </div>
            </div>
          </div>
        </div>
        <n-empty v-else-if="!loading" :description="$t('routeMap.noRoute')" />
      </n-spin>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi, type RouteMapNode } from '@/api/game';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const message = useMessage();

const sessionId = route.params.sessionId as string;
const scriptTitle = ref('');
const nodes = ref<RouteMapNode[]>([]);
const currentNodeId = ref('');
const loading = ref(false);

useHead({
  title: 'Isekai Wanderer - Route Map',
  meta: [{ name: 'description', content: () => t('routeMap.subtitle') }],
});

function emotionEmoji(emotion: string): string {
  const map: Record<string, string> = {
    normal: '😌', tense: '😰', warm: '🥰', sad: '😢',
    excited: '🤩', angry: '😠', surprised: '😲',
  };
  return map[emotion] || '📖';
}

function isVisited(nodeId: string): boolean {
  const idx = nodes.value.findIndex(n => n.node_id === nodeId);
  const curIdx = nodes.value.findIndex(n => n.node_id === currentNodeId.value);
  return idx < curIdx;
}

async function loadRouteMap() {
  loading.value = true;
  try {
    const resp = await gameApi.getRouteMap(sessionId);
    nodes.value = resp.nodes;
    currentNodeId.value = resp.current_node_id;
    try {
      const script = await gameApi.getScript(resp.script_id);
      scriptTitle.value = script.title;
    } catch {
      scriptTitle.value = resp.script_id;
    }
  } catch (err) {
    message.error(t('routeMap.loadFailed'));
  } finally {
    loading.value = false;
  }
}

onMounted(loadRouteMap);
</script>

<style scoped>
.route-map-page { max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }
.map-header { text-align: center; margin-bottom: 24px; }
.map-header h1 { font-size: 24px; font-weight: 700; margin: 8px 0 4px; }
.map-subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }
.back-btn { color: var(--text-muted) !important; font-size: 13px !important; }
.route-map-container { margin-top: 16px; }
.route-nodes { display: flex; flex-direction: column; align-items: center; gap: 0; }
.route-node { width: 100%; max-width: 480px; padding: 16px 20px; position: relative; display: flex; gap: 16px; align-items: flex-start; transition: all 0.3s ease; }
.route-node:hover { transform: translateX(4px); border-color: rgba(192, 132, 252, 0.3); }
.node-current { border-color: var(--brand-primary) !important; box-shadow: 0 0 20px rgba(79, 70, 229, 0.2); }
.node-visited { opacity: 0.7; }
.node-index { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #4F46E5, #818CF8); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; flex-shrink: 0; }
.node-body { flex: 1; min-width: 0; }
.node-label { font-size: 15px; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }
.node-meta { display: flex; gap: 8px; align-items: center; font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
.node-emotion { font-size: 16px; }
.node-choices { display: flex; flex-wrap: wrap; gap: 6px; }
.choice-tag { font-size: 11px; }
.node-connector { position: absolute; bottom: -24px; left: 50%; transform: translateX(-50%); width: 40px; height: 24px; z-index: 1; }
.connector-line { width: 100%; height: 100%; }

/* === 移动端适配 === */
@media (max-width: 768px) {
  .route-map-page { padding: 16px 8px 32px; }
  .map-header { margin-bottom: 16px; }
  .map-header h1 { font-size: 20px; }
  .map-subtitle { font-size: 13px; }
  .back-btn { font-size: 12px !important; }
  .route-map-container { margin-top: 8px; }
  .route-node { max-width: 100%; padding: 12px 14px; gap: 10px; }
  .route-node:hover { transform: none; }
  .node-index { width: 30px; height: 30px; font-size: 12px; }
  .node-label { font-size: 14px; }
  .node-meta { font-size: 11px; gap: 6px; }
  .node-emotion { font-size: 14px; }
  .node-choices { gap: 4px; }
  .choice-tag { font-size: 10px; }
  .node-connector { bottom: -16px; height: 16px; }
}
</style>

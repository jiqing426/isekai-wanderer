<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="visible" class="history-drawer-overlay" @click="handleOverlayClick">
        <div class="history-drawer" @click.stop>
          <!-- 抽屉头部 -->
          <div class="drawer-header">
            <h3>{{ $t('historyDrawer.title') }}</h3>
            <n-button text @click="close" class="close-btn">
              <span>✕</span>
            </n-button>
          </div>

          <!-- 对话历史列表 -->
          <div class="drawer-content">
            <div v-if="loading && dialogueHistory.length === 0" class="loading-state">
              <n-spin size="medium" />
            </div>
            <div v-else-if="dialogueHistory.length === 0" class="empty-state">
              <p>{{ $t('historyDrawer.noHistory') }}</p>
            </div>
            <div v-else class="history-timeline">
              <div
                v-for="(item, index) in dialogueHistory"
                :key="index"
                class="timeline-item"
                :class="{ 'is-choice': item.type === 'choice' }"
              >
                <div class="timeline-marker">
                  <span v-if="item.type === 'dialogue'">💬</span>
                  <span v-else-if="item.type === 'choice'">🔀</span>
                  <span v-else>📝</span>
                </div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-label">
                      {{ item.type === 'dialogue' ? item.characterName : $t('historyDrawer.yourChoice') }}
                    </span>
                    <span class="timeline-time">{{ formatTime(item.timestamp) }}</span>
                  </div>
                  <div class="timeline-text">{{ item.text }}</div>
                  <div v-if="item.affectionDelta" class="affection-change">
                    💕 {{ item.affectionDelta > 0 ? '+' : '' }}{{ item.affectionDelta }}
                  </div>
                </div>
              </div>
              <!-- {{ $t('historyDrawer.loadMore') }}按钮 -->
              <div v-if="hasMore" class="load-more">
                <n-button @click="loadMore" :loading="loading" size="small">
                  {{ $t('historyDrawer.loadMore') }}
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { NButton, NSpin } from 'naive-ui';
import { gameApi } from '@/api/game';
import { useI18n } from 'vue-i18n'

interface DialogueHistoryItem {
  type: 'dialogue' | 'choice' | 'system';
  characterName?: string;
  text: string;
  timestamp: number;
  affectionDelta?: number;
}

interface Props {
  visible: boolean;
  sessionId?: string;
}

const { t } = useI18n()

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const dialogueHistory = ref<DialogueHistoryItem[]>([]);
const loading = ref(false);
const hasMore = ref(false);
const pageSize = 20;
let currentPage = 0;

function close() {
  emit('close');
}

function handleOverlayClick() {
  emit('close');
}

function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

async function loadHistory(reset = false) {
  if (!props.sessionId) return;
  
  if (reset) {
    dialogueHistory.value = [];
    currentPage = 0;
    hasMore.value = false;
  }
  
  loading.value = true;
  try {
    const offset = currentPage * pageSize;
    const response = await gameApi.getDialogues(props.sessionId, {
      limit: pageSize,
      offset,
    });
    
    const newItems: DialogueHistoryItem[] = response.dialogues.map(d => ({
      type: d.role === 'user' ? 'choice' : 'dialogue',
      characterName: d.character_name || 'AI',
      text: d.content,
      timestamp: new Date(d.created_at).getTime(),
    }));
    
    // 新数据插入到开头（最新的在前面）
    dialogueHistory.value = [...newItems.reverse(), ...dialogueHistory.value];
    
    // 判断是否还有更多
    hasMore.value = response.dialogues.length === pageSize;
    currentPage++;
  } catch (err) {
    console.error('Failed to load dialogue history:', err);
  } finally {
    loading.value = false;
  }
}

function loadMore() {
  loadHistory(false);
}

// 监听 visible 变化，打开时加载历史
watch(() => props.visible, (newVal) => {
  if (newVal) {
    loadHistory(true);
  }
});
</script>

<style scoped>
.history-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  justify-content: flex-end;
}

.history-drawer {
  width: 400px;
  height: 100vh;
  background: var(--bg-primary, #1a1a2e);
  border-left: 1px solid var(--border-color, rgba(167, 139, 250, 0.2));
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.3);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, rgba(167, 139, 250, 0.2));
  background: var(--bg-secondary, #16213e);
}

.drawer-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main, #f5f3ff);
  margin: 0;
}

.close-btn {
  font-size: 20px;
  color: var(--text-muted, #7c6f9b);
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--text-main, #f5f3ff);
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-muted, #7c6f9b);
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timeline-item {
  display: flex;
  gap: 12px;
  position: relative;
}

.timeline-item.is-choice {
  margin-left: 8px;
}

.timeline-marker {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--bg-secondary, #16213e);
  border: 2px solid var(--border-color, rgba(167, 139, 250, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.timeline-content {
  flex: 1;
  background: var(--bg-secondary, #16213e);
  border: 1px solid var(--border-color, rgba(167, 139, 250, 0.1));
  border-radius: 12px;
  padding: 12px 16px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-primary, #a78bfa);
}

.timeline-time {
  font-size: 12px;
  color: var(--text-muted, #7c6f9b);
}

.timeline-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-main, #f5f3ff);
}

.affection-change {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #f472b6;
}

/* 抽屉动画 */
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .history-drawer,
.drawer-leave-active .history-drawer {
  transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .history-drawer,
.drawer-leave-to .history-drawer {
  transform: translateX(100%);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .history-drawer {
    width: 100vw;
  }
}
</style>

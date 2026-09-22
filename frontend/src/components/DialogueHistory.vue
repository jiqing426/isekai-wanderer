<template>
  <div class="dialogue-history" ref="scrollRef">
    <div v-if="history.length === 0" class="empty-hint">
      {{ $t('dialogueHistory.noRecords') }}
    </div>
    <div
      v-for="msg in history"
      :key="msg.id"
      class="history-item"
      :class="{ narrator: msg.is_narrator }"
    >
      <div class="history-meta">
        <span class="history-name" :class="msg.is_narrator ? 'narrator' : 'character'">
          {{ msg.character_name }}
        </span>
        <span class="history-scene" v-if="msg.scene">🎬 {{ msg.scene }}</span>
      </div>
      <div class="history-text">{{ msg.text }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue';

export interface HistoryMessage {
  id: string;
  character_name: string;
  character_id?: string;
  text: string;
  scene?: string;
  is_narrator?: boolean;
  timestamp?: number;
}

const props = defineProps<{
  history: HistoryMessage[];
}>();

const scrollRef = ref<HTMLElement | null>(null);
let _timer: ReturnType<typeof setTimeout> | null = null;

function scrollToBottom() {
  if (!scrollRef.value) {
    console.warn('[DialogueHistory] scrollRef is null!');
    return;
  }
  const el = scrollRef.value;
  console.log('[DialogueHistory] scrollToBottom called', {
    scrollTop: el.scrollTop,
    scrollHeight: el.scrollHeight,
    clientHeight: el.clientHeight,
    style: el.style.cssText,
  });
  el.scrollTop = el.scrollHeight;
  // double-shot for safety
  if (_timer) clearTimeout(_timer);
  _timer = setTimeout(() => {
    if (el) {
      el.scrollTop = el.scrollHeight;
      console.log('[DialogueHistory] delayed scroll', {
        scrollTop: el.scrollTop,
        scrollHeight: el.scrollHeight,
      });
    }
  }, 100);
}

onMounted(() => {
  console.log('[DialogueHistory] mounted, scrollRef:', !!scrollRef.value);
  scrollToBottom();
});

watch(
  () => props.history,
  () => {
    console.log('[DialogueHistory] history changed, len:', props.history.length);
    nextTick(scrollToBottom);
  },
  { deep: true },
);

defineExpose({ scrollToBottom });
</script>

<style scoped>
.dialogue-history {
  position: relative;
  max-height: 280px;
  overflow-y: auto;
  padding: 8px 0;
}
.dialogue-history::-webkit-scrollbar {
  width: 6px;
}
.dialogue-history::-webkit-scrollbar-track {
  background: transparent;
}
.dialogue-history::-webkit-scrollbar-thumb {
  background: rgba(167, 139, 250, 0.2);
  border-radius: 3px;
}
.empty-hint {
  text-align: center;
  color: var(--text-subtle);
  font-size: 12px;
  padding: 20px 0;
}
.history-item {
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 4px;
  background: rgba(167, 139, 250, 0.03);
  transition: background 0.2s;
}
.history-item:hover {
  background: rgba(167, 139, 250, 0.06);
}
.history-item.narrator {
  background: transparent;
  font-style: italic;
  opacity: 0.8;
}
.history-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.history-name {
  font-size: 11px;
  font-weight: 600;
}
.history-name.character {
  color: var(--brand-primary);
}
.history-name.narrator {
  color: var(--text-muted);
}
.history-scene {
  font-size: 10px;
  color: var(--text-subtle);
}
.history-text {
  font-size: 13px;
  color: var(--text-main);
  line-height: 1.5;
}
</style>

<template>
  <div class="memory-card glass-card" :class="{ important: memory.importance >= 0.8 }">
    <div class="memory-header">
      <div class="memory-icon" :class="memory.emotion || 'neutral'">
        {{ emotionEmoji }}
      </div>
      <div class="memory-meta">
        <span class="memory-character">{{ memory.character_name }}</span>
        <span class="memory-importance">
          <span v-for="n in 3" :key="n" class="star" :class="{ filled: n <= importanceStars }">★</span>
        </span>
      </div>
      <span class="memory-time">{{ formatTime(memory.created_at) }}</span>
    </div>
    <div class="memory-content">
      <p class="memory-text">{{ memory.content }}</p>
      <div class="memory-context" v-if="memory.scene_context">
        <span class="context-label">场景:</span>
        <span class="context-value">{{ memory.scene_context }}</span>
      </div>
    </div>
    <div class="memory-tags" v-if="memory.tags && memory.tags.length > 0">
      <n-tag v-for="tag in memory.tags" :key="tag" size="tiny" :bordered="false" type="info">
        {{ tag }}
      </n-tag>
    </div>
    <div class="memory-actions">
      <n-button size="tiny" quaternary @click="$emit('delete', memory.id)">
        删除
      </n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NButton, NTag } from 'naive-ui';
import { computed } from 'vue';

export interface Memory {
  id: string;
  character_id: string;
  character_name: string;
  content: string;
  importance: number;
  emotion?: string;
  scene_context?: string;
  tags?: string[];
  created_at: string;
}

const props = defineProps<{ memory: Memory }>();
defineEmits<{ delete: [id: string] }>();

const EMOTION_EMOJI: Record<string, string> = {
  warm: '💕', happy: '😊', sad: '😢', angry: '😠',
  nervous: '😰', surprised: '😲', loving: '💕', calm: '😌',
};

const emotionEmoji = computed(() =>
  props.memory.emotion ? (EMOTION_EMOJI[props.memory.emotion] || '💭') : '💭'
);

const importanceStars = computed(() => {
  if (props.memory.importance >= 0.8) return 3;
  if (props.memory.importance >= 0.5) return 2;
  return 1;
});

function formatTime(iso: string): string {
  return new Date(iso).toLocaleDateString('zh-CN');
}
</script>

<style scoped>
.memory-card {
  padding: 16px;
  transition: all 0.2s;
}
.memory-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
}
.memory-card.important {
  border-color: rgba(251, 191, 36, 0.2);
  background: rgba(251, 191, 36, 0.03);
}

.memory-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.memory-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: rgba(167, 139, 250, 0.1);
  flex-shrink: 0;
}
.memory-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.memory-character {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}
.memory-importance {
  font-size: 10px;
}
.star { color: rgba(167, 139, 250, 0.3); }
.star.filled { color: #fbbf24; }
.memory-time {
  font-size: 10px;
  color: var(--text-subtle);
  flex-shrink: 0;
}

.memory-content { margin-bottom: 8px; }
.memory-text {
  font-size: 14px;
  color: var(--text-main);
  line-height: 1.5;
  margin: 0;
}
.memory-context {
  margin-top: 6px;
  font-size: 11px;
  color: var(--text-muted);
}
.context-label { color: var(--text-subtle); margin-right: 4px; }
.context-value { color: var(--text-muted); }

.memory-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.memory-actions {
  display: flex;
  justify-content: flex-end;
}
</style>

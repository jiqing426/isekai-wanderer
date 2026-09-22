<template>
  <div class="story-panel">
    <div class="character-tag" v-if="characterName">
      <span class="tag-dot"></span>
      {{ characterName }}
    </div>
    <!-- Loading placeholder: 首次等待 AI 叙事时显示 -->
    <div v-if="isLoading && !displayedText" class="loading-placeholder">
      <div class="loading-pulse">
        <div class="pulse-line"></div>
        <div class="pulse-line short"></div>
        <div class="pulse-line medium"></div>
      </div>
      <span class="loading-label">{{ $t('storyPanel.aiWeaving') }}</span>
    </div>
    <div class="story-text" v-html="formattedText" v-show="displayedText || !isLoading"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  text?: string;
  characterName?: string;
  emotion?: string;
  speed?: number;
}>(), {
  text: '',
  characterName: '',
  emotion: 'neutral',
  speed: 1,
});

// D4: displayedText 直接等于 props.text（computed）
// SSE 本身已是逐字流式输出，前端不需要再叠加打字机
const displayedText = computed(() => props.text || '');

// isLoading: 仅在无文字时显示骨架屏
const isLoading = computed(() => !props.text);

const formattedText = computed(() => {
  return displayedText.value
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
});
</script>

<style scoped>
.story-panel {
  background: rgba(139, 92, 246, 0.04);
  border: 1px solid rgba(167, 139, 250, 0.1);
  border-radius: 16px;
  padding: 24px;
  position: relative;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  transition: all 0.2s ease;
}

.story-panel:hover {
  border-color: rgba(167, 139, 250, 0.2);
}

.character-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(79, 70, 229, 0.1);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--brand-primary, #4F46E5);
  margin-bottom: 12px;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand-primary, #4F46E5);
}

.story-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  word-break: break-word;
}

.story-text :deep(strong) {
  color: var(--brand-primary, #4F46E5);
  font-weight: 700;
}

.story-text :deep(em) {
  color: var(--text-muted);
  font-style: italic;
}

/* Loading placeholder — 骨架屏脉冲效果 */
.loading-placeholder {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px 0;
  animation: fadeIn 0.4s ease-in;
}

.loading-pulse {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pulse-line {
  height: 14px;
  width: 100%;
  border-radius: 7px;
  background: linear-gradient(90deg, rgba(139,92,246,0.06) 25%, rgba(139,92,246,0.15) 50%, rgba(139,92,246,0.06) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s ease-in-out infinite;
}

.pulse-line.short {
  width: 45%;
}

.pulse-line.medium {
  width: 72%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.loading-label {
  font-size: 13px;
  color: var(--text-muted, #9ca3af);
  letter-spacing: 0.5px;
  animation: pulse-text 2s ease-in-out infinite;
}

@keyframes pulse-text {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>

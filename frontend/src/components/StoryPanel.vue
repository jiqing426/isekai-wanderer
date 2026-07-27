<template>
  <div class="story-panel" @click="onPanelClick">
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
      <span class="loading-label">AI 正在编织故事…</span>
    </div>
    <div class="story-text" v-html="formattedText" v-show="displayedText || !isLoading"></div>
    <div v-if="isTyping" class="typing-indicator">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
    <div v-if="isLoading" class="loading-indicator">
      <div class="spinner"></div>
      <span class="loading-text">AI 叙事引擎实时生成中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onUnmounted } from 'vue';

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

const emit = defineEmits<{
  (e: 'complete'): void;
}>();

const displayedText = ref('');
const isTyping = ref(false);
const isPaused = ref(false);
const isLoading = ref(false);
let timer: ReturnType<typeof setInterval> | null = null;

// 情绪→速度映射
const emotionSpeedMap: Record<string, number> = {
  neutral: 1,
  normal: 1,
  excited: 1.8,
  happy: 1.3,
  angry: 1.5,
  sad: 0.7,
  slow: 0.6,
  fear: 1.4,
  surprise: 1.6,
};

const effectiveSpeed = computed(() => {
  const baseSpeed = props.speed || 1;
  const emotionMult = emotionSpeedMap[props.emotion || 'neutral'] || 1;
  return baseSpeed * emotionMult;
});

const formattedText = computed(() => {
  // 处理换行和特殊标记
  return displayedText.value
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
});

function cleanup() {
  if (timer !== null) {
    clearInterval(timer);
    timer = null;
  }
}

function typeWriter(text: string) {
  cleanup();
  displayedText.value = '';
  isTyping.value = true;
  isPaused.value = false;

  const speed = effectiveSpeed.value;

  // 瞬时模式
  if (speed >= 5) {
    displayedText.value = text;
    isTyping.value = false;
    emit('complete');
    return;
  }

  let i = 0;
  const interval = Math.max(10, Math.round(30 / speed)); // 改为30ms/字

  timer = setInterval(() => {
    if (isPaused.value) return;
    if (i < text.length) {
      displayedText.value += text[i];
      i++;
    } else {
      cleanup();
      isTyping.value = false;
      emit('complete');
    }
  }, interval);
}

function onPanelClick() {
  if (isTyping.value) {
    cleanup();
    displayedText.value = props.text;
    isTyping.value = false;
    emit('complete');
  }
}

function togglePause() {
  isPaused.value = !isPaused.value;
}

// 暴露暂停/继续方法给父组件
defineExpose({
  togglePause,
  isPaused,
  isTyping,
  isLoading
});

watch(() => props.text, (newText, oldText) => {
  if (newText && newText !== displayedText.value) {
    // 显示loading状态
    if (!oldText || oldText === '') {
      isLoading.value = true;
      setTimeout(() => {
        isLoading.value = false;
        typeWriter(newText);
      }, 500);
    } else {
      typeWriter(newText);
    }
  }
}, { immediate: true });

watch(effectiveSpeed, () => {
  // 速度变化时如果正在打字，调整间隔
  if (isTyping.value) {
    const remaining = props.text.slice(displayedText.value.length);
    if (remaining) {
      cleanup();
      typeWriter(remaining);
      // 保留已显示部分
      displayedText.value = props.text.slice(0, props.text.length - remaining.length) + displayedText.value;
    }
  }
});

onUnmounted(() => {
  cleanup();
});
</script>

<style scoped>
.story-panel {
  background: rgba(139, 92, 246, 0.04);
  border: 1px solid rgba(167, 139, 250, 0.1);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
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

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0 0;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand-primary, #4F46E5);
  animation: blink 1.4s infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 60%, 100% { opacity: 0.2; }
  30% { opacity: 1; }
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  color: var(--text-secondary);
  animation: fadeIn 0.3s ease-in;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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
</style>

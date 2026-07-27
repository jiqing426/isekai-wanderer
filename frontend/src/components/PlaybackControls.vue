<template>
  <div class="playback-controls">
    <div class="control-group">
      <label class="control-item">
        <input 
          type="checkbox" 
          v-model="autoPlay" 
          @change="handleAutoPlayChange"
          class="control-checkbox"
        />
        <span class="control-label">自动播放</span>
      </label>
      
      <button 
        class="control-button" 
        @click="handleSkipRead"
        :disabled="!hasUnreadNodes"
      >
        ⏭️ 跳过已读
      </button>
      
      <button 
        class="control-button" 
        @click="handlePauseResume"
      >
        {{ isPaused ? '▶️ 继续' : '⏸️ 暂停' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  hasUnreadNodes: boolean;
}>();

const emit = defineEmits<{
  (e: 'autoPlayChange', value: boolean): void;
  (e: 'skipRead'): void;
  (e: 'pauseResume'): void;
}>();

const autoPlay = ref(false);
const isPaused = ref(false);

function handleAutoPlayChange() {
  emit('autoPlayChange', autoPlay.value);
}

function handleSkipRead() {
  emit('skipRead');
}

function handlePauseResume() {
  isPaused.value = !isPaused.value;
  emit('pauseResume');
}

// 暴露状态给父组件
defineExpose({
  autoPlay,
  isPaused
});
</script>

<style scoped>
.playback-controls {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(15, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(167, 139, 250, 0.12);
  padding: 12px 24px;
  z-index: 100;
}

.control-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.control-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #a78bfa;
}

.control-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.control-button {
  padding: 8px 16px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-button:hover:not(:disabled) {
  background: rgba(167, 139, 250, 0.2);
  border-color: rgba(167, 139, 250, 0.3);
}

.control-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .playback-controls {
    padding: 10px 16px;
  }

  .control-group {
    gap: 12px;
  }

  .control-label {
    font-size: 13px;
  }

  .control-button {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>

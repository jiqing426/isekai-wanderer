<template>
  <div class="free-chat-wrapper">
    <!-- AI 回复气泡 -->
    <transition name="fade">
      <div v-if="lastReply" class="reply-bubble">
        <div class="reply-header">
          <span class="reply-avatar">{{ characterName?.[0] || '?' }}</span>
          <span class="reply-character">{{ characterName }}</span>
        </div>
        <div class="reply-text">{{ lastReply }}</div>
        <button class="reply-close" @click="lastReply = ''">✕</button>
      </div>
    </transition>

    <!-- 输入区域 -->
    <div class="free-chat-input" :class="{ expanded: isExpanded }">
      <div v-if="!isExpanded" class="collapsed-trigger" @click="isExpanded = true">
        <span class="trigger-icon">💬</span>
        <span class="trigger-placeholder">输入你想说的话...</span>
      </div>
      <div v-else class="expanded-input">
        <div class="input-row">
          <n-input
            v-model:value="inputText"
            type="textarea"
            placeholder="输入你想说的话..."
            :autosize="{ minRows: 1, maxRows: 4 }"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <n-button
            type="primary"
            :loading="loading"
            :disabled="!inputText.trim()"
            @click="sendMessage"
          >
            发送
          </n-button>
        </div>
        <div class="input-footer">
          <span class="hint">Enter 发送，Shift+Enter 换行</span>
          <n-button text size="small" @click="isExpanded = false">收起</n-button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <n-spin size="small" />
      <span>{{ characterName }}正在思考...</span>
    </div>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <span>{{ error }}</span>
      <n-button text size="small" @click="error = ''">关闭</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMessage } from 'naive-ui';

const props = withDefaults(defineProps<{
  characterId?: string;
  characterName?: string;
  disabled?: boolean;
}>(), {
  characterId: '',
  characterName: '',
});

const emit = defineEmits<{
  (e: 'send', message: string): void;
  (e: 'close'): void;
}>();

const message = useMessage();
const isExpanded = ref(false);
const inputText = ref('');
const loading = ref(false);
const lastReply = ref('');
const error = ref('');

async function sendMessage() {
  if (!inputText.value.trim() || loading.value) return;

  loading.value = true;
  error.value = '';

  try {
    // 调用自由对话 API
    const response = await fetch('/api/v1/chat/free', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('isekai_access_token') || ''}`,
      },
      body: JSON.stringify({
        character_id: props.characterId,
        message: inputText.value.trim(),
      }),
    });

    if (!response.ok) {
      throw new Error(`API 错误: ${response.status}`);
    }

    const data = await response.json();
    lastReply.value = data.reply || '（角色沉默不语...）';
    emit('send', inputText.value.trim());
    inputText.value = '';
  } catch (err) {
    const msg = err instanceof Error ? err.message : '未知错误';
    error.value = `对话失败: ${msg}`;
    message.error(error.value);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.free-chat-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-bubble {
  background: rgba(139, 92, 246, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.15);
  border-radius: 12px;
  padding: 16px;
  position: relative;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reply-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.reply-character {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.reply-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-main);
}

.reply-close {
  position: absolute;
  top: 8px;
  right: 8px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  line-height: 1;
}

.reply-close:hover {
  color: var(--text-main);
}

.free-chat-input {
  border: 1px solid rgba(167, 139, 250, 0.15);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.free-chat-input.expanded {
  border-color: rgba(167, 139, 250, 0.3);
}

.collapsed-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 14px;
  transition: all 0.2s ease;
}

.collapsed-trigger:hover {
  background: rgba(139, 92, 246, 0.04);
  color: var(--text-main);
}

.trigger-icon {
  font-size: 18px;
}

.trigger-placeholder {
  color: var(--text-subtle);
  font-size: 14px;
}

.expanded-input {
  padding: 12px;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
}

.hint {
  font-size: 11px;
  color: var(--text-subtle);
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
  color: var(--text-muted);
}

.error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 8px;
  font-size: 13px;
  color: #ef4444;
}

.fade-enter-active, .fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

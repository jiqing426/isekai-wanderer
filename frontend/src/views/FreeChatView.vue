<template>
  <div class="page-bg">
    <div class="free-chat-page">
      <header class="chat-header fade-in-up">
        <div class="chat-header-row">
          <n-button text @click="router.back()" class="back-btn">← {{ $t('common.back') }}</n-button>
          <h1 class="gradient-text">💬 {{ $t('freeChat.title') }}</h1>
        </div>
      </header>

      <div class="chat-layout">
        <!-- 左侧人物介绍栏 -->
        <aside class="left-sidebar">
          <CharacterInfo
            :character-id="characterId"
            :character-name="characterName"
            :character-title="characterTitle"
          />
          <AffectionDisplay
            :character-id="characterId"
            :value="currentAffection"
          />
          <div class="script-info">
            <div class="script-label">📖 剧本</div>
            <div class="script-value">{{ scriptName }}</div>
          </div>
        </aside>

        <!-- 右侧聊天区域 -->
        <div class="chat-container">
          <div class="chat-messages" ref="messagesContainer">
            <div v-if="messages.length === 0 && !loading" class="chat-welcome fade-in-up">
              <div class="welcome-avatar">✨</div>
              <div class="welcome-text">{{ $t('freeChat.welcome', { name: characterName }) }}</div>
            </div>

            <div
              v-for="(msg, index) in messages"
              :key="index"
              class="chat-message"
              :class="msg.role"
            >
              <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '✨' }}</div>
              <div class="message-bubble">
                <div class="message-content">{{ msg.content }}</div>
                <div v-if="msg.timestamp" class="message-time">{{ formatTime(msg.timestamp) }}</div>
              </div>
            </div>
            <div v-if="loading" class="chat-message assistant">
              <div class="message-avatar">✨</div>
              <div class="message-bubble typing">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
            </div>
          </div>

          <!-- FC-05: 动态话题推荐区域 - 移到输入框上方 -->
          <div class="topic-recommendation" v-if="topics.length > 0">
            <div class="topic-header">
              <span class="topic-icon">💡</span>
              <span class="topic-title">推荐话题</span>
            </div>
            <div class="topic-chips-row">
              <button
                v-for="topic in topics"
                :key="topic.id"
                class="topic-chip-btn"
                @click="useTopic(topic)"
              >
                <span class="topic-emoji">{{ topic.emoji }}</span>
                <span class="topic-text">{{ topic.label }}</span>
              </button>
            </div>
          </div>

          <div class="chat-input-area">
            <n-input
              v-model:value="inputMessage"
              :placeholder="$t('freeChat.inputPlaceholder')"
              @keyup.enter="sendMessage"
              :disabled="loading"
              size="large"
            >
              <template #suffix>
                <n-button
                  text
                  @click="sendMessage"
                  :disabled="!inputMessage.trim() || loading"
                  class="send-btn"
                >
                  📤
                </n-button>
              </template>
            </n-input>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { gameApi, type FreeChatMessage, type FreeChatTopic } from '@/api/game';
import { useAffectionStore } from '@/stores/affection';
import CharacterInfo from '@/components/CharacterInfo.vue';
import AffectionDisplay from '@/components/AffectionDisplay.vue';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const message = useMessage();
const affectionStore = useAffectionStore();

const sessionId = route.params.sessionId as string;
const characterId = ref('');
const characterName = ref('');
const characterTitle = ref('');
const scriptName = ref('');
const affectionValue = ref(0);
const topics = ref<FreeChatTopic[]>([]);
const messages = ref<FreeChatMessage[]>([]);
const inputMessage = ref('');
const loading = ref(false);
const currentTopicId = ref<string | undefined>();
const messagesContainer = ref<HTMLElement | null>(null);
const page = ref(1);
const hasMore = ref(true);
const loadingMore = ref(false);

// 好感度相关
const currentAffection = computed(() => {
  // 直接使用 API 返回的好感度值（包括0）
  return affectionValue.value;
});

// 预设快捷话题
const presetTopics = [
  { id: 'past', emoji: '📖', label: '聊聊你的过去' },
  { id: 'favorite', emoji: '⭐', label: '你最喜欢的地方' },
  { id: 'mood', emoji: '😊', label: '今天的心情' },
  { id: 'dream', emoji: '✨', label: '你的梦想是什么' },
  { id: 'secret', emoji: '🤫', label: '告诉我一个秘密' },
];

// 好感度相关
const affectionLevel = computed(() => {
  if (!characterId.value) return '';
  const aff = affectionStore.getAffection(characterId.value);
  return aff?.level || '';
});

const affectionEmoji = computed(() => {
  const level = affectionLevel.value;
  const emojiMap: Record<string, string> = {
    '相识': '🤝',
    '暧昧': '💕',
    '信赖': '💙',
    '羁绊': '💜',
    '挚友': '💖',
  };
  return emojiMap[level] || '🤝';
});
void affectionEmoji; // used in template

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function loadTopics() {
  try {
    const resp = await gameApi.getFreeChatTopics(sessionId);
    topics.value = resp.topics;
  } catch {
    // 如果API失败，使用预设话题
    topics.value = presetTopics;
  }
}

function useTopic(topic: FreeChatTopic) {
  currentTopicId.value = topic.id;
  inputMessage.value = t('freeChat.topicPrefix', { topic: topic.label });
  sendMessage();
}

async function loadHistory() {
  try {
    const resp = await gameApi.getFreeChatHistory(sessionId);
    messages.value = resp.messages;
    page.value = 1;
    hasMore.value = resp.messages.length >= 20;
    await scrollToBottom();
  } catch {}
}

async function loadMoreHistory() {
  if (loadingMore.value || !hasMore.value) return;
  loadingMore.value = true;
  try {
    const resp = await gameApi.getFreeChatHistory(sessionId, page.value + 1);
    if (resp.messages.length > 0) {
      messages.value = [...resp.messages, ...messages.value];
      page.value += 1;
      hasMore.value = resp.messages.length >= 20;
    } else {
      hasMore.value = false;
    }
  } catch {
    hasMore.value = false;
  } finally {
    loadingMore.value = false;
  }
}

function handleScroll() {
  if (!messagesContainer.value) return;
  if (messagesContainer.value.scrollTop === 0 && hasMore.value && !loadingMore.value) {
    loadMoreHistory();
  }
}

async function sendMessage() {
  const content = inputMessage.value.trim();
  if (!content || loading.value) return;

  messages.value.push({ role: 'user', content });
  inputMessage.value = '';
  await scrollToBottom();

  loading.value = true;
  try {
    const resp = await gameApi.sendFreeChatMessage(sessionId, content, currentTopicId.value);
    messages.value.push({ role: 'assistant', content: resp.reply, timestamp: new Date().toISOString() });
    await scrollToBottom();
  } catch (err) {
    message.error(t('freeChat.sendFailed'));
  } finally {
    loading.value = false;
  }
}

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

onMounted(async () => {
  // FE-FEAT-021: 从 API 加载剧本和角色名称
  // BUG-029-002: 优先使用 query 参数中的角色（用户点击的目标角色），而非 API 返回的玩家角色
  const queryCharacterId = (route.query.characterId as string) || '';
  const queryCharacterName = (route.query.character as string) || '';
  try {
    const status = await gameApi.getGameStatus(sessionId);
    characterId.value = queryCharacterId || status.character_id || '';
    characterName.value = queryCharacterName || status.character_name || t('freeChat.defaultCharacter');
    characterTitle.value = (status as any).character_title || '';
    scriptName.value = status.script_name || (route.query.scriptName as string) || '未知剧本';
    affectionValue.value = status.affection_value || 0;
  } catch {
    characterName.value = queryCharacterName || t('freeChat.defaultCharacter');
    characterTitle.value = '';
    characterId.value = queryCharacterId || '';
    scriptName.value = (route.query.scriptName as string) || '未知剧本';
    affectionValue.value = 0;
  }
  
  // 加载好感度数据（作为备用）
  if (characterId.value && affectionValue.value === 0) {
    await affectionStore.loadAffections();
  }
  
  // FE-FEAT-020: 加载历史对话
  await loadHistory();
  loadTopics();
  
  // 添加滚动事件监听
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll);
  }
});
</script>

<style scoped>
.free-chat-page { 
  max-width: 1200px; 
  margin: 0 auto; 
  padding: 24px 16px; 
  display: flex; 
  flex-direction: column; 
  height: calc(100vh - 60px); 
  overflow: hidden;
}
.chat-header { margin-bottom: 16px; flex-shrink: 0; }
.chat-header-row { display: flex; align-items: center; gap: 12px; }
.chat-header h1 { font-size: 24px; font-weight: 700; margin: 0; }
.back-btn { color: var(--text-muted) !important; font-size: 13px !important; }

/* 两栏布局 */
.chat-layout {
  flex: 1;
  display: flex;
  gap: 24px;
  min-height: 0;
  overflow: hidden;
}

/* 左侧人物介绍栏 */
.left-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow-y: auto;
}

.script-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: rgba(167, 139, 250, 0.05);
  border: 1px solid rgba(167, 139, 250, 0.15);
  border-radius: 12px;
}

.script-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.script-value {
  font-size: 14px;
  color: var(--text-main);
  font-weight: 600;
}

/* 右侧聊天区域 */
.chat-container { 
  flex: 1; 
  display: flex; 
  flex-direction: column; 
  min-height: 0; 
  overflow: hidden;
}

.chat-messages { flex: 1; overflow-y: auto; padding: 16px 0; display: flex; flex-direction: column; gap: 16px; }

.chat-welcome { text-align: center; padding: 40px 20px; flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; }
.welcome-avatar { font-size: 48px; }
.welcome-text { font-size: 16px; color: var(--text-main); }

/* FC-05: 动态话题推荐样式 - 输入框上方 */
.topic-recommendation {
  flex-shrink: 0;
  padding: 12px 16px;
}
.topic-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}
.topic-icon {
  font-size: 16px;
}
.topic-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}
.topic-chips-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.topic-chips-row::-webkit-scrollbar {
  height: 4px;
}
.topic-chips-row::-webkit-scrollbar-thumb {
  background: rgba(192, 132, 252, 0.3);
  border-radius: 2px;
}
.topic-chip-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid var(--border-color);
  background: var(--glass-bg);
  color: var(--text-main);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}
.topic-chip-btn:hover {
  border-color: var(--brand-primary);
  background: rgba(192, 132, 252, 0.1);
  color: var(--brand-primary);
  transform: translateY(-1px);
}
.topic-emoji {
  font-size: 14px;
}
.topic-text {
  font-weight: 500;
}

.chat-message { display: flex; gap: 12px; max-width: 85%; }
.chat-message.user { align-self: flex-end; flex-direction: row-reverse; }
.chat-message.assistant { align-self: flex-start; }
.message-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--glass-bg); display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.message-bubble { padding: 12px 16px; border-radius: 16px; background: var(--glass-bg); border: 1px solid var(--border-color); }
.chat-message.user .message-bubble { background: linear-gradient(135deg, rgba(79, 70, 229, 0.15), rgba(129, 140, 248, 0.15)); border-color: rgba(192, 132, 252, 0.3); }
.message-content { font-size: 14px; line-height: 1.6; color: var(--text-main); white-space: pre-wrap; }
.message-time { font-size: 11px; color: var(--text-subtle); margin-top: 4px; }

.typing { display: flex; gap: 4px; padding: 12px 16px; }
.typing-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--text-muted); animation: typing 1.4s infinite ease-in-out; }
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0%, 60%, 100% { transform: translateY(0); opacity: 0.4; } 30% { transform: translateY(-8px); opacity: 1; } }

.chat-input-area { flex-shrink: 0; padding: 12px 0; border-top: 1px solid var(--border-color); }
.send-btn { font-size: 18px; }

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-layout {
    flex-direction: column;
  }
  .left-sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    padding: 12px;
    gap: 12px;
  }
  .left-sidebar > :deep(.character-info) {
    flex: 1;
    min-width: 200px;
  }
  .left-sidebar > :deep(.affection-display) {
    flex: 1;
    min-width: 200px;
  }
  .script-info {
    flex: 1;
    min-width: 150px;
  }
}
</style>

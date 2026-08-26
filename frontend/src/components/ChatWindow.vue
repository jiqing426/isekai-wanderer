<template>
  <div class="chat-window">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="chat-header-left">
        <h2>{{ characterName }}</h2>
        <div class="affection-badge">
          <span class="heart-icon">❤️</span>
          <span>{{ affectionValue }}/100</span>
        </div>
      </div>
      <button class="detail-btn" @click="goToCharacterDetail">
        <span>📋</span>
        <span>查看详情</span>
      </button>
    </div>

    <!-- 消息列表区 -->
    <div class="message-list" ref="messageListRef" @scroll="handleScroll">
      <div v-if="isLoadingMore" class="loading-more">
        <span>加载中...</span>
      </div>
      <div v-else-if="!hasMoreMessages && messages.length > 0" class="no-more-messages">
        <span>没有更多消息了</span>
      </div>
      <div v-if="messages.length === 0 && !isStreaming" class="empty-messages">
        <p>开始和{{ characterName }}对话吧！</p>
      </div>
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="message.sender_type"
      >
        <div class="message-avatar">
          <img v-if="message.sender_type === 'npc' && characterAvatar && !npcAvatarFailed" :src="characterAvatar" :alt="characterName" class="avatar-img" @error="npcAvatarFailed = true" />
          <span v-else-if="message.sender_type === 'npc'" class="avatar-initial">{{ characterName?.charAt(0) || '?' }}</span>
          <img v-else-if="userAvatar && !userAvatarFailed" :src="userAvatar" alt="我" class="avatar-img" @error="userAvatarFailed = true" />
          <span v-else class="avatar-initial">{{ userDisplayName?.charAt(0) || '我' }}</span>
        </div>
        <div class="message-bubble">
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.created_at) }}</div>
        </div>
      </div>
      <!-- 流式消息气泡 -->
      <div v-if="isStreaming" class="message-item npc">
        <div class="message-avatar">
          <img v-if="characterAvatar && !npcAvatarFailed" :src="characterAvatar" :alt="characterName" class="avatar-img" @error="npcAvatarFailed = true" />
          <span v-else class="avatar-initial">{{ characterName?.charAt(0) || '?' }}</span>
        </div>
        <div class="message-bubble streaming">
          <div class="message-content" v-if="streamingContent">
            {{ streamingContent }}<span class="typing-cursor">▊</span>
          </div>
          <div class="typing-indicator" v-else>
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐话题区 -->
    <div class="topics-section" v-if="topics.length > 0">
      <div class="topics-label">推荐话题：</div>
      <div class="topics-list">
        <div
          v-for="topic in topics"
          :key="topic.id"
          class="topic-tag"
          @click="selectTopic(topic.topic_text)"
        >
          {{ topic.topic_text }}
        </div>
      </div>
    </div>

    <!-- 输入栏 -->
    <div class="input-bar">
      <button class="plus-btn" :class="{ active: showPlusMenu }" @click="togglePlusMenu">
        <span>+</span>
      </button>
      <div class="input-wrapper">
        <textarea
          ref="textareaRef"
          v-model="inputMessage"
          placeholder="输入消息..."
          rows="1"
          @keydown="handleKeydown"
          @input="autoResize"
          :disabled="sending"
        />
      </div>
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="!inputMessage.trim() || sending"
      >
        发送
      </button>

      <!-- 加号菜单 -->
      <Transition name="menu-fade">
        <div v-if="showPlusMenu" class="plus-menu">
          <div class="menu-item" @click="openGiftModal">
            <span>🎁</span>
            <span>送礼</span>
          </div>
          <div class="menu-item" @click="openGiftHistoryModal">
            <span>📜</span>
            <span>送礼记录</span>
          </div>
        </div>
      </Transition>
    </div>

    <!-- 送礼弹框 - 使用统一的 GiftModal 组件 -->
    <GiftModal
      v-model="showGiftModal"
      :target-name="characterName"
      :target-id="characterId"
      @gift-sent="handleGiftSent"
    />

    <!-- 送礼记录弹窗 -->
    <div v-if="showGiftHistoryModal" class="modal-overlay" @click="closeGiftHistoryModal">
      <div class="modal-content" @click.stop>
        <h3>送礼记录</h3>
        <div class="history-list">
          <div v-if="giftHistory.length === 0" class="empty-history">
            <p>暂无送礼记录</p>
          </div>
          <div
            v-for="record in giftHistory"
            :key="record.id"
            class="history-item"
          >
            <div class="history-character">{{ record.character_name }}</div>
            <div class="history-gift">{{ record.gift_icon }} {{ record.gift_name }}</div>
            <div class="history-affection">+{{ record.affection_change }}</div>
            <div class="history-time">{{ formatTime(record.created_at) }}</div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="close-btn" @click="closeGiftHistoryModal">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { characterChatApi, giftApi } from '@/api/characterChat'
import { affectionApi } from '@/api/character'
import { useAuthStore } from '@/stores/auth'
import { gameApi } from '@/api/game'
import GiftModal from '@/components/GiftModal.vue'
import type { ChatMessage, ChatTopic, GiftHistory } from '@/types/chat'

const props = defineProps<{
  characterId: string
  characterName: string
  characterAvatar?: string
  initialAffection?: number
}>()

const router = useRouter()
const authStore = useAuthStore()
const userAvatar = computed(() => {
  const avatar = authStore.user?.avatar
  console.log('[ChatWindow] userAvatar:', avatar, 'user:', authStore.user)
  return avatar || ''
})

const userDisplayName = computed(() => {
  return authStore.user?.displayName || authStore.user?.username || '我'
})

// CR-032: 头像加载失败状态
const npcAvatarFailed = ref(false)
const userAvatarFailed = ref(false)

// 当角色切换时重置失败状态
watch(() => props.characterAvatar, () => {
  npcAvatarFailed.value = false
})

const messages = ref<ChatMessage[]>([])
const topics = ref<ChatTopic[]>([])
const inputMessage = ref('')
const sending = ref(false)
const messageListRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const affectionValue = ref(0)
const streamingContent = ref('')
const isStreaming = ref(false)

// 分页加载状态
const currentPage = ref(1)
const pageSize = 20
const hasMoreMessages = ref(true)
const isLoadingMore = ref(false)

const showPlusMenu = ref(false)
const showGiftModal = ref(false)
const showGiftHistoryModal = ref(false)
const giftHistory = ref<GiftHistory[]>([])

const formatTime = (dateString: string) => {
  // 处理各种日期格式：ISO 8601 带时区偏移、带 Z、或无时区
  let date: Date
  if (dateString.includes('+') || dateString.endsWith('Z')) {
    // 已经有时区信息，直接解析
    date = new Date(dateString)
  } else {
    // 无时区信息，假设为 UTC
    date = new Date(dateString + 'Z')
  }
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return '未知时间'
  }
  
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const loadMessages = async (page: number = 1, prepend: boolean = false) => {
  try {
    isLoadingMore.value = true
    console.log('[ChatWindow] 开始加载消息:', { page, prepend, characterId: props.characterId })
    const response = await characterChatApi.getMessages(props.characterId, page, pageSize)
    console.log('[ChatWindow] 加载消息响应:', { page, count: response.messages.length, total: response.total })
    
    if (prepend) {
      // 保存当前滚动位置
      const container = messageListRef.value
      const oldScrollHeight = container?.scrollHeight || 0
      
      // 将旧消息追加到新消息后面
      messages.value = [...response.messages, ...messages.value]
      
      // 恢复滚动位置
      await nextTick()
      if (container) {
        const newScrollHeight = container.scrollHeight
        container.scrollTop = newScrollHeight - oldScrollHeight
      }
    } else {
      messages.value = response.messages
      await scrollToBottom()
    }
    
    // 判断是否还有更多消息
    hasMoreMessages.value = response.messages.length === pageSize
    currentPage.value = page
    console.log('[ChatWindow] 加载完成:', { currentPage: currentPage.value, hasMore: hasMoreMessages.value })
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    isLoadingMore.value = false
  }
}

const loadMoreMessages = async () => {
  if (isLoadingMore.value || !hasMoreMessages.value) return
  await loadMessages(currentPage.value + 1, true)
}

const handleScroll = () => {
  const container = messageListRef.value
  if (!container) return
  
  // 当滚动到顶部附近时（距离顶部 100px 以内），加载更多
  if (container.scrollTop < 100 && !isLoadingMore.value && hasMoreMessages.value) {
    console.log('[ChatWindow] 触发分页加载，当前页:', currentPage.value)
    loadMoreMessages()
  }
}

const loadTopics = async () => {
  try {
    const response = await characterChatApi.getTopics(props.characterId)
    console.log('[ChatWindow] 加载话题:', props.characterId, response)
    // 后端直接返回数组，不是 { topics: [] }
    topics.value = Array.isArray(response) ? response : (response.topics || [])
  } catch (error) {
    console.error('加载推荐话题失败:', error)
    topics.value = []
  }
}

const loadAffection = async () => {
  try {
    const response = await affectionApi.getAffection(props.characterId)
    console.log('[ChatWindow] 加载好感度:', props.characterId, response)
    affectionValue.value = response.affection_value
  } catch (error) {
    console.error('加载好感度失败:', error)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || sending.value || isStreaming.value) return

  const userContent = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息到列表
  messages.value.push({
    id: Date.now().toString(),
    character_id: props.characterId,
    sender_type: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  })
  await scrollToBottom()

  sending.value = true
  isStreaming.value = true
  streamingContent.value = ''

  try {
    await characterChatApi.sendMessageStream(
      props.characterId,
      userContent,
      {
        onText: (content) => {
          streamingContent.value += content
          scrollToBottom()
        },
        onDone: (messageId) => {
          // 流式完成，将完整消息添加到列表
          messages.value.push({
            id: messageId || Date.now().toString(),
            character_id: props.characterId,
            sender_type: 'npc',
            content: streamingContent.value,
            created_at: new Date().toISOString()
          })
          isStreaming.value = false
          streamingContent.value = ''
          sending.value = false
          
          // 触发对话达人任务进度
          gameApi.updateDailyTaskProgress('task_dialogue').catch(err => {
            console.error('Failed to update dialogue task progress:', err)
          })
        },
        onError: (error) => {
          console.error('流式消息错误:', error)
          isStreaming.value = false
          streamingContent.value = ''
          sending.value = false
        }
      }
    )
  } catch (error) {
    console.error('发送消息失败:', error)
    isStreaming.value = false
    streamingContent.value = ''
    sending.value = false
  }
}

const selectTopic = (topicText: string) => {
  inputMessage.value = topicText
  sendMessage()
}

const togglePlusMenu = () => {
  showPlusMenu.value = !showPlusMenu.value
}

const handleKeydown = (e: KeyboardEvent) => {
  // Enter 发送，Shift+Enter 换行
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

// 点击外部关闭加号菜单
const handleClickOutside = (e: MouseEvent) => {
  if (!showPlusMenu.value) return
  const target = e.target as HTMLElement
  if (!target.closest('.plus-menu') && !target.closest('.plus-btn')) {
    showPlusMenu.value = false
  }
}

const openGiftModal = async () => {
  console.log('[ChatWindow] 打开送礼弹窗')
  showPlusMenu.value = false
  showGiftModal.value = true
}

const handleGiftSent = (result: any) => {
  console.log('[ChatWindow] 送礼成功:', result)
  // 更新好感度
  if (result.new_affection_value !== undefined) {
    affectionValue.value = result.new_affection_value
  }
  // 可以添加系统消息提示
  messages.value.push({
    id: Date.now().toString(),
    character_id: props.characterId,
    sender_type: 'npc',
    content: `谢谢你送的礼物！我好喜欢！`,
    created_at: new Date().toISOString()
  })
  scrollToBottom()
}

const openGiftHistoryModal = async () => {
  showPlusMenu.value = false
  showGiftHistoryModal.value = true
  try {
    const response = await giftApi.getAllGiftHistory()
    giftHistory.value = response.history
  } catch (error) {
    console.error('加载送礼记录失败:', error)
  }
}

const closeGiftHistoryModal = () => {
  showGiftHistoryModal.value = false
}

const goToCharacterDetail = () => {
  router.push(`/characters/${props.characterId}`)
}

// 监听角色切换
watch(() => props.characterId, () => {
  messages.value = []
  topics.value = []
  affectionValue.value = props.initialAffection || 0
  // 关闭所有弹框
  showGiftModal.value = false
  showGiftHistoryModal.value = false
  showPlusMenu.value = false
  loadMessages()
  loadTopics()
  loadAffection()
})

// 监听好感度变化
watch(() => props.initialAffection, (newValue) => {
  if (newValue !== undefined) {
    affectionValue.value = newValue
  }
})

onMounted(() => {
  affectionValue.value = props.initialAffection || 0
  loadMessages()
  loadTopics()
  loadAffection()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.chat-window {
  flex: 1;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  /* 移除 overflow: hidden，让加号菜单能正常显示 */
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-header h2 {
  margin: 0;
  color: var(--text-main);
  font-size: 20px;
}

.detail-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  color: var(--text-main);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.detail-btn:hover {
  background: rgba(79, 70, 229, 0.1);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.affection-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(244, 114, 182, 0.15);
  border: 1px solid rgba(244, 114, 182, 0.3);
  border-radius: 20px;
  color: var(--brand-secondary);
  font-size: 14px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-messages {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.message-item.npc {
  flex-direction: row;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  overflow: hidden;
}

.message-avatar .avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-avatar .avatar-initial {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a78bfa, #f472b6);
  color: white;
  font-size: 18px;
  font-weight: 700;
}

.message-bubble {
  max-width: 70%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 12px 16px;
  border-radius: 16px;
}

.message-item.npc .message-bubble {
  border-top-left-radius: 4px;
}

.message-item.user .message-bubble {
  border-top-right-radius: 4px;
  background: rgba(79, 70, 229, 0.15);
  border-color: rgba(79, 70, 229, 0.3);
}

.message-content {
  color: var(--text-main);
  font-size: 15px;
  line-height: 1.5;
  word-wrap: break-word;
}

.typing-cursor {
  display: inline-block;
  animation: blink 0.8s step-end infinite;
  color: var(--brand-primary);
  font-weight: bold;
}

@keyframes blink {
  50% { opacity: 0; }
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: var(--text-muted);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.message-time {
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 4px;
}

.topics-section {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 12px;
}

.topics-label {
  color: var(--text-muted);
  font-size: 13px;
  white-space: nowrap;
}

.topics-list {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  flex: 1;
}

.topic-tag {
  padding: 6px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  color: var(--text-main);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
}

.topic-tag:hover {
  background: rgba(79, 70, 229, 0.15);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.input-bar {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 12px;
  align-items: center;
  position: relative;
}

.plus-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
}

.plus-btn:hover,
.plus-btn.active {
  background: rgba(79, 70, 229, 0.15);
  border-color: var(--brand-primary);
  color: var(--brand-primary);
}

.plus-btn.active {
  transform: rotate(45deg);
}

.input-wrapper {
  flex: 1;
}

.input-wrapper textarea {
  width: 100%;
  padding: 10px 16px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-main);
  font-size: 14px;
  outline: none;
  transition: all 0.3s;
  resize: none;
  overflow-y: auto;
  max-height: 120px;
  line-height: 1.5;
  font-family: inherit;
  scrollbar-width: none;
}

.input-wrapper textarea::-webkit-scrollbar {
  display: none;
}

.input-wrapper textarea:focus {
  border-color: var(--brand-primary);
  background: var(--input-bg, var(--bg-card));
}

.input-wrapper textarea::placeholder {
  color: var(--text-muted);
}

.send-btn {
  padding: 10px 24px;
  border-radius: 20px;
  border: none;
  background: var(--brand-primary);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
  background: #4338ca;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.plus-menu {
  position: absolute;
  bottom: 70px;
  left: 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 8px;
  box-shadow: var(--card-shadow);
  z-index: 10;
  min-width: 160px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-main);
  font-size: 14px;
  transition: all 0.3s;
}

.menu-item:hover {
  background: rgba(79, 70, 229, 0.1);
  color: var(--brand-primary);
}

/* Menu transition */
.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

/* 送礼记录弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--card-shadow);
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: var(--text-main);
  font-size: 20px;
}

.close-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-card);
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: var(--border-color);
  color: var(--text-main);
}

.history-list {
  margin-bottom: 20px;
}

.empty-history {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.history-gift {
  flex: 1;
  font-size: 14px;
  color: var(--text-main);
}

.history-affection {
  color: var(--brand-secondary);
  font-weight: 600;
  font-size: 14px;
}

.history-time {
  color: var(--text-muted);
  font-size: 12px;
}
</style>

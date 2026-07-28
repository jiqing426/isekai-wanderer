<template>
  <div class="chat-window">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <h2>{{ characterName }}</h2>
      <div class="affection-badge">
        <span class="heart-icon">❤️</span>
        <span>{{ affectionValue }}/100</span>
      </div>
    </div>

    <!-- 消息列表区 -->
    <div class="message-list" ref="messageListRef">
      <div v-if="messages.length === 0" class="empty-messages">
        <p>开始和{{ characterName }}对话吧！</p>
      </div>
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="message.sender_type"
      >
        <div class="message-avatar">
          <span v-if="message.sender_type === 'npc'">🤖</span>
          <span v-else>👤</span>
        </div>
        <div class="message-bubble">
          <div class="message-content">{{ message.content }}</div>
          <div class="message-time">{{ formatTime(message.created_at) }}</div>
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
      <button class="plus-btn" @click="togglePlusMenu">
        <span>+</span>
      </button>
      <input
        v-model="inputMessage"
        type="text"
        placeholder="输入消息..."
        @keyup.enter="sendMessage"
        :disabled="sending"
      />
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="!inputMessage.trim() || sending"
      >
        发送
      </button>

      <!-- 加号菜单 -->
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
    </div>

    <!-- 送礼弹窗 -->
    <div v-if="showGiftModal" class="modal-overlay" @click="closeGiftModal">
      <div class="modal-content" @click.stop>
        <h3>送礼给 {{ characterName }}</h3>
        <div class="gift-list">
          <div
            v-for="gift in gifts"
            :key="gift.id"
            class="gift-item"
            @click="selectGift(gift)"
          >
            <div class="gift-icon">{{ gift.icon }}</div>
            <div class="gift-info">
              <div class="gift-name">{{ gift.name }}</div>
              <div class="gift-price">💎 {{ gift.price }}</div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeGiftModal">取消</button>
          <button
            class="confirm-btn"
            :disabled="!selectedGift || sending"
            @click="sendGift"
          >
            赠送
          </button>
        </div>
      </div>
    </div>

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
import { ref, onMounted, nextTick, watch } from 'vue'
import { characterChatApi, giftApi } from '@/api/characterChat'
import type { ChatMessage, ChatTopic, Gift, GiftHistory } from '@/types/chat'

const props = defineProps<{
  characterId: string
  characterName: string
}>()

const messages = ref<ChatMessage[]>([])
const topics = ref<ChatTopic[]>([])
const inputMessage = ref('')
const sending = ref(false)
const messageListRef = ref<HTMLElement | null>(null)
const affectionValue = ref(0)

const showPlusMenu = ref(false)
const showGiftModal = ref(false)
const showGiftHistoryModal = ref(false)
const gifts = ref<Gift[]>([])
const selectedGift = ref<Gift | null>(null)
const giftHistory = ref<GiftHistory[]>([])

const formatTime = (dateString: string) => {
  const date = new Date(dateString)
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

const loadMessages = async () => {
  try {
    const response = await characterChatApi.getMessages(props.characterId, 1, 50)
    messages.value = response.messages
    await scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

const loadTopics = async () => {
  try {
    const response = await characterChatApi.getTopics(props.characterId)
    topics.value = response.topics
  } catch (error) {
    console.error('加载推荐话题失败:', error)
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || sending.value) return

  sending.value = true
  try {
    const response = await characterChatApi.sendMessage(
      props.characterId,
      inputMessage.value
    )
    messages.value.push(response.message)
    inputMessage.value = ''
    await scrollToBottom()
    
    // 更新好感度
    if (response.affection_change) {
      affectionValue.value = response.affection_change.new_value
    }
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
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

const openGiftModal = async () => {
  showPlusMenu.value = false
  showGiftModal.value = true
  try {
    const response = await giftApi.getAvailableGifts()
    gifts.value = response.gifts
  } catch (error) {
    console.error('加载礼物列表失败:', error)
  }
}

const closeGiftModal = () => {
  showGiftModal.value = false
  selectedGift.value = null
}

const selectGift = (gift: Gift) => {
  selectedGift.value = gift
}

const sendGift = async () => {
  if (!selectedGift.value || sending.value) return

  sending.value = true
  try {
    const response = await giftApi.sendGift({
      character_id: props.characterId,
      gift_id: selectedGift.value.id
    })
    
    // 更新好感度
    affectionValue.value = response.new_affection_value
    
    // 添加系统消息
    messages.value.push({
      id: Date.now().toString(),
      character_id: props.characterId,
      sender_type: 'npc',
      content: `谢谢你送的${selectedGift.value.name}！我好喜欢！`,
      created_at: new Date().toISOString()
    })
    await scrollToBottom()
    
    closeGiftModal()
  } catch (error) {
    console.error('送礼失败:', error)
  } finally {
    sending.value = false
  }
}

const openGiftHistoryModal = async () => {
  showPlusMenu.value = false
  showGiftHistoryModal.value = true
  try {
    const response = await giftApi.getGiftHistory(props.characterId)
    giftHistory.value = response.history
  } catch (error) {
    console.error('加载送礼记录失败:', error)
  }
}

const closeGiftHistoryModal = () => {
  showGiftHistoryModal.value = false
}

// 监听角色切换
watch(() => props.characterId, () => {
  messages.value = []
  topics.value = []
  affectionValue.value = 0
  loadMessages()
  loadTopics()
})

onMounted(() => {
  loadMessages()
  loadTopics()
})
</script>

<style scoped>
.chat-window {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  color: white;
  font-size: 20px;
}

.affection-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 107, 157, 0.2);
  border-radius: 20px;
  color: white;
  font-size: 14px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-messages {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
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
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-bubble {
  max-width: 70%;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 16px;
  border-radius: 16px;
}

.message-item.npc .message-bubble {
  border-top-left-radius: 4px;
}

.message-item.user .message-bubble {
  border-top-right-radius: 4px;
  background: rgba(102, 126, 234, 0.3);
}

.message-content {
  color: white;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-time {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin-top: 4px;
}

.topics-section {
  padding: 12px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
}

.topics-label {
  color: rgba(255, 255, 255, 0.7);
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
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  color: white;
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
}

.topic-tag:hover {
  background: rgba(255, 255, 255, 0.25);
}

.input-bar {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  gap: 12px;
  align-items: center;
  position: relative;
}

.plus-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.plus-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.input-bar input {
  flex: 1;
  padding: 10px 16px;
  border-radius: 20px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-size: 14px;
  outline: none;
}

.input-bar input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.send-btn {
  padding: 10px 24px;
  border-radius: 20px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.plus-menu {
  position: absolute;
  bottom: 70px;
  left: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  cursor: pointer;
  color: #333;
  font-size: 14px;
  transition: all 0.3s;
}

.menu-item:hover {
  background: rgba(102, 126, 234, 0.1);
}

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
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

.gift-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.gift-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.gift-item:hover {
  border-color: #667eea;
}

.gift-icon {
  font-size: 32px;
}

.gift-info {
  flex: 1;
}

.gift-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.gift-price {
  font-size: 13px;
  color: #666;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn,
.close-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn:hover,
.close-btn:hover {
  background: #f5f5f5;
}

.confirm-btn {
  padding: 10px 24px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.history-list {
  margin-bottom: 20px;
}

.empty-history {
  text-align: center;
  color: #999;
  padding: 40px 20px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.history-gift {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.history-affection {
  color: #ff6b9d;
  font-weight: 600;
  font-size: 14px;
}

.history-time {
  color: #999;
  font-size: 12px;
}
</style>

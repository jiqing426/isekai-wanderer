import { api } from './http'
import type { ChatMessage, ChatTopic, Gift, GiftHistory } from '@/types/chat'

export interface StreamCallbacks {
  onText: (content: string) => void
  onDone: (messageId: string) => void
  onError: (error: string) => void
}

export const characterChatApi = {
  // 获取聊天消息
  getMessages(characterId: string, page: number = 1, pageSize: number = 20) {
    return api.get<{ messages: ChatMessage[]; total: number }>(`/character-chat/${characterId}/messages?page=${page}&page_size=${pageSize}`)
  },

  // 发送消息（非流式）
  sendMessage(characterId: string, content: string) {
    return api.post<{ message: ChatMessage; npc_message?: ChatMessage; affection_change?: { old_value: number; new_value: number } }>(`/character-chat/${characterId}/messages`, { content })
  },

  // 发送消息（流式）
  async sendMessageStream(characterId: string, content: string, callbacks: StreamCallbacks): Promise<void> {
    const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
    const token = match ? decodeURIComponent(match[2]) : null;
    if (!token) {
      callbacks.onError('未登录');
      return;
    }
    const response = await fetch(`/api/v1/character-chat/${characterId}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content })
    })

    if (!response.ok) {
      callbacks.onError(`HTTP ${response.status}`)
      return
    }

    const reader = response.body?.getReader()
    if (!reader) {
      callbacks.onError('No response body')
      return
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          // event type already handled by data parsing
          continue
        }
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6)
          try {
            const data = JSON.parse(dataStr)
            if (data.type === 'text') {
              callbacks.onText(data.content || '')
            } else if (data.type === 'done') {
              callbacks.onDone(data.message_id || '')
            } else if (data.type === 'error') {
              callbacks.onError(data.message || 'Unknown error')
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', dataStr, e)
          }
        }
      }
    }
  },

  // 获取推荐话题
  getTopics(characterId: string) {
    return api.get<{ topics: ChatTopic[] }>(`/character-chat/${characterId}/topics`)
  }
}

export const giftApi = {
  // 获取可用礼物列表
  getAvailableGifts() {
    return api.get<{ gifts: Gift[] }>('/gifts/available')
  },

  // 送礼
  sendGift(data: { character_id: string; gift_id: string }) {
    return api.post<{ new_affection_value: number }>('/gifts/send', data)
  },

  // 获取送礼记录
  getGiftHistory(characterId: string) {
    return api.get<{ history: GiftHistory[] }>(`/gifts/history/${characterId}`)
  },
  getAllGiftHistory() {
    return api.get<{ history: GiftHistory[] }>('/gifts/history')
  }
}

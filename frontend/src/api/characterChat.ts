import { api } from './http'
import type { ChatMessage, ChatTopic, Gift, GiftHistory } from '@/types/chat'

export const characterChatApi = {
  // 获取聊天消息
  getMessages(characterId: string, page: number = 1, pageSize: number = 20) {
    return api.get<{ messages: ChatMessage[]; total: number }>(`/character-chat/${characterId}/messages?page=${page}&page_size=${pageSize}`)
  },

  // 发送消息
  sendMessage(characterId: string, content: string) {
    return api.post<{ message: ChatMessage; affection_change?: { old_value: number; new_value: number } }>(`/character-chat/${characterId}/messages`, { content })
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
  }
}

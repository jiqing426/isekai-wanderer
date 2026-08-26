export interface ChatMessage {
  id: string
  character_id: string
  sender_type: 'npc' | 'user'
  content: string
  created_at: string
}

export interface ChatTopic {
  id: string
  character_id: string
  topic_text: string
}

export interface Gift {
  id: string
  name: string
  icon: string
  price: number
}

export interface GiftHistory {
  id: string
  character_id: string
  character_name: string
  gift_name: string
  gift_icon: string
  affection_change: number
  created_at: string
}

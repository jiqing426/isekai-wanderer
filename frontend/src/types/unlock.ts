export type UnlockType = 'cg' | 'achievement' | 'hidden_story' | 'voice' | 'exclusive_script' | 'reward_float' | 'multi_reward'
export type Rarity = 'R' | 'SR' | 'SSR'

export interface UnlockReward {
  type: 'fragment' | 'exp' | 'gold'
  amount: number
}

export interface UnlockData {
  type: UnlockType
  title: string
  description: string
  image?: string
  rarity?: Rarity
  reward?: UnlockReward
  rewards?: UnlockReward[]  // 多奖励汇总
  contentId?: string
  onConfirm?: () => void
  onLater?: () => void
}

export interface UnlockRecord {
  id: number
  type: UnlockType
  content_id: string
  title: string
  description: string
  image?: string
  rarity?: Rarity
  reward?: UnlockReward
  rewards?: UnlockReward[]
  unlocked_at: string
  viewed: boolean
}

export interface UnlockListResponse {
  unlocks: UnlockRecord[]
  total: number
}

export interface PendingUnlockResponse {
  pending: UnlockData[]
}

export interface RecordUnlockRequest {
  type: UnlockType
  content_id: string
  title: string
  description: string
  image?: string
  rarity?: Rarity
  reward?: UnlockReward
  rewards?: UnlockReward[]
}

export interface RecordUnlockResponse {
  id: number
  success: boolean
}

export interface BatchUnlockRequest {
  unlocks: RecordUnlockRequest[]
}

export interface BatchUnlockResponse {
  ids: number[]
  success: boolean
}

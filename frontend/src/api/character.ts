import { api } from './http'
import type { Character } from '@/types/character'

export const characterApi = {
  // 获取所有角色列表
  getCharacters() {
    return api.get<{ characters: Character[] }>('/characters')
  },

  // 获取用户已解锁的角色列表（后端未实现，暂时返回所有角色）
  getUnlockedCharacters() {
    return api.get<{ characters: Character[] }>('/characters')
  },

  // 获取角色详情
  getCharacterDetail(characterId: string) {
    return api.get<Character>(`/characters/${characterId}`)
  }
}

export const affectionApi = {
  // 获取用户所有角色的好感度
  getAllAffections() {
    return api.get<{ affections: Array<{ character_id: string; value: number; level: string; character_name?: string; level_label?: string }> }>('/affection')
  },

  // 获取单个角色的好感度
  getAffection(characterId: string) {
    return api.get<{ character_id: string; affection_value: number; level: string }>(`/affection/${characterId}`)
  }
}

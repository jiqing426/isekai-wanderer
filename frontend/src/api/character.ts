import request from '@/utils/request'
import type { ApiResponse } from '@/types/api'
import type { Character } from '@/types/character'

export const characterApi = {
  // 获取用户已解锁的角色列表
  getUnlockedCharacters() {
    return request<ApiResponse<{ characters: Character[] }>>({
      url: '/characters/unlocked',
      method: 'get'
    })
  },

  // 获取角色详情
  getCharacterDetail(characterId: string) {
    return request<ApiResponse<Character>>({
      url: `/characters/${characterId}`,
      method: 'get'
    })
  }
}

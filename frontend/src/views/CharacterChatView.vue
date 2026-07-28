<template>
  <div class="character-chat-page">
    <div class="chat-container">
      <!-- 左侧角色列表 -->
      <CharacterList
        :characters="characters"
        :selected-character-id="selectedCharacterId"
        @select-character="handleSelectCharacter"
      />

      <!-- 右侧聊天窗口 -->
      <ChatWindow
        v-if="selectedCharacterId"
        :character-id="selectedCharacterId"
        :character-name="selectedCharacterName"
      />
      <div v-else class="no-character-selected">
        <p>请选择一个角色开始对话</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import CharacterList from '@/components/CharacterList.vue'
import ChatWindow from '@/components/ChatWindow.vue'
import { characterApi } from '@/api/character'
import type { Character } from '@/types/character'

const characters = ref<Character[]>([])
const selectedCharacterId = ref<string | null>(null)
const selectedCharacterName = computed(() => {
  const char = characters.value.find(c => c.id === selectedCharacterId.value)
  return char?.name || ''
})

const handleSelectCharacter = (characterId: string) => {
  selectedCharacterId.value = characterId
}

onMounted(async () => {
  try {
    // 获取用户已解锁的角色列表
    const response = await characterApi.getUnlockedCharacters()
    characters.value = response.characters || []
    
    // 默认选择第一个角色
    if (characters.value.length > 0) {
      selectedCharacterId.value = characters.value[0].id
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
})
</script>

<style scoped>
.character-chat-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.chat-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 40px);
}

.no-character-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  color: white;
  font-size: 18px;
}
</style>

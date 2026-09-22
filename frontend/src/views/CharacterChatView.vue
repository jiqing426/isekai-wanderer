<template>
  <div class="character-chat-page">
    <!-- 移动端顶部导航栏 -->
    <div v-if="isMobile" class="mobile-header">
      <button 
        class="toggle-btn"
        @click="showCharacterList = !showCharacterList"
      >
        <span class="icon">{{ showCharacterList ? '💬' : '👥' }}</span>
        <span class="text">{{ showCharacterList ? $t('characterChat.backToChat') : $t('characterChat.characterList') }}</span>
      </button>
      <div v-if="!showCharacterList && selectedCharacterName" class="current-character">
        {{ selectedCharacterName }}
      </div>
    </div>

    <div class="chat-container">
      <!-- 左侧角色列表 -->
      <CharacterList
        v-show="!isMobile || showCharacterList"
        :characters="characters"
        :selected-character-id="selectedCharacterId"
        :class="{ 'mobile-full': isMobile }"
        @select-character="handleSelectCharacter"
      />

      <!-- 右侧聊天窗口 -->
      <ChatWindow
        v-show="!isMobile || !showCharacterList"
        v-if="selectedCharacterId"
        :class="{ 'mobile-full': isMobile }"
        :character-id="selectedCharacterId"
        :character-name="selectedCharacterName"
        :character-avatar="selectedCharacterAvatar"
        :initial-affection="selectedCharacterAffection"
      />
      <div 
        v-show="!isMobile || !showCharacterList"
        v-else 
        class="no-character-selected"
        :class="{ 'mobile-full': isMobile }"
      >
        <p>{{ $t('characterChat.selectCharacter') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import CharacterList from '@/components/CharacterList.vue'
import ChatWindow from '@/components/ChatWindow.vue'
import { characterApi, affectionApi } from '@/api/character'
import { useI18n } from 'vue-i18n'
import type { Character } from '@/types/character'

const { t } = useI18n()
const characters = ref<Character[]>([])
const selectedCharacterId = ref<string | null>(null)

// 移动端适配状态
const isMobile = ref(false)
const showCharacterList = ref(false)

// 响应式检测
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  // 桌面端切换时重置状态
  if (!isMobile.value) {
    showCharacterList.value = false
  }
}

const selectedCharacterName = computed(() => {
  const char = characters.value.find(c => c.id === selectedCharacterId.value)
  return char?.name || ''
})

const selectedCharacterAffection = computed(() => {
  const char = characters.value.find(c => c.id === selectedCharacterId.value)
  return char?.affection_value || 0
})

const selectedCharacterAvatar = computed(() => {
  const char = characters.value.find(c => c.id === selectedCharacterId.value)
  return char?.avatar_url || ''
})

const handleSelectCharacter = (characterId: string) => {
  selectedCharacterId.value = characterId
  // 移动端选择角色后自动返回聊天界面
  if (isMobile.value) {
    showCharacterList.value = false
  }
}

onMounted(async () => {
  // 初始化移动端检测
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  try {
    // 并行获取角色列表和好感度数据
    const [charactersResponse, affectionsResponse] = await Promise.all([
      characterApi.getCharacters(),
      affectionApi.getAllAffections()
    ])
    
    const charactersList = charactersResponse.characters || []
    const affectionsList = affectionsResponse.affections || []
    
    // 创建好感度映射
    const affectionMap = new Map(affectionsList.map(a => [a.character_id, a]))
    
    // 合并好感度数据到角色列表
    characters.value = charactersList.map(char => {
      const affection = affectionMap.get(char.id)
      return {
        ...char,
        affection_value: affection?.value ?? 0,
        affection_level: affection?.level ?? t('characterChat.defaultLevel')
      }
    })
    
    // 默认选择第一个角色
    if (characters.value.length > 0) {
      selectedCharacterId.value = characters.value[0].id
    }
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.character-chat-page {
  min-height: calc(100vh - 60px);
  background: linear-gradient(160deg, var(--page-bg-start) 0%, var(--page-bg-end) 100%);
  padding: 20px;
}

/* 移动端顶部导航栏 */
.mobile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--glass-bg);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-main);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--brand-primary);
}

.toggle-btn .icon {
  font-size: 16px;
}

.current-character {
  margin-left: auto;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.chat-container {
  display: flex;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: calc(100vh - 100px);
}

/* 桌面端：CharacterList 固定宽度，ChatWindow 占剩余空间 */
.chat-container :deep(.character-list) {
  width: 320px;
  flex-shrink: 0;
}

.chat-container > .mobile-full {
  flex: 1;
  min-width: 0;
}

.no-character-selected.mobile-full {
  flex: 1;
  min-width: 0;
}

.no-character-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  color: var(--text-main);
  font-size: 18px;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .character-chat-page {
    padding: 12px;
  }

  .chat-container {
    height: calc(100vh - 160px);
  }

  .chat-container > .mobile-full {
    width: 100%;
    flex: none;
  }
}
</style>

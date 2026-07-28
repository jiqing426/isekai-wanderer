<template>
  <div class="character-list">
    <div class="list-header">
      <h2>我的角色</h2>
    </div>
    <div class="list-content">
      <div
        v-for="character in characters"
        :key="character.id"
        class="character-item"
        :class="{ active: character.id === selectedCharacterId }"
        @click="handleSelect(character.id)"
      >
        <div class="character-avatar">
          <img :src="character.avatar_url" :alt="character.name" />
        </div>
        <div class="character-info">
          <div class="character-name">{{ character.name }}</div>
          <div class="affection-bar">
            <div
              class="affection-fill"
              :style="{ width: `${character.affection_value}%` }"
            ></div>
          </div>
          <div class="affection-text">好感度: {{ character.affection_value }}/100</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Character } from '@/types/character'

defineProps<{
  characters: Character[]
  selectedCharacterId: string | null
}>()

const emit = defineEmits<{
  (e: 'select-character', characterId: string): void
}>()

const handleSelect = (characterId: string) => {
  emit('select-character', characterId)
}
</script>

<style scoped>
.character-list {
  width: 320px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.list-header h2 {
  margin: 0;
  color: white;
  font-size: 20px;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.character-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
}

.character-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.character-item.active {
  background: rgba(255, 255, 255, 0.2);
}

.character-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.character-name {
  color: white;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.affection-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.affection-fill {
  height: 100%;
  background: linear-gradient(90deg, #ff6b9d, #c06c84);
  transition: width 0.5s ease;
}

.affection-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
}
</style>

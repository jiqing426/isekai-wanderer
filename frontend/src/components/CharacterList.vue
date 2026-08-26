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
          <img v-if="character.avatar_url && !imageErrors.has(character.id)" :src="character.avatar_url" :alt="character.name" @error="handleImageError(character.id)" />
          <div v-else class="avatar-placeholder">
            <span>{{ character.name.charAt(0) }}</span>
          </div>
        </div>
        <div class="character-info">
          <div class="character-name">{{ character.name }}</div>
          <div class="affection-bar">
            <div
              class="affection-fill"
              :style="{ width: `${character.affection_value}%` }"
            ></div>
          </div>
          <div class="affection-text">
            <span>{{ getAffectionStatus(character.affection_value) }}</span>
            <span>{{ character.affection_value }}/100</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Character } from '@/types/character'

defineProps<{
  characters: Character[]
  selectedCharacterId: string | null
}>()

const emit = defineEmits<{
  (e: 'select-character', characterId: string): void
}>()

const imageErrors = ref<Set<string>>(new Set())

const handleSelect = (characterId: string) => {
  emit('select-character', characterId)
}

const handleImageError = (characterId: string) => {
  imageErrors.value.add(characterId)
}

const getAffectionStatus = (value: number): string => {
  if (value >= 80) return '挚友'
  if (value >= 60) return '羁绊'
  if (value >= 40) return '信赖'
  if (value >= 20) return '暧昧'
  return '相识'
}
</script>

<style scoped>
.character-list {
  width: 320px;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.list-header h2 {
  margin: 0;
  color: var(--text-main);
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
  background: rgba(79, 70, 229, 0.1);
}

.character-item.active {
  background: rgba(79, 70, 229, 0.15);
  border-left: 3px solid var(--brand-primary);
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

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary));
  color: white;
  font-size: 24px;
  font-weight: 600;
}

.character-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.character-name {
  color: var(--text-main);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.affection-bar {
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.affection-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand-primary), var(--brand-secondary));
  transition: width 0.5s ease;
}

.affection-text {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 12px;
}

.affection-text span:first-child {
  color: var(--brand-secondary);
  font-weight: 500;
}
</style>

<template>
  <div class="character-scroll-list">
    <div class="scroll-container">
      <div 
        v-for="character in characters" 
        :key="character.id" 
        class="character-card"
        :class="{ selected: selectedCharacterId === character.id }"
        @click="emit('select', character.id)"
      >
        <div class="character-avatar">
          <span class="character-emoji">{{ character.emoji }}</span>
        </div>
        <div class="character-name">{{ character.name }}</div>
        <div class="character-title">{{ character.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Character {
  id: string;
  emoji: string;
  name: string;
  title: string;
}

defineProps<{
  characters: Character[];
  selectedCharacterId: string | null;
}>();

const emit = defineEmits<{
  (e: 'select', characterId: string): void;
}>();
</script>

<style scoped>
.character-scroll-list {
  width: 100%;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.character-scroll-list::-webkit-scrollbar {
  display: none;
}

.scroll-container {
  display: flex;
  gap: 16px;
  padding: 8px 0;
}

.character-card {
  flex-shrink: 0;
  width: 140px;
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.character-card:hover {
  border-color: rgba(167, 139, 250, 0.3);
  background: rgba(167, 139, 250, 0.1);
  transform: translateY(-4px);
}

.character-card.selected {
  border-color: #a78bfa;
  background: rgba(167, 139, 250, 0.15);
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.4);
}

.character-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 12px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.character-emoji {
  font-size: 40px;
}

.character-name {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.character-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}
</style>

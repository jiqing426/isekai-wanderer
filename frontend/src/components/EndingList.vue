<template>
  <div class="ending-list">
    <div v-for="ending in unlockedEndings" :key="ending.id" class="ending-item unlocked">
      <span class="ending-icon">✅</span>
      <span class="ending-name">{{ ending.name }}</span>
      <span class="ending-type">｜{{ ending.type }}</span>
    </div>
    <div v-if="lockedCount > 0" class="ending-item locked">
      <span class="ending-icon">🔒</span>
      <span class="ending-name">【{{ lockedCount }}个未解锁结局】</span>
      <span class="ending-hint">（含隐藏真结局）</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Ending {
  id: string;
  name: string;
  type: string;
}

defineProps<{
  unlockedEndings: Ending[];
  lockedCount: number;
}>();
</script>

<style scoped>
.ending-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ending-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.8);
}

.ending-item.locked {
  opacity: 0.6;
  background: rgba(255, 255, 255, 0.03);
}

.ending-icon {
  font-size: 18px;
}

.ending-name {
  font-weight: 600;
}

.ending-type {
  color: rgba(167, 139, 250, 0.9);
  font-weight: 600;
}

.ending-hint {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}
</style>

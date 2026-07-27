<template>
  <div class="cg-preview-grid">
    <div v-for="cg in cgs" :key="cg.id" class="cg-item" :class="{ locked: cg.isLocked }">
      <div class="cg-thumbnail">
        <span v-if="cg.isLocked" class="lock-icon">🔒</span>
        <span v-else class="cg-emoji">{{ cg.emoji }}</span>
      </div>
    </div>
    <div class="cg-hint">
      完整版 CG 前往画廊查看
    </div>
  </div>
</template>

<script setup lang="ts">
interface CG {
  id: string;
  emoji?: string;
  isLocked: boolean;
}

defineProps<{
  cgs: CG[];
}>();
</script>

<style scoped>
.cg-preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-width: 500px;
}

.cg-item {
  aspect-ratio: 4/3;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 150px;
  max-height: 112px;
}

.cg-item.locked {
  opacity: 0.5;
}

.cg-thumbnail {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.cg-item:not(.locked) .cg-thumbnail {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
}

.lock-icon {
  font-size: 20px;
}

.cg-emoji {
  font-size: 28px;
}

.cg-hint {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
}

/* Responsive */
@media (max-width: 768px) {
  .cg-preview-grid {
    grid-template-columns: repeat(2, 1fr);
    max-width: 100%;
  }
  
  .cg-item {
    max-width: 120px;
    max-height: 90px;
  }
}
</style>

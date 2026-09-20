<template>
  <div class="cg-preview-grid">
    <div v-for="cg in cgs" :key="cg.id" class="cg-item" :class="{ locked: cg.isLocked }">
      <div class="cg-thumbnail">
        <span v-if="cg.isLocked" class="lock-icon">🔒</span>
        <img v-else-if="cg.image_url || cg.thumbnail_url" :src="cg.image_url || cg.thumbnail_url" class="cg-image" />
        <span v-else class="cg-emoji">{{ cg.emoji }}</span>
      </div>
      <div class="cg-info">
        <div class="cg-title">{{ cg.title }}</div>
        <div v-if="cg.chapter" class="cg-chapter">{{ cg.chapter }}</div>
        <div v-if="cg.description" class="cg-description">{{ cg.description }}</div>
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
  image_url?: string;
  thumbnail_url?: string;
  title?: string;
  chapter?: string;
  description?: string;
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
  gap: 20px;
  max-width: 1200px;
}

.cg-item {
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
}

.cg-item.locked {
  opacity: 0.5;
}

.cg-thumbnail {
  width: 100%;
  aspect-ratio: 16/9;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.cg-item:not(.locked) .cg-thumbnail {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
}

.lock-icon {
  font-size: 32px;
}

.cg-emoji {
  font-size: 40px;
}

.cg-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.cg-item:hover .cg-image {
  transform: scale(1.05);
}

.cg-info {
  padding: 12px;
}

.cg-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cg-chapter {
  font-size: 12px;
  color: rgba(167, 139, 250, 0.9);
  margin-bottom: 6px;
}

.cg-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
    grid-template-columns: 1fr;
    max-width: 100%;
  }
}
</style>

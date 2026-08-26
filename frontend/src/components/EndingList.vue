<template>
  <div class="ending-list">
    <div v-for="(chapterData, index) in chapterEndings" :key="`chapter-${index}-${chapterData.chapterIndex}`" class="chapter-group">
      <div class="chapter-header">
        <span class="chapter-label">{{ chapterData.chapter }}</span>
        <span class="chapter-progress">{{ chapterData.unlockedCount }}/{{ chapterData.endings.length }} 结局</span>
      </div>
      <div class="endings-grid">
        <div
          v-for="ending in chapterData.endings"
          :key="ending.id"
          class="ending-item"
          :class="{ unlocked: ending.unlocked, locked: !ending.unlocked }"
        >
          <div class="ending-image">
            <img v-if="ending.image_url" :src="ending.image_url" :alt="ending.name" @error="handleImageError" />
            <div v-if="!ending.unlocked" class="ending-lock-overlay">
              <span class="ending-lock-icon">🔒</span>
            </div>
          </div>
          <div class="ending-content">
            <div class="ending-header">
              <span v-if="ending.name" class="ending-name">{{ ending.name }}</span>
              <span v-if="ending.type" class="ending-type">{{ endingTypeLabel(ending.type) }}</span>
            </div>
            <div v-if="ending.unlocked && ending.description" class="ending-description">{{ ending.description }}</div>
            <div v-else-if="!ending.unlocked" class="ending-hint">完成本章以解锁结局</div>
            <div v-else class="ending-hint">暂无结局描述</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="chapterEndings.length === 0" class="ending-item locked">
      <div class="ending-image">
        <span class="ending-icon">🔒</span>
      </div>
      <div class="ending-content">
        <div class="ending-header">
          <span class="ending-name">暂无结局</span>
        </div>
        <div class="ending-hint">完成剧本以解锁结局</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Ending {
  id: string;
  name: string;
  type: string;
  description?: string;
  unlockCondition?: string;
  unlocked: boolean;
  image_url?: string;
}

interface ChapterEnding {
  chapter: string;
  chapterIndex: number;
  endings: Ending[];
  unlockedCount: number;
}

defineProps<{
  chapterEndings: ChapterEnding[];
  lockedCount: number;
}>();

const endingTypeLabel = (type: string): string => {
  const map: Record<string, string> = {
    good: '好结局',
    bad: '坏结局',
    normal: '普通结局',
    true_end: '真结局',
    hidden: '隐藏结局'
  };
  return map[type] || type;
};

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement;
  img.style.display = 'none';
  const parent = img.parentElement;
  if (parent) {
    const icon = document.createElement('span');
    icon.className = 'ending-icon';
    icon.textContent = '🖼️';
    parent.appendChild(icon);
  }
};
</script>

<style scoped>
.ending-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.chapter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
}

.chapter-label {
  font-size: 14px;
  padding: 4px 12px;
  background: rgba(251, 191, 36, 0.15);
  color: rgba(251, 191, 36, 0.9);
  border-radius: 6px;
  font-weight: 600;
}

.chapter-progress {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.endings-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.ending-item {
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s;
}

.ending-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.ending-item.locked {
  opacity: 0.6;
}

.ending-image {
  width: 100%;
  aspect-ratio: 16/9;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.ending-item:not(.locked) .ending-image {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
}

.ending-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.ending-item:hover .ending-image img {
  transform: scale(1.05);
}

.ending-icon {
  font-size: 32px;
}

.ending-lock-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.ending-lock-icon {
  font-size: 28px;
}

.ending-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ending-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ending-name {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ending-type {
  font-size: 12px;
  padding: 2px 8px;
  background: rgba(167, 139, 250, 0.2);
  color: rgba(167, 139, 250, 0.9);
  border-radius: 4px;
  font-weight: 600;
  flex-shrink: 0;
}

.ending-description {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ending-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Responsive */
@media (max-width: 768px) {
  .endings-grid {
    grid-template-columns: 1fr;
  }
}
</style>

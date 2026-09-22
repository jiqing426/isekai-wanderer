<template>
  <div class="route-tree">
    <div v-for="chapter in chapters" :key="chapter.id" class="chapter-node">
      <div 
        class="chapter-header" 
        :class="{ current: chapter.isCurrent, locked: chapter.isLocked, unlocked: !chapter.isLocked }"
        @click="handleChapterClick(chapter)"
      >
        <span class="chapter-icon">
          {{ chapter.isCompleted ? '✅' : chapter.isCurrent ? '🔵' : chapter.isLocked ? '🔒' : '🔓' }}
        </span>
        <span class="chapter-title">{{ chapter.title }}</span>
        <span v-if="chapter.isLocked && chapter.lockReason" class="lock-reason">
          （{{ chapter.lockReason }}）
        </span>
        <span v-else-if="!chapter.isLocked" class="play-hint">{{ $t('routeTree.clickToContinue') }}</span>
      </div>
      
      <div v-if="chapter.subRoutes && chapter.subRoutes.length > 0" class="sub-routes">
        <div 
          v-for="route in chapter.subRoutes" 
          :key="route.id" 
          class="sub-route"
          :class="{ locked: route.isLocked }"
        >
          <span class="route-icon">{{ route.icon }}</span>
          <span class="route-name">{{ route.name }}</span>
          <span v-if="route.isLocked" class="route-lock">【{{ route.lockReason }}】</span>
          <span v-else-if="route.affection" class="route-affection">
            {{ $t('routeTree.affectionStatus', { affection: route.affection, status: route.status }) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

interface SubRoute {
  id: string;
  icon: string;
  name: string;
  affection?: number;
  status?: string;
  isLocked: boolean;
  lockReason?: string;
}

interface Chapter {
  id: string;
  routeId?: string;
  title: string;
  isCompleted: boolean;
  isCurrent: boolean;
  isLocked: boolean;
  lockReason?: string;
  subRoutes?: SubRoute[];
}

defineProps<{
  chapters: Chapter[];
}>();

const emit = defineEmits<{
  (e: 'chapter-click', chapter: Chapter): void;
}>();


function handleChapterClick(chapter: Chapter) {
  if (chapter.isLocked) {
    return;
  }
  emit('chapter-click', chapter);
}
</script>

<style scoped>
.route-tree {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-node {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.chapter-header.current {
  background: rgba(167, 139, 250, 0.15);
  border-color: rgba(167, 139, 250, 0.4);
  color: #fff;
}

.chapter-header.locked {
  opacity: 0.5;
}

.chapter-icon {
  font-size: 18px;
}

.chapter-title {
  flex: 1;
}

.lock-reason {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
}

.sub-routes {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 40px;
  border-left: 2px solid rgba(167, 139, 250, 0.2);
  margin-left: 20px;
}

.sub-route {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.sub-route.locked {
  opacity: 0.5;
}

.route-icon {
  font-size: 16px;
}

.route-name {
  flex: 1;
}

.route-lock {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.route-affection {
  font-size: 12px;
  color: rgba(167, 139, 250, 0.9);
}
</style>

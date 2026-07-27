<template>
  <div class="post-card" @click="handleClick">
    <div class="post-header">
      <div class="author-info">
        <div v-if="post.author?.avatar" class="author-avatar-wrapper">
          <img 
            :src="post.author.avatar" 
            :alt="post.author.name || '匿名用户'" 
            class="author-avatar" 
          />
        </div>
        <div v-else class="author-avatar-wrapper">
          <div class="author-avatar-initial">
            {{ (post.author?.name || '匿名用户').charAt(0).toUpperCase() }}
          </div>
        </div>
        <div class="author-details">
          <span class="author-name">{{ post.author?.name || '匿名用户' }}</span>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
        </div>
      </div>
      <DeletePostButton v-if="canDelete" :post-id="post.id" @deleted="emit('deleted', post.id)" />
    </div>

    <div class="post-content">
      <h3 class="post-title">{{ post.title }}</h3>
      <p class="post-text">{{ post.content }}</p>
    </div>

    <div v-if="post.images && post.images.length > 0" class="post-images">
      <img
        v-for="(image, index) in post.images"
        :key="index"
        :src="image"
        :alt="`Image ${index + 1}`"
        class="post-image"
        @click.stop="$emit('image-click', index)"
      />
    </div>

    <div class="post-footer">
      <div class="post-stats">
        <span class="stat-item">
          <span class="stat-icon">👁️</span>
          <span class="stat-value">{{ post.stats?.views ?? 0 }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-icon">💬</span>
          <span class="stat-value">{{ post.stats?.comments ?? 0 }}</span>
        </span>
      </div>

      <div class="post-actions">
        <LikeButton
          :post-id="post.id"
          :is-liked="post.is_liked"
          :likes-count="post.stats?.likes ?? 0"
          @liked="handleLiked"
          @unliked="handleUnliked"
          @click.stop
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import type { Post } from '@/types/community';
import LikeButton from './LikeButton.vue';
import DeletePostButton from './DeletePostButton.vue';

const props = defineProps<{
  post: Post;
}>();

const emit = defineEmits<{
  (e: 'select', post: Post): void;
  (e: 'liked', postId: string, likesCount: number): void;
  (e: 'unliked', postId: string, likesCount: number): void;
  (e: 'deleted', postId: string): void;
  (e: 'image-click', index: number): void;
}>();

function handleClick() {
  emit('select', props.post);
}

const authStore = useAuthStore();

const canDelete = computed(() => {
  return authStore.isAuthenticated && authStore.user?.id === props.post.author?.id;
});

function formatTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN');
}

function handleLiked(likesCount: number) {
  emit('liked', props.post.id, likesCount);
}

function handleUnliked(likesCount: number) {
  emit('unliked', props.post.id, likesCount);
}
</script>

<style scoped>
.post-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.post-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-avatar-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.author-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.author-avatar-initial {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.post-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.post-content {
  margin-bottom: 16px;
}

.post-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.post-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.post-images {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin-bottom: 16px;
}

.post-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.post-image:hover {
  transform: scale(1.05);
}

.post-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.post-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-icon {
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
}

.post-actions {
  display: flex;
  gap: 8px;
}
</style>

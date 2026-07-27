<template>
  <button
    class="like-button"
    :class="{ liked: isLiked }"
    @click="handleClick"
    :disabled="loading"
  >
    <span class="like-icon">{{ isLiked ? '❤️' : '🤍' }}</span>
    <span class="like-count">{{ likesCount }}</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useMessage } from 'naive-ui';
import { likePost, unlikePost } from '@/api/community';

const props = defineProps<{
  postId: string;
  isLiked: boolean;
  likesCount: number;
}>();

const emit = defineEmits<{
  (e: 'liked', newCount: number): void;
  (e: 'unliked', newCount: number): void;
}>();

const authStore = useAuthStore();
const message = useMessage();
const loading = ref(false);

async function handleClick() {
  if (!authStore.isAuthenticated) {
    message.warning('请先登录后再点赞');
    return;
  }

  loading.value = true;
  try {
    if (props.isLiked) {
      const response = await unlikePost(props.postId);
      emit('unliked', response.likes_count);
    } else {
      const response = await likePost(props.postId);
      emit('liked', response.likes_count);
    }
  } catch (error) {
    console.error('点赞操作失败:', error);
    message.error('操作失败，请重试');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.like-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: var(--text-secondary);
}

.like-button:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.like-button.liked {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.like-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  font-size: 16px;
}

.like-count {
  font-weight: 600;
}
</style>

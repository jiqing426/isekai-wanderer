<template>
  <button
    class="delete-button"
    @click="handleClick"
    :disabled="loading"
    title="删除帖子"
  >
    <span class="delete-icon">🗑️</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMessage } from 'naive-ui';
import { deletePost } from '@/api/community';

const props = defineProps<{
  postId: string;
}>();

const emit = defineEmits<{
  (e: 'deleted'): void;
}>();

const message = useMessage();
const loading = ref(false);

async function handleClick() {
  if (!confirm('确定要删除这个帖子吗？此操作不可撤销。')) {
    return;
  }

  loading.value = true;
  try {
    await deletePost(props.postId);
    message.success('帖子已删除');
    emit('deleted');
  } catch (error) {
    console.error('删除帖子失败:', error);
    message.error('删除失败，请重试');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.delete-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-button:hover:not(:disabled) {
  background: #fee;
  border-color: #f66;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.delete-icon {
  font-size: 16px;
}
</style>

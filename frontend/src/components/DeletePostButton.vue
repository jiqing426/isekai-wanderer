<template>
  <button
    class="delete-button"
    @click="handleClick"
    :disabled="loading"
    :title="$t('deletePostButton.deletePost')"
  >
    <span class="delete-icon">🗑️</span>
  </button>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useMessage } from 'naive-ui';
import { deletePost } from '@/api/community';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps<{
  postId: string;
}>();

const emit = defineEmits<{
  (e: 'deleted'): void;
}>();

const message = useMessage();
const loading = ref(false);

async function handleClick() {
  if (!confirm(t('deletePostButton.confirmDelete'))) {
    return;
  }

  loading.value = true;
  try {
    await deletePost(props.postId);
    message.success(t('deletePostButton.deleted'));
    emit('deleted');
  } catch (error) {
    console.error('删除帖子失败:', error);
    message.error(t('deletePostButton.deleteFailed'));
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

<template>
  <n-popconfirm @positive-click="handleFork" positive-text="确认" negative-text="取消">
    <template #trigger>
      <n-button size="tiny" text type="primary">🔀 从这里重新开始</n-button>
    </template>
    将从此快照创建新存档，复制到此节点的所有选择历史。
  </n-popconfirm>
</template>

<script setup lang="ts">
import { useMessage } from 'naive-ui';
import { gameApi } from '@/api/game';

const props = defineProps<{
  snapshotId: string;
}>();

const emit = defineEmits<{
  fork: [newSessionId: string];
}>();

const message = useMessage();

async function handleFork() {
  try {
    const resp = await gameApi.forkFromSnapshot(props.snapshotId);
    message.success('新存档已创建');
    emit('fork', resp.new_session_id);
  } catch (err) {
    message.error(`创建分支失败: ${err instanceof Error ? err.message : '未知错误'}`);
  }
}
</script>

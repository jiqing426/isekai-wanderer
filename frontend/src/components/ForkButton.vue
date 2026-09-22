<template>
  <n-popconfirm @positive-click="handleFork" :positive-text="$t('common.confirm')" :negative-text="$t('common.cancel')">
    <template #trigger>
      <n-button size="tiny" text type="primary">{{ $t('forkButton.restartFromHere') }}</n-button>
    </template>
    {{ $t('forkButton.forkDescription') }}
  </n-popconfirm>
</template>

<script setup lang="ts">
import { useMessage } from 'naive-ui';
import { gameApi } from '@/api/game';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
    message.success(t('forkButton.created'));
    emit('fork', resp.new_session_id);
  } catch (err) {
    message.error(t('forkButton.createFailed', { error: err instanceof Error ? err.message : t('forkButton.unknownError') }));
  }
}
</script>

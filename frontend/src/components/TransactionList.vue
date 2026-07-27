<template>
  <div class="transaction-list">
    <div class="list-header">
      <h3>📋 {{ $t('shardCenter.transactions') }}</h3>
      <div class="filters">
        <n-select
          v-model:value="filterDays"
          :options="daysOptions"
          size="small"
          style="width: 120px"
          @update:value="emitFilter"
        />
        <n-select
          v-model:value="filterType"
          :options="typeOptions"
          size="small"
          style="width: 100px"
          @update:value="emitFilter"
        />
      </div>
    </div>

    <n-empty v-if="transactions.length === 0" :description="$t('shardCenter.noTransactions')" size="small" />

    <div v-else class="list-body">
      <div
        v-for="tx in transactions.filter(t => t != null)"
        :key="tx.id"
        class="tx-row"
      >
        <div class="tx-icon">{{ tx.type === 'earn' ? '📥' : '📤' }}</div>
        <div class="tx-info">
          <div class="tx-desc">{{ tx.description }}</div>
          <div class="tx-source">{{ tx.source }}</div>
        </div>
        <div class="tx-right">
          <span class="tx-amount" :class="tx.type">{{ tx.type === 'earn' ? '+' : '-' }}{{ tx.amount }}</span>
          <span class="tx-time">{{ formatTime(tx.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="hasMore" class="load-more">
      <n-button size="small" @click="$emit('loadMore')" :loading="loadingMore" secondary>{{ $t('shardCenter.loadMore') }}</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NButton, NEmpty, NSelect } from 'naive-ui';
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { ShardTransaction } from '@/api/game';

const { t } = useI18n();

defineProps<{
  transactions: ShardTransaction[];
  hasMore: boolean;
  loadingMore: boolean;
}>();

const emit = defineEmits<{
  filter: [params: { days: number | null; type: string | null }];
  loadMore: [];
}>();

const filterDays = ref<number | null>(null);
const filterType = ref<string | null>(null);

const daysOptions = computed(() => [
  { label: t('shardCenter.allTime'), value: null },
  { label: t('shardCenter.last7days'), value: 7 },
  { label: t('shardCenter.last30days'), value: 30 },
] as any[]);

const typeOptions = computed(() => [
  { label: t('shardCenter.all'), value: null },
  { label: t('shardCenter.earnOnly'), value: 'earn' },
  { label: t('shardCenter.spendOnly'), value: 'spend' },
] as any[]);

function emitFilter() {
  emit('filter', { days: filterDays.value, type: filterType.value });
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
</script>

<style scoped>
.transaction-list { width: 100%; }
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.list-header h3 { font-size: 16px; font-weight: 600; color: var(--text-main); margin: 0; }
.filters { display: flex; gap: 8px; }
.list-body { display: flex; flex-direction: column; gap: 8px; }
.tx-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.03);
}
.tx-icon { font-size: 20px; flex-shrink: 0; }
.tx-info { flex: 1; min-width: 0; }
.tx-desc { font-size: 13px; font-weight: 500; color: var(--text-main); }
.tx-source { font-size: 11px; color: var(--text-subtle); }
.tx-right { text-align: right; flex-shrink: 0; }
.tx-amount {
  display: block;
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.tx-amount.earn { color: #18A058; }
.tx-amount.spend { color: #E11D48; }
.tx-time { font-size: 10px; color: var(--text-subtle); }
.load-more { display: flex; justify-content: center; margin-top: 12px; }
</style>

<template>
  <div class="snapshot-timeline">
    <div class="timeline-header">
      <span class="timeline-title">{{ $t('snapshotTimeline.title') }}</span>
      <n-button size="tiny" type="primary" @click="createManual" :loading="creating">{{ $t('snapshotTimeline.createSnapshot') }}</n-button>
    </div>

    <n-spin :show="loading" size="small">
      <n-empty v-if="!loading && snapshots.length === 0" :description="$t('snapshotTimeline.noSnapshots')" size="small" />
      <div v-else class="timeline-list">
        <div
          v-for="snap in snapshots"
          :key="snap.id"
          class="timeline-item"
          :class="{ pinned: snap.is_pinned, auto: snap.is_auto }"
        >
          <div class="timeline-dot" :class="{ 'dot-auto': snap.is_auto, 'dot-manual': !snap.is_auto }"></div>
          <div class="timeline-content">
            <div class="snap-header">
              <span class="snap-node">{{ snap.node_name }}</span>
              <n-tag v-if="snap.is_auto" size="tiny" :bordered="false" type="default">{{ $t('snapshotTimeline.auto') }}</n-tag>
              <n-tag v-if="!snap.is_auto" size="tiny" :bordered="false" type="success">{{ $t('snapshotTimeline.manual') }}</n-tag>
              <n-tag v-if="snap.is_pinned" size="tiny" :bordered="false" type="warning">{{ $t('snapshotTimeline.pinned') }}</n-tag>
            </div>
            <div class="snap-meta">
              <span>{{ formatTime(snap.created_at) }}</span>
              <span v-if="snap.label" class="snap-label">— {{ snap.label }}</span>
            </div>
            <!-- Expiry warning (AC-SAVE-003.7) -->
            <div v-if="expiringSoon(snap) && !snap.is_pinned" class="snap-expiry">
              {{ $t('snapshotTimeline.autoCleanupWarning', { n: daysUntilExpiry(snap) }) }}
              <n-button size="tiny" text type="warning" @click="pinSnapshot(snap, true)">{{ $t('snapshotTimeline.pin') }}</n-button>
            </div>
            <div class="snap-actions">
              <ForkButton :snapshot-id="snap.id" @fork="$emit('fork', $event)" />
              <n-button
                v-if="!snap.is_pinned"
                size="tiny"
                text
                @click="pinSnapshot(snap, true)"
              >{{ $t('snapshotTimeline.pin') }}</n-button>
              <n-button
                v-else
                size="tiny"
                text
                @click="pinSnapshot(snap, false)"
              >{{ $t('snapshotTimeline.unpin') }}</n-button>
            </div>
          </div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMessage } from 'naive-ui';
import { gameApi } from '@/api/game';
import type { SnapshotItem } from '@/api/game';
import ForkButton from './ForkButton.vue';

const props = defineProps<{
  sessionId: string;
}>();

defineEmits<{
  fork: [newSessionId: string];
}>();

const message = useMessage();
const { t } = useI18n();
const snapshots = ref<SnapshotItem[]>([]);
const loading = ref(false);
const creating = ref(false);

function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function expiringSoon(snap: SnapshotItem): boolean {
  if (!snap.expires_at) return false;
  const days = daysUntilExpiry(snap);
  return days >= 0 && days <= 7;
}

function daysUntilExpiry(snap: SnapshotItem): number {
  if (!snap.expires_at) return 999;
  const exp = new Date(snap.expires_at).getTime();
  const now = Date.now();
  return Math.ceil((exp - now) / 86400000);
}

async function loadSnapshots() {
  loading.value = true;
  try {
    const resp = await gameApi.getSnapshots(props.sessionId);
    snapshots.value = resp.snapshots;
  } catch (err) {
    console.warn('加载快照失败:', err instanceof Error ? err.message : err);
  } finally {
    loading.value = false;
  }
}

async function createManual() {
  creating.value = true;
  try {
    const snap = await gameApi.createSnapshot(props.sessionId);
    snapshots.value.unshift(snap);
    message.success(t('snapshotTimeline.createSuccess'));
  } catch (err) {
    message.error(t('snapshotTimeline.createFailed', { error: err instanceof Error ? err.message : t('snapshotTimeline.unknownError') }));
  } finally {
    creating.value = false;
  }
}

async function pinSnapshot(snap: SnapshotItem, pinned: boolean) {
  try {
    await gameApi.pinSnapshot(snap.id, pinned);
    snap.is_pinned = pinned;
    message.success(pinned ? t('snapshotTimeline.pinnedStatus') : t('snapshotTimeline.unpinnedStatus'));
  } catch (err) {
    message.error(t('snapshotTimeline.operationFailed', { error: err instanceof Error ? err.message : t('snapshotTimeline.unknownError') }));
  }
}

onMounted(() => {
  loadSnapshots();
});
</script>

<style scoped>
.snapshot-timeline {
  width: 100%;
  padding-top: 12px;
  border-top: 1px solid rgba(167, 139, 250, 0.1);
  margin-top: 12px;
}
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.timeline-title { font-size: 14px; font-weight: 600; color: var(--text-main); }
.timeline-list { position: relative; padding-left: 20px; }
.timeline-item {
  position: relative;
  padding-bottom: 16px;
  padding-left: 16px;
  border-left: 2px solid rgba(167, 139, 250, 0.15);
}
.timeline-item:last-child { border-left-color: transparent; padding-bottom: 0; }
.timeline-dot {
  position: absolute;
  left: -7px;
  top: 2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid var(--bg-card, #1a1a2e);
}
.dot-auto { background: rgba(167, 139, 250, 0.5); }
.dot-manual { background: #18A058; }
.timeline-content { flex: 1; }
.snap-header { display: flex; align-items: center; gap: 6px; margin-bottom: 2px; }
.snap-node { font-size: 13px; font-weight: 600; color: var(--text-main); }
.snap-meta { font-size: 11px; color: var(--text-subtle); }
.snap-label { color: var(--text-muted); }
.snap-expiry {
  font-size: 11px;
  color: #F59E0B;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.snap-actions { display: flex; gap: 8px; margin-top: 4px; }
</style>

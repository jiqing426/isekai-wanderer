<template>
  <div class="page-bg">
    <div class="save-manager-page">
      <header class="page-header">
        <h1 class="gradient-text">💾 {{ $t('saveManager.title') }}</h1>
        <p class="subtitle">{{ $t('saveManager.subtitle') }}</p>
      </header>

      <!-- CR-028: 角色筛选标签栏 -->
      <div v-if="characterTabs.length > 0" class="character-filter-tabs">
        <button
          v-for="tab in characterTabs"
          :key="tab.id"
          class="filter-tab"
          :class="{ active: selectedCharacterId === tab.filterValue }"
          @click="selectCharacterFilter(tab.filterValue)"
        >
          {{ tab.name }}
        </button>
      </div>

      <n-spin :show="loading">
        <n-empty v-if="!loading && saves.length === 0" :description="$t('saveManager.noSaves')">
          <template #extra>
            <n-button type="primary" @click="router.push('/discover')">🔍 {{ $t('saveManager.discoverScripts') }}</n-button>
          </template>
        </n-empty>

        <div v-else class="saves-list">
          <div
            v-for="(save, i) in saves"
            :key="save.session_id"
            class="save-card glass-card fade-in-up"
            :style="{ animationDelay: `${i * 0.05}s` }"
          >
            <div class="save-cover">
              <span class="save-emoji">{{ save.status === 'completed' ? '🏆' : '📖' }}</span>
            </div>
            <div class="save-info">
              <div class="save-title-row">
                <span class="save-title">{{ save.script_title }}</span>
                <!-- CR-028: 显示角色名 -->
                <span v-if="save.character_name" class="save-character-badge">🎮 {{ save.character_name }}</span>
                <n-tag v-if="save.status === 'completed'" size="small" type="success" :bordered="false">{{ $t('saveManager.completed') }}</n-tag>
                <n-tag v-if="save.status === 'active'" size="small" type="info" :bordered="false">{{ $t('saveManager.inProgress') }}</n-tag>
              </div>
              <div class="save-route">{{ save.route_name }}</div>
              <div class="save-node">📍 {{ save.current_node_name }}</div>
              <div class="save-meta">
                <n-progress
                  type="line"
                  :percentage="save.progress_percent"
                  :show-indicator="false"
                  :height="6"
                  :color="save.status === 'completed' ? '#18A058' : '#A78BFA'"
                  :rail-color="'rgba(167, 139, 250, 0.1)'"
                  style="width: 120px"
                />
                <span class="save-percent">{{ save.progress_percent }}%</span>
                <span class="save-time">{{ formatTime(save.last_played_at) }}</span>
              </div>
              <div class="save-name-row" v-if="editingId === save.session_id">
                <n-input v-model:value="editName" size="small" :placeholder="$t('saveManager.renamePlaceholder')" @keyup.enter="confirmRename(save)" />
                <n-button size="tiny" type="primary" @click="confirmRename(save)">{{ $t('common.confirm') }}</n-button>
                <n-button size="tiny" @click="editingId = null">{{ $t('common.cancel') }}</n-button>
              </div>
            </div>
            <div class="save-actions">
              <n-button
                v-if="save.status === 'completed'"
                type="primary"
                size="small"
                @click="restartGame(save)"
              >🔄 {{ $t('saveManager.restart') }}</n-button>
              <n-button
                v-else
                type="primary"
                size="small"
                @click="continueGame(save)"
              >▶️ {{ $t('saveManager.continueGame') }}</n-button>

              <n-tooltip trigger="hover">
                <template #trigger>
                  <n-button quaternary size="small" @click="startRename(save)">✏️</n-button>
                </template>
                {{ $t('saveManager.rename') }}
              </n-tooltip>

              <n-tooltip trigger="hover">
                <template #trigger>
                  <n-button quaternary size="small" @click="toggleSnapshotTimeline(save)">🕐</n-button>
                </template>
                {{ $t('saveManager.snapshotTimeline') }}
              </n-tooltip>

              <n-button quaternary size="small" @click="confirmDelete(save)" class="delete-btn">🗑️</n-button>
            </div>

            <SnapshotTimeline
              v-if="expandedSessionId === save.session_id"
              :session-id="save.session_id"
              @fork="handleFork"
            />
          </div>
        </div>
      </n-spin>

      <n-modal v-model:show="showDeleteModal" preset="dialog" type="warning" :title="$t('saveManager.confirmDeleteTitle')" :positive-text="$t('saveManager.deleteBtn')" :negative-text="$t('common.cancel')" @positive-click="executeDelete">
        <p>{{ $t('saveManager.confirmDeleteDesc') }}</p>
        <p class="delete-target" v-if="deleteTarget">{{ deleteTarget.script_title }} — {{ deleteTarget.route_name }}</p>
      </n-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';
import type { SaveItem } from '@/api/game';
import SnapshotTimeline from '@/components/SnapshotTimeline.vue';

const { t } = useI18n();

useHead({
  title: 'Isekai Wanderer - Save Manager',
  meta: [{ name: 'description', content: () => t('saveManager.metaDesc') }],
});

const router = useRouter();
const message = useMessage();

const saves = ref<SaveItem[]>([]);
const loading = ref(false);
const editingId = ref<string | null>(null);
const editName = ref('');
const expandedSessionId = ref<string | null>(null);
const showDeleteModal = ref(false);
const deleteTarget = ref<SaveItem | null>(null);

// CR-028: 角色筛选
const selectedCharacterId = ref<string | null>(null);

// 从存档列表中提取角色标签（去重）
const characterTabs = computed(() => {
  const map = new Map<string, string>();
  for (const save of saves.value) {
    if (save.character_id && save.character_name) {
      map.set(save.character_id, save.character_name);
    }
  }
  const tabs: { id: string; name: string; filterValue: string | null }[] = [{ id: '__all__', name: '全部', filterValue: null }];
  for (const [id, name] of map) {
    tabs.push({ id, name, filterValue: id });
  }
  return tabs;
});

function selectCharacterFilter(filterValue: string | null) {
  selectedCharacterId.value = filterValue;
  loadSaves();
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return t('saveManager.justNow');
  if (hours < 24) return t('saveManager.hoursAgo', { n: hours });
  const days = Math.floor(hours / 24);
  if (days < 7) return t('saveManager.daysAgo', { n: days });
  return d.toLocaleDateString();
}

function continueGame(save: SaveItem) {
  router.push(`/game?session=${save.session_id}`);
}

function restartGame(save: SaveItem) {
  router.push(`/game?script=${save.script_id}&restart=true`);
}

function startRename(save: SaveItem) {
  editingId.value = save.session_id;
  editName.value = save.name || '';
}

async function confirmRename(save: SaveItem) {
  if (!editName.value.trim()) {
    message.warning(t('saveManager.nameEmpty'));
    return;
  }
  try {
    await gameApi.renameSave(save.session_id, editName.value.trim());
    save.name = editName.value.trim();
    editingId.value = null;
    message.success(t('saveManager.renameSuccess'));
  } catch (err) {
    message.error(`${t('saveManager.renameFailed')}: ${err instanceof Error ? err.message : t('common.error')}`);
  }
}

function confirmDelete(save: SaveItem) {
  deleteTarget.value = save;
  showDeleteModal.value = true;
}

async function executeDelete() {
  if (!deleteTarget.value) return;
  try {
    await gameApi.deleteSave(deleteTarget.value.session_id);
    saves.value = saves.value.filter(s => s.session_id !== deleteTarget.value!.session_id);
    message.success(t('saveManager.deleteSuccess'));
  } catch (err) {
    message.error(`${t('saveManager.deleteFailed')}: ${err instanceof Error ? err.message : t('common.error')}`);
  } finally {
    deleteTarget.value = null;
  }
}

function toggleSnapshotTimeline(save: SaveItem) {
  if (expandedSessionId.value === save.session_id) {
    expandedSessionId.value = null;
  } else {
    expandedSessionId.value = save.session_id;
  }
}

function handleFork(newSessionId: string) {
  // 从 saves 列表中找到对应的 script_id
  const save = saves.value.find(s => s.session_id === newSessionId);
  if (save) {
    router.push(`/game?script=${save.script_id}`);
  }
}

async function loadSaves() {
  loading.value = true;
  try {
    const resp = await gameApi.getSaves(selectedCharacterId.value || undefined);
    saves.value = resp.saves;
  } catch (err) {
    console.warn('加载存档失败:', err);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadSaves();
});
</script>

<style scoped>
.save-manager-page { max-width: 800px; margin: 0 auto; padding: 24px 16px 48px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { font-size: 24px; font-weight: 700; margin: 0; }
.subtitle { color: var(--text-muted); font-size: 14px; margin: 4px 0 0; }
.saves-list { display: flex; flex-direction: column; gap: 16px; }
.save-card { display: flex; flex-wrap: wrap; gap: 16px; padding: 16px; align-items: flex-start; }
.save-cover { width: 80px; height: 80px; border-radius: 12px; background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(192, 132, 252, 0.08)); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.save-emoji { font-size: 36px; }
.save-info { flex: 1; min-width: 0; }
.save-title-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.save-title { font-size: 16px; font-weight: 600; color: var(--text-main); }
.save-route { font-size: 13px; color: var(--text-muted); margin-bottom: 2px; }
.save-node { font-size: 12px; color: var(--text-subtle); margin-bottom: 8px; }
.save-meta { display: flex; align-items: center; gap: 8px; }
.save-percent { font-size: 12px; color: var(--text-muted); font-weight: 600; }
.save-time { font-size: 11px; color: var(--text-subtle); }
.save-name-row { display: flex; gap: 6px; align-items: center; margin-top: 8px; }
.save-actions { display: flex; gap: 4px; align-items: center; flex-shrink: 0; }
.delete-btn:hover { color: #E11D48 !important; }
.delete-target { font-weight: 600; color: var(--text-main); }

/* CR-028: 角色筛选标签栏 */
.character-filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 6px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.3);
}

.filter-tab.active {
  background: rgba(167, 139, 250, 0.2);
  border-color: #a78bfa;
  color: #fff;
  font-weight: 600;
}

/* CR-028: 存档卡片角色徽章 */
.save-character-badge {
  font-size: 12px;
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 6px;
  padding: 2px 8px;
  color: rgba(255, 255, 255, 0.9);
}
</style>

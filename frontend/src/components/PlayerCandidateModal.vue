<template>
  <n-modal
    v-model:show="visible"
    data-testid="player-candidate-modal"
    preset="card"
    :title="t('corvus.candidateSelection')"
    :mask-closable="false"
    :style="{ maxWidth: '800px', width: '90%' }"
    @after-leave="onClose"
  >
    <div class="candidate-modal-content">
      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <n-spin size="large" />
      </div>

      <!-- 剧本预设角色列表 -->
      <div v-else-if="scriptCharacters && scriptCharacters.length > 0" class="script-characters-section">
        <div class="section-label">{{ $t('playerCandidateModal.selectCharacter') }}</div>
        <div class="candidates-grid">
          <div
            v-for="character in scriptCharacters"
            :key="character.id"
            class="candidate-card"
            :class="{ selected: selectedScriptCharacter?.id === character.id }"
            data-testid="script-character-card"
            @click="selectScriptCharacter(character)"
          >
            <div class="candidate-avatar">
              <n-avatar
                :size="64"
                round
                :style="{ backgroundColor: getAvatarColor(character.name) }"
              >
                {{ character.name.charAt(0) }}
              </n-avatar>
            </div>
            <div class="candidate-info">
              <div class="candidate-name">{{ character.name }}</div>
              <div v-if="character.description" class="candidate-personality">
                {{ character.description }}
              </div>
              <div v-if="character.play_description" class="candidate-backstory">
                {{ character.play_description }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 无角色 -->
      <div v-else class="empty-state">
        <n-empty :description="$t('playerCandidateModal.noCharacters')" />
      </div>

      <!-- 底部操作栏 -->
      <div class="modal-footer">
        <div class="footer-left">
          <n-tag v-if="scriptCharacters && scriptCharacters.length === 0" type="info">
            {{ $t('playerCandidateModal.noCharacters') }}
          </n-tag>
        </div>
        <div class="footer-right">
          <n-button @click="handleClose">{{ t('common.cancel') }}</n-button>
          <n-button
            type="primary"
            @click="confirmSelection"
            :disabled="!selectedScriptCharacter"
            :loading="confirming"
            data-testid="select-candidate-confirm-btn"
          >
            {{ t('common.confirm') }}
          </n-button>
        </div>
      </div>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMessage } from 'naive-ui';
import { api } from '@/api/http';

const { t } = useI18n();
const message = useMessage();

const props = defineProps<{
  modelValue: boolean;
  scriptId: string;
  scriptCharacters?: any[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'selected', sessionId: string, initialScene?: any): void;
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

// 状态
const loading = ref(false);
const confirming = ref(false);
const selectedScriptCharacter = ref<any>(null);

const scriptCharactersData = ref<any[]>([]);

// CR-038 改造: 加载剧本预设角色 — GET /api/v1/game/scripts/{script_id}/characters
async function loadScriptCharacters() {
  loading.value = true;
  try {
    const response = await api.get<any>(`/game/scripts/${props.scriptId}/characters`);
    scriptCharactersData.value = (response.data ?? []);
  } catch (error) {
    console.error('Failed to load script characters:', error);
    message.error(t('playerCandidateModal.loadFailed'));
  } finally {
    loading.value = false;
  }
}

// 暴露给模板的剧本角色列表（优先用 props 传入，否则自行加载）
const scriptCharacters = computed(() => props.scriptCharacters?.length ? props.scriptCharacters : scriptCharactersData.value);

// 选择剧本预设角色
function selectScriptCharacter(character: any) {
  selectedScriptCharacter.value = character;
}

// 确认选择
// CR-038 改造: POST /game/session/select-player 传 character_id（不再创建 player_candidate）
async function confirmSelection() {
  if (!selectedScriptCharacter.value) return;

  confirming.value = true;
  try {
    const character = selectedScriptCharacter.value;

    // 1. 创建 Corvus 游戏会话
    const sessionResponse = await api.post<any>('/game/session/create', {
      script_id: props.scriptId,
    });
    const sessionId = (sessionResponse.data?.game_session_id ?? sessionResponse.game_session_id);

    if (!sessionId) {
      throw new Error('No game_session_id returned from server');
    }

    // 2. 选择玩家角色 — 传 character_id 而非 player_candidate_id
    const selectResponse = await api.post<any>('/game/session/select-player', {
      game_session_id: sessionId,
      character_id: character.id,
    });

    const selectData = (selectResponse.data ?? selectResponse);
    if ((selectData.status !== 'playing') && !selectData.initial_scene) {
      throw new Error('Unexpected select-player response format');
    }

    message.success(t('corvus.selectionConfirmed'));
    visible.value = false;
    emit('selected', sessionId, selectData.initial_scene);
  } catch (error: any) {
    const msg = (error as any)?.response?.data?.message ||
                (error as any)?.message ||
                t('playerCandidateModal.selectFailed');
    message.error(msg);
  } finally {
    confirming.value = false;
  }
}

// 关闭
function handleClose() {
  visible.value = false;
}

function onClose() {
  selectedScriptCharacter.value = null;
}

// 获取头像颜色
function getAvatarColor(name: string): string {
  const colors = [
    '#18a058',
    '#2080f0',
    '#f0a020',
    '#d03050',
    '#8a2be2',
    '#20b2aa',
  ];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
}

// 监听 visible 变化
watch(visible, (newValue) => {
  if (newValue) {
    if (!props.scriptCharacters?.length) {
      loadScriptCharacters();
    }
  }
});
</script>

<style scoped>
.candidate-modal-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.script-characters-section {
  margin-bottom: 8px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--n-text-color);
  margin-bottom: 12px;
}

.candidates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.candidate-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid var(--n-border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.candidate-card:hover {
  border-color: var(--n-primary-color);
  background: var(--n-action-color-hover);
}

.candidate-card.selected {
  border-color: var(--n-primary-color);
  background: var(--n-action-color-hover);
}

.candidate-avatar {
  flex-shrink: 0;
}

.candidate-info {
  flex: 1;
  min-width: 0;
}

.candidate-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.candidate-personality {
  font-size: 13px;
  color: var(--n-text-color-3);
  margin-bottom: 2px;
}

.candidate-backstory {
  font-size: 12px;
  color: var(--n-text-color-3);
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--n-border-color);
}

.footer-left, .footer-right {
  display: flex;
  gap: 8px;
}

.loading-state, .empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}
</style>

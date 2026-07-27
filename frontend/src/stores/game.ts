import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/api/http';

// Real API types (based on curl verification)
export interface Script {
  id: string;
  slug: string;
  title: string;
  description: string;
  genre: string;
  cover_image_url?: string;
}

export interface DialogueResponse {
  type: string; // "dialogue" or "ending"
  node_type?: string;
  node_id: string;
  text: string;
  emotion?: string;
  scene?: string;
  character_id?: string;
  character_title?: string;
  chapter?: string;
  convergence_point?: string;
  progress?: number;
  choices?: ChoiceResponse[];
  // ending fields
  ending_type?: 'good' | 'bad';
  ending_title?: string;
  ending_description?: string;
  monologue?: string;
}

export interface ChoiceResponse {
  id: string;
  text: string;
  affection_delta?: number;
}

export interface GameStartResponse {
  session_id: string;
  node_id: string;
  message: string;
}

export interface ChoiceSubmitResponse {
  session_id: string;
  is_ended: boolean;
  next_node_id: string;
  affection_change?: {
    character_id: string;
    delta: number;
    old_value: number;
    new_value: number;
    old_level: string;
    new_level: string;
    level_changed: boolean;
  };
  ending?: {
    ending_type: 'good' | 'bad';
    title: string;
    description: string;
  };
}

export interface GameSession {
  id: string;
  script_id: string;
  current_node_id: string;
  status: 'active' | 'completed' | 'abandoned';
}

export const useGameStore = defineStore('game', () => {
  const scripts = ref<Script[]>([]);
  const currentScript = ref<Script | null>(null);
  const currentSession = ref<GameSession | null>(null);
  const currentDialogue = ref<DialogueResponse | null>(null);
  const pendingChoices = ref<ChoiceResponse[]>([]);
  const choiceHistory = ref<{ choice_id: string; node_id: string }[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Character ID → display name mapping (populated from dialogue responses)
  const characterNameMap = ref<Map<string, string>>(new Map());

  const hasDialogue = computed(() => currentDialogue.value !== null);
  const hasChoices = computed(() => pendingChoices.value.length > 0);
  const isEnded = computed(() => currentDialogue.value?.type === 'ending');
  const isSaved = computed(() => currentSession.value !== null);

  async function loadScripts() {
    loading.value = true;
    try {
      const resp = await api.get<{ scripts: Script[] }>('/scripts');
      scripts.value = resp.scripts;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load scripts';
    } finally {
      loading.value = false;
    }
  }

  async function startGame(scriptId: string) {
    loading.value = true;
    try {
      const resp = await api.post<GameStartResponse>('/game/start', {
        script_id: scriptId,
      });
      currentSession.value = {
        id: resp.session_id,
        script_id: scriptId,
        current_node_id: resp.node_id,
        status: 'active',
      };
      currentScript.value = scripts.value.find((s) => s.id === scriptId) || null;

      // Fetch initial dialogue
      await fetchDialogue();
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to start game';
    } finally {
      loading.value = false;
    }
  }

  async function fetchDialogue() {
    if (!currentSession.value) return;
    loading.value = true;
    try {
      const resp = await api.get<(DialogueResponse & { character_name?: string }) | null>(`/game/${currentSession.value.id}/dialogue`);
      if (!resp) {
        error.value = '对话数据为空，请稍后重试';
        return;
      }
      currentDialogue.value = resp;
      if (resp.node_id) {
        currentSession.value.current_node_id = resp.node_id;
      }
      pendingChoices.value = resp.choices || [];
      
      // Cache character name if provided
      if (resp.character_id && (resp as any).character_name) {
        characterNameMap.value.set(resp.character_id, (resp as any).character_name);
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch dialogue';
    } finally {
      loading.value = false;
    }
  }

  async function submitChoice(choiceId: string) {
    if (!currentSession.value) return;
    loading.value = true;
    try {
      choiceHistory.value.push({
        choice_id: choiceId,
        node_id: currentSession.value.current_node_id,
      });

      const resp = await api.post<ChoiceSubmitResponse & { error?: string; message?: string; remaining_quota?: number }>(`/game/${currentSession.value.id}/choice`, {
        choice_id: choiceId,
      });

      // CR-016: Check for quota exhausted response
      if ((resp as any).error === 'quota_exhausted') {
        error.value = (resp as any).message || '对话额度已用完';
        return { quotaExhausted: true };
      }

      currentSession.value.current_node_id = resp.next_node_id;

      // 记录好感度变化，让 UI 可以响应
      const affectionDelta = resp.affection_change?.delta;

      // 先清选项，避免重复点击
      pendingChoices.value = [];

      if (resp.is_ended) {
        currentSession.value.status = 'completed';
        const endingDialogue = await api.get<(DialogueResponse & { character_name?: string }) | null>(`/game/${currentSession.value.id}/dialogue`);
        if (endingDialogue) {
          currentDialogue.value = endingDialogue;
        }
      } else {
        // 直接 fetch 新对话，不先清空 currentDialogue，避免闪烁
        await fetchDialogue();
      }

      return { affectionDelta };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to submit choice';
    } finally {
      loading.value = false;
    }
  }

  // 自定义输入推进剧情
  async function submitCustomInput(text: string) {
    if (!currentSession.value) return;
    loading.value = true;
    try {
      const resp = await api.post<DialogueResponse & { choices?: ChoiceResponse[]; is_custom?: boolean }>(
        `/game/${currentSession.value.id}/custom-input`,
        { text },
      );
      currentDialogue.value = resp;
      if (resp.node_id) {
        currentSession.value.current_node_id = resp.node_id;
      }
      if (resp.choices) {
        pendingChoices.value = resp.choices;
      }
      if ((resp as any).character_id) {
        // cache name if present
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送失败';
    } finally {
      loading.value = false;
    }
  }

  function reset() {
    currentScript.value = null;
    currentSession.value = null;
    currentDialogue.value = null;
    pendingChoices.value = [];
    choiceHistory.value = [];
    error.value = null;
  }

  const currentNode = computed(() => {
    if (!currentDialogue.value || !currentSession.value) return null;
    return {
      id: currentSession.value.current_node_id,
      ...currentDialogue.value,
    };
  });

  return {
    scripts,
    currentScript,
    currentSession,
    currentDialogue,
    currentNode,
    pendingChoices,
    choiceHistory,
    loading,
    error,
    characterNameMap,
    hasDialogue,
    hasChoices,
    isEnded,
    isSaved,
    loadScripts,
    startGame,
    fetchDialogue,
    submitChoice,
    submitCustomInput,
    reset,
  };
});

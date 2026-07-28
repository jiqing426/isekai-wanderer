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
  // 从 localStorage 恢复会话信息
  const savedSession = localStorage.getItem('game_session');
  const savedScript = localStorage.getItem('game_script');
  
  const scripts = ref<Script[]>([]);
  const currentScript = ref<Script | null>(savedScript ? JSON.parse(savedScript) : null);
  const currentSession = ref<GameSession | null>(savedSession ? JSON.parse(savedSession) : null);
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
      // 检查是否有已保存的会话
      const savedSession = localStorage.getItem('game_session');
      if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.script_id === scriptId && session.status === 'active') {
          // 恢复已有会话
          currentSession.value = session;
          currentScript.value = scripts.value.find((s) => s.id === scriptId) || null;
          await fetchDialogue();
          return;
        }
      }
      
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
      
      // 保存到 localStorage
      localStorage.setItem('game_session', JSON.stringify(currentSession.value));
      if (currentScript.value) {
        localStorage.setItem('game_script', JSON.stringify(currentScript.value));
      }

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

      const resp = await api.post<ChoiceSubmitResponse & { error?: string; message?: string; remaining_quota?: number; new_achievements?: any[] }>(`/game/${currentSession.value.id}/choice`, {
        choice_id: choiceId,
      });

      // CR-016: Check for quota exhausted response
      if ((resp as any).error === 'quota_exhausted') {
        error.value = (resp as any).message || '对话额度已用完';
        return { quotaExhausted: true };
      }

      currentSession.value.current_node_id = resp.next_node_id;
      
      // 更新 localStorage
      localStorage.setItem('game_session', JSON.stringify(currentSession.value));

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

      return { affectionDelta, new_achievements: (resp as any).new_achievements || [] };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to submit choice';
      return { error: true };
    } finally {
      loading.value = false;
    }
  }

  // 自定义输入推进剧情
  async function submitCustomInput(text: string) {
    if (!currentSession.value) return;
    loading.value = true;
    try {
      const resp = await api.post<DialogueResponse & { choices?: ChoiceResponse[]; is_custom?: boolean; new_achievements?: any[] }>(
        `/game/${currentSession.value.id}/custom-input`,
        { text },
      );
      
      // 更新对话内容（后端返回 text 字段）
      if (resp.text) {
        currentDialogue.value = {
          ...currentDialogue.value!,
          text: resp.text,
          emotion: resp.emotion || currentDialogue.value?.emotion,
          character_id: resp.character_id || currentDialogue.value?.character_id,
        };
      }
      
      // 更新选择按钮（后端返回 choices 数组）
      if (resp.choices && resp.choices.length > 0) {
        pendingChoices.value = resp.choices;
      }
      
      if (resp.character_id) {
        // cache name if present
      }
      return { new_achievements: (resp as any).new_achievements || [] };
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送失败';
      return { error: true };
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
    
    // 清除 localStorage
    localStorage.removeItem('game_session');
    localStorage.removeItem('game_script');
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

import { defineStore } from 'pinia';
import { ref, reactive, computed } from 'vue';
import { api } from '@/api/http';
import { gameApi } from '@/api/game';

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
  character_id?: string;  // CR-028: Store character_id for session comparison
  route_id?: string;      // CR-028: Store route_id for session comparison
  affection_value?: number; // CR-031: Persist affection value for session restore
  engine_type?: 'legacy' | 'corvus';  // CR-037: Engine type for feature flag
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
  // CR-035: 使用 reactive Record 替代 ref<Map>，确保 Vue 响应式追踪
  const characterNameMap = reactive<Record<string, string>>({});

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

  async function startGame(scriptId: string, routeId?: string, characterId?: string) {
    loading.value = true;
    try {
      // 检查是否有已保存的会话
      const savedSession = localStorage.getItem('game_session');
      if (savedSession) {
        const session = JSON.parse(savedSession);
        if (session.script_id === scriptId && session.status === 'active') {
          // CR-028: 检查 character_id 或 route_id 是否变化，如果变化则需要调用后端创建新会话
          const savedCharacterId = session.character_id || null;
          const savedRouteId = session.route_id || null;
          const newCharacterId = characterId || null;
          const newRouteId = routeId || null;
          const characterChanged = newCharacterId !== savedCharacterId;
          const routeChanged = newRouteId !== savedRouteId;
          
          if (!characterChanged && !routeChanged) {
            // 恢复已有会话（角色和路线都没变）
            currentSession.value = session;
            currentScript.value = scripts.value.find((s) => s.id === scriptId) || null;
            try {
              await fetchDialogue();
              return;
            } catch (err) {
              // 恢复失败，清除旧会话，重新开始
              console.warn('恢复会话失败，将重新开始:', err);
              localStorage.removeItem('game_session');
              localStorage.removeItem('game_script');
              currentSession.value = null;
              currentScript.value = null;
            }
          }
          // 如果角色或路线变化了，继续往下走，调用后端 API 创建新会话
          console.log(`CR-028: Session changed - character: ${savedCharacterId} -> ${characterId}, route: ${savedRouteId} -> ${routeId}`);
        }
      }
      
      const resp = await api.post<GameStartResponse>('/game/start', {
        script_id: scriptId,
        route_id: routeId,
        character_id: characterId || undefined,  // CR-028: 可选角色 ID
      });
      currentSession.value = {
        id: resp.session_id,
        script_id: scriptId,
        current_node_id: resp.node_id,
        status: 'active',
        character_id: characterId,  // CR-028: Store for session comparison
        route_id: routeId,          // CR-028: Store for session comparison
      };
      currentScript.value = scripts.value.find((s) => s.id === scriptId) || null;
      
      // 保存到 localStorage
      localStorage.setItem('game_session', JSON.stringify(currentSession.value));
      if (currentScript.value) {
        localStorage.setItem('game_script', JSON.stringify(currentScript.value));
      }

      // Fetch initial dialogue
      try {
        await fetchDialogue();
      } catch (err) {
        // 如果获取对话失败（如 429 限流），清除会话状态，让调用方知道失败了
        console.error('Failed to fetch initial dialogue:', err);
        currentSession.value = null;
        currentScript.value = null;
        localStorage.removeItem('game_session');
        localStorage.removeItem('game_script');
        throw err;
      }
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
      const resp = await api.get<(DialogueResponse & { character_name?: string; cg_unlock?: any; node_type?: string }) | null>(`/game/${currentSession.value.id}/dialogue`);
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
        characterNameMap[resp.character_id] = (resp as any).character_name;
      }
      
      // CR-036: preset 节点异步调用 AI 补充对话
      if (resp.node_type === 'preset' && resp.character_id) {
        fetchAIDialogue();
      }
      
      // NOTE: 每日任务「对话达人」只在自由对话/角色聊天时触发，游戏节点推进不再更新
      
      // 检测 CG 解锁，触发解锁动效
      if ((resp as any).cg_unlock) {
        const { useUnlockModal } = await import('@/composables/useUnlockModal');
        const unlockModal = useUnlockModal();
        unlockModal.show({
          type: 'cg',
          title: (resp as any).cg_unlock.title || '特殊CG',
          description: (resp as any).cg_unlock.description || '你解锁了一张特殊CG！',
          image: (resp as any).cg_unlock.image || '',
          rarity: (resp as any).cg_unlock.rarity || 'SR',
        });
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch dialogue';
    } finally {
      loading.value = false;
    }
  }

  // CR-036: 异步获取 AI 增强对话
  async function fetchAIDialogue() {
    if (!currentSession.value) return;
    try {
      const resp = await api.get<{ text: string; emotion: string; timeout?: boolean }>(`/game/${currentSession.value.id}/ai-dialogue`);
      // AI 生成成功且非空时，替换预设文本
      if (resp.text && currentDialogue.value) {
        currentDialogue.value = {
          ...currentDialogue.value,
          text: resp.text,
          emotion: resp.emotion || currentDialogue.value.emotion,
        };
      }
    } catch (err) {
      // AI 失败时保持预设文本不变
      console.warn('AI dialogue generation failed, keeping preset text');
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

      // CR-037: Corvus SSE 流式分支
      const isCorvus = currentSession.value.engine_type === 'corvus';
      if (isCorvus) {
        const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
        const token = match ? decodeURIComponent(match[2]) : null;
        if (!token) { error.value = '未登录'; loading.value = false; return { error: true }; }

        const response = await fetch(`/api/v1/game/${currentSession.value.id}/choice`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ choice_id: choiceId }),
        });

        if (!response.ok) { error.value = `HTTP ${response.status}`; loading.value = false; return { error: true }; }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';
        let affectionDelta = 0;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'text') {
                  fullText += data.content || '';
                  currentDialogue.value = { ...currentDialogue.value!, text: fullText, type: 'dialogue' };
                } else if (data.type === 'done') {
                  currentDialogue.value = {
                    ...currentDialogue.value!,
                    text: data.text || fullText,
                    character_id: data.character_id || currentDialogue.value?.character_id || '',
                    node_id: data.node_id || '',
                    type: 'dialogue',
                  };
                  if (data.node_id) {
                    currentSession.value.current_node_id = data.node_id;
                    localStorage.setItem('game_session', JSON.stringify(currentSession.value));
                  }
                  pendingChoices.value = [];
                } else if (data.type === 'gm_update') {
                  if (data.affinity_delta) affectionDelta = data.affinity_delta;
                } else if (data.type === 'error') {
                  error.value = data.message || 'Unknown error';
                }
              } catch (e) { console.error('SSE parse error:', e); }
            }
          }
        }
        loading.value = false;
        return { affectionDelta, new_achievements: [], chapter_transition: null };
      }

      const resp = await api.post<ChoiceSubmitResponse & { error?: string; message?: string; remaining_quota?: number; new_achievements?: any[]; chapter_transition?: any }>(`/game/${currentSession.value.id}/choice`, {
        choice_id: choiceId,
      });

      // CR-016: Check for quota exhausted response
      if ((resp as any).error === 'quota_exhausted') {
        error.value = (resp as any).message || '对话额度已用完';
        return { quotaExhausted: true };
      }

      currentSession.value.current_node_id = resp.next_node_id;
      
      // CR-031: 持久化好感度值，防止刷新后丢失
      if (resp.affection_change?.new_value !== undefined) {
        currentSession.value.affection_value = resp.affection_change.new_value;
      }
      
      // 更新 localStorage
      localStorage.setItem('game_session', JSON.stringify(currentSession.value));

      // CR-031 BUG-031-002: 调用 auto-save API 持久化游戏进度
      try {
        await api.post('/game/auto-save', {
          session_id: currentSession.value.id,
          node_id: currentSession.value.current_node_id,
          choice_id: choiceId,
        });
      } catch (saveErr) {
        // auto-save 失败不应阻塞游戏流程，只记录警告
        console.warn('CR-031: auto-save failed:', saveErr);
      }

      // 记录好感度变化，让 UI 可以响应
      const affectionDelta = resp.affection_change?.delta;

      // CR-035 T-035-FE-002: 不清空 pendingChoices，保留旧选项直到新对话返回
      // 旧选项会在 fetchDialogue() 完成后被新选项替换

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

      return { 
        affectionDelta, 
        new_achievements: (resp as any).new_achievements || [],
        chapter_transition: (resp as any).chapter_transition || null,
      };
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

    // CR-037: Corvus SSE 流式分支
    const isCorvus = currentSession.value.engine_type === 'corvus';
    if (isCorvus) {
      try {
        const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
        const token = match ? decodeURIComponent(match[2]) : null;
        if (!token) { error.value = '未登录'; loading.value = false; return { error: true }; }

        const response = await fetch(`/api/v1/game/${currentSession.value.id}/custom-input`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ text }),
        });

        if (!response.ok) { error.value = `HTTP ${response.status}`; loading.value = false; return { error: true }; }

        const reader = response.body!.getReader();
        

        const decoder = new TextDecoder();
        let buffer = '';
        let fullText = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.type === 'text') {
                  fullText += data.content || '';
                  currentDialogue.value = { ...currentDialogue.value!, text: fullText, type: 'dialogue' };
                } else if (data.type === 'done') {
                  currentDialogue.value = {
                    ...currentDialogue.value!,
                    text: data.text || fullText,
                    character_id: data.character_id || currentDialogue.value?.character_id || '',
                    node_id: data.node_id || '',
                    type: 'dialogue',
                  };
                  if (data.node_id) {
                    currentSession.value.current_node_id = data.node_id;
                    localStorage.setItem('game_session', JSON.stringify(currentSession.value));
                  }
                  pendingChoices.value = [];
                } else if (data.type === 'gm_update') {
                  // 好感度/道具/标记更新 - 异步处理
                } else if (data.type === 'error') {
                  error.value = data.message || 'Unknown error';
                }
              } catch (e) { console.error('SSE parse error:', e); }
            }
          }
        }
        loading.value = false;
        return { new_achievements: [], chapter_transition: null };
      } catch (err) {
        error.value = err instanceof Error ? err.message : '发送失败';
        loading.value = false;
        return { error: true };
      }
    }

    // 旧引擎路径
    try {
      const resp = await api.post<DialogueResponse & { choices?: ChoiceResponse[]; is_custom?: boolean; new_achievements?: any[]; node_id?: string; chapter_transition?: any }>(
        `/game/${currentSession.value.id}/custom-input`,
        { text },
      );
      
      // 更新当前节点 ID（后端已推进到新节点）
      if (resp.node_id) {
        currentSession.value.current_node_id = resp.node_id;
        localStorage.setItem('game_session', JSON.stringify(currentSession.value));
      }
      
      // 更新对话内容（后端返回 text 字段）
      if (resp.text) {
        currentDialogue.value = {
          ...currentDialogue.value!,
          text: resp.text,
          emotion: resp.emotion || currentDialogue.value?.emotion,
          character_id: resp.character_id || currentDialogue.value?.character_id || '',
          node_id: resp.node_id || currentDialogue.value?.node_id || '',
        };
      }
      
      // 更新选择按钮（始终更新，即使为空也要清空旧选项）
      pendingChoices.value = resp.choices || [];
      
      if (resp.character_id) {
        // cache name if present
      }
      return { 
        new_achievements: (resp as any).new_achievements || [],
        chapter_transition: resp.chapter_transition || null,
      };
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

  // 从个人中心「继续游戏」恢复会话
  async function resumeSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    
    try {
      // 从后端获取完整的 session 数据
      const sessionData = await api.get<{
        session_id: string;
        script_id: string;
        character_id: string | null;
        character_name: string | null;
        route_id: string | null;
        status: string;
        current_node_id: string | null;
      }>(`/game/${sessionId}`);
      
      // 设置当前会话（包含完整的角色和剧本信息）
      currentSession.value = {
        id: sessionData.session_id,
        script_id: sessionData.script_id || '',
        current_node_id: sessionData.current_node_id || '',
        status: (sessionData.status as 'active' | 'completed' | 'abandoned') || 'active',
        character_id: sessionData.character_id || undefined,
        route_id: sessionData.route_id || undefined,
      };
      
      // 保存到 localStorage
      localStorage.setItem('game_session', JSON.stringify(currentSession.value));
      
      // 加载剧本信息
      if (currentSession.value.script_id) {
        await loadScripts();
        currentScript.value = scripts.value.find((s) => s.id === currentSession.value!.script_id) || null;
        if (currentScript.value) {
          localStorage.setItem('game_script', JSON.stringify(currentScript.value));
        }
      }
      
      // 拉取当前对话
      await fetchDialogue();
    } catch (err) {
      console.error('resumeSession failed:', err);
      error.value = err instanceof Error ? err.message : '恢复会话失败';
      currentSession.value = null;
      localStorage.removeItem('game_session');
    } finally {
      loading.value = false;
    }
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
    fetchAIDialogue,
    submitChoice,
    submitCustomInput,
    reset,
    resumeSession,
  };
});

import { defineStore } from 'pinia';
import { ref, reactive, computed } from 'vue';
import { api } from '@/api/http';
import { useSSEStream } from '@/composables/useSSEStream';

// CR-042: Helper — check if a fetch response is SSE (text/event-stream)
function isSSEResponse(response: Response): boolean {
  const ct = response.headers.get('Content-Type') || '';
  return ct.includes('text/event-stream');
}

// CR-042: Helper — consume an SSE response body and dispatch to callbacks
// This is used for Legacy submit_choice where we pre-fetch and need to consume
// the existing response body (rather than letting useSSEStream do its own fetch)
interface SSEBodyCallbacks {
  onText: (content: string) => void;
  onDone?: (data: any) => void;
  onError?: (error: string) => void;
  onEmotion?: (data: any) => void;
  onAffectionUpdate?: (data: any) => void;
  onGmUpdate?: (data: any) => void;
}

async function consumeSSEBody(response: Response, callbacks: SSEBodyCallbacks): Promise<void> {
  if (!response.body) {
    callbacks.onError?.('Response body is null');
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith(':') || !trimmed.startsWith('data: ')) continue;

        try {
          const data = JSON.parse(trimmed.slice(6));
          switch (data.type) {
            case 'text':
              callbacks.onText(data.content || '');
              break;
            case 'done':
              callbacks.onDone?.(data);
              break;
            case 'error':
              callbacks.onError?.(data.message || 'Unknown error');
              break;
            case 'emotion':
              callbacks.onEmotion?.(data);
              break;
            case 'affection_update':
              callbacks.onAffectionUpdate?.(data);
              break;
            case 'gm_update':
              callbacks.onGmUpdate?.(data);
              break;
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      }
    }

    // Process remaining buffer
    if (buffer.trim()) {
      const trimmed = buffer.trim();
      if (trimmed.startsWith('data: ')) {
        try {
          const data = JSON.parse(trimmed.slice(6));
          switch (data.type) {
            case 'text': callbacks.onText(data.content || ''); break;
            case 'done': callbacks.onDone?.(data); break;
            case 'error': callbacks.onError?.(data.message || 'Unknown error'); break;
            case 'emotion': callbacks.onEmotion?.(data); break;
            case 'affection_update': callbacks.onAffectionUpdate?.(data); break;
            case 'gm_update': callbacks.onGmUpdate?.(data); break;
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      }
    }
  } finally {
    try { reader.releaseLock(); } catch {}
  }
}

// Real API types (based on curl verification)
export interface Script {
  id: string;
  slug: string;
  title: string;
  description: string;
  genre: string;
  cover_image_url?: string;
  engine_type: 'legacy' | 'corvus';  // CR-038 C1/C2: engine_type 必填（无 ?）
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
  engine_type: 'legacy' | 'corvus';  // CR-038 C2: engine_type 必填（去掉 ?）
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

  // CR-039 D2: 从 gm_update 事件提取的角色名（Corvus done 事件 characterName=null 时的 fallback）
  const currentCharacterName = ref<string>('');

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
        }
      }
      
      // CR-038: 获取剧本信息以判断引擎类型
      const script = scripts.value.find((s) => s.id === scriptId);
      const isCorvus = script?.engine_type === 'corvus';
      
      if (isCorvus) {
        // Corvus 流程：POST /game/session/create → 选角 → POST /game/session/select-player
        // Backend returns { code: 0, data: { game_session_id, status, engine_type } }
        const resp = await api.post<any>('/game/session/create', {
          script_id: scriptId,
        });
        
        const sessionId = (resp as any)?.data?.game_session_id || (resp as any)?.game_session_id;
        if (!sessionId) {
          throw new Error('No game_session_id returned from session/create');
        }
        
        currentSession.value = {
          id: sessionId,
          script_id: scriptId,
          current_node_id: '',
          status: 'active',
          character_id: characterId,
          route_id: routeId,
          engine_type: 'corvus',  // CR-038: 写入 engine_type
        };
        currentScript.value = script || null;
        
        // 保存到 localStorage
        localStorage.setItem('game_session', JSON.stringify(currentSession.value));
        if (currentScript.value) {
          localStorage.setItem('game_script', JSON.stringify(currentScript.value));
        }
        
        // 返回会话信息，让调用方（如 ScriptDetailView）处理选角流程
        return;
      }
      
      // Legacy 流程（保留不激活）
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
        engine_type: 'legacy',      // CR-038: 写入 engine_type
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

      const isCorvus = currentSession.value.engine_type === 'corvus';

      // CR-042: Unified SSE path using useSSEStream composable for both Corvus and Legacy branches
      // Corvus: always SSE; Legacy: SSE for transition/ai_dialog nodes, JSON for preset/choice nodes
      const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
      const token = match ? decodeURIComponent(match[2]) : null;
      if (!token) { error.value = '未登录'; loading.value = false; return { error: true }; }

      // For Legacy path: first try fetch, check if response is SSE or JSON
      if (!isCorvus) {
        // CR-042: Legacy submit_choice — backend returns SSE for transition/ai_dialog, JSON for preset/choice
        const response = await fetch(`/api/v1/game/${currentSession.value.id}/choice`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ choice_id: choiceId }),
        });

        if (!response.ok) {
          // Try to read error message
          let errorMsg = `HTTP ${response.status}`;
          try {
            const errBody = await response.json();
            errorMsg = errBody.message || errorMsg;
            if (errBody.error === 'quota_exhausted') {
              error.value = errBody.message || '对话额度已用完';
              return { quotaExhausted: true };
            }
          } catch {}
          error.value = errorMsg;
          return { error: true };
        }

        // Check if response is SSE (transition/ai_dialog node) or JSON (preset/choice node)
        if (isSSEResponse(response)) {
          // CR-042 AC-005: SSE path — done event carries node_id + choices, no fetchDialogue() needed
          // Use consumeSSEBody to parse the existing pre-fetched response body
          await consumeSSEBody(response, {
            onText: (content) => {
              if (!currentDialogue.value) {
                currentDialogue.value = { text: content, type: 'dialogue', node_id: '' };
              } else {
                currentDialogue.value.text = (currentDialogue.value.text || '') + content;
              }
            },
            onDone: (data) => {
              if (currentDialogue.value) {
                if (data.text) currentDialogue.value.text = data.text;
                currentDialogue.value.character_id = data.character_id || currentDialogue.value.character_id || '';
                currentDialogue.value.node_id = data.node_id || '';
                currentDialogue.value.type = 'dialogue';
              } else {
                currentDialogue.value = {
                  text: data.text || '',
                  character_id: data.character_id || '',
                  node_id: data.node_id || '',
                  type: 'dialogue',
                };
              }
              if (data.node_id) {
                currentSession.value!.current_node_id = data.node_id;
                localStorage.setItem('game_session', JSON.stringify(currentSession.value));
              }
              // CR-042 AC-005: done event carries choices — no fetchDialogue() needed
              pendingChoices.value = data.choices || [];
              if (data.affection_change?.new_value !== undefined) {
                currentSession.value!.affection_value = data.affection_change.new_value;
              }
            },
            onError: (msg) => { error.value = msg; },
            onEmotion: (data) => {
              if (currentDialogue.value && data.emotion) {
                currentDialogue.value.emotion = data.emotion;
              }
            },
            onAffectionUpdate: (data) => {
              if (data.value !== undefined) {
                currentSession.value!.affection_value = data.value;
              }
            },
          });
          // CR-031: auto-save after SSE
          try {
            await api.post('/game/auto-save', {
              session_id: currentSession.value.id,
              node_id: currentSession.value.current_node_id,
              choice_id: choiceId,
            });
          } catch (saveErr) {
            console.warn('CR-031: auto-save failed:', saveErr);
          }
          // Refresh affection from status
          try {
            const statusResp = await api.get(`/game/${currentSession.value.id}/status`);
            if ((statusResp as any)?.affection_value !== undefined) {
              currentSession.value.affection_value = (statusResp as any).affection_value;
            }
          } catch (e) {
            console.warn('Failed to refresh status after SSE:', e);
          }
          loading.value = false;
          return { affectionDelta: 0, new_achievements: [], chapter_transition: null };
        } else {
          // JSON response (preset/choice node) — process as before
          const resp = await response.json() as ChoiceSubmitResponse & { error?: string; message?: string; remaining_quota?: number; new_achievements?: any[]; chapter_transition?: any };

          if ((resp as any).error === 'quota_exhausted') {
            error.value = (resp as any).message || '对话额度已用完';
            return { quotaExhausted: true };
          }

          currentSession.value.current_node_id = resp.next_node_id;
          if (resp.affection_change?.new_value !== undefined) {
            currentSession.value.affection_value = resp.affection_change.new_value;
          }
          localStorage.setItem('game_session', JSON.stringify(currentSession.value));

          // CR-031: auto-save
          try {
            await api.post('/game/auto-save', {
              session_id: currentSession.value.id,
              node_id: currentSession.value.current_node_id,
              choice_id: choiceId,
            });
          } catch (saveErr) {
            console.warn('CR-031: auto-save failed:', saveErr);
          }

          const affectionDelta = resp.affection_change?.delta;

          if (resp.is_ended) {
            currentSession.value.status = 'completed';
            const endingDialogue = await api.get<(DialogueResponse & { character_name?: string }) | null>(`/game/${currentSession.value.id}/dialogue`);
            if (endingDialogue) {
              currentDialogue.value = endingDialogue;
            }
          } else {
            await fetchDialogue();
          }

          return {
            affectionDelta,
            new_achievements: (resp as any).new_achievements || [],
            chapter_transition: (resp as any).chapter_transition || null,
          };
        }
      }

      // CR-042 AC-022: Corvus path — migrated to useSSEStream composable
      let fullText = '';
      let affectionDelta = 0;

      const { start } = useSSEStream(
        {
          url: `/api/v1/game/${currentSession.value.id}/choice`,
          method: 'POST',
          body: { choice_id: choiceId },
        },
        {
          onText: (content) => {
            fullText += content;
            if (!currentDialogue.value) {
              currentDialogue.value = { text: fullText, type: 'dialogue', node_id: '' };
            } else {
              currentDialogue.value.text = fullText;
            }
          },
          onDone: (data) => {
            if (currentDialogue.value) {
              currentDialogue.value.text = data.text || fullText;
              currentDialogue.value.character_id = data.character_id || currentDialogue.value.character_id || '';
              currentDialogue.value.node_id = data.node_id || '';
              currentDialogue.value.type = 'dialogue';
            } else {
              currentDialogue.value = {
                text: data.text || fullText,
                character_id: data.character_id || '',
                node_id: data.node_id || '',
                type: 'dialogue',
              };
            }
            if (data.node_id) {
              currentSession.value!.current_node_id = data.node_id;
              localStorage.setItem('game_session', JSON.stringify(currentSession.value));
            }
            // D7: done event clears pendingChoices
            pendingChoices.value = [];
          },
          onError: (msg) => {
            error.value = msg;
          },
          onEmotion: (data) => {
            if (currentDialogue.value && data.emotion) {
              currentDialogue.value.emotion = data.emotion;
            }
          },
          onAffectionUpdate: (data) => {
            if (data.value !== undefined) {
              currentSession.value!.affection_value = data.value;
            }
          },
          onGmUpdate: (data) => {
            // CR-038 T-038-FE-004: gm_update UI update logic
            // CR-039 T-039-FE-001: player_options/choices assignment
            const newChoices = data.player_options || data.choices;
            if (newChoices && newChoices.length > 0) {
              pendingChoices.value = newChoices;
            }
            // CR-039 D2: extract character name
            if (data.new_characters && data.new_characters.length > 0) {
              currentCharacterName.value = data.new_characters[0];
            }
            // CR-039 D3: affection — handle affinity_current (absolute value)
            if (data.affinity_current !== undefined && data.affinity_current !== null) {
              currentSession.value!.affection_value = data.affinity_current;
            }
            if (data.affinity_delta || data.affinity_deltas) {
              const delta = data.affinity_delta || (data.affinity_deltas?.[0]?.delta);
              if (delta) affectionDelta = delta;
            }
          },
        }
      );

      await start();

      // CR-039 D3: Refresh affection after SSE
      try {
        const statusResp = await api.get(`/game/${currentSession.value.id}/status`);
        if ((statusResp as any)?.affection_value !== undefined) {
          currentSession.value.affection_value = (statusResp as any).affection_value;
        }
      } catch (e) {
        console.warn('Failed to refresh status after SSE:', e);
      }
      loading.value = false;
      return { affectionDelta, new_achievements: [], chapter_transition: null };
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to submit choice';
      return { error: true };
    } finally {
      loading.value = false;
    }
  }

  // 自定义输入推进剧情
  async function submitCustomInput(text: string): Promise<{ affectionDelta?: number; new_achievements?: any[]; chapter_transition?: any; error?: boolean; quotaExhausted?: boolean }> {
    if (!currentSession.value) return {};
    loading.value = true;

    // CR-042 AC-010: Both Corvus and Legacy paths now use useSSEStream composable
    // Legacy path: BE now returns SSE for custom-input (DEV-001)
    // Corvus path: already SSE, migrated to composable (AC-022)
    const match = document.cookie.match(/(^| )isekai_access_token=([^;]+)/);
    const token = match ? decodeURIComponent(match[2]) : null;
    if (!token) { error.value = '未登录'; loading.value = false; return { error: true }; }

    try {
      let fullText = '';
      let affectionDelta = 0;

      const { start } = useSSEStream(
        {
          url: `/api/v1/game/${currentSession.value.id}/custom-input`,
          method: 'POST',
          body: { text },
        },
        {
          onText: (content) => {
            fullText += content;
            if (!currentDialogue.value) {
              currentDialogue.value = { text: fullText, type: 'dialogue', node_id: '' };
            } else {
              currentDialogue.value.text = fullText;
            }
          },
          onDone: (data) => {
            if (currentDialogue.value) {
              currentDialogue.value.text = data.text || fullText;
              currentDialogue.value.character_id = data.character_id || currentDialogue.value.character_id || '';
              currentDialogue.value.node_id = data.node_id || '';
              currentDialogue.value.type = 'dialogue';
            } else {
              currentDialogue.value = {
                text: data.text || fullText,
                character_id: data.character_id || '',
                node_id: data.node_id || '',
                type: 'dialogue',
              };
            }
            if (data.node_id) {
              currentSession.value!.current_node_id = data.node_id;
              localStorage.setItem('game_session', JSON.stringify(currentSession.value));
            }
            // D7: done event clears pendingChoices
            pendingChoices.value = [];
            // Update affection if provided
            if (data.affection_change?.new_value !== undefined) {
              currentSession.value!.affection_value = data.affection_change.new_value;
            }
          },
          onError: (msg) => {
            error.value = msg;
          },
          onEmotion: (data) => {
            if (currentDialogue.value && data.emotion) {
              currentDialogue.value.emotion = data.emotion;
            }
          },
          onAffectionUpdate: (data) => {
            if (data.value !== undefined) {
              currentSession.value!.affection_value = data.value;
            }
          },
          onGmUpdate: (data) => {
            // Corvus path: gm_update event handling
            const newChoices = data.player_options || data.choices;
            if (newChoices && newChoices.length > 0) {
              pendingChoices.value = newChoices;
            }
            if (data.new_characters && data.new_characters.length > 0) {
              currentCharacterName.value = data.new_characters[0];
            }
            if (data.affinity_current !== undefined && data.affinity_current !== null) {
              currentSession.value!.affection_value = data.affinity_current;
            }
            if (data.affinity_delta || data.affinity_deltas) {
              const delta = data.affinity_delta || (data.affinity_deltas?.[0]?.delta);
              if (delta) affectionDelta = delta;
            }
          },
        }
      );

      await start();

      // CR-039 D3: Refresh affection after SSE
      try {
        const statusResp = await api.get(`/game/${currentSession.value.id}/status`);
        if ((statusResp as any)?.affection_value !== undefined) {
          currentSession.value.affection_value = (statusResp as any).affection_value;
        }
      } catch (e) {
        console.warn('Failed to refresh status after SSE:', e);
      }
      loading.value = false;
      return { affectionDelta, new_achievements: [], chapter_transition: null };
    } catch (err) {
      error.value = err instanceof Error ? err.message : '发送失败';
      loading.value = false;
      return { error: true };
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
      // CR-038 BUG-038-005: GET /game/{sessionId} 现在返回 engine_type 字段
      const sessionData = await api.get<{
        session_id: string;
        script_id: string;
        character_id: string | null;
        character_name: string | null;
        route_id: string | null;
        status: string;
        current_node_id: string | null;
        engine_type?: string;
      }>(`/game/${sessionId}`);
      
      const engineType = (sessionData as any).engine_type || 'legacy';
      
      // 设置当前会话（包含完整的角色和剧本信息）
      currentSession.value = {
        id: sessionData.session_id,
        script_id: sessionData.script_id || '',
        current_node_id: sessionData.current_node_id || '',
        status: (sessionData.status as 'active' | 'completed' | 'abandoned') || 'active',
        character_id: sessionData.character_id || undefined,
        route_id: sessionData.route_id || undefined,
        engine_type: engineType as 'legacy' | 'corvus',  // CR-038: 从 API 响应读取
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
      // CR-038: Corvus session in 'playing' status can fetch dialogue
      if (engineType === 'corvus' && sessionData.status === 'playing') {
        await fetchDialogue();
        // CR-039 T-039-FE-002: 如果 fetchDialogue 未返回对话，尝试从 sessionStorage 获取 initial_scene
        if (!currentDialogue.value) {
          const sceneKey = `corvus_initial_scene_${sessionId}`;
          const sceneJson = sessionStorage.getItem(sceneKey);
          if (sceneJson) {
            try {
              const scene = JSON.parse(sceneJson);
              if (scene.opening_text) {
                currentDialogue.value = {
                  text: scene.opening_text,
                  type: 'dialogue',
                  node_id: '',
                  character_id: sessionData.character_id || undefined,
                };
              }
              // 清理 sessionStorage
              sessionStorage.removeItem(sceneKey);
            } catch (e) {
              console.warn('Failed to parse initial_scene from sessionStorage:', e);
            }
          }
        }
      } else if (engineType === 'legacy') {
        await fetchDialogue();
      }
      // For Corvus sessions in 'waiting_select_player' status, skip dialogue fetch
      // (the session hasn't started yet, no dialogue available)
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
    currentCharacterName,
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

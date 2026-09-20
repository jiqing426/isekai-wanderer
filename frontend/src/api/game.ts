import { api } from './http';

export interface RouteMapNode {
  node_id: string;
  scene_index: number;
  label: string;
  emotion?: string;
  choices: { choice_id: string; label: string; next_node_id: string }[];
}

export interface RouteMapResponse {
  session_id: string;
  script_id: string;
  current_node_id: string;
  nodes: RouteMapNode[];
}

export interface Script {
  id: string;
  title: string;
  description: string;
  genre: string;
  cover_url?: string;
  cover_image_url?: string;
  is_premium?: boolean;
  tag_list?: string[];
  slug?: string;
  route_count?: number;
  tags?: string[];
  play_count_7d?: number;
}

export interface FreeChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface FreeChatTopic {
  id: string;
  label: string;
  emoji: string;
}

// ── CR3-005/006: Discover API types ──

export interface DiscoverCard {
  id: string;
  slug?: string;
  title: string;
  description: string;
  genre: string;
  cover_image_url?: string;
  route_count: number;
  tags: string[];
  created_at?: string;
  play_count_7d?: number;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
  script_count: number;
}

export interface Tag {
  id: string;
  name: string;
  group: string;
  script_count: number;
}

// ── CR3-009/010/011: Character API types ──

export interface CharacterCard {
  id: string;
  script_id: string;
  name: string;
  description: string;
  dialogue_style: string;
  affection_value?: number;
  affection_level?: string;
}

// ── CR3-022: Achievement types ──

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  rarity?: string;
  isUnlocked: boolean;
  isClaimed: boolean;
  unlockedAt: string | null;
  claimedAt: string | null;
  condition?: {
    type: string;
    value?: number;
    target?: number;
    current?: number;
  };
  progress?: {
    current: number;
    target: number;
    percentage?: number;
  };
  reward?: {
    type: string;
    amount: number;
  };
}

// ── CR3-025: Daily Task types ──

export interface DailyTask {
  id: string;
  name: string;
  description: string;
  progress: number;
  target: number;
  completed: boolean;
  claimed: boolean;
  reward: number;
}

// ── CR3-026: Activity types ──

export interface ActivityMilestone {
  threshold: number;
  reward: number;
  claimed: boolean;
}

export interface ActivityProgress {
  current_score: number;
  max_score: number;
  milestones?: ActivityMilestone[];
}

// ── CR3-012: Recap types ──
export interface RecapEvent {
  id: string;
  type: 'dialogue' | 'choice' | 'scene_change' | 'ending';
  text: string;
  scene?: string;
  choice_text?: string;
  affection_delta?: number;
  timestamp?: string;
}

// ── CR3-013: Memory types ──
export interface Memory {
  id: string;
  character_id: string;
  character_name: string;
  content: string;
  importance: number;
  emotion?: string;
  scene_context?: string;
  tags?: string[];
  created_at: string;
}

export interface CharacterSprite {
  id: string;
  emotion: string;
  image_url: string;
}

// ── CR-005: Voice sample types ──
export interface VoiceSample {
  id: string;
  label: string;        // 情绪标签：打招呼/日常对话/告白/生气
  icon: string;         // emoji 图标
  audio_url: string | null;  // 预生成的音频 URL（null 时降级到 Web Speech）
  text: string;         // 试听文案（降级时使用）
  voice: string;        // CosyVoice 声音角色（降级时使用）
  speed: number;        // 语速（降级时使用）
}

export interface AffectionDetail {
  value: number;
  level: string;
  level_label: string;
  next_level?: {
    level: string;
    level_label: string;
    threshold: number;
    remaining: number;
  };
}

export interface CharacterDetail {
  id: string;
  script_id: string;
  script_title?: string;
  name: string;
  description: string;
  dialogue_style: string;
  personality: Record<string, any> | string;
  likes: string[] | { items: string[] };
  dislikes: string[];
  greeting: string;
  sprites: CharacterSprite[];
  affection: AffectionDetail;
  age?: number;
  height?: number;
  birthday?: string;
  created_at?: string;
  avatar_url?: string;
}

export interface GiftItem {
  id: string;
  name: string;
  cost: number;
  price?: number; // 后端可能返回 price
  affection_bonus: number;
  description: string;
  icon_url?: string;
}

// ── CR3-015/016/017: Save & Snapshot & Ending types ──

export interface SaveItem {
  session_id: string;
  script_id: string;
  script_title: string;
  route_name: string;
  current_node_name: string;
  progress_percent: number;
  status: 'active' | 'completed' | 'paused';
  name?: string;
  last_played_at: string;
  created_at: string;
  ending_name?: string;
  // CR-028: 角色信息
  character_id?: string | null;
  character_name?: string;
}

export interface SnapshotItem {
  id: string;
  session_id: string;
  node_id: string;
  node_name: string;
  is_auto: boolean;
  is_pinned: boolean;
  label?: string;
  created_at: string;
  expires_at?: string;
}

export interface EndingProgressResponse {
  script_id: string;
  script_title: string;
  total_endings: number;
  unlocked_count: number;
  unlocked_endings: Array<{
    ending_id: string;
    ending_name: string;
    ending_type: string;
    unlocked_at: string;
  }>;
  locked_endings: Array<{
    ending_id: string;
    hint: string;
  }>;
}

// ── CR3-019: Shard types ──

export interface ShardTransaction {
  id: string;
  type: 'earn' | 'spend';
  amount: number;
  source: string;
  description: string;
  created_at: string;
}

export const gameApi = {
  // AC-045: Route map
  getRouteMap(sessionId: string): Promise<RouteMapResponse> {
    return api.get(`/game/${sessionId}/route-map`);
  },

  // Scripts listing
  getScripts(): Promise<{ scripts: Script[] }> {
    return api.get('/scripts');
  },

  getScript(scriptId: string): Promise<Script> {
    return api.get(`/scripts/${scriptId}`);
  },

  // AC-058: Free chat
  getFreeChatTopics(sessionId: string): Promise<{ topics: FreeChatTopic[] }> {
    return api.get(`/game/${sessionId}/free-chat/topics`);
  },

  sendFreeChatMessage(sessionId: string, message: string, topicId?: string): Promise<{ reply: string }> {
    return api.post(`/game/${sessionId}/free-chat`, { message, topic_id: topicId });
  },

  // CR-042 AC-016: Free chat SSE streaming endpoint
  /**
   * Send a free chat message via SSE streaming endpoint.
   * Returns the URL and body for useSSEStream composable — does NOT call fetch directly.
   * The caller (FreeChatView) uses useSSEStream to handle the SSE response.
   */
  getFreeChatStreamConfig(sessionId: string, message: string) {
    return {
      url: `/api/v1/game/${sessionId}/free-chat/stream`,
      method: 'POST' as const,
      body: { message },
    };
  },

  getFreeChatHistory(sessionId: string, page?: number): Promise<{ messages: FreeChatMessage[] }> {
    const params = page ? `?page=${page}` : '';
    return api.get(`/game/${sessionId}/free-chat/history${params}`);
  },

  // Discord config (AC-055)
  getDiscordConfig(): Promise<{ invite_url: string; guild_id?: string; enabled: boolean }> {
    return api.get('/discord/config');
  },

  // ── CR3-005/006: Discover API ──

  getRecommendations(limit?: number): Promise<{ recommendations: DiscoverCard[]; total: number }> {
    return api.get('/discover/recommendations' + (limit ? `?limit=${limit}` : ''));
  },

  getCategories(): Promise<{ categories: Category[] }> {
    return api.get('/discover/categories');
  },

  getTags(): Promise<{ tags: Tag[] }> {
    return api.get('/discover/tags');
  },

  getDiscoverScripts(params?: {
    category?: string;
    tags?: string;
    sort_by?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ scripts: DiscoverCard[]; total: number; offset: number; limit: number }> {
    const query = new URLSearchParams();
    if (params?.category) query.set('category', params.category);
    if (params?.tags) query.set('tags', params.tags);
    if (params?.sort_by) query.set('sort_by', params.sort_by);
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return api.get('/discover/scripts' + (qs ? `?${qs}` : ''));
  },

  getTrending(limit?: number): Promise<{ trending: DiscoverCard[]; total: number }> {
    return api.get('/discover/trending' + (limit ? `?limit=${limit}` : ''));
  },

  // ── CR3-009/010/011: Character API ──

  getCharacters(params?: {
    script_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ characters: CharacterCard[]; total: number; offset: number; limit: number }> {
    const query = new URLSearchParams();
    if (params?.script_id) query.set('script_id', params.script_id);
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return api.get('/characters' + (qs ? `?${qs}` : ''));
  },

  getCharacterDetail(characterId: string): Promise<CharacterDetail> {
    return api.get(`/characters/${characterId}`);
  },

  getCharacterAffection(characterId: string, limit?: number): Promise<{
    character_id: string;
    character_name: string;
    value: number;
    level: string;
    level_label: string;
    next_level?: {
      level: string;
      level_label: string;
      threshold: number;
      remaining: number;
    };
    history: Array<{
      change_value: number;
      reason: string;
      created_at: string;
    }>;
  }> {
    return api.get(`/characters/${characterId}/affection` + (limit ? `?limit=${limit}` : ''));
  },

  getGiftCatalog(): Promise<{ gifts: GiftItem[] }> {
    return api.get('/characters/gifts/catalog');
  },

  getCharacterGiftHistory(characterId: string): Promise<{
    gifts: Array<{
      id: string;
      character_id: string;
      character_name: string;
      gift_id: string;
      gift_name: string;
      quantity: number;
      affection_delta: number;
      created_at: string;
    }>;
    total: number;
  }> {
    // CR-032: 后端返回 history 字段，前端映射为 gifts
    return api.get<any>(`/characters/${characterId}/gift-history`).then((resp: any) => ({
      gifts: resp.history || resp.gifts || [],
      total: (resp.history || resp.gifts || []).length,
    }));
  },

  sendGift(characterId: string, giftId: string): Promise<{
    status: string;
    new_affection_value: number;
    affection_gained: number;
    remaining_shards: number;
  }> {
    return api.post(`/gifts/send`, { character_id: characterId, gift_id: giftId });
  },

  // ── CR-025 S017: Daily Tasks API ──

  getDailyTasks(): Promise<any> {
    return api.get('/daily-tasks');
  },

  updateDailyTaskProgress(taskType: string, increment = 1): Promise<any> {
    return api.post('/daily-tasks/progress', { task_type: taskType, increment });
  },

  claimDailyTask(taskType: string): Promise<any> {
    return api.post('/daily-tasks/claim', { task_type: taskType });
  },

  claimAllDailyTasks(): Promise<any> {
    return api.post('/daily-tasks/claim-all');
  },

  // ── CR3-015/016/017: Save & Snapshot & Ending API ──

  getSaves(characterId?: string): Promise<{ saves: SaveItem[] }> {
    const query = characterId ? `?character_id=${characterId}` : '';
    return api.get(`/saves${query}`);
  },

  renameSave(sessionId: string, name: string): Promise<{ status: string }> {
    return api.patch(`/saves/${sessionId}`, { name });
  },

  deleteSave(sessionId: string): Promise<{ status: string }> {
    return api.delete(`/saves/${sessionId}`);
  },

  getSnapshots(sessionId: string): Promise<{ snapshots: SnapshotItem[] }> {
    return api.get(`/saves/${sessionId}/snapshots`);
  },

  createSnapshot(sessionId: string, label?: string): Promise<SnapshotItem> {
    return api.post(`/saves/${sessionId}/snapshots`, { label });
  },

  pinSnapshot(snapshotId: string, pinned: boolean): Promise<{ status: string }> {
    return api.patch(`/snapshots/${snapshotId}`, { is_pinned: pinned });
  },

  forkFromSnapshot(snapshotId: string): Promise<{ new_session_id: string }> {
    return api.post(`/snapshots/${snapshotId}/fork`);
  },

  getEndingProgress(scriptId: string): Promise<EndingProgressResponse> {
    return api.get(`/scripts/${scriptId}/ending-progress`);
  },

  // ── CR3-019: Shard Center API ──

  getShardBalance(): Promise<{ balance: number; lifetime_earned: number; lifetime_spent: number }> {
    return api.get('/shards/balance');
  },

  getShardTransactions(params?: {
    type?: string;
    days?: number;
    limit?: number;
    offset?: number;
  }): Promise<{ transactions: ShardTransaction[]; total: number }> {
    const query = new URLSearchParams();
    if (params?.type) query.set('type', params.type);
    if (params?.days) query.set('days', String(params.days));
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset) query.set('offset', String(params.offset));
    const qs = query.toString();
    return api.get('/shards/transactions' + (qs ? `?${qs}` : ''));
  },

  // ── CR3-022: Achievement Wall API ──

  getAchievements(): Promise<{ achievements: Achievement[] }> {
    return api.get('/achievements');
  },

  claimAchievement(achievementId: string): Promise<{ success: boolean }> {
    return api.post('/achievements/claim', { achievement_id: achievementId });
  },

  // ── CR3-026: Activity Chest API ──

  getActivityProgress(): Promise<ActivityProgress> {
    return api.get('/activity/progress');
  },

  claimActivityChest(threshold: number): Promise<{ success: boolean }> {
    return api.post('/activity/claim', { threshold });
  },

  // ── CR3-012: Recap API ──
  getRecap(sessionId: string): Promise<{ events: RecapEvent[] }> {
    return api.get(`/game/${sessionId}/recap`);
  },

  // ── CR3-013: Memory API ──
  getMemories(characterId: string): Promise<{ memories: Memory[] }> {
    return api.get(`/characters/${characterId}/memories`);
  },

  // ── Mock Data Removal: New APIs ──
  
  getPopularScripts(limit: number = 6): Promise<{ scripts: DiscoverCard[] }> {
    return api.get(`/scripts?sort=popular&limit=${limit}`);
  },

  getScriptCharacters(scriptId: string): Promise<{ characters: CharacterCard[] }> {
    return api.get(`/scripts/${scriptId}/characters`);
  },

  getScriptRoutes(scriptId: string): Promise<{ routes: any[] }> {
    return api.get(`/scripts/${scriptId}/routes`);
  },

  getScriptEndings(scriptId: string): Promise<{ endings: any[] }> {
    return api.get(`/scripts/${scriptId}/endings`);
  },

  getScriptCGPreview(scriptId: string): Promise<{ cgs: any[] }> {
    return api.get(`/scripts/${scriptId}/cg-preview`);
  },

  getUserProgress(scriptId: string): Promise<{ progress: any }> {
    return api.get(`/user/progress/${scriptId}`);
  },

  getCharacterPersonality(characterId: string): Promise<{ personality: any }> {
    return api.get(`/characters/${characterId}/personality`);
  },

  getCharacterVoices(characterId: string): Promise<{ voices: VoiceSample[] }> {
    return api.get(`/characters/${characterId}/voices`);
  },

  getUserSubscription(): Promise<any> {
    return api.get('/user/subscription');
  },

  sendChatDemo(message: string): Promise<{ reply: string }> {
    return api.post('/chat/demo', { message });
  },

  // ── CR-009: Game Progress & History APIs ──

  getGameProgress(sessionId: string): Promise<{
    session_id: string;
    script_id: string;
    current_node_id: string;
    total_nodes: number;
    explored_nodes: number;
    completion_rate: number;
    choice_count: number;
    dialogue_count: number;
  }> {
    return api.get(`/game/${sessionId}/progress`);
  },

  // FE-O2: 获取游戏状态（角色名称、好感度）
  getGameStatus(sessionId: string): Promise<{
    session_id: string;
    script_name: string;
    character_name: string;
    character_id: string;
    affection_value: number;
    affinity_level: string;  // BE returns affinity_level, not affection_level
    status?: string;
    current_node_id?: string | null;
    current_chapter?: string;
    total_chapters?: number;
    chapter_number?: number | null;
    chapter_type?: string | null;
    chapter_title?: string | null;
  }> {
    return api.get(`/game/${sessionId}/status`);
  },

  getGameHistory(sessionId: string, params?: { page?: number; page_size?: number }): Promise<{
    history: Array<{
      id: string;
      type: 'dialogue' | 'choice';
      character_id?: string;
      character_name?: string;
      content?: string;
      emotion?: string;
      choice_text?: string;
      created_at: string;
    }>;
    total: number;
    page: number;
    page_size: number;
  }> {
    const query = new URLSearchParams();
    if (params?.page) query.set('page', String(params.page));
    if (params?.page_size) query.set('page_size', String(params.page_size));
    const qs = query.toString();
    return api.get(`/game/${sessionId}/history${qs ? `?${qs}` : ''}`);
  },

  sendGameGift(sessionId: string, characterId: string, giftId: string, quantity: number = 1): Promise<{
    status: 'ok';
    character_id: string;
    gift_id: string;
    affection_delta: number;
    new_affection: number;
    message: string;
  }> {
    return api.post(`/game/${sessionId}/gift`, {
      character_id: characterId,
      gift_id: giftId,
      quantity,
    });
  },

  getGiftHistory(sessionId: string): Promise<{
    gifts: Array<{
      id: string;
      character_id: string;
      character_name: string;
      gift_id: string;
      gift_name: string;
      quantity: number;
      affection_delta: number;
      created_at: string;
    }>;
    total: number;
  }> {
    return api.get(`/game/${sessionId}/gift-history`);
  },

  // ── CR-019: Dialogue History Storage API ──

  storeDialogue(sessionId: string, data: {
    role: 'user' | 'assistant';
    content: string;
    character_id?: string;
    character_name?: string;
    emotion?: string;
  }): Promise<{
    id: string;
    session_id: string;
    role: string;
    content: string;
    character_id?: string;
    character_name?: string;
    emotion?: string;
    created_at: string;
  }> {
    return api.post(`/game/${sessionId}/dialogue`, data);
  },

  getDialogues(sessionId: string, params?: { limit?: number; offset?: number }): Promise<{
    dialogues: Array<{
      id: string;
      session_id: string;
      role: string;
      content: string;
      character_id?: string;
      character_name?: string;
      emotion?: string;
      created_at: string;
    }>;
    total: number;
    limit: number;
    offset: number;
  }> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', String(params.limit));
    if (params?.offset !== undefined) query.set('offset', String(params.offset));
    const qs = query.toString();
    return api.get(`/game/${sessionId}/dialogues${qs ? `?${qs}` : ''}`);
  },
};

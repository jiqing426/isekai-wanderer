<template>
  <div class="page-bg">
    <div class="game-page">
      <!-- Loading state -->
      <div v-if="phase === 'loading'" class="phase-loading fade-in-up">
        <div class="loading-hero">
          <div class="loading-emoji">📖</div>
          <h2 class="gradient-text">{{ $t('common.loading') }}</h2>
          <n-spin size="large" />
        </div>
      </div>

      <!-- Phase: Game Playing -->
      <div v-if="phase === 'playing'" class="phase-game">
        <!-- 游戏标题栏 -->
        <div class="game-header">
          <n-button @click="router.back()" class="back-btn" :title="t('gameViewExtra.back')">
            {{ $t('gameViewExtra.back') }}
          </n-button>
          <ChapterProgress
            :chapter="currentChapter"
            :chapter-number="gameStatus?.chapter_number"
            :chapter-title="gameStatus?.chapter_title"
            :convergence-point="currentConvergencePoint"
            :progress="chapterProgress"
          />
          <div class="header-actions">
            <!-- CR-016: 额度展示 - 移到header-actions中 -->
            <div 
              class="quota-inline" 
              v-if="subscriptionStore.dialogueQuota"
              :title="subscriptionStore.isSubscriber 
                ? t('gameViewExtra.subscriberUnlimitedQuota') 
                : t('gameViewExtra.dialogueQuotaRemaining', { remaining: subscriptionStore.dialogueQuota.remaining, total: subscriptionStore.dialogueQuota.base_quota })"
            >
              <span class="quota-icon">💬</span>
              <span class="quota-value" :class="{ 'is-subscriber': subscriptionStore.isSubscriber }">
                {{ subscriptionStore.isSubscriber ? '∞' : `${subscriptionStore.dialogueQuota.remaining}/${subscriptionStore.dialogueQuota.base_quota}` }}
              </span>
              <span v-if="!subscriptionStore.isSubscriber && subscriptionStore.dialogueQuota.remaining <= 2" class="quota-reset-hint" :title="quotaResetHint">
                {{ $t('gameViewExtra.quotaResetHint') }}
              </span>
              <n-button v-if="!subscriptionStore.isSubscriber && subscriptionStore.dialogueQuota.remaining <= 2" size="tiny" type="primary" @click="router.push('/subscribe')">
                {{ $t('gameViewExtra.supplement') }}
              </n-button>
            </div>
            <n-button @click="handleManualSave" class="icon-btn" :title="t('gameViewExtra.save')">
              {{ $t('gameViewExtra.save') }}
            </n-button>
            <n-button @click="openHistory" class="icon-btn" :title="t('gameViewExtra.history')">
              {{ $t('gameViewExtra.history') }}
            </n-button>
          </div>
        </div>

        <div class="game-layout">
          <!-- 左侧栏 280px -->
          <aside class="left-sidebar">
            <CharacterInfo
              :character-id="gameStatus?.character_id || game.currentDialogue?.character_id"
              :character-name="gameStatus?.character_name || characterDisplayName"
              :character-title="characterTitle"
              :character-age="characterDetail?.age"
              :character-birthday="characterDetail?.birthday"
              :character-likes="parsedCharacterLikes"
              :avatar-url="playerCharacterAvatar"
            />
            <AffectionDisplay
              :character-id="gameStatus?.character_id || game.currentDialogue?.character_id"
              :value="gameStatus?.affection_value ?? game.currentSession?.affection_value ?? currentAffection"
            />
            <n-button @click="openGiftModal" class="action-btn">{{ $t('gameViewExtra.sendGift') }}</n-button>
            <n-button @click="goToFreeChat" class="action-btn">{{ $t('gameViewExtra.freeChat') }}</n-button>
            <n-button @click="viewGiftHistory" class="action-btn">{{ $t('gameViewExtra.giftHistory') }}</n-button>
          </aside>

          <!-- 右侧栏 flex:1 -->
          <main class="right-story-stage" :style="{ backgroundImage: `url(${currentBackground})` }">
            <StoryPanel
              :text="game.currentDialogue?.text || t('gameViewExtra.storyUnfolding')"
              :character-name="characterDisplayName"
              :emotion="game.currentDialogue?.emotion"
              :speed="typewriterSpeed"
              @complete="onStoryComplete"
            />
            <ChoicePanel
              ref="choicePanelRef"
              v-if="game.hasChoices"
              :choices="choiceOptions"
              :loading="game.loading"
              @select="handleChoice"
            />
            <!-- 好感度动效 -->
            <transition name="fade">
              <div v-if="showAffectionAnimation" class="affection-animation" :class="affectionDelta > 0 ? 'positive' : 'negative'">
                {{ affectionDelta > 0 ? '+' : '' }}{{ affectionDelta }} {{ $t('gameViewExtra.affectionPoint') }}
              </div>
            </transition>
            <!-- 剧本对话输入框 -->
            <FreeChatInput
              v-if="!game.isEnded"
              :character-id="game.currentDialogue?.character_id"
              :character-name="characterDisplayName"
              :default-expanded="game.currentSession?.engine_type === 'corvus'"
              @send="handleFreeChat"
              @close="showFreeChat = false"
            />
            <!-- Ending detected -->
            <div v-if="game.isEnded" class="ending-detected fade-in-up">
              <div class="ending-card glass-card" :class="game.currentDialogue?.ending_type">
                <div class="ending-badge" :class="game.currentDialogue?.ending_type">
                  {{ game.currentDialogue?.ending_type === 'good' ? ('✦ ' + $t('ending.good')) : ('✧ ' + $t('ending.bad')) }}
                </div>
                <h2 class="ending-title">{{ game.currentDialogue?.ending_title || $t('game.ending') }}</h2>
                <p class="ending-desc">{{ game.currentDialogue?.ending_description || game.currentDialogue?.text || '' }}</p>
                <div class="ending-actions">
                  <n-button size="large" secondary @click="router.push('/discover')">{{ $t('gameViewExtra.backToHome') }}</n-button>
                  <n-button size="large" secondary @click="handleRestartCurrentChapter">{{ $t('gameViewExtra.restart') }}</n-button>
                  <n-button 
                    v-if="(game.currentDialogue as any)?.has_next_chapter" 
                    size="large" 
                    type="primary" 
                    @click="handleNextChapter"
                  >
                    ▶️ {{ $t('gameViewExtra.enterNextChapter') }}{{ (game.currentDialogue as any)?.next_chapter_title || $t('gameViewExtra.nextChapter') }}
                  </n-button>
                </div>
              </div>
            </div>
            <n-alert v-if="game.error" type="error" :title="game.error" closable @close="game.error = null" style="margin-top: 16px" />
          </main>
        </div>
      </div>

      <NotificationPrompt />

      <!-- 历史对话抽屉 -->
      <HistoryDrawer
        :visible="showHistory"
        :session-id="game.currentSession?.id"
        @close="closeHistory"
      />

      <!-- FE-O5: 送礼弹窗 -->
      <GiftModal
        v-model="showGiftModal"
        :target-name="characterDisplayName"
        :target-id="game.currentDialogue?.character_id || ''"
        :session-id="game.currentSession?.id"
        @gift-sent="onGiftSent"
      />

      <!-- FE-O5: 送礼记录弹窗 -->
      <n-modal
        v-model:show="showGiftHistoryModal"
        preset="card"
        :title="t('gameViewExtra.giftHistoryTitle')"
        :style="{ width: '450px' }"
      >
        <div v-if="giftHistoryLoading" style="text-align: center; padding: 20px;">
          <n-spin size="medium" />
        </div>
        <div v-else-if="giftHistory.length === 0" style="text-align: center; padding: 20px;">
          <n-empty :description="$t('gameViewExtra.noGiftHistory')" />
        </div>
        <div v-else class="gift-history-list">
          <div v-for="record in giftHistory" :key="record.id" class="gift-history-item">
            <span class="gift-history-icon">🎁</span>
            <div class="gift-history-info">
              <span class="gift-history-name">{{ record.gift_name }}</span>
              <span class="gift-history-to">{{ $t('gameViewExtra.sentTo') }} {{ record.character_name }}</span>
            </div>
            <span class="gift-history-affection">+{{ record.affection_delta }}</span>
          </div>
        </div>
      </n-modal>

      <div v-if="phase === 'error'" class="phase-error fade-in-up">
        <n-result status="error" :title="$t('common.error')" :description="errorMsg">
          <template #footer>
            <n-space>
              <n-button @click="router.push('/discover')">{{ $t('common.back') }}</n-button>
              <n-button type="primary" @click="initGame">{{ $t('common.submit') }}</n-button>
            </n-space>
          </template>
        </n-result>
      </div>

      <!-- CR-016: Paywall 统一管理 -->
      <PaywallManager ref="paywallManagerRef" />

      <!-- 成就解锁动画 -->
      <div v-if="showAchievementUnlock" class="achievement-unlock-overlay" @click.self="closeAchievementUnlock">
        <AchievementUnlockCard
          :title="currentUnlockAchievement?.title || ''"
          :description="currentUnlockAchievement?.description"
          :reward="currentUnlockAchievement?.reward"
          @confirm="closeAchievementUnlock"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NAlert, NButton, NResult, NSpace, NSpin, NModal, NEmpty, useMessage } from 'naive-ui';
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useGameStore } from '@/stores/game';
import { useAffectionStore } from '@/stores/affection';
// import { chatApi } from '@/api/chat';
import { saveApi } from '@/api/saves';
import { gameApi } from '@/api/game';
import GiftModal from '@/components/GiftModal.vue';

// New components
import StoryPanel from '@/components/StoryPanel.vue';
import CharacterInfo from '@/components/CharacterInfo.vue';
import AffectionDisplay from '@/components/AffectionDisplay.vue';
import ChapterProgress from '@/components/ChapterProgress.vue';
import FreeChatInput from '@/components/FreeChatInput.vue';
import ChoicePanel from '@/components/ChoicePanel.vue';
import NotificationPrompt from '@/components/NotificationPrompt.vue';
import HistoryDrawer from '@/components/HistoryDrawer.vue';
import PaywallManager from '@/components/paywall/PaywallManager.vue';
import AchievementUnlockCard from '@/components/unlock/AchievementUnlockCard.vue';
import { useSubscriptionStore } from '@/stores/subscription';
import type { PaywallTrigger } from '@/types/subscription';

const { t } = useI18n();
const message = useMessage();
const route = useRoute();
const router = useRouter();
const game = useGameStore();
const affectionStore = useAffectionStore();
const subscriptionStore = useSubscriptionStore();

const paywallManagerRef = ref<InstanceType<typeof PaywallManager> | null>(null);
const choicePanelRef = ref<InstanceType<typeof ChoicePanel> | null>(null);

const phase = ref<'loading' | 'playing' | 'error'>('loading');
const errorMsg = ref('');
const showFreeChat = ref(false);
const typewriterSpeed = ref(1);

// 好感度动效
const showAffectionAnimation = ref(false);
const affectionDelta = ref(0);

// 成就解锁动画
const showAchievementUnlock = ref(false);
const currentUnlockAchievement = ref<any>(null);
let achievementAutoCloseTimer: ReturnType<typeof setTimeout> | null = null;

function closeAchievementUnlock() {
  showAchievementUnlock.value = false;
  currentUnlockAchievement.value = null;
  if (achievementAutoCloseTimer) {
    clearTimeout(achievementAutoCloseTimer);
    achievementAutoCloseTimer = null;
  }
}

function showAchievementUnlockAnimation(achievement: any) {
  currentUnlockAchievement.value = achievement;
  showAchievementUnlock.value = true;
  
  // 3秒后自动关闭
  if (achievementAutoCloseTimer) {
    clearTimeout(achievementAutoCloseTimer);
  }
  achievementAutoCloseTimer = setTimeout(() => {
    closeAchievementUnlock();
  }, 3000);
}

// 历史对话
const showHistory = ref(false);
const dialogueHistory = ref<Array<{
  type: 'dialogue' | 'choice' | 'system';
  characterName?: string;
  text: string;
  timestamp: number;
  affectionDelta?: number;
}>>([]);

// 游戏进度
const gameProgress = ref<{
  completion_rate: number;
  choice_count: number;
  dialogue_count: number;
  current_chapter?: string;
  total_chapters?: number;
  explored_nodes?: number;
  total_nodes?: number;
} | null>(null);

// 游戏状态（角色信息）
const gameStatus = ref<{
  script_name: string;
  character_name: string;
  character_id: string;
  affection_value: number;
  affection_level: string;
  chapter_number?: number | null;
  chapter_type?: string | null;
  chapter_title?: string | null;
} | null>(null);

// 角色详细数据
const characterDetail = ref<{
  age?: number;
  height?: number;
  birthday?: string;
  likes?: string[] | { items: string[] };
  personality?: string | Record<string, any>;
  avatar_url?: string;
  sprites?: Array<{ emotion: string; image_url: string }>;
} | null>(null);

// CR-028: 玩家扮演角色头像（供 CharacterInfo 组件复用）
// CR-031 BUG-031-003: 只使用 avatar_url，不走 sprites fallback（新角色可能无头像或 sprites 为占位图）
const playerCharacterAvatar = computed(() => {
  return characterDetail.value?.avatar_url || '';
});

// 解析角色喜好（兼容数组和对象格式）
const parsedCharacterLikes = computed(() => {
  const likes = characterDetail.value?.likes;
  if (!likes) return [];
  if (Array.isArray(likes)) return likes;
  if (typeof likes === 'object' && 'items' in likes) return likes.items || [];
  return [];
});

// 加载游戏进度 - FE-O1
async function loadGameProgress() {
  if (!game.currentSession) return;
  try {
    const progress = await gameApi.getGameProgress(game.currentSession.id);
    gameProgress.value = {
      completion_rate: progress.completion_rate || 0,
      choice_count: progress.choice_count || 0,
      dialogue_count: progress.dialogue_count || 0,
      current_chapter: (progress as any).current_chapter,  // CR-020: 保存章节信息
    };
  } catch (err) {
    console.error('Failed to load game progress:', err);
  }
}

// 加载游戏状态 - FE-O2
async function loadGameStatus() {
  if (!game.currentSession) return;
  try {
    const status = await gameApi.getGameStatus(game.currentSession.id);
    gameStatus.value = {
      script_name: status.script_name || '',
      character_name: status.character_name || '',
      character_id: status.character_id || '',
      // Fix: use ?? to preserve 0 (valid value), and read affinity_level from BE
      affection_value: status.affection_value ?? 0,
      affection_level: status.affinity_level ?? t('game.acquaintance'),
      chapter_number: status.chapter_number ?? null,
      chapter_type: status.chapter_type ?? null,
      chapter_title: status.chapter_title ?? null,
    };
    // 加载角色详细数据
    if (status.character_id) {
      try {
        const detail = await gameApi.getCharacterDetail(status.character_id);
        characterDetail.value = {
          age: detail.age,
          height: detail.height,
          birthday: detail.birthday,
          likes: detail.likes || [],
          personality: detail.personality,
          avatar_url: detail.avatar_url || '',
          sprites: detail.sprites || [],
        };
      } catch (e) {
        console.warn('Failed to load character detail:', e);
      }
    }
  } catch (err) {
    console.error('Failed to load game status:', err);
  }
}

// 加载历史对话 - FE-O3
async function loadHistoryFromApi() {
  if (!game.currentSession) return;
  try {
    const response = await gameApi.getGameHistory(game.currentSession.id);
    if (response && response.history && response.history.length > 0) {
      dialogueHistory.value = response.history.map((item: any) => ({
        type: item.type || 'dialogue',
        characterName: item.character_name,
        text: item.content || item.text || '',
        timestamp: new Date(item.created_at).getTime(),
        affectionDelta: item.affection_delta
      }));
    }
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

// CR-016: 生命周期阶段标签（保留但暂时未使用，避免 TS 报错）
// @ts-ignore
function lifecycleStageLabel(stage: string): string {
  const map: Record<string, string> = {
    honeymoon: t('gameViewExtra.lifecycleHoneymoon'),
    growth: t('gameViewExtra.lifecycleGrowth'),
    regular: t('gameViewExtra.lifecycleRegular'),
    returnee: t('gameViewExtra.lifecycleReturnee')
  };
  return map[stage] || stage;
}

// CR-016: 触发 Paywall（供对话接口返回 paywall 字段时调用）
function triggerPaywall(trigger: PaywallTrigger) {
  if (paywallManagerRef.value) {
    paywallManagerRef.value.triggerPaywall(trigger);
  }
}

// CR-016: 额度重置时间提示（UTC 00:00 = 北京时间 08:00）
const quotaResetHint = computed(() => {
  return t('gameViewExtra.quotaResetHintFull');
});


// Computed properties for new components
const currentChapter = computed(() => {
  // CR-030: 优先使用 gameStatus 的章节信息（来自 API），其次使用 progress API 的章节信息
  if (gameStatus.value?.chapter_number && gameStatus.value?.chapter_title) {
    return t('gameViewExtra.chapterTitle', { n: gameStatus.value.chapter_number, title: gameStatus.value.chapter_title });
  }
  // CR-020: 其次使用 progress API 的章节信息，最后使用 dialogue 的章节信息
  return gameProgress.value?.current_chapter || game.currentDialogue?.chapter || t('gameViewExtra.prologue');
});

// 章节背景图片映射：根据章节动态切换背景
const chapterBackgrounds: Record<string, string> = {
  t('gameViewExtra.chapter1'): 'http://47.107.174.176:8000/static/images/others/d6eb2bac-5b7e-496d-bed7-df085f34a564.png',
  t('gameViewExtra.chapter2'): 'http://47.107.174.176:8000/static/images/scripts/covers/edaa2171-11c9-403e-a55f-543e97e94205.png',
  t('gameViewExtra.chapter3'): 'http://47.107.174.176:8000/static/images/scripts/covers/3cfbf3fb-9164-4a54-8191-631f4bb6bb79.png',
};

const defaultBackground = 'http://47.107.174.176:8000/static/images/others/d6eb2bac-5b7e-496d-bed7-df085f34a564.png';

const currentBackground = computed(() => {
  const chapter = currentChapter.value;
  // 先精确匹配
  if (chapterBackgrounds[chapter]) {
    return chapterBackgrounds[chapter];
  }
  // 尝试模糊匹配（如 "第二章" 可能包含在 "第二章：星月奇缘" 中）
  for (const [key, url] of Object.entries(chapterBackgrounds)) {
    if (chapter.includes(key) || key.includes(chapter)) {
      return url;
    }
  }
  return defaultBackground;
});

const currentConvergencePoint = computed(() => {
  return game.currentDialogue?.convergence_point || '';
});

const chapterProgress = computed(() => {
  // FE-O1: 优先使用后端 progress API 数据
  if (gameProgress.value) {
    return Math.round(gameProgress.value.completion_rate || 0);
  }
  return game.currentDialogue?.progress || 0;
});

const currentAffection = computed(() => {
  const charId = game.currentDialogue?.character_id;
  if (!charId) return 0;
  const aff = affectionStore.getAffection(charId);
  return aff?.value || 0;
});

const characterTitle = computed(() => {
  return game.currentDialogue?.character_title || '';
});

const choiceOptions = computed(() => {
  return (game.pendingChoices || []).slice(0, 4).map((c) => ({
    id: c.id,
    text: c.text,
    affection_delta: c.affection_delta,
    hint: (c as any).hint,
  }));
});

const characterDisplayName = computed(() => {
  // CR-035 T-035-FE-001: 优先使用 gameStatus 中的角色名（从 /game/{session_id}/status API 获取）
  if (gameStatus.value?.character_name) {
    return gameStatus.value.character_name;
  }
  // CR-039 D2: 其次使用 gm_update 提取的角色名（Corvus done 事件 characterName=null 时的 fallback）
  if (game.currentCharacterName) return game.currentCharacterName;
  // 其次使用 currentDialogue 的 character_id 查找
  if (game.currentDialogue?.character_id) {
    const cid = game.currentDialogue.character_id;
    const gameName = game.characterNameMap[cid];
    if (gameName) return gameName;
    const aff = affectionStore.getAffection(cid);
    if (aff?.character_name) return aff.character_name;
  }
  return t('gameView.narrator');
});

// Initialize game
async function initGame() {
  const scriptId = route.query.script as string;
  const sessionId = route.query.session as string | undefined;
  const routeId = route.query.route as string | undefined;  // CR-020: 支持从指定章节开始
  const characterId = route.query.character_id as string | undefined;  // CR-028: 支持指定角色

  // 从个人中心「继续游戏」跳转：带 session 参数；或页面刷新时 localStorage 有 session
  // CR-031 BUG-031-001: await resumeSession
  if (sessionId && !scriptId) {
    phase.value = 'loading';
    game.reset();
    await game.loadScripts();
    try {
      // CR-031: await the async resumeSession call (previously missing await)
      await game.resumeSession(sessionId);
      if (game.currentSession) {
        phase.value = 'playing';
        await affectionStore.loadAffections();
        await Promise.all([
          loadGameProgress(),
          loadGameStatus(),
          loadHistoryFromApi()
        ]);
        // CR-039 T-039-FE-002: Corvus 会话如果没有初始对话或对话文字为空，自动发送一条初始消息
        if (game.currentSession.engine_type === 'corvus' && (!game.currentDialogue || !game.currentDialogue.text)) {
          await game.submitCustomInput(t('gameViewExtra.startGameCommand'));
        }
      } else {
        phase.value = 'error';
        errorMsg.value = t('gameViewExtra.cantRestoreSession');
      }
    } catch (err) {
      phase.value = 'error';
      errorMsg.value = err instanceof Error ? err.message : t('gameViewExtra.restoreSessionFailed');
    }
    return;
  }

  if (!scriptId) {
    phase.value = 'error';
    errorMsg.value = t('gameView.missingScriptId');
    return;
  }
  phase.value = 'loading';
  game.reset();
  await game.loadScripts();
  try {
    await game.startGame(scriptId, routeId, characterId);  // CR-020: 传递 routeId, CR-028: 传递 characterId
    if (game.currentSession) {
      phase.value = 'playing';
      await affectionStore.loadAffections();
      // FE-O1~O3: 加载游戏进度、状态和历史对话
      await Promise.all([
        loadGameProgress(),
        loadGameStatus(),
        loadHistoryFromApi()
      ]);
    } else {
      phase.value = 'error';
      errorMsg.value = game.error || t('gameView.cantStart');
    }
  } catch (err) {
    phase.value = 'error';
    errorMsg.value = err instanceof Error ? err.message : (game.error || t('gameView.startFailed'));
  }
}

// Story panel complete
function onStoryComplete() {
  // 记录对话到历史
  if (game.currentDialogue?.text) {
    dialogueHistory.value.push({
      type: 'dialogue',
      characterName: characterDisplayName.value,
      text: game.currentDialogue.text,
      timestamp: Date.now(),
    });
  }
}

// Handle choice selection
async function handleChoice(choiceId: string) {
  const choice = choiceOptions.value.find(c => c.id === choiceId);
  
  // 记录选择到历史
  if (choice) {
    dialogueHistory.value.push({
      type: 'choice',
      text: choice.text,
      timestamp: Date.now(),
      affectionDelta: choice.affection_delta,
    });
  }
  
  // 触发选择大师任务进度
  try {
    await gameApi.updateDailyTaskProgress('task_choice');
  } catch (err) {
    console.error('Failed to update choice task progress:', err);
  }
  
  // 检查当前额度是否足够（如果只剩1次，这次用完就没了）
  const quotaBefore = subscriptionStore.dialogueQuota?.remaining || 0;
  const willExhaustQuota = quotaBefore <= 1 && !subscriptionStore.isSubscriber;
  
  // CR-039: Corvus 引擎选项点击走 submitCustomInput
  const isCorvus = game.currentSession?.engine_type === 'corvus';
  const result = isCorvus
    ? await game.submitCustomInput(choice?.text || '')
    : await game.submitChoice(choiceId);
  
  // 如果发生错误，重置选择面板状态
  if (result?.error) {
    choicePanelRef.value?.reset();
    return;
  }

  // CR-016: 如果额度用完，不触发好感度动效
  if ((result as any)?.quotaExhausted) {
    // 额度不足，跳过好感度更新
    return;
  }
  
  // CR-019: 存储对话历史到数据库
  if (game.currentSession && game.currentDialogue?.text) {
    try {
      await gameApi.storeDialogue(game.currentSession.id, {
        role: 'assistant',
        content: game.currentDialogue.text,
        character_id: game.currentDialogue.character_id,
        character_name: characterDisplayName.value,
        emotion: game.currentDialogue.emotion,
      });
    } catch (err) {
      console.error('Failed to store dialogue:', err);
    }
  }
  
  // 刷新好感度和对话额度
  await Promise.all([
    affectionStore.loadAffections(),
    subscriptionStore.fetchDialogueQuota(),
    loadGameStatus()
  ]);

  // 只有额度没有用完时才显示好感度动效
  if (!willExhaustQuota && choice?.affection_delta) {
    showAffectionAnimation.value = true;
    affectionDelta.value = choice.affection_delta;
    setTimeout(() => {
      showAffectionAnimation.value = false;
    }, 1500);
  }

  // CR-016: 检查后端是否返回 paywall 触发指令
  const dialogue = game.currentDialogue as any;
  if (dialogue?.paywall) {
    triggerPaywall(dialogue.paywall);
  }

  // 成就解锁动画
  if (result?.new_achievements && result.new_achievements.length > 0) {
    for (const achievement of result.new_achievements) {
      showAchievementUnlockAnimation(achievement);
      // 如果有多个成就，依次显示（间隔 3.5 秒）
      await new Promise(resolve => setTimeout(resolve, 3500));
    }
  }
}

// Go to free chat page
function goToFreeChat() {
  if (!game.currentSession) {
    message.warning(t('gameViewExtra.pleaseStartGame'));
    return;
  }
  // CR-032 T-032-FE-003: 确保传递 NPC 角色 ID，不传递玩家角色 ID
  // D7: Corvus done 事件 character_id=null，fallback 到 gameStatus
  const npcCharacterId = game.currentDialogue?.character_id || gameStatus.value?.character_id;
  if (!npcCharacterId) {
    message.warning(t('gameViewExtra.noCharacterForChat'));
    return;
  }
  router.push({
    path: `/game/${game.currentSession.id}/free-chat`,
    query: {
      character: characterDisplayName.value,
      characterId: npcCharacterId,  // CR-032: 必须传递 NPC 角色，不能 fallback 到玩家角色
      scriptId: game.currentScript?.id,
    },
  });
}

// Open history drawer
function openHistory() {
  showHistory.value = true;
}

function closeHistory() {
  showHistory.value = false;
}

// Handle free chat message
async function handleFreeChat(msg: string) {
  // 记录自定义输入到历史
  dialogueHistory.value.push({
    type: 'choice',
    text: msg,
    timestamp: Date.now(),
    affectionDelta: 0, // 自定义输入的好感度变化由后端计算
  });
  
  // CR-019: 存储用户输入到数据库
  if (game.currentSession) {
    try {
      await gameApi.storeDialogue(game.currentSession.id, {
        role: 'user',
        content: msg,
        character_id: game.currentDialogue?.character_id,
        character_name: characterDisplayName.value,
      });
    } catch (err) {
      console.error('Failed to store user dialogue:', err);
    }
  }
  
  // 使用 submitCustomInput 推进剧情（和选择一样）
  const result = await game.submitCustomInput(msg);
  
  // CR-020: 处理章节转换提示
  if (result?.chapter_transition) {
    const transitionMsg = result.chapter_transition.message;
    // 显示章节转换提示
    message.success(`🎉 ${transitionMsg}`, { duration: 3000 });
    // 可以在这里添加更复杂的章节转换动画
  }
  
  // CR-019: 存储 AI 回复到数据库
  if (game.currentSession && game.currentDialogue?.text) {
    try {
      await gameApi.storeDialogue(game.currentSession.id, {
        role: 'assistant',
        content: game.currentDialogue.text,
        character_id: game.currentDialogue.character_id,
        character_name: characterDisplayName.value,
        emotion: game.currentDialogue.emotion,
      });
    } catch (err) {
      console.error('Failed to store AI dialogue:', err);
    }
  }
  
  // 刷新好感度和对话额度
  await Promise.all([
    affectionStore.loadAffections(),
    subscriptionStore.fetchDialogueQuota(),
    loadGameStatus()
  ]);
  
  // 成就解锁动画
  if (result?.new_achievements && result.new_achievements.length > 0) {
    for (const achievement of result.new_achievements) {
      showAchievementUnlockAnimation(achievement);
      // 如果有多个成就，依次显示（间隔 3.5 秒）
      await new Promise(resolve => setTimeout(resolve, 3500));
    }
  }
}

// FE-O5: 送礼弹窗状态
const showGiftModal = ref(false);
const showGiftHistoryModal = ref(false);
const giftLoading = ref(false);
const giftHistoryLoading = ref(false);
const giftList = ref<Array<{ id: string; name: string; icon?: string; cost: number; affection_bonus: number }>>([]);
const giftHistory = ref<Array<{ id: string; gift_name: string; character_name: string; affection_delta: number }>>([]);
const selectedGift = ref<{ id: string; name: string; icon?: string; cost: number; affection_bonus: number } | null>(null);
const shardBalance = ref(0);

// Open gift modal
async function openGiftModal() {
  if (!game.currentSession || !game.currentDialogue?.character_id) {
    message.warning(t('gameViewExtra.cannotSendGiftNow'));
    return;
  }
  
  showGiftModal.value = true;
  giftLoading.value = true;
  selectedGift.value = null;
  
  try {
    // 并行加载礼物列表和碎片余额
    const [giftData, balanceData] = await Promise.all([
      gameApi.getGiftCatalog(),
      gameApi.getShardBalance()
    ]);
    if (giftData && giftData.gifts) {
      // 字段映射：后端返回 price，前端用 cost
      giftList.value = giftData.gifts.map((g: any) => ({
        ...g,
        cost: g.cost ?? g.price ?? 0,
      }));
    }
    if (balanceData && typeof balanceData.balance === 'number') {
      shardBalance.value = balanceData.balance;
    }
  } catch (err) {
    console.error('加载礼物列表失败:', err);
    message.error(t('gameViewExtra.loadGiftListFailed'));
  } finally {
    giftLoading.value = false;
  }
}

// Gift sent callback
async function onGiftSent() {
  // 刷新好感度
  await affectionStore.loadAffections();
}

// View gift history
async function viewGiftHistory() {
  // CR-032 T-032-FE-004: 获取当前 NPC 角色的送礼记录
  const npcCharacterId = game.currentDialogue?.character_id || gameStatus.value?.character_id;
  if (!npcCharacterId) {
    message.warning(t('gameViewExtra.noCharacterForGiftHistory'));
    return;
  }
  
  showGiftHistoryModal.value = true;
  giftHistoryLoading.value = true;
  
  try {
    // 使用角色专属的送礼记录 API，而非 session 级别的全局记录
    const historyData = await gameApi.getCharacterGiftHistory(npcCharacterId);
    if (historyData && historyData.gifts) {
      giftHistory.value = historyData.gifts;
    }
  } catch (err) {
    console.error('获取送礼历史失败:', err);
    message.error(t('gameViewExtra.getGiftHistoryFailed'));
  } finally {
    giftHistoryLoading.value = false;
  }
}

// Manual save
async function handleManualSave() {
  if (!game.currentSession) return;
  try {
    await saveApi.createSave({
      session_id: game.currentSession.id,
      script_id: game.currentScript?.id,
      character_id: game.currentDialogue?.character_id,
      current_node_id: game.currentNode?.id,
      affection_value: currentAffection.value,
      choice_history: game.choiceHistory,
    });
    message.success(t('gameViewExtra.saveSuccess'));
  } catch (err) {
    message.error(t('gameViewExtra.saveFailed'));
  }
}

// Restart current chapter
async function handleRestartCurrentChapter() {
  const scriptId = game.currentScript?.id;
  const chapterId = game.currentDialogue?.chapter;
  if (!scriptId) {
    router.push('/discover');
    return;
  }
  phase.value = 'loading';
  // 先清除 localStorage 中的旧会话，避免 startGame 直接恢复旧会话
  localStorage.removeItem('game_session');
  localStorage.removeItem('game_script');
  game.reset();
  await game.loadScripts();
  // 从当前章节重新开始
  await game.startGame(scriptId, chapterId);
  if (game.currentSession) {
    phase.value = 'playing';
    await affectionStore.loadAffections();
    // 重新加载游戏状态
    await Promise.all([
      loadGameProgress(),
      loadGameStatus(),
      loadHistoryFromApi()
    ]);
  } else {
    phase.value = 'error';
    errorMsg.value = game.error || t('gameViewExtra.cantRestartChapter');
  }
}

// Go to next chapter
async function handleNextChapter() {
  const scriptId = game.currentScript?.id;
  const nextChapterId = (game.currentDialogue as any)?.next_chapter;
  if (!scriptId || !nextChapterId) {
    router.push('/discover');
    return;
  }
  phase.value = 'loading';
  // 先清除 localStorage 中的旧会话，避免 startGame 直接恢复旧会话
  localStorage.removeItem('game_session');
  localStorage.removeItem('game_script');
  game.reset();
  await game.loadScripts();
  // 从下一章节开始
  await game.startGame(scriptId, nextChapterId);
  if (game.currentSession) {
    phase.value = 'playing';
    await affectionStore.loadAffections();
    // 重新加载游戏状态
    await Promise.all([
      loadGameProgress(),
      loadGameStatus(),
      loadHistoryFromApi()
    ]);
  } else {
    phase.value = 'error';
    errorMsg.value = game.error || t('gameViewExtra.cantEnterNextChapter');
  }
}

// Exit warning
onBeforeRouteLeave((_to, _from, next) => {
  if (game.currentSession && !game.isSaved) {
    const confirmed = window.confirm(t('gameViewExtra.unsavedProgressConfirm'));
    if (confirmed) {
      handleManualSave();
    }
  }
  next();
});

onMounted(async () => {
  await initGame();
  // CR-016: 加载订阅状态和对话额度
  await subscriptionStore.fetchSubscriptionStatus();
  await subscriptionStore.fetchDialogueQuota();
});
</script>

<style scoped>
.game-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
}

.phase-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.loading-hero {
  text-align: center;
}

.loading-hero h2 {
  font-size: 22px;
  margin: 16px 0 24px;
}

.loading-emoji {
  font-size: 56px;
}

/* Two-column layout */
.game-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.back-btn {
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-left: auto;
}

/* CR-016: 额度展示 - 内联样式 */
.quota-inline {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(192, 132, 252, 0.08);
  border: 1px solid rgba(192, 132, 252, 0.2);
  border-radius: 8px;
  font-size: 13px;
}

.quota-inline .quota-icon {
  font-size: 14px;
}

.quota-inline .quota-value {
  font-weight: 600;
  color: var(--text-main);
}

.quota-inline .quota-value.is-subscriber {
  color: #ffd700;
}

.quota-inline .quota-reset-hint {
  font-size: 11px;
  color: var(--text-muted);
}

.icon-btn {
  padding: 8px 12px;
  font-size: 14px;
}

.game-layout {
  display: grid;
  grid-template-columns: 25% 75%;
  gap: 24px;
  height: calc(100vh - 180px);
  flex: 1;
  min-height: 0;
}

/* Responsive: single column on mobile */
@media (max-width: 768px) {
  .game-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 0;
  }
  
  .left-sidebar {
    display: none; /* 移动端隐藏左侧栏，角色信息通过其他方式展示 */
  }
  
  .right-story-stage {
    height: auto;
    min-height: calc(100vh - 200px);
    overflow-y: visible; /* 移动端让内容自然流动 */
  }
}

.left-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow-y: auto;
}

.right-story-stage {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
  transition: background-image 0.6s ease;
  background-blend-mode: overlay;
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
  position: relative;
}

.right-story-stage::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 10, 26, 0.75);
  border-radius: 16px;
  pointer-events: none;
  z-index: 0;
}

.right-story-stage > * {
  position: relative;
  z-index: 1;
}

.action-btn {
  width: 100%;
  justify-content: center;
}

/* FE-O5: Gift modal styles */
.shard-balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 16px;
  background: rgba(var(--brand-primary-rgb), 0.05);
  border-radius: 8px;
  border: 1px solid rgba(var(--brand-primary-rgb), 0.2);
}

.balance-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.balance-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--brand-primary);
}

.gift-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.gift-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.gift-item:hover {
  background: var(--hover-bg);
}

.gift-item.selected {
  border-color: var(--brand-primary);
  background: rgba(var(--brand-primary-rgb), 0.1);
}

.gift-icon {
  font-size: 24px;
}

.gift-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.gift-name {
  font-weight: 500;
}

.gift-cost {
  font-size: 12px;
  color: var(--text-muted);
}

.gift-affection {
  color: var(--brand-primary);
  font-weight: 500;
}

/* FE-O5: Gift history modal styles */
.gift-history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.gift-history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
}

.gift-history-icon {
  font-size: 20px;
}

.gift-history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.gift-history-name {
  font-weight: 500;
}

.gift-history-to {
  font-size: 12px;
  color: var(--text-muted);
}

.gift-history-affection {
  color: var(--brand-primary);
  font-weight: 500;
}

/* Ending card */
.ending-detected {
  margin-top: 20px;
}

.ending-card {
  padding: 28px;
  text-align: center;
}

.ending-card.good {
  border-color: rgba(192, 132, 252, 0.25);
}

.ending-card.bad {
  border-color: rgba(252, 165, 165, 0.2);
}

.ending-badge {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
}

.ending-badge.good {
  background: rgba(192, 132, 252, 0.15);
  color: var(--brand-primary);
}

.ending-badge.bad {
  background: rgba(252, 165, 165, 0.12);
  color: #fca5a5;
}

.ending-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 10px;
}

.ending-desc {
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}

.ending-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.phase-error {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

/* CR-016: 额度展示条 */
.quota-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  margin-bottom: 12px;
  background: rgba(139, 92, 246, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.12);
  border-radius: 12px;
  font-size: 13px;
}

.quota-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quota-icon {
  font-size: 16px;
}

.quota-label {
  color: var(--text-muted);
}

.quota-value {
  font-weight: 600;
  color: var(--text-main);
}

.quota-value.is-subscriber {
  color: #fbbf24;
  font-size: 16px;
}

.quota-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lifecycle-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.lifecycle-tag.honeymoon {
  background: rgba(244, 114, 182, 0.15);
  color: #f472b6;
}

.lifecycle-tag.growth {
  background: rgba(79, 70, 229, 0.15);
  color: #818cf8;
}

.lifecycle-tag.regular {
  background: rgba(124, 111, 155, 0.15);
  color: var(--text-muted);
}

.lifecycle-tag.returnee {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

/* 好感度动效 */
.affection-animation {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  font-weight: 800;
  padding: 20px 40px;
  border-radius: 16px;
  z-index: 9999;
  pointer-events: none;
  animation: affectionPop 1.5s ease-out;
}

.affection-animation.positive {
  background: rgba(134, 239, 172, 0.9);
  color: #065f46;
  box-shadow: 0 8px 32px rgba(134, 239, 172, 0.5);
}

.affection-animation.negative {
  background: rgba(252, 165, 165, 0.9);
  color: #991b1b;
  box-shadow: 0 8px 32px rgba(252, 165, 165, 0.5);
}

@keyframes affectionPop {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  20% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1.2);
  }
  40% {
    transform: translate(-50%, -50%) scale(1);
  }
  80% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.8);
  }
}

/* 成就解锁动画覆盖层 */
.achievement-unlock-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  animation: overlayFadeIn 300ms ease forwards;
}

@keyframes overlayFadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

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
        <!-- CR-016: 额度展示条 -->
        <div class="quota-bar" v-if="subscriptionStore.dialogueQuota">
          <div class="quota-left">
            <span class="quota-icon">💬</span>
            <span class="quota-label">对话额度</span>
            <span class="quota-value" :class="{ 'is-subscriber': subscriptionStore.isSubscriber }">
              {{ subscriptionStore.isSubscriber ? '∞' : `${subscriptionStore.dialogueQuota.remaining} / ${subscriptionStore.dialogueQuota.base_quota}` }}
            </span>
            <span v-if="!subscriptionStore.isSubscriber" class="quota-reset-hint" :title="quotaResetHint">
              🕐 每日 08:00 重置
            </span>
          </div>
          <div class="quota-right">
            <span class="lifecycle-tag" :class="subscriptionStore.dialogueQuota.lifecycle_stage">
              {{ lifecycleStageLabel(subscriptionStore.dialogueQuota.lifecycle_stage) }}
            </span>
            <n-button v-if="!subscriptionStore.isSubscriber && subscriptionStore.dialogueQuota.remaining <= 2" size="tiny" type="primary" @click="router.push('/subscribe')">
              补充额度
            </n-button>
          </div>
        </div>

        <!-- 游戏标题栏 -->
        <div class="game-header">
          <ChapterProgress
            :chapter="currentChapter"
            :convergence-point="currentConvergencePoint"
            :progress="chapterProgress"
          />
          <div class="header-actions">
            <n-button @click="handleManualSave" class="icon-btn" title="存档">
              💾 存档
            </n-button>
            <n-button @click="openHistory" class="icon-btn" title="历史">
              📜 历史
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
            />
            <AffectionDisplay
              :character-id="gameStatus?.character_id || game.currentDialogue?.character_id"
              :value="gameStatus?.affection_value ?? currentAffection"
              :level="gameStatus?.affection_level || affectionLevel"
            />
            <n-button @click="openGiftModal" class="action-btn">🎁 送礼</n-button>
            <n-button @click="goToFreeChat" class="action-btn">💬 自由对话</n-button>
            <n-button @click="handleManualSave" class="action-btn">💾 手动存档</n-button>
            <n-button @click="viewGiftHistory" class="action-btn">📋 送礼记录</n-button>
          </aside>

          <!-- 右侧栏 flex:1 -->
          <main class="right-story-stage">
            <StoryPanel
              :text="game.currentDialogue?.text || '剧情正在展开...'"
              :character-name="characterDisplayName"
              :emotion="game.currentDialogue?.emotion"
              :speed="typewriterSpeed"
              @complete="onStoryComplete"
            />
            <ChoicePanel
              v-if="game.hasChoices"
              :choices="choiceOptions"
              @select="handleChoice"
            />
            <!-- 剧本对话输入框 -->
            <FreeChatInput
              v-if="!game.isEnded"
              :character-id="game.currentDialogue?.character_id"
              :character-name="characterDisplayName"
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
                  <n-button size="large" secondary @click="router.push('/discover')">{{ $t('game.backToHome') }}</n-button>
                  <n-button size="large" secondary @click="handleRestart">🔄 {{ $t('game.startGame') }}</n-button>
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
        :dialogue-history="dialogueHistory"
        @close="closeHistory"
      />

      <!-- FE-O5: 送礼弹窗 -->
      <n-modal
        v-model:show="showGiftModal"
        preset="card"
        title="🎁 送礼"
        :style="{ width: '400px' }"
      >
        <div v-if="giftLoading" style="text-align: center; padding: 20px;">
          <n-spin size="medium" />
          <p style="margin-top: 10px; color: var(--text-muted);">加载礼物列表...</p>
        </div>
        <div v-else-if="giftList.length === 0" style="text-align: center; padding: 20px;">
          <n-empty description="暂无可用礼物" />
        </div>
        <div v-else class="gift-list">
          <div
            v-for="gift in giftList"
            :key="gift.id"
            class="gift-item"
            :class="{ selected: selectedGift?.id === gift.id }"
            @click="selectedGift = gift"
          >
            <span class="gift-icon">{{ gift.icon || '🎁' }}</span>
            <div class="gift-info">
              <span class="gift-name">{{ gift.name }}</span>
              <span class="gift-cost">💎 {{ gift.cost }} 碎片</span>
            </div>
            <span class="gift-affection">+{{ gift.affection_bonus }} 好感</span>
          </div>
        </div>
        <template #footer>
          <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <n-button @click="showGiftModal = false">取消</n-button>
            <n-button
              type="primary"
              :disabled="!selectedGift || giftLoading"
              @click="confirmSendGift"
            >
              确认送礼
            </n-button>
          </div>
        </template>
      </n-modal>

      <!-- FE-O5: 送礼记录弹窗 -->
      <n-modal
        v-model:show="showGiftHistoryModal"
        preset="card"
        title="📋 送礼记录"
        :style="{ width: '450px' }"
      >
        <div v-if="giftHistoryLoading" style="text-align: center; padding: 20px;">
          <n-spin size="medium" />
        </div>
        <div v-else-if="giftHistory.length === 0" style="text-align: center; padding: 20px;">
          <n-empty description="暂无送礼记录" />
        </div>
        <div v-else class="gift-history-list">
          <div v-for="record in giftHistory" :key="record.id" class="gift-history-item">
            <span class="gift-history-icon">🎁</span>
            <div class="gift-history-info">
              <span class="gift-history-name">{{ record.gift_name }}</span>
              <span class="gift-history-to">送给 {{ record.character_name }}</span>
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
import { chatApi } from '@/api/chat';
import { saveApi } from '@/api/saves';
import { gameApi } from '@/api/game';

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

const phase = ref<'loading' | 'playing' | 'error'>('loading');
const errorMsg = ref('');
const showFreeChat = ref(false);
const typewriterSpeed = ref(1);

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
} | null>(null);

// 游戏状态（角色信息）
const gameStatus = ref<{
  script_name: string;
  character_name: string;
  character_id: string;
  affection_value: number;
  affection_level: string;
} | null>(null);

// 角色详细数据
const characterDetail = ref<{
  age?: number;
  height?: number;
  birthday?: string;
  likes?: string[] | { items: string[] };
  personality?: string | Record<string, any>;
} | null>(null);

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
      affection_value: status.affection_value || 0,
      affection_level: status.affection_level || '相识',
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

// CR-016: 生命周期阶段标签
function lifecycleStageLabel(stage: string): string {
  const map: Record<string, string> = {
    honeymoon: '蜜月期',
    growth: '养成期',
    regular: '常规期',
    returnee: '回归期'
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
  return '每日 08:00 重置（UTC 00:00）';
});


// Computed properties for new components
const currentChapter = computed(() => {
  // Extract chapter from current node or dialogue
  return game.currentDialogue?.chapter || '第一章';
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

const affectionLevel = computed(() => {
  const charId = game.currentDialogue?.character_id;
  if (!charId) return '相识';
  const aff = affectionStore.getAffection(charId);
  return aff?.level || '相识';
});

const characterTitle = computed(() => {
  return game.currentDialogue?.character_title || '';
});

const choiceOptions = computed(() => {
  return (game.pendingChoices || []).slice(0, 3).map((c) => ({
    id: c.id,
    text: c.text,
    affection_delta: c.affection_delta,
  }));
});

const characterDisplayName = computed(() => {
  if (!game.currentDialogue?.character_id) return t('gameView.narrator');
  const cid = game.currentDialogue.character_id;
  const gameName = game.characterNameMap.get(cid);
  if (gameName) return gameName;
  const aff = affectionStore.getAffection(cid);
  if (aff?.character_name) return aff.character_name;
  return t('gameView.character');
});

// Initialize game
async function initGame() {
  const scriptId = route.query.script as string;
  if (!scriptId) {
    phase.value = 'error';
    errorMsg.value = t('gameView.missingScriptId');
    return;
  }
  phase.value = 'loading';
  game.reset();
  await game.loadScripts();
  try {
    await game.startGame(scriptId);
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
  
  const result = await game.submitChoice(choiceId);
  
  // CR-016: 如果额度用完，不触发好感度动效
  if (result?.quotaExhausted) {
    // 额度不足，跳过好感度更新
    return;
  }
  
  await affectionStore.loadAffections();

  // CR-016: 检查后端是否返回 paywall 触发指令
  const dialogue = game.currentDialogue as any;
  if (dialogue?.paywall) {
    triggerPaywall(dialogue.paywall);
  }
}

// Go to free chat page
function goToFreeChat() {
  if (!game.currentSession) {
    message.warning('请先开始游戏');
    return;
  }
  router.push({
    path: `/game/${game.currentSession.id}/free-chat`,
    query: {
      character: characterDisplayName.value,
      characterId: game.currentDialogue?.character_id,
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
  const characterId = game.currentDialogue?.character_id;
  if (!characterId) return;
  try {
    const response = await chatApi.sendFreeChat({
      character_id: characterId,
      message: msg,
      script_id: game.currentScript?.id,
      session_id: game.currentSession?.id, // CR-018 T-002 fix: include session_id
    });
    message.success(response.reply);
  } catch (err) {
    message.error('自由对话失败');
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

// Open gift modal
async function openGiftModal() {
  if (!game.currentSession || !game.currentDialogue?.character_id) {
    message.warning('当前无法送礼');
    return;
  }
  
  showGiftModal.value = true;
  giftLoading.value = true;
  selectedGift.value = null;
  
  try {
    const giftData = await gameApi.getGiftCatalog();
    if (giftData && giftData.gifts) {
      giftList.value = giftData.gifts;
    }
  } catch (err) {
    console.error('加载礼物列表失败:', err);
    message.error('加载礼物列表失败');
  } finally {
    giftLoading.value = false;
  }
}

// Confirm send gift
async function confirmSendGift() {
  if (!selectedGift.value || !game.currentSession || !game.currentDialogue?.character_id) {
    return;
  }
  
  try {
    const result = await gameApi.sendGameGift(
      game.currentSession.id,
      game.currentDialogue.character_id,
      selectedGift.value.id,
      1
    );
    
    message.success(result.message || `成功送出 ${selectedGift.value.name}！`);
    showGiftModal.value = false;
    // 刷新好感度
    await affectionStore.loadAffections();
  } catch (err) {
    console.error('送礼失败:', err);
    message.error(err instanceof Error ? err.message : '送礼失败');
  }
}

// View gift history
async function viewGiftHistory() {
  if (!game.currentSession) {
    message.warning('暂无送礼记录');
    return;
  }
  
  showGiftHistoryModal.value = true;
  giftHistoryLoading.value = true;
  
  try {
    const historyData = await gameApi.getGiftHistory(game.currentSession.id);
    if (historyData && historyData.gifts) {
      giftHistory.value = historyData.gifts;
    }
  } catch (err) {
    console.error('获取送礼历史失败:', err);
    message.error('获取送礼历史失败');
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
    message.success('存档成功');
  } catch (err) {
    message.error('存档失败');
  }
}

// Restart game
async function handleRestart() {
  const scriptId = game.currentScript?.id;
  if (!scriptId) {
    router.push('/discover');
    return;
  }
  game.reset();
  await game.startGame(scriptId);
  if (game.currentSession) {
    await affectionStore.loadAffections();
  }
}

// Exit warning
onBeforeRouteLeave((_to, _from, next) => {
  if (game.currentSession && !game.isSaved) {
    const confirmed = window.confirm('当前进度尚未存档，是否存档后再离开？');
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 8px;
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
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;
}

.action-btn {
  width: 100%;
  justify-content: center;
}

/* FE-O5: Gift modal styles */
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
</style>

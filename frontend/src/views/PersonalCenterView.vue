<template>
  <div class="personal-center-page">
    <!-- 用户信息卡片 -->
    <div class="user-info-card glass-card">
      <div class="user-avatar">
        <img v-if="userProfile?.avatar_url && !userAvatarFailed" :src="userProfile.avatar_url" :alt="userProfile.display_name || '用户'" @error="userAvatarFailed = true" />
        <div v-else class="avatar-placeholder">
          {{ (userProfile?.display_name || 'U').charAt(0).toUpperCase() }}
        </div>
      </div>
      <div class="user-info">
        <h2 class="user-name">{{ userProfile?.display_name || '用户' }}</h2>
        <p class="user-email">{{ userProfile?.email || '' }}</p>
        <div class="user-badges">
          <span class="badge" :class="subscriptionStatus?.tier || 'free'">
            {{ subscriptionStatus?.tier === 'premium' ? '高级会员' : subscriptionStatus?.tier === 'standard' ? '标准会员' : '免费用户' }}
          </span>
          <span class="badge email-verified" v-if="userProfile?.email_verified">✓ 已验证</span>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-card glass-card">
      <h3 class="card-title">📊 游戏统计</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats?.scripts_completed || 0 }}</div>
          <div class="stat-label">完成剧本</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_play_time_minutes || 0 }}</div>
          <div class="stat-label">游戏时长(分钟)</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.endings_unlocked || 0 }}</div>
          <div class="stat-label">解锁结局</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.cgs_collected || 0 }}</div>
          <div class="stat-label">收集 CG</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_dialogues || 0 }}</div>
          <div class="stat-label">总对话数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_choices || 0 }}</div>
          <div class="stat-label">选择次数</div>
        </div>
        <!-- CR-028: 扮演角色数 -->
        <div class="stat-item" v-if="stats?.characters_played !== undefined">
          <div class="stat-value">{{ stats.characters_played }}</div>
          <div class="stat-label">扮演角色</div>
        </div>
      </div>
    </div>

    <!-- 对话额度卡片 -->
    <div class="quota-card glass-card">
      <h3 class="card-title">💬 今日对话额度</h3>
      <div class="quota-content">
        <div class="quota-display">
          <div class="quota-used">
            <span class="quota-value">{{ dialogueQuota?.used || 0 }}</span>
            <span class="quota-label">已使用</span>
          </div>
          <div class="quota-separator">/</div>
          <div class="quota-total">
            <span class="quota-value" v-if="dialogueQuota?.total === -1">无限额度</span>
            <span class="quota-value" v-else>{{ dialogueQuota?.total || 0 }}</span>
            <span class="quota-label" v-if="dialogueQuota?.total !== -1">总额度</span>
          </div>
        </div>
        <div class="quota-progress">
          <div 
            class="progress-bar" 
            :style="{ width: `${Math.min(100, ((dialogueQuota?.used || 0) / (dialogueQuota?.total || 1)) * 100)}%` }"
            :class="{ 'warning': ((dialogueQuota?.used || 0) / (dialogueQuota?.total || 1)) > 0.8 }"
          ></div>
        </div>
        <div class="quota-hint" v-if="dialogueQuota">
          <span v-if="dialogueQuota.is_subscriber">✨ 订阅用户 · 无限额度</span>
          <span v-else>剩余 {{ dialogueQuota.total - dialogueQuota.used }} 次对话</span>
        </div>
      </div>
    </div>

    <!-- 碎片资产卡片 -->
    <div class="asset-card glass-card">
      <h3 class="card-title">💎 碎片资产</h3>
      <div class="asset-content">
        <div class="asset-balance">
          <div class="balance-value">{{ asset?.balance || 0 }}</div>
          <div class="balance-label">当前余额</div>
        </div>
        <div class="asset-stats">
          <div class="asset-stat">
            <span class="stat-label">累计获得</span>
            <span class="stat-value">{{ asset?.total_earned || 0 }}</span>
          </div>
          <div class="asset-stat">
            <span class="stat-label">累计消费</span>
            <span class="stat-value">{{ asset?.total_spent || 0 }}</span>
          </div>
        </div>
        <n-button type="primary" size="small" @click="router.push('/subscribe')">
          充值碎片
        </n-button>
      </div>
    </div>

    <!-- 签到卡片 -->
    <div class="checkin-card glass-card">
      <h3 class="card-title">📅 每日签到</h3>
      <div class="checkin-content">
        <div class="checkin-info">
          <div class="streak-days">
            <span class="streak-value">{{ signInfo?.streak_days || 0 }}</span>
            <span class="streak-label">连续签到</span>
          </div>
          <div class="total-checkins">
            <span class="total-value">{{ signInfo?.total_checkins || 0 }}</span>
            <span class="total-label">累计签到</span>
          </div>
          <div class="total-fragments">
            <span class="total-value">{{ signInfo?.total_fragments || 0 }}</span>
            <span class="total-label">累计获得</span>
          </div>
        </div>
        <div class="checkin-week">
          <div 
            v-for="(checked, index) in signInfo?.this_week || []" 
            :key="index"
            class="week-day"
            :class="{ checked }"
          >
            {{ ['一', '二', '三', '四', '五', '六', '日'][index] }}
          </div>
        </div>
        <n-button 
          type="primary" 
          size="small" 
          :disabled="signInfo?.checked_in_today"
          @click="handleCheckin"
        >
          {{ signInfo?.checked_in_today ? '今日已签到' : '立即签到' }}
        </n-button>
      </div>
    </div>

    <!-- CR-025 S017: 每日任务卡片 -->
    <div class="daily-tasks-card glass-card">
      <div class="card-header">
        <h3 class="card-title">📋 每日任务</h3>
        <div class="reset-info">每日 0:00 刷新</div>
        <div class="all-complete-btn">
          <n-button
            v-if="allTasksCompleted && !allCompleteClaimed"
            type="success"
            size="small"
            @click="claimAllTasks"
          >
            🎁 全完成奖励
          </n-button>
          <n-tag v-else-if="allCompleteClaimed" type="success" size="small">已领取</n-tag>
          <n-button v-else size="small" disabled>🎁 全完成奖励</n-button>
        </div>
      </div>
      <div class="tasks-list">
        <div v-for="task in dailyTasks" :key="task.id" class="task-item">
          <div class="task-info">
            <div class="task-title">{{ task.icon }} {{ task.title }}</div>
            <div class="task-desc">{{ task.description }}</div>
            <div class="task-progress">
              <n-progress 
                type="line" 
                :percentage="Math.min(100, (task.progress / task.target) * 100)" 
                :show-indicator="false" 
                :height="6" 
              />
              <span class="progress-text">{{ task.progress }}/{{ task.target }}</span>
            </div>
          </div>
          <div class="task-reward">
            <span class="reward-amount">💎 +{{ task.reward_amount }}</span>
            <n-button 
              v-if="task.completed && !task.claimed" 
              size="tiny" 
              type="primary"
              @click="claimTask(task)"
            >
              领取
            </n-button>
            <n-tag v-else-if="task.claimed" type="success" size="small">已领取</n-tag>
            <n-button 
              v-else 
              size="tiny" 
              :disabled="true"
            >
              领取
            </n-button>
          </div>
        </div>
        <n-empty v-if="dailyTasks.length === 0" description="暂无任务" />
      </div>
    </div>

    <!-- 继续游玩卡片 -->
    <div class="continue-card glass-card" v-if="latestSave">
      <h3 class="card-title">🎮 继续游玩</h3>
      <div class="continue-content">
        <!-- CR-028: 角色头像展示 -->
        <div v-if="latestSave.character_avatar || latestSave.character_name" class="continue-character">
          <div class="continue-avatar">
            <img v-if="latestSave.character_avatar && !continueAvatarFailed" :src="latestSave.character_avatar" :alt="latestSave.character_name || '角色'" @error="continueAvatarFailed = true" />
            <span v-else>{{ (latestSave.character_name || '?').charAt(0) }}</span>
          </div>
        </div>
        <div class="save-info">
          <div class="script-name">{{ latestSave.script_name }}</div>
          <div class="character-name" v-if="latestSave.character_name">🎮 {{ latestSave.character_name }}</div>
          <div class="save-time">
            {{ new Date(latestSave.updated_at).toLocaleString('zh-CN') }}
          </div>
        </div>
        <n-button type="primary" size="small" @click="continueGame">
          继续游戏
        </n-button>
      </div>
    </div>

    <!-- 角色羁绊卡片 -->
    <div class="bond-card glass-card">
      <h3 class="card-title">💕 角色羁绊</h3>
      <div 
        class="bond-list" 
        ref="bondListRef"
        @scroll="handleBondScroll"
      >
        <div 
          v-for="character in bondCharacters" 
          :key="character.id"
          class="bond-item"
        >
          <div class="bond-avatar">
            {{ character.name.charAt(0) }}
          </div>
          <div class="bond-info">
            <div class="bond-name">{{ character.name }}</div>
            <div class="bond-level">{{ getAffectionLevelLabel(character.affection_level) }}</div>
          </div>
          <div class="bond-value">
            {{ character.affection_value }}/{{ character.max_affection }}
          </div>
        </div>
        <div v-if="bondLoading" class="bond-loading">
          <n-spin size="small" />
          <span>加载中...</span>
        </div>
        <div v-if="bondNoMore && bondCharacters.length > 0" class="bond-no-more">
          没有更多了
        </div>
        <n-empty v-if="!bondLoading && bondCharacters.length === 0" description="暂无羁绊" />
      </div>
    </div>

    <!-- 结局追踪卡片 -->
    <div class="endings-card glass-card">
      <h3 class="card-title">🏆 结局追踪</h3>
      <div class="endings-summary">
        <span class="endings-count">{{ endingsList?.total_endings_unlocked || 0 }}</span>
        <span class="endings-label">已解锁结局</span>
      </div>
      <div class="endings-list" v-if="endingsList?.endings && endingsList.endings.length > 0">
        <div 
          v-for="ending in endingsList.endings" 
          :key="ending.script_id"
          class="ending-item"
        >
          <div class="ending-script">{{ ending.script_name }}</div>
          <div class="ending-progress">
            {{ ending.unlocked_endings }}/{{ ending.total_endings }}
          </div>
        </div>
      </div>
      <n-empty v-else description="暂无结局" />
    </div>

    <!-- 新解锁结局卡片 -->
    <div class="continue-card glass-card" v-if="recentEndings?.recent_endings && recentEndings.recent_endings.length > 0">
      <h3 class="card-title">✨ 新解锁结局</h3>
      <div class="recent-endings-scroll">
        <div 
          v-for="ending in recentEndings.recent_endings" 
          :key="ending.id"
          class="recent-ending-item"
        >
          <div class="ending-info">
            <div class="ending-title">{{ cleanEndingTitle(ending.ending_title) }}</div>
            <div class="ending-meta">
              {{ ending.script_name }} · {{ ending.character_name }}
            </div>
          </div>
          <div class="ending-type" :class="ending.ending_type">
            {{ ending.ending_type === 'good' ? '好结局' : ending.ending_type === 'bad' ? '坏结局' : ending.ending_type }}
          </div>
        </div>
      </div>
    </div>

    <!-- AI 记忆卡片 -->
    <div class="memory-card glass-card">
      <h3 class="card-title">
        🧠 AI 记忆
        <span class="tooltip-icon" title="展示 AI 记住的对话内容">?</span>
      </h3>
      <div class="memory-content">
        <div class="memory-summary">
          <span class="memory-count">{{ memorySummary?.total_memories || 0 }}</span>
          <span class="memory-label">条记忆</span>
        </div>
        
        <!-- FE-FEAT-025: 分类展示记忆 -->
        <div class="memory-categories">
          <!-- 用户偏好 -->
          <div class="memory-category" v-if="memorySummary?.preferences && memorySummary.preferences.length > 0">
            <h4 class="category-title">🎯 用户偏好 ({{ memorySummary.preferences.length }})</h4>
            <div class="memory-list">
              <div 
                v-for="pref in memorySummary.preferences" 
                :key="pref.id"
                class="memory-item"
              >
                <div class="memory-text">{{ pref.description }}</div>
                <div class="memory-time">{{ formatDate(pref.created_at) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 角色羁绊 -->
          <div class="memory-category" v-if="memorySummary?.bonds && memorySummary.bonds.length > 0">
            <h4 class="category-title">💕 角色羁绊 ({{ memorySummary.bonds.length }})</h4>
            <div class="memory-list">
              <div 
                v-for="bond in memorySummary.bonds" 
                :key="bond.id"
                class="memory-item"
              >
                <div class="memory-character">{{ bond.character_name }}</div>
                <div class="memory-text">{{ bond.description }}</div>
                <div class="memory-time">{{ formatDate(bond.created_at) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 重要事件 -->
          <div class="memory-category" v-if="memorySummary?.events && memorySummary.events.length > 0">
            <h4 class="category-title">✨ 重要事件 ({{ memorySummary.events.length }})</h4>
            <div class="memory-list">
              <div 
                v-for="event in memorySummary.events" 
                :key="event.id"
                class="memory-item"
              >
                <div class="memory-text">{{ event.description }}</div>
                <div class="memory-time">{{ formatDate(event.created_at) }}</div>
              </div>
            </div>
          </div>
          
          <!-- 默认显示最近记忆 -->
          <div class="recent-memories" v-if="!hasCategorizedMemories && memorySummary?.recent && memorySummary.recent.length > 0">
            <div 
              v-for="memory in memorySummary.recent" 
              :key="memory.id"
              class="memory-item"
            >
              <div class="memory-character">{{ memory.character_name }}</div>
              <div class="memory-text">{{ memory.content }}</div>
              <div class="memory-time">{{ formatDate(memory.created_at) }}</div>
            </div>
          </div>
        </div>
        
        <n-empty v-if="!hasAnyMemories" description="暂无记忆" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NButton, NEmpty } from 'naive-ui';
import { api } from '@/api/http';
import { gameApi } from '@/api/game';
import { getMe, getMySubscription, getMyStats, getMyAsset, getSignInfo, getLatestSave, getMemorySummary, getCharacterBond, getMyEndings, getRecentEndings } from '@/api/user';
import type { UserProfile, SubscriptionStatus } from '@/types/user';
import type { UserStats, UserAsset, SignInfo, LatestSave, MemorySummary, EndingsList, RecentEndings } from '@/types/personal-center';

const router = useRouter();
const message = useMessage();

const userProfile = ref<UserProfile | null>(null);
const subscriptionStatus = ref<SubscriptionStatus | null>(null);
const stats = ref<UserStats | null>(null);
const asset = ref<UserAsset | null>(null);
const signInfo = ref<SignInfo | null>(null);
const latestSave = ref<LatestSave | null>(null);
const userAvatarFailed = ref(false);
const continueAvatarFailed = ref(false);
const memorySummary = ref<MemorySummary | null>(null);
const bondCharacters = ref<any[]>([]);
const bondOffset = ref(0);
const bondLimit = 10;
const bondTotal = ref(0);
const bondLoading = ref(false);
const bondNoMore = ref(false);
const bondListRef = ref<HTMLElement | null>(null);
const endingsList = ref<EndingsList | null>(null);
const recentEndings = ref<RecentEndings | null>(null);
const dialogueQuota = ref<{ used: number; total: number; is_subscriber: boolean; remaining?: number; lifecycle_stage?: string } | null>(null);

// CR-025 S017: 每日任务
const dailyTasks = ref<any[]>([]);
const showCelebration = ref(false);
const allTasksCompleted = computed(() => dailyTasks.value.length > 0 && dailyTasks.value.every(t => t.completed));
const allCompleteClaimed = ref(false);

async function loadDailyTasks() {
  try {
    const response = await gameApi.getDailyTasks();
    dailyTasks.value = response.tasks || [];
    allCompleteClaimed.value = response.all_complete_claimed || false;
  } catch (err) {
    console.error('Failed to load daily tasks:', err);
  }
}

async function claimTask(task: any) {
  try {
    await gameApi.claimDailyTask(task.id);
    message.success(`领取成功！+${task.reward_amount} 碎片`);
    await loadDailyTasks();
    await loadAsset();
  } catch (err: any) {
    message.error(err?.message || '领取失败');
  }
}

async function claimAllTasks() {
  try {
    await gameApi.claimAllDailyTasks();
    message.success('🎉 全完成奖励领取成功！+5 碎片');
    showCelebration.value = true;
    setTimeout(() => { showCelebration.value = false; }, 2000);
    await loadDailyTasks();
    await loadAsset();
  } catch (err: any) {
    message.error(err?.message || '领取失败');
  }
}

// FE-FEAT-025: 检查是否有分类记忆
const hasCategorizedMemories = computed(() => {
  return (memorySummary.value?.preferences?.length || 0) > 0 ||
         (memorySummary.value?.bonds?.length || 0) > 0 ||
         (memorySummary.value?.events?.length || 0) > 0;
});

const hasAnyMemories = computed(() => {
  return hasCategorizedMemories.value || (memorySummary.value?.recent?.length || 0) > 0;
});

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '';
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

function cleanEndingTitle(title: string | null | undefined): string {
  if (!title) return '';
  // 移除 "- good ending", "- bad ending" 等后缀
  return title.replace(/\s*-\s*(good|bad|normal|true|hidden)\s*ending/i, '').trim();
}

async function loadUserData() {
  try {
    const [profile, subscription] = await Promise.all([
      getMe(),
      getMySubscription(),
    ]);
    userProfile.value = profile;
    subscriptionStatus.value = subscription;
  } catch (error) {
    console.error('加载用户信息失败:', error);
    message.error('加载用户信息失败');
  }
}

async function loadStats() {
  try {
    stats.value = await getMyStats();
  } catch (error) {
    console.error('加载统计数据失败:', error);
  }
}

async function loadAsset() {
  try {
    asset.value = await getMyAsset();
  } catch (error) {
    console.error('加载资产信息失败:', error);
  }
}

async function loadSignInfo() {
  try {
    signInfo.value = await getSignInfo();
  } catch (error) {
    console.error('加载签到信息失败:', error);
  }
}

async function loadLatestSave() {
  try {
    latestSave.value = await getLatestSave();
  } catch (error) {
    console.error('加载存档信息失败:', error);
  }
}

async function loadMemorySummary() {
  try {
    memorySummary.value = await getMemorySummary();
  } catch (error) {
    console.error('加载记忆摘要失败:', error);
  }
}

function getAffectionLevelLabel(level: string): string {
  const levelMap: Record<string, string> = {
    acquaintance: '相识',
    ambiguous: '暧昧',
    trust: '信赖',
    bond: '羁绊',
    love: '挚友'
  };
  return levelMap[level] || level;
}

async function loadBondList(reset = false) {
  if (reset) {
    bondOffset.value = 0;
    bondCharacters.value = [];
    bondNoMore.value = false;
  }
  if (bondLoading.value || bondNoMore.value) return;
  
  bondLoading.value = true;
  try {
    const response = await getCharacterBond(bondOffset.value, bondLimit);
    bondTotal.value = response.total;
    bondCharacters.value = [...bondCharacters.value, ...response.characters];
    bondOffset.value += response.characters.length;
    bondNoMore.value = !response.has_more;
  } catch (error) {
    console.error('加载角色羁绊失败:', error);
  } finally {
    bondLoading.value = false;
  }
}

function handleBondScroll(e: Event) {
  const target = e.target as HTMLElement;
  const { scrollTop, scrollHeight, clientHeight } = target;
  // 滚动到底部时加载更多
  if (scrollTop + clientHeight >= scrollHeight - 50) {
    loadBondList();
  }
}

async function loadEndingsList() {
  try {
    endingsList.value = await getMyEndings();
  } catch (error) {
    console.error('加载结局列表失败:', error);
  }
}

async function loadRecentEndings() {
  try {
    recentEndings.value = await getRecentEndings();
  } catch (error) {
    console.error('加载最近结局失败:', error);
  }
}

async function loadDialogueQuota() {
  try {
    // CR-018 T-011: Use correct API path for quota status
    const response: any = await api.get('/cr016/dialogue/quota/status');
    dialogueQuota.value = {
      used: response.consumed || 0,
      total: response.is_exempt ? -1 : (response.base_quota || 10),
      remaining: response.remaining ?? (response.base_quota - response.consumed),
      is_subscriber: response.is_exempt || false,
      lifecycle_stage: response.lifecycle_stage || 'honeymoon'
    };
  } catch (error) {
    console.error('加载对话额度失败:', error);
  }
}

async function handleCheckin() {
  try {
    const response: any = await api.post('/daily/checkin');
    message.success(`签到成功！获得 ${response.fragments_earned} 碎片`);
    await loadSignInfo();
    await loadAsset(); // 刷新碎片余额
  } catch (error: any) {
    message.error(error?.message || '签到失败');
  }
}

function continueGame() {
  if (latestSave.value) {
    const sessionId = latestSave.value.session_id;
    const characterId = latestSave.value.character_id;
    // CR-032: 传递 character_id 确保继续游戏时角色正确
    router.push(`/game?session=${sessionId}${characterId ? `&character_id=${characterId}` : ''}`);
  }
}

onMounted(() => {
  loadUserData();
  loadStats();
  loadAsset();
  loadSignInfo();
  loadLatestSave();
  loadMemorySummary();
  loadBondList();
  loadEndingsList();
  loadRecentEndings();
  loadDialogueQuota();
  loadDailyTasks();
});
</script>

<style scoped>
.personal-center-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--text-main, #fff);
  display: flex;
  align-items: center;
  gap: 8px;
}

.tooltip-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(167, 139, 250, 0.2);
  color: #a78bfa;
  font-size: 12px;
  font-weight: 700;
  cursor: help;
  transition: all 0.2s;
}

.tooltip-icon:hover {
  background: rgba(167, 139, 250, 0.3);
  transform: scale(1.1);
}

/* 用户信息卡片 */
.user-info-card {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #a78bfa, #f472b6);
  color: white;
  font-size: 32px;
  font-weight: 700;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: var(--text-main, #fff);
}

.user-email {
  font-size: 14px;
  color: var(--text-muted, #9ca3af);
  margin: 0 0 12px 0;
}

.user-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(156, 163, 175, 0.2);
  color: var(--text-muted, #9ca3af);
}

.badge.premium {
  background: rgba(251, 191, 36, 0.2);
  color: #fbbf24;
}

.badge.standard {
  background: rgba(167, 139, 250, 0.2);
  color: #a78bfa;
}

.badge.email-verified {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

/* 碎片资产卡片 */
.asset-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.asset-balance {
  text-align: center;
}

.balance-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
}

.balance-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
  margin-top: 4px;
}

.asset-stats {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.asset-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.asset-stat .stat-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

.asset-stat .stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #fff);
}

/* 签到卡片 */
.checkin-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkin-info {
  display: flex;
  justify-content: space-around;
}

.streak-days,
.total-checkins,
.total-fragments {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.streak-value,
.total-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
}

.streak-label,
.total-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

.checkin-week {
  display: flex;
  justify-content: space-around;
  gap: 8px;
}

.week-day {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted, #9ca3af);
}

.week-day.checked {
  background: #22c55e;
  color: white;
}

/* 继续游玩卡片 */
.continue-content {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
}

.continue-character {
  flex-shrink: 0;
}

.continue-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(236, 72, 153, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px solid rgba(167, 139, 250, 0.3);
}

.continue-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.continue-avatar span {
  font-size: 24px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
}

.save-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.script-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main, #fff);
}

.character-name {
  font-size: 14px;
  color: var(--text-muted, #9ca3af);
}

.save-time {
  font-size: 12px;
  color: var(--text-subtle, #6b7280);
}

/* AI 记忆卡片 */
.memory-card {
  grid-column: 1 / -1;
}

.memory-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-summary {
  text-align: center;
}

.memory-count {
  font-size: 36px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
}

.memory-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
  margin-left: 4px;
}

.recent-memories {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.memory-categories {
  max-height: 320px;
  overflow-y: auto;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.memory-item {
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.memory-character {
  font-size: 12px;
  font-weight: 600;
  color: var(--brand-primary, #a78bfa);
  margin-bottom: 4px;
}

.memory-text {
  font-size: 13px;
  color: var(--text-main, #fff);
  line-height: 1.5;
}

/* 角色羁绊卡片 */
.bond-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 320px;
  overflow-y: auto;
}

.bond-list::-webkit-scrollbar {
  width: 4px;
}

.bond-list::-webkit-scrollbar-thumb {
  background: rgba(167, 139, 250, 0.3);
  border-radius: 2px;
}

.bond-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  color: var(--text-muted, #9ca3af);
  font-size: 13px;
}

.bond-no-more {
  text-align: center;
  padding: 12px;
  color: var(--text-muted, #9ca3af);
  font-size: 13px;
}

.bond-list::-webkit-scrollbar-track {
  background: transparent;
}

.bond-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.bond-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #f472b6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  flex-shrink: 0;
}

.bond-info {
  flex: 1;
}

.bond-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #fff);
}

.bond-level {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

.bond-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-primary, #a78bfa);
}

/* 结局追踪卡片 */
.endings-summary {
  text-align: center;
  margin-bottom: 16px;
}

.endings-count {
  font-size: 36px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
}

.endings-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
  margin-left: 4px;
}

.endings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.ending-script {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #fff);
}

.ending-progress {
  font-size: 14px;
  font-weight: 600;
  color: var(--brand-primary, #a78bfa);
}

/* 新解锁结局滚动 */
.recent-endings-scroll {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 240px;
  overflow-y: auto;
  padding-right: 4px;
}

.recent-endings-scroll::-webkit-scrollbar {
  width: 4px;
}

.recent-endings-scroll::-webkit-scrollbar-thumb {
  background: rgba(167, 139, 250, 0.3);
  border-radius: 2px;
}

.recent-ending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
}

.ending-info {
  flex: 1;
}

.ending-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main, #fff);
  margin-bottom: 4px;
}

.ending-meta {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

.ending-type {
  align-self: flex-start;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.ending-type.good {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.ending-type.bad {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}
/* 对话额度卡片 */
.quota-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.quota-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.quota-used,
.quota-total {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.quota-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand-primary, #a78bfa);
}

.quota-label {
  font-size: 12px;
  color: var(--text-muted, #9ca3af);
}

.quota-separator {
  font-size: 24px;
  color: var(--text-muted, #9ca3af);
  font-weight: 300;
}

.quota-progress {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #f472b6);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-bar.warning {
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
}

.quota-hint {
  text-align: center;
  font-size: 13px;
  color: var(--text-muted, #9ca3af);
}

@media (max-width: 768px) {
  .personal-center-page {
    grid-template-columns: 1fr;
  }
  
  .user-info-card {
    flex-direction: column;
    text-align: center;
  }
  
  .user-badges {
    justify-content: center;
  }
}

/* CR-025 S017: 每日任务卡片样式 */
.daily-tasks-card {
  margin-top: 16px;
}

.card-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.card-header .card-title {
  margin: 0;
  justify-self: start;
}

.reset-info {
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  justify-self: center;
}

.all-complete-btn {
  justify-self: end;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.task-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 6px;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  min-width: 40px;
}

.task-reward {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  min-width: 70px;
}

.reward-amount {
  font-size: 12px;
  font-weight: 600;
  color: #fbbf24;
}

.celebration-content {
  text-align: center;
  padding: 20px;
}

.celebration-emoji {
  font-size: 64px;
  animation: bounce 0.5s ease-in-out infinite alternate;
}

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-10px); }
}
</style>

<template>
  <div class="personal-center-page">
    <!-- 用户信息卡片 -->
    <div class="user-info-card glass-card">
      <div class="user-avatar" @click="toggleAvatarMenu">
        <img v-if="userProfile?.avatar_url && !userAvatarFailed" :src="userProfile.avatar_url" :alt="userProfile.display_name || t('personalCenter.defaultUser')" @error="userAvatarFailed = true" />
        <div v-else class="avatar-placeholder">
          {{ (userProfile?.display_name || 'U').charAt(0).toUpperCase() }}
        </div>
        <div class="avatar-dropdown" v-if="showAvatarMenu" @click.stop>
          <div class="dropdown-item" @click="goToSettings">⚙️ {{ $t('personalCenter.settings') }}</div>
          <div class="dropdown-item logout" @click="handleLogout">🚪 {{ $t('personalCenter.logout') }}</div>
        </div>
      </div>
      <div class="user-info">
        <h2 class="user-name">{{ userProfile?.display_name || $t('personalCenter.defaultUser') }}</h2>
        <p class="user-email">{{ userProfile?.email || '' }}</p>
        <div class="user-badges">
          <span class="badge" :class="subscriptionStatus?.tier || 'free'">
            {{ subscriptionStatus?.tier === 'premium' ? $t('personalCenter.premiumMember') : subscriptionStatus?.tier === 'standard' ? $t('personalCenter.standardMember') : $t('personalCenter.freeUser') }}
          </span>
          <span class="badge email-verified" v-if="userProfile?.email_verified">✓ {{ $t('personalCenter.verified') }}</span>
        </div>
      </div>
    </div>

    <!-- 会员卡区域 -->
    <div class="membership-card glass-card">
      <div class="membership-header">
        <span class="membership-tier" :class="subscriptionStatus?.tier || 'free'">
          {{ subscriptionStatus?.tier === 'premium' ? $t('personalCenter.premiumMemberIcon') : subscriptionStatus?.tier === 'standard' ? $t('personalCenter.standardMemberIcon') : $t('personalCenter.freeUserIcon') }}
        </span>
        <span class="membership-status" :class="subscriptionStatus?.status">
          {{ subscriptionStatus?.status === 'active' ? $t('personalCenter.statusActive') : subscriptionStatus?.status === 'cancelled' ? $t('personalCenter.statusCancelled') : $t('personalCenter.statusExpired') }}
        </span>
      </div>
      <div class="membership-details">
        <div class="detail-row">
          <span class="detail-label">{{ $t('personalCenter.expiresAt') }}</span>
          <span class="detail-value">{{ subscriptionStatus?.expires_at ? formatDate(subscriptionStatus.expires_at) : $t('personalCenter.permanent') }}</span>
        </div>
        <div v-if="subscriptionStatus?.pending_tier" class="detail-row pending-downgrade">
          <span class="detail-label">{{ $t('personalCenter.pendingDowngrade') }}</span>
          <span class="detail-value">→ {{ tierLabel(subscriptionStatus.pending_tier) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">{{ $t('personalCenter.fragmentBalance') }}</span>
          <span class="detail-value">💎 {{ asset?.balance || 0 }}</span>
        </div>
      </div>
      <div class="membership-actions">
        <n-button type="primary" size="small" @click="router.push('/subscribe')">
          {{ subscriptionStatus?.tier === 'free' ? $t('personalCenter.upgradeMember') : $t('personalCenter.renew') }}
        </n-button>
        <n-button size="small" @click="router.push('/fragment')">
          {{ $t('personalCenter.fragmentMall') }}
        </n-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.gameStats') }}</h3>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-value">{{ stats?.scripts_completed || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.scriptsCompleted') }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_play_time_minutes || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.playTimeMinutes') }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.endings_unlocked || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.endingsUnlocked') }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.cgs_collected || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.cgsCollected') }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_dialogues || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.totalDialogues') }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ stats?.total_choices || 0 }}</div>
          <div class="stat-label">{{ $t('personalCenter.totalChoices') }}</div>
        </div>
        <!-- CR-028: 扮演角色数 -->
        <div class="stat-item" v-if="stats?.characters_played !== undefined">
          <div class="stat-value">{{ stats.characters_played }}</div>
          <div class="stat-label">{{ $t('personalCenter.charactersPlayed') }}</div>
        </div>
      </div>
    </div>

    <!-- 对话额度卡片 -->
    <div class="quota-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.dailyQuota') }}</h3>
      <div class="quota-content">
        <div class="quota-display">
          <div class="quota-used">
            <span class="quota-value">{{ dialogueQuota?.used || 0 }}</span>
            <span class="quota-label">{{ $t('personalCenter.used') }}</span>
          </div>
          <div class="quota-separator">/</div>
          <div class="quota-total">
            <span class="quota-value" v-if="dialogueQuota?.total === -1">{{ $t('personalCenter.unlimitedQuota') }}</span>
            <span class="quota-value" v-else>{{ dialogueQuota?.total || 0 }}</span>
            <span class="quota-label" v-if="dialogueQuota?.total !== -1">{{ $t('personalCenter.totalQuota') }}</span>
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
          <span v-if="dialogueQuota.is_subscriber">{{ $t('personalCenter.subscriberUnlimited') }}</span>
          <span v-else>{{ $t('personalCenter.remainingDialogues', { n: dialogueQuota.total - dialogueQuota.used }) }}</span>
        </div>
      </div>
    </div>

    <!-- 碎片资产卡片 -->
    <div class="asset-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.fragmentAssets') }}</h3>
      <div class="asset-content">
        <div class="asset-balance">
          <div class="balance-value">{{ asset?.balance || 0 }}</div>
          <div class="balance-label">{{ $t('personalCenter.currentBalance') }}</div>
        </div>
        <div class="asset-stats">
          <div class="asset-stat">
            <span class="stat-label">{{ $t('personalCenter.totalEarned') }}</span>
            <span class="stat-value">{{ asset?.total_earned || 0 }}</span>
          </div>
          <div class="asset-stat">
            <span class="stat-label">{{ $t('personalCenter.totalSpent') }}</span>
            <span class="stat-value">{{ asset?.total_spent || 0 }}</span>
          </div>
        </div>
        <n-button type="primary" size="small" @click="router.push('/subscribe')">
          {{ $t('personalCenter.rechargeFragments') }}
        </n-button>
      </div>
    </div>

    <!-- 签到卡片 -->
    <div class="checkin-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.dailyCheckin') }}</h3>
      <div class="checkin-content">
        <div class="checkin-info">
          <div class="streak-days">
            <span class="streak-value">{{ signInfo?.streak_days || 0 }}</span>
            <span class="streak-label">{{ $t('personalCenter.streakDays') }}</span>
          </div>
          <div class="total-checkins">
            <span class="total-value">{{ signInfo?.total_checkins || 0 }}</span>
            <span class="total-label">{{ $t('personalCenter.totalCheckins') }}</span>
          </div>
          <div class="total-fragments">
            <span class="total-value">{{ signInfo?.total_fragments || 0 }}</span>
            <span class="total-label">{{ $t('personalCenter.totalFragmentsEarned') }}</span>
          </div>
        </div>
        <div class="checkin-week">
          <div 
            v-for="(checked, index) in signInfo?.this_week || []" 
            :key="index"
            class="week-day"
            :class="{ checked }"
          >
            {{ $t('personalCenter.weekDays').split(',')[index] }}
          </div>
        </div>
        <n-button 
          type="primary" 
          size="small" 
          :disabled="signInfo?.checked_in_today"
          @click="handleCheckin"
        >
          {{ signInfo?.checked_in_today ? $t('personalCenter.checkedInToday') : $t('personalCenter.checkinNow') }}
        </n-button>
      </div>
    </div>

    <!-- CR-025 S017: 每日任务卡片 -->
    <div class="daily-tasks-card glass-card">
      <div class="card-header">
        <h3 class="card-title">{{ $t('personalCenter.dailyTasks') }}</h3>
        <div class="reset-info">{{ $t('personalCenter.resetDaily') }}</div>
        <div class="all-complete-btn">
          <n-button
            v-if="allTasksCompleted && !allCompleteClaimed"
            type="success"
            size="small"
            @click="claimAllTasks"
          >
            {{ $t('personalCenter.allCompleteReward') }}
          </n-button>
          <n-tag v-else-if="allCompleteClaimed" type="success" size="small">{{ $t('personalCenter.claimed') }}</n-tag>
          <n-button v-else size="small" disabled>{{ $t('personalCenter.allCompleteReward') }}</n-button>
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
              {{ $t('personalCenter.claim') }}
            </n-button>
            <n-tag v-else-if="task.claimed" type="success" size="small">{{ $t('personalCenter.claimed') }}</n-tag>
            <n-button 
              v-else 
              size="tiny" 
              :disabled="true"
            >
              {{ $t('personalCenter.claim') }}
            </n-button>
          </div>
        </div>
        <n-empty v-if="dailyTasks.length === 0" :description="$t('personalCenter.noTasks')" />
      </div>
    </div>

    <!-- 继续游玩卡片 -->
    <div class="continue-card glass-card" v-if="latestSave">
      <h3 class="card-title">{{ $t('personalCenter.continuePlaying') }}</h3>
      <div class="continue-content">
        <!-- CR-028: 角色头像展示 -->
        <div v-if="latestSave.character_avatar || latestSave.character_name" class="continue-character">
          <div class="continue-avatar">
            <img v-if="latestSave.character_avatar && !continueAvatarFailed" :src="latestSave.character_avatar" :alt="latestSave.character_name || t('personalCenter.defaultCharacter')" @error="continueAvatarFailed = true" />
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
          {{ $t('personalCenter.continueGame') }}
        </n-button>
      </div>
    </div>

    <!-- 角色羁绊卡片 -->
    <div class="bond-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.characterBonds') }}</h3>
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
          <span>{{ $t('personalCenter.loading') }}</span>
        </div>
        <div v-if="bondNoMore && bondCharacters.length > 0" class="bond-no-more">
          {{ $t('personalCenter.noMore') }}
        </div>
        <n-empty v-if="!bondLoading && bondCharacters.length === 0" :description="$t('personalCenter.noBonds')" />
      </div>
    </div>

    <!-- 结局追踪卡片 -->
    <div class="endings-card glass-card">
      <h3 class="card-title">{{ $t('personalCenter.endingTracking') }}</h3>
      <div class="endings-summary">
        <span class="endings-count">{{ endingsList?.total_endings_unlocked || 0 }}</span>
        <span class="endings-label">{{ $t('personalCenter.endingsUnlockedCount') }}</span>
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
      <n-empty v-else :description="$t('personalCenter.noEndings')" />
    </div>

    <!-- 新解锁结局卡片 -->
    <div class="continue-card glass-card" v-if="recentEndings?.recent_endings && recentEndings.recent_endings.length > 0">
      <h3 class="card-title">{{ $t('personalCenter.newEndings') }}</h3>
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
            {{ ending.ending_type === 'good' ? $t('personalCenter.goodEnding') : ending.ending_type === 'bad' ? $t('personalCenter.badEnding') : ending.ending_type }}
          </div>
        </div>
      </div>
    </div>

    <!-- AI 记忆卡片 -->
    <div class="memory-card glass-card">
      <h3 class="card-title">
        {{ $t('personalCenter.aiMemory') }}
        <span class="tooltip-icon" :title="t('personalCenter.aiMemoryTooltip')">?</span>
      </h3>
      <div class="memory-content">
        <div class="memory-summary">
          <span class="memory-count">{{ memorySummary?.total_memories || 0 }}</span>
          <span class="memory-label">{{ $t('personalCenter.memoryCount') }}</span>
        </div>
        
        <!-- FE-FEAT-025: 分类展示记忆 -->
        <div class="memory-categories">
          <!-- 用户偏好 -->
          <div class="memory-category" v-if="memorySummary?.preferences && memorySummary.preferences.length > 0">
            <h4 class="category-title">{{ $t('personalCenter.userPreferences') }} ({{ memorySummary.preferences.length }})</h4>
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
            <h4 class="category-title">{{ $t('personalCenter.characterBondsMemory') }} ({{ memorySummary.bonds.length }})</h4>
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
            <h4 class="category-title">{{ $t('personalCenter.importantEvents') }} ({{ memorySummary.events.length }})</h4>
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
        
        <n-empty v-if="!hasAnyMemories" :description="$t('personalCenter.noMemories')" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage, NButton, NEmpty } from 'naive-ui';
import { api } from '@/api/http';
import { gameApi } from '@/api/game';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import { getMe, getMyStats, getMyAsset, getSignInfo, getLatestSave, getMemorySummary, getCharacterBond, getMyEndings, getRecentEndings } from '@/api/user';
import { useSubscriptionStore } from '@/stores/subscription';
import type { UserProfile, SubscriptionStatus } from '@/types/user';
import type { UserStats, UserAsset, SignInfo, LatestSave, MemorySummary, EndingsList, RecentEndings } from '@/types/personal-center';

const router = useRouter();
const message = useMessage();
const { t } = useI18n();
const authStore = useAuthStore();
const subscriptionStore = useSubscriptionStore();

// Avatar dropdown menu
const showAvatarMenu = ref(false);

const toggleAvatarMenu = () => {
  showAvatarMenu.value = !showAvatarMenu.value;
};

const goToSettings = () => {
  showAvatarMenu.value = false;
  router.push('/settings');
};

const handleLogout = () => {
  showAvatarMenu.value = false;
  authStore.logout();
  router.push('/login');
};

// Close avatar menu when clicking outside
const closeAvatarMenu = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (!target.closest('.user-avatar')) {
    showAvatarMenu.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', closeAvatarMenu);
});

onUnmounted(() => {
  document.removeEventListener('click', closeAvatarMenu);
});

// Format date helper — uses existing formatDate function defined below

function tierLabel(tier: string): string {
  const labels: Record<string, string> = {
    free: t('personalCenter.tierFree'),
    basic: t('personalCenter.tierBasic'),
    standard: t('personalCenter.tierStandard'),
    premium: t('personalCenter.tierPremium'),
  };
  return labels[tier] || tier;
}

const userProfile = ref<UserProfile | null>(null);
// Subscription status from store (calls /cr016/subscription/status)
const subscriptionStatus = computed(() => subscriptionStore.subscriptionStatus);
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
    message.success(t('personalCenter.claimSuccess', { n: task.reward_amount }));
    await loadDailyTasks();
    await loadAsset();
  } catch (err: any) {
    message.error(err?.message || t('personalCenter.claimFailed'));
  }
}

async function claimAllTasks() {
  try {
    await gameApi.claimAllDailyTasks();
    message.success(t('personalCenter.allCompleteSuccess'));
    showCelebration.value = true;
    setTimeout(() => { showCelebration.value = false; }, 2000);
    await loadDailyTasks();
    await loadAsset();
  } catch (err: any) {
    message.error(err?.message || t('personalCenter.claimFailed'));
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
    // Load profile and subscription status separately — one failing should not block the other
    const profilePromise = getMe().catch(err => {
      console.error('加载用户信息失败:', err);
      return null;
    });
    const subPromise = subscriptionStore.fetchSubscriptionStatus().catch(err => {
      console.error('加载订阅状态失败:', err);
    });
    const [profile] = await Promise.all([profilePromise, subPromise]);
    if (profile) userProfile.value = profile;
  } catch (error) {
    console.error('加载用户数据失败:', error);
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
    acquaintance: t('personalCenter.affectionAcquaintance'),
    ambiguous: t('personalCenter.affectionAmbiguous'),
    trust: t('personalCenter.affectionTrust'),
    bond: t('personalCenter.affectionBond'),
    love: t('personalCenter.affectionLove')
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
    message.success(t('personalCenter.checkinSuccess', { n: response.fragments_earned }));
    await loadSignInfo();
    await loadAsset(); // 刷新碎片余额
  } catch (error: any) {
    message.error(error?.message || t('personalCenter.checkinFailed'));
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
.user-avatar {
  position: relative;
  cursor: pointer;
}

.avatar-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  background: rgba(30, 20, 50, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 8px;
  min-width: 120px;
  z-index: 100;
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 16px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: rgba(102, 126, 234, 0.2);
}

.dropdown-item.logout {
  color: rgba(255, 100, 100, 0.9);
}

.membership-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.membership-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.membership-tier {
  font-size: 18px;
  font-weight: 600;
}

.membership-tier.premium { color: #fbbf24; }
.membership-tier.standard { color: #667eea; }
.membership-tier.basic { color: #a78bfa; }
.membership-tier.free { color: rgba(255, 255, 255, 0.6); }
.membership-status.expired { color: rgba(255, 255, 255, 0.4); }

.pending-downgrade {
  margin-top: 4px;
  padding: 8px 12px;
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 8px;
  font-size: 13px;
}
.pending-downgrade .detail-label { color: rgba(251, 191, 36, 0.8); }
.pending-downgrade .detail-value { color: #fbbf24; font-weight: 600; }

.membership-status.active { color: #4ade80; }
.membership-status.cancelled { color: #f87171; }
.membership-status.expired { color: #9ca3af; }

.membership-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

.detail-value {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.membership-actions {
  display: flex;
  gap: 8px;
}

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

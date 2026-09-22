<template>
  <div class="script-detail-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('scriptDetail.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>{{ $t('scriptDetail.loadFailed') }}</h3>
      <p>{{ error }}</p>
      <button class="cta-secondary" @click="loadScript">{{ $t('scriptDetail.retry') }}</button>
    </div>

    <!-- Main Content -->
    <div v-else-if="scriptDetail" class="script-content">
      <!-- Header with Back Button -->
      <header class="detail-header">
        <button class="back-button" @click="router.back()">
          <span class="back-icon">🔙</span>
          <span>{{ $t('scriptDetail.back') }}</span>
        </button>
      </header>

      <!-- 1. Hero Section -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="hero-cover">
            <img v-if="scriptDetail.cover" :src="scriptDetail.cover" :alt="scriptDetail.title" class="cover-image" />
            <div v-else class="cover-gradient">
              <span class="cover-emoji">📖</span>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="hero-info">
            <h1 class="script-title">{{ scriptDetail.title }}</h1>
            <p class="script-author">{{ $t('scriptDetail.author') }}：{{ scriptDetail.author }}</p>
            <p class="script-description">{{ scriptDetail.description }}</p>

            <!-- FE-FEAT-023: 展示路线和结局数量 -->
            <div class="script-stats">
              <div class="stat-badge">
                <span class="stat-icon">🗺️</span>
                <span class="stat-text">{{ routeChapters.length }} {{ $t('scriptDetail.routes') }}</span>
              </div>
              <div class="stat-badge">
                <span class="stat-icon">🏆</span>
                <span class="stat-text">{{ unlockedEndings.length + lockedEndingCount }} {{ $t('scriptDetail.endings') }}</span>
              </div>
              <div class="stat-badge">
                <span class="stat-icon">👥</span>
                <span class="stat-text">{{ characters.length }} {{ $t('scriptDetail.characters') }}</span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress-section">
              <div class="progress-header">
                <span class="progress-label">{{ $t('scriptDetail.completionProgress') }}</span>
                <span class="progress-percentage">{{ scriptDetail.completionRate }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${scriptDetail.completionRate}%` }"></div>
              </div>
              <div class="progress-stats">
                <span>{{ $t('scriptDetail.unlockedNodes') }}：{{ scriptDetail.unlockedNodes }}/{{ scriptDetail.totalNodes }}</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="hero-actions">
              <button class="cta-primary" @click="startGame">
                {{ startGameButtonText }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. Character Selection Section (CR-028: integrated playable badges + lock overlay) -->
      <section class="character-selection-section">
        <h2 class="section-title">{{ $t('scriptDetail.characterGuide') }}</h2>
        <p v-if="playableCharacters.length > 0" class="section-desc">{{ $t('scriptDetail.characterSelectHint') }}</p>
        <div class="character-grid">
          <CharacterDetailCard
            v-for="character in characters"
            :key="character.id"
            :character="character"
            :isSelected="isCharacterSelected(character.id)"
            :isPlayable="isCharacterPlayable(character.id)"
            :isUnlocked="isCharacterUnlocked(character.id)"
            :unlockType="getCharacterUnlockType(character.id)"
            :unlockPrice="getCharacterUnlockPrice(character.id)"
            @select="handleCharacterSelect(character.id)"
          />
        </div>
      </section>

      <!-- CR-028: 锁定角色解锁弹窗 -->
      <LockedCharacterOverlay
        :visible="showLockedOverlay"
        :character="lockedCharacter"
        @close="closeLockedOverlay"
        @unlock="handleUnlockCharacter"
      />

      <!-- CR-038: Corvus player candidate selection modal -->
      <PlayerCandidateModal
        v-model="showCandidateModal"
        :script-id="scriptId"
        :script-characters="characters"
        @selected="handleCandidateSelected"
      />

      <!-- 3. Route Tree Section -->
      <section class="route-tree-section">
        <h2 class="section-title">{{ $t('scriptDetail.routeExploration') }}</h2>
        <RouteTree :chapters="routeChapters" @chapter-click="handleChapterClick" />
      </section>

      <!-- 4. Ending List Section -->
      <section class="ending-list-section">
        <h2 class="section-title">{{ $t('scriptDetail.endingCollection') }}</h2>
        <EndingList :chapter-endings="chapterEndings" :locked-count="lockedEndingCount" />
      </section>

      <!-- 5. CG Preview Grid Section -->
      <section class="cg-preview-section">
        <h2 class="section-title">{{ $t('scriptDetail.cgPreview') }}</h2>
        <CGPreviewGrid :cgs="cgPreviews" />
      </section>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📖</div>
      <h3>{{ $t('scriptDetail.scriptNotFound') }}</h3>
      <p>{{ $t('scriptDetail.scriptNotFoundDesc') }}</p>
      <button class="cta-secondary" @click="router.push('/discover')">
        {{ $t('scriptDetail.backToLobby') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/api/http';
import CharacterDetailCard from '@/components/CharacterDetailCard.vue';
import RouteTree from '@/components/RouteTree.vue';
import EndingList from '@/components/EndingList.vue';
import CGPreviewGrid from '@/components/CGPreviewGrid.vue';
import LockedCharacterOverlay from '@/components/LockedCharacterOverlay.vue';
import PlayerCandidateModal from '@/components/PlayerCandidateModal.vue';
import type { PlayableCharacter } from '@/components/LockedCharacterOverlay.vue';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const auth = useAuthStore();

const scriptId = route.params.scriptId as string;
const loading = ref(true);
const error = ref<string | null>(null);
const scriptDetail = ref<any>(null);

// 角色选择相关
const characters = ref<any[]>([]);
const selectedCharacterId = ref<string | null>(null);

// CR-028: 可扮演角色相关（集成到角色图鉴）
const playableCharacters = ref<PlayableCharacter[]>([]);
const selectedPlayableCharacterId = ref<string | null>(null);
const showLockedOverlay = ref(false);
const lockedCharacter = ref<PlayableCharacter | null>(null);

// CR-038: Candidate selection flow
const showCandidateModal = ref(false);

// CR-038: Handle candidate selection from PlayerCandidateModal
// CR-039 T-039-FE-002: 传递 initial_scene 到 GameView
function handleCandidateSelected(sessionId: string, initialScene?: any) {
  if (initialScene) {
    sessionStorage.setItem(`corvus_initial_scene_${sessionId}`, JSON.stringify(initialScene));
  }
  // Navigate to game page with the Corvus session
  router.push(`/game?session=${sessionId}`);
}

// 路线树相关
const routeChapters = ref<any[]>([]);

// 结局列表相关（按章节分组）
const chapterEndings = ref<any[]>([]);
const unlockedEndings = ref<any[]>([]);
const lockedEndingCount = ref(0);

// CG预览相关
const cgPreviews = ref<any[]>([]);

// FE-FEAT-023: 统计数据
const routesCount = ref(0);
const endingsCount = ref(0);

// CR-028: 角色图鉴集成可扮演逻辑
function isCharacterPlayable(characterId: string): boolean {
  return playableCharacters.value.some(c => c.id === characterId);
}

function isCharacterUnlocked(characterId: string): boolean {
  const pc = playableCharacters.value.find(c => c.id === characterId);
  return pc ? pc.is_unlocked : false;
}

function getCharacterUnlockType(characterId: string): string {
  const pc = playableCharacters.value.find(c => c.id === characterId);
  return pc ? pc.unlock_type : 'free';
}

function getCharacterUnlockPrice(characterId: string): number | null | undefined {
  const pc = playableCharacters.value.find(c => c.id === characterId);
  return pc ? pc.unlock_price : undefined;
}

function isCharacterSelected(characterId: string): boolean {
  return selectedPlayableCharacterId.value === characterId;
}

function handleCharacterSelect(characterId: string) {
  // 检查是否可扮演角色
  const playableChar = playableCharacters.value.find(c => c.id === characterId);
  if (playableChar) {
    if (!playableChar.is_unlocked) {
      // 锁定角色，显示解锁弹窗
      lockedCharacter.value = playableChar;
      showLockedOverlay.value = true;
      return;
    }
    // 已解锁角色，切换选中状态
    if (selectedPlayableCharacterId.value === characterId) {
      selectedPlayableCharacterId.value = null;
    } else {
      selectedPlayableCharacterId.value = characterId;
    }
  } else {
    // 非可扮演角色，仅更新图鉴选中状态（原有逻辑）
    selectedCharacterId.value = characterId;
  }
}

// CR-028: 关闭锁定弹窗
function closeLockedOverlay() {
  showLockedOverlay.value = false;
  lockedCharacter.value = null;
}

// CR-028: 解锁角色
async function handleUnlockCharacter(characterId: string) {
  try {
    await api.post(`/characters/${characterId}/unlock`);
    // 解锁成功后更新本地状态
    const char = playableCharacters.value.find(c => c.id === characterId);
    if (char) {
      char.is_unlocked = true;
    }
    // 关闭弹窗并自动选中
    showLockedOverlay.value = false;
    lockedCharacter.value = null;
    selectedPlayableCharacterId.value = characterId;
  } catch (err) {
    console.error('解锁角色失败:', err);
    throw err;
  }
}

// CR-028: 开始游戏按钮文案
const startGameButtonText = computed(() => {
  if (selectedPlayableCharacterId.value) {
    const selectedChar = playableCharacters.value.find(c => c.id === selectedPlayableCharacterId.value);
    if (selectedChar) {
      return t('scriptDetail.startGameAs', { name: selectedChar.name });
    }
  }
  return t('scriptDetail.startGameDefault');
});

function startGame() {
  if (!auth.isAuthenticated) {
    router.push(`/login?redirect=/scripts/${scriptId}`);
    return;
  }

  // CR-038: For Corvus engine scripts, show candidate selection modal
  // instead of directly navigating to /game
  // Use the scriptDetail response which contains engine_type from GET /scripts/{id}
  const isCorvus = (scriptDetail.value as any)?.engine_type === 'corvus';
  
  if (isCorvus) {
    // Show PlayerCandidateModal for Corvus scripts
    showCandidateModal.value = true;
    return;
  }

  // Legacy flow: navigate directly to /game
  const characterId = selectedPlayableCharacterId.value;
  const currentChapter = routeChapters.value.find(ch => ch.isCurrent);
  if (currentChapter) {
    const routeParam = `&route=${currentChapter.routeId}`;
    const charParam = characterId ? `&character_id=${characterId}` : '';
    router.push(`/game?script=${scriptId}${routeParam}${charParam}`);
  } else {
    const charParam = characterId ? `&character_id=${characterId}` : '';
    router.push(`/game?script=${scriptId}${charParam}`);
  }
}

function handleChapterClick(chapter: any) {
  if (!auth.isAuthenticated) {
    router.push(`/login?redirect=/scripts/${scriptId}`);
    return;
  }
  // 从指定章节开始游戏
  router.push(`/game?script=${scriptId}&route=${chapter.routeId || chapter.id}`);
}

async function loadScript() {
  loading.value = true;
  error.value = null;

  try {
    // FE-FEAT-023: 调用正确的后端接口 GET /scripts/{script_id}
    const response = await api.get<any>(`/scripts/${scriptId}`);
    
    // 构建 scriptDetail 对象
    scriptDetail.value = {
      scriptId: response.id,
      title: response.title,
      description: response.description,
      cover: response.cover_image_url,
      author: response.author || t('scriptDetail.defaultAuthor'),
      completionRate: response.completionRate || 0,
      unlockedNodes: response.unlockedNodes || 0,
      totalNodes: response.totalNodes || 0,
      engine_type: response.engine_type || 'legacy', // CR-038: store engine_type
    };
    
    // FE-FEAT-023: 更新统计数据
    routesCount.value = response.routes_count || 0;
    endingsCount.value = response.endings_count || 0;
    
    // 角色数据
    if (response.characters && Array.isArray(response.characters)) {
      characters.value = response.characters;
    } else {
      characters.value = [];
    }
    
    // CR-028: 可扮演角色数据
    if (response.playable_characters && Array.isArray(response.playable_characters)) {
      playableCharacters.value = response.playable_characters.map((c: any) => ({
        id: c.id,
        name: c.name,
        avatar_url: c.avatar_url,
        play_description: c.play_description,
        unlock_type: c.unlock_type || 'free',
        unlock_price: c.unlock_price,
        is_unlocked: c.is_unlocked ?? false,
      }));
    } else {
      playableCharacters.value = [];
    }
    // 重置选中状态
    selectedPlayableCharacterId.value = null;
    
    // 路线数据 - 转换为 RouteTree 需要的格式
    if (response.routes && Array.isArray(response.routes)) {
      routeChapters.value = response.routes.map((route: any, index: number) => {
        // 优先使用 chapter_type_label（和游戏内一致），fallback 到 route.title
        const chapterLabel = route.chapter_type_label || route.title || t('scriptDetail.chapterPrefix', { n: index + 1 });
        const chapterNum = route.chapter_number || index + 1;
        const title = route.chapter_type_label ? t('scriptDetail.chapterTitle', { n: chapterNum, title: chapterLabel }) : chapterLabel;
        return {
          id: route.id,
          routeId: route.id,
          title: title,
          description: route.description,
          isCompleted: route.is_completed || false,
          isCurrent: route.is_unlocked && !route.is_completed, // 已解锁但未完成 = 当前章节
          isLocked: !route.is_unlocked,
          lockReason: !route.is_unlocked ? t('scriptDetail.locked') : '',
        };
      });
    } else {
      routeChapters.value = [];
    }
    
    // 结局数据 - 按章节分组，每章一个结局（展示解锁状态）
    // 使用 route_id 作为 chapterMap 的 key，避免 title 重复或 fallback 不一致导致重复章节
    if (response.endings && Array.isArray(response.endings)) {
      // 构建 route_id → route info 映射
      const routeInfoMap = new Map<string, { title: string; index: number }>();
      if (response.routes && Array.isArray(response.routes)) {
        response.routes.forEach((route: any, index: number) => {
          routeInfoMap.set(route.id, {
            title: route.title || t('scriptDetail.chapterPrefix', { n: index + 1 }),
            index: index
          });
        });
      }
      
      // 用 route_id 作为 key 分组结局
      const chapterMap = new Map<string, {
        chapter: string;
        chapterIndex: number;
        endings: any[];
        hasUnlocked: boolean;
      }>();
      
      // 先初始化所有章节（用 route_id 作为 key）
      if (response.routes && Array.isArray(response.routes)) {
        response.routes.forEach((route: any, index: number) => {
          chapterMap.set(route.id, {
            chapter: route.title || t('scriptDetail.chapterPrefix', { n: index + 1 }),
            chapterIndex: index,
            endings: [],
            hasUnlocked: false
          });
        });
      }
      
      // 填充结局数据
      response.endings.forEach((ending: any) => {
        const isUnlocked = ending.unlocked || ending.is_unlocked || false;
        const routeId = ending.route_id;
        
        if (routeId && chapterMap.has(routeId)) {
          // 正常情况：route_id 匹配到已知 route
          const chapterData = chapterMap.get(routeId)!;
          chapterData.endings.push({
            id: ending.id,
            name: ending.title,
            type: ending.type,
            description: ending.description || '',
            unlockCondition: ending.unlock_condition || '',
            unlocked: isUnlocked,
            image_url: ending.image_url || `/assets/cg/${ending.title}.jpg`
          });
          if (isUnlocked) {
            chapterData.hasUnlocked = true;
          }
        } else if (routeId) {
          // route_id 存在但不在 routes 数组中，创建新条目
          chapterMap.set(routeId, {
            chapter: t('scriptDetail.unknownChapter'),
            chapterIndex: chapterMap.size,
            endings: [{
              id: ending.id,
              name: ending.title,
              type: ending.type,
              description: ending.description || '',
              unlockCondition: ending.unlock_condition || '',
              unlocked: isUnlocked,
              image_url: ending.image_url || `/assets/cg/${ending.title}.jpg`
            }],
            hasUnlocked: isUnlocked
          });
        }
        // 如果没有 route_id，忽略这个 ending
      });
      
      // CR-031 T-031-04: 转换为数组，按章节排序，传递所有章节结局（不再只取一个）
      chapterEndings.value = Array.from(chapterMap.values())
        .filter(ch => ch.endings.length > 0) // 过滤掉没有结局的章节
        .sort((a, b) => a.chapterIndex - b.chapterIndex)
        .map(ch => ({
          chapter: ch.chapter,
          chapterIndex: ch.chapterIndex,
          endings: ch.endings,
          unlockedCount: ch.endings.filter((e: any) => e.unlocked).length
        }));
      lockedEndingCount.value = chapterEndings.value.reduce(
        (sum: number, c: any) => sum + (c.endings.length - c.unlockedCount), 0
      );
    } else {
      chapterEndings.value = [];
      lockedEndingCount.value = response.endings_count || 0;
    }
    
    // CG 预览
    if (response.cg_previews && Array.isArray(response.cg_previews)) {
      cgPreviews.value = response.cg_previews.map((cg: any) => ({
        id: cg.id,
        title: cg.name,
        image_url: cg.image_url,
        thumbnail_url: cg.image_url,
        chapter: cg.chapter,
        description: cg.description,
        isLocked: !cg.is_unlocked
      }));
    } else {
      cgPreviews.value = [];
    }
    
  } catch (err) {
    console.error('加载剧本详情失败:', err);
    error.value = t('scriptDetail.loadScriptFailed');
    characters.value = [];
    unlockedEndings.value = [];
    lockedEndingCount.value = 0;
    cgPreviews.value = [];
    routeChapters.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadScript();
});
</script>

<style scoped>
.script-detail-page {
  min-height: 100vh;
  padding: 20px;
  background: #0a0a0f;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 80px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

/* Error State */
.error-state {
  text-align: center;
  padding: 80px 20px;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.error-state h3 {
  color: #fff;
  font-size: 24px;
  margin: 0 0 8px;
}

.error-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  margin: 0 0 24px;
}

/* Main Content */
.script-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* Header with Back Button */
.detail-header {
  margin-bottom: 24px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 16px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(167, 139, 250, 0.3);
}

.back-icon {
  font-size: 16px;
}

/* Hero Section - Left-Right Layout */
.hero-section {
  display: flex;
  gap: 40px;
  margin-bottom: 48px;
}

.hero-left {
  flex-shrink: 0;
  width: 320px;
}

.hero-right {
  flex: 1;
}

.hero-cover {
  position: relative;
  width: 100%;
  max-width: 320px;
  aspect-ratio: 4 / 5;
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid rgba(167, 139, 250, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-gradient {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(236, 72, 153, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
}

.cover-emoji {
  font-size: 120px;
  filter: drop-shadow(0 8px 32px rgba(0, 0, 0, 0.3));
}

.premium-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #000;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.4);
}

.hero-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.script-title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  line-height: 1.3;
}

.script-title-en {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  font-style: italic;
}

.script-tags {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tag {
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
  padding: 6px 12px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 600;
}

.script-description {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* FE-FEAT-023: Script stats badges */
.script-stats {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 8px;
  padding: 8px 12px;
}

.stat-icon {
  font-size: 16px;
}

.stat-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

/* Player Progress Section */
.player-progress {
  background: rgba(167, 139, 250, 0.08);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.progress-percentage {
  font-size: 20px;
  font-weight: 700;
  color: #a78bfa;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #FF6B9D);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  font-size: 16px;
}

/* Hero Actions */
.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.hero-actions .cta-primary,
.hero-actions .cta-secondary {
  flex: 1;
  padding: 14px 24px;
  font-size: 16px;
}

/* Section Titles */
.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 20px;
}

.section-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 20px;
}

/* Chapters Section */
.chapters-section {
  margin-bottom: 48px;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-item {
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

.chapter-header {
  padding: 20px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.chapter-header:hover {
  background: var(--bg-hover);
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chapter-icon {
  font-size: 14px;
  color: var(--text-secondary);
  transition: transform 0.2s ease;
}

.chapter-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.chapter-nodes {
  font-size: 13px;
  color: var(--text-muted);
}

.chapter-content {
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.nodes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

@media (max-width: 768px) {
  .nodes-grid {
    grid-template-columns: 1fr;
  }
}

/* Route Tree Section */
.route-tree-section {
  margin-bottom: 48px;
}

/* Ending List Section */
.ending-list-section {
  margin-bottom: 48px;
}

/* Character Selection Section */
.character-selection-section {
  margin-bottom: 48px;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .character-grid {
    grid-template-columns: 1fr;
  }
}

/* CR-028: 可扮演角色选择区域 - REMOVED, integrated into character gallery */

/* CG Preview Section */
.cg-preview-section {
  margin-bottom: 48px;
}

/* Action Buttons Section */
.action-buttons-section {
  margin-bottom: 48px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  max-width: 500px;
  margin: 0 auto;
}

.cta-primary {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 12px;
  padding: 14px 32px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.3);
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(167, 139, 250, 0.4);
}

.cta-primary.large {
  padding: 16px 48px;
  font-size: 18px;
  flex: 1;
}

.cta-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 14px 32px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cta-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(167, 139, 250, 0.3);
}

.cta-secondary.large {
  padding: 16px 48px;
  font-size: 18px;
  flex: 1;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state h3 {
  color: #fff;
  font-size: 24px;
  margin: 0 0 8px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  margin: 0 0 24px;
}

/* Chapter Selector Modal */
.chapter-selector-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.chapter-selector-content {
  background: #1a1a2e;
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  padding: 32px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.chapter-selector-title {
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 24px;
  text-align: center;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.chapter-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chapter-item.unlocked:hover {
  background: rgba(167, 139, 250, 0.1);
  border-color: rgba(167, 139, 250, 0.4);
  transform: translateY(-2px);
}

.chapter-item.locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chapter-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.chapter-details {
  flex: 1;
  min-width: 0;
}

.chapter-name {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
}

.chapter-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chapter-status {
  color: rgba(167, 139, 250, 0.8);
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.close-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section {
    flex-direction: column;
    gap: 24px;
  }

  .hero-left {
    width: 100%;
  }

  .hero-cover {
    width: 100%;
    height: 300px;
  }

  .script-title {
    font-size: 24px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .cta-primary.large,
  .cta-secondary.large {
    padding: 14px 32px;
    font-size: 16px;
  }
}
</style>

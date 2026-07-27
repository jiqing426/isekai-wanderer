<template>
  <div class="script-detail-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button class="cta-secondary" @click="loadScript">重试</button>
    </div>

    <!-- Main Content -->
    <div v-else-if="scriptDetail" class="script-content">
      <!-- Header with Back Button -->
      <header class="detail-header">
        <button class="back-button" @click="router.back()">
          <span class="back-icon">🔙</span>
          <span>返回</span>
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
            <p class="script-author">作者：{{ scriptDetail.author }}</p>
            <p class="script-description">{{ scriptDetail.description }}</p>

            <!-- FE-FEAT-023: 展示路线和结局数量 -->
            <div class="script-stats">
              <div class="stat-badge">
                <span class="stat-icon">🗺️</span>
                <span class="stat-text">{{ routeChapters.length }} 条路线</span>
              </div>
              <div class="stat-badge">
                <span class="stat-icon">🏆</span>
                <span class="stat-text">{{ unlockedEndings.length + lockedEndingCount }} 个结局</span>
              </div>
              <div class="stat-badge">
                <span class="stat-icon">👥</span>
                <span class="stat-text">{{ characters.length }} 个角色</span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress-section">
              <div class="progress-header">
                <span class="progress-label">完成进度</span>
                <span class="progress-percentage">{{ scriptDetail.completionRate }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${scriptDetail.completionRate}%` }"></div>
              </div>
              <div class="progress-stats">
                <span>已解锁节点：{{ scriptDetail.unlockedNodes }}/{{ scriptDetail.totalNodes }}</span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="hero-actions">
              <button class="cta-primary" @click="startGame">
                🎮 开始游戏
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. Character Selection Section -->
      <section class="character-selection-section">
        <div class="character-grid">
          <CharacterDetailCard
            v-for="character in characters"
            :key="character.id"
            :character="character"
            :isSelected="selectedCharacterId === character.id"
            @select="selectCharacter(character.id)"
          />
        </div>
      </section>

      <!-- 3. Route Tree Section -->
      <section class="route-tree-section">
        <h2 class="section-title">🗺️ 路线探索</h2>
        <RouteTree :chapters="routeChapters" />
      </section>

      <!-- 4. Ending List Section -->
      <section class="ending-list-section">
        <h2 class="section-title">🏆 结局收集</h2>
        <EndingList :unlocked-endings="unlockedEndings" :locked-count="lockedEndingCount" />
      </section>

      <!-- 5. CG Preview Grid Section -->
      <section class="cg-preview-section">
        <h2 class="section-title">🎨 CG 预览</h2>
        <CGPreviewGrid :cgs="cgPreviews" />
      </section>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">📖</div>
      <h3>剧本不存在</h3>
      <p>请返回剧本大厅选择其他剧本</p>
      <button class="cta-secondary" @click="router.push('/discover')">
        返回剧本大厅
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/api/http';
import CharacterDetailCard from '@/components/CharacterDetailCard.vue';
import RouteTree from '@/components/RouteTree.vue';
import EndingList from '@/components/EndingList.vue';
import CGPreviewGrid from '@/components/CGPreviewGrid.vue';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

const scriptId = route.params.scriptId as string;
const loading = ref(true);
const error = ref<string | null>(null);
const scriptDetail = ref<any>(null);

// 角色选择相关
const characters = ref<any[]>([]);
const selectedCharacterId = ref<string | null>(null);

// 路线树相关
const routeChapters = ref<any[]>([]);

// 结局列表相关
const unlockedEndings = ref<any[]>([]);
const lockedEndingCount = ref(0);

// CG预览相关
const cgPreviews = ref<any[]>([]);

// FE-FEAT-023: 统计数据
const routesCount = ref(0);
const endingsCount = ref(0);

function selectCharacter(characterId: string) {
  selectedCharacterId.value = characterId;
}

function startGame() {
  if (!auth.isAuthenticated) {
    router.push(`/login?redirect=/scripts/${scriptId}`);
    return;
  }
  router.push(`/game?script=${scriptId}`);
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
      author: '未知作者', // 后端未提供 author 字段
      completionRate: 0,
      unlockedNodes: 0,
      totalNodes: 0,
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
    
    // 路线数据
    if (response.routes && Array.isArray(response.routes)) {
      routeChapters.value = response.routes;
    } else {
      routeChapters.value = [];
    }
    
    // 结局数据（后端只提供数量，不提供详细列表）
    unlockedEndings.value = [];
    lockedEndingCount.value = response.endings_count || 0;
    
    // CG 预览（后端未提供）
    cgPreviews.value = [];
    
  } catch (err) {
    console.error('加载剧本详情失败:', err);
    error.value = '加载剧本详情失败，请稍后重试';
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

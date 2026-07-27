<template>
  <div class="discover-page">
    <!-- Background effects -->
    <div class="discover-bg-effects">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="star-field"></div>
    </div>

    <div class="discover-container">
      <!-- Header with title and search in one row for PC -->
      <div class="discover-header">
        <div class="header-left">
          <h1 class="gradient-text">🎭 剧本大厅</h1>
          <p class="subtitle">探索精彩的异世界冒险故事</p>
        </div>
        <div class="header-right">
          <div class="search-box" :class="{ focused: searchFocused }">
            <span class="search-icon">🔍</span>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索剧本..."
              class="search-input"
              @focus="searchFocused = true"
              @blur="searchFocused = false"
              @keyup.enter="handleSearch"
            />
            <button
              v-if="searchQuery"
              class="clear-button"
              @click="clearSearch"
            >
              ✕
            </button>
            <button
              class="search-button"
              @click="handleSearch"
            >
              搜索
            </button>
          </div>
        </div>
      </div>

      <!-- Category Tabs - FE-D1: 横向分类 Tab 栏，使用后端 categoryList -->
      <div class="category-tabs">
        <button
          v-for="category in categories"
          :key="category.id"
          class="category-tab"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          <span class="tab-icon">{{ category.icon }}</span>
          <span class="tab-label">{{ category.name }}</span>
        </button>
      </div>

      <!-- Sort Options -->
      <div class="sort-section">
        <div class="sort-dropdown">
          <button class="sort-button" @click="toggleSortMenu">
            <span class="sort-label">排序：</span>
            <span class="sort-value">{{ currentSortLabel }}</span>
            <span class="sort-arrow" :class="{ open: sortMenuOpen }">▼</span>
          </button>
          <div v-if="sortMenuOpen" class="sort-menu">
            <button
              v-for="option in sortOptions"
              :key="option.value"
              class="sort-option"
              :class="{ active: sortBy === option.value }"
              @click="selectSort(option.value)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        <div class="result-count">
          共 {{ totalScripts }} 个剧本
        </div>
      </div>

      <!-- Scripts Grid -->
      <div class="scripts-section">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="scripts.length === 0" class="empty-state">
          <div class="empty-icon">🔍</div>
          <h3>未找到相关剧本</h3>
          <p>试试其他搜索词或分类</p>
        </div>

        <div v-else class="scripts-grid">
          <div
            v-for="script in scripts"
            :key="script.id"
            class="script-card"
            @click="goToScript(script.id)"
          >
            <div class="script-cover">
              <span class="script-emoji">{{ script.emoji }}</span>
              <span class="genre-tag" v-if="script.category">{{ categoryLabel(script.category) }}</span>
            </div>
            <div class="script-info">
              <h3 class="script-title">{{ script.title }}</h3>
              <p class="script-title-en">{{ script.titleEn }}</p>
              <div class="script-meta">
                <span class="script-rating">
                  <span class="stars">{{ renderStars(script.rating) }}</span>
                  <span class="rating-num">{{ script.rating.toFixed(1) }}</span>
                </span>
                <span class="script-routes">{{ script.routes }} 条路线</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loadingMore" class="loading-more">
          <div class="spinner-small"></div>
          <p>加载更多...</p>
        </div>

        <!-- 没有更多剧本 -->
        <div v-if="!loading && scripts.length > 0 && currentPage >= totalPages" class="no-more">
          <p>— 没有更多剧本 —</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          class="page-button"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          ‹ 上一页
        </button>

        <div class="page-numbers">
          <button
            v-for="page in displayedPages"
            :key="page"
            class="page-number"
            :class="{ active: currentPage === page, ellipsis: page === '...' }"
            :disabled="page === '...'"
            @click="page !== '...' && goToPage(page as number)"
          >
            {{ page }}
          </button>
        </div>

        <button
          class="page-button"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页 ›
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

interface Script {
  id: string;
  title: string;
  titleEn: string;
  emoji: string;
  rating: number;
  routes: number;
  description?: string;
  category?: string;
  hot_value?: number;
}

interface Category {
  id: string;
  name: string;
  icon: string;
}

const router = useRouter();

// State
const searchQuery = ref('');
const searchFocused = ref(false);
const selectedCategory = ref('all');
const sortBy = ref('newest');
const sortMenuOpen = ref(false);
const loading = ref(false);
const loadingMore = ref(false);
const scripts = ref<Script[]>([]);
const currentPage = ref(1);
const totalScripts = ref(0);
const totalPages = ref(0);
const scriptsPerPage = 12;

// Categories - 从后端 categoryList 动态获取
const categories = ref<Category[]>([
  { id: 'all', name: '全部', icon: '🎭' },
]);

// Sort options - 使用 sortType=popular/rating 触发后端排序
const sortOptions = [
  { value: 'newest', label: '最新' },
  { value: 'popular', label: '热门优先' },
  { value: 'rating', label: '评分优先' },
];

// Computed
const currentSortLabel = computed(() => {
  return sortOptions.find(o => o.value === sortBy.value)?.label || '最新';
});

const displayedPages = computed(() => {
  const pages: (number | string)[] = [];
  const total = totalPages.value;
  const current = currentPage.value;

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
  } else {
    if (current <= 3) {
      pages.push(1, 2, 3, 4, '...', total);
    } else if (current >= total - 2) {
      pages.push(1, '...', total - 3, total - 2, total - 1, total);
    } else {
      pages.push(1, '...', current - 1, current, current + 1, '...', total);
    }
  }

  return pages;
});

// Methods
function categoryLabel(cat: string): string {
  // 优先从后端返回的 categoryList 中查找
  const found = categories.value.find(c => c.id === cat);
  if (found) return found.name;
  
  const map: Record<string, string> = {
    romance: '恋爱',
    fantasy: '冒险',
    mystery: '悬疑',
    horror: '恐怖',
    scifi: '科幻',
    slice_of_life: '日常',
    action: '动作',
    drama: '剧情',
  };
  return map[cat] || cat;
}

function renderStars(rating: number): string {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '☆' : '') + '☆'.repeat(empty > 0 ? empty : 0);
}

function clearSearch() {
  searchQuery.value = '';
  currentPage.value = 1;
  loadScripts();
}

function handleSearch() {
  currentPage.value = 1;
  loadScripts();
}

function selectCategory(category: string) {
  selectedCategory.value = category;
  currentPage.value = 1;
  scripts.value = []; // 清空当前列表
  loadScripts();
}

function toggleSortMenu() {
  sortMenuOpen.value = !sortMenuOpen.value;
}

function selectSort(sort: string) {
  sortBy.value = sort;
  sortMenuOpen.value = false;
  currentPage.value = 1;
  scripts.value = []; // 清空当前列表
  loadScripts();
}

function goToPage(page: number) {
  currentPage.value = page;
  loadScripts();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goToScript(id: string) {
  router.push(`/scripts/${id}`);
}

async function loadScripts(append = false) {
  if (append) {
    loadingMore.value = true;
  } else {
    loading.value = true;
  }

  try {
    // 构建 API 请求参数 - 使用后端真实字段名
    const params: Record<string, any> = {
      page: currentPage.value,
      size: scriptsPerPage  // 使用 size 参数（BE-D4）
    };

    if (searchQuery.value) {
      params.search = searchQuery.value;
    }

    // 分类筛选 - 使用 category 参数（BE-D2）
    if (selectedCategory.value !== 'all') {
      params.category = selectedCategory.value;
    }

    // 排序 - 使用 sortType 参数（BE-D2/D3）
    // popular 触发 hot_value DESC, script_id ASC
    // rating 触发 created_at DESC, script_id ASC
    // newest 触发 created_at DESC, script_id ASC
    if (sortBy.value !== 'newest') {
      params.sortType = sortBy.value;
    }

    // 调用后端 API
    const response = await fetch(`/api/v1/scripts?${new URLSearchParams(params).toString()}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // FE-D1: 从后端 categoryList 动态更新分类列表
    if (data.categoryList && categories.value.length <= 1) {
      categories.value = data.categoryList;
    }

    // 适配后端数据结构
    const emojiMap: Record<string, string> = {
      'romance': '💕',
      'fantasy': '⚔️',
      'mystery': '🔍',
      'horror': '👻',
      'scifi': '🚀',
      'slice_of_life': '🌸',
      'action': '🔥',
      'drama': '🎭'
    };

    const newScripts = data.scripts.map((script: any) => ({
      id: script.id,
      title: script.title,
      titleEn: script.title, // 后端暂无英文标题，使用中文
      emoji: emojiMap[script.genre] || '📖',
      rating: 4.5 + Math.random() * 0.5, // 后端暂无评分字段，生成随机评分展示
      routes: script.route_count,
      category: script.genre,
      description: script.description,
      hot_value: script.hot_value || 0  // FE-D1: 使用后端 hot_value 字段
    }));

    // 追加或替换数据
    if (append) {
      scripts.value = [...scripts.value, ...newScripts];
    } else {
      scripts.value = newScripts;
    }

    totalScripts.value = data.total;
    // FE-D3: 使用后端返回的 totalPage（BE-D2）
    totalPages.value = data.totalPage || Math.ceil(data.total / scriptsPerPage);

  } catch (error) {
    console.error('Failed to load scripts:', error);
    if (!append) {
      scripts.value = [];
      totalScripts.value = 0;
      totalPages.value = 0;
    }
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
}

// Watchers
let searchTimeout: ReturnType<typeof setTimeout>;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    loadScripts();
  }, 300);
});

// 滚动加载处理
function handleScroll() {
  if (loadingMore.value || loading.value) return;
  if (currentPage.value >= totalPages.value) return;

  const scrollHeight = document.documentElement.scrollHeight;
  const scrollTop = document.documentElement.scrollTop;
  const clientHeight = document.documentElement.clientHeight;

  // 距离底部 200px 时加载更多
  if (scrollHeight - scrollTop - clientHeight < 200) {
    currentPage.value++;
    loadScripts(true);
  }
}

// Close sort menu when clicking outside
function handleClickOutside(e: Event) {
  const target = e.target as HTMLElement;
  if (!target.closest('.sort-dropdown')) {
    sortMenuOpen.value = false;
  }
}

onMounted(() => {
  loadScripts();
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.discover-page {
  min-height: calc(100vh - 60px);
  padding: 20px;
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
}

/* Background effects */
.discover-bg-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #4F46E5;
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #F472B6;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #fbbf24;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.star-field {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 15% 25%, rgba(192,132,252,.6) 0%, transparent 100%),
    radial-gradient(2px 2px at 35% 55%, rgba(249,168,212,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 55% 15%, rgba(251,191,36,.4) 0%, transparent 100%),
    radial-gradient(2px 2px at 75% 70%, rgba(192,132,252,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 85% 35%, rgba(249,168,212,.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 80%, rgba(251,191,36,.3) 0%, transparent 100%);
}

.discover-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.discover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 24px;
}

.header-left {
  flex-shrink: 0;
}

.header-right {
  flex: 1;
  max-width: 400px;
}

.discover-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #FF6B9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

/* Search Bar */
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 16px;
  transition: all 0.3s ease;
}

.search-box.focused {
  border-color: #a78bfa;
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 16px rgba(167, 139, 250, 0.2);
}

.search-icon {
  font-size: 16px;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.clear-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  width: 24px;
  height: 24px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
}

.clear-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.search-button {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 6px;
  padding: 6px 16px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  font-weight: 600;
}

.search-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(167, 139, 250, 0.3);
}

/* Category Tabs */
.category-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 24px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  line-height: 1;
}

.category-tab:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
}

.category-tab.active {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.3);
}

/* Sort Section */
.sort-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.sort-dropdown {
  position: relative;
}

.sort-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 16px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-button:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
}

.sort-label {
  opacity: 0.6;
}

.sort-value {
  font-weight: 600;
}

.sort-arrow {
  font-size: 10px;
  transition: transform 0.2s ease;
}

.sort-arrow.open {
  transform: rotate(180deg);
}

.sort-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  background: rgba(20, 20, 30, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 8px;
  min-width: 150px;
  z-index: 10;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.sort-option {
  display: block;
  width: 100%;
  background: transparent;
  border: none;
  border-radius: 8px;
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-option:hover {
  background: rgba(255, 255, 255, 0.08);
}

.sort-option.active {
  background: rgba(167, 139, 250, 0.2);
  color: #a78bfa;
}

.result-count {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
}

/* Scripts Grid */
.scripts-section {
  margin-bottom: 48px;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
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
  font-size: 20px;
  margin: 0 0 8px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

.scripts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.script-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.script-card:hover {
  transform: translateY(-4px);
  border-color: rgba(167, 139, 250, 0.3);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
}

.script-cover {
  height: 160px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(236, 72, 153, 0.2));
  display: flex;
  align-items: center;
  justify-content: center;
}

.script-emoji {
  font-size: 64px;
}

.script-info {
  padding: 20px;
}

.script-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 4px;
}

.script-title-en {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 12px;
  font-style: italic;
}

.script-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.script-rating {
  color: #fbbf24;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 48px;
}

.page-button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 10px 20px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
}

.page-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-numbers {
  display: flex;
  gap: 8px;
}

.page-number {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-number:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
}

.page-number.active {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border-color: transparent;
  color: #fff;
}

.page-number.ellipsis {
  cursor: default;
  background: transparent;
  border: none;
}

/* Loading More */
.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: var(--text-muted);
  font-size: 14px;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* No More */
.no-more {
  text-align: center;
  padding: 24px;
  color: var(--text-muted);
  font-size: 14px;
}

.no-more p {
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 1023px) {
  .scripts-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (max-width: 767px) {
  .discover-page {
    padding: 16px;
  }

  .discover-header h1 {
    font-size: 28px;
  }

  .subtitle {
    font-size: 14px;
  }

  .search-box {
    padding: 14px 16px;
  }

  .search-input {
    font-size: 15px;
  }

  .category-tabs {
    gap: 8px;
  }

  .category-tab {
    padding: 10px 16px;
    font-size: 14px;
  }

  .sort-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .scripts-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .script-cover {
    height: 140px;
  }

  .script-emoji {
    font-size: 56px;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .page-numbers {
    order: 3;
    width: 100%;
    justify-content: center;
  }
}
</style>

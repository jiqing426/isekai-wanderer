<template>
  <div class="fragment-mall-page">
    <!-- Header -->
    <div class="page-header">
      <h1>{{ $t('fragment.title') }}</h1>
      <div class="balance-display">
        <span class="balance-icon">💎</span>
        <span class="balance-amount">{{ userBalance }}</span>
      </div>
    </div>

    <!-- Mobile Tabs -->
    <div class="mobile-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key"
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Desktop Layout -->
    <div class="desktop-layout">
      <!-- Left Sidebar (Desktop) -->
      <div class="sidebar">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          :class="['sidebar-btn', { active: activeTab === tab.key }]"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Main Content -->
      <div class="main-content">
        <!-- Tab 1: Shop -->
        <div v-if="activeTab === 'shop'" class="shop-tab">
          <div v-if="loadingShop" class="loading-state">
            <n-spin size="large" />
          </div>
          <div v-else-if="shopGoods.length === 0" class="empty-state">
            <n-empty :description="$t('fragment.noGoods')" />
          </div>
          <div v-else class="goods-grid">
            <div 
              v-for="goods in shopGoods" 
              :key="goods.id"
              class="goods-card"
            >
              <div class="goods-icon">
                <img v-if="goods.icon_url" :src="goods.icon_url" :alt="goods.name" />
                <span v-else class="goods-emoji">{{ getCategoryEmoji(goods.category) }}</span>
              </div>
              <div class="goods-info">
                <h3 class="goods-name">{{ goods.name }}</h3>
                <p class="goods-desc">{{ goods.description }}</p>
                <div class="goods-meta">
                  <span class="goods-price">💎 {{ goods.price }}</span>
                  <span v-if="goods.stock === -1" class="goods-stock">{{ $t('fragment.unlimitedStock') }}</span>
                  <span v-else class="goods-stock">{{ $t('fragment.stock') }}: {{ goods.stock }}</span>
                </div>
              </div>
              <div class="goods-actions">
                <n-button 
                  v-if="goods.owned"
                  type="default"
                  disabled
                >
                  {{ $t('fragment.owned') }}
                </n-button>
                <n-button 
                  v-else-if="!goods.is_available"
                  type="default"
                  disabled
                >
                  {{ $t('fragment.unavailable') }}
                </n-button>
                <n-button 
                  v-else
                  type="primary"
                  :loading="exchangingId === goods.id"
                  @click="handleExchange(goods)"
                >
                  {{ $t('fragment.exchange') }}
                </n-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 2: Transactions -->
        <div v-if="activeTab === 'transactions'" class="transactions-tab">
          <div class="transaction-filters">
            <n-select 
              v-model:value="transactionFilter"
              :options="transactionFilterOptions"
              size="small"
              style="width: 150px"
              @update:value="loadTransactions"
            />
          </div>
          <div v-if="loadingTransactions" class="loading-state">
            <n-spin size="large" />
          </div>
          <div v-else-if="transactions.length === 0" class="empty-state">
            <n-empty :description="$t('fragment.noTransactions')" />
          </div>
          <div v-else class="transaction-list">
            <div 
              v-for="tx in transactions" 
              :key="tx.id"
              class="transaction-item"
              :class="tx.type"
            >
              <div class="tx-info">
                <span class="tx-desc">{{ getTransactionDescription(tx) }}</span>
                <span class="tx-time">{{ formatTime(tx.created_at) }}</span>
              </div>
              <div class="tx-amount">
                <span v-if="tx.amount > 0" class="amount-positive">+{{ tx.amount }}</span>
                <span v-else class="amount-negative">{{ tx.amount }}</span>
              </div>
            </div>
          </div>
          <div v-if="transactions.length > 0" class="load-more">
            <n-button 
              v-if="hasMoreTransactions"
              :loading="loadingMore"
              @click="loadMoreTransactions"
            >
              {{ $t('fragment.loadMore') }}
            </n-button>
          </div>
        </div>

        <!-- Tab 3: Get Fragments -->
        <div v-if="activeTab === 'get'" class="get-tab">
          <div class="guide-cards">
            <div class="guide-card" @click="$router.push('/personal-center')">
              <div class="guide-icon">📅</div>
              <div class="guide-info">
                <h3>{{ $t('fragment.dailyCheckin') }}</h3>
                <p>{{ $t('fragment.dailyCheckinDesc') }}</p>
              </div>
              <n-button type="primary" size="small">
                {{ $t('fragment.goCheckin') }}
              </n-button>
            </div>

            <div class="guide-card" @click="$router.push('/personal-center')">
              <div class="guide-icon">🎯</div>
              <div class="guide-info">
                <h3>{{ $t('fragment.dailyTasks') }}</h3>
                <p>{{ $t('fragment.dailyTasksDesc') }}</p>
              </div>
              <n-button type="primary" size="small">
                {{ $t('fragment.goTasks') }}
              </n-button>
            </div>

            <div class="guide-card" @click="$router.push('/achievements')">
              <div class="guide-icon">🏆</div>
              <div class="guide-info">
                <h3>{{ $t('fragment.achievements') }}</h3>
                <p>{{ $t('fragment.achievementsDesc') }}</p>
              </div>
              <n-button type="primary" size="small">
                {{ $t('fragment.goAchievements') }}
              </n-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Exchange Confirmation Modal -->
    <n-modal
      v-model:show="showExchangeModal"
      preset="dialog"
      :title="$t('fragment.confirmExchange')"
      :positive-text="$t('common.confirm')"
      :negative-text="$t('common.cancel')"
      @positive-click="confirmExchange"
    >
      <div v-if="selectedGoods" class="exchange-modal-content">
        <p>{{ $t('fragment.exchangeConfirm', { name: selectedGoods.name, price: selectedGoods.price }) }}</p>
        <p class="balance-after">
          {{ $t('fragment.balanceAfter') }}: 💎 {{ userBalance - selectedGoods.price }}
        </p>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMessage, NSpin, NEmpty, NButton, NModal, NSelect } from 'naive-ui';
import { getMyAsset, getShopGoods, exchangeGoods, getFragmentTransactions } from '@/api/fragment';
import type { ShopGood, FragmentTransaction } from '@/types/fragment';

const { t } = useI18n();
const message = useMessage();

// State
const activeTab = ref<'shop' | 'transactions' | 'get'>('shop');
const userBalance = ref(0);
const shopGoods = ref<ShopGood[]>([]);
const transactions = ref<FragmentTransaction[]>([]);
const loadingShop = ref(false);
const loadingTransactions = ref(false);
const loadingMore = ref(false);
const exchangingId = ref<string | null>(null);
const showExchangeModal = ref(false);
const selectedGoods = ref<ShopGood | null>(null);
const transactionFilter = ref<string>('all');
const transactionPage = ref(1);
const transactionTotal = ref(0);

// Tabs
const tabs = computed(() => [
  { key: 'shop' as const, label: t('fragment.shop') },
  { key: 'transactions' as const, label: t('fragment.transactions') },
  { key: 'get' as const, label: t('fragment.getFragments') },
]);

const transactionFilterOptions = computed(() => [
  { label: t('fragment.allTransactions'), value: 'all' },
  { label: t('fragment.income'), value: 'income' },
  { label: t('fragment.expense'), value: 'expense' },
]);

const hasMoreTransactions = computed(() => transactions.value.length < transactionTotal.value);

// Methods
async function loadBalance() {
  try {
    const asset = await getMyAsset();
    userBalance.value = asset.balance;
  } catch (error) {
    console.error('Failed to load balance:', error);
  }
}

async function loadShopGoods() {
  loadingShop.value = true;
  try {
    const res = await getShopGoods();
    shopGoods.value = res.goods;
    userBalance.value = res.user_balance;
  } catch (error) {
    console.error('Failed to load shop goods:', error);
    message.error(t('fragment.loadShopFailed'));
  } finally {
    loadingShop.value = false;
  }
}

async function loadTransactions() {
  loadingTransactions.value = true;
  transactionPage.value = 1;
  try {
    const params: any = { page: 1, page_size: 20 };
    if (transactionFilter.value && transactionFilter.value !== 'all') {
      params.type = transactionFilter.value;
    }
    const res = await getFragmentTransactions(params);
    transactions.value = res.transactions;
    transactionTotal.value = res.total;
  } catch (error) {
    console.error('Failed to load transactions:', error);
    message.error(t('fragment.loadTransactionsFailed'));
  } finally {
    loadingTransactions.value = false;
  }
}

async function loadMoreTransactions() {
  loadingMore.value = true;
  transactionPage.value++;
  try {
    const params: any = { page: transactionPage.value, page_size: 20 };
    if (transactionFilter.value && transactionFilter.value !== 'all') {
      params.type = transactionFilter.value;
    }
    const res = await getFragmentTransactions(params);
    transactions.value.push(...res.transactions);
  } catch (error) {
    console.error('Failed to load more transactions:', error);
    message.error(t('fragment.loadMoreFailed'));
  } finally {
    loadingMore.value = false;
  }
}

function handleExchange(goods: ShopGood) {
  selectedGoods.value = goods;
  showExchangeModal.value = true;
}

async function confirmExchange() {
  if (!selectedGoods.value) return false;
  
  exchangingId.value = selectedGoods.value.id;
  try {
    const res = await exchangeGoods({ goods_id: selectedGoods.value.id });
    message.success(res.message);
    userBalance.value = res.new_balance;
    // Reload shop to update owned status
    await loadShopGoods();
    return true;
  } catch (error: any) {
    console.error('Failed to exchange:', error);
    const errorMsg = error?.response?.data?.message || t('fragment.exchangeFailed');
    message.error(errorMsg);
    return false;
  } finally {
    exchangingId.value = null;
  }
}

function getCategoryEmoji(category: string): string {
  const emojiMap: Record<string, string> = {
    cg: '🖼️',
    voice: '🎵',
    skin: '👗',
    item: '📦',
  };
  return emojiMap[category] || '🎁';
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getTransactionDescription(tx: FragmentTransaction): string {
  // 优先使用后端提供的 reason_label
  if (tx.reason_label) {
    return tx.reason_label;
  }
  
  // 如果后端已提供 description，直接使用
  if (tx.description) {
    return tx.description;
  }
  
  // 使用 i18n 映射
  const typeKey = tx.reason || tx.type;
  const mapped = t(`fragment.transactionTypes.${typeKey}`);
  
  // 如果映射成功（不是 key 本身），返回映射结果
  if (mapped !== `fragment.transactionTypes.${typeKey}`) {
    return mapped;
  }
  
  // 否则返回原始值或默认文本
  return typeKey || '交易';
}

// Lifecycle
onMounted(() => {
  loadBalance();
  loadShopGoods();
  loadTransactions();
});
</script>

<style scoped>
.fragment-mall-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.balance-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
}

.balance-icon {
  font-size: 24px;
}

.balance-amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
}

/* Tabs */
.mobile-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* Desktop Layout */
.desktop-layout {
  display: flex;
  gap: 24px;
}

.sidebar {
  display: none;
  flex-direction: column;
  gap: 8px;
  min-width: 160px;
}

.sidebar-btn {
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.sidebar-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.main-content {
  flex: 1;
  min-width: 0;
}

/* Shop Tab */
.goods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.goods-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.2s;
}

.goods-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.goods-icon {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.goods-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.goods-emoji {
  font-size: 40px;
}

.goods-info {
  flex: 1;
}

.goods-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.goods-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.goods-meta {
  display: flex;
  gap: 12px;
  font-size: 14px;
}

.goods-price {
  color: var(--primary-color);
  font-weight: 600;
}

.goods-stock {
  color: var(--text-tertiary);
}

.goods-actions {
  margin-top: auto;
}

/* Transactions Tab */
.transaction-filters {
  margin-bottom: 20px;
}

.transaction-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.transaction-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tx-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tx-desc {
  font-size: 14px;
  color: var(--text-primary);
}

.tx-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.tx-amount {
  font-size: 16px;
  font-weight: 600;
}

.amount-positive {
  color: #10b981;
}

.amount-negative {
  color: #ef4444;
}

.load-more {
  margin-top: 20px;
  text-align: center;
}

/* Get Tab */
.guide-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.guide-card:hover {
  border-color: var(--primary-color);
  transform: translateX(4px);
}

.guide-icon {
  font-size: 40px;
}

.guide-info {
  flex: 1;
}

.guide-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.guide-info p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* Loading & Empty States */
.loading-state,
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

/* Exchange Modal */
.exchange-modal-content {
  padding: 16px 0;
}

.exchange-modal-content p {
  margin: 0 0 12px 0;
  font-size: 14px;
  line-height: 1.6;
}

.balance-after {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .fragment-mall-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .mobile-tabs {
    display: flex;
  }

  .desktop-layout {
    flex-direction: column;
  }

  .sidebar {
    display: none;
  }

  .goods-grid {
    grid-template-columns: 1fr;
  }
}
</style>

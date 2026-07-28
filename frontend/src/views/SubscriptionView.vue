<template>
  <div class="page-bg">
    <div class="subscription-page">
      <!-- Header -->
      <div class="page-header fade-in-up">
        <div class="page-header-info">
          <h1 class="gradient-text">{{ $t('subscription.title') }}</h1>
          <p class="page-subtitle">{{ $t('subscription.subtitle') }}</p>
        </div>
      </div>

      <!-- CR-016: 当前订阅状态 -->
      <div v-if="subscriptionStore.subscriptionStatus" class="current-subscription glass-card fade-in-up">
        <div class="subscription-status-header">
          <div class="status-left">
            <span class="status-label">当前订阅</span>
            <span class="tier-badge" :class="subscriptionStore.currentTier">
              {{ tierNameMap[subscriptionStore.currentTier] }}
            </span>
          </div>
          <div class="status-right">
            <span v-if="subscriptionStore.subscriptionStatus.expires_at" class="expires-info">
              到期时间：{{ formatDate(subscriptionStore.subscriptionStatus.expires_at) }}
            </span>
            <span v-else class="expires-info">永久有效</span>
          </div>
        </div>
        <div class="subscription-actions">
          <n-button v-if="subscriptionStore.isSubscriber" size="small" secondary @click="showCancelConfirm = true">
            取消订阅
          </n-button>
        </div>
      </div>

      <!-- CR-016: 碎片购买入口 -->
      <div class="fragment-purchase-section glass-card fade-in-up">
        <div class="fragment-header">
          <span class="fragment-icon">✨</span>
          <span class="fragment-title">碎片购买额外对话</span>
          <span class="fragment-balance">💎 {{ shardBalance }}</span>
        </div>
        <p class="fragment-desc">使用碎片临时补充对话额度，3 碎片 = 1 次额外对话</p>
        <n-button type="primary" size="small" @click="openFragmentPurchase">
          立即购买
        </n-button>
      </div>

      <!-- New Subscription Plans Component -->
      <SubscriptionPlans />

      <!-- CR-016: 套餐对比表格 -->
      <div class="comparison-section reveal">
        <h2 class="section-title">{{ $t('subscription.comparePlans') }}</h2>
        <div class="tier-comparison-wrapper glass-card">
          <TierComparison />
        </div>
      </div>

      <!-- Feature Comparison Table (保留原有) -->
      <div class="comparison-section reveal">
        <h2 class="section-title">详细功能对比</h2>
        <div class="comparison-table glass-card">
          <div class="comp-header">
            <div class="comp-cell comp-label">功能</div>
            <div class="comp-cell">免费版</div>
            <div class="comp-cell">基础版</div>
            <div class="comp-cell">标准版</div>
            <div class="comp-cell">高级版</div>
          </div>
          <div v-for="row in comparisonRows" :key="row.label" class="comp-row">
            <div class="comp-cell comp-label">{{ row.label }}</div>
            <div class="comp-cell">
              <span class="comp-check" :class="row.free ? 'included' : 'excluded'">
                {{ row.free ? '✓' : '✗' }}
              </span>
            </div>
            <div class="comp-cell">
              <span class="comp-check" :class="row.basic ? 'included' : 'excluded'">
                {{ row.basic ? '✓' : '✗' }}
              </span>
            </div>
            <div class="comp-cell">
              <span class="comp-check" :class="row.standard ? 'included' : 'excluded'">
                {{ row.standard ? '✓' : '✗' }}
              </span>
            </div>
            <div class="comp-cell">
              <span class="comp-check" :class="row.premium ? 'included' : 'excluded'">
                {{ row.premium ? '✓' : '✗' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ Section -->
      <div class="faq-section reveal" ref="faqSectionRef">
        <h2 class="section-title gradient-text">{{ $t('faq.title') }}</h2>
        <n-collapse class="faq-collapse">
          <n-collapse-item v-for="i in 10" :key="i" :name="`q${i}`" :title="$t(`faq.q${i}`)">
            <p class="faq-answer">{{ $t(`faq.a${i}`) }}</p>
          </n-collapse-item>
        </n-collapse>
      </div>

      <!-- Exit retention modal -->
      <n-modal v-model:show="showExitModal" preset="card" style="max-width: 480px" :mask-closable="false">
        <div class="exit-retention">
          <div class="exit-icon">🎁</div>
          <h2 class="exit-title">确定不领取免费试用？</h2>
          <p class="exit-desc">
            现在订阅 Standard 计划，即可享受 <strong>7天免费试用</strong>！
            <br />试用期间可随时取消，不会收取任何费用。
          </p>
          <div class="exit-benefits">
            <div class="benefit-item">
              <span class="benefit-icon">✓</span>
              <span>无限游戏次数</span>
            </div>
            <div class="benefit-item">
              <span class="benefit-icon">✓</span>
              <span>全部剧本访问</span>
            </div>
            <div class="benefit-item">
              <span class="benefit-icon">✓</span>
              <span>无限体力</span>
            </div>
            <div class="benefit-item">
              <span class="benefit-icon">✓</span>
              <span>专属剧本</span>
            </div>
          </div>
          <n-space vertical :size="12" style="margin-top: 20px;">
            <n-button type="primary" block size="large" @click="claimTrial">
              🎉 领取7天免费试用
            </n-button>
            <n-button block @click="continueLeave">继续离开</n-button>
          </n-space>
        </div>
      </n-modal>

      <!-- CR-016: 取消订阅确认弹窗 -->
      <n-modal v-model:show="showCancelConfirm" preset="card" style="max-width: 420px" :mask-closable="false">
        <div class="cancel-confirm">
          <div class="confirm-icon">⚠️</div>
          <h3 class="confirm-title">确定取消订阅？</h3>
          <p class="confirm-desc">取消后将在当前周期结束后停止服务，届时将失去所有订阅特权。</p>
          <n-space vertical :size="12" style="margin-top: 20px;">
            <n-button type="error" block @click="handleCancelSubscription">确认取消</n-button>
            <n-button block secondary @click="showCancelConfirm = false">再想想</n-button>
          </n-space>
        </div>
      </n-modal>

      <!-- CR-016: 碎片购买弹窗 -->
      <n-modal v-model:show="showFragmentPurchase" preset="card" style="max-width: 420px" :mask-closable="false">
        <div class="fragment-purchase-modal">
          <div class="modal-icon">✨</div>
          <h3 class="modal-title">碎片购买额外对话</h3>
          <p class="modal-desc">3 碎片 = 1 次额外对话</p>
          <div class="modal-balance">当前碎片余额：<span class="balance-value">💎 {{ shardBalance }}</span></div>
          <div class="amount-selector">
            <n-input-number v-model:value="fragmentAmount" :min="1" :max="99" placeholder="购买次数" />
            <div class="cost-display">
              消耗碎片：<span class="cost-value">{{ fragmentAmount * 3 }}</span>
            </div>
          </div>
          <n-space vertical :size="12" style="margin-top: 20px;">
            <n-button type="primary" block :loading="purchasing" @click="handleFragmentPurchase">
              确认购买
            </n-button>
            <n-button block secondary @click="showFragmentPurchase = false">取消</n-button>
          </n-space>
        </div>
      </n-modal>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useScrollReveal } from '@/composables/useScrollReveal';
import { useSubscriptionStore } from '@/stores/subscription';
import { cancelSubscription, purchaseFragmentQuota } from '@/api/subscription';
import { gameApi } from '@/api/game';
import { useMessage } from 'naive-ui';
import SubscriptionPlans from '@/components/SubscriptionPlans.vue';
import TierComparison from '@/components/paywall/TierComparison.vue';

useScrollReveal();

const router = useRouter();
const message = useMessage();
const subscriptionStore = useSubscriptionStore();
const showExitModal = ref(false);
const showCancelConfirm = ref(false);
const showFragmentPurchase = ref(false);
const fragmentAmount = ref(1);
const purchasing = ref(false);
const shardBalance = ref(0);

async function loadShardBalance() {
  try {
    const data = await gameApi.getShardBalance();
    shardBalance.value = data.balance;
  } catch {
    // ignore
  }
}

function openFragmentPurchase() {
  showFragmentPurchase.value = true;
  loadShardBalance();
}

const tierNameMap: Record<string, string> = {
  free: '免费版',
  basic: '基础版',
  standard: '标准版',
  premium: '高级版'
};

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  // 后端返回 UTC 时间，前端转换为本地时区显示
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short'
  });
}

async function handleCancelSubscription() {
  try {
    await cancelSubscription();
    message.success('订阅已取消');
    showCancelConfirm.value = false;
    await subscriptionStore.fetchSubscriptionStatus();
  } catch (err) {
    message.error('取消订阅失败');
  }
}

async function handleFragmentPurchase() {
  purchasing.value = true;
  try {
    await purchaseFragmentQuota({ amount: fragmentAmount.value });
    message.success(`成功购买 ${fragmentAmount.value} 次额外对话`);
    showFragmentPurchase.value = false;
    await subscriptionStore.fetchDialogueQuota();
  } catch (err) {
    message.error('购买失败');
  } finally {
    purchasing.value = false;
  }
}

onMounted(async () => {
  await subscriptionStore.fetchSubscriptionStatus();
  await subscriptionStore.fetchDialogueQuota();
  await loadShardBalance();
});

// 功能对比数据
const comparisonRows = [
  { label: '每日游戏次数', free: true, basic: true, standard: true, premium: true },
  { label: '全部剧本', free: false, basic: true, standard: true, premium: true },
  { label: '无限体力', free: false, basic: false, standard: true, premium: true },
  { label: '社区发帖', free: false, basic: true, standard: true, premium: true },
  { label: '碎片加成', free: false, basic: true, standard: true, premium: true },
  { label: '专属剧本', free: false, basic: false, standard: true, premium: true },
  { label: '优先体验', free: false, basic: false, standard: false, premium: true },
  { label: '专属头像框', free: false, basic: false, standard: false, premium: true },
  { label: '月度碎片礼包', free: false, basic: false, standard: false, premium: true },
  { label: '专属客服支持', free: false, basic: false, standard: false, premium: true },
  { label: '自定义角色', free: false, basic: false, standard: true, premium: true },
];

function claimTrial() {
  showExitModal.value = false;
  router.push('/subscription');
}

function continueLeave() {
  showExitModal.value = false;
  router.push('/discover');
}
</script>

<style scoped>
.subscription-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 16px 48px;
}

.page-header { margin-bottom: 24px; }
.page-header-row { display: flex; align-items: center; margin-bottom: 12px; }
.back-btn { color: var(--text-muted) !important; font-size: 13px !important; padding: 0 !important; }
.page-header-info { display: flex; flex-direction: column; gap: 4px; }
.page-header h1 { font-size: 28px; font-weight: 700; margin: 0; }
.page-subtitle { color: var(--text-muted); font-size: 14px; margin: 0; }

.billing-toggle {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}
.billing-tabs {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: rgba(139, 92, 246, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.12);
  border-radius: 16px;
}
.billing-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 10px 28px;
  border: none;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  transition: all 0.25s ease;
  color: var(--text-muted);
}
.billing-tab:hover {
  color: var(--text-main);
  background: rgba(167, 139, 250, 0.06);
}
.billing-tab.active {
  background: rgba(79, 70, 229, 0.15);
  color: var(--text-main);
  border: 1px solid rgba(79, 70, 229, 0.3);
}
.tab-label {
  font-size: 15px;
  font-weight: 600;
}
.tab-hint {
  font-size: 11px;
  color: var(--text-muted);
}
.tab-save {
  color: #86efac;
  font-weight: 600;
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 48px;
}

.plan-card {
  padding: 28px 24px;
  position: relative;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.plan-card:hover {
  transform: translateY(-6px) rotateX(2deg);
  box-shadow: 0 16px 48px rgba(139, 92, 246, 0.15);
}

.plan-popular {
  border-color: rgba(192, 132, 252, 0.4) !important;
}

.plan-current {
  border-color: rgba(134, 239, 172, 0.4) !important;
}

.popular-badge {
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 16px;
  border-radius: 0 0 12px 12px;
}

.plan-header {
  text-align: center;
  margin-bottom: 20px;
}

.plan-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 2px;
}

.price-amount {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.price-unit {
  font-size: 14px;
  color: var(--text-muted);
}

.price-save {
  font-size: 12px;
  color: #86efac;
  font-weight: 600;
  margin-top: 4px;
}
.price-monthly-equiv {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  flex: 1;
}

.plan-feature {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.feature-icon.included {
  color: #86efac;
}

.feature-icon.excluded {
  color: rgba(124, 111, 155, 0.4);
}

.feature-disabled {
  color: var(--text-muted);
  opacity: 0.5;
}

/* Comparison */
.comparison-section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 20px;
}

.comparison-table {
  overflow-x: auto;
  border-radius: 16px;
}

.comp-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  padding: 12px 16px;
  background: rgba(139, 92, 246, 0.06);
  border-bottom: 1px solid rgba(167, 139, 250, 0.1);
  font-weight: 600;
  font-size: 13px;
}

.comp-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.06);
  font-size: 13px;
}

.comp-row:last-child {
  border-bottom: none;
}

.comp-cell {
  text-align: center;
}

.comp-label {
  text-align: left;
  color: var(--text-main);
}

.comp-check.included {
  color: #86efac;
  font-weight: 700;
}

.comp-check.excluded {
  color: rgba(124, 111, 155, 0.3);
}

/* Confirm modal */
.subscribe-confirm {
  text-align: center;
}

.confirm-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px;
}

.confirm-plan {
  padding: 16px;
  background: rgba(139, 92, 246, 0.06);
  border-radius: 12px;
  margin-bottom: 16px;
}

.confirm-plan-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.confirm-plan-price {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.confirm-cycle {
  font-size: 16px;
  font-weight: 400;
}

.confirm-note {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 16px;
}

/* FAQ */
.faq-section {
  max-width: 680px;
  margin: 0 auto 48px;
}

.faq-section .section-title {
  font-size: 24px;
  font-weight: 800;
  text-align: center;
  margin: 0 0 24px;
}

:deep(.faq-collapse) {
  background: transparent;
  border: none;
}

:deep(.faq-collapse .n-collapse-item) {
  margin-bottom: 8px;
  border-radius: 12px !important;
  overflow: hidden;
  background: rgba(139, 92, 246, 0.04);
  border: 1px solid rgba(167, 139, 250, 0.1);
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

:deep(.faq-collapse .n-collapse-item:hover) {
  border-color: rgba(192, 132, 252, 0.25);
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.06);
}

:deep(.faq-collapse .n-collapse-item__header) {
  padding: 16px 20px !important;
  font-weight: 600;
  font-size: 14px;
  color: var(--text-main);
}

:deep(.faq-collapse .n-collapse-item__content-inner) {
  padding: 0 20px 16px !important;
}

.faq-answer {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-muted);
  margin: 0;
}

/* CR-016: 当前订阅状态 */
.current-subscription {
  padding: 20px 24px;
  margin-bottom: 24px;
}

.subscription-status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-label {
  font-size: 14px;
  color: var(--text-muted);
}

.tier-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.tier-badge.free {
  background: rgba(124, 111, 155, 0.2);
  color: var(--text-muted);
}

.tier-badge.basic {
  background: rgba(79, 70, 229, 0.2);
  color: #818CF8;
}

.tier-badge.standard {
  background: rgba(244, 114, 182, 0.2);
  color: #F472B6;
}

.tier-badge.premium {
  background: rgba(251, 191, 36, 0.2);
  color: #FBBF24;
}

.expires-info {
  font-size: 13px;
  color: var(--text-muted);
}

.subscription-actions {
  display: flex;
  justify-content: flex-end;
}

/* CR-016: 碎片购买入口 */
.fragment-purchase-section {
  padding: 20px 24px;
  margin-bottom: 24px;
}

.fragment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.fragment-icon {
  font-size: 24px;
}

.fragment-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.fragment-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
}

/* CR-016: 套餐对比包装 */
.tier-comparison-wrapper {
  padding: 24px;
  margin-bottom: 48px;
}

/* CR-016: 取消订阅确认 */
.cancel-confirm {
  text-align: center;
}

.confirm-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.confirm-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.confirm-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
  line-height: 1.6;
}

/* CR-016: 碎片购买弹窗 */
.fragment-purchase-modal {
  text-align: center;
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.modal-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 20px 0;
}

.amount-selector {
  margin: 20px 0;
}

.cost-display {
  margin-top: 12px;
  font-size: 14px;
  color: var(--text-muted);
}

.cost-value {
  font-size: 18px;
  font-weight: 700;
  color: #FBBF24;
}

</style>

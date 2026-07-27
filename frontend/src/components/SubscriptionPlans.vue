<template>
  <div class="subscription-plans">
    <!-- Tab 切换 -->
    <div class="billing-toggle">
      <div class="billing-tabs">
        <button
          class="billing-tab"
          :class="{ active: billingCycle === 'monthly' }"
          @click="billingCycle = 'monthly'"
        >
          <span class="tab-label">按月订阅</span>
          <span class="tab-hint">灵活续订</span>
        </button>
        <button
          class="billing-tab"
          :class="{ active: billingCycle === 'yearly' }"
          @click="billingCycle = 'yearly'"
        >
          <span class="tab-label">按年订阅</span>
          <span class="tab-hint tab-save">省17%</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载套餐中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadPlans">重试</button>
    </div>

    <div v-else class="plans-grid">
      <div
        v-for="plan in plans"
        :key="plan.planId"
        class="plan-card"
        :class="{ current: plan.is_current, recommended: plan.recommend }"
      >
        <div v-if="plan.recommend" class="recommended-badge">推荐</div>
        
        <div class="plan-header">
          <div class="plan-icon">{{ getTierIcon(plan.planId) }}</div>
          <h3 class="plan-name">{{ plan.name }}</h3>
        </div>

        <div class="plan-price">
          <span v-if="getPrice(plan) === 0" class="price-free">免费</span>
          <template v-else>
            <span class="price-currency">¥</span>
            <span class="price-amount">{{ getPrice(plan) }}</span>
            <span class="price-period">/{{ billingCycle === 'monthly' ? '月' : '年' }}</span>
          </template>
          <div v-if="billingCycle === 'yearly' && plan.priceMonthly > 0" class="price-monthly-equiv">
            ≈ ¥{{ (plan.priceYearly / 12).toFixed(1) }}/月
          </div>
          <div v-if="billingCycle === 'yearly' && plan.priceMonthly > 0" class="price-save">
            比月付省 ¥{{ Math.round(plan.priceMonthly * 12 - plan.priceYearly) }}
          </div>
        </div>

        <ul class="plan-features">
          <li v-for="(feature, index) in plan.featureList" :key="index">
            <span class="feature-icon">✓</span>
            <span class="feature-text">{{ feature }}</span>
          </li>
        </ul>

        <div class="plan-actions">
          <button
            v-if="plan.is_current"
            class="btn-current"
            disabled
          >
            当前套餐
          </button>
          <button
            v-else-if="plan.planId === 'free'"
            class="btn-current"
            disabled
          >
            免费版
          </button>
          <button
            v-else
            class="btn-subscribe"
            :class="{ 'btn-upgrade': plan.recommend }"
            @click="handleSubscribe(plan.planId)"
            :disabled="subscribing"
          >
            {{ subscribing ? '处理中...' : '订阅' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import { getSubscriptionPlans, createOrder } from '@/api/subscription';

interface SubscriptionPlan {
  planId: string;
  name: string;
  priceMonthly: number;
  priceYearly: number;
  featureList: string[];
  fragmentDiscountRate: number;
  recommend: boolean;
  is_current?: boolean;
}

const message = useMessage();

const loading = ref(false);
const error = ref<string | null>(null);
const plans = ref<SubscriptionPlan[]>([]);
const subscribing = ref(false);
const billingCycle = ref<'monthly' | 'yearly'>('monthly');

function getTierIcon(planId: string): string {
  const icons: Record<string, string> = {
    free: '🆓',
    basic: '⭐',
    standard: '💎',
    premium: '👑'
  };
  return icons[planId] || '🆓';
}

function getPrice(plan: SubscriptionPlan): number {
  return billingCycle.value === 'monthly' ? plan.priceMonthly : plan.priceYearly;
}

async function loadPlans() {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await getSubscriptionPlans();
    plans.value = response.plans as unknown as SubscriptionPlan[];
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载套餐失败';
    message.error('加载套餐失败');
  } finally {
    loading.value = false;
  }
}

async function handleSubscribe(planId: string) {
  subscribing.value = true;
  
  try {
    const response = await createOrder({
      planId,
      cycleType: billingCycle.value
    });
    
    if (response.payUrl) {
      window.location.href = response.payUrl;
    } else {
      message.success('订阅成功！');
      await loadPlans();
    }
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : '订阅失败';
    message.error(errorMsg);
  } finally {
    subscribing.value = false;
  }
}

onMounted(() => {
  loadPlans();
});
</script>

<style scoped>
.subscription-plans {
  width: 100%;
}

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

.loading-state,
.error-state {
  text-align: center;
  padding: 48px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.plans-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 24px 0;
}

.plan-card {
  position: relative;
  background: var(--bg-card);
  border: 2px solid var(--border-color);
  border-radius: 16px;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.plan-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.plan-card.current {
  border-color: var(--color-primary);
  background: linear-gradient(135deg, rgba(var(--color-primary-rgb), 0.05), transparent);
}

.plan-card.recommended {
  border-color: #8b5cf6;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.2);
}

.recommended-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
  color: white;
  padding: 4px 16px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.plan-header {
  text-align: center;
  margin-bottom: 24px;
}

.plan-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.plan-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.plan-price {
  text-align: center;
  margin-bottom: 16px;
}

.price-free {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.price-currency {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-secondary);
  vertical-align: top;
}

.price-amount {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary);
}

.price-period {
  font-size: 16px;
  color: var(--text-secondary);
}

.plan-quota {
  text-align: center;
  margin-bottom: 24px;
  padding: 12px;
  background: var(--bg-hover);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.quota-unlimited {
  color: #f59e0b;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  flex: 1;
}

.plan-features li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.feature-icon {
  color: var(--color-primary);
  font-weight: 700;
  flex-shrink: 0;
}

.feature-text {
  flex: 1;
}

.plan-actions {
  margin-top: auto;
}

.btn-current,
.btn-subscribe {
  width: 100%;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-current {
  background: var(--bg-hover);
  color: var(--text-secondary);
  cursor: not-allowed;
}

.btn-subscribe {
  background: var(--color-primary);
  color: white;
}

.btn-subscribe:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
}

.btn-subscribe:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-upgrade {
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
}

.btn-upgrade:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c3aed, #8b5cf6);
}

@media (max-width: 768px) {
  .plans-grid {
    grid-template-columns: 1fr;
  }
}
</style>

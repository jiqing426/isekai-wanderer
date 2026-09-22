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
          <span class="tab-label">{{ $t('subscriptionPlans.monthlyTab') }}</span>
          <span class="tab-hint">{{ $t('subscriptionPlans.monthlyHint') }}</span>
        </button>
        <button
          class="billing-tab"
          :class="{ active: billingCycle === 'yearly' }"
          @click="billingCycle = 'yearly'"
        >
          <span class="tab-label">{{ $t('subscriptionPlans.yearlyTab') }}</span>
          <span class="tab-hint tab-save">{{ $t('subscriptionPlans.yearlyHint') }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('subscriptionPlans.loadingPlans') }}</p>
    </div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadPlans">{{ $t('subscriptionPlans.retry') }}</button>
    </div>

    <div v-else class="plans-grid">
      <div
        v-for="plan in plans"
        :key="plan.planId"
        class="plan-card"
        :class="{ current: plan.is_current, recommended: plan.recommend }"
      >
        <div v-if="plan.recommend" class="recommended-badge">{{ $t('subscriptionPlans.recommend') }}</div>
        
        <div class="plan-header">
          <div class="plan-icon">{{ getTierIcon(plan.planId) }}</div>
          <h3 class="plan-name">{{ plan.name }}</h3>
        </div>

        <div class="plan-price">
          <span v-if="getPrice(plan) === 0" class="price-free">{{ $t('subscriptionPlans.free') }}</span>
          <template v-else>
            <span class="price-currency">¥</span>
            <span class="price-amount">{{ getPrice(plan) }}</span>
            <span class="price-period">/{{ billingCycle === 'monthly' ? $t('subscriptionPlans.perMonth') : $t('subscriptionPlans.perYear') }}</span>
          </template>
          <div v-if="billingCycle === 'yearly' && plan.priceMonthly > 0" class="price-monthly-equiv">
            {{ $t('subscriptionPlans.monthlyEstimate', { n: (plan.priceYearly / 12).toFixed(1) }) }}
          </div>
          <div v-if="billingCycle === 'yearly' && plan.priceMonthly > 0" class="price-save">
            {{ $t('subscriptionPlans.saveVsMonthly', { n: Math.round(plan.priceMonthly * 12 - plan.priceYearly) }) }}
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
            v-if="isCurrentPlan(plan.planId)"
            class="btn-current"
            disabled
          >
            {{ $t('subscriptionPlans.currentPlan') }}
          </button>
          <button
            v-else-if="plan.planId === 'free'"
            class="btn-current"
            disabled
          >
            {{ $t('subscriptionPlans.freeVersion') }}
          </button>
          <button
            v-else
            class="btn-subscribe"
            :class="{ 'btn-upgrade': plan.recommend }"
            @click="handleSubscribe(plan.planId)"
            :disabled="subscribing"
          >
            {{ subscribing ? $t('subscriptionPlans.processing') : $t('subscriptionPlans.subscribe') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMessage } from 'naive-ui';
import { getSubscriptionPlans, createOrder } from '@/api/subscription';
import { useSubscriptionStore } from '@/stores/subscription';
import { useAuthStore } from '@/stores/auth';
import { authApi } from '@/api/auth';

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
const { t } = useI18n();
const subscriptionStore = useSubscriptionStore();
const authStore = useAuthStore();

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

// CR-043 FIX: 判断当前用户是否已订阅该套餐且周期匹配
function isCurrentPlan(planId: string): boolean {
  // 1. API 返回的 is_current 标记
  const plan = plans.value.find(p => p.planId === planId);
  if (plan?.is_current) return true;
  // 2. subscriptionStore 实时状态 — 必须同时匹配 tier 和 billing cycle
  const subStatus = subscriptionStore.subscriptionStatus;
  if (subStatus && subStatus.tier === planId) {
    // Use billing_cycle directly from API
    if (subStatus.billing_cycle) {
      if (subStatus.billing_cycle === billingCycle.value) return true;
      return false;
    }
    // Fallback: infer from started_at + expires_at if billing_cycle missing
    if (subStatus.started_at && subStatus.expires_at) {
      const start = new Date(subStatus.started_at);
      const expires = new Date(subStatus.expires_at);
      const daysDiff = Math.round((expires.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
      const currentCycle = daysDiff > 180 ? 'yearly' : 'monthly';
      if (currentCycle === billingCycle.value) return true;
      return false;
    }
    // 没有日期信息时只判断 tier
    return true;
  }
  // 3. authStore 中的 subscription_tier
  if (authStore.user?.subscription_tier === planId) return true;
  return false;
}

// CR-043 FIX: 判断用户是否已订阅该 tier（不考虑周期）
function isSubscribedTier(planId: string): boolean {
  const subStatus = subscriptionStore.subscriptionStatus;
  if (subStatus && subStatus.tier === planId) return true;
  if (authStore.user?.subscription_tier === planId) return true;
  return false;
}

// 当前订阅周期标签
const subscribedCycleLabel = computed(() => {
  const subStatus = subscriptionStore.subscriptionStatus;
  if (subStatus?.started_at && subStatus?.expires_at) {
    const start = new Date(subStatus.started_at);
    const expires = new Date(subStatus.expires_at);
    const daysDiff = Math.round((expires.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    return daysDiff > 180 ? t('subscriptionPlans.yearlyLabel') : t('subscriptionPlans.monthlyLabel');
  }
  return '';
})

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
    error.value = err instanceof Error ? err.message : t('subscriptionPlans.loadFailed');
    message.error(t('subscriptionPlans.loadFailed'));
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
    
    if (response.status === 'success') {
      message.success(t('subscriptionPlans.subscribeSuccess'));
      await loadPlans();
      // CR-043 AC-016: 刷新订阅状态
      await subscriptionStore.fetchSubscriptionStatus();
      // CR-043 AC-017: 刷新用户信息，更新 authStore 中的 tier
      try {
        const profile = await authApi.getProfile();
        authStore.setUser({
          ...authStore.user,
          id: profile.id,
          email: profile.email,
          displayName: profile.display_name || undefined,
          emailVerified: profile.email_verified,
          onboardingCompleted: profile.onboarding_completed,
          avatar: profile.avatar_url || undefined,
          subscription_tier: (profile as any).subscription_tier || 'free',
        } as any);
      } catch (profileErr) {
        console.warn('CR-043: Failed to refresh user profile after subscription:', profileErr);
      }
    } else if (response.payUrl) {
      // 支付链接模式：跳转后返回时需要页面重新加载状态
      // 但在跳转前先预加载订阅状态
      await subscriptionStore.fetchSubscriptionStatus();
      window.location.href = response.payUrl;
    } else {
      message.success(t('subscriptionPlans.subscribeSuccess'));
      await loadPlans();
      await subscriptionStore.fetchSubscriptionStatus();
    }
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : t('subscriptionPlans.subscribeFailed');
    message.error(errorMsg);
  } finally {
    subscribing.value = false;
  }
}

onMounted(() => {
  loadPlans();
  // CR-043 FIX: 加载订阅状态用于实时判断当前套餐
  subscriptionStore.fetchSubscriptionStatus();
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

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
        <h2 class="section-title">{{ $t('subscriptionView.detailComparison') }}</h2>
        <div class="comparison-table glass-card">
          <div class="comp-header">
            <div class="comp-cell comp-label">{{ $t('subscriptionView.feature') }}</div>
            <div class="comp-cell">{{ $t('subscription.free') }}</div>
            <div class="comp-cell">{{ $t('subscription.basic') }}</div>
            <div class="comp-cell">{{ $t('subscription.standard') }}</div>
            <div class="comp-cell">{{ $t('subscription.premium') }}</div>
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

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useScrollReveal } from '@/composables/useScrollReveal';
import { useSubscriptionStore } from '@/stores/subscription';
import { useI18n } from 'vue-i18n';
import SubscriptionPlans from '@/components/SubscriptionPlans.vue';
import TierComparison from '@/components/paywall/TierComparison.vue';

useScrollReveal();

const { t } = useI18n();
const subscriptionStore = useSubscriptionStore();

const tierNameMap = computed<Record<string, string>>(() => ({
  free: t('subscription.free'),
  basic: t('subscription.basic'),
  standard: t('subscription.standard'),
  premium: t('subscription.premium')
}));

onMounted(async () => {
  await subscriptionStore.fetchSubscriptionStatus();
});

// 功能对比数据
const comparisonRows = computed(() => [
  { label: t('subscriptionView.featDailyPlays'), free: true, basic: true, standard: true, premium: true },
  { label: t('subscriptionView.featAllScripts'), free: false, basic: true, standard: true, premium: true },
  { label: t('subscriptionView.featUnlimitedStamina'), free: false, basic: false, standard: true, premium: true },
  { label: t('subscriptionView.featCommunityPost'), free: false, basic: true, standard: true, premium: true },
  { label: t('subscriptionView.featShardBonus'), free: false, basic: true, standard: true, premium: true },
  { label: t('subscriptionView.featExclusiveScripts'), free: false, basic: false, standard: true, premium: true },
  { label: t('subscriptionView.featPriorityAccess'), free: false, basic: false, standard: false, premium: true },
  { label: t('subscriptionView.featExclusiveAvatar'), free: false, basic: false, standard: false, premium: true },
  { label: t('subscriptionView.featMonthlyShardPack'), free: false, basic: false, standard: false, premium: true },
  { label: t('subscriptionView.featExclusiveSupport'), free: false, basic: false, standard: false, premium: true },
  { label: t('subscriptionView.featCustomCharacter'), free: false, basic: false, standard: true, premium: true },
]);

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

/* Mobile Responsive */
@media (max-width: 768px) {
  .subscription-page { padding: 16px 12px 32px; }
  .page-header { margin-bottom: 16px; }
  .page-header h1 { font-size: 22px; }
  .page-subtitle { font-size: 13px; }
  .billing-toggle { margin-bottom: 20px; }
  .billing-tabs { gap: 4px; }
  .billing-tab { padding: 8px 16px; }
  .tab-label { font-size: 13px; }
  .tab-hint { font-size: 10px; }
  .plans-grid { grid-template-columns: 1fr; gap: 12px; margin-bottom: 32px; }
  .plan-card { padding: 20px 16px; }
  .plan-card:hover { transform: none; }
  .plan-name { font-size: 16px; }
  .price-amount { font-size: 30px; }
  .price-unit { font-size: 12px; }
  .plan-feature { font-size: 12px; padding: 5px 0; }
  .comparison-section { margin-bottom: 32px; }
  .section-title { font-size: 18px; margin: 0 0 14px; }
  .comparison-table { border-radius: 12px; }
  .comp-header, .comp-row { grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr; padding: 10px 8px; font-size: 11px; }
  .comp-cell { font-size: 11px; }
  .comp-label { font-size: 11px; }
  .tier-comparison-wrapper { padding: 16px; margin-bottom: 32px; }
  .faq-section { max-width: 100%; margin: 0 auto 32px; }
  .faq-section .section-title { font-size: 20px; margin: 0 0 16px; }
  :deep(.faq-collapse .n-collapse-item__header) { padding: 14px 16px !important; font-size: 13px; }
  :deep(.faq-collapse .n-collapse-item__content-inner) { padding: 0 16px 12px !important; }
  .faq-answer { font-size: 12px; }
  .current-subscription { padding: 16px; margin-bottom: 16px; }
  .subscription-status-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .status-left { gap: 8px; }
  .status-label { font-size: 13px; }
  .tier-badge { font-size: 12px; }
  .expires-info { font-size: 12px; }
  .subscription-actions { justify-content: stretch; }
  .subscription-actions :deep(.n-button) { width: 100%; }
}
</style>

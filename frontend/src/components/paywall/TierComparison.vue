<template>
  <div class="tier-comparison" :class="{ compact }">
    <div class="comparison-grid">
      <!-- 表头 -->
      <div class="grid-header">
        <div class="header-cell feature-col">{{ $t('tierComparison.featureHeader') }}</div>
        <div
          v-for="tier in tiers"
          :key="tier.key"
          class="header-cell tier-col"
          :class="{ recommended: tier.key === 'standard' }"
        >
          <span class="tier-name">{{ tier.name }}</span>
          <span v-if="tier.key === 'standard'" class="recommend-tag">{{ $t('tierComparison.recommend') }}</span>
        </div>
      </div>

      <!-- 价格行 -->
      <div class="grid-row price-row">
        <div class="row-cell feature-col">{{ $t('tierComparison.monthlyFee') }}</div>
        <div
          v-for="tier in tiers"
          :key="tier.key"
          class="row-cell tier-col"
          :class="{ recommended: tier.key === 'standard' }"
        >
          <span class="price">{{ tier.price }}</span>
        </div>
      </div>

      <!-- 功能行 -->
      <div v-for="feature in features" :key="feature.key" class="grid-row">
        <div class="row-cell feature-col">
          <span class="feature-label">{{ feature.label }}</span>
        </div>
        <div
          v-for="tier in tiers"
          :key="tier.key"
          class="row-cell tier-col"
          :class="{ recommended: tier.key === 'standard' }"
        >
          <span class="cell-value" :class="getCellClass(tier.key, feature.key)">
            {{ getCellValue(tier.key, feature.key) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { SubscriptionTier } from '@/types/subscription';

interface Props {
  compact?: boolean;
}

withDefaults(defineProps<Props>(), {
  compact: false
});

const { t } = useI18n();

interface TierConfig {
  key: SubscriptionTier;
  name: string;
  price: string;
}

interface FeatureConfig {
  key: string;
  label: string;
}

const tiers = computed<TierConfig[]>(() => [
  { key: 'free', name: t('tierComparison.tierFree'), price: '¥0' },
  { key: 'basic', name: t('tierComparison.tierBasic'), price: '¥19' },
  { key: 'standard', name: t('tierComparison.tierStandard'), price: '¥39' },
  { key: 'premium', name: t('tierComparison.tierPremium'), price: '¥69' }
]);

const features = computed<FeatureConfig[]>(() => [
  { key: 'dialogue', label: t('tierComparison.featureDialogue') },
  { key: 'archive', label: t('tierComparison.featureArchive') },
  { key: 'script', label: t('tierComparison.featureScript') },
  { key: 'voice', label: t('tierComparison.featureVoice') },
  { key: 'rewind', label: t('tierComparison.featureRewind') },
  { key: 'ugc', label: 'UGC' },
  { key: 'discount', label: t('tierComparison.featureDiscount') },
  { key: 'hidden', label: t('tierComparison.featureHidden') }
]);

type CellValue = string | boolean;

const featureValues: Record<string, Record<SubscriptionTier, CellValue>> = {
  dialogue: {
    free: t('tierComparison.dialogueFree'),
    basic: t('tierComparison.dialogueBasic'),
    standard: t('tierComparison.dialogueStandard'),
    premium: t('tierComparison.dialoguePremium')
  },
  archive: {
    free: t('tierComparison.archiveFree'),
    basic: t('tierComparison.archiveBasic'),
    standard: t('tierComparison.archiveStandard'),
    premium: t('tierComparison.archivePremium')
  },
  script: {
    free: t('tierComparison.scriptFree'),
    basic: t('tierComparison.scriptBasic'),
    standard: t('tierComparison.scriptStandard'),
    premium: t('tierComparison.scriptPremium')
  },
  voice: {
    free: false,
    basic: false,
    standard: true,
    premium: true
  },
  rewind: {
    free: false,
    basic: false,
    standard: true,
    premium: true
  },
  ugc: {
    free: false,
    basic: false,
    standard: true,
    premium: true
  },
  discount: {
    free: t('tierComparison.discountFree'),
    basic: t('tierComparison.discountBasic'),
    standard: t('tierComparison.discountStandard'),
    premium: t('tierComparison.discountPremium')
  },
  hidden: {
    free: false,
    basic: false,
    standard: false,
    premium: true
  }
};

function getCellValue(tier: SubscriptionTier, featureKey: string): string {
  const value = featureValues[featureKey]?.[tier];
  if (value === true) return '✓';
  if (value === false) return '✗';
  return String(value ?? '—');
}

function getCellClass(tier: SubscriptionTier, featureKey: string): string {
  const value = featureValues[featureKey]?.[tier];
  if (value === true) return 'cell-yes';
  if (value === false) return 'cell-no';
  return 'cell-text';
}
</script>

<style scoped>
.tier-comparison {
  width: 100%;
  overflow-x: auto;
}

.comparison-grid {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-width: 320px;
}

.grid-header {
  display: flex;
  border-bottom: 1px solid rgba(167, 139, 250, 0.2);
  padding-bottom: 10px;
  margin-bottom: 8px;
}

.header-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.grid-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid rgba(167, 139, 250, 0.08);
}

.grid-row:last-child {
  border-bottom: none;
}

.feature-col {
  flex: 0 0 80px;
  text-align: left;
}

.tier-col {
  flex: 1;
  text-align: center;
  padding: 4px 2px;
  border-radius: 6px;
}

.tier-col.recommended {
  background: rgba(79, 70, 229, 0.1);
  border: 1px solid rgba(79, 70, 229, 0.3);
}

.tier-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
}

.recommend-tag {
  font-size: 10px;
  padding: 1px 6px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border-radius: 4px;
  color: #fff;
  font-weight: 600;
}

.price {
  font-size: 14px;
  font-weight: 700;
  color: #fbbf24;
}

.feature-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.cell-value {
  font-size: 12px;
  font-weight: 500;
}

.cell-yes {
  color: #10b981;
}

.cell-no {
  color: rgba(255, 255, 255, 0.3);
}

.cell-text {
  color: rgba(255, 255, 255, 0.8);
}

/* compact 模式 */
.tier-comparison.compact .feature-col {
  flex: 0 0 60px;
}

.tier-comparison.compact .feature-label {
  font-size: 11px;
}

.tier-comparison.compact .tier-name {
  font-size: 12px;
}

.tier-comparison.compact .cell-value {
  font-size: 11px;
}

.tier-comparison.compact .price {
  font-size: 12px;
}
</style>

<template>
  <n-modal
    v-model:show="visible"
    preset="card"
    :title="modalTitle"
    style="max-width: 520px"
    @after-leave="$emit('close')"
  >
    <!-- Shard packages -->
    <div v-if="mode === 'shards'" class="payment-section">
      <div class="package-grid">
        <div
          v-for="pkg in shardPackages"
          :key="pkg.id"
          class="package-card glass-card"
          :class="{ 'pkg-selected': selectedPkg === pkg.id, 'pkg-popular': pkg.popular }"
          @click="selectedPkg = pkg.id"
        >
          <div v-if="pkg.popular" class="popular-badge">{{ $t('paymentModal.popular') }}</div>
          <div class="pkg-shards">💎 {{ pkg.shards }}</div>
          <div v-if="pkg.bonus" class="pkg-bonus">{{ $t('paymentModal.bonus', { n: pkg.bonus }) }}</div>
          <div class="pkg-price">¥{{ pkg.price }}</div>
        </div>
      </div>
    </div>

    <!-- Stamina packages -->
    <div v-else-if="mode === 'stamina'" class="payment-section">
      <div class="package-grid">
        <div
          v-for="pkg in staminaPackages"
          :key="pkg.id"
          class="package-card glass-card"
          :class="{ 'pkg-selected': selectedPkg === pkg.id }"
          @click="selectedPkg = pkg.id"
        >
          <div class="pkg-shards">⚡ {{ pkg.stamina }}</div>
          <div class="pkg-desc">{{ pkg.description }}</div>
          <div class="pkg-price">¥{{ pkg.price }}</div>
        </div>
      </div>
    </div>

    <!-- Script purchase -->
    <div v-else-if="mode === 'script'" class="payment-section">
      <div v-if="scriptPurchase" class="script-confirm">
        <div class="script-title-large">📖 {{ scriptPurchase.scriptTitle }}</div>
        <div class="script-price">
          {{ scriptPurchase.currency === 'shards' ? $t('paymentModal.shardsPrice', { n: scriptPurchase.price }) : `¥${scriptPurchase.price}` }}
        </div>
      </div>
    </div>

    <!-- Payment result -->
    <div v-if="paymentResult" class="payment-result">
      <div class="result-icon" :class="paymentResult.success ? 'result-success' : 'result-fail'">
        {{ paymentResult.success ? '✓' : '✗' }}
      </div>
      <div class="result-message">{{ paymentResult.message }}</div>
    </div>

    <template #action>
      <n-space justify="end">
        <n-button @click="visible = false">{{ paymentResult ? $t('paymentModal.closeOrCancel') : $t('paymentModal.cancel') }}</n-button>
        <n-button
          v-if="!paymentResult"
          type="primary"
          :loading="processing"
          :disabled="!canPurchase"
          @click="handlePurchase"
        >
          {{ purchaseButtonText }}
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { api } from '@/api/http';

const { t } = useI18n();

interface ShardPkg { id: string; shards: number; bonus: number; price: number; popular?: boolean }
interface StaminaPkg { id: string; stamina: number; description: string; price: number }
interface ScriptPurchase { scriptTitle: string; price: number; currency: 'shards' | 'cny' }

const shardPackages: ShardPkg[] = [
  { id: 'shards_100', shards: 100, bonus: 0, price: 6 },
  { id: 'shards_500', shards: 500, bonus: 50, price: 25, popular: true },
  { id: 'shards_1000', shards: 1000, bonus: 200, price: 45 },
];

const staminaPackages: StaminaPkg[] = [
  { id: 'stamina_1', stamina: 1, description: t('paymentModal.stamina1Desc'), price: 1 },
  { id: 'stamina_5', stamina: 5, description: t('paymentModal.stamina5Desc'), price: 4 },
  { id: 'stamina_10', stamina: 10, description: t('paymentModal.stamina10Desc'), price: 7 },
];

const props = defineProps<{
  show: boolean;
  mode: 'shards' | 'stamina' | 'script';
  scriptPurchase?: ScriptPurchase;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update:show', value: boolean): void;
  (e: 'success'): void;
}>();

const message = useMessage();

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
});

const selectedPkg = ref<string | null>(null);
const processing = ref(false);
const paymentResult = ref<{ success: boolean; message: string } | null>(null);

const modalTitle = computed(() => {
  switch (props.mode) {
    case 'shards': return `💎 ${t('payment.shards')}`;
    case 'stamina': return `⚡ ${t('payment.stamina')}`;
    case 'script': return `📖 ${t('nav.scripts')}`;
    default: return t('payment.title');
  }
});

const canPurchase = computed(() => {
  if (props.mode === 'script') return !!props.scriptPurchase;
  return selectedPkg.value !== null;
});

const purchaseButtonText = computed(() => {
  switch (props.mode) {
    case 'shards': return t('payment.buy');
    case 'stamina': return t('payment.buy');
    case 'script': return t('common.confirm');
    default: return t('payment.buy');
  }
});

async function handlePurchase() {
  processing.value = true;
  paymentResult.value = null;
  try {
    let item_id: string;
    let item_name: string;
    let price: number;

    if (props.mode === 'shards') {
      const pkg = shardPackages.find((p) => p.id === selectedPkg.value);
      if (!pkg) throw new Error(t('paymentModal.noShardPkg'));
      item_id = pkg.id;
      item_name = t('paymentModal.shardPkgItem', { n: pkg.shards }) + (pkg.bonus ? t('paymentModal.shardBonus', { n: pkg.bonus }) : '');
      price = pkg.price;
    } else if (props.mode === 'stamina') {
      const pkg = staminaPackages.find((p) => p.id === selectedPkg.value);
      if (!pkg) throw new Error(t('paymentModal.noStaminaPkg'));
      item_id = pkg.id;
      item_name = t('paymentModal.staminaItem', { n: pkg.stamina });
      price = pkg.price;
    } else if (props.mode === 'script' && props.scriptPurchase) {
      item_id = 'script_purchase';
      item_name = props.scriptPurchase.scriptTitle;
      price = props.scriptPurchase.price;
    } else {
      throw new Error(t('paymentModal.invalidType'));
    }

    const resp = await api.post<{
      purchase_id: string;
      status: string;
      item_name: string;
    }>('/payment/purchase', { item_id, item_name, price });

    paymentResult.value = {
      success: resp.status === 'completed',
      message: resp.status === 'completed'
        ? t('paymentModal.purchaseSuccess', { name: item_name })
        : t('paymentModal.paymentAbnormal', { status: resp.status }),
    };
    emit('success');
  } catch (err) {
    paymentResult.value = {
      success: false,
      message: t('paymentModal.paymentFailed', { error: err instanceof Error ? err.message : t('paymentModal.unknownError') }),
    };
    message.error(t('paymentModal.paymentFailedShort'));
  } finally {
    processing.value = false;
  }
}
</script>

<style scoped>
.payment-section { padding: 4px 0; }

.package-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }

.package-card {
  padding: 20px 12px;
  text-align: center;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}
.package-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(139, 92, 246, 0.12); }

.pkg-selected { border-color: rgba(192, 132, 252, 0.5) !important; box-shadow: 0 0 0 1px rgba(192, 132, 252, 0.3); }
.pkg-popular { border-color: rgba(251, 191, 36, 0.3) !important; }

.popular-badge {
  position: absolute; top: -1px; right: -1px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #0f0a1a; font-size: 10px; font-weight: 700;
  padding: 2px 8px; border-radius: 0 16px 0 8px;
}

.pkg-shards { font-size: 20px; font-weight: 700; margin-bottom: 4px; }
.pkg-bonus { font-size: 11px; color: #86efac; font-weight: 600; margin-bottom: 4px; }
.pkg-desc { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; }
.pkg-price {
  font-size: 16px; font-weight: 700; margin-top: 8px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.script-confirm { text-align: center; padding: 12px 0; }
.script-title-large { font-size: 22px; font-weight: 700; margin-bottom: 12px; }
.script-price {
  font-size: 28px; font-weight: 700;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.payment-result { text-align: center; padding: 24px 0 8px; }
.result-icon {
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 12px; font-size: 28px; font-weight: 700;
}
.result-success { background: rgba(134, 239, 172, 0.15); color: #86efac; }
.result-fail { background: rgba(248, 113, 113, 0.15); color: #f87171; }
.result-message { font-size: 15px; font-weight: 600; color: var(--text-main); }

</style>

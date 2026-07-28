<template>
  <!-- 礼物列表弹框 -->
  <n-modal
    v-model:show="showGiftModal"
    preset="card"
    :title="`🎁 赠送礼物给 ${targetName}`"
    :style="{ maxWidth: '480px' }"
    :bordered="false"
  >
    <div class="gift-modal-body">
      <div class="gift-balance-row">
        <span class="gift-balance-label">我的碎片</span>
        <span class="gift-balance-value">💎 {{ shardBalance }}</span>
      </div>
      <n-spin :show="loading">
        <div class="gift-grid" v-if="gifts.length > 0">
          <div
            v-for="gift in gifts"
            :key="gift.id"
            class="gift-card"
            :class="{ selected: selectedGift?.id === gift.id, disabled: gift.cost > shardBalance }"
            @click="selectGift(gift)"
          >
            <span class="gift-icon">{{ giftIcon(gift.id) }}</span>
            <div class="gift-name">{{ gift.name }}</div>
            <div class="gift-meta">
              <span class="gift-cost">💎 {{ gift.cost }}</span>
              <span class="gift-bonus" :class="{ high: gift.affection_bonus >= 10 }">💕 +{{ gift.affection_bonus }}</span>
            </div>
          </div>
        </div>
        <n-empty v-else-if="!loading" description="暂无礼物" />
      </n-spin>
    </div>
  </n-modal>

  <!-- 确认赠送弹框 -->
  <n-modal v-model:show="showConfirm" :mask-closable="false" style="width: 400px; max-width: 92vw" :bordered="false">
    <div class="confirm-card glass-card" v-if="selectedGift">
      <h2 class="confirm-title">确认赠送</h2>
      <div class="confirm-gift">
        <span class="confirm-icon">{{ giftIcon(selectedGift.id) }}</span>
        <div class="confirm-info">
          <div class="confirm-name">{{ selectedGift.name }}</div>
          <div class="confirm-meta">
            <span>💎 {{ selectedGift.cost }} 碎片</span>
            <span class="bonus">💕 +{{ selectedGift.affection_bonus }} 好感</span>
          </div>
        </div>
      </div>
      <p class="confirm-desc">"{{ selectedGift.description }}"</p>
      <div class="confirm-balance">
        <span>当前碎片</span>
        <span class="balance-value">💎 {{ shardBalance }}</span>
      </div>
      <div class="confirm-after">
        <span>赠送后剩余</span>
        <span class="balance-value">💎 {{ shardBalance - selectedGift.cost }}</span>
      </div>
      <div class="confirm-target">
        赠送给 <strong>{{ targetName }}</strong>
      </div>
      <div class="confirm-actions">
        <n-button @click="showConfirm = false" secondary>取消</n-button>
        <n-button type="primary" @click="confirmSend" :loading="sending">
          🎁 确认赠送
        </n-button>
      </div>
    </div>
  </n-modal>

  <!-- 赠送结果弹框 -->
  <n-modal v-model:show="showResult" :mask-closable="true" style="max-width: 360px" :bordered="false">
    <div class="result-card glass-card" v-if="sendResult">
      <div class="result-icon">🎉</div>
      <h2 class="result-title">赠送成功！</h2>
      <div class="result-stats">
        <div class="result-stat">
          <span class="result-label">好感度变化</span>
          <span class="result-value up">💕 +{{ sendResult.affection_gained }}</span>
        </div>
        <div class="result-stat">
          <span class="result-label">当前好感度</span>
          <span class="result-value">{{ sendResult.new_affection_value }}</span>
        </div>
        <div class="result-stat">
          <span class="result-label">剩余碎片</span>
          <span class="result-value">💎 {{ sendResult.remaining_shards }}</span>
        </div>
      </div>
      <n-button type="primary" @click="showResult = false" block>好的</n-button>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useMessage } from 'naive-ui';
import { gameApi } from '@/api/game';
import type { GiftItem } from '@/api/game';

const props = defineProps<{
  modelValue: boolean;
  targetName: string;
  targetId: string;
  sessionId?: string; // 剧本游戏中需要传 sessionId
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'giftSent', result: any): void;
}>();

const message = useMessage();

const showGiftModal = ref(false);
const showConfirm = ref(false);
const showResult = ref(false);

const gifts = ref<GiftItem[]>([]);
const loading = ref(false);
const selectedGift = ref<GiftItem | null>(null);
const sending = ref(false);
const shardBalance = ref(0);
const sendResult = ref<{ new_affection_value: number; affection_gained: number; remaining_shards: number; status?: string; character_id?: string; gift_id?: string; message?: string } | null>(null);

// 同步 props.modelValue
watch(() => props.modelValue, (val) => {
  showGiftModal.value = val;
  if (val) {
    loadGifts();
  }
});

watch(showGiftModal, (val) => {
  emit('update:modelValue', val);
});

function giftIcon(giftId: string): string {
  const icons: Record<string, string> = {
    'gift-001': '💐',
    'gift-002': '🍪',
    'gift-003': '✨',
    'gift-004': '📚',
    'gift-005': '🔮',
  };
  return icons[giftId] || '🎁';
}

async function loadGifts() {
  loading.value = true;
  selectedGift.value = null;
  try {
    const [giftData, balanceData] = await Promise.all([
      gameApi.getGiftCatalog(),
      gameApi.getShardBalance()
    ]);
    if (giftData && giftData.gifts) {
      // 字段映射：后端可能返回 price 而不是 cost
      gifts.value = giftData.gifts.map((g: any) => ({
        ...g,
        cost: g.cost ?? g.price ?? 0,
      }));
    }
    if (balanceData && typeof balanceData.balance === 'number') {
      shardBalance.value = balanceData.balance;
    }
  } catch (err) {
    console.error('加载礼物列表失败:', err);
    message.error('加载礼物列表失败');
  } finally {
    loading.value = false;
  }
}

function selectGift(gift: GiftItem) {
  if (gift.cost > shardBalance.value) {
    message.warning('碎片不足，无法赠送此礼物');
    return;
  }
  selectedGift.value = gift;
  showConfirm.value = true;
}

async function confirmSend() {
  if (!selectedGift.value) return;
  sending.value = true;
  try {
    let result;
    if (props.sessionId) {
      // 剧本游戏中送礼
      result = await gameApi.sendGameGift(props.sessionId, props.targetId, selectedGift.value.id);
    } else {
      // 角色详情中送礼
      result = await gameApi.sendGift(props.targetId, selectedGift.value.id);
    }
    sendResult.value = result as any;
    shardBalance.value = (result as any).remaining_shards ?? shardBalance.value - selectedGift.value.cost;
    showConfirm.value = false;
    showResult.value = true;
    message.success(`成功赠送「${selectedGift.value.name}」！`);
    emit('giftSent', result);
  } catch (err) {
    message.error(err instanceof Error ? err.message : '赠送失败');
  } finally {
    sending.value = false;
  }
}
</script>

<style scoped>
.gift-modal-body {
  padding: 0 4px;
}

.gift-balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(251, 191, 36, 0.06);
  border-radius: 10px;
  margin-bottom: 16px;
}
.gift-balance-label {
  font-size: 14px;
  color: var(--text-muted);
}
.gift-balance-value {
  font-size: 18px;
  font-weight: 700;
  color: #fbbf24;
}

.gift-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.gift-card {
  padding: 16px;
  border: 1px solid rgba(167, 139, 250, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
}
.gift-card:hover:not(.disabled) {
  transform: translateY(-2px);
  border-color: rgba(192, 132, 252, 0.3);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.1);
}
.gift-card.selected {
  border-color: var(--brand-primary);
  background: rgba(139, 92, 246, 0.08);
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.15);
}
.gift-card.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.gift-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 8px;
}
.gift-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 6px;
}
.gift-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
.gift-cost {
  color: #fbbf24;
  font-weight: 600;
}
.gift-bonus {
  color: var(--text-muted);
}
.gift-bonus.high {
  color: #f472b6;
}

/* 确认弹框 */
.confirm-card {
  padding: 28px;
  text-align: center;
  background: var(--card-bg, rgba(30, 30, 40, 0.95));
  border-radius: 16px;
}
.confirm-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 20px;
}
.confirm-gift {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(192, 132, 252, 0.06);
  border-radius: 12px;
  margin-bottom: 16px;
}
.confirm-icon {
  font-size: 40px;
  flex-shrink: 0;
}
.confirm-info {
  text-align: left;
}
.confirm-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}
.confirm-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}
.confirm-meta .bonus {
  color: #f472b6;
}
.confirm-desc {
  font-size: 13px;
  color: var(--text-subtle);
  font-style: italic;
  margin: 0 0 16px;
}
.confirm-balance,
.confirm-after {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  font-size: 14px;
  color: var(--text-muted);
  background: rgba(251, 191, 36, 0.05);
  border-radius: 8px;
  margin-bottom: 8px;
}
.balance-value {
  font-weight: 700;
  color: #fbbf24;
}
.confirm-after {
  background: rgba(192, 132, 252, 0.05);
}
.confirm-after .balance-value {
  color: var(--brand-primary);
}
.confirm-target {
  font-size: 14px;
  color: var(--text-main);
  margin: 8px 0 20px;
}
.confirm-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 结果弹框 */
.result-card {
  padding: 32px;
  text-align: center;
  background: var(--card-bg, rgba(30, 30, 40, 0.95));
  border-radius: 16px;
}
.result-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.result-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-main);
  margin: 0 0 20px;
}
.result-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}
.result-stat {
  text-align: center;
}
.result-label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.result-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-main);
}
.result-value.up {
  color: #f472b6;
}
</style>

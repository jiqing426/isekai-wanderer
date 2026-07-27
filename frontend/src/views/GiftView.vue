<template>
  <div class="page-bg">
    <div class="gift-page">
      <!-- Back Button -->
      <div class="back-bar">
        <n-button text @click="router.back()">← {{ $t('common.back') }}</n-button>
      </div>

      <!-- Character Header -->
      <div class="gift-header glass-card">
        <div class="header-avatar">
          <div class="avatar-circle">{{ nameInitial(characterName) }}</div>
        </div>
        <div class="header-info">
          <h1 class="char-name">{{ characterName }}</h1>
          <p class="char-subtitle">选择一份礼物，增进你们的羁绊</p>
        </div>
        <div class="shard-balance" v-if="shardBalance !== null">
          <span class="shard-icon">💎</span>
          <span class="shard-value">{{ shardBalance }}</span>
          <span class="shard-label">碎片</span>
        </div>
      </div>

      <!-- Gift Catalog -->
      <n-spin :show="loading">
        <n-empty v-if="!loading && gifts.length === 0" description="暂无礼物" />
        <div class="gift-grid" v-else>
          <div
            v-for="gift in gifts"
            :key="gift.id"
            class="gift-card glass-card"
            :class="{ 'selected': selectedGift?.id === gift.id, 'disabled': gift.cost > (shardBalance || 0) }"
            @click="selectGift(gift)"
          >
            <div class="gift-icon-wrap">
              <span class="gift-icon">{{ giftIcon(gift.id) }}</span>
            </div>
            <div class="gift-name">{{ gift.name }}</div>
            <p class="gift-desc">{{ gift.description }}</p>
            <div class="gift-footer">
              <div class="gift-cost">
                <span class="cost-icon">💎</span>
                <span>{{ gift.cost }}</span>
              </div>
              <div class="gift-bonus" :class="gift.affection_bonus >= 10 ? 'high' : ''">
                💕 +{{ gift.affection_bonus }}
              </div>
            </div>
          </div>
        </div>
      </n-spin>

      <!-- Confirm Modal -->
      <n-modal v-model:show="showConfirm" :mask-closable="false" class="gift-modal" :style="{ width: '380px' }">
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
          <div class="confirm-target">
            赠送给 <strong>{{ characterName }}</strong>
          </div>
          <div class="confirm-actions">
            <n-button @click="showConfirm = false" secondary block>取消</n-button>
            <n-button type="primary" @click="confirmSend" :loading="sending" block>
              🎁 确认赠送
            </n-button>
          </div>
        </div>
      </n-modal>

      <!-- Result Modal -->
      <n-modal v-model:show="showResult" :mask-closable="true" class="gift-modal" :style="{ width: '360px' }">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';
import type { GiftItem } from '@/api/game';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const message = useMessage();

const characterId = route.params.characterId as string;
const characterName = ref('');
const gifts = ref<GiftItem[]>([]);
const loading = ref(false);
const selectedGift = ref<GiftItem | null>(null);
const showConfirm = ref(false);
const sending = ref(false);
const showResult = ref(false);
const shardBalance = ref<number | null>(null);
const sendResult = ref<{ new_affection_value: number; affection_gained: number; remaining_shards: number } | null>(null);

useHead({
  title: '赠送礼物 - Isekai Wanderer',
});

function nameInitial(name: string): string {
  return name ? name.charAt(0) : '?';
}

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

function selectGift(gift: GiftItem) {
  if (gift.cost > (shardBalance.value || 0)) {
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
    const result = await gameApi.sendGift(characterId, selectedGift.value.id);
    sendResult.value = result;
    shardBalance.value = result.remaining_shards;
    showConfirm.value = false;
    showResult.value = true;
    message.success(`成功赠送「${selectedGift.value.name}」！`);
  } catch (err) {
    message.error(err instanceof Error ? err.message : '赠送失败');
  } finally {
    sending.value = false;
  }
}

async function loadData() {
  loading.value = true;
  try {
    const [giftResp, balanceResp, charResp] = await Promise.all([
      gameApi.getGiftCatalog(),
      gameApi.getShardBalance(),
      gameApi.getCharacterDetail(characterId),
    ]);
    gifts.value = giftResp.gifts;
    shardBalance.value = balanceResp.balance;
    characterName.value = charResp.name;
  } catch (err) {
    message.error(t('common.error'));
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<style scoped>
.gift-page { max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }
.back-bar { margin-bottom: 16px; }

/* Header */
.gift-header {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 24px;
  margin-bottom: 24px;
}
.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3);
  flex-shrink: 0;
}
.header-info { flex: 1; min-width: 0; }
.char-name { font-size: 22px; font-weight: 700; color: var(--text-main); margin: 0 0 4px; }
.char-subtitle { color: var(--text-muted); font-size: 13px; margin: 0; }

/* Shard balance badge */
.shard-balance {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(251, 191, 36, 0.08);
  border: 1px solid rgba(251, 191, 36, 0.15);
  border-radius: 12px;
  flex-shrink: 0;
}
.shard-icon { font-size: 18px; }
.shard-value { font-size: 18px; font-weight: 700; color: #fbbf24; }
.shard-label { font-size: 11px; color: var(--text-muted); }

/* Gift grid */
.gift-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.gift-card {
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}
.gift-card:hover:not(.disabled) {
  transform: translateY(-4px);
  border-color: rgba(192, 132, 252, 0.3);
  box-shadow: 0 12px 32px rgba(139, 92, 246, 0.12);
}
.gift-card.selected {
  border-color: var(--brand-primary);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.2);
}
.gift-card.disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.gift-icon-wrap {
  width: 64px;
  height: 64px;
  margin: 0 auto 12px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(192, 132, 252, 0.1), rgba(249, 168, 212, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
}
.gift-icon { font-size: 32px; }
.gift-name { font-size: 16px; font-weight: 600; color: var(--text-main); margin-bottom: 6px; }
.gift-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.gift-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(167, 139, 250, 0.08);
}
.gift-cost {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #fbbf24;
}
.cost-icon { font-size: 14px; }
.gift-bonus {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}
.gift-bonus.high { color: #f472b6; }

/* Confirm modal */
.confirm-card {
  padding: 28px;
  text-align: center;
}
.confirm-title { font-size: 20px; font-weight: 700; color: var(--text-main); margin: 0 0 20px; }
.confirm-gift {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(192, 132, 252, 0.06);
  border-radius: 12px;
  margin-bottom: 16px;
}
.confirm-icon { font-size: 40px; flex-shrink: 0; }
.confirm-info { text-align: left; }
.confirm-name { font-size: 16px; font-weight: 600; color: var(--text-main); }
.confirm-meta { display: flex; gap: 12px; font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.confirm-meta .bonus { color: #f472b6; }
.confirm-desc {
  font-size: 13px;
  color: var(--text-subtle);
  font-style: italic;
  margin: 0 0 16px;
}
.confirm-target {
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 20px;
}
.confirm-actions { display: flex; flex-direction: column; gap: 10px; }

/* Result modal */
.result-card {
  padding: 32px;
  text-align: center;
}
.result-icon { font-size: 48px; margin-bottom: 12px; }
.result-title { font-size: 22px; font-weight: 700; color: var(--text-main); margin: 0 0 20px; }
.result-stats {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 24px;
}
.result-stat { text-align: center; }
.result-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.result-value { font-size: 18px; font-weight: 700; color: var(--text-main); }
.result-value.up { color: #f472b6; }
</style>

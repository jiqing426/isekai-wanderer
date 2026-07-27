<template>
  <Teleport to="body">
    <Transition name="fade-scale">
      <div v-if="visible" class="quota-modal-overlay" @click.self="handleClose">
        <div class="quota-modal" role="dialog" aria-modal="true" aria-labelledby="quota-modal-title">
          <button class="close-btn" @click="handleClose" aria-label="关闭">
            <span>✕</span>
          </button>

          <div class="modal-content">
            <!-- 进度信息 -->
            <div class="progress-info">
              <div class="icon">⚠️</div>
              <h2 id="quota-modal-title" class="title">对话额度已用完</h2>
              <p v-if="scriptProgress" class="script-progress">
                <span class="script-title">{{ scriptProgress.script_title }}</span>
                <span class="chapter-info">第 {{ scriptProgress.chapter }} / {{ scriptProgress.total_chapters }} 章</span>
              </p>
              <p v-if="scriptProgress" class="play-duration">
                已游玩 {{ formatDuration(scriptProgress.play_duration_minutes) }}
              </p>
            </div>

            <!-- 额度信息 -->
            <div class="quota-info">
              <div class="quota-item">
                <span class="label">基础额度</span>
                <span class="value">{{ quotaInfo.base_quota }}</span>
              </div>
              <div class="quota-item">
                <span class="label">已使用</span>
                <span class="value">{{ quotaInfo.consumed }}</span>
              </div>
              <div class="quota-item">
                <span class="label">剩余</span>
                <span class="value remaining">{{ quotaInfo.remaining }}</span>
              </div>
            </div>

            <!-- 双方案 -->
            <div class="solutions">
              <!-- 方案① 升级订阅 -->
              <div class="solution-card subscribe-card">
                <div class="card-header">
                  <span class="card-icon">💎</span>
                  <span class="card-title">升级订阅</span>
                  <span class="recommend-badge">推荐</span>
                </div>
                <p class="card-desc">解锁无限对话和更多专属特权</p>
                <button class="btn-primary" @click="handleSubscribe">
                  查看订阅套餐
                </button>
              </div>

              <!-- 方案② 碎片购买 -->
              <div class="solution-card fragment-card">
                <div class="card-header">
                  <span class="card-icon">✨</span>
                  <span class="card-title">碎片购买</span>
                </div>
                <p class="card-desc">使用碎片临时补充对话额度</p>
                <button class="btn-secondary" @click="showFragmentConfirm = true">
                  购买额外额度
                </button>
              </div>
            </div>

            <!-- 套餐对比 -->
            <div class="tier-comparison-section">
              <h3 class="comparison-title">套餐对比</h3>
              <TierComparison compact />
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 碎片购买确认弹窗 -->
    <Transition name="fade-scale">
      <div v-if="showFragmentConfirm" class="fragment-confirm-overlay" @click.self="showFragmentConfirm = false">
        <div class="fragment-confirm-modal">
          <div class="fragment-icon">✨</div>
          <h3 class="fragment-title">使用碎片购买对话</h3>
          <p class="fragment-desc">3 碎片 = 1 次额外对话</p>
          <div class="fragment-amount">
            <label>购买次数：</label>
            <input type="number" v-model.number="fragmentAmount" min="1" max="99" />
          </div>
          <div class="fragment-cost">
            消耗碎片：<span class="cost-value">{{ fragmentAmount * 3 }}</span>
          </div>
          <div class="fragment-actions">
            <button class="btn-cancel" @click="showFragmentConfirm = false">取消</button>
            <button class="btn-confirm" @click="confirmFragmentPurchase">确认购买</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { DialogueQuotaStatus, ScriptProgressInfo } from '@/types/subscription';
import TierComparison from './TierComparison.vue';

interface Props {
  visible: boolean;
  quotaInfo: DialogueQuotaStatus;
  scriptProgress?: ScriptProgressInfo;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'subscribe'): void;
  (e: 'buy-fragment'): void;
}>();

const showFragmentConfirm = ref(false);
const fragmentAmount = ref(1);

function handleClose() {
  emit('close');
}

function handleSubscribe() {
  emit('subscribe');
}

function confirmFragmentPurchase() {
  emit('buy-fragment');
  showFragmentConfirm.value = false;
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes} 分钟`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours} 小时 ${mins} 分钟` : `${hours} 小时`;
}
</script>

<style scoped>
.quota-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.quota-modal {
  position: relative;
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  background: rgba(15, 10, 26, 0.98);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 20px;
  overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 10;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.modal-content {
  padding: 32px 24px;
}

.progress-info {
  text-align: center;
  margin-bottom: 24px;
}

.icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
}

.script-progress {
  margin: 8px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.script-title {
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.chapter-info {
  margin-left: 8px;
  color: rgba(255, 255, 255, 0.6);
}

.play-duration {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.quota-info {
  display: flex;
  justify-content: space-around;
  padding: 16px;
  background: rgba(167, 139, 250, 0.08);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  margin-bottom: 24px;
}

.quota-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.quota-item .label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.quota-item .value {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.quota-item .value.remaining {
  color: #fbbf24;
}

.solutions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.solution-card {
  padding: 20px;
  background: rgba(167, 139, 250, 0.06);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.solution-card:hover {
  border-color: rgba(167, 139, 250, 0.4);
  background: rgba(167, 139, 250, 0.1);
}

.subscribe-card {
  border-color: rgba(79, 70, 229, 0.4);
  background: rgba(79, 70, 229, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.card-icon {
  font-size: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.recommend-badge {
  padding: 2px 8px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  color: #fff;
}

.card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 12px 0;
}

.btn-primary {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
}

.btn-secondary {
  width: 100%;
  padding: 12px 24px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
}

.tier-comparison-section {
  margin-top: 24px;
}

.comparison-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
  text-align: center;
}

/* 动画 */
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
}

.fade-scale-enter-from .quota-modal,
.fade-scale-leave-to .quota-modal {
  transform: scale(0.9);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .quota-modal {
    max-width: 90vw;
  }

  .modal-content {
    padding: 28px 20px;
  }

  .title {
    font-size: 22px;
  }

  .icon {
    font-size: 48px;
  }
}

/* 碎片购买确认弹窗 */
.fragment-confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.fragment-confirm-modal {
  width: 100%;
  max-width: 360px;
  background: rgba(15, 10, 26, 0.98);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  padding: 28px 24px;
  text-align: center;
}

.fragment-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.fragment-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.fragment-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 20px 0;
}

.fragment-amount {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.fragment-amount label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.fragment-amount input {
  width: 80px;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.fragment-cost {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 24px;
}

.cost-value {
  font-size: 18px;
  font-weight: 700;
  color: #fbbf24;
}

.fragment-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  padding: 10px 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-confirm {
  flex: 1;
  padding: 10px 20px;
  background: linear-gradient(135deg, #4F46E5, #818CF8);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
}
</style>

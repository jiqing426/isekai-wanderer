<template>
  <Teleport to="body">
    <div v-if="visible" class="paywall-overlay" @click="handleOverlayClick">
      <div class="paywall-modal" @click.stop>
        <button class="close-btn" @click="close">×</button>
        
        <div class="paywall-content">
          <div class="icon">🎁</div>
          <h2 class="title">{{ $t('gamePaywallModal.trialTitle') }}</h2>
          <p class="description">{{ $t('gamePaywallModal.trialDesc') }}</p>
          
          <div class="features">
            <div class="feature-item">
              <span class="check">✓</span>
              <span>{{ $t('gamePaywallModal.featureUnlimitedChat') }}</span>
            </div>
            <div class="feature-item">
              <span class="check">✓</span>
              <span>{{ $t('gamePaywallModal.featureUnlockScripts') }}</span>
            </div>
            <div class="feature-item">
              <span class="check">✓</span>
              <span>{{ $t('gamePaywallModal.featureExclusiveContent') }}</span>
            </div>
          </div>
          
          <div class="cta-section">
            <button class="cta-button" @click="handleSubscribe">
              {{ $t('gamePaywallModal.subscribeNow') }}
            </button>
            <button class="later-button" @click="handleLater">
              {{ $t('gamePaywallModal.later') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  visible: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'subscribe'): void;
  (e: 'later'): void;
}>();

function close() {
  emit('close');
}

function handleOverlayClick() {
  emit('close');
}

function handleSubscribe() {
  emit('subscribe');
}

function handleLater() {
  emit('later');
}
</script>

<style scoped>
.paywall-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.paywall-modal {
  position: relative;
  width: 600px;
  height: 700px;
  max-width: 90vw;
  max-height: 90vh;
  background: rgba(15, 10, 26, 0.95);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 24px;
  overflow: hidden;
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
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.paywall-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.icon {
  font-size: 80px;
  margin-bottom: 24px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
}

.description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 40px 0;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 40px;
  width: 100%;
  max-width: 400px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  font-size: 16px;
  color: #fff;
}

.check {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  flex-shrink: 0;
}

.cta-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 400px;
}

.cta-button {
  width: 100%;
  padding: 16px 32px;
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(167, 139, 250, 0.4);
}

.later-button {
  width: 100%;
  padding: 14px 32px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.later-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .paywall-modal {
    width: 90vw;
    height: auto;
    max-height: 80vh;
  }

  .paywall-content {
    padding: 32px 24px;
  }

  .icon {
    font-size: 60px;
  }

  .title {
    font-size: 24px;
  }

  .description {
    font-size: 14px;
  }

  .feature-item {
    padding: 12px 16px;
    font-size: 14px;
  }

  .cta-button {
    padding: 14px 24px;
    font-size: 16px;
  }

  .later-button {
    padding: 12px 24px;
    font-size: 14px;
  }
}
</style>

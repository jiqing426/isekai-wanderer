<template>
  <Teleport to="body">
    <div v-if="visible" class="paywall-overlay" @click="handleOverlayClick">
      <div class="paywall-modal" @click.stop>
        <button class="close-button" @click="close">×</button>
        
        <div class="paywall-content">
          <div class="crown-icon">👑</div>
          <h2 class="paywall-title">{{ title }}</h2>
          <p class="paywall-description">{{ description }}</p>
          
          <div class="features-list">
            <div v-for="(feature, index) in features" :key="index" class="feature-item">
              <span class="feature-icon">✓</span>
              <span class="feature-text">{{ feature }}</span>
            </div>
          </div>
          
          <div class="trial-info" v-if="showTrial">
            <span class="trial-badge">{{ $t('paywallModal.trialBadge') }}</span>
            <p class="trial-text">{{ $t('paywallModal.trialText') }}</p>
          </div>
          
          <div class="action-buttons">
            <button class="primary-button" @click="handleSubscribe">
              {{ subscribeText }}
            </button>
            <button v-if="showLater" class="secondary-button" @click="handleLater">
              {{ $t('paywallModal.later') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface Props {
  visible: boolean;
  title?: string;
  description?: string;
  features?: string[];
  subscribeText?: string;
  showTrial?: boolean;
  showLater?: boolean;
  closeOnClickOutside?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  title: t('paywallModal.title'),
  description: t('paywallModal.description'),
  features: () => [
    t('paywallModal.feature1'),
    t('paywallModal.feature2'),
    t('paywallModal.feature3'),
  ],
  subscribeText: t('paywallModal.subscribeText'),
  showTrial: true,
  showLater: true,
  closeOnClickOutside: true,
});

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'subscribe'): void;
  (e: 'later'): void;
}>();

function close() {
  emit('close');
}

function handleOverlayClick() {
  if (props.closeOnClickOutside) {
    close();
  }
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
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.paywall-modal {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 24px;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow: hidden;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 1;
}

.close-button:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  transform: rotate(90deg);
}

.paywall-content {
  padding: 32px 24px 24px;
  text-align: center;
}

.crown-icon {
  font-size: 48px;
  margin-bottom: 16px;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.paywall-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #FF6B9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.paywall-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
  margin: 0 0 20px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 10px;
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.feature-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.feature-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.trial-info {
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 16px;
}

.trial-badge {
  display: inline-block;
  font-size: 14px;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 4px;
}

.trial-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.primary-button {
  width: 100%;
  padding: 12px 24px;
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.4);
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(167, 139, 250, 0.5);
}

.primary-button:active {
  transform: translateY(0);
}

.secondary-button {
  width: 100%;
  padding: 10px 24px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-button:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

@media (max-width: 640px) {
  .paywall-modal {
    max-width: 100%;
    margin: 0 12px;
  }

  .paywall-content {
    padding: 28px 20px 20px;
  }

  .crown-icon {
    font-size: 40px;
    margin-bottom: 12px;
  }

  .paywall-title {
    font-size: 20px;
  }

  .paywall-description {
    font-size: 13px;
  }

  .feature-item {
    padding: 6px 10px;
  }

  .feature-text {
    font-size: 12px;
  }

  .primary-button,
  .secondary-button {
    padding: 10px 20px;
    font-size: 13px;
  }
}
</style>

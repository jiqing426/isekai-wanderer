<template>
  <div class="onboarding-page">
    <!-- Background effects -->
    <div class="onboarding-bg-effects">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="star-field"></div>
    </div>

    <div class="onboarding-container">
      <!-- Header -->
      <div class="onboarding-header">
        <div class="brand-mark">✦</div>
        <h1 class="gradient-text">{{ $t('onboarding.title') }}</h1>
        <p class="subtitle">{{ $t('onboarding.subtitle') }}</p>
      </div>

      <!-- Progress Indicator -->
      <div class="progress-indicator">
        <div class="progress-line">
          <div class="progress-fill" :style="{ width: progressWidth }"></div>
        </div>
        <div class="progress-steps">
          <div 
            v-for="step in 3" 
            :key="step" 
            class="progress-step"
            :class="{ 
              active: step === currentStep, 
              completed: step < currentStep 
            }"
          >
            <div class="step-circle">
              <span v-if="step < currentStep" class="check-icon">✓</span>
              <span v-else>{{ step }}</span>
            </div>
            <div class="step-label">{{ getStepLabel(step) }}</div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="step-content">
        <transition :name="slideDirection" mode="out-in">
          <!-- Step 1: Type Selection -->
          <div v-if="currentStep === 1" key="step1" class="step-panel">
            <h2 class="step-title">{{ $t('onboarding.step1Title') }}</h2>
            <p class="step-description">{{ $t('onboarding.step1Desc') }}</p>
            
            <div class="card-grid">
              <div
                v-for="type in storyTypes"
                :key="type.value"
                class="selection-card"
                :class="{ selected: selectedType === type.value }"
                @click="selectType(type.value)"
              >
                <div class="card-icon">{{ type.icon }}</div>
                <div class="card-title">{{ type.label }}</div>
                <div class="card-desc">{{ type.desc }}</div>
              </div>
            </div>
          </div>

          <!-- Step 2: Character Style -->
          <div v-else-if="currentStep === 2" key="step2" class="step-panel">
            <h2 class="step-title">{{ $t('onboarding.step2Title') }}</h2>
            <p class="step-description">{{ $t('onboarding.step2Desc') }}</p>
            
            <div class="card-grid">
              <div
                v-for="style in characterStyles"
                :key="style.value"
                class="selection-card"
                :class="{ selected: selectedStyle === style.value }"
                @click="selectStyle(style.value)"
              >
                <div class="card-icon">{{ style.icon }}</div>
                <div class="card-title">{{ style.label }}</div>
                <div class="card-desc">{{ style.desc }}</div>
              </div>
            </div>
          </div>

          <!-- Step 3: AI Demo Chat -->
          <div v-else key="step3" class="step-panel">
            <h2 class="step-title">{{ $t('onboarding.step3Title') }}</h2>
            <p class="step-description">{{ $t('onboarding.step3Desc') }}</p>
            
            <div class="demo-chat-container">
              <div class="chat-messages" ref="chatContainer">
                <div 
                  v-for="(msg, index) in chatMessages" 
                  :key="index"
                  class="chat-message"
                  :class="msg.role"
                >
                  <div class="message-avatar">
                    {{ msg.role === 'ai' ? '🌸' : '👤' }}
                  </div>
                  <div class="message-content">{{ msg.text }}</div>
                </div>
                
                <!-- Typing indicator -->
                <div v-if="isTyping" class="chat-message ai">
                  <div class="message-avatar">🌸</div>
                  <div class="message-content typing-indicator">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
              
              <div class="chat-input-container">
                <input
                  v-model="userInput"
                  type="text"
                  :placeholder="$t('onboarding.chatPlaceholder')"
                  class="chat-input"
                  @keyup.enter="sendMessage"
                  :disabled="isTyping"
                />
                <button 
                  class="send-button"
                  @click="sendMessage"
                  :disabled="!userInput.trim() || isTyping"
                >
                  {{ $t('onboarding.send') }}
                </button>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Navigation Buttons -->
      <div class="step-actions">
        <button
          v-if="currentStep > 1"
          class="nav-button secondary"
          @click="prevStep"
        >
          {{ $t('common.previous') }}
        </button>
        <div class="spacer"></div>
        <button
          v-if="currentStep < 3"
          class="nav-button primary"
          @click="nextStep"
          :disabled="!canProceed"
        >
          {{ $t('common.next') }}
        </button>
        <button
          v-else
          class="nav-button primary"
          @click="completeOnboarding"
          :disabled="completing"
        >
          {{ completing ? $t('common.loading') : $t('onboarding.startAdventure') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { api } from '@/api/http';
import { gameApi } from '@/api/game';

const { t } = useI18n();
const router = useRouter();
const message = useMessage();
const auth = useAuthStore();

// State
const currentStep = ref(1);
const selectedType = ref<string | null>(null);
const selectedStyle = ref<string | null>(null);
const completing = ref(false);
const slideDirection = ref('slide-right');

// Chat state
const userInput = ref('');
const isTyping = ref(false);
const chatContainer = ref<HTMLElement | null>(null);
const chatMessages = ref([
  { role: 'ai', text: '你好！我是雪乃，很高兴认识你。让我来为你介绍一下这个奇妙的世界吧！' },
  { role: 'ai', text: '在这里，每一个选择都会影响故事的走向。你可以和我聊天，探索不同的可能性。' },
]);

// Story types (single select)
const storyTypes = [
  { value: 'romance', icon: '💕', label: t('onboardingLabels.genreRomance'), desc: t('onboardingLabels.descRomance') },
  { value: 'adventure', icon: '⚔️', label: t('onboardingLabels.genreFantasy'), desc: t('onboardingLabels.descFantasy') },
  { value: 'mystery', icon: '🔍', label: t('onboardingLabels.genreMystery'), desc: t('onboardingLabels.descMystery') },
  { value: 'scifi', icon: '🚀', label: t('onboardingLabels.genreScifi'), desc: t('onboardingLabels.descScifi') },
  { value: 'school', icon: '🎓', label: t('onboardingLabels.genreSchool'), desc: t('onboardingLabels.descSchool') },
  { value: 'slice', icon: '🌸', label: t('onboardingLabels.genreSlice'), desc: t('onboardingLabels.descSlice') },
];

// Character styles (single select)
const characterStyles = [
  { value: 'gentle', icon: '🌷', label: t('onboardingLabels.styleGentle'), desc: t('onboardingLabels.styleGentleDesc') },
  { value: 'tsundere', icon: '🔥', label: t('onboardingLabels.styleTsundere'), desc: t('onboardingLabels.styleTsundereDesc') },
  { value: 'energetic', icon: '✨', label: t('onboardingLabels.styleEnergetic'), desc: t('onboardingLabels.styleEnergeticDesc') },
  { value: 'mysterious', icon: '🌙', label: t('onboardingLabels.styleMysterious'), desc: t('onboardingLabels.styleMysteriousDesc') },
  { value: 'cool', icon: '🧊', label: t('onboardingLabels.styleCool'), desc: t('onboardingLabels.styleCoolDesc') },
  { value: 'playful', icon: '🎭', label: t('onboardingLabels.stylePlayful'), desc: t('onboardingLabels.stylePlayfulDesc') },
];

// Computed
const progressWidth = computed(() => {
  return `${((currentStep.value - 1) / 2) * 100}%`;
});

const canProceed = computed(() => {
  if (currentStep.value === 1) return selectedType.value !== null;
  if (currentStep.value === 2) return selectedStyle.value !== null;
  return true;
});

// Methods
function getStepLabel(step: number): string {
  const labels = [
    t('onboarding.step1Title'),
    t('onboarding.step2Title'),
    t('onboarding.step3Title')
  ];
  return labels[step - 1] || '';
}

function selectType(value: string) {
  selectedType.value = value;
}

function selectStyle(value: string) {
  selectedStyle.value = value;
}

function nextStep() {
  if (currentStep.value < 3 && canProceed.value) {
    slideDirection.value = 'slide-left';
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    slideDirection.value = 'slide-right';
    currentStep.value--;
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || isTyping.value) return;

  // Add user message
  chatMessages.value.push({
    role: 'user',
    text: userInput.value
  });

  const userMessage = userInput.value;
  userInput.value = '';
  
  // Scroll to bottom
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }

  // Simulate AI typing
  isTyping.value = true;
  
  try {
    // Call API to get AI response
    const response = await gameApi.sendChatDemo(userMessage);
    
    chatMessages.value.push({
      role: 'ai',
      text: response.reply
    });
  } catch (err) {
    console.error('Failed to get AI response:', err);
    // Fallback message on error
    chatMessages.value.push({
      role: 'ai',
      text: '抱歉，我暂时无法回复。请稍后再试。'
    });
  } finally {
    isTyping.value = false;
  }
  
  // Scroll to bottom again
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}

async function completeOnboarding() {
  completing.value = true;
  try {
    // Save preferences to backend
    const profilePayload = {
      preferred_genre: selectedType.value,
      preferred_style: selectedStyle.value,
      locale: 'zh',
      onboarding_completed: true,
    };
    
    try {
      await api.put('/user/profile', profilePayload);
    } catch (putErr: unknown) {
      const msg = putErr instanceof Error ? putErr.message : '';
      if (msg.includes('405') || msg.includes('Method Not Allowed')) {
        await api.patch('/user/preferences', {
          preferred_genre: selectedType.value,
          preferred_style: selectedStyle.value,
          locale: 'zh',
        });
      } else {
        throw putErr;
      }
    }
    
    // Update local state
    auth.setUser({ ...auth.user!, onboardingCompleted: true });
    
    // Save to localStorage as backup
    localStorage.setItem('onboarding_preferences', JSON.stringify({
      type: selectedType.value,
      style: selectedStyle.value
    }));
    
    message.success(t('onboardingLabels.completeSuccess'));
    router.push('/discover');
  } catch (err) {
    const msg = err instanceof Error ? err.message : '';
    message.warning(`${t('onboardingLabels.saveFailed')} (${msg})`);
    // Still mark as completed locally
    auth.setUser({ ...auth.user!, onboardingCompleted: true });
    router.push('/discover');
  } finally {
    completing.value = false;
  }
}
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #0a0a0f;
  position: relative;
  overflow: hidden;
}

/* Background effects */
.onboarding-bg-effects {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: orbFloat 8s ease-in-out infinite;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: #4F46E5;
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: #F472B6;
  bottom: -50px;
  right: -50px;
  animation-delay: 2s;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: #fbbf24;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 4s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(20px, -20px); }
}

.star-field {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(2px 2px at 15% 25%, rgba(192,132,252,.6) 0%, transparent 100%),
    radial-gradient(2px 2px at 35% 55%, rgba(249,168,212,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 55% 15%, rgba(251,191,36,.4) 0%, transparent 100%),
    radial-gradient(2px 2px at 75% 70%, rgba(192,132,252,.5) 0%, transparent 100%),
    radial-gradient(1px 1px at 85% 35%, rgba(249,168,212,.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 25% 80%, rgba(251,191,36,.3) 0%, transparent 100%);
}

.onboarding-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 700px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

/* Header */
.onboarding-header {
  text-align: center;
  margin-bottom: 16px;
}

.brand-mark {
  font-size: 24px;
  color: #a78bfa;
  filter: drop-shadow(0 0 12px rgba(192, 132, 252, 0.4));
  margin-bottom: 4px;
}

.onboarding-header h1 {
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px;
  background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #FF6B9D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  margin: 0;
}

/* Progress Indicator */
.progress-indicator {
  margin-bottom: 20px;
  position: relative;
}

.progress-line {
  position: absolute;
  top: 20px;
  left: 60px;
  right: 60px;
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #FF6B9D);
  transition: width 0.4s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.step-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.progress-step.active .step-circle {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.4);
}

.progress-step.completed .step-circle {
  background: rgba(167, 139, 250, 0.2);
  border-color: #a78bfa;
  color: #a78bfa;
}

.check-icon {
  font-size: 18px;
}

.step-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.progress-step.active .step-label {
  color: #fff;
}

/* Step Content */
.step-content {
  min-height: 400px;
  margin-bottom: 32px;
}

.step-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-title {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px;
  text-align: center;
}

.step-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 32px;
  text-align: center;
}

/* Card Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.selection-card {
  background: rgba(255, 255, 255, 0.03);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.selection-card:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(167, 139, 250, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(167, 139, 250, 0.2);
}

.selection-card.selected {
  background: rgba(167, 139, 250, 0.15);
  border-color: #a78bfa;
  box-shadow: 0 0 24px rgba(167, 139, 250, 0.3);
  transform: scale(1.02);
}

.card-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  line-height: 1.4;
}

/* Demo Chat */
.demo-chat-container {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 400px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(167, 139, 250, 0.3);
  border-radius: 3px;
}

.chat-message {
  display: flex;
  gap: 12px;
  animation: messageSlide 0.3s ease;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.chat-message.ai .message-avatar {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
}

.message-content {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 12px 16px;
  color: #fff;
  font-size: 14px;
  line-height: 1.5;
  max-width: 70%;
}

.chat-message.user .message-content {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Chat Input */
.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px 16px;
  color: #fff;
  font-size: 14px;
  outline: none;
  transition: all 0.2s ease;
}

.chat-input:focus {
  border-color: #a78bfa;
  background: rgba(255, 255, 255, 0.1);
}

.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.send-button {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Navigation Buttons */
.step-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.spacer {
  flex: 1;
}

.nav-button {
  padding: 14px 32px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.nav-button.primary {
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  color: #fff;
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.3);
}

.nav-button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(167, 139, 250, 0.4);
}

.nav-button.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-button.secondary {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-button.secondary:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.3);
}

/* Slide animations */
.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .onboarding-container {
    padding: 24px 20px;
  }

  .onboarding-header h1 {
    font-size: 24px;
  }

  .progress-line {
    left: 40px;
    right: 40px;
  }

  .step-circle {
    width: 36px;
    height: 36px;
    font-size: 14px;
  }

  .step-label {
    font-size: 11px;
  }

  .step-title {
    font-size: 20px;
  }

  .card-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .selection-card {
    padding: 20px 16px;
  }

  .card-icon {
    font-size: 40px;
  }

  .demo-chat-container {
    height: 350px;
  }

  .chat-input-container {
    flex-direction: column;
  }

  .send-button {
    width: 100%;
  }

  .nav-button {
    padding: 12px 24px;
    font-size: 14px;
  }
}
</style>

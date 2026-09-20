<template>
  <Teleport to="body">
    <Transition name="overlay-fade">
      <div v-if="visible" class="locked-overlay-backdrop" @click.self="$emit('close')">
        <div class="locked-overlay-modal">
          <!-- Lock Icon -->
          <div class="lock-icon-wrapper">
            <span class="lock-icon">🔒</span>
          </div>

          <!-- Character Info -->
          <h3 class="modal-title">解锁角色</h3>
          <div class="character-preview">
            <div class="preview-avatar">
              <img v-if="character?.avatar_url && !avatarFailed" :src="character.avatar_url" :alt="character?.name" @error="avatarFailed = true" />
              <span v-else>{{ character?.name?.charAt(0) || '?' }}</span>
            </div>
            <p class="preview-name">{{ character?.name }}</p>
            <p v-if="character?.play_description" class="preview-desc">{{ character.play_description }}</p>
          </div>

          <!-- Unlock Info -->
          <div class="unlock-info">
            <template v-if="character?.unlock_type === 'paid'">
              <p class="unlock-message">该角色为付费角色，解锁后即可扮演</p>
              <div class="price-tag">
                <span class="price-icon">💎</span>
                <span class="price-value">{{ character?.unlock_price }}</span>
              </div>
            </template>
            <template v-else-if="character?.unlock_type === 'subscription'">
              <p class="unlock-message">该角色仅限高级订阅用户扮演</p>
              <div class="subscription-badge">
                <span>⭐ 高级订阅</span>
              </div>
            </template>
          </div>

          <!-- Actions -->
          <div class="modal-actions">
            <button class="btn-cancel" @click="$emit('close')">取消</button>
            <button class="btn-unlock" @click="handleUnlock" :disabled="unlocking">
              <span v-if="unlocking" class="btn-spinner"></span>
              <span v-else>{{ unlockButtonText }}</span>
            </button>
          </div>

          <!-- Error Message -->
          <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

export interface PlayableCharacter {
  id: string;
  name: string;
  avatar_url?: string;
  play_description?: string;
  unlock_type: 'free' | 'paid' | 'subscription';
  unlock_price: number | null;
  is_unlocked: boolean;
}

const props = defineProps<{
  visible: boolean;
  character: PlayableCharacter | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'unlock', characterId: string): void;
}>();

const unlocking = ref(false);
const errorMessage = ref('');

// CR-032: 图片加载失败时 fallback 到首字母
const avatarFailed = ref(false);

watch(() => props.character?.avatar_url, () => {
  avatarFailed.value = false;
});

const unlockButtonText = computed(() => {
  if (!props.character) return '解锁';
  if (props.character.unlock_type === 'paid') {
    return `💎 ${props.character.unlock_price} 解锁`;
  }
  if (props.character.unlock_type === 'subscription') {
    return '⭐ 订阅解锁';
  }
  return '解锁';
});

async function handleUnlock() {
  if (!props.character || unlocking.value) return;
  unlocking.value = true;
  errorMessage.value = '';
  try {
    emit('unlock', props.character.id);
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : '解锁失败，请稍后重试';
  } finally {
    unlocking.value = false;
  }
}
</script>

<style scoped>
.locked-overlay-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.locked-overlay-modal {
  background: #1a1a2e;
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 20px;
  padding: 32px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}

.lock-icon-wrapper {
  margin-bottom: 16px;
}

.lock-icon {
  font-size: 48px;
  filter: drop-shadow(0 4px 12px rgba(167, 139, 250, 0.4));
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 20px;
}

.character-preview {
  margin-bottom: 20px;
}

.preview-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(236, 72, 153, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  overflow: hidden;
  border: 2px solid rgba(167, 139, 250, 0.3);
}

.preview-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-avatar span {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.8);
}

.preview-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px;
}

.preview-desc {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
  line-height: 1.5;
}

.unlock-info {
  margin-bottom: 24px;
}

.unlock-message {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 12px;
}

.price-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 12px;
  padding: 8px 16px;
}

.price-icon {
  font-size: 18px;
}

.price-value {
  font-size: 18px;
  font-weight: 700;
  color: #fbbf24;
}

.subscription-badge {
  display: inline-block;
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 12px;
  padding: 8px 16px;
  color: #a78bfa;
  font-size: 16px;
  font-weight: 600;
}

.modal-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.25);
}

.btn-unlock {
  flex: 1;
  background: linear-gradient(135deg, #a78bfa, #FF6B9D);
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-unlock:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.4);
}

.btn-unlock:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  font-size: 13px;
  color: #f87171;
  margin: 12px 0 0;
}

/* Transition */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}

.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
</style>

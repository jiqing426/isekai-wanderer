<template>
  <div class="dialogue-box" @click="$emit('click')">
    <div class="dialogue-header" v-if="characterName">
      <span class="char-tag" :class="{ narrator: !characterId }">
        {{ characterName }}
      </span>
      <span class="emotion-tag" v-if="emotion">{{ emotion }}</span>
    </div>
    <div class="dialogue-text">
      <span class="text-content">{{ displayedText }}</span>
      <span class="cursor" v-if="!isComplete">▍</span>
    </div>
    <div class="dialogue-hint" v-if="isComplete && !hasChoices">
      <span>点击继续 ▸</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useAudioManager } from '@/composables/useAudioManager';

const props = defineProps<{
  text: string;
  characterName?: string;
  characterId?: string;
  emotion?: string;
  speed?: number;
  typingSound?: boolean;
  hasChoices?: boolean;
}>();

const emit = defineEmits<{
  complete: [];
  click: [];
}>();

const audioManager = useAudioManager();
const displayedText = ref('');
const isComplete = ref(false);
let animFrameId = 0;
let charIndex = 0;
let lastTime = 0;
let lastSoundChar = 0;
const CHARS_PER_SEC = 30;
const SOUND_INTERVAL = 3; // Play sound every 3 characters

function startTyping() {
  displayedText.value = '';
  charIndex = 0;
  lastSoundChar = 0;
  isComplete.value = false;
  lastTime = 0;
  cancelAnimationFrame(animFrameId);

  function tick(time: number) {
    if (!lastTime) lastTime = time;
    const elapsed = time - lastTime;
    const targetIndex = Math.min(
      Math.floor((elapsed / 1000) * CHARS_PER_SEC),
      props.text.length
    );
    if (targetIndex > charIndex) {
      charIndex = targetIndex;
      displayedText.value = props.text.slice(0, charIndex);
      // AC-GAME-004: Play typing sound every N characters
      if (props.typingSound && charIndex - lastSoundChar >= SOUND_INTERVAL) {
        audioManager.playTypingSound();
        lastSoundChar = charIndex;
      }
    }
    if (charIndex < props.text.length) {
      animFrameId = requestAnimationFrame(tick);
    } else {
      isComplete.value = true;
      emit('complete');
    }
  }
  animFrameId = requestAnimationFrame(tick);
}

function skipToEnd() {
  cancelAnimationFrame(animFrameId);
  displayedText.value = props.text;
  charIndex = props.text.length;
  isComplete.value = true;
  emit('complete');
}

watch(() => props.text, () => { startTyping(); });

onMounted(() => { startTyping(); });
onUnmounted(() => { cancelAnimationFrame(animFrameId); });

defineExpose({ skipToEnd, isComplete });
</script>

<style scoped>
.dialogue-box {
  background: var(--glass-bg, rgba(15, 10, 26, 0.8));
  backdrop-filter: blur(20px);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(167, 139, 250, 0.15);
  border-radius: 16px;
  padding: 20px 24px;
  cursor: pointer;
  transition: border-color 0.3s;
  position: relative;
}

.dialogue-box:hover {
  border-color: rgba(192, 132, 252, 0.3);
}

.dialogue-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.char-tag {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 14px;
  font-size: 13px;
  font-weight: 600;
  background: linear-gradient(135deg, rgba(192, 132, 252, 0.15), rgba(249, 168, 212, 0.1));
  color: var(--brand-primary);
}

.char-tag.narrator {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.emotion-tag {
  font-size: 11px;
  color: var(--brand-secondary);
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(249, 168, 212, 0.08);
}

.dialogue-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-main);
  min-height: 48px;
}

.text-content {
  letter-spacing: 0.02em;
}

.cursor {
  color: var(--brand-primary);
  animation: blink 0.8s ease-in-out infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.dialogue-hint {
  text-align: right;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
  opacity: 0.6;
}
</style>

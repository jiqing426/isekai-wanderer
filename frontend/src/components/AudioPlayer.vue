<template>
  <div class="audio-player" v-if="hasAudio">
    <button class="mute-btn" @click="toggleMute" :aria-label="isMuted ? 'Unmute' : 'Mute'">
      <span>{{ isMuted ? '🔇' : '🔊' }}</span>
    </button>
    <div class="volume-bar">
      <div class="volume-fill" :style="{ width: effectiveVolumePercent + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { getEmotionParams } from '@/constants/emotions';

/**
 * AudioPlayer — AC-048: Emotion-driven BGM volume multiplier.
 *
 * Props:
 *   src: audio file URL (optional, player hidden when empty)
 *   volume: base volume 0..1 (default 0.5)
 *
 * Exposes:
 *   emotionVolumeMultiplier (reactive)
 *   setEmotionVolumeMultiplier(emotion: string)
 *   isMuted, toggleMute()
 */
const props = withDefaults(defineProps<{
  src?: string;
  volume?: number;
}>(), {
  volume: 0.5,
});

const isMuted = ref(false);
const emotionVolumeMultiplier = ref(1);
let audioEl: HTMLAudioElement | null = null;

const hasAudio = computed(() => !!props.src);

const effectiveVolume = computed(() => {
  if (isMuted.value) return 0;
  return Math.min(props.volume * emotionVolumeMultiplier.value, 1);
});

const effectiveVolumePercent = computed(() => Math.round(effectiveVolume.value * 100));

function setEmotionVolumeMultiplier(emotion: string) {
  emotionVolumeMultiplier.value = getEmotionParams(emotion).bgmVolumeMultiplier;
}

function toggleMute() {
  isMuted.value = !isMuted.value;
}

function applyVolume() {
  if (audioEl) {
    audioEl.volume = effectiveVolume.value;
    audioEl.muted = effectiveVolume.value === 0;
  }
}

watch(effectiveVolume, () => { applyVolume(); });

watch(() => props.src, (newSrc) => {
  if (audioEl) {
    audioEl.pause();
    audioEl.src = '';
  }
  if (newSrc) {
    if (!audioEl) {
      audioEl = new Audio(newSrc);
      audioEl.loop = true;
    } else {
      audioEl.src = newSrc;
    }
    applyVolume();
    audioEl.play().catch(() => { /* autoplay blocked */ });
  }
}, { immediate: true });

onUnmounted(() => {
  if (audioEl) {
    audioEl.pause();
    audioEl.src = '';
    audioEl = null;
  }
});

defineExpose({
  emotionVolumeMultiplier,
  setEmotionVolumeMultiplier,
  isMuted,
  toggleMute,
});
</script>

<style scoped>
.audio-player {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.06);
}
.mute-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 2px 4px;
  line-height: 1;
}
.volume-bar {
  width: 60px;
  height: 4px;
  background: rgba(167, 139, 250, 0.12);
  border-radius: 2px;
  overflow: hidden;
}
.volume-fill {
  height: 100%;
  background: var(--brand-primary, #4F46E5);
  border-radius: 2px;
  transition: width 0.3s ease;
}
</style>

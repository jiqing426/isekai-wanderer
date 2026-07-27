import { ref, watch, computed } from 'vue';
import { getEmotionParams } from '@/constants/emotions';

/**
 * Typewriter effect using requestAnimationFrame.
 * Renders characters at target FPS (default 30fps = ~33ms per char).
 * Click to skip: instantly shows full text.
 *
 * AC-048: Emotion speed multiplier support via setEmotionMultiplier().
 */
export function useTypewriter(
  sourceText: () => string,
  options: { fps?: number; charsPerFrame?: number } = {},
) {
  const baseFps = options.fps ?? 30;
  const charsPerFrame = options.charsPerFrame ?? 1;
  const displayedText = ref('');
  const isComplete = ref(false);
  const isAnimating = ref(false);

  // AC-048: emotion-driven speed multiplier
  const speedMultiplier = ref(1);

  let rafId: number | null = null;
  let charIndex = 0;
  let currentFullText = '';
  let lastFrameTime = 0;

  // Effective frame interval accounts for emotion speed multiplier
  const effectiveFrameInterval = computed(() => {
    const effectiveFps = baseFps * speedMultiplier.value;
    return 1000 / Math.max(effectiveFps, 1);
  });

  function setEmotionMultiplier(emotion: string) {
    speedMultiplier.value = getEmotionParams(emotion).typewriterSpeed;
  }

  function animate(timestamp: number) {
    if (!isAnimating.value) return;

    if (timestamp - lastFrameTime >= effectiveFrameInterval.value) {
      lastFrameTime = timestamp;
      const end = Math.min(charIndex + charsPerFrame, currentFullText.length);
      displayedText.value = currentFullText.slice(0, end);
      charIndex = end;

      if (charIndex >= currentFullText.length) {
        isAnimating.value = false;
        isComplete.value = true;
        return;
      }
    }

    rafId = requestAnimationFrame(animate);
  }

  function start(text: string) {
    stop();
    currentFullText = text;
    charIndex = 0;
    displayedText.value = '';
    isComplete.value = false;
    isAnimating.value = true;
    lastFrameTime = 0;
    rafId = requestAnimationFrame(animate);
  }

  function append(text: string) {
    currentFullText += text;
    if (!isAnimating.value && !isComplete.value) {
      isAnimating.value = true;
      lastFrameTime = 0;
      rafId = requestAnimationFrame(animate);
    }
  }

  function skip() {
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    displayedText.value = currentFullText;
    charIndex = currentFullText.length;
    isAnimating.value = false;
    isComplete.value = true;
  }

  function stop() {
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    isAnimating.value = false;
  }

  function reset() {
    stop();
    displayedText.value = '';
    currentFullText = '';
    charIndex = 0;
    isComplete.value = false;
    speedMultiplier.value = 1;
  }

  // Watch source text changes
  watch(sourceText, (newText) => {
    if (newText) {
      start(newText);
    }
  });

  const progress = computed(() => {
    if (!currentFullText) return 0;
    return Math.round((charIndex / currentFullText.length) * 100);
  });

  return {
    displayedText,
    isComplete,
    isAnimating,
    progress,
    speedMultiplier,
    start,
    append,
    skip,
    stop,
    reset,
    setEmotionMultiplier,
  };
}

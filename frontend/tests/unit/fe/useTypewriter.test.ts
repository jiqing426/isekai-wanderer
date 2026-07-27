import { describe, it, expect, vi } from 'vitest';
import { useTypewriter } from '@/composables/useTypewriter';

describe('useTypewriter', () => {
  // AC-048: Emotion speed multiplier
  describe('emotion speed multiplier', () => {
    it('should have default speed multiplier of 1x', () => {
      const { speedMultiplier } = useTypewriter(() => '');
      expect(speedMultiplier?.value).toBe(1);
    });

    it('should apply tense emotion multiplier (2x faster)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('tense');
      expect(speedMultiplier?.value).toBe(2);
    });

    it('should apply warm emotion multiplier (0.7x slower)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('warm');
      expect(speedMultiplier?.value).toBe(0.7);
    });

    it('should apply sad emotion multiplier (0.6x slower)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('sad');
      expect(speedMultiplier?.value).toBe(0.6);
    });

    it('should apply excited emotion multiplier (1.5x faster)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('excited');
      expect(speedMultiplier?.value).toBe(1.5);
    });

    it('should apply angry emotion multiplier (1.8x faster)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('angry');
      expect(speedMultiplier?.value).toBe(1.8);
    });

    it('should apply normal emotion multiplier (1x)', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('normal');
      expect(speedMultiplier?.value).toBe(1);
    });

    it('should fall back to 1x for unknown emotion', () => {
      const { setEmotionMultiplier, speedMultiplier } = useTypewriter(() => '');
      setEmotionMultiplier('unknown_emotion');
      expect(speedMultiplier?.value).toBe(1);
    });
  });
});

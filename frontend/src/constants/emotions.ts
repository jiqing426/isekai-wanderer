/**
 * AC-048: Emotion mapping table.
 * Maps emotion tags to typewriter speed multiplier and BGM volume multiplier.
 */

export interface EmotionParams {
  /** Typewriter speed multiplier: >1 = faster, <1 = slower */
  typewriterSpeed: number;
  /** BGM volume multiplier: >1 = louder, <1 = softer */
  bgmVolumeMultiplier: number;
  /** Emoji fallback for sprite display */
  emoji: string;
}

export const EMOTION_MAP: Record<string, EmotionParams> = {
  normal:    { typewriterSpeed: 1.0, bgmVolumeMultiplier: 1.0, emoji: '😐' },
  tense:     { typewriterSpeed: 2.0, bgmVolumeMultiplier: 0.7, emoji: '😬' },
  warm:      { typewriterSpeed: 0.7, bgmVolumeMultiplier: 0.8, emoji: '😊' },
  sad:       { typewriterSpeed: 0.6, bgmVolumeMultiplier: 0.5, emoji: '😢' },
  excited:   { typewriterSpeed: 1.5, bgmVolumeMultiplier: 1.2, emoji: '✨' },
  angry:     { typewriterSpeed: 1.8, bgmVolumeMultiplier: 1.1, emoji: '😠' },
  happy:     { typewriterSpeed: 1.2, bgmVolumeMultiplier: 1.0, emoji: '😊' },
  shy:       { typewriterSpeed: 0.8, bgmVolumeMultiplier: 0.7, emoji: '😳' },
  surprised: { typewriterSpeed: 1.4, bgmVolumeMultiplier: 1.0, emoji: '😲' },
  calm:      { typewriterSpeed: 0.8, bgmVolumeMultiplier: 0.6, emoji: '😌' },
  nervous:   { typewriterSpeed: 1.3, bgmVolumeMultiplier: 0.8, emoji: '😰' },
  loving:    { typewriterSpeed: 0.7, bgmVolumeMultiplier: 0.9, emoji: '💕' },
  neutral:   { typewriterSpeed: 1.0, bgmVolumeMultiplier: 1.0, emoji: '😐' },
};

export const DEFAULT_EMOTION: EmotionParams = EMOTION_MAP.normal;

export function getEmotionParams(emotion?: string): EmotionParams {
  if (!emotion) return DEFAULT_EMOTION;
  return EMOTION_MAP[emotion] ?? DEFAULT_EMOTION;
}

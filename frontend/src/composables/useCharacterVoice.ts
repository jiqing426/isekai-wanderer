/**
 * AC-GAME-017: Character voice TTS using Web Speech API.
 * Different characters get different voice configurations.
 */

import { ref } from 'vue';

export interface VoiceConfig {
  pitch?: number;       // 0-2, default 1
  rate?: number;        // 0.1-10, default 1
  volume?: number;      // 0-1, default 1
  lang?: string;        // e.g. 'zh-CN', 'ja-JP'
}

const DEFAULT_VOICES: Record<string, VoiceConfig> = {
  female: { pitch: 1.3, rate: 1.05, lang: 'zh-CN' },
  male: { pitch: 0.8, rate: 0.95, lang: 'zh-CN' },
  child: { pitch: 1.6, rate: 1.1, lang: 'zh-CN' },
  elder: { pitch: 0.7, rate: 0.85, lang: 'zh-CN' },
  narrator: { pitch: 1.0, rate: 0.9, lang: 'zh-CN' },
};

const voiceEnabled = ref(false);
const globalVolume = ref(0.8);

function getVoiceForCharacter(characterId?: string): VoiceConfig {
  if (!characterId) return DEFAULT_VOICES.narrator;
  // Hash character ID to pick a consistent voice type
  const hash = characterId.charCodeAt(0) % 4;
  const types = ['female', 'male', 'child', 'elder'];
  return DEFAULT_VOICES[types[hash]] || DEFAULT_VOICES.narrator;
}

function speak(text: string, characterId?: string, customConfig?: VoiceConfig) {
  if (!voiceEnabled.value) return;
  if (typeof window === 'undefined' || !window.speechSynthesis) return;

  // Stop any ongoing speech
  stop();

  const config = customConfig || getVoiceForCharacter(characterId);
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.pitch = config.pitch ?? 1;
  utterance.rate = config.rate ?? 1;
  utterance.volume = (config.volume ?? 1) * globalVolume.value;
  utterance.lang = config.lang ?? 'zh-CN';

  window.speechSynthesis.speak(utterance);
}

function stop() {
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}

function setVoiceEnabled(enabled: boolean) {
  voiceEnabled.value = enabled;
  if (!enabled) stop();
}

function setGlobalVolume(vol: number) {
  globalVolume.value = Math.max(0, Math.min(1, vol));
}

export function useCharacterVoice() {
  return {
    speak,
    stop,
    setVoiceEnabled,
    setGlobalVolume,
    voiceEnabled,
    globalVolume,
  };
}

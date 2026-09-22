/**
 * CR-005: Character voice TTS with CosyVoice + Web Speech API fallback.
 * 
 * 优先播放预生成的音频文件（来自阿里云 CosyVoice），
 * 失败时降级到浏览器 Web Speech API。
 */

import { ref } from 'vue';

export interface VoiceFallbackConfig {
  text?: string;
  voice?: string;      // 保留用于日志
  speed?: number;
  pitch?: number;
  volume?: number;
}

const voiceEnabled = ref(false);
const globalVolume = ref(0.8);
let currentAudio: HTMLAudioElement | null = null;
let selectedSpeechVoice: SpeechSynthesisVoice | null = null;

// 初始化时选择最佳中文语音（用于降级）
function initBestChineseVoice() {
  if (typeof window === 'undefined' || !window.speechSynthesis) return;
  
  const voices = window.speechSynthesis.getVoices();
  if (voices.length === 0) {
    window.speechSynthesis.onvoiceschanged = () => {
      selectBestVoice();
    };
  } else {
    selectBestVoice();
  }
}

function selectBestVoice() {
  const voices = window.speechSynthesis.getVoices();
  
  const preferredNames = [
    'Microsoft Xiaoxiao',
    'Microsoft Yaoyao',
    'Microsoft Huihui',
    'Google 普通话',
    'Ting-Ting',
    'Mei-Jia'
  ];
  
  for (const preferredName of preferredNames) {
    const voice = voices.find(v => v.name.includes(preferredName) && v.lang.startsWith('zh'));
    if (voice) {
      selectedSpeechVoice = voice;
      return;
    }
  }
  
  const chineseVoice = voices.find(v => v.lang.startsWith('zh'));
  if (chineseVoice) {
    selectedSpeechVoice = chineseVoice;
  }
}

// 立即初始化
initBestChineseVoice();

/**
 * 播放预生成的音频 URL
 */
function playAudioUrl(url: string, onEnd?: () => void): Promise<void> {
  return new Promise((resolve, reject) => {
    // 停止当前播放
    stopCurrentAudio();
    
    const audio = new Audio(url);
    audio.volume = globalVolume.value;
    currentAudio = audio;
    
    audio.onended = () => {
      currentAudio = null;
      onEnd?.();
      resolve();
    };
    
    audio.onerror = (e) => {
      currentAudio = null;
      reject(new Error(`Audio playback failed: ${e}`));
    };
    
    audio.play().catch(reject);
  });
}

/**
 * 降级到 Web Speech API
 */
function speakWithWebSpeech(text: string, config?: VoiceFallbackConfig, onEnd?: () => void) {
  if (!voiceEnabled.value) return;
  if (typeof window === 'undefined' || !window.speechSynthesis) return;

  // 停止当前播放
  stop();

  const utterance = new SpeechSynthesisUtterance(text);
  
  if (selectedSpeechVoice) {
    utterance.voice = selectedSpeechVoice;
  }
  
  utterance.pitch = config?.pitch ?? 1.2;
  utterance.rate = config?.speed ?? 1.0;
  utterance.volume = (config?.volume ?? 0.85) * globalVolume.value;
  utterance.lang = 'zh-CN';

  utterance.onend = () => {
    onEnd?.();
  };

  window.speechSynthesis.speak(utterance);
}

/**
 * 停止当前音频播放
 */
function stopCurrentAudio() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.currentTime = 0;
    currentAudio = null;
  }
}

/**
 * 播放语音（优先预生成音频，降级到 Web Speech）
 * 
 * @param audioUrl 预生成的音频 URL（可为 null）
 * @param fallbackConfig 降级配置（audioUrl 为 null 或播放失败时使用）
 * @param onEnd 播放结束回调
 */
async function speak(
  audioUrl: string | null,
  fallbackConfig?: VoiceFallbackConfig,
  onEnd?: () => void,
) {
  if (!voiceEnabled.value) return;

  try {
    if (audioUrl) {
      // 优先播放预生成的音频
      await playAudioUrl(audioUrl, onEnd);
      return;
    }
    
    // 没有音频 URL，降级到 Web Speech
    if (fallbackConfig?.text) {
      speakWithWebSpeech(fallbackConfig.text, fallbackConfig, onEnd);
    }
  } catch (err) {
    console.warn('[TTS] Audio playback failed, falling back to Web Speech:', err);
    // 降级到 Web Speech API
    if (fallbackConfig?.text) {
      speakWithWebSpeech(fallbackConfig.text, fallbackConfig, onEnd);
    }
  }
}

/**
 * 停止所有播放
 */
function stop() {
  stopCurrentAudio();
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

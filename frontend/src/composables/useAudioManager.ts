/**
 * AC-GAME-003: BGM management with fade transitions
 * AC-GAME-004: Typing sound effects via Web Audio API
 *
 * Uses Web Audio API to generate procedural sounds (no external assets needed).
 * BGM categories: calm, tense, warm, battle.
 * Typing sounds: short click/tap noise.
 */

import { ref } from 'vue';

// --- BGM via Web Audio API (procedural ambient tones) ---

const audioCtx = typeof window !== 'undefined'
  ? new (window.AudioContext || (window as any).webkitAudioContext)()
  : null;

let currentBgmGain: GainNode | null = null;
let currentBgmOscillators: OscillatorNode[] = [];
let bgmPlaying = false;

const FADE_DURATION = 1.5; // seconds for crossfade

// BGM presets: [frequency, waveform, gain] per category
const BGM_PRESETS: Record<string, Array<{ freq: number; type: OscillatorType; gain: number }>> = {
  calm: [
    { freq: 220, type: 'sine', gain: 0.06 },
    { freq: 330, type: 'sine', gain: 0.03 },
    { freq: 440, type: 'triangle', gain: 0.02 },
  ],
  tense: [
    { freq: 110, type: 'sawtooth', gain: 0.04 },
    { freq: 165, type: 'square', gain: 0.02 },
    { freq: 220, type: 'sine', gain: 0.05 },
  ],
  warm: [
    { freq: 261.63, type: 'sine', gain: 0.05 },
    { freq: 329.63, type: 'sine', gain: 0.04 },
    { freq: 392, type: 'triangle', gain: 0.03 },
  ],
  battle: [
    { freq: 82.41, type: 'sawtooth', gain: 0.06 },
    { freq: 110, type: 'square', gain: 0.04 },
    { freq: 164.81, type: 'sawtooth', gain: 0.03 },
  ],
};

// Map emotions to BGM categories
const EMOTION_TO_BGM: Record<string, string> = {
  calm: 'calm', peaceful: 'calm', neutral: 'calm',
  warm: 'warm', loving: 'warm', happy: 'warm', shy: 'warm',
  nervous: 'tense', angry: 'tense', sad: 'tense', surprised: 'tense',
  excited: 'battle',
};

/**
 * Map scene names to BGM categories (fallback to emotion-based).
 */
const SCENE_TO_BGM: Record<string, string> = {
  'forest': 'calm', 'garden': 'warm', 'castle': 'warm',
  'battlefield': 'battle', 'dungeon': 'tense', 'night': 'tense',
  'market': 'warm', 'temple': 'calm', 'mountain': 'calm',
};

function getBgmCategory(scene?: string, emotion?: string): string {
  if (scene) {
    const lower = scene.toLowerCase();
    for (const [key, cat] of Object.entries(SCENE_TO_BGM)) {
      if (lower.includes(key)) return cat;
    }
  }
  if (emotion) {
    return EMOTION_TO_BGM[emotion] || 'calm';
  }
  return 'calm';
}

function stopBgm(fadeOut = true) {
  if (!audioCtx || !currentBgmGain) return;

  if (fadeOut && bgmPlaying) {
    const now = audioCtx.currentTime;
    currentBgmGain.gain.linearRampToValueAtTime(0, now + FADE_DURATION);
    const oscs = currentBgmOscillators;
    const gain = currentBgmGain;
    setTimeout(() => {
      oscs.forEach((o) => { try { o.stop(); } catch {} });
      gain.disconnect();
    }, FADE_DURATION * 1000 + 100);
  } else {
    currentBgmOscillators.forEach((o) => { try { o.stop(); } catch {} });
    currentBgmGain.disconnect();
  }

  currentBgmOscillators = [];
  currentBgmGain = null;
  bgmPlaying = false;
}

function startBgm(category: string, volume = 0.5) {
  if (!audioCtx) return;
  if (audioCtx.state === 'suspended') audioCtx.resume();

  const preset = BGM_PRESETS[category] || BGM_PRESETS.calm;
  const masterGain = audioCtx.createGain();
  masterGain.gain.value = 0;
  masterGain.connect(audioCtx.destination);

  const oscillators: OscillatorNode[] = [];
  for (const p of preset) {
    const osc = audioCtx.createOscillator();
    osc.type = p.type;
    osc.frequency.value = p.freq;
    const oscGain = audioCtx.createGain();
    oscGain.gain.value = p.gain * volume;
    osc.connect(oscGain);
    oscGain.connect(masterGain);
    osc.start();
    oscillators.push(osc);
  }

  // Fade in
  const now = audioCtx.currentTime;
  masterGain.gain.linearRampToValueAtTime(volume * 0.3, now + FADE_DURATION);

  currentBgmGain = masterGain;
  currentBgmOscillators = oscillators;
  bgmPlaying = true;
}

// --- Typing sound effect ---

let typingEnabled = ref(false);
let typingVolume = ref(0.3);

function playTypingSound() {
  if (!audioCtx || !typingEnabled.value) return;
  if (audioCtx.state === 'suspended') audioCtx.resume();

  const osc = audioCtx.createOscillator();
  osc.type = 'sine';
  osc.frequency.value = 800 + Math.random() * 400; // slight variation

  const gain = audioCtx.createGain();
  gain.gain.value = typingVolume.value * 0.15;

  const now = audioCtx.currentTime;
  gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);

  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.start(now);
  osc.stop(now + 0.05);
}

// --- Ambient environmental sounds (AC-GAME-016) ---

let ambientGain: GainNode | null = null;
let ambientOscillators: OscillatorNode[] = [];
let ambientPlaying = false;
let lastAmbientScene = '';

const AMBIENT_PRESETS: Record<string, Array<{ freq: number; type: OscillatorType; gain: number; detune?: number }>> = {
  forest: [
    { freq: 120, type: 'sine', gain: 0.03 },
    { freq: 180, type: 'sine', gain: 0.02, detune: 5 },
    { freq: 90, type: 'triangle', gain: 0.01 },
  ],
  ocean: [
    { freq: 60, type: 'sine', gain: 0.04 },
    { freq: 80, type: 'sine', gain: 0.03, detune: -3 },
    { freq: 100, type: 'triangle', gain: 0.02 },
  ],
  dungeon: [
    { freq: 50, type: 'sine', gain: 0.03 },
    { freq: 70, type: 'sawtooth', gain: 0.01 },
  ],
  market: [
    { freq: 200, type: 'sine', gain: 0.02 },
    { freq: 300, type: 'triangle', gain: 0.015 },
    { freq: 150, type: 'sine', gain: 0.01 },
  ],
  castle: [
    { freq: 150, type: 'sine', gain: 0.02 },
    { freq: 200, type: 'triangle', gain: 0.015 },
  ],
};

const SCENE_TO_AMBIENT: Record<string, string> = {
  forest: 'forest', garden: 'forest', mountain: 'forest',
  ocean: 'ocean', beach: 'ocean',
  dungeon: 'dungeon', night: 'dungeon',
  market: 'market', village: 'market',
  castle: 'castle', palace: 'castle', throne: 'castle',
};

function getAmbientCategory(scene?: string): string | null {
  if (!scene) return null;
  const lower = scene.toLowerCase();
  for (const [key, cat] of Object.entries(SCENE_TO_AMBIENT)) {
    if (lower.includes(key)) return cat;
  }
  return null;
}

function stopAmbient(fadeOut = true) {
  if (!audioCtx || !ambientGain) return;
  if (fadeOut && ambientPlaying) {
    const now = audioCtx.currentTime;
    ambientGain.gain.linearRampToValueAtTime(0, now + 2);
    const oscs = ambientOscillators;
    const gain = ambientGain;
    setTimeout(() => {
      oscs.forEach((o) => { try { o.stop(); } catch {} });
      gain.disconnect();
    }, 2100);
  } else {
    ambientOscillators.forEach((o) => { try { o.stop(); } catch {} });
    ambientGain.disconnect();
  }
  ambientOscillators = [];
  ambientGain = null;
  ambientPlaying = false;
  lastAmbientScene = '';
}

function startAmbient(category: string, volume = 0.3) {
  if (!audioCtx) return;
  if (audioCtx.state === 'suspended') audioCtx.resume();
  const preset = AMBIENT_PRESETS[category];
  if (!preset) return;
  const masterGain = audioCtx.createGain();
  masterGain.gain.value = 0;
  masterGain.connect(audioCtx.destination);
  const oscillators: OscillatorNode[] = [];
  for (const p of preset) {
    const osc = audioCtx.createOscillator();
    osc.type = p.type;
    osc.frequency.value = p.freq;
    if (p.detune) osc.detune.value = p.detune;
    const oscGain = audioCtx.createGain();
    oscGain.gain.value = p.gain * volume;
    osc.connect(oscGain);
    oscGain.connect(masterGain);
    osc.start();
    oscillators.push(osc);
  }
  const now = audioCtx.currentTime;
  masterGain.gain.linearRampToValueAtTime(volume * 0.2, now + 2);
  ambientGain = masterGain;
  ambientOscillators = oscillators;
  ambientPlaying = true;
}

// --- Public API ---

let lastBgmCategory = '';

export function useAudioManager() {
  function switchBgm(scene?: string, emotion?: string, volume = 0.5) {
    const category = getBgmCategory(scene, emotion);
    if (category === lastBgmCategory && bgmPlaying) return;
    stopBgm(true);
    startBgm(category, volume);
    lastBgmCategory = category;
  }

  // AC-GAME-016: Ambient environmental sounds
  function switchAmbient(scene?: string, volume = 0.3) {
    const category = getAmbientCategory(scene);
    if (category === lastAmbientScene && ambientPlaying) return;
    stopAmbient(true);
    if (category) {
      startAmbient(category, volume);
      lastAmbientScene = category;
    }
  }

  function stopAll() {
    stopBgm(false);
    stopAmbient(false);
    lastBgmCategory = '';
    lastAmbientScene = '';
  }

  function setTypingEnabled(enabled: boolean) {
    typingEnabled.value = enabled;
  }

  function setTypingVolume(vol: number) {
    typingVolume.value = Math.max(0, Math.min(1, vol));
  }

  return {
    switchBgm,
    switchAmbient,
    stopAll,
    playTypingSound,
    setTypingEnabled,
    setTypingVolume,
    typingEnabled,
    typingVolume,
  };
}

<template>
  <div class="page-bg">
    <div class="character-detail-page" v-if="character">
      <!-- Back Button -->
      <div class="back-bar">
        <n-button text @click="router.back()">← {{ $t('common.back') }}</n-button>
      </div>

      <!-- Header Card -->
      <div class="detail-header glass-card">
        <div class="header-avatar">
          <div class="avatar-circle">{{ nameInitial(character.name) }}</div>
        </div>
        <div class="header-info">
          <h1 class="char-name">{{ character.name }}</h1>
          <div class="char-meta">
            <n-tag size="small" :bordered="false" type="primary">{{ personalityLabel }}</n-tag>
            <span v-if="character.script_title" class="meta-script">📖 {{ character.script_title }}</span>
          </div>
        </div>
      </div>

      <!-- Affection Section -->
      <section class="section glass-card" v-if="character.affection">
        <div class="section-title-row">
          <h2>💕 {{ $t('character.affection') }}</h2>
          <n-button size="small" type="primary" secondary @click="openGiftModal" class="gift-btn">
            🎁 {{ $t('character.sendGift') }}
          </n-button>
        </div>
        <AffectionMeter :value="character.affection.value" :label="character.name" />
        <div class="aff-stats" v-if="character.affection.next_level">
          <div class="stat-item">
            <span class="stat-label">{{ $t('character.currentLevel') }}</span>
            <span class="stat-value" :style="{ color: currentLevelColor }">{{ character.affection.level_label }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ $t('character.nextLevel') }}</span>
            <span class="stat-value">{{ character.affection.next_level.level_label }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">{{ $t('character.remaining') }}</span>
            <span class="stat-value highlight" v-if="character.affection.next_level.remaining != null && !isNaN(character.affection.next_level.remaining)">
              {{ character.affection.next_level.remaining }} {{ $t('character.points') }}
            </span>
            <span class="stat-value" v-else>{{ $t('characterDetail.maxLevel') }}</span>
          </div>
        </div>
      </section>

      <!-- Profile Section -->
      <section class="section glass-card">
        <h2>📋 {{ $t('character.profile') }}</h2>
        <div class="profile-grid">
          <div class="profile-item">
            <span class="profile-label">{{ $t('character.bio') }}</span>
            <p class="profile-text">{{ character.description }}</p>
          </div>
          <div class="profile-item" v-if="parsedLikes.length">
            <span class="profile-label">{{ $t('character.likes') }}</span>
            <div class="tag-list">
              <n-tag v-for="like in parsedLikes" :key="like" size="small" :bordered="false" type="success">
                ❤️ {{ like }}
              </n-tag>
            </div>
          </div>
          <div class="profile-item" v-if="character.dislikes && character.dislikes.length">
            <span class="profile-label">{{ $t('character.dislikes') }}</span>
            <div class="tag-list">
              <n-tag v-for="dislike in (character.dislikes || [])" :key="dislike" size="small" :bordered="false" type="error">
                💔 {{ dislike }}
              </n-tag>
            </div>
          </div>
          <div class="profile-item" v-if="character.greeting">
            <span class="profile-label">{{ $t('character.greeting') }}</span>
            <p class="profile-text quote">"{{ character.greeting }}"</p>
          </div>
        </div>
      </section>

      <!-- Personality Analysis Section -->
      <section class="section glass-card">
        <h2>📊 {{ $t('characterDetail.personality') }}</h2>
        <div class="personality-analysis">
          <div class="personality-list" v-if="personalityTraits.length > 0">
            <div v-for="trait in personalityTraits" :key="trait.key" class="personality-item">
              <div class="trait-header">
                <span class="trait-label">{{ trait.label }}</span>
                <span class="trait-value">{{ trait.value }}%</span>
              </div>
              <div class="trait-bar-container">
                <div class="trait-bar">
                  <div 
                    class="trait-bar-fill" 
                    :style="{ width: trait.value + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-personality">
            <p>{{ $t('characterDetail.noPersonalityData') }}</p>
          </div>
        </div>
      </section>

      <!-- Voice Preview Section -->
      <section class="section glass-card">
        <h2>🎤 {{ $t('characterDetail.voicePreview') }}</h2>
        <div class="voice-list">
          <div v-for="voice in voiceSamples" :key="voice.id" class="voice-item">
            <div class="voice-info">
              <span class="voice-icon">{{ voice.icon }}</span>
              <span class="voice-label">{{ voice.label }}</span>
            </div>
            <button 
              v-if="canPlayVoice" 
              class="voice-play-btn"
              :class="{ 'is-playing': playingVoiceId === voice.id }"
              @click="playVoice(voice.id)"
            >
              <span v-if="playingVoiceId === voice.id" class="playing-indicator">⏸️</span>
              <span v-else>▶️</span>
            </button>
            <button 
              v-else 
              class="voice-lock-btn"
              @click="showUpgradePrompt"
            >
              🔒
            </button>
          </div>
        </div>
        <div v-if="!canPlayVoice" class="voice-upgrade-hint">
          💎 {{ $t('characterDetail.unlockVoice') }}
        </div>
      </section>

      <!-- Character Portrait Section (暂时隐藏) -->
      <!-- <section class="section glass-card">
        <h2>🎭 {{ $t('characterDetail.characterArt') }}</h2>
        <div class="portrait-display">
          <div class="portrait-main">
            <div class="portrait-container" :class="`emotion-${currentEmotion}`">
              <img v-if="currentPortraitUrl" :src="currentPortraitUrl" :alt="character.name" class="portrait-image" />
              <div v-else class="portrait-placeholder">
                <span class="portrait-emoji">{{ emotionEmoji(currentEmotion) }}</span>
              </div>
            </div>
            <div class="emotion-info">
              <span class="emotion-label">{{ $t('characterDetail.currentEmotion') }}</span>
              <span class="emotion-value">{{ emotionLabel(currentEmotion) }}</span>
            </div>
          </div>
          <div class="emotion-switcher">
            <h3>{{ $t('characterDetail.switchEmotion') }}</h3>
            <div class="emotion-buttons">
              <button
                v-for="emotion in availableEmotions"
                :key="emotion"
                class="emotion-btn"
                :class="{ active: currentEmotion === emotion }"
                @click="switchEmotion(emotion)"
              >
                <span class="btn-emoji">{{ emotionEmoji(emotion) }}</span>
                <span class="btn-label">{{ emotionLabel(emotion) }}</span>
              </button>
            </div>
          </div>
        </div>
      </section> -->

      <!-- Actions (暂时隐藏) -->
      <!-- <div class="action-bar">
        <n-button type="primary" size="large" @click="startChat" block>
          💬 {{ $t('character.startChat') }}
        </n-button>
      </div> -->
    </div>

    <!-- Loading / Error States -->
    <div class="loading-state" v-else-if="loading">
      <n-spin size="large" />
    </div>
    <div class="error-state glass-card" v-else-if="error">
      <n-result status="error" :title="$t('common.error')" :description="error">
        <template #footer>
          <n-button @click="loadCharacter">{{ $t('character.retry') }}</n-button>
        </template>
      </n-result>
    </div>

    <!-- ═══ 礼物弹框 ═══ -->
    <!-- 礼物选择 -->
    <!-- 统一送礼组件 -->
    <GiftModal
      v-model="showGiftModal"
      :target-name="character?.name || $t('characterDetail.character')"
      :target-id="characterId"
      @gift-sent="onGiftSent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useMessage } from 'naive-ui';
import { useHead } from '@vueuse/head';
import { useI18n } from 'vue-i18n';
import { gameApi } from '@/api/game';
import type { CharacterDetail, VoiceSample } from '@/api/game';
import AffectionMeter from '@/components/AffectionMeter.vue';
import GiftModal from '@/components/GiftModal.vue';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const message = useMessage();

const character = ref<CharacterDetail | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const characterId = route.params.characterId as string;

// 表情切换 (暂时隐藏)
// const currentEmotion = ref<string>('normal');
// const availableEmotions = ['normal', 'happy', 'sad', 'angry', 'shy'];

// const currentPortraitUrl = computed(() => {
//   if (!character.value?.sprites) return '';
//   const sprite = character.value.sprites.find(s => s.emotion === currentEmotion.value);
//   return sprite?.image_url || '';
// });

// function switchEmotion(emotion: string) {
//   currentEmotion.value = emotion;
// }

// 性格分析数据
const personalityTraits = ref<Array<{ key: string; label: string; value: number; average: number }>>([]);
const loadingPersonality = ref(false);

// 解析 likes 字段（可能是数组或对象）
const parsedLikes = computed(() => {
  const likes = character.value?.likes;
  if (!likes) return [];
  if (Array.isArray(likes)) return likes;
  if (typeof likes === 'object' && 'items' in likes) return likes.items || [];
  return [];
});

async function loadPersonality() {
  if (!character.value) return;
  loadingPersonality.value = true;
  try {
    const response = await gameApi.getCharacterPersonality(character.value.id);
    personalityTraits.value = response.personality.traits;
  } catch (err) {
    console.error('Failed to load personality:', err);
    // Fallback to empty array
    personalityTraits.value = [];
  } finally {
    loadingPersonality.value = false;
  }
}

// 语音试听相关 (CR-005: 支持预生成音频 + 降级)
const voiceSamples = ref<VoiceSample[]>([]);
const loadingVoices = ref(false);

async function loadVoices() {
  if (!character.value) return;
  loadingVoices.value = true;
  try {
    const response = await gameApi.getCharacterVoices(character.value.id);
    voiceSamples.value = response.voices;
  } catch (err) {
    console.error('Failed to load voices:', err);
    voiceSamples.value = [];
  } finally {
    loadingVoices.value = false;
  }
}

const playingVoiceId = ref<string | null>(null);

// 检查用户是否可以播放语音（Standard/Premium）
const userSubscription = ref<string>('free');
const loadingSubscription = ref(false);

async function loadUserSubscription() {
  loadingSubscription.value = true;
  try {
    const response = await gameApi.getUserSubscription();
    // 兼容两种返回格式
    userSubscription.value = response.currentPlanId || response.subscription?.plan || 'free';
  } catch (err) {
    console.error('Failed to load subscription:', err);
    userSubscription.value = 'free';
  } finally {
    loadingSubscription.value = false;
  }
}

const canPlayVoice = computed(() => {
  return userSubscription.value === 'standard' || userSubscription.value === 'premium';
});

import { useCharacterVoice } from '@/composables/useCharacterVoice';

const { setVoiceEnabled } = useCharacterVoice();

// 启用语音功能
onMounted(() => {
  setVoiceEnabled(true);
});

// CR-036: 播放语音 — 调用后端实时合成接口
async function playVoice(voiceId: string) {
  const voice = voiceSamples.value.find(v => v.id === voiceId);
  if (!voice) return;
  
  if (playingVoiceId.value === voiceId) {
    playingVoiceId.value = null;
    return;
  }
  
  playingVoiceId.value = voiceId;
  
  try {
    const emotion = voice.label || t('characterDetail.greeting');
    
    // 使用 api 工具类发请求（自动带 token）
    const response = await fetch(
      `/api/v1/characters/${character.value?.id}/voices/synthesize?emotion=${encodeURIComponent(emotion)}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getCookieValue('isekai_access_token')}`,
        },
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const blob = await response.blob();
    const audioUrl = URL.createObjectURL(blob);
    
    const audio = new Audio(audioUrl);
    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      if (playingVoiceId.value === voiceId) {
        playingVoiceId.value = null;
      }
    };
    audio.onerror = () => {
      URL.revokeObjectURL(audioUrl);
      playingVoiceId.value = null;
    };
    audio.play();
  } catch (err) {
    console.error('Voice synthesis failed:', err);
    playingVoiceId.value = null;
    message.error(t('characterDetail.voiceSynthesisError'));
  }
}

function getCookieValue(name: string): string {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : '';
}

function showUpgradePrompt() {
  message.info(t('characterDetail.unlockVoiceHint'));
}

// ── 礼物相关 ──
const showGiftModal = ref(false);

const personalityMap: Record<string, () => string> = {
  gentle: () => t('character.gentle'),
  tsundere: () => t('character.tsundere'),
  cool: () => t('character.cool'),
  energetic: () => t('character.energetic'),
  mysterious: () => t('character.mysterious'),
  formal: () => t('character.formal'),
  loyal: () => t('character.loyal'),
  brave: () => t('character.brave'),
  wisdom: () => t('character.wisdom'),
  charisma: () => t('character.charisma'),
  luck: () => t('character.luck'),
  intelligence: () => t('character.intelligence'),
  strength: () => t('character.strength'),
  agility: () => t('character.agility'),
  charm: () => t('character.charm'),
  wit: () => t('character.wit'),
  courage: () => t('character.courage'),
  kindness: () => t('character.kindness'),
  humor: () => t('character.humor'),
  passion: () => t('character.passion'),
  calm: () => t('character.calm'),
  creative: () => t('character.creative'),
  determined: () => t('character.determined'),
  empathetic: () => t('character.empathetic'),
  optimistic: () => t('character.optimistic'),
  rational: () => t('character.rational'),
  sensitive: () => t('character.sensitive'),
  stubborn: () => t('character.stubborn'),
  wise: () => t('character.wise')
};

// const emotionMap: Record<string, string> = {
//   normal: '😌', happy: '😊', sad: '😢', angry: '😠',
//   surprised: '😲', tense: '😰', warm: '🥰', excited: '🤩',
//   fearful: '😨', calm: '😌',
// };

const levelColors: Record<string, string> = {
  acquaintance: '#9CA3AF',
  ambiguous: '#F472B6',
  trust: '#38BDF8',
  bond: '#A78BFA',
  love: '#F43F5E',
};

const personalityLabel = computed(() => {
  const raw = character.value?.personality;
  if (!raw) return '';
  
  // If it's already an object (not a string), use it directly
  let parsed: any = raw;
  
  // If it's a string, try to parse it as JSON
  if (typeof raw === 'string') {
    try {
      parsed = JSON.parse(raw);
    } catch {
      // Not JSON, use as-is
      const fn = personalityMap[raw];
      return fn ? fn() : raw;
    }
  }
  
  // If it's an array, join with Chinese punctuation
  if (Array.isArray(parsed)) {
    return parsed.map((item: string) => {
      const fn = personalityMap[item];
      return fn ? fn() : item;
    }).join('、');
  }
  
  // If it's an object, convert keys to Chinese labels
  if (typeof parsed === 'object' && parsed !== null) {
    return Object.entries(parsed)
      .filter(([_, value]) => Number(value) > 0) // Only show traits with value > 0
      .map(([key, value]) => {
        const fn = personalityMap[key];
        const label = fn ? fn() : key;
        return `${label} ${value}%`;
      })
      .join('、');
  }
  
  return String(raw);
});

const currentLevelColor = computed(() =>
  levelColors[character.value?.affection?.level || 'acquaintance'] || '#9CA3AF'
);

function nameInitial(name: string): string {
  return name.charAt(0);
}

// function emotionEmoji(emotion: string): string {
//   return emotionMap[emotion] || '😌';
// }

// function emotionLabel(emotion: string): string {
//   return emotionMap[emotion] ? emotionMap[emotion] : emotion;
// }

// function startChat() {
//   if (character.value?.script_id) {
//     router.push(`/game?script=${character.value.script_id}&character=${character.value.id}`);
//   } else {
//     message.warning(t('character.noScriptInfo'));
//   }
// }

function openGiftModal() {
  showGiftModal.value = true;
}

function onGiftSent() {
  // 好感度由 GiftModal 回调刷新，这里可以做额外处理
}

async function loadCharacter() {
  const id = route.params.characterId as string;
  if (!id) {
    error.value = t('character.missingId');
    return;
  }

  loading.value = true;
  error.value = null;

  try {
    character.value = await gameApi.getCharacterDetail(id);

    useHead({
      title: `${character.value.name} - Isekai Wanderer`,
      meta: [{ name: 'description', content: character.value.description }],
    });
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('character.loadFailed');
    message.error(error.value);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await loadCharacter();
  if (character.value) {
    // Load all related data in parallel
    await Promise.all([
      loadPersonality(),
      loadVoices(),
      loadUserSubscription()
    ]);
    
    // 触发角色探索任务进度
    try {
      await gameApi.updateDailyTaskProgress('task_profile');
    } catch (err) {
      console.error('Failed to update daily task progress:', err);
    }
  }
});
</script>

<style scoped>
.character-detail-page { max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }
.back-bar { margin-bottom: 16px; }
.detail-header {
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 24px;
  margin-bottom: 20px;
}
.header-avatar { flex-shrink: 0; }
.avatar-circle {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3);
}
.header-info { flex: 1; min-width: 0; }
.char-name { font-size: 28px; font-weight: 700; color: var(--text-main); margin: 0 0 8px 0; }
.char-meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.meta-script { font-size: 13px; color: var(--text-muted); }

/* 好感度标题行 */
.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-title-row h2 { margin: 0; }
.gift-btn {
  flex-shrink: 0;
  font-weight: 600;
}

.section { margin-bottom: 20px; padding: 20px; }
.section h2 { font-size: 18px; font-weight: 600; color: var(--text-main); }
.aff-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(167, 139, 250, 0.1);
}
.stat-item { text-align: center; }
.stat-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.stat-value { font-size: 16px; font-weight: 600; color: var(--text-main); }
.stat-value.highlight { color: var(--brand-primary); }
.profile-grid { display: flex; flex-direction: column; gap: 16px; }
.profile-label { display: block; font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 6px; }
.profile-text { font-size: 14px; color: var(--text-main); line-height: 1.6; margin: 0; }
.profile-text.quote { font-style: italic; color: var(--text-subtle); padding-left: 12px; border-left: 3px solid var(--brand-primary); }
.tag-list { display: flex; gap: 6px; flex-wrap: wrap; }
/* 角色立绘展示 */
.portrait-display {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.portrait-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.portrait-container {
  width: 280px;
  height: 380px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(236, 72, 153, 0.1));
  border: 2px solid rgba(167, 139, 250, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
}

.portrait-container:hover {
  border-color: rgba(167, 139, 250, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.25);
}

.portrait-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.portrait-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
}

.portrait-emoji {
  font-size: 120px;
}

.emotion-info {
  margin-top: 16px;
  text-align: center;
}

.emotion-label {
  font-size: 14px;
  color: var(--text-muted);
}

.emotion-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--brand-primary);
  margin-left: 8px;
}

.emotion-switcher {
  flex: 1;
}

.emotion-switcher h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  margin: 0 0 16px 0;
}

.emotion-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.emotion-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: 12px;
  background: rgba(167, 139, 250, 0.05);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.emotion-btn:hover {
  border-color: rgba(167, 139, 250, 0.4);
  background: rgba(167, 139, 250, 0.1);
  transform: translateX(4px);
}

.emotion-btn.active {
  border-color: var(--brand-primary);
  background: rgba(167, 139, 250, 0.15);
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.2);
}

.btn-emoji {
  font-size: 28px;
}

.btn-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

/* 表情动画 */
.portrait-container.emotion-normal {
  animation: emotionFade 0.3s ease;
}

.portrait-container.emotion-happy {
  animation: emotionBounce 0.4s ease;
}

.portrait-container.emotion-sad {
  animation: emotionFade 0.3s ease;
}

.portrait-container.emotion-angry {
  animation: emotionShake 0.4s ease;
}

.portrait-container.emotion-shy {
  animation: emotionFade 0.3s ease;
}

@keyframes emotionFade {
  from {
    opacity: 0.7;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes emotionBounce {
  0% {
    transform: scale(0.95);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes emotionShake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .portrait-display {
    flex-direction: column;
  }
  
  .portrait-container {
    width: 240px;
    height: 320px;
  }
  
  .portrait-emoji {
    font-size: 100px;
  }
  
  .emotion-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .emotion-btn {
    flex: 1;
    min-width: 120px;
  }
}

/* 性格分析 */
.personality-analysis {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.personality-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.personality-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.trait-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.trait-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.trait-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--brand-primary);
}

.trait-bar-container {
  width: 100%;
}

.trait-bar {
  width: 100%;
  height: 8px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.trait-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
  background: linear-gradient(90deg, #a78bfa, #ec4899);
}

.no-personality {
  text-align: center;
  padding: 32px;
  color: var(--text-muted);
}

/* 语音试听 */
.voice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.voice-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: rgba(167, 139, 250, 0.05);
  border: 1px solid rgba(167, 139, 250, 0.1);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.voice-item:hover {
  background: rgba(167, 139, 250, 0.08);
  border-color: rgba(167, 139, 250, 0.2);
}

.voice-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.voice-icon {
  font-size: 24px;
}

.voice-label {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
}

.voice-play-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a78bfa, #ec4899);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-play-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.4);
}

.voice-play-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.playing-indicator {
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.voice-lock-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(156, 163, 175, 0.2);
  border: 1px solid rgba(156, 163, 175, 0.3);
  color: rgba(156, 163, 175, 0.8);
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.voice-lock-btn:hover {
  background: rgba(156, 163, 175, 0.3);
  border-color: rgba(156, 163, 175, 0.5);
}

.voice-upgrade-hint {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 8px;
  color: #fbbf24;
  font-size: 14px;
  text-align: center;
}

.action-bar { display: flex; flex-direction: column; gap: 12px; margin-top: 24px; }
.loading-state, .error-state { max-width: 480px; margin: 80px auto; padding: 48px 24px; text-align: center; }

/* ═══ 礼物弹框 ═══ */
.gift-modal-body { display: flex; flex-direction: column; gap: 16px; }
.gift-balance-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(251, 191, 36, 0.06);
  border-radius: 10px;
  border: 1px solid rgba(251, 191, 36, 0.12);
}
.gift-balance-label { font-size: 13px; color: var(--text-muted); }
.gift-balance-value { font-size: 16px; font-weight: 700; color: #fbbf24; }

.gift-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.gift-card {
  padding: 16px 12px;
  border-radius: 12px;
  background: rgba(167, 139, 250, 0.04);
  border: 1px solid rgba(167, 139, 250, 0.08);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}
.gift-card:hover:not(.disabled) {
  border-color: rgba(192, 132, 252, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.1);
}
.gift-card.selected {
  border-color: var(--brand-primary);
  box-shadow: 0 0 16px rgba(139, 92, 246, 0.15);
}
.gift-card.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.gift-icon { font-size: 32px; display: block; margin-bottom: 6px; }
.gift-name { font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 6px; }
.gift-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}
.gift-cost { color: #fbbf24; font-weight: 600; }
.gift-bonus { color: var(--text-muted); font-weight: 600; }
.gift-bonus.high { color: #f472b6; }

/* 确认弹框 */
.confirm-card { padding: 28px; text-align: center; }
.confirm-icon { font-size: 48px; margin-bottom: 8px; }
.confirm-title { font-size: 18px; font-weight: 700; color: var(--text-main); margin: 0 0 10px; }
.confirm-name { font-size: 16px; font-weight: 600; color: var(--text-main); margin-bottom: 6px; }
.confirm-meta { display: flex; justify-content: center; gap: 14px; font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
.confirm-meta .bonus { color: #f472b6; }
.confirm-desc { font-size: 12px; color: var(--text-subtle); font-style: italic; margin: 0 0 12px; }
.confirm-target { font-size: 14px; color: var(--text-main); margin-bottom: 18px; }
.confirm-actions { display: flex; gap: 12px; margin-top: 8px; }
.confirm-actions :deep(.n-button) { flex: 1; }

/* 结果弹框 */
.result-card { padding: 32px; text-align: center; }
.result-icon { font-size: 48px; margin-bottom: 8px; }
.result-title { font-size: 20px; font-weight: 700; color: var(--text-main); margin: 0 0 16px; }
.result-stats { display: flex; justify-content: center; gap: 20px; margin-bottom: 20px; }
.result-stat { text-align: center; }
.result-label { display: block; font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
.result-value { font-size: 16px; font-weight: 700; color: var(--text-main); }
.result-value.up { color: #f472b6; }
</style>

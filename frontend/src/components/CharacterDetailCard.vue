<template>
  <div class="character-detail-card" :class="{ selected: isSelected, locked: isPlayable && !isUnlocked }" @click="$emit('select')">
    <!-- CR-028: 可扮演标识角标 -->
    <span v-if="isPlayable && isUnlocked" class="playable-badge">{{ $t('characterDetailCard.playable') }}</span>
    
    <!-- 角色头像和基础信息 -->
    <div class="character-header">
      <div class="character-avatar">
        <img v-if="!showPlaceholder(character)" :src="character.avatar_url" :alt="character.name" @error="handleImageError(character.id)" />
        <span v-else>{{ character.name.charAt(0) }}</span>
      </div>
      <div class="character-basic">
        <h3>{{ character.name }}</h3>
        <p class="character-desc">{{ character.description || $t('characterDetailCard.noDescription') }}</p>
        <div class="basic-info">
          <span v-if="character.age">{{ $t('characterDetailCard.yearsOld', { age: character.age }) }}</span>
          <span v-if="character.height">{{ character.height }}cm</span>
          <span v-if="character.birthday">{{ character.birthday }}</span>
        </div>
      </div>
    </div>
    
    <!-- CR-028: 锁定角色覆盖层 -->
    <div v-if="isPlayable && !isUnlocked" class="card-locked-overlay">
      <span class="card-locked-icon">🔒</span>
      <span v-if="unlockType === 'paid' && unlockPrice" class="card-locked-price">
        💎 {{ unlockPrice }}
      </span>
      <span v-else-if="unlockType === 'subscription'" class="card-locked-subscription">
        {{ $t('characterDetailCard.subscriptionExclusive') }}
      </span>
    </div>

    <!-- 喜好标签 -->
    <div class="character-likes" v-if="character.likes && character.likes.length > 0">
      <span class="likes-label">{{ $t('characterDetailCard.likesLabel') }}</span>
      <div class="likes-tags">
        <span v-for="like in character.likes" :key="like" class="like-tag">
          {{ like }}
        </span>
      </div>
    </div>

    <!-- 性格特征进度条 -->
    <div class="personality-traits" v-if="parsedPersonality && Object.keys(parsedPersonality).length > 0">
      <h4>{{ $t('characterDetailCard.personalityTitle') }}</h4>
      <div class="trait-item" v-for="(value, key) in parsedPersonality" :key="key">
        <span class="trait-label">{{ getPersonalityLabel(String(key)) }}</span>
        <div class="trait-bar">
          <div class="trait-fill" :style="{ width: value + '%' }"></div>
        </div>
        <span class="trait-value">{{ value }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useI18n } from 'vue-i18n';

interface Character {
  id: string;
  name: string;
  description?: string;
  age?: number;
  height?: number;
  birthday?: string;
  likes?: string[];
  personality?: Record<string, any> | string;
  avatar_url?: string;
  is_main?: boolean;
}

const { t } = useI18n();

const props = defineProps<{
  character: Character;
  isSelected: boolean;
  /** CR-028: 是否可扮演 */
  isPlayable?: boolean;
  /** CR-028: 是否已解锁（仅 isPlayable=true 时有意义） */
  isUnlocked?: boolean;
  /** CR-028: 解锁类型 free/paid/subscription */
  unlockType?: string;
  /** CR-028: 解锁价格 */
  unlockPrice?: number | null;
}>();

defineEmits<{
  (e: 'select'): void;
}>();

// BUG-030-004: 跟踪加载失败的头像图片
const imageErrors = ref<Set<string>>(new Set());

function handleImageError(characterId: string) {
  imageErrors.value.add(characterId);
}

function showPlaceholder(char: Character) {
  return !char.avatar_url || imageErrors.value.has(char.id);
}

// Parse personality - handle both string and object formats
const parsedPersonality = computed(() => {
  const raw = props.character.personality;
  if (!raw) return {};
  if (typeof raw === 'string') {
    try {
      return JSON.parse(raw);
    } catch {
      return {};
    }
  }
  return raw;
});

function getPersonalityLabel(key: string): string {
  const keyMap: Record<string, string> = {
    gentle: 'characterDetailCard.pGentle',
    tsundere: 'characterDetailCard.pTsundere',
    cool: 'characterDetailCard.pCool',
    energetic: 'characterDetailCard.pEnergetic',
    mysterious: 'characterDetailCard.pMysterious',
    loyal: 'characterDetailCard.pLoyal',
    brave: 'characterDetailCard.pBrave',
    brav: 'characterDetailCard.pBrave',
    wisdom: 'characterDetailCard.pWisdom',
    charisma: 'characterDetailCard.pCharisma',
    luck: 'characterDetailCard.pLuck',
    intelligence: 'characterDetailCard.pIntelligence',
    strength: 'characterDetailCard.pStrength',
    agility: 'characterDetailCard.pAgility',
    charm: 'characterDetailCard.pCharm',
    wit: 'characterDetailCard.pWit',
    courage: 'characterDetailCard.pCourage',
    kindness: 'characterDetailCard.pKindness',
    humor: 'characterDetailCard.pHumor',
    passion: 'characterDetailCard.pPassion',
    calm: 'characterDetailCard.pCalm',
    creative: 'characterDetailCard.pCreative',
    determined: 'characterDetailCard.pDetermined',
    empathetic: 'characterDetailCard.pEmpathetic',
    optimistic: 'characterDetailCard.pOptimistic',
    rational: 'characterDetailCard.pRational',
    sensitive: 'characterDetailCard.pSensitive',
    stubborn: 'characterDetailCard.pStubborn',
    wise: 'characterDetailCard.pWise'
  };
  const i18nKey = keyMap[key];
  return i18nKey ? t(i18nKey) : key;
}
</script>

<style scoped>
.character-detail-card {
  position: relative;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.character-detail-card:hover {
  border-color: rgba(167, 139, 250, 0.4);
  transform: translateY(-4px);
}

.character-detail-card.selected {
  border-color: #a78bfa;
  background: rgba(167, 139, 250, 0.1);
  box-shadow: 0 0 20px rgba(167, 139, 250, 0.4);
}

.character-detail-card.locked {
  opacity: 0.75;
}

/* CR-028: 可扮演角标 */
.playable-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 12px;
  background: rgba(34, 197, 94, 0.2);
  border: 1px solid rgba(34, 197, 94, 0.4);
  border-radius: 6px;
  padding: 2px 8px;
  color: #22c55e;
  z-index: 2;
}

/* CR-028: 锁定覆盖层 */
.card-locked-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 14px;
  z-index: 3;
}

.card-locked-icon {
  font-size: 28px;
}

.card-locked-price {
  font-size: 13px;
  font-weight: 600;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.2);
  border: 1px solid rgba(251, 191, 36, 0.4);
  border-radius: 8px;
  padding: 4px 10px;
}

.card-locked-subscription {
  font-size: 13px;
  font-weight: 600;
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.2);
  border: 1px solid rgba(167, 139, 250, 0.4);
  border-radius: 8px;
  padding: 4px 10px;
}

/* 角色头像和基础信息 */
.character-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.character-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(236, 72, 153, 0.3));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  flex-shrink: 0;
  overflow: hidden;
}

.character-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 8px 0;
  line-height: 1.4;
}

.character-basic {
  flex: 1;
}

.character-basic h3 {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.basic-info {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 喜好标签 */
.character-likes {
  margin-bottom: 20px;
}

.likes-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-right: 8px;
}

.likes-tags {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}

.like-tag {
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

/* 性格特征进度条 */
.personality-traits h4 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 12px 0;
}

.trait-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.trait-label {
  width: 50px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.trait-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.trait-fill {
  height: 100%;
  background: linear-gradient(90deg, #a78bfa, #FF6B9D);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.trait-value {
  width: 40px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  text-align: right;
  flex-shrink: 0;
}
</style>

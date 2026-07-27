<template>
  <div class="character-detail-card" :class="{ selected: isSelected }" @click="$emit('select')">
    <!-- 角色头像和基础信息 -->
    <div class="character-header">
      <div class="character-avatar">
        <img v-if="character.avatar_url" :src="character.avatar_url" :alt="character.name" />
        <span v-else>{{ character.name.charAt(0) }}</span>
      </div>
      <div class="character-basic">
        <h3>{{ character.name }}</h3>
        <p class="character-desc">{{ character.description || '暂无描述' }}</p>
        <div class="basic-info">
          <span v-if="character.age">{{ character.age }}岁</span>
          <span v-if="character.height">{{ character.height }}cm</span>
          <span v-if="character.birthday">{{ character.birthday }}</span>
        </div>
      </div>
    </div>

    <!-- 喜好标签 -->
    <div class="character-likes" v-if="character.likes && character.likes.length > 0">
      <span class="likes-label">喜好：</span>
      <div class="likes-tags">
        <span v-for="like in character.likes" :key="like" class="like-tag">
          {{ like }}
        </span>
      </div>
    </div>

    <!-- 性格特征进度条 -->
    <div class="personality-traits" v-if="parsedPersonality && Object.keys(parsedPersonality).length > 0">
      <h4>性格特征</h4>
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
import { computed } from 'vue';

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

const props = defineProps<{
  character: Character;
  isSelected: boolean;
}>();

defineEmits<{
  (e: 'select'): void;
}>();

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
  const labels: Record<string, string> = {
    gentle: '温柔',
    tsundere: '傲娇',
    cool: '冷静',
    energetic: '活泼',
    mysterious: '神秘',
    loyal: '忠诚',
    brave: '勇敢',
    brav: '勇敢',
    wisdom: '智慧',
    charisma: '魅力',
    luck: '幸运',
    intelligence: '智力',
    strength: '力量',
    agility: '敏捷',
    charm: '魅力',
    wit: '机智',
    courage: '勇气',
    kindness: '善良',
    humor: '幽默',
    passion: '热情',
    calm: '沉稳',
    creative: '创造力',
    determined: '决心',
    empathetic: '共情',
    optimistic: '乐观',
    rational: '理性',
    sensitive: '敏感',
    stubborn: '固执',
    wise: '睿智'
  };
  return labels[key] || key;
}
</script>

<style scoped>
.character-detail-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
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

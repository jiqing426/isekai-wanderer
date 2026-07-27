<template>
  <div class="script-card glass-card fade-in-up" :style="{ animationDelay: `${delay}s` }" @click="$emit('click')">
    <div class="card-cover" :style="coverStyle">
      <img v-if="hasCoverImage" :src="script.cover_image_url" :alt="script.title" class="cover-img" />
      <span v-else class="card-emoji">{{ genreEmoji }}</span>
      <n-tag v-if="script.genre" size="small" :bordered="false" class="genre-tag">{{ genreLabel }}</n-tag>
      <div v-if="script.route_count" class="route-badge">
        <span>🗺️ {{ script.route_count }} 路线</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-title">{{ script.title }}</div>
      <p class="card-desc">{{ script.description }}</p>
      <div v-if="script.tags && script.tags.length" class="card-tags">
        <n-tag v-for="tag in displayTags" :key="tag" size="tiny" :bordered="false" class="card-tag">{{ tagLabel(tag) }}</n-tag>
      </div>
    </div>
    <div class="card-footer">
      <div v-if="script.play_count_7d" class="play-count">🔥 {{ script.play_count_7d }} 人玩过</div>
      <n-button type="primary" size="small">{{ $t('game.startGame') }}</n-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NButton, NTag } from 'naive-ui';
import { computed } from 'vue';
import type { DiscoverCard } from '@/api/game';

const props = withDefaults(defineProps<{
  script: DiscoverCard;
  delay?: number;
}>(), {
  delay: 0,
});

defineEmits<{
  click: [];
}>();

const genreEmojiMap: Record<string, string> = {
  fantasy: '⚔️', romance: '💕', mystery: '🔍', scifi: '🚀',
  horror: '👁️', slice_of_life: '🌸', action: '🔥', drama: '🎭',
};

const genreLabelMap: Record<string, string> = {
  fantasy: '奇幻', romance: '恋爱', mystery: '悬疑', scifi: '科幻',
  horror: '恐怖', slice_of_life: '日常', action: '动作', drama: '剧情',
};

const tagLabelMap: Record<string, string> = {
  multiple_endings: '多结局', character_driven: '角色驱动', romance_options: '恋爱选项',
  dark_story: '暗黑', lighthearted: '轻松', emotional: '感人',
  short: '短篇', medium: '中篇', long: '长篇',
  male_protagonist: '男主', female_protagonist: '女主', custom_protagonist: '自定义',
};

const genreEmoji = computed(() => genreEmojiMap[props.script.genre] || '📖');
const genreLabel = computed(() => genreLabelMap[props.script.genre] || props.script.genre);

const hasCoverImage = computed(() => !!props.script.cover_image_url && props.script.cover_image_url.trim() !== '');

const coverStyle = computed(() => {
  if (hasCoverImage.value) {
    return {
      backgroundImage: `url(${props.script.cover_image_url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    };
  }
  return {};
});

const displayTags = computed(() => (props.script.tags || []).slice(0, 3));

function tagLabel(tag: string): string {
  return tagLabelMap[tag] || tag;
}
</script>

<style scoped>
.script-card {
  cursor: pointer;
  overflow: hidden;
  padding: 0;
  transition: all 0.3s ease;
}
.script-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.12);
}
.card-cover {
  aspect-ratio: 16/9;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(192, 132, 252, 0.06), rgba(249, 168, 212, 0.06));
  position: relative;
  overflow: hidden;
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  position: absolute;
  top: 0;
  left: 0;
}
.card-emoji { font-size: 44px; }
.genre-tag {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(192, 132, 252, 0.15) !important;
  color: var(--brand-primary) !important;
}
.route-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  padding: 2px 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.5);
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  backdrop-filter: blur(4px);
}
.card-body { padding: 14px 16px 8px; }
.card-title { font-size: 15px; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }
.card-desc {
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}
.card-tags { display: flex; gap: 4px; margin-top: 8px; flex-wrap: wrap; }
.card-tag {
  background: rgba(167, 139, 250, 0.08) !important;
  color: var(--text-muted) !important;
  font-size: 10px !important;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px 14px;
}
.play-count { font-size: 11px; color: var(--text-subtle); }
</style>

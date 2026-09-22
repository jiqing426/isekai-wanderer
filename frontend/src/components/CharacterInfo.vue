<template>
  <div class="character-info">
    <div class="avatar-placeholder">
      <img v-if="avatarUrl && !avatarFailed" :src="avatarUrl" :alt="characterName" class="avatar-img" @error="avatarFailed = true" />
      <span v-else class="avatar-initial">{{ characterName?.[0] || '?' }}</span>
    </div>
    <div class="info-text">
      <div class="char-name">{{ characterName || $t('characterInfo.unknownCharacter') }}</div>
      <div v-if="characterTitle" class="char-title">{{ characterTitle }}</div>
      <div v-if="characterAge || characterBirthday" class="char-meta">
        <span v-if="characterAge">{{ characterAge }}{{ $t('characterInfo.yearsOld', { age: characterAge }) }}</span>
        <span v-if="characterBirthday">· {{ characterBirthday }}</span>
      </div>
      <div v-if="characterLikes && characterLikes.length > 0" class="char-likes">
        <span v-for="like in characterLikes.slice(0, 3)" :key="like" class="like-tag">{{ like }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = withDefaults(defineProps<{
  characterId?: string;
  characterName: string;
  characterTitle?: string;
  avatarUrl?: string;
  characterAge?: number | string;
  characterBirthday?: string;
  characterLikes?: string[];
}>(), {
  characterName: t('characterInfo.unknownCharacter'),
  characterLikes: () => [],
});

// CR-032: 图片加载失败时 fallback 到首字母
const avatarFailed = ref(false);

// 当 avatarUrl 或 characterId 变化时重置失败状态
watch(() => [props.avatarUrl, props.characterId], () => {
  avatarFailed.value = false;
});
</script>

<style scoped>
.character-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #818CF8, #C084FC);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-initial {
  color: white;
  font-size: 18px;
  font-weight: 700;
}

.info-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.char-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.char-title {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.char-meta {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.char-likes {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.like-tag {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(167, 139, 250, 0.15);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 4px;
  color: var(--text-secondary);
}
</style>

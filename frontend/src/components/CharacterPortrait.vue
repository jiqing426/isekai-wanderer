<template>
  <div class="character-portrait">
    <div class="portrait-container" :class="[`emotion-${emotion}`]">
      <div class="portrait-emoji">{{ currentEmoji }}</div>
      <div class="portrait-name">{{ name }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  characterId: string;
  name: string;
  emoji: string;
  emotion?: 'normal' | 'happy' | 'sad' | 'angry' | 'shy';
}

const props = withDefaults(defineProps<Props>(), {
  emotion: 'normal'
});

// 表情映射表
const emotionMap: Record<string, string> = {
  normal: '🌸',
  happy: '😊',
  sad: '😢',
  angry: '😠',
  shy: '😳'
};

// 根据 emotion 返回对应的 emoji
const currentEmoji = computed(() => {
  return emotionMap[props.emotion] || props.emoji;
});
</script>

<style scoped>
.character-portrait {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.portrait-container {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(167, 139, 250, 0.1);
  border: 2px solid rgba(167, 139, 250, 0.3);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.portrait-container:hover {
  border-color: rgba(167, 139, 250, 0.5);
  box-shadow: 0 8px 24px rgba(167, 139, 250, 0.2);
}

.portrait-emoji {
  font-size: 80px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.portrait-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  text-align: center;
}

/* 表情动画 */
.emotion-normal .portrait-emoji {
  animation: fadeIn 0.3s ease;
}

.emotion-happy .portrait-emoji {
  animation: bounceIn 0.4s ease;
}

.emotion-sad .portrait-emoji {
  animation: fadeIn 0.3s ease;
}

.emotion-angry .portrait-emoji {
  animation: shake 0.4s ease;
}

.emotion-shy .portrait-emoji {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes bounceIn {
  0% {
    transform: scale(0.8);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes shake {
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
  .portrait-container {
    width: 150px;
    height: 150px;
  }

  .portrait-emoji {
    font-size: 60px;
  }

  .portrait-name {
    font-size: 14px;
  }
}
</style>

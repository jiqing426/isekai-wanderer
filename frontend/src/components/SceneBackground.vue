<template>
  <div class="scene-background">
    <transition name="fade" mode="out-in">
      <div
        :key="background"
        class="background-layer"
        :style="backgroundStyle"
      >
        <div class="overlay"></div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  background: string; // 支持图片URL或CSS渐变
}

const props = defineProps<Props>();

const backgroundStyle = computed(() => {
  // 判断是否为URL（以http或/开头）
  if (props.background.startsWith('http') || props.background.startsWith('/')) {
    return {
      backgroundImage: `url(${props.background})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    };
  }
  // 否则作为CSS渐变
  return {
    background: props.background
  };
});
</script>

<style scoped>
.scene-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  overflow: hidden;
}

.background-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

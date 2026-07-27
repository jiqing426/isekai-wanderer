<template>
  <transition :name="transitionName" @after-leave="onDone">
    <div v-if="visible" class="scene-transition" :class="{ flash: type === 'flash' }">
      <div class="transition-overlay">
        <div v-if="sceneName" class="transition-label fade-in-up">
          <span class="scene-icon">🎬</span>
          <span class="scene-text">{{ sceneName }}</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

export type TransitionType = 'fade' | 'slide' | 'flash';

const props = defineProps<{
  scene: string | null;
  type?: TransitionType;
  duration?: number;
}>();

const emit = defineEmits<{ done: [] }>();

const visible = ref(false);
const sceneName = ref<string | null>(null);
const transitionName = ref('scene-fade');

const TRANSITION_MAP: Record<TransitionType, string> = {
  fade: 'scene-fade',
  slide: 'scene-slide',
  flash: 'scene-flash',
};

watch(
  () => props.scene,
  (newScene, oldScene) => {
    if (!newScene || newScene === oldScene) return;
    sceneName.value = newScene;
    transitionName.value = TRANSITION_MAP[props.type || 'fade'];
    visible.value = true;
    const dur = props.duration || 800;
    setTimeout(() => {
      visible.value = false;
    }, dur);
  },
);

function onDone() {
  emit('done');
}
</script>

<style scoped>
.scene-transition {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
}
.transition-overlay {
  width: 100%;
  height: 100%;
  background: rgba(10, 8, 20, 0.92);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
}
.scene-transition.flash .transition-overlay {
  background: rgba(255, 255, 255, 0.85);
}
.transition-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 28px;
  border-radius: 16px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  backdrop-filter: blur(12px);
}
.scene-icon {
  font-size: 28px;
}
.scene-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
  letter-spacing: 0.05em;
}

/* Fade transition */
.scene-fade-enter-active,
.scene-fade-leave-active {
  transition: opacity 0.4s ease;
}
.scene-fade-enter-from,
.scene-fade-leave-to {
  opacity: 0;
}

/* Slide transition */
.scene-slide-enter-active,
.scene-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}
.scene-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.scene-slide-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}

/* Flash transition */
.scene-flash-enter-active {
  transition: opacity 0.15s ease-out;
}
.scene-flash-leave-active {
  transition: opacity 0.6s ease-in;
}
.scene-flash-enter-from,
.scene-flash-leave-to {
  opacity: 0;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up {
  animation: fadeInUp 0.5s ease;
}
</style>

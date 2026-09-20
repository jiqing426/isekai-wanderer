<template>
  <div class="mobile-tabbar" v-if="isVisible">
    <div
      v-for="tab in tabs"
      :key="tab.route"
      class="tabbar-item"
      :class="{ active: isActive(tab.route) }"
      @click="navigateTo(tab.route)"
    >
      <div class="tab-icon">{{ tab.icon }}</div>
      <div class="tab-label">{{ tab.label }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const tabs = [
  { route: '/discover', icon: '🏠', label: '首页' },
  { route: '/discover', icon: '🔍', label: '发现' },
  { route: '/game', icon: '🎮', label: '游戏' },
  { route: '/community', icon: '👥', label: '社区' },
  { route: '/personal-center', icon: '👤', label: '我的' },
];

// GameView 隐藏 TabBar（沉浸模式）
const isVisible = computed(() => {
  const path = route.path;
  // Hide on /game and /game/* routes (immersive mode)
  if (path === '/game' || path.startsWith('/game/')) {
    return false;
  }
  return true;
});

function isActive(tabRoute: string): boolean {
  const currentPath = route.path;
  // Exact match for /home, /discover, /community, /profile
  // Prefix match for /game/* routes
  if (tabRoute === '/game') {
    return currentPath === '/game' || currentPath.startsWith('/game/');
  }
  return currentPath === tabRoute;
}

function navigateTo(targetRoute: string) {
  if (route.path === targetRoute) return;
  router.push(targetRoute);
}
</script>

```

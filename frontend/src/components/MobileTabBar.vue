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
import { useI18n } from 'vue-i18n'

const route = useRoute();
const router = useRouter();

const tabs = [
  { route: '/discover', icon: '🏠', label: t('mobileTabBar.home') },
  { route: '/discover', icon: '🔍', label: t('mobileTabBar.discover') },
  { route: '/game', icon: '🎮', label: t('mobileTabBar.game') },
  { route: '/community', icon: '👥', label: t('mobileTabBar.community') },
  { route: '/personal-center', icon: '👤', label: t('mobileTabBar.profile') },
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

<template>
  <n-config-provider :theme="naiveTheme" :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <AppHeader v-if="showHeader" />
        <main :class="{ 'main-content': showHeader }">
          <router-view :key="$route.path" />
        </main>
        <!-- MobileTabBar 已隐藏，移动端只显示 Header Tab -->
        <!-- <MobileTabBar /> -->
        <UnlockModal />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { darkTheme } from 'naive-ui';
import AppHeader from '@/components/AppHeader.vue';
import UnlockModal from '@/components/unlock/UnlockModal.vue';
// MobileTabBar 已隐藏，移动端只显示 Header Tab
// import MobileTabBar from '@/components/MobileTabBar.vue';
import { themeMode } from '@/composables/useTheme';
import { themeOverrides } from '@/styles/theme';
import { useThemeStore } from '@/stores/theme';
import { useUnlockStore } from '@/stores/unlock';
import { useUnlockModal } from '@/composables/useUnlockModal';

const route = useRoute();
const themeStore = useThemeStore();
const unlockStore = useUnlockStore();
const unlockModal = useUnlockModal();

// Routes that should NOT show the header
const noHeaderRoutes = ['/onboarding'];
const showHeader = computed(() => {
  // Show header on all routes except onboarding
  return !noHeaderRoutes.some(r => route.path.startsWith(r));
});



const naiveTheme = computed(() => themeMode.value === 'dark' ? darkTheme : null);

// Initialize theme on mount
onMounted(async () => {
  themeStore.init();
  // Fetch pending unlocks and push to modal queue
  try {
    await unlockStore.fetchPending();
    if (unlockStore.hasPending) {
      const pending = [...unlockStore.pendingQueue];
      unlockStore.pendingQueue = [];
      unlockModal.queue(pending);
    }
  } catch (err) {
    console.error('Failed to load pending unlocks:', err);
  }
});

// Apply theme on change
watch(themeMode, () => {}, { immediate: true });
</script>

<style>
@import '@/styles/global.css';

.main-content {
  padding-top: 60px;
}

</style>

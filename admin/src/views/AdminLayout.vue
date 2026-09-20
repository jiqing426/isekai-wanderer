<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      show-trigger
    >
      <div style="padding: 20px; text-align: center; font-size: 18px; font-weight: bold">
        🌟 Admin
      </div>
      <n-menu :options="menuOptions" :value="activeKey" @update:value="handleMenuClick" />
    </n-layout-sider>
    <n-layout>
      <n-layout-header bordered style="padding: 16px 24px; display: flex; justify-content: space-between; align-items: center">
        <h2 style="margin: 0; font-size: 16px">Isekai Wanderer 管理后台</h2>
        <n-space>
          <span>{{ auth.user?.email }}</span>
          <n-button @click="handleLogout" size="small">退出</n-button>
        </n-space>
      </n-layout-header>
      <n-layout-content content-style="padding: 24px;" style="height: calc(100vh - 64px); overflow: auto">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { computed, h } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { NIcon } from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import {
  BookOutline,
  MapOutline,
  PeopleOutline,
  HomeOutline,
} from '@vicons/ionicons5';

const router = useRouter();
const route = useRoute();
const auth = useAuthStore();

function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

const menuOptions: MenuOption[] = [
  { label: '首页', key: 'Dashboard', icon: renderIcon(HomeOutline) },
  { label: 'Lorebook 管理', key: 'LorebookManage', icon: renderIcon(BookOutline) },
  { label: '场景配置', key: 'SceneConfig', icon: renderIcon(MapOutline) },
  { label: '角色管理', key: 'CharacterList', icon: renderIcon(PeopleOutline) },
];

const activeKey = computed(() => {
  const name = route.name as string;
  if (name?.startsWith('Character')) return 'CharacterList';
  return name;
});

function handleMenuClick(key: string) {
  router.push({ name: key });
}

function handleLogout() {
  auth.logout();
  router.push({ name: 'Login' });
}
</script>
